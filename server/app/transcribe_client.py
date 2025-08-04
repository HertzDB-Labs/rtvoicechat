import boto3
import json
import os
import tempfile
import time
import asyncio
import websockets
import uuid
from typing import Dict, Any, Optional, AsyncGenerator, Callable
from .config import Config
from .streaming_transcribe_client import StreamingTranscribeClient
from .audio_converter import AudioConverter

class TranscribeClient:
    """Client for Amazon Transcribe integration."""
    
    def __init__(self):
        self.client = boto3.client(
            'transcribe',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.s3_client = boto3.client(
            's3',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.streaming_client = StreamingTranscribeClient()
        self.current_transcription_mode = Config.TRANSCRIPTION_MODE
    
    async def transcribe_audio_file(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file using Amazon Transcribe.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dict containing transcription results
        """
        try:
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Use transcription
            transcription_result = await self._transcribe_audio(audio_data)
            
            return {
                "success": True,
                "transcription": transcription_result,
                "file_path": audio_file_path
            }
            
        except Exception as e:
            print(f"Error in transcription: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": None
            }
    
    async def transcribe_audio_bytes(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Transcribe audio bytes using Amazon Transcribe.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Dict containing transcription results
        """
        try:
            # Check if audio data is valid
            if len(audio_data) < 100:  # Very small audio file
                return {
                    "success": False,
                    "error": "Audio data too small or invalid",
                    "transcription": None
                }
            
            # Choose transcription method based on configuration
            if self.current_transcription_mode == "streaming":
                return await self._transcribe_audio_streaming(audio_data)
            else:
                return await self._transcribe_audio_bucket(audio_data)
            
        except Exception as e:
            print(f"Error in audio transcription: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": None
            }
    
    async def _transcribe_audio_streaming(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Perform transcription using Amazon Transcribe streaming (bucketless).
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Dict containing transcription results
        """
        try:
            # Check if we have AWS credentials configured
            if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
                if Config.ENABLE_STREAMING_FALLBACK:
                    print("AWS credentials not configured, falling back to bucket method")
                    return await self._transcribe_audio_bucket(audio_data)
                else:
                    return {
                        "success": False,
                        "error": "AWS credentials not configured",
                        "transcription": None
                    }
            
            # Detect audio format and convert to PCM
            audio_format = AudioConverter.detect_audio_format(audio_data)
            print(f"Detected audio format: {audio_format}")
            
            # Convert to PCM format for streaming
            pcm_audio = AudioConverter.convert_to_pcm(audio_data, audio_format)
            
            if not pcm_audio:
                if Config.ENABLE_STREAMING_FALLBACK:
                    print("Audio conversion failed, falling back to bucket method")
                    return await self._transcribe_audio_bucket(audio_data)
                else:
                    return {
                        "success": False,
                        "error": "Failed to convert audio to PCM format",
                        "transcription": None
                    }
            
            # Create an async generator for the PCM audio data
            async def audio_stream():
                # Split PCM audio data into appropriate chunks for streaming
                # Use larger chunks for better performance (8KB chunks)
                chunk_size = 1024 * 8  # 8KB chunks
                for i in range(0, len(pcm_audio), chunk_size):
                    chunk = pcm_audio[i:i + chunk_size]
                    yield chunk
                    # Smaller delay for faster processing
                    await asyncio.sleep(0.005)
            
            # Use a future to capture the transcription result
            transcription_result = {"text": "", "completed": False}
            
            def on_transcription(text: str):
                transcription_result["text"] = text
                transcription_result["completed"] = True
            
            def on_error(error: str):
                transcription_result["error"] = error
                transcription_result["completed"] = True
            
            # Start streaming transcription
            print("Starting streaming transcription...")
            stream_result = await self.streaming_client.start_streaming_transcription(
                audio_stream(),
                on_transcription,
                on_error
            )
            
            if not stream_result.get("success"):
                if Config.ENABLE_STREAMING_FALLBACK:
                    print(f"Streaming failed: {stream_result.get('error')}, falling back to bucket method")
                    return await self._transcribe_audio_bucket(audio_data)
                else:
                    return {
                        "success": False,
                        "error": stream_result.get("error", "Streaming transcription failed"),
                        "transcription": None
                    }
            
            # Wait for transcription to complete (with timeout)
            timeout = Config.STREAMING_TIMEOUT
            start_time = time.time()
            
            while not transcription_result["completed"]:
                if time.time() - start_time > timeout:
                    await self.streaming_client.stop_live_transcription()
                    if Config.ENABLE_STREAMING_FALLBACK:
                        print("Streaming timeout, falling back to bucket method")
                        return await self._transcribe_audio_bucket(audio_data)
                    else:
                        return {
                            "success": False,
                            "error": "Streaming transcription timeout",
                            "transcription": None
                        }
                await asyncio.sleep(0.1)
            
            # Stop streaming
            await self.streaming_client.stop_live_transcription()
            
            # Check if we got an error
            if "error" in transcription_result:
                if Config.ENABLE_STREAMING_FALLBACK:
                    print(f"Streaming error: {transcription_result['error']}, falling back to bucket method")
                    return await self._transcribe_audio_bucket(audio_data)
                else:
                    return {
                        "success": False,
                        "error": transcription_result["error"],
                        "transcription": None
                    }
            
            # Return successful transcription
            return {
                "success": True,
                "transcription": transcription_result["text"],
                "note": "Streaming transcription completed successfully."
            }
                
        except Exception as e:
            print(f"Error in streaming transcription: {e}")
            if Config.ENABLE_STREAMING_FALLBACK:
                print("Falling back to bucket method due to streaming error")
                return await self._transcribe_audio_bucket(audio_data)
            else:
                return {
                    "success": False,
                    "error": str(e),
                    "transcription": None
                }
    
    async def _transcribe_audio_bucket(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Perform transcription using Amazon Transcribe with S3 bucket (existing method).
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Dict containing transcription results
        """
        try:
            transcription_result = await self._transcribe_audio(audio_data)
            
            return {
                "success": True,
                "transcription": transcription_result,
                "note": "Bucket-based transcription completed."
            }
            
        except Exception as e:
            print(f"Error in bucket transcription: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": None
            }
    
    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """
        Perform transcription using Amazon Transcribe (original bucket-based method).
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        try:
            # Create a temporary file for the audio data
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Check if we have AWS credentials configured
                if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
                    return "This is a test transcription. Please configure AWS credentials for real transcription."
                
                # Create a unique job name
                job_name = f"transcribe_job_{uuid.uuid4().hex[:8]}"
                
                # Real transcription implementation
                try:
                    # Create a unique file name
                    file_name = f"audio_{uuid.uuid4().hex[:8]}.wav"
                    s3_key = f"transcribe-input/{file_name}"
                    
                    # Upload audio to S3
                    print(f"Uploading audio to S3: {Config.S3_BUCKET_NAME}/{s3_key}")
                    self.s3_client.upload_file(temp_file_path, Config.S3_BUCKET_NAME, s3_key)
                    
                    # Start transcription job
                    print(f"Starting transcription job: {job_name}")
                    response = self.client.start_transcription_job(
                        TranscriptionJobName=job_name,
                        Media={'MediaFileUri': f"s3://{Config.S3_BUCKET_NAME}/{s3_key}"},
                        MediaFormat='wav',
                        LanguageCode='en-US'
                    )
                    
                    # Poll for completion
                    print("Polling for transcription completion...")
                    while True:
                        job_response = self.client.get_transcription_job(
                            TranscriptionJobName=job_name
                        )
                        
                        status = job_response['TranscriptionJob']['TranscriptionJobStatus']
                        
                        if status == 'COMPLETED':
                            # Get transcription results
                            transcript_uri = job_response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                            print(f"Transcription completed. Results at: {transcript_uri}")
                            
                            # Download and parse transcript
                            import requests
                            transcript_response = requests.get(transcript_uri)
                            transcript_data = transcript_response.json()
                            
                            # Extract transcription text
                            transcription = transcript_data['results']['transcripts'][0]['transcript']
                            
                            # Clean up S3 file
                            try:
                                self.s3_client.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=s3_key)
                            except Exception as e:
                                print(f"Warning: Could not delete S3 file: {e}")
                            
                            return transcription
                            
                        elif status == 'FAILED':
                            error_message = job_response['TranscriptionJob'].get('FailureReason', 'Unknown error')
                            print(f"Transcription job failed: {error_message}")
                            raise Exception(f"Transcription job failed: {error_message}")
                        
                        # Wait before polling again
                        await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"Transcription error: {e}")
                    
                    # If S3 or transcription fails, try a fallback approach
                    # This could be using a different transcription service or method
                    
                    # For now, return a helpful error message
                    if "NoSuchBucket" in str(e):
                        return "S3 bucket not found. Please create the bucket or check configuration."
                    elif "AccessDenied" in str(e):
                        return "Access denied. Please check AWS credentials and permissions."
                    else:
                        return f"Transcription failed: {str(e)}"
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            print(f"Error in transcription: {e}")
            raise e
    
    async def start_real_time_transcription(
        self, 
        on_transcription: Callable[[str], None],
        on_error: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Start a real-time transcription session for LiveKit audio streams.
        
        Args:
            on_transcription: Callback for transcription results
            on_error: Optional callback for errors
            
        Returns:
            Dict containing session info and methods to send audio
        """
        try:
            # Check if streaming is available
            if not self.streaming_client.test_connection():
                return {
                    "success": False,
                    "error": "Streaming transcription not available"
                }
            
            # Start live transcription session
            result = await self.streaming_client.start_live_transcription(
                on_transcription, on_error
            )
            
            if result.get("success"):
                self.is_streaming_active = True
                
            return result
            
        except Exception as e:
            print(f"Error starting real-time transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_audio_chunk_to_stream(self, audio_chunk: bytes, audio_format: str = "webm") -> bool:
        """
        Send an audio chunk to the active streaming transcription.
        
        Args:
            audio_chunk: Raw audio bytes
            audio_format: Format of the audio (webm, wav, etc.)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not hasattr(self, 'is_streaming_active') or not self.is_streaming_active:
                print("No active streaming session")
                return False
            
            # Convert chunk to PCM
            pcm_chunk = AudioConverter.convert_to_pcm(audio_chunk, audio_format)
            
            if not pcm_chunk:
                print(f"Failed to convert audio chunk to PCM")
                return False
            
            # Send to streaming client
            return await self.streaming_client.send_audio_chunk(pcm_chunk)
            
        except Exception as e:
            print(f"Error sending audio chunk to stream: {e}")
            return False
    
    async def stop_real_time_transcription(self) -> Dict[str, Any]:
        """Stop the active real-time transcription session."""
        try:
            if hasattr(self, 'is_streaming_active') and self.is_streaming_active:
                result = await self.streaming_client.stop_live_transcription()
                self.is_streaming_active = False
                return result
            else:
                return {
                    "success": False,
                    "error": "No active streaming session"
                }
        except Exception as e:
            print(f"Error stopping real-time transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def start_realtime_transcription(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """
        Start real-time transcription from a continuous audio stream.
        This would use WebSocket-based streaming with Amazon Transcribe.
        
        Args:
            audio_stream: Async generator yielding audio bytes
            
        Yields:
            Transcribed text as it becomes available
        """
        try:
            # This is a placeholder for real-time streaming transcription
            # In production, you would:
            # 1. Establish WebSocket connection to Amazon Transcribe
            # 2. Stream audio data in real-time
            # 3. Receive transcription results as they become available
            
            async for audio_chunk in audio_stream:
                # Simulate real-time transcription processing
                await asyncio.sleep(0.1)
                
                # For now, yield a placeholder
                # This should be replaced with actual transcription logic
                yield "Real-time transcription placeholder"
                
        except Exception as e:
            print(f"Error in real-time transcription: {e}")
            yield f"Transcription error: {str(e)}"
    
    def test_connection(self) -> bool:
        """Test the Transcribe connection."""
        try:
            # Try to list transcription jobs to test connection
            self.client.list_transcription_jobs(MaxResults=1)
            return True
        except Exception as e:
            print(f"Transcribe connection test failed: {e}")
            return False 