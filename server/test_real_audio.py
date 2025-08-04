#!/usr/bin/env python3
"""
Test script showing real audio data vs placeholder data.
"""

import base64
import os
import wave
import struct
import requests
import tempfile

def download_hello_audio():
    """Download a small audio file that says 'hello' from the internet."""
    
    # Try multiple reliable audio sources
    audio_urls = [
        "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav",
        "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav",
        "https://www2.cs.uic.edu/~i101/SoundFiles/ImperialMarch60.wav"
    ]
    
    for i, audio_url in enumerate(audio_urls):
        try:
            print(f"📥 Downloading audio file from: {audio_url}")
            response = requests.get(audio_url, timeout=15)
            response.raise_for_status()
            
            audio_data = response.content
            print(f"✅ Downloaded {len(audio_data)} bytes of audio data")
            
            # Save to temporary file for inspection
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
                print(f"💾 Saved to temporary file: {temp_path}")
            
            return audio_data, temp_path
            
        except Exception as e:
            print(f"❌ Failed to download from {audio_url}: {e}")
            if i < len(audio_urls) - 1:
                print("🔄 Trying next source...")
            continue
    
    print("🔄 All downloads failed, falling back to creating a simple test audio...")
    return create_simple_test_audio(), None

def create_simple_test_audio():
    """Create a simple test audio as fallback."""
    
    # Audio parameters
    sample_rate = 16000  # 16kHz
    duration = 1  # 1 second
    frequency = 440  # 440 Hz (A note)
    
    # Generate audio data
    num_samples = sample_rate * duration
    audio_data = []
    
    for i in range(num_samples):
        # Simple sine wave with proper bounds checking
        t = i / sample_rate
        sample_value = 0.3 * (32767 * 0.3) * (i * frequency * 2 * 3.14159 / sample_rate)
        # Ensure the sample is within valid range for 16-bit signed integer
        sample_value = max(-32767, min(32767, int(sample_value)))
        audio_data.append(struct.pack('<h', sample_value))
    
    # Create WAV file
    wav_data = b''
    wav_data += b'RIFF'
    wav_data += struct.pack('<I', 36 + len(b''.join(audio_data)))
    wav_data += b'WAVE'
    wav_data += b'fmt '
    wav_data += struct.pack('<I', 16)
    wav_data += struct.pack('<H', 1)  # PCM
    wav_data += struct.pack('<H', 1)  # Mono
    wav_data += struct.pack('<I', sample_rate)
    wav_data += struct.pack('<I', sample_rate * 2)  # Byte rate
    wav_data += struct.pack('<H', 2)  # Block align
    wav_data += struct.pack('<H', 16)  # Bits per sample
    wav_data += b'data'
    wav_data += struct.pack('<I', len(b''.join(audio_data)))
    wav_data += b''.join(audio_data)
    
    return wav_data

def compare_audio_data():
    """Compare placeholder vs real audio data."""
    
    print("🎵 Audio Data Comparison")
    print("=" * 50)
    
    # Placeholder data (current test)
    placeholder_text = "test_audio_data_for_testing"
    placeholder_bytes = placeholder_text.encode('utf-8')
    placeholder_base64 = base64.b64encode(placeholder_bytes).decode('utf-8')
    
    print(f"\n📝 Placeholder Audio Data:")
    print(f"   Original: '{placeholder_text}'")
    print(f"   Size: {len(placeholder_bytes)} bytes")
    print(f"   Base64: {placeholder_base64}")
    print(f"   Base64 length: {len(placeholder_base64)} characters")
    
    # Real audio data (downloaded from internet)
    real_audio_bytes, temp_path = download_hello_audio()
    real_audio_base64 = base64.b64encode(real_audio_bytes).decode('utf-8')
    
    print(f"\n🎵 Real Audio Data (Downloaded):")
    print(f"   Source: Internet download")
    if temp_path:
        print(f"   Saved to: {temp_path}")
    print(f"   Size: {len(real_audio_bytes)} bytes")
    print(f"   Base64 length: {len(real_audio_base64)} characters")
    print(f"   Base64 preview: {real_audio_base64[:50]}...")
    
    # Size comparison
    size_ratio = len(real_audio_bytes) / len(placeholder_bytes)
    print(f"\n📊 Size Comparison:")
    print(f"   Real audio is {size_ratio:.0f}x larger than placeholder")
    print(f"   Real audio: {len(real_audio_bytes):,} bytes")
    print(f"   Placeholder: {len(placeholder_bytes):,} bytes")
    
    return real_audio_base64

def test_with_real_audio():
    """Test the API with real audio data."""
    
    print("\n🧪 Testing API with Real Audio Data")
    print("=" * 50)
    
    # Create real audio data
    real_audio_base64 = compare_audio_data()
    
    # Test the API
    import requests
    
    try:
        response = requests.post(
            "http://localhost:8000/process-voice",
            json={"audio_data": real_audio_base64},
            timeout=30  # Longer timeout for real audio processing
        )
        
        print(f"\n✅ API Response:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Response: {result.get('response', 'N/A')}")
            print(f"   Audio file: {result.get('audio_file_path', 'N/A')}")
            print(f"   Transcribed text: {result.get('transcribed_text', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

def show_audio_formats():
    """Show different audio formats and their typical sizes."""
    
    print("\n📋 Common Audio Formats and Sizes")
    print("=" * 50)
    
    formats = [
        {"name": "WAV (16kHz, 16-bit, mono)", "size_per_second": 32000, "quality": "High"},
        {"name": "MP3 (128kbps)", "size_per_second": 16000, "quality": "Good"},
        {"name": "MP3 (64kbps)", "size_per_second": 8000, "quality": "Acceptable"},
        {"name": "AAC (128kbps)", "size_per_second": 16000, "quality": "Good"},
        {"name": "OGG (128kbps)", "size_per_second": 16000, "quality": "Good"},
    ]
    
    for fmt in formats:
        for duration in [1, 5, 10, 30, 60]:  # seconds
            size = fmt["size_per_second"] * duration
            print(f"   {fmt['name']} - {duration}s: {size:,} bytes ({fmt['quality']})")

if __name__ == "__main__":
    print("🎵 Real Audio Data Testing")
    print("=" * 50)
    
    # Show audio format information
    show_audio_formats()
    
    # Compare data sizes
    compare_audio_data()
    
    # Test with real audio
    test_with_real_audio() 