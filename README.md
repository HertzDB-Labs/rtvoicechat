# Voice Agent Project

A voice agent that uses AWS Bedrock, Amazon Polly, and Amazon Transcribe to answer questions about country and state capitals. The agent processes voice input, transcribes speech to text, generates responses using Claude Haiku, and converts responses back to speech.

## Project Status

**Current Phase: Phase 3 - LiveKit Integration** ✅ **COMPLETED & WORKING**

### Phase 1: Core Setup ✅ COMPLETED
- [x] Set up Python development environment
- [x] Create FastAPI application structure
- [x] Implement static JSON datasets
- [x] Basic Bedrock integration
- [x] Local development with virtual environment
- [x] Text-based query processing
- [x] Comprehensive testing framework

### Phase 2: Voice Integration ✅ COMPLETED
- [x] Amazon Transcribe integration
- [x] Amazon Polly integration
- [x] Voice processing pipeline
- [x] Audio file handling
- [x] Real audio data testing
- [x] Voice-to-text and text-to-speech
- [x] Base64 audio encoding/decoding
- [x] Response audio generation

### Phase 3: LiveKit Integration ✅ COMPLETED & WORKING
- [x] LiveKit client integration
- [x] Real-time room connection
- [x] Audio track subscription and processing
- [x] Event handler implementation
- [x] Audio response publishing
- [x] Room state management
- [x] Error handling and recovery
- [x] API endpoints for LiveKit operations
- [x] Import error fixes (TrackType, ConnectOptions)
- [x] Event handler fixes (string-based approach)
- [x] Connection options fixes (RoomOptions)
- [x] Track processing fixes (numeric track types)
- [x] Comprehensive testing and documentation

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice Input   │    │   EC2 Instance  │    │   AWS Bedrock   │
│   (Audio File)  │◄──►│   (Python App)  │◄──►│   (Claude Haiku)│
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
                       │   LiveKit       │
                       │   (Real-time)   │
                       └─────────────────┘
```

## Technology Stack

- **Backend**: Python 3.10+, FastAPI
- **AWS Services**: Bedrock (Claude Haiku), Polly (TTS), Transcribe (STT)
- **Real-time Communication**: LiveKit
- **Audio Processing**: WAV, MP3, Base64 encoding
- **Data**: Static JSON files
- **Deployment**: Virtual Environment, EC2

## Quick Start

### Prerequisites

1. **Python 3.10+** installed on your system
2. **AWS Account** with access to:
   - AWS Bedrock (Claude Haiku model)
   - Amazon Polly (Text-to-Speech)
   - Amazon Transcribe (Speech-to-Text)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vagent
   ```

2. **Run the setup script**
   ```bash
   cd server
   ./setup.sh
   ```

3. **Configure environment variables**
   ```bash
   # Edit the .env file with your AWS credentials
   nano .env
   ```

4. **Activate virtual environment and run**
   ```bash
   source venv/bin/activate
   python run.py
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Test Endpoint: http://localhost:8000/test

### Manual Setup (Alternative)

If you prefer to set up manually:

1. **Create virtual environment**
   ```bash
   cd server
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file**
   ```bash
   cp ../env.example .env
   # Edit .env with your AWS credentials
   ```

4. **Run the application**
   ```bash
   python run.py
   # Or use uvicorn directly:
   # uvicorn app.main:app --reload
   ```

## Testing

### Phase 1 Testing (Text Processing)

#### Automated Testing
```bash
cd server
source venv/bin/activate
python test_local.py
```

#### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# System status
curl http://localhost:8000/status

# Process text
curl -X POST "http://localhost:8000/process-text" \
     -H "Content-Type: application/json" \
     -d '{"text": "What is the capital of France?"}'
```

Expected response:
```json
{
  "response": "The capital of France is Paris.",
  "success": true,
  "query_type": "COUNTRY",
  "entity": "France",
  "capital": "Paris"
}
```

### Phase 2 Testing (Voice Processing)

#### Real Audio Testing
```bash
cd server
source venv/bin/activate
python test_real_audio.py
```

This test:
- Downloads real audio files from the internet (or generates test audio)
- Compares placeholder vs real audio data sizes
- Tests the voice processing API with real audio
- Shows detailed size comparisons and processing results

#### Voice API Testing
```bash
# Test with base64 encoded audio
curl -X POST "http://localhost:8000/process-voice" \
     -H "Content-Type: application/json" \
     -d '{"audio_data": "base64_encoded_audio_data_here"}'
```

Expected response:
```json
{
  "success": true,
  "response": "The capital of France is Paris.",
  "audio_file_path": "audio/response_123456789.mp3",
  "transcribed_text": "What is the capital of France?"
}
```

#### Phase 2 Specific Tests
```bash
# Test transcription only
python test_phase2.py

# Test Bedrock access
python test_bedrock_access.py

# List available models
python list_models.py
```

#### Phase 3 Testing (LiveKit Integration)
```bash
# Test LiveKit integration
python test_phase3.py

# Start the React client
cd ../client
npm install
npm start
```

This test:
- Tests LiveKit server integration
- Tests real-time voice communication
- Provides client setup instructions
- Shows Phase 3 features and capabilities

### Comprehensive Testing Suite

#### 1. Basic Functionality Tests
```bash
# Test local functionality
python test_local.py

# Test voice processing
python test_real_audio.py
```

#### 2. AWS Service Tests
```bash
# Test Bedrock access
python test_bedrock_access.py

# Test Polly and Transcribe
python test_phase2.py
```

#### 3. API Endpoint Tests
```bash
# Health check
curl http://localhost:8000/health

# Status check
curl http://localhost:8000/status

# Text processing
curl -X POST "http://localhost:8000/process-text" \
     -H "Content-Type: application/json" \
     -d '{"text": "What is the capital of California?"}'

# Voice processing (requires real audio data)
curl -X POST "http://localhost:8000/process-voice" \
     -H "Content-Type: application/json" \
     -d '{"audio_data": "base64_audio_data"}'
```

## API Endpoints

### Core Endpoints

- `GET /` - Basic information
- `GET /health` - Health check
- `GET /status` - System status and AWS connection
- `GET /entities` - Available countries and states
- `POST /process-text` - Process text input (Phase 1)
- `POST /process-voice` - Process voice input (Phase 2)

### Phase 2 Voice Processing

The `/process-voice` endpoint:
1. Accepts base64-encoded audio data
2. Decodes and saves audio to temporary file
3. Uses Amazon Transcribe to convert speech to text
4. Processes text through Claude Haiku
5. Uses Amazon Polly to generate response audio
6. Returns response with audio file path

## Data Structure

The application uses static JSON files for country and state data:

- `server/data/countries.json` - 195 countries with capitals
- `server/data/us-states.json` - 50 US states with capitals

## Development Phases

### Phase 1: Core Setup ✅ COMPLETED
- [x] Python development environment
- [x] FastAPI application structure
- [x] Static JSON datasets
- [x] Basic Bedrock integration
- [x] Virtual environment setup
- [x] Text-based query processing
- [x] Comprehensive testing framework

### Phase 2: Voice Integration ✅ COMPLETED
- [x] Amazon Transcribe integration
- [x] Amazon Polly integration
- [x] Voice processing pipeline
- [x] Audio file handling
- [x] Real audio data testing
- [x] Voice-to-text and text-to-speech
- [x] Base64 audio encoding/decoding
- [x] Response audio generation

### Phase 3: LiveKit Integration ✅ COMPLETED
- [x] LiveKit server integration
- [x] Web client with React/TypeScript
- [x] Real-time audio streaming
- [x] End-to-end voice communication
- [x] LiveKit Python SDK integration
- [x] Room management and participant handling
- [x] Real-time audio response publishing
- [x] Modern UI with voice controls

### Phase 4: Production Ready
- [ ] Error handling and logging
- [ ] Performance optimization
- [ ] Security hardening
- [ ] EC2 deployment setup

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `DEBUG` | Debug mode | `false` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

### AWS Services Setup

1. **AWS Bedrock**
   - Enable Claude Haiku model access
   - Configure IAM permissions

2. **Amazon Polly** ✅ Phase 2 Complete
   - Enable text-to-speech service
   - Configure voice preferences

3. **Amazon Transcribe** ✅ Phase 2 Complete
   - Enable speech-to-text service
   - Configure language settings

## File Structure

```
vagent/
├── client/                 # React/TypeScript Web Client
│   ├── src/
│   │   ├── components/
│   │   │   ├── VoiceAgent.tsx
│   │   │   └── VoiceAgent.css
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.tsx
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── README.md
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── voice_agent.py
│   │   ├── bedrock_client.py
│   │   ├── polly_client.py
│   │   ├── transcribe_client.py
│   │   ├── livekit_client.py
│   │   ├── data_handler.py
│   │   └── config.py
│   ├── data/
│   │   ├── countries.json
│   │   └── us-states.json
│   ├── audio/              # Generated audio files
│   ├── venv/              # Virtual environment
│   ├── requirements.txt
│   ├── run.py             # Run script
│   ├── setup.sh           # Setup script
│   ├── test_local.py      # Phase 1 tests
│   ├── test_real_audio.py # Phase 2 tests
│   ├── test_phase2.py     # Phase 2 specific tests
│   ├── test_phase3.py     # Phase 3 tests
│   ├── test_bedrock_access.py
│   ├── list_models.py
│   └── .env               # Environment variables
├── env.example
├── README.md
└── VOICE_AGENT_PLAN.md
```

## Troubleshooting

### Common Issues

1. **Python Version**
   - Ensure Python 3.10+ is installed
   - Check with: `python3 --version`

2. **Virtual Environment**
   - Always activate: `source venv/bin/activate`
   - Reinstall if corrupted: `rm -rf venv && ./setup.sh`

3. **AWS Credentials**
   - Ensure AWS credentials are properly configured in `.env`
   - Check IAM permissions for Bedrock, Polly, and Transcribe access

4. **Dependencies**
   - Reinstall if issues: `pip install -r requirements.txt`
   - Check for conflicts: `pip list`

5. **Audio Processing**
   - Ensure audio files are properly formatted (WAV/MP3)
   - Check base64 encoding for voice API calls
   - Verify audio file permissions in `server/audio/` directory

### Logs

View application logs in the terminal where you run the server.

## Development Commands

```bash
# Setup (first time only)
cd server
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Run server
python run.py

# Run Phase 1 tests
python test_local.py

# Run Phase 2 tests
python test_real_audio.py

# Run specific Phase 2 tests
python test_phase2.py

# Test AWS access
python test_bedrock_access.py

# Install new dependencies
pip install package_name
pip freeze > requirements.txt
```

## Testing Checklist

### Phase 1 Testing ✅
- [x] Text processing with country queries
- [x] Text processing with state queries
- [x] Error handling for invalid queries
- [x] AWS Bedrock integration
- [x] API endpoint functionality
- [x] Health and status checks

### Phase 2 Testing ✅
- [x] Real audio data processing
- [x] Base64 audio encoding/decoding
- [x] Amazon Transcribe integration
- [x] Amazon Polly integration
- [x] Audio file generation
- [x] Voice-to-text accuracy
- [x] Text-to-speech quality
- [x] End-to-end voice processing pipeline

### Phase 3 Testing ✅
- [x] LiveKit server integration
- [x] Real-time voice communication
- [x] Web client with React/TypeScript
- [x] Room management and participant handling
- [x] Real-time audio response publishing
- [x] Modern UI with voice controls
- [x] End-to-end voice communication pipeline
- [x] Client-server integration testing

## Contributing

1. Follow the development phases outlined in the plan
2. Test thoroughly before submitting changes
3. Update documentation as needed
4. Ensure all tests pass for both Phase 1 and Phase 2

## License

[Add your license information here]

## Support

For issues and questions, please refer to the project documentation or create an issue in the repository.
