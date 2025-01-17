"""Test ElevenLabs API integration."""
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import (
    Client,
    VoiceSettings,
    Voice
)

# Initialize environment
load_dotenv()
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY not found in environment variables")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up output directory
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def test_elevenlabs_generation():
    """Test audio generation with ElevenLabs."""
    # Initialize client
    client = Client(api_key=ELEVENLABS_API_KEY)
    
    # Test text
    test_text = """
[HOST]
Welcome to our technical podcast. Today we're discussing artificial intelligence and its impact on modern software development.

[EXPERT]
Thank you for having me. Let me start by explaining what AI really means in today's context.
"""
    
    # Get available voices
    available_voices = client.voices.get_all()
    logger.info(f"Available voices: {[v.name for v in available_voices]}")
    
    try:
        # Create output directory
        output_dir = OUTPUT_DIR / "elevenlabs_test"
        output_dir.mkdir(exist_ok=True)
        
        # Split text by roles and generate audio
        lines = test_text.strip().split('\n')
        current_role = None
        current_text = []
        
        for line in lines:
            if line.startswith('['):
                # Process previous role's text
                if current_role and current_text:
                    text = ' '.join(current_text)
                    logger.info(f"Generating audio for {current_role}")
                    
                    # Select voice based on role
                    voice_name = "Rachel" if current_role == "[HOST]" else "Josh"
                    
                    # Generate audio
                    audio = client.generate(
                        text=text,
                        voice=voice_name,
                        model="eleven_multilingual_v2"
                    )
                    
                    # Save audio file
                    output_file = output_dir / f"{current_role.strip('[]').lower()}_test.mp3"
                    audio.save(str(output_file))
                    logger.info(f"Saved audio to {output_file}")
                
                # Start new role
                current_role = line
                current_text = []
            else:
                current_text.append(line.strip())
        
        # Process final role
        if current_role and current_text:
            text = ' '.join(current_text)
            logger.info(f"Generating audio for {current_role}")
            
            voice_name = "Rachel" if current_role == "[HOST]" else "Josh"
            audio = client.generate(
                text=text,
                voice=voice_name,
                model="eleven_multilingual_v2"
            )
            
            output_file = output_dir / f"{current_role.strip('[]').lower()}_test.mp3"
            audio.save(str(output_file))
            logger.info(f"Saved audio to {output_file}")
        
        logger.info("Audio generation complete!")
        
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise

if __name__ == "__main__":
    test_elevenlabs_generation() 