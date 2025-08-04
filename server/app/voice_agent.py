from typing import Dict, Any, Optional
from .bedrock_client import BedrockClient
from .data_handler import DataHandler
from .transcribe_client import TranscribeClient
from .polly_client import PollyClient
from .config import Config

class VoiceAgent:
    """Main voice agent that coordinates all components."""
    
    def __init__(self):
        self.bedrock_client = BedrockClient()
        self.data_handler = DataHandler()
        self.transcribe_client = TranscribeClient()
        self.polly_client = PollyClient()
    
    async def process_text_input(self, text: str) -> Dict[str, Any]:
        """
        Process text input and return appropriate response.
        
        Args:
            text: User's text input
            
        Returns:
            Dict containing response text and metadata
        """
        try:
            # Analyze intent using Bedrock
            intent_result = await self.bedrock_client.analyze_intent(text)
            
            if intent_result.get("error"):
                return {
                    "response": "I'm sorry, I'm having trouble processing your request right now.",
                    "success": False,
                    "error": intent_result["error"]
                }
            
            # Check if it's a capital query
            if intent_result.get("is_capital_query"):
                entity = intent_result.get("entity")
                query_type = intent_result.get("query_type")
                
                if entity:
                    # Look up the capital
                    capital = self.data_handler.find_capital(entity)
                    
                    if capital:
                        # Generate natural response
                        response = await self.bedrock_client.generate_response(
                            query_type, entity, capital
                        )
                        return {
                            "response": response,
                            "success": True,
                            "query_type": query_type,
                            "entity": entity,
                            "capital": capital
                        }
                    else:
                        return {
                            "response": f"I'm sorry, I don't have information about the capital of {entity}.",
                            "success": True,
                            "query_type": query_type,
                            "entity": entity,
                            "capital": None
                        }
                else:
                    return {
                        "response": "I'm sorry, I couldn't understand which country or state you're asking about.",
                        "success": True,
                        "query_type": "unknown",
                        "entity": None,
                        "capital": None
                    }
            else:
                # Not a capital query
                return {
                    "response": Config.UNSUPPORTED_QUERY_RESPONSE,
                    "success": True,
                    "query_type": "other",
                    "entity": None,
                    "capital": None
                }
                
        except Exception as e:
            return {
                "response": "I'm sorry, I encountered an error processing your request.",
                "success": False,
                "error": str(e)
            }
    
    async def process_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process voice input with speech-to-text and text-to-speech.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Dict containing response text, audio, and metadata
        """
        try:
            # Step 1: Transcribe audio to text
            transcribe_result = await self.transcribe_client.transcribe_audio_bytes(audio_data)
            
            if not transcribe_result.get("success"):
                return {
                    "response": "I'm sorry, I couldn't understand your voice input.",
                    "success": False,
                    "error": transcribe_result.get("error", "Transcription failed")
                }
            
            # Use actual transcription result
            transcribed_text = transcribe_result.get("transcription")
            if not transcribed_text:
                return {
                    "response": "I'm sorry, I couldn't transcribe your voice input.",
                    "success": False,
                    "error": "No transcription result"
                }
            
            # Step 2: Process the transcribed text
            text_result = await self.process_text_input(transcribed_text)
            
            if not text_result.get("success"):
                return text_result
            
            # Step 3: Convert response to speech
            response_text = text_result.get("response", "I'm sorry, I couldn't process your request.")
            polly_result = await self.polly_client.synthesize_speech_bytes(response_text)
            
            if not polly_result.get("success"):
                return {
                    "response": response_text,
                    "success": True,
                    "audio_bytes": None,
                    "error": "Speech synthesis failed"
                }
            
            return {
                "response": response_text,
                "success": True,
                "audio_bytes": polly_result.get("audio_bytes"),
                "transcribed_text": transcribed_text,
                "query_type": text_result.get("query_type"),
                "entity": text_result.get("entity"),
                "capital": text_result.get("capital")
            }
            
        except Exception as e:
            return {
                "response": "I'm sorry, I encountered an error processing your voice input.",
                "success": False,
                "error": str(e)
            }
    
    async def process_voice_with_audio_response(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process voice input and return both text and audio response.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Dict containing response text, audio file path, and metadata
        """
        try:
            # Step 1: Transcribe audio to text
            transcribe_result = await self.transcribe_client.transcribe_audio_bytes(audio_data)
            
            if not transcribe_result.get("success"):
                return {
                    "response": "I'm sorry, I couldn't understand your voice input.",
                    "success": False,
                    "error": transcribe_result.get("error", "Transcription failed")
                }
            
            # Use actual transcription result
            transcribed_text = transcribe_result.get("transcription")
            if not transcribed_text:
                return {
                    "response": "I'm sorry, I couldn't transcribe your voice input.",
                    "success": False,
                    "error": "No transcription result"
                }
            
            # Step 2: Process the transcribed text
            text_result = await self.process_text_input(transcribed_text)
            
            if not text_result.get("success"):
                return text_result
            
            # Step 3: Convert response to speech and save to file
            response_text = text_result.get("response", "I'm sorry, I couldn't process your request.")
            polly_result = await self.polly_client.synthesize_speech(response_text)
            
            if not polly_result.get("success"):
                return {
                    "response": response_text,
                    "success": True,
                    "audio_file_path": None,
                    "error": "Speech synthesis failed"
                }
            
            return {
                "response": response_text,
                "success": True,
                "audio_file_path": polly_result.get("audio_file_path"),
                "transcribed_text": transcribed_text,
                "query_type": text_result.get("query_type"),
                "entity": text_result.get("entity"),
                "capital": text_result.get("capital")
            }
            
        except Exception as e:
            return {
                "response": "I'm sorry, I encountered an error processing your voice input.",
                "success": False,
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health information."""
        bedrock_status = self.bedrock_client.test_connection()
        transcribe_status = self.transcribe_client.test_connection()
        streaming_status = self.transcribe_client.streaming_client.test_connection()
        polly_status = self.polly_client.test_connection()
        data_summary = self.data_handler.get_data_summary()
        
        return {
            "bedrock_connection": bedrock_status,
            "transcribe_connection": transcribe_status,
            "streaming_transcribe_connection": streaming_status,
            "polly_connection": polly_status,
            "data_loaded": data_summary,
            "config": {
                "aws_region": Config.AWS_REGION,
                "bedrock_model": Config.BEDROCK_MODEL_ID,
                "transcription_mode": Config.TRANSCRIPTION_MODE,
                "streaming_fallback_enabled": Config.ENABLE_STREAMING_FALLBACK,
                "debug_mode": Config.DEBUG
            }
        }
    
    def get_available_entities(self) -> Dict[str, Any]:
        """Get lists of available countries and states."""
        return {
            "countries": self.data_handler.get_all_countries(),
            "states": self.data_handler.get_all_states()
        }
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available Polly voices."""
        return self.polly_client.get_available_voices() 