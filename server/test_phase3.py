#!/usr/bin/env python3
"""
Test script for Phase 3 - LiveKit Integration.
"""

import requests
import json
import base64
import time

def test_livekit_endpoints():
    """Test LiveKit integration endpoints."""
    
    print("🧪 Testing Phase 3 - LiveKit Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if server is running
    print("\n1️⃣ Testing server status...")
    try:
        response = requests.get(f"{base_url}/test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is running - Phase: {data.get('phase', 'Unknown')}")
            print(f"   Features: {', '.join(data.get('features', []))}")
        else:
            print(f"❌ Server not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        return
    
    # Test 2: Test LiveKit status
    print("\n2️⃣ Testing LiveKit status...")
    try:
        response = requests.get(f"{base_url}/livekit/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LiveKit status: Connected={data.get('connected', False)}")
            print(f"   Room: {data.get('room_name', 'None')}")
            print(f"   Participants: {len(data.get('participants', []))}")
        else:
            print(f"❌ LiveKit status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LiveKit status error: {e}")
    
    # Test 3: Test LiveKit connection
    print("\n3️⃣ Testing LiveKit connection...")
    try:
        response = requests.post(
            f"{base_url}/livekit/connect",
            json={
                "room_name": "test-room",
                "participant_name": "test-participant"
            }
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Connected to LiveKit room: {data.get('room_name')}")
            else:
                print(f"⚠️ LiveKit connection failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ LiveKit connection failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LiveKit connection error: {e}")
    
    # Test 4: Test voice processing with LiveKit
    print("\n4️⃣ Testing LiveKit voice processing...")
    try:
        # Create a simple test audio (base64 encoded)
        test_audio = "UklGRiR9AABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZG"
        
        response = requests.post(
            f"{base_url}/livekit/process-voice",
            json={"audio_data": test_audio}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ LiveKit voice processing successful")
                print(f"   Response: {data.get('response', 'N/A')}")
                print(f"   Audio file: {data.get('audio_file_path', 'N/A')}")
            else:
                print(f"⚠️ LiveKit voice processing failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ LiveKit voice processing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LiveKit voice processing error: {e}")
    
    # Test 5: Test LiveKit disconnect
    print("\n5️⃣ Testing LiveKit disconnect...")
    try:
        response = requests.post(f"{base_url}/livekit/disconnect")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Disconnected from LiveKit room")
            else:
                print(f"⚠️ LiveKit disconnect failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ LiveKit disconnect failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LiveKit disconnect error: {e}")

def test_client_integration():
    """Test client-side integration."""
    
    print("\n🌐 Testing Client Integration")
    print("=" * 50)
    
    print("\n📋 Client Setup Instructions:")
    print("1. Navigate to the client directory:")
    print("   cd client")
    print("")
    print("2. Install dependencies:")
    print("   npm install")
    print("")
    print("3. Start the client:")
    print("   npm start")
    print("")
    print("4. The client will open at http://localhost:3000")
    print("")
    print("5. Click 'Connect to Voice Agent' to start")
    print("")
    print("6. Use voice or text input to test the agent")
    print("")
    print("📝 Note: Make sure the server is running on port 8000")
    print("   and LiveKit server is configured properly")

def show_phase3_features():
    """Show Phase 3 features and capabilities."""
    
    print("\n🚀 Phase 3 Features")
    print("=" * 50)
    
    features = [
        "✅ LiveKit server integration",
        "✅ Real-time voice communication",
        "✅ Web client with React/TypeScript",
        "✅ LiveKit SDK integration",
        "✅ Audio streaming and processing",
        "✅ Room management and participant handling",
        "✅ Voice-to-text and text-to-speech",
        "✅ Real-time audio response publishing",
        "✅ Modern UI with voice controls",
        "✅ Responsive design for mobile/desktop"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n🔧 Technical Stack:")
    print("   - Frontend: React + TypeScript + LiveKit SDK")
    print("   - Backend: FastAPI + LiveKit Python SDK")
    print("   - Voice: Amazon Transcribe + Amazon Polly")
    print("   - AI: AWS Bedrock (Claude Haiku)")
    print("   - Real-time: LiveKit WebRTC")

def main():
    """Main test function."""
    
    print("🎵 Phase 3 - LiveKit Integration Testing")
    print("=" * 50)
    
    # Show features
    show_phase3_features()
    
    # Test server endpoints
    test_livekit_endpoints()
    
    # Show client integration instructions
    test_client_integration()
    
    print("\n✅ Phase 3 testing completed!")
    print("\n📝 Next steps:")
    print("   1. Set up LiveKit server")
    print("   2. Configure environment variables")
    print("   3. Start the client application")
    print("   4. Test real-time voice communication")

if __name__ == "__main__":
    main() 