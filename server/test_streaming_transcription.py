#!/usr/bin/env python3
"""
Test script for streaming transcription functionality.
This script tests both streaming and bucket-based transcription modes.
"""

import asyncio
import logging
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.transcribe_client import TranscribeClient
from app.streaming_transcribe_client import StreamingTranscribeClient
from app.voice_agent import VoiceAgent
from app.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_transcription_modes():
    """Test both streaming and bucket transcription modes."""
    
    # Read test audio file
    with open('test.webm', 'rb') as f:
        dummy_audio = f.read()
    
    logger.info("=== Testing Transcription Modes ===")
    
    # Test bucket-based transcription (existing method)
    logger.info("\n1. Testing bucket-based transcription...")
    transcribe_client = TranscribeClient()
    
    # Temporarily set mode to bucket
    transcribe_client.current_transcription_mode = "bucket"
    
    bucket_result = await transcribe_client.transcribe_audio_bytes(dummy_audio)
    logger.info(f"Bucket result: {bucket_result}")
    
    # Test streaming transcription
    logger.info("\n2. Testing streaming transcription...")
    
    # Temporarily set mode to streaming
    transcribe_client.current_transcription_mode = "streaming"
    
    streaming_result = await transcribe_client.transcribe_audio_bytes(dummy_audio)
    logger.info(f"Streaming result: {streaming_result}")
    
    # Test system status
    logger.info("\n3. Testing system status...")
    voice_agent = VoiceAgent()
    status = voice_agent.get_system_status()
    logger.info(f"System status: {status}")
    
    return {
        "bucket_result": bucket_result,
        "streaming_result": streaming_result,
        "system_status": status
    }

async def test_streaming_client():
    """Test the streaming transcription client directly."""
    
    logger.info("\n=== Testing Streaming Client ===")
    
    streaming_client = StreamingTranscribeClient()
    
    # Test connection
    connection_ok = streaming_client.test_connection()
    logger.info(f"Streaming connection: {'✅ OK' if connection_ok else '❌ FAILED'}")
    
    return connection_ok

async def test_configuration():
    """Test configuration settings."""
    
    logger.info("\n=== Testing Configuration ===")
    
    logger.info(f"Transcription mode: {Config.TRANSCRIPTION_MODE}")
    logger.info(f"Streaming fallback enabled: {Config.ENABLE_STREAMING_FALLBACK}")
    logger.info(f"Streaming timeout: {Config.STREAMING_TIMEOUT} seconds")
    logger.info(f"AWS region: {Config.AWS_REGION}")
    logger.info(f"S3 bucket: {Config.S3_BUCKET_NAME}")
    
    return {
        "transcription_mode": Config.TRANSCRIPTION_MODE,
        "streaming_fallback": Config.ENABLE_STREAMING_FALLBACK,
        "streaming_timeout": Config.STREAMING_TIMEOUT,
        "aws_region": Config.AWS_REGION,
        "s3_bucket": Config.S3_BUCKET_NAME
    }

async def main():
    """Run all tests."""
    try:
        logger.info("Starting streaming transcription tests...")
        
        # Test configuration
        config_result = await test_configuration()
        
        # Test streaming client
        streaming_result = await test_streaming_client()
        
        # Test transcription modes
        transcription_result = await test_transcription_modes()
        
        logger.info("\n=== Test Summary ===")
        logger.info(f"Configuration: ✅ OK")
        logger.info(f"Streaming client: {'✅ OK' if streaming_result else '❌ FAILED'}")
        logger.info(f"Bucket transcription: {'✅ OK' if transcription_result['bucket_result'].get('success') else '❌ FAILED'}")
        logger.info(f"Streaming transcription: {'✅ OK' if transcription_result['streaming_result'].get('success') else '❌ FAILED'}")
        
        return {
            "config": config_result,
            "streaming_client": streaming_result,
            "transcription": transcription_result
        }
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\nTest completed: {result}") 