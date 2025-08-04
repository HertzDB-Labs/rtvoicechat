#!/usr/bin/env python3
"""
POC test script for Amazon Transcribe WebSocket streaming.
This script tests direct WebSocket connection to Amazon Transcribe streaming service.
"""

import asyncio
import json
import time
import uuid
import base64
import hmac
import hashlib
import websockets
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

# AWS credentials from environment
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

def get_signature_key(key, date_stamp, region_name, service_name):
    """Get AWS signature key."""
    k_date = hmac.new(f'AWS4{key}'.encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
    k_region = hmac.new(k_date, region_name.encode('utf-8'), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service_name.encode('utf-8'), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, 'aws4_request'.encode('utf-8'), hashlib.sha256).digest()
    return k_signing

def create_presigned_url():
    """Create presigned URL for WebSocket connection."""
    
    # Create a date for headers and the credential string
    t = datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    # Service details
    service = 'transcribe'
    algorithm = 'AWS4-HMAC-SHA256'
    
    # Create canonical URI and query string
    canonical_uri = '/v2/streaming-transcription'
    session_id = str(uuid.uuid4())
    
    # Parameters required by Transcribe streaming
    params = {
        'language-code': 'en-US',
        'media-encoding': 'pcm',
        'sample-rate': '16000',
        'session-id': session_id,
        'enable-partial-results-stabilization': 'true'
    }
    
    # Add AWS auth params
    credential_scope = f"{date_stamp}/{AWS_REGION}/{service}/aws4_request"
    params.update({
        'X-Amz-Algorithm': algorithm,
        'X-Amz-Credential': f"{AWS_ACCESS_KEY}/{credential_scope}",
        'X-Amz-Date': amz_date,
        'X-Amz-Expires': '300',
        'X-Amz-SignedHeaders': 'host'
    })
    
    # Create canonical querystring
    canonical_querystring = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    
    # Create canonical headers
    canonical_headers = f"host:transcribestreaming.{AWS_REGION}.amazonaws.com\n"
    
    # Create payload hash
    payload_hash = hashlib.sha256(''.encode('utf-8')).hexdigest()
    
    # Combine elements to create canonical request
    canonical_request = '\n'.join([
        'GET',
        canonical_uri,
        canonical_querystring,
        canonical_headers,
        'host',
        payload_hash
    ])
    
    # Create string to sign
    credential_scope = f"{date_stamp}/{AWS_REGION}/{service}/aws4_request"
    string_to_sign = '\n'.join([
        algorithm,
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    ])
    
    # Calculate signature
    signing_key = get_signature_key(AWS_SECRET_KEY, date_stamp, AWS_REGION, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Create URL
    endpoint = f"wss://transcribestreaming.{AWS_REGION}.amazonaws.com{canonical_uri}"
    request_url = f"{endpoint}?{canonical_querystring}&X-Amz-Signature={signature}"
    
    return request_url

async def test_transcribe_streaming():
    """Test Amazon Transcribe streaming with WebSocket."""
    try:
        # Get presigned URL
        websocket_url = create_presigned_url()
        print(f"\nTrying to connect to: {websocket_url}\n")
        
        # Connect to WebSocket
        async with websockets.connect(websocket_url) as websocket:
            print("Connected to WebSocket!")
            
            # Create a simple audio event (empty for testing connection)
            audio_event = {
                "AudioEvent": {
                    "AudioChunk": ""
                }
            }
            
            # Send audio event
            await websocket.send(json.dumps(audio_event))
            print("Sent audio event")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received response: {response}")
                return True
            except asyncio.TimeoutError:
                print("Timeout waiting for response")
                return False
            
    except Exception as e:
        print(f"Error in streaming test: {e}")
        return False

async def main():
    """Run the POC test."""
    print("\n=== Amazon Transcribe WebSocket Streaming POC Test ===\n")
    
    # Check AWS credentials
    print("AWS Credentials:")
    print(f"Access Key: {AWS_ACCESS_KEY[:10]}..." if AWS_ACCESS_KEY else "Not found")
    print(f"Secret Key: {AWS_SECRET_KEY[:10]}..." if AWS_SECRET_KEY else "Not found")
    print(f"Region: {AWS_REGION}")
    
    # Test streaming
    success = await test_transcribe_streaming()
    
    print("\n=== Test Results ===")
    print("Streaming test:", "✅ SUCCESS" if success else "❌ FAILED")

if __name__ == "__main__":
    asyncio.run(main()) 