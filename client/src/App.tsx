import React, { useState, useEffect } from 'react';
import { Room, RoomEvent, RemoteParticipant } from 'livekit-client';
import VoiceAgent from './components/VoiceAgent';
import './App.css';

function App() {
  const [room, setRoom] = useState<Room | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connectToRoom = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Create a new room instance
      const newRoom = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      // Set up event listeners
      newRoom.on(RoomEvent.ParticipantConnected, (participant: RemoteParticipant) => {
        console.log('Participant connected:', participant.identity);
      });

      newRoom.on(RoomEvent.ParticipantDisconnected, (participant: RemoteParticipant) => {
        console.log('Participant disconnected:', participant.identity);
      });

      newRoom.on(RoomEvent.AudioPlaybackStatusChanged, (playing: boolean) => {
        console.log('Audio playback status:', playing);
      });

      // Using the verified working token
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjE4Mzg2NzcsImlzcyI6ImRldmtleSIsIm5hbWUiOiJ0ZXN0X3VzZXIiLCJuYmYiOjE3NTMxOTg2NzcsInN1YiI6InRlc3RfdXNlciIsInZpZGVvIjp7InJvb20iOiJ0ZXN0X3Jvb20iLCJyb29tSm9pbiI6dHJ1ZX19.QiAvojO8F5ItaDwxWUd9UhZ6T6fRXSgZNnEx258rCUg';

      // Connect to the room
      await newRoom.connect('ws://localhost:7880', token);

      setRoom(newRoom);
      setIsConnected(true);
      console.log('Connected to room:', newRoom.name);
    } catch (err) {
      console.error('Failed to connect to room:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect to room');
    } finally {
      setIsLoading(false);
    }
  };

  const disconnectFromRoom = async () => {
    if (room) {
      await room.disconnect();
      setRoom(null);
      setIsConnected(false);
      console.log('Disconnected from room');
    }
  };

  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Hertz Geography Agent</h1>
        <p>Ask me about country and state capitals!</p>
      </header>

      <main className="App-main">
        {!isConnected ? (
          <div className="connection-section">
            <button 
              onClick={connectToRoom}
              disabled={isLoading}
              className="connect-button"
            >
              {isLoading ? 'Connecting...' : 'Connect to Voice Agent'}
            </button>
            {error && (
              <div className="error-message">
                Error: {error}
              </div>
            )}
          </div>
        ) : (
          <VoiceAgent 
            room={room!}
            onDisconnect={disconnectFromRoom}
          />
        )}
      </main>

      <footer className="App-footer">
        <p>Powered by LiveKit, AWS Bedrock, and Amazon Polly</p>
      </footer>
    </div>
  );
}

export default App; 
