#!/usr/bin/env python3
"""
Test script for the voice API endpoints.
"""

import requests
import base64
import json

def test_voice_api():
    """Test the voice processing API."""
    
    base_url = "http://localhost:8000"
    
    print("🎤 Testing Voice Agent API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: System status
    print("\n2. Testing system status...")
    try:
        response = requests.get(f"{base_url}/status")
        print(f"✅ System status: {response.status_code}")
        status = response.json()
        print(f"   Bedrock: {'✅' if status.get('bedrock_connection') else '❌'}")
        print(f"   Transcribe: {'✅' if status.get('transcribe_connection') else '❌'}")
        print(f"   Polly: {'✅' if status.get('polly_connection') else '❌'}")
    except Exception as e:
        print(f"❌ System status failed: {e}")
    
    # Test 3: Text processing
    print("\n3. Testing text processing...")
    try:
        test_text = "What is the capital of France?"
        response = requests.post(
            f"{base_url}/process-text",
            json={"text": test_text}
        )
        print(f"✅ Text processing: {response.status_code}")
        result = response.json()
        print(f"   Response: {result.get('response', 'N/A')}")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Entity: {result.get('entity', 'N/A')}")
        print(f"   Capital: {result.get('capital', 'N/A')}")
    except Exception as e:
        print(f"❌ Text processing failed: {e}")
    
    # Test 4: Voice processing with proper base64
    print("\n4. Testing voice processing...")
    try:
        # Create a simple test audio data (just some bytes)
        test_audio_bytes = b"test_audio_data_for_testing"
        test_audio_base64 = base64.b64encode(test_audio_bytes).decode('utf-8')
        
        response = requests.post(
            f"{base_url}/process-voice",
            json={"audio_data": test_audio_base64}
        )
        print(f"✅ Voice processing: {response.status_code}")
        result = response.json()
        print(f"   Response: {result.get('response', 'N/A')}")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Audio file: {result.get('audio_file_path', 'N/A')}")
        print(f"   Transcribed text: {result.get('transcribed_text', 'N/A')}")
    except Exception as e:
        print(f"❌ Voice processing failed: {e}")
    
    # Test 5: Get available voices
    print("\n5. Testing voices endpoint...")
    try:
        response = requests.get(f"{base_url}/voices")
        print(f"✅ Voices: {response.status_code}")
        result = response.json()
        if result.get('success'):
            voices = result.get('voices', [])
            print(f"   Found {len(voices)} voices")
            for voice in voices[:3]:  # Show first 3
                print(f"   - {voice.get('name', 'N/A')} ({voice.get('id', 'N/A')})")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Voices failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Voice API Testing Complete!")

if __name__ == "__main__":
    test_voice_api() 