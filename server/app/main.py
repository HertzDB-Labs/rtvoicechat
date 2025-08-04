from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import base64
import os

from .voice_agent import VoiceAgent
from .livekit_client import LiveKitVoiceAgent
from .config import Config

# Initialize FastAPI app
app = FastAPI(
    title="Voice Agent API",
    description="A voice agent that answers questions about country and state capitals",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize voice agent and LiveKit client
voice_agent = VoiceAgent()
livekit_agent = LiveKitVoiceAgent()

# Pydantic models for request/response
class TextRequest(BaseModel):
    text: str

class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio

class VoiceResponse(BaseModel):
    response: str
    success: bool
    audio_file_path: Optional[str] = None
    transcribed_text: Optional[str] = None
    query_type: Optional[str] = None
    entity: Optional[str] = None
    capital: Optional[str] = None
    error: Optional[str] = None

class Response(BaseModel):
    response: str
    success: bool
    query_type: Optional[str] = None
    entity: Optional[str] = None
    capital: Optional[str] = None
    error: Optional[str] = None

class LiveKitConnectRequest(BaseModel):
    room_name: str
    participant_name: str

class LiveKitVoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio

def decode_base64_audio(audio_data: str) -> bytes:
    """Safely decode base64 audio data with proper padding."""
    try:
        # Add padding if needed
        padding = 4 - (len(audio_data) % 4)
        if padding != 4:
            audio_data += '=' * padding
        
        return base64.b64decode(audio_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Voice Agent API",
        "version": "2.0.0",
        "description": "A voice agent that answers questions about country and state capitals",
        "phase": "Phase 3 - LiveKit Integration"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "voice-agent"}

@app.get("/status")
async def get_status():
    """Get system status and health information."""
    return voice_agent.get_system_status()

@app.get("/entities")
async def get_entities():
    """Get available countries and states."""
    return voice_agent.get_available_entities()

@app.get("/voices")
async def get_voices():
    """Get available Polly voices."""
    return await voice_agent.get_available_voices()

@app.post("/process-text", response_model=Response)
async def process_text(request: TextRequest):
    """
    Process text input and return response.
    
    This endpoint analyzes the text to determine if it's asking about a country or state capital,
    and returns the appropriate response.
    """
    try:
        result = await voice_agent.process_text_input(request.text)
        return Response(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/process-voice", response_model=VoiceResponse)
async def process_voice(request: VoiceRequest):
    """
    Process voice input with speech-to-text and text-to-speech.
    
    This endpoint processes audio data, transcribes it to text, processes the text,
    and returns both text and audio responses.
    """
    try:
        # Decode base64 audio data with proper error handling
        audio_data = decode_base64_audio(request.audio_data)
        
        # Process voice input
        result = await voice_agent.process_voice_with_audio_response(audio_data)
        return VoiceResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing voice: {str(e)}")

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve audio files."""
    audio_path = os.path.join(Config.AUDIO_STORAGE_PATH, filename)
    if os.path.exists(audio_path):
        return FileResponse(audio_path, media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice communication."""
    await websocket.accept()
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_text()
            
            try:
                # Decode base64 audio data with proper error handling
                audio_data = decode_base64_audio(data)
                
                # Process voice input
                result = await voice_agent.process_voice_input(audio_data)
                
                # Send response back
                await websocket.send_json(result)
                
            except Exception as e:
                await websocket.send_json({
                    "success": False,
                    "error": str(e)
                })
                
    except WebSocketDisconnect:
        print("WebSocket client disconnected")

@app.get("/test")
async def test_endpoint():
    """Test endpoint for development."""
    return {
        "message": "Voice Agent API is running",
        "phase": "Phase 3 - LiveKit Integration",
        "features": [
            "FastAPI application",
            "Bedrock integration",
            "Static data loading",
            "Text processing",
            "Amazon Transcribe integration",
            "Amazon Polly integration",
            "WebSocket support",
            "LiveKit integration",
            "Real-time voice communication",
            "Health checks"
        ]
    }

# LiveKit endpoints
@app.post("/livekit/connect")
async def connect_to_livekit_room(request: LiveKitConnectRequest):
    """Connect to a LiveKit room."""
    try:
        result = await livekit_agent.connect_to_room(request.room_name, request.participant_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to LiveKit room: {str(e)}")

@app.post("/livekit/disconnect")
async def disconnect_from_livekit_room():
    """Disconnect from the current LiveKit room."""
    try:
        result = await livekit_agent.disconnect_from_room()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting from LiveKit room: {str(e)}")

@app.get("/livekit/status")
async def get_livekit_status():
    """Get LiveKit room status."""
    try:
        return livekit_agent.get_room_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting LiveKit status: {str(e)}")

@app.post("/livekit/process-voice")
async def process_livekit_voice(request: LiveKitVoiceRequest):
    """Process voice input through LiveKit."""
    try:
        # Decode base64 audio data
        audio_bytes = decode_base64_audio(request.audio_data)
        
        # Process through LiveKit agent
        result = await livekit_agent.process_voice_input(audio_bytes)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing LiveKit voice: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    ) 