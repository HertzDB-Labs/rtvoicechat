#!/usr/bin/env python3
"""
Test script for transcription functionality.
This script tests the transcription client to identify issues.
"""

import asyncio
import logging
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.transcribe_client import TranscribeClient
from app.voice_agent import VoiceAgent
from app.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_transcribe_client():
    """Test the transcription client directly."""
    
    transcribe_client = TranscribeClient()
    
    # Test connection
    logger.info("Testing Transcribe connection...")
    connection_ok = transcribe_client.test_connection()
    logger.info(f"Transcribe connection: {'✅ OK' if connection_ok else '❌ FAILED'}")
    
    # Test with dummy audio data
    logger.info("Testing transcription with dummy audio data...")
    dummy_audio = b"dummy_audio_data_for_testing" * 100  # Make it larger
    
    result = await transcribe_client.transcribe_audio_bytes(dummy_audio)
    logger.info(f"Transcription result: {result}")
    
    if result.get("success"):
        logger.info("✅ Transcription test completed")
        logger.info(f"Transcription: {result.get('transcription')}")
        logger.info(f"Note: {result.get('note', 'No note')}")
    else:
        logger.error(f"❌ Transcription failed: {result.get('error')}")

async def test_voice_agent_transcription():
    """Test transcription through the voice agent."""
    
    voice_agent = VoiceAgent()
    
    # Test with dummy audio data
    logger.info("Testing voice agent transcription...")
    dummy_audio = b"dummy_audio_data_for_testing" * 100
    
    result = await voice_agent.process_voice_input(dummy_audio)
    logger.info(f"Voice agent result: {result}")
    
    if result.get("success"):
        logger.info("✅ Voice agent transcription completed")
        logger.info(f"Transcribed text: {result.get('transcribed_text')}")
        logger.info(f"Response: {result.get('response')}")
    else:
        logger.error(f"❌ Voice agent transcription failed: {result.get('error')}")

async def test_real_transcription():
    """Test with a real audio file if available."""
    
    # Check if there are any audio files in the audio directory
    audio_dir = Config.AUDIO_STORAGE_PATH
    if os.path.exists(audio_dir):
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.wav', '.mp3'))]
        
        if audio_files:
            logger.info(f"Found audio files: {audio_files}")
            
            # Test with the first audio file
            audio_file_path = os.path.join(audio_dir, audio_files[0])
            logger.info(f"Testing with audio file: {audio_file_path}")
            
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            voice_agent = VoiceAgent()
            result = await voice_agent.process_voice_input(audio_data)
            
            logger.info(f"Real audio transcription result: {result}")
            
            if result.get("success"):
                logger.info("✅ Real audio transcription completed")
                logger.info(f"Transcribed text: {result.get('transcribed_text')}")
                logger.info(f"Response: {result.get('response')}")
            else:
                logger.error(f"❌ Real audio transcription failed: {result.get('error')}")
        else:
            logger.info("No audio files found in audio directory")
    else:
        logger.info("Audio directory does not exist")

async def main():
    """Main test function."""
    logger.info("Starting transcription tests...")
    
    # Test 1: Direct transcription client
    await test_transcribe_client()
    
    # Test 2: Voice agent transcription
    await test_voice_agent_transcription()
    
    # Test 3: Real audio file (if available)
    await test_real_transcription()
    
    logger.info("Transcription tests completed.")

if __name__ == "__main__":
    asyncio.run(main()) 