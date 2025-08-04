import React, { useState, useEffect, useRef } from 'react';
import { Room, LocalParticipant, RoomEvent, AudioTrack } from 'livekit-client';
import './VoiceAgent.css';

interface VoiceAgentProps {
  room: Room;
  onDisconnect: () => void;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  audioUrl?: string;
}

const VoiceAgent: React.FC<VoiceAgentProps> = ({ room, onDisconnect }) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [localParticipant, setLocalParticipant] = useState<LocalParticipant | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    const participant = room.localParticipant;
    setLocalParticipant(participant);

    // Set up room event listeners
    room.on(RoomEvent.AudioPlaybackStatusChanged, (playing: boolean) => {
      console.log('Audio playback status:', playing);
    });

    room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
      console.log('Track subscribed:', track.kind, participant.identity);
    });

    return () => {
      // Cleanup
    };
  }, [room]);

  const startListening = async () => {
    try {
      setError(null);
      setIsListening(true);
      audioChunksRef.current = [];

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        } 
      });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        await processAudio();
      };

      // Start recording
      mediaRecorder.start();
      console.log('Started listening...');

    } catch (err) {
      console.error('Failed to start listening:', err);
      setError('Failed to access microphone');
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      setIsListening(false);
      console.log('Stopped listening...');
    }
  };

  const processAudio = async () => {
    if (audioChunksRef.current.length === 0) return;

    setIsProcessing(true);
    
    // Create user message first, so we have access to it in the catch block
      const userMessage: Message = {
        id: Date.now().toString(),
        text: '🎤 Listening...',
        isUser: true,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);
    
    try {
      // Create audio blob
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Convert to base64 using a more compatible approach
      const buffer = await audioBlob.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      let binary = '';
      for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const base64Audio = btoa(binary);

      // Send to backend
      const response = await fetch('http://localhost:8000/process-voice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audio_data: base64Audio
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Update user message with transcribed text
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id 
          ? { ...msg, text: result.transcribed_text || 'Could not transcribe audio' }
          : msg
      ));

      // Add agent response
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: result.response || 'Sorry, I could not process your request.',
        isUser: false,
        timestamp: new Date(),
        audioUrl: result.audio_file_path ? `http://localhost:8000/audio/${result.audio_file_path.split('/').pop()}` : undefined,
      };
      setMessages(prev => [...prev, agentMessage]);

      // Play response audio if available
      if (agentMessage.audioUrl && audioRef.current) {
        audioRef.current.src = agentMessage.audioUrl;
        audioRef.current.play().catch(err => {
          console.error('Failed to play audio:', err);
        });
      }

    } catch (err) {
      console.error('Failed to process audio:', err);
      setError('Failed to process audio');
      
      // Update user message with error
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id 
          ? { ...msg, text: '❌ Failed to process audio' }
          : msg
      ));
    } finally {
      setIsProcessing(false);
      audioChunksRef.current = [];
    }
  };

  const sendTextMessage = async (text: string) => {
    if (!text.trim()) return;

    setIsProcessing(true);
    
    try {
      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        text: text,
        isUser: true,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);

      // Send to backend
      const response = await fetch('http://localhost:8000/process-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Add agent response
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: result.response || 'Sorry, I could not process your request.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, agentMessage]);

    } catch (err) {
      console.error('Failed to send text message:', err);
      setError('Failed to send message');
    } finally {
      setIsProcessing(false);
    }
  };

  const [textInput, setTextInput] = useState('');

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (textInput.trim()) {
      sendTextMessage(textInput);
      setTextInput('');
    }
  };

  return (
    <div className="voice-agent">
      <div className="agent-header">
        <h2>Voice Agent</h2>
        <button onClick={onDisconnect} className="disconnect-button">
          Disconnect
        </button>
      </div>

      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.isUser ? 'user' : 'agent'}`}>
            <div className="message-content">
              <p>{message.text}</p>
              {message.audioUrl && (
                <audio 
                  ref={audioRef}
                  controls 
                  className="response-audio"
                  src={message.audioUrl}
                />
              )}
            </div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="message agent">
            <div className="message-content">
              <p>🤔 Processing...</p>
            </div>
          </div>
        )}
      </div>

      <div className="input-section">
        <div className="voice-controls">
          <button
            onClick={isListening ? stopListening : startListening}
            disabled={isProcessing}
            className={`voice-button ${isListening ? 'listening' : ''}`}
          >
            {isListening ? '🛑 Stop' : '🎤 Start Voice'}
          </button>
        </div>

        <form onSubmit={handleTextSubmit} className="text-input-form">
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Or type your question here..."
            disabled={isProcessing}
            className="text-input"
          />
          <button type="submit" disabled={isProcessing || !textInput.trim()}>
            Send
          </button>
        </form>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="status-indicator">
        <span className={`status-dot ${isListening ? 'listening' : 'idle'}`}></span>
        {isListening ? 'Listening...' : 'Ready'}
      </div>
    </div>
  );
};

export default VoiceAgent; 