#!/usr/bin/env python3
"""
Script to generate test audio files in different formats.
"""

import wave
import numpy as np
import subprocess
import os

def create_test_wav():
    """Create a test WAV file with a sine wave."""
    # Parameters
    duration = 3  # seconds
    sample_rate = 16000
    frequency = 440  # Hz (A4 note)
    amplitude = 0.5
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    samples = (amplitude * np.sin(2 * np.pi * frequency * t)).astype(np.float32)
    
    # Convert to 16-bit PCM
    samples = (samples * 32767).astype(np.int16)
    
    # Save as WAV
    with wave.open('test.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())
    
    print("Created test.wav")
    return 'test.wav'

def convert_to_webm(wav_path):
    """Convert WAV to WebM."""
    webm_path = wav_path.replace('.wav', '.webm')
    subprocess.run([
        'ffmpeg',
        '-i', wav_path,
        '-c:a', 'libopus',
        '-b:a', '96k',
        '-y',
        webm_path
    ], check=True)
    print(f"Created {webm_path}")
    return webm_path

def main():
    """Generate test audio files."""
    print("\n=== Generating Test Audio Files ===\n")
    
    try:
        # Create WAV file
        wav_path = create_test_wav()
        
        # Convert to WebM
        webm_path = convert_to_webm(wav_path)
        
        # Print file info
        print("\nFile Information:")
        for path in [wav_path, webm_path]:
            size = os.path.getsize(path)
            print(f"{path}: {size} bytes")
        
        print("\n✅ Successfully created test audio files!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 