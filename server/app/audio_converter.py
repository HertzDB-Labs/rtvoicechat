import io
import tempfile
import os
from typing import Optional
from pydub import AudioSegment
from pydub.utils import make_chunks

class AudioConverter:
    """Utility for converting audio formats for transcription."""
    
    @staticmethod
    def convert_to_pcm(audio_data: bytes, input_format: str = "webm") -> Optional[bytes]:
        """
        Convert audio data to PCM format for Amazon Transcribe streaming.
        
        Args:
            audio_data: Raw audio bytes
            input_format: Input audio format (webm, mp3, wav, etc.)
            
        Returns:
            PCM audio bytes or None if conversion fails
        """
        try:
            # If it's already WAV, try to extract PCM directly
            if input_format == "wav" and audio_data.startswith(b'RIFF'):
                try:
                    # Skip WAV header (44 bytes for standard PCM WAV)
                    if len(audio_data) > 44:
                        return audio_data[44:]
                except:
                    pass
            
            # Use pydub for audio conversion
            try:
                # Create AudioSegment from raw bytes
                if input_format == "webm":
                    audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
                elif input_format == "mp3":
                    audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
                elif input_format == "wav":
                    audio = AudioSegment.from_wav(io.BytesIO(audio_data))
                elif input_format == "ogg":
                    audio = AudioSegment.from_ogg(io.BytesIO(audio_data))
                else:
                    # Try to auto-detect format
                    audio = AudioSegment.from_file(io.BytesIO(audio_data))
                
                # Convert to 16kHz, mono, 16-bit PCM
                audio = audio.set_frame_rate(16000)
                audio = audio.set_channels(1)
                audio = audio.set_sample_width(2)  # 16-bit = 2 bytes
                
                # Export as raw PCM bytes
                pcm_io = io.BytesIO()
                audio.export(pcm_io, format="raw")
                return pcm_io.getvalue()
                
            except Exception as e:
                print(f"pydub conversion failed: {e}")
                
                # Fallback: try with ffmpeg if available
                try:
                    import subprocess
                    
                    # Create temporary files
                    with tempfile.NamedTemporaryFile(suffix=f'.{input_format}', delete=False) as temp_input, \
                         tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
                        
                        # Write input audio
                        temp_input.write(audio_data)
                        temp_input_path = temp_input.name
                        temp_output_path = temp_output.name
                    
                    try:
                        # Convert to PCM WAV (16kHz, 16-bit, mono)
                        subprocess.run([
                            'ffmpeg',
                            '-i', temp_input_path,
                            '-ar', '16000',  # Sample rate
                            '-ac', '1',      # Mono
                            '-acodec', 'pcm_s16le',  # 16-bit PCM
                            '-f', 'wav',     # WAV format
                            '-y',  # Overwrite output
                            temp_output_path
                        ], check=True, capture_output=True, stderr=subprocess.DEVNULL)
                        
                        # Read the PCM data (skip WAV header)
                        with open(temp_output_path, 'rb') as wav_file:
                            wav_file.seek(44)  # Skip WAV header
                            pcm_data = wav_file.read()
                        
                        return pcm_data
                        
                    finally:
                        # Clean up temporary files
                        if os.path.exists(temp_input_path):
                            os.unlink(temp_input_path)
                        if os.path.exists(temp_output_path):
                            os.unlink(temp_output_path)
                            
                except Exception as ffmpeg_error:
                    print(f"ffmpeg conversion also failed: {ffmpeg_error}")
                    return None
                    
        except Exception as e:
            print(f"Error converting audio to PCM: {e}")
            return None
    
    @staticmethod
    def chunk_audio(audio_data: bytes, chunk_size_ms: int = 100) -> list[bytes]:
        """
        Split audio data into chunks for streaming.
        
        Args:
            audio_data: PCM audio bytes
            chunk_size_ms: Size of each chunk in milliseconds
            
        Returns:
            List of audio chunks
        """
        try:
            # Convert bytes to AudioSegment
            audio = AudioSegment.from_raw(io.BytesIO(audio_data), 
                                        sample_width=2, 
                                        frame_rate=16000, 
                                        channels=1)
            
            # Create chunks
            chunks = make_chunks(audio, chunk_size_ms)
            
            # Convert chunks back to bytes
            chunk_bytes = []
            for chunk in chunks:
                chunk_io = io.BytesIO()
                chunk.export(chunk_io, format="raw")
                chunk_bytes.append(chunk_io.getvalue())
            
            return chunk_bytes
            
        except Exception as e:
            print(f"Error chunking audio: {e}")
            return [audio_data]  # Return original as single chunk
    
    @staticmethod
    def detect_audio_format(audio_data: bytes) -> str:
        """
        Detect audio format from file header.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Detected format string
        """
        try:
            # Check file headers
            if audio_data.startswith(b'RIFF') and audio_data[8:12] == b'WAVE':
                return "wav"
            elif audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
                return "mp3"
            elif audio_data.startswith(b'\x1a\x45\xdf\xa3'):
                return "webm"
            elif audio_data.startswith(b'OggS'):
                return "ogg"
            else:
                # Default to webm for unknown formats
                return "webm"
                
        except Exception as e:
            print(f"Error detecting audio format: {e}")
            return "webm"  # Default fallback 
