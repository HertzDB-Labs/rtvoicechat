"""
LiveKit client for real-time voice communication.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from livekit import rtc
from livekit.rtc import Room, AudioTrack, TrackSource
import base64
import tempfile
import os

from .voice_agent import VoiceAgent
from .config import Config

logger = logging.getLogger(__name__)

class LiveKitVoiceAgent:
    """LiveKit voice agent for real-time voice communication."""
    
    def __init__(self):
        self.voice_agent = VoiceAgent()
        self.room: Optional[Room] = None
        self.is_connected = False
        self.room_name: Optional[str] = None
        self.participant_name: Optional[str] = None
        
    async def connect_to_room(self, room_name: str, participant_name: str) -> Dict[str, Any]:
        """Connect to a LiveKit room."""
        try:
            # Create room instance
            self.room = Room()
            self.room_name = room_name
            self.participant_name = participant_name
            
            # Set up event handlers using string-based event names
            self.room.on("participant_connected", self._on_participant_connected)
            self.room.on("participant_disconnected", self._on_participant_disconnected)
            self.room.on("track_subscribed", self._on_track_subscribed)
            self.room.on("track_unsubscribed", self._on_track_unsubscribed)
            self.room.on("audio_playback_status_changed", self._on_audio_playback_changed)
            
            # Connect to room
            await self.room.connect(
                Config.LIVEKIT_URL,
                Config.LIVEKIT_TOKEN,
                rtc.RoomOptions(
                    auto_subscribe=True
                )
            )
            
            self.is_connected = True
            logger.info(f"Connected to room: {room_name} as {participant_name}")
            
            return {
                "success": True,
                "room_name": room_name,
                "participant_name": participant_name,
                "message": "Successfully connected to LiveKit room"
            }
            
        except Exception as e:
            logger.error(f"Failed to connect to room: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to connect to LiveKit room"
            }
    
    async def disconnect_from_room(self) -> Dict[str, Any]:
        """Disconnect from the current room."""
        try:
            if self.room and self.is_connected:
                await self.room.disconnect()
                self.room = None
                self.is_connected = False
                self.room_name = None
                self.participant_name = None
                logger.info("Disconnected from room")
                
                return {
                    "success": True,
                    "message": "Successfully disconnected from room"
                }
            else:
                return {
                    "success": False,
                    "error": "Not connected to any room",
                    "message": "No active connection to disconnect"
                }
                
        except Exception as e:
            logger.error(f"Failed to disconnect from room: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to disconnect from room"
            }
    
    async def publish_audio_response(self, audio_data: bytes, filename: str) -> bool:
        """Publish audio response to the room."""
        try:
            if not self.room or not self.is_connected:
                logger.error("Not connected to room")
                return False
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Create audio track from file
                audio_track = await rtc.LocalAudioTrack.create_audio_track_from_file(
                    temp_file_path,
                    rtc.AudioCaptureOptions()
                )
                
                # Publish track to room
                await self.room.local_participant.publish_track(audio_track)
                logger.info(f"Published audio response: {filename}")
                return True
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Failed to publish audio response: {e}")
            return False
    
    async def process_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """Process voice input and return response."""
        try:
            # Process voice input using the voice agent
            result = await self.voice_agent.process_voice_with_audio_response(audio_data)
            
            # If we have an audio response and are connected to a room, publish it
            if result.get('audio_file_path') and self.room and self.is_connected:
                audio_filename = os.path.basename(result['audio_file_path'])
                audio_path = os.path.join(Config.AUDIO_STORAGE_PATH, audio_filename)
                
                if os.path.exists(audio_path):
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    await self.publish_audio_response(audio_bytes, audio_filename)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process voice input: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I couldn't process your request."
            }
    
    def _on_participant_connected(self, participant):
        """Handle participant connection."""
        logger.info(f"Participant connected: {participant.identity}")
    
    def _on_participant_disconnected(self, participant):
        """Handle participant disconnection."""
        logger.info(f"Participant disconnected: {participant.identity}")
    
    def _on_track_subscribed(self, track, publication, participant):
        """Handle track subscription."""
        logger.info(f"Track subscribed: {track.kind} from {participant.identity}")
        
        # If it's an audio track from a remote participant, set up audio processing
        # Check if it's an audio track by checking the track kind value (0 = AUDIO, 1 = VIDEO)
        if track.kind == 0 and participant.identity != self.room.local_participant.identity:
            # Set up audio processing for remote audio
            track.on("data_received", self._on_audio_data_received)
    
    def _on_track_unsubscribed(self, track, publication, participant):
        """Handle track unsubscription."""
        logger.info(f"Track unsubscribed: {track.kind} from {participant.identity}")
    
    def _on_audio_playback_changed(self, playing: bool):
        """Handle audio playback status change."""
        logger.info(f"Audio playback status: {playing}")
    
    async def _on_audio_data_received(self, data: bytes):
        """Handle received audio data from remote participants."""
        try:
            logger.info(f"Received audio data: {len(data)} bytes")
            
            # Process the received audio data
            result = await self.process_voice_input(data)
            
            # If processing was successful and we have an audio response, publish it
            if result.get('success') and result.get('audio_file_path'):
                audio_filename = os.path.basename(result['audio_file_path'])
                audio_path = os.path.join(Config.AUDIO_STORAGE_PATH, audio_filename)
                
                if os.path.exists(audio_path):
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    await self.publish_audio_response(audio_bytes, audio_filename)
                    logger.info(f"Published response for audio input: {audio_filename}")
                
        except Exception as e:
            logger.error(f"Failed to process received audio data: {e}")
    
    def get_room_status(self) -> Dict[str, Any]:
        """Get current room status."""
        if not self.room:
            return {
                "connected": False,
                "room_name": None,
                "participants": []
            }
        
        participants = []
        for participant in self.room.participants.values():
            participants.append({
                "identity": participant.identity,
                "name": participant.name,
                "audio_tracks": len(participant.audio_tracks),
                "video_tracks": len(participant.video_tracks)
            })
        
        return {
            "connected": self.is_connected,
            "room_name": self.room_name,
            "participants": participants,
            "local_participant": {
                "identity": self.room.local_participant.identity,
                "name": self.room.local_participant.name
            } if self.room.local_participant else None
        } 