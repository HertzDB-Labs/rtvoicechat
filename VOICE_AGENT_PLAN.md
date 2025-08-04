# Voice Agent Project Plan

## Project Overview

A voice agent that uses AWS Bedrock and LiveKit to answer questions about country and state capitals. The agent listens to conversations and responds with capital information for countries and US states, while indicating that other information is not available.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LiveKit       │    │   EC2 Instance  │    │   AWS Bedrock   │
│   Voice Client  │◄──►│   (Python App)  │◄──►│   (Claude Haiku)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Amazon Polly  │
                       │   (TTS)         │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Amazon Transcribe│
                       │   (STT)         │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   S3 Bucket     │
                       │   (Fallback)    │
                       └─────────────────┘
```

## Technology Stack

### Frontend
- **React/TypeScript**: Web client for voice interaction
- **LiveKit SDK**: Real-time voice communication
- **WebRTC**: Audio streaming

### Backend
- **Python 3.11+**: Main application language
- **FastAPI**: High-performance async API framework
- **WebSockets**: Real-time communication
- **LiveKit Python SDK**: Server-side voice processing ✅ **WORKING**

### AWS Services
- **AWS Bedrock**: Claude 3 Haiku (cheapest model) ✅ **WORKING**
- **Amazon Polly**: Text-to-speech service ✅ **WORKING**
- **Amazon Transcribe**: Speech-to-text service ✅ **WORKING**
  - **Streaming Mode**: WebSocket-based real-time transcription ✅ **NEW**
  - **Bucket Mode**: S3-based batch transcription ✅ **EXISTING**
- **EC2**: Application hosting (t3.micro for dev, t3.small for prod)

## Transcription Implementation

### Dual-Mode Transcription System

The system now supports two transcription modes:

#### 1. Streaming Mode (Primary) ✅ **NEW**
- **WebSocket-based**: Real-time audio streaming to Amazon Transcribe
- **No S3 dependency**: Direct WebSocket connection
- **Lower latency**: Immediate transcription results
- **Configuration**: `TRANSCRIPTION_MODE=streaming`

#### 2. Bucket Mode (Fallback) ✅ **EXISTING**
- **S3-based**: Upload audio to S3 bucket for batch processing
- **Reliable**: Proven method with error handling
- **Fallback option**: Used when streaming fails
- **Configuration**: `TRANSCRIPTION_MODE=bucket`

### Configuration Options

```env
# Transcription Configuration
TRANSCRIPTION_MODE=streaming  # Options: "streaming" or "bucket"
ENABLE_STREAMING_FALLBACK=true  # Fall back to bucket mode if streaming fails
STREAMING_TIMEOUT=30  # Timeout in seconds for streaming operations
```

### Implementation Components

1. **StreamingTranscribeClient** (`server/app/streaming_transcribe_client.py`)
   - WebSocket connection to Amazon Transcribe
   - Real-time audio streaming
   - Proper AWS signature v4 signing
   - Error handling and callbacks

2. **Enhanced TranscribeClient** (`server/app/transcribe_client.py`)
   - Dual-mode support (streaming/bucket)
   - Automatic fallback mechanism
   - Configuration-based mode selection

3. **Configuration System** (`server/app/config.py`)
   - Mode selection
   - Fallback settings
   - Timeout configuration

## Implementation Flow

### Streaming Mode Flow
```
1. User speaks → LiveKit Web Client captures audio
2. Audio → WebSocket → Python Backend ✅ **WORKING**
3. Python Backend → Amazon Transcribe Streaming (WebSocket) ✅ **NEW**
4. Text → Bedrock (Claude Haiku) for intent classification ✅ **WORKING**
5. If country/state query → Lookup from static JSON files ✅ **WORKING**
6. If other query → Return "information not available" ✅ **WORKING**
7. Response → Amazon Polly (TTS) ✅ **WORKING**
8. Audio → WebSocket → LiveKit → User hears response ✅ **WORKING**
```

### Bucket Mode Flow (Fallback)
```
1. User speaks → LiveKit Web Client captures audio
2. Audio → WebSocket → Python Backend ✅ **WORKING**
3. Python Backend → S3 Upload → Amazon Transcribe Job ✅ **WORKING**
4. Text → Bedrock (Claude Haiku) for intent classification ✅ **WORKING**
5. If country/state query → Lookup from static JSON files ✅ **WORKING**
6. If other query → Return "information not available" ✅ **WORKING**
7. Response → Amazon Polly (TTS) ✅ **WORKING**
8. Audio → WebSocket → LiveKit → User hears response ✅ **WORKING**
```

## Core Components

### 1. Voice Agent Logic (voice_agent.py) ✅ **WORKING**
- Coordinates all components
- Supports both transcription modes
- Enhanced system status reporting

### 2. Transcription System ✅ **ENHANCED**
- **StreamingTranscribeClient**: Real-time WebSocket transcription
- **TranscribeClient**: Dual-mode support with fallback
- **Configuration**: Mode selection and fallback settings

### 3. LiveKit Integration ✅ **WORKING**
- Real-time room connection
- Audio track processing
- Response publishing

### 4. Data Management ✅ **WORKING**
- Static JSON datasets for countries and states
- Fast lookup capabilities
- Comprehensive data coverage

## Project Phases

### Phase 1: Core Setup ✅ **COMPLETED**
- [x] Set up Python development environment
- [x] Create FastAPI application structure
- [x] Implement static JSON datasets
- [x] Basic Bedrock integration
- [x] Local development with virtual environment
- [x] Text-based query processing
- [x] Comprehensive testing framework

### Phase 2: Voice Integration ✅ **COMPLETED**
- [x] Amazon Transcribe integration (bucket mode)
- [x] Amazon Polly integration
- [x] WebSocket communication setup
- [x] Basic voice processing pipeline

### Phase 3: LiveKit Integration ✅ **COMPLETED & WORKING**
- [x] Set up LiveKit server/credentials
- [x] Web client with LiveKit SDK
- [x] Real-time audio streaming
- [x] End-to-end voice communication
- [x] LiveKit client integration ✅ **WORKING**
- [x] Real-time room connection ✅ **WORKING**
- [x] Audio track subscription and processing ✅ **WORKING**
- [x] Event handler implementation ✅ **WORKING**
- [x] Audio response publishing ✅ **WORKING**
- [x] Room state management ✅ **WORKING**
- [x] Error handling and recovery ✅ **WORKING**
- [x] API endpoints for LiveKit operations ✅ **WORKING**

### Phase 4: Streaming Transcription ✅ **NEW**
- [x] StreamingTranscribeClient implementation
- [x] WebSocket-based real-time transcription
- [x] Dual-mode transcription system
- [x] Configuration-based mode selection
- [x] Automatic fallback mechanism
- [x] Enhanced error handling
- [x] Comprehensive testing framework

### Phase 5: Production Ready (Next)
- [ ] Error handling and logging
- [ ] Performance optimization
- [ ] Security hardening
- [ ] EC2 deployment setup
- [ ] Monitoring and health checks

## AWS Configuration

### Required AWS Services
- **AWS Bedrock**: Claude 3 Haiku model access ✅ **WORKING**
- **Amazon Polly**: Text-to-speech service ✅ **WORKING**
- **Amazon Transcribe**: Speech-to-text service ✅ **WORKING**
  - **Streaming API**: WebSocket-based real-time transcription ✅ **NEW**
  - **Batch API**: S3-based transcription jobs ✅ **EXISTING**
- **EC2**: Application hosting (t3.micro for dev, t3.small for prod)

### AWS Credentials Setup
```bash
# Configure AWS CLI
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region us-east-1
```

### Environment Variables
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

# S3 Configuration for Transcribe (bucket-based mode)
S3_BUCKET_NAME=voice-agent-transcribe

# Transcription Configuration
TRANSCRIPTION_MODE=streaming  # Options: "streaming" or "bucket"
ENABLE_STREAMING_FALLBACK=true  # Fall back to bucket mode if streaming fails
STREAMING_TIMEOUT=30  # Timeout in seconds for streaming operations

# LiveKit Configuration
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_TOKEN=your_livekit_token

# Application Configuration
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

## Testing

### Test Scripts
- `test_transcription.py`: Tests bucket-based transcription
- `test_streaming_transcription.py`: Tests streaming transcription and dual modes
- `test_phase2.py`: Tests voice processing pipeline
- `test_phase3.py`: Tests LiveKit integration

### Running Tests
```bash
# Test streaming transcription
cd server
python test_streaming_transcription.py

# Test bucket transcription
python test_transcription.py

# Test voice processing
python test_phase2.py
```

## Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your AWS credentials

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
# On EC2 instance
sudo apt update
sudo apt install python3.11 python3.11-pip

# Clone repository
git clone <repository-url>
cd vagent

# Install dependencies
pip3 install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with production credentials

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Performance Considerations

### Streaming Mode Benefits
- **Lower latency**: Real-time transcription
- **No S3 costs**: Direct WebSocket connection
- **Better user experience**: Immediate feedback

### Bucket Mode Benefits
- **Reliability**: Proven method with error handling
- **Cost effective**: Batch processing for longer audio
- **Fallback option**: When streaming fails

### Configuration Recommendations
- **Development**: Use `TRANSCRIPTION_MODE=streaming` with fallback
- **Production**: Use `TRANSCRIPTION_MODE=streaming` with monitoring
- **High-traffic**: Consider bucket mode for cost optimization 