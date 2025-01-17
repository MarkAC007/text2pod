"""Test ElevenLabs API with multiple voices in conversation."""
import os
import logging
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests
from pydub import AudioSegment

# Set up logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"voice_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_ffmpeg():
    """Verify ffmpeg is installed and accessible."""
    if shutil.which('ffmpeg') is None:
        raise RuntimeError(
            "ffmpeg not found. Please install ffmpeg:\n"
            "Windows (conda): conda install ffmpeg\n"
            "Windows (chocolatey): choco install ffmpeg\n"
            "Linux: sudo apt-get install ffmpeg\n"
            "Mac: brew install ffmpeg"
        )
    logger.info("ffmpeg found and accessible")

def merge_audio_segments(segment_files, output_file, crossfade_ms=500):
    """Merge multiple audio segments with crossfade."""
    logger.info("Merging audio segments...")
    
    # Verify all files exist
    for file in segment_files:
        if not file.exists():
            raise FileNotFoundError(f"Audio segment not found: {file}")
    
    try:
        # Load the first segment
        combined = AudioSegment.from_mp3(str(segment_files[0]))
        
        # Add subsequent segments with crossfade
        for segment_file in segment_files[1:]:
            next_segment = AudioSegment.from_mp3(str(segment_file))
            combined = combined.append(next_segment, crossfade=crossfade_ms)
        
        # Export the combined audio
        combined.export(str(output_file), format="mp3")
        logger.info(f"Merged audio saved to: {output_file}")
        
        return output_file
    
    except Exception as e:
        logger.error(f"Error merging audio segments: {e}")
        raise

def generate_audio(text, voice_id, api_key, voice_settings=None):
    """Generate audio for a single segment."""
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Default voice settings if none provided
    if voice_settings is None:
        voice_settings = {
            "stability": 0.71,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }

    tts_headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    tts_payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": voice_settings
    }
    
    tts_response = requests.post(
        f"{BASE_URL}/text-to-speech/{voice_id}",
        json=tts_payload,
        headers=tts_headers
    )
    
    if tts_response.status_code != 200:
        raise ValueError(f"TTS request failed: {tts_response.text}")
        
    return tts_response.content

def test_voice_conversation():
    """Test generating a conversation between two voices."""
    try:
        logger.info("=== Starting Voice Conversation Test ===")
        
        # Verify ffmpeg installation
        check_ffmpeg()
        
        # Load API key
        load_dotenv()
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment")
        logger.info("API key loaded successfully")

        # Get available voices
        BASE_URL = "https://api.elevenlabs.io/v1"
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }

        voices_response = requests.get(f"{BASE_URL}/voices", headers=headers)
        voices_data = voices_response.json()
        
        # Select voices for host and expert
        host_voice = None
        expert_voice = None
        
        for voice in voices_data["voices"]:
            if voice["name"] == "Jessica":  # Host voice
                host_voice = voice["voice_id"]
            elif voice["name"] == "Daniel":  # Expert voice (British, authoritative)
                expert_voice = voice["voice_id"]

        if not (host_voice and expert_voice):
            raise ValueError("Required voices not found")
            
        logger.info(f"Using Jessica (ID: {host_voice}) as host")
        logger.info(f"Using Daniel (ID: {expert_voice}) as expert")

        # Test conversation
        conversation = [
            {
                "role": "host",
                "voice_id": host_voice,
                "text": "Welcome to our tech podcast! Today we're discussing artificial intelligence and its impact on software development. With us is our expert guest, who'll share some fascinating insights."
            },
            {
                "role": "expert",
                "voice_id": expert_voice,
                "text": "Thank you for having me. AI is indeed transforming how we approach software development. Let me explain some key concepts that developers should be aware of."
            },
            {
                "role": "host",
                "voice_id": host_voice,
                "text": "That would be great! What's the first thing developers should understand about AI integration?"
            },
            {
                "role": "expert",
                "voice_id": expert_voice,
                "text": "The most important aspect is understanding that AI isn't magic - it's a tool that requires careful consideration. Let's start with the basics of machine learning models and their practical applications."
            }
        ]

        # Generate and save audio for each segment
        output_dir = Path(__file__).parent.parent / "output" / "voice_conversation_test"
        output_dir.mkdir(exist_ok=True)
        
        segment_files = []  # Keep track of segment files for merging

        for i, segment in enumerate(conversation, 1):
            logger.info(f"\n=== Generating Segment {i} ({segment['role']}) ===")
            
            # Adjust voice settings based on role
            voice_settings = {
                "stability": 0.71,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            }
            
            # Generate audio
            audio = generate_audio(
                text=segment["text"],
                voice_id=segment["voice_id"],
                api_key=api_key,
                voice_settings=voice_settings
            )
            
            # Save audio file
            output_file = output_dir / f"segment_{i:02d}_{segment['role']}.mp3"
            with open(output_file, 'wb') as f:
                f.write(audio)
            logger.info(f"Saved audio to: {output_file}")
            
            segment_files.append(output_file)

        # Merge all segments
        merged_file = output_dir / "complete_conversation.mp3"
        merge_audio_segments(segment_files, merged_file)

        logger.info("\n=== Test Complete ===")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Individual segments: {output_dir}")
        logger.info(f"Merged conversation: {merged_file}")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    test_voice_conversation() 