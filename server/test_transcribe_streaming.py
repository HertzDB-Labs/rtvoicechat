#!/usr/bin/env python3
"""
Test script for Amazon Transcribe streaming using AWS SDK.
"""

import asyncio
import json
import os
import time
import wave
import boto3
from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, ClientError

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

# AWS credentials from environment
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

def create_test_audio():
    """Create a test WAV file."""
    try:
        # Create a simple WAV file with 1 second of silence
        with wave.open('test.wav', 'wb') as wav_file:
            # Set parameters
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(16000)  # 16kHz
            
            # Create 1 second of silence
            samples = b'\x00\x00' * 16000
            wav_file.writeframes(samples)
        
        return True
    except Exception as e:
        print(f"Error creating test audio: {e}")
        return False

def test_transcribe_streaming():
    """Test Amazon Transcribe streaming."""
    try:
        # Create test audio file
        if not create_test_audio():
            return False
        
        # Create transcribe client
        client = boto3.client('transcribe',
                            region_name=AWS_REGION,
                            aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_KEY)
        
        print("\nTesting transcribe client connection...")
        
        # Test connection by starting a streaming session
        try:
            # Open test audio file
            with open('test.wav', 'rb') as audio_file:
                # Read audio data
                audio_data = audio_file.read()
                
                # Start streaming transcription
                print("\nStarting streaming transcription...")
                stream = client.start_transcription_stream(
                    LanguageCode='en-US',
                    MediaEncoding='pcm',
                    MediaSampleRateHertz=16000,
                    AudioStream=audio_data
                )
                
                print("Successfully started streaming!")
                print(f"Stream info: {stream}")
                return True
                
        except (BotoCoreError, ClientError) as e:
            print(f"AWS error: {e}")
            return False
            
        except Exception as e:
            print(f"Error in streaming: {e}")
            return False
            
        finally:
            # Clean up test file
            if os.path.exists('test.wav'):
                os.remove('test.wav')
        
    except Exception as e:
        print(f"Error in test: {e}")
        return False

def main():
    """Run the test."""
    print("\n=== Amazon Transcribe Streaming Test ===\n")
    
    # Check AWS credentials
    print("AWS Credentials:")
    print(f"Access Key: {AWS_ACCESS_KEY[:10]}..." if AWS_ACCESS_KEY else "Not found")
    print(f"Secret Key: {AWS_SECRET_KEY[:10]}..." if AWS_SECRET_KEY else "Not found")
    print(f"Region: {AWS_REGION}")
    
    # Test streaming
    success = test_transcribe_streaming()
    
    print("\n=== Test Results ===")
    print("Streaming test:", "✅ SUCCESS" if success else "❌ FAILED")

if __name__ == "__main__":
    main() 