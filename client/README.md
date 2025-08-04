# Voice Agent Client

A React/TypeScript web client for real-time voice communication with the Voice Agent API.

## Features

- 🎤 Real-time voice communication using LiveKit
- 💬 Text-based chat interface
- 🎵 Audio response playback
- 📱 Responsive design for mobile and desktop
- 🌐 Modern UI with voice controls
- 🔄 Real-time message updates

## Prerequisites

- Node.js 16+ and npm
- Voice Agent server running on port 8000
- LiveKit server configured

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment variables**
   Create a `.env` file in the client directory:
   ```env
   REACT_APP_LIVEKIT_URL=ws://localhost:7880
   REACT_APP_LIVEKIT_TOKEN=your_livekit_token
   REACT_APP_API_URL=http://localhost:8000
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open the application**
   The app will open at http://localhost:3000

## Usage

### Connecting to Voice Agent

1. Click "Connect to Voice Agent" button
2. Grant microphone permissions when prompted
3. The interface will show the voice agent interface

### Voice Communication

1. **Start Voice Input**: Click the "🎤 Start Voice" button
2. **Speak**: Ask questions about country and state capitals
3. **Stop**: Click "🛑 Stop" to end recording
4. **Listen**: The agent will respond with both text and audio

### Text Communication

1. **Type**: Use the text input field at the bottom
2. **Send**: Press Enter or click the Send button
3. **Response**: View the agent's response in the chat

## Features

### Real-time Voice Processing
- Captures audio using MediaRecorder API
- Converts to base64 for transmission
- Sends to backend for processing
- Receives audio responses for playback

### Modern UI
- Glassmorphism design with backdrop blur
- Smooth animations and transitions
- Responsive layout for all devices
- Voice activity indicators

### Message History
- Persistent chat history during session
- Timestamp for each message
- Audio playback for responses
- User and agent message distinction

## Technical Details

### Architecture
```
User Voice → MediaRecorder → Base64 → API → Transcribe → Bedrock → Polly → Audio Response
```

### Key Components

- **App.tsx**: Main application component with LiveKit room management
- **VoiceAgent.tsx**: Voice interface with recording and playback
- **LiveKit Integration**: Real-time WebRTC communication
- **Audio Processing**: WebM/Opus audio format support

### Audio Format
- **Input**: WebM with Opus codec
- **Output**: MP3 from Amazon Polly
- **Quality**: Optimized for voice communication

## Development

### Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App

### Project Structure
```
client/
├── src/
│   ├── components/
│   │   ├── VoiceAgent.tsx
│   │   └── VoiceAgent.css
│   ├── App.tsx
│   ├── App.css
│   ├── index.tsx
│   └── index.css
├── public/
│   └── index.html
├── package.json
└── README.md
```

## Troubleshooting

### Microphone Access
- Ensure browser has microphone permissions
- Check browser console for MediaRecorder errors
- Try refreshing the page if permissions are denied

### LiveKit Connection
- Verify LiveKit server is running
- Check environment variables are set correctly
- Ensure network connectivity to LiveKit server

### Audio Playback
- Check browser audio settings
- Ensure audio files are accessible
- Verify CORS settings on server

## Browser Support

- Chrome 66+
- Firefox 60+
- Safari 14+
- Edge 79+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here] 