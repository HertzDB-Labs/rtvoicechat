#!/usr/bin/env python3
"""
Simple test for streaming transcription fixes.
"""

import asyncio
import logging
from app.streaming_transcribe_client import StreamingTranscribeClient
from app.audio_converter import AudioConverter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_streaming():
    """Test the fixed streaming transcription with a simple audio file."""
    
    # Create streaming client
    client = StreamingTranscribeClient()
    
    # Test connection
    if not client.test_connection():
        logger.error("❌ Streaming client connection failed")
        return False
    
    logger.info("✅ Streaming client connection successful")
    
    # Read test audio file
    try:
        with open("test.webm", "rb") as f:
            audio_data = f.read()
            
        logger.info(f"📁 Loaded audio file: {len(audio_data)} bytes")
        
        # Detect and convert audio
        audio_format = AudioConverter.detect_audio_format(audio_data)
        logger.info(f"🎵 Detected audio format: {audio_format}")
        
        pcm_audio = AudioConverter.convert_to_pcm(audio_data, audio_format)
        
        if not pcm_audio:
            logger.error("❌ Failed to convert audio to PCM")
            return False
            
        logger.info(f"🔄 Converted to PCM: {len(pcm_audio)} bytes")
        
        # Create audio stream generator
        async def audio_stream():
            chunk_size = 1024 * 8  # 8KB chunks
            for i in range(0, len(pcm_audio), chunk_size):
                chunk = pcm_audio[i:i + chunk_size]
                yield chunk
                await asyncio.sleep(0.01)  # Small delay to simulate streaming
        
        # Set up callbacks
        transcription_results = []
        
        def on_transcription(text: str):
            logger.info(f"📝 Transcription received: '{text}'")
            transcription_results.append(text)
        
        def on_error(error: str):
            logger.error(f"❌ Transcription error: {error}")
        
        # Start streaming transcription
        logger.info("🚀 Starting streaming transcription...")
        
        result = await client.start_streaming_transcription(
            audio_stream(),
            on_transcription,
            on_error
        )
        
        logger.info(f"📊 Streaming result: {result}")
        
        if result.get("success"):
            logger.info("✅ Streaming transcription completed successfully")
            if transcription_results:
                logger.info(f"📝 Final transcription: '{' '.join(transcription_results)}'")
            else:
                logger.warning("⚠️ No transcription results received (audio might be too short or silent)")
            return True
        else:
            logger.error(f"❌ Streaming transcription failed: {result.get('error')}")
            return False
            
    except FileNotFoundError:
        logger.error("❌ Test audio file 'test.webm' not found")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_streaming())
    
    if success:
        print("\n🎉 Streaming transcription test PASSED!")
    else:
        print("\n💥 Streaming transcription test FAILED!")