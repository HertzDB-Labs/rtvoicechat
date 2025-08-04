import boto3
import json
import os
from typing import Dict, Any, Optional
from .config import Config

class PollyClient:
    """Client for Amazon Polly text-to-speech integration."""
    
    def __init__(self):
        self.client = boto3.client(
            'polly',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
    
    async def synthesize_speech(self, text: str, voice_id: str = "Joanna") -> Dict[str, Any]:
        """
        Convert text to speech using Amazon Polly.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (default: Joanna)
            
        Returns:
            Dict containing audio data and metadata
        """
        try:
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine='neural'  # Use neural engine for better quality
            )
            
            # Save audio to file
            audio_file_path = os.path.join(Config.AUDIO_STORAGE_PATH, f"response_{hash(text)}.mp3")
            os.makedirs(Config.AUDIO_STORAGE_PATH, exist_ok=True)
            
            with open(audio_file_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            return {
                "success": True,
                "audio_file_path": audio_file_path,
                "voice_id": voice_id,
                "text": text
            }
            
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_file_path": None
            }
    
    async def synthesize_speech_bytes(self, text: str, voice_id: str = "Joanna") -> Dict[str, Any]:
        """
        Convert text to speech and return as bytes.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (default: Joanna)
            
        Returns:
            Dict containing audio bytes and metadata
        """
        try:
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine='neural'
            )
            
            audio_bytes = response['AudioStream'].read()
            
            return {
                "success": True,
                "audio_bytes": audio_bytes,
                "voice_id": voice_id,
                "text": text
            }
            
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_bytes": None
            }
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices."""
        try:
            response = self.client.describe_voices(
                Engine='neural'
            )
            
            voices = []
            for voice in response['Voices']:
                voices.append({
                    "id": voice['Id'],
                    "name": voice['Name'],
                    "language": voice['LanguageCode'],
                    "gender": voice['Gender']
                })
            
            return {
                "success": True,
                "voices": voices
            }
            
        except Exception as e:
            print(f"Error getting voices: {e}")
            return {
                "success": False,
                "error": str(e),
                "voices": []
            }
    
    def test_connection(self) -> bool:
        """Test the Polly connection."""
        try:
            # Try to describe voices to test connection
            self.client.describe_voices(Engine='neural')
            return True
        except Exception as e:
            print(f"Polly connection test failed: {e}")
            return False 