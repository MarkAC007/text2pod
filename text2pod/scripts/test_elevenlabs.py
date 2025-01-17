"""Test ElevenLabs API integration."""
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests

# Set up logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"elevenlabs_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_elevenlabs_generation():
    """Test audio generation with ElevenLabs."""
    try:
        logger.info("=== Starting ElevenLabs Test ===")
        
        # Load API key
        load_dotenv()
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment")
        logger.info("API key loaded successfully")

        # API endpoints
        BASE_URL = "https://api.elevenlabs.io/v1"
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }

        # List available voices
        logger.info("\n=== Voice Information ===")
        voices_response = requests.get(f"{BASE_URL}/voices", headers=headers)
        voices_data = voices_response.json()
        
        # Log available voices
        logger.info("Available voices:")
        selected_voice_id = None
        selected_voice_name = "Jessica"
        
        for voice in voices_data["voices"]:
            logger.info(f"- {voice['name']} (ID: {voice['voice_id']})")
            if voice["name"] == selected_voice_name:
                selected_voice_id = voice["voice_id"]

        if not selected_voice_id:
            raise ValueError(f"{selected_voice_name} voice not found in available voices")
        logger.info(f"Using {selected_voice_name} voice ID: {selected_voice_id}")

        # Test text
        test_text = """
[HOST]
Welcome to our technical podcast. Today we're discussing artificial intelligence.
"""
        logger.info("\n=== Test Configuration ===")
        logger.info(f"Test text: {test_text.strip()}")
        
        # Voice settings
        voice_settings = {
            "stability": 0.71,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }
        logger.info(f"Voice settings: {voice_settings}")

        # Generate audio
        logger.info("\n=== Generating Audio ===")
        
        tts_headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        tts_payload = {
            "text": test_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": voice_settings
        }
        
        tts_response = requests.post(
            f"{BASE_URL}/text-to-speech/{selected_voice_id}",
            json=tts_payload,
            headers=tts_headers
        )
        
        if tts_response.status_code != 200:
            raise ValueError(f"TTS request failed: {tts_response.text}")
            
        audio = tts_response.content
        logger.info("Audio generation successful")

        # Save the audio
        output_dir = Path(__file__).parent.parent / "output" / "elevenlabs_test"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "test_generation.mp3"
        
        with open(output_file, 'wb') as f:
            f.write(audio)
        logger.info(f"Audio saved to: {output_file}")
        
        logger.info("\n=== Test Complete ===")
        logger.info(f"Log file: {log_file}")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    test_elevenlabs_generation() 