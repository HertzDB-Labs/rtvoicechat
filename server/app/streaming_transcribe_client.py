import asyncio
import json
import logging
import uuid
import base64
from typing import Dict, Any, Optional, AsyncGenerator, Callable
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from .config import Config
from .audio_converter import AudioConverter

logger = logging.getLogger(__name__)

class StreamingTranscribeClient:
    """Client for Amazon Transcribe streaming (WebSocket-based) transcription."""
    
    def __init__(self):
        self.transcription_callback: Optional[Callable[[str], None]] = None
        self.error_callback: Optional[Callable[[str], None]] = None
        self.session_id: Optional[str] = None
        self.client = TranscribeStreamingClient(region=Config.AWS_REGION)
        
    async def start_streaming_transcription(
        self, 
        audio_stream: AsyncGenerator[bytes, None],
        on_transcription: Callable[[str], None],
        on_error: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Start real-time streaming transcription from audio stream.
        
        Args:
            audio_stream: Async generator yielding audio bytes
            on_transcription: Callback function for transcription results
            on_error: Optional callback for error handling
            
        Returns:
            Dict containing connection status
        """
        try:
            self.transcription_callback = on_transcription
            self.error_callback = on_error
            self.session_id = str(uuid.uuid4())
            
            # Create event handler
            class EventHandler(TranscriptResultStreamHandler):
                def __init__(self, output_stream, callback):
                    super().__init__(output_stream)
                    self.callback = callback
                
                async def handle_transcript_event(self, transcript_event: TranscriptEvent):
                    results = transcript_event.transcript.results
                    for result in results:
                        if result.is_partial:
                            # Handle partial results
                            for alt in result.alternatives:
                                if self.callback and alt.transcript.strip():
                                    logger.debug(f"Partial transcription: {alt.transcript}")
                                    self.callback(alt.transcript)
                        else:
                            # Handle final results
                            for alt in result.alternatives:
                                if self.callback and alt.transcript.strip():
                                    logger.info(f"Final transcription: {alt.transcript}")
                                    self.callback(alt.transcript)
            
            # Start transcription stream
            stream = await self.client.start_stream_transcription(
                language_code="en-US",
                media_sample_rate_hz=16000,
                media_encoding="pcm"
            )
            
            # Process audio stream
            async def process_audio():
                try:
                    # Process chunks as they arrive (true streaming)
                    chunk_count = 0
                    async for chunk in audio_stream:
                        chunk_count += 1
                        if chunk and len(chunk) > 0:
                            try:
                                # Send chunk directly to transcribe stream
                                await stream.input_stream.send_audio_event(audio_chunk=chunk)
                                logger.debug(f"Sent audio chunk {chunk_count}, size: {len(chunk)} bytes")
                                # Small delay to prevent overwhelming the service
                                await asyncio.sleep(0.01)
                            except Exception as chunk_error:
                                logger.warning(f"Error sending chunk {chunk_count}: {chunk_error}")
                                continue
                    
                    if chunk_count == 0:
                        if self.error_callback:
                            self.error_callback("No audio data received")
                        return
                    
                    logger.info(f"Processed {chunk_count} audio chunks")
                    
                    # End stream
                    await stream.input_stream.end_stream()
                    
                except Exception as e:
                    logger.error(f"Error processing audio: {e}")
                    if self.error_callback:
                        self.error_callback(str(e))
            
            # Create handler and start processing
            handler = EventHandler(stream.output_stream, self.transcription_callback)
            await asyncio.gather(process_audio(), handler.handle_events())
            
            return {
                "success": True,
                "message": "Streaming transcription completed",
                "session_id": self.session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to start streaming transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_live_transcription(
        self,
        on_transcription: Callable[[str], None],
        on_error: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Start a live transcription session that can accept real-time audio chunks.
        
        Args:
            on_transcription: Callback function for transcription results
            on_error: Optional callback for error handling
            
        Returns:
            Dict containing connection status and methods to send audio
        """
        try:
            self.transcription_callback = on_transcription
            self.error_callback = on_error
            self.session_id = str(uuid.uuid4())
            
            # Create event handler
            class EventHandler(TranscriptResultStreamHandler):
                def __init__(self, output_stream, callback):
                    super().__init__(output_stream)
                    self.callback = callback
                
                async def handle_transcript_event(self, transcript_event: TranscriptEvent):
                    results = transcript_event.transcript.results
                    for result in results:
                        if result.is_partial:
                            # Handle partial results
                            for alt in result.alternatives:
                                if self.callback and alt.transcript.strip():
                                    logger.debug(f"Live partial transcription: {alt.transcript}")
                                    self.callback(alt.transcript)
                        else:
                            # Handle final results
                            for alt in result.alternatives:
                                if self.callback and alt.transcript.strip():
                                    logger.info(f"Live final transcription: {alt.transcript}")
                                    self.callback(alt.transcript)
            
            # Start transcription stream
            stream = await self.client.start_stream_transcription(
                language_code="en-US",
                media_sample_rate_hz=16000,
                media_encoding="pcm"
            )
            
            # Store stream for sending audio chunks
            self.active_stream = stream
            self.active_handler = EventHandler(stream.output_stream, self.transcription_callback)
            
            # Start handler in background
            asyncio.create_task(self.active_handler.handle_events())
            
            return {
                "success": True,
                "message": "Live transcription session started",
                "session_id": self.session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to start live transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_audio_chunk(self, audio_chunk: bytes) -> bool:
        """
        Send an audio chunk to the active transcription session.
        
        Args:
            audio_chunk: PCM audio data chunk
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if hasattr(self, 'active_stream') and self.active_stream:
                await self.active_stream.input_stream.send_audio_event(audio_chunk=audio_chunk)
                return True
            else:
                logger.error("No active transcription session")
                return False
        except Exception as e:
            logger.error(f"Error sending audio chunk: {e}")
            return False
    
    async def stop_live_transcription(self) -> Dict[str, Any]:
        """Stop the active live transcription session."""
        try:
            if hasattr(self, 'active_stream') and self.active_stream:
                await self.active_stream.input_stream.end_stream()
                self.active_stream = None
                self.active_handler = None
                return {
                    "success": True,
                    "message": "Live transcription session stopped"
                }
            else:
                return {
                    "success": False,
                    "error": "No active session to stop"
                }
        except Exception as e:
            logger.error(f"Error stopping live transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def test_connection(self) -> bool:
        """Test if streaming transcription is available."""
        try:
            # Check if AWS credentials are configured
            if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
                return False
            
            # Create test client
            client = TranscribeStreamingClient(region=Config.AWS_REGION)
            return True
            
        except Exception as e:
            logger.error(f"Streaming transcription connection test failed: {e}")
            return False 