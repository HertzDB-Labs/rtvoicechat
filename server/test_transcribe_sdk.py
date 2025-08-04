#!/usr/bin/env python3
"""
Test script for Amazon Transcribe streaming using the official SDK.
Based on: https://github.com/awslabs/amazon-transcribe-streaming-sdk
"""

import asyncio
import os
from dotenv import load_dotenv
import wave
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.utils import apply_realtime_delay

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

# Audio settings
SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2
CHANNEL_NUMS = 1
CHUNK_SIZE = 1024 * 8

# AWS settings
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

class MyEventHandler(TranscriptResultStreamHandler):
    """Custom event handler for transcription results."""
    
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        """Handle incoming transcription events."""
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(f"Transcript: {alt.transcript}")

def create_test_audio():
    """Create a test WAV file with 1 second of silence."""
    try:
        audio_path = "test.wav"
        with wave.open(audio_path, 'wb') as wav_file:
            # Set parameters
            wav_file.setnchannels(CHANNEL_NUMS)  # Mono
            wav_file.setsampwidth(BYTES_PER_SAMPLE)  # 2 bytes per sample
            wav_file.setframerate(SAMPLE_RATE)  # 16kHz
            
            # Create 1 second of silence
            samples = b'\x00\x00' * SAMPLE_RATE
            wav_file.writeframes(samples)
        
        return audio_path
    except Exception as e:
        print(f"Error creating test audio: {e}")
        return None

async def test_transcribe_streaming():
    """Test Amazon Transcribe streaming."""
    try:
        # Create test audio file
        audio_path = create_test_audio()
        if not audio_path:
            print("Failed to create test audio file")
            return False
        
        print("\nStarting streaming transcription test...")
        
        # Create streaming client
        client = TranscribeStreamingClient(region=AWS_REGION)
        
        # Start transcription stream
        stream = await client.start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=SAMPLE_RATE,
            media_encoding="pcm"
        )
        
        print("Successfully started streaming!")
        
        async def write_chunks():
            """Write audio chunks to the stream."""
            try:
                with open(audio_path, 'rb') as audio_file:
                    while chunk := audio_file.read(CHUNK_SIZE):
                        await stream.input_stream.send_audio_event(audio_chunk=chunk)
                        await asyncio.sleep(0.1)  # Simulate real-time streaming
                await stream.input_stream.end_stream()
            except Exception as e:
                print(f"Error writing chunks: {e}")
        
        # Create handler and process events
        handler = MyEventHandler(stream.output_stream)
        await asyncio.gather(write_chunks(), handler.handle_events())
        
        print("Streaming test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error in streaming test: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists('test.wav'):
            os.remove('test.wav')

async def main():
    """Run the test."""
    print("\n=== Amazon Transcribe Streaming SDK Test ===\n")
    
    # Check AWS credentials
    print("AWS Region:", AWS_REGION)
    
    # Test streaming
    success = await test_transcribe_streaming()
    
    print("\n=== Test Results ===")
    print("Streaming test:", "✅ SUCCESS" if success else "❌ FAILED")

if __name__ == "__main__":
    asyncio.run(main()) 