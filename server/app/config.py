import os
from dotenv import load_dotenv

# Load .env from parent directory (project root)
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

class Config:
    """Configuration settings for the Voice Agent application."""
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # S3 Configuration for Transcribe
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "voice-agent-transcribe")
    
    # Transcription Configuration
    TRANSCRIPTION_MODE = os.getenv("TRANSCRIPTION_MODE", "streaming")  # "streaming" or "bucket"
    ENABLE_STREAMING_FALLBACK = os.getenv("ENABLE_STREAMING_FALLBACK", "true").lower() == "true"
    STREAMING_TIMEOUT = int(os.getenv("STREAMING_TIMEOUT", "30"))
    
    # LiveKit Configuration
    LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
    LIVEKIT_TOKEN = os.getenv("LIVEKIT_TOKEN", "your_token_here")
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Data file paths
    COUNTRIES_DATA_PATH = "data/countries.json"
    STATES_DATA_PATH = "data/us-states.json"
    
    # Audio storage
    AUDIO_STORAGE_PATH = "audio"
    
    # Bedrock model configuration - Updated to Claude 3 Haiku
    BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # Response templates
    UNSUPPORTED_QUERY_RESPONSE = "I'm sorry, but I can only provide information about country and state capitals. For other questions, this information is not available." 