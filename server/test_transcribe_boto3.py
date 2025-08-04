#!/usr/bin/env python3
"""
POC test script for Amazon Transcribe streaming using boto3.
This script tests streaming transcription using the AWS SDK.
"""

import asyncio
import json
import os
from dotenv import load_dotenv
import boto3
import time

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

# AWS credentials from environment
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

def test_transcribe_streaming():
    """Test Amazon Transcribe streaming using boto3."""
    try:
        # Create clients
        transcribe_client = boto3.client('transcribe',
                                       region_name=AWS_REGION,
                                       aws_access_key_id=AWS_ACCESS_KEY,
                                       aws_secret_access_key=AWS_SECRET_KEY)
        
        streaming_client = boto3.client('transcribe-streaming',
                                      region_name=AWS_REGION,
                                      aws_access_key_id=AWS_ACCESS_KEY,
                                      aws_secret_access_key=AWS_SECRET_KEY)
        
        print("\nTesting transcribe client connection...")
        
        # Test batch transcription connection
        response = transcribe_client.list_transcription_jobs(MaxResults=1)
        print("Successfully connected to Transcribe!")
        
        # Extract job names from response
        jobs = response.get('TranscriptionJobSummaries', [])
        job_names = [job.get('TranscriptionJobName') for job in jobs]
        print(f"Recent jobs: {job_names}")
        
        # Test streaming capabilities
        print("\nTesting streaming capabilities...")
        try:
            # Try to start a streaming session
            response = streaming_client.start_stream_transcription(
                LanguageCode='en-US',
                MediaSampleRateHertz=16000,
                MediaEncoding='pcm'
            )
            print("Streaming transcription supported!")
            print(f"Response: {response}")
            return True
        except Exception as e:
            print(f"Streaming test error: {e}")
            return False
        
    except Exception as e:
        print(f"Error in streaming test: {e}")
        return False

def main():
    """Run the POC test."""
    print("\n=== Amazon Transcribe Streaming POC Test (boto3) ===\n")
    
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