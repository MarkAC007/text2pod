"""Diagnostic script for ElevenLabs."""
import sys
import logging
from datetime import datetime
from pathlib import Path
from elevenlabs import api

# Set up logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"elevenlabs_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_diagnostics():
    """Run diagnostic checks for ElevenLabs setup."""
    try:
        # 1. Package Information
        logger.info("=== Package Information ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"ElevenLabs version: {api.__version__}")

        # 2. Test API Key Setup
        logger.info("\n=== API Key Setup ===")
        import os
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('ELEVENLABS_API_KEY')
        logger.info(f"API Key present: {bool(api_key)}")

        # 3. Test Voice Listing
        logger.info("\n=== Voice Listing Test ===")
        try:
            available_voices = api.Voices.from_api(api_key=api_key)
            logger.info(f"Available voices: {[v.name for v in available_voices]}")
        except Exception as e:
            logger.error(f"Voice listing error: {e}", exc_info=True)

        # 4. Test Simple Generation
        logger.info("\n=== Generation Test ===")
        try:
            test_text = "This is a test of the ElevenLabs API."
            audio = api.TextToSpeech.generate(
                api_key=api_key,
                text=test_text,
                voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice ID
                model_id="eleven_monolingual_v1"
            )
            
            # Save test audio
            output_dir = Path(__file__).parent.parent / "output" / "elevenlabs_test"
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / "test_generation.mp3"
            
            with open(output_file, 'wb') as f:
                f.write(audio)
            logger.info(f"Audio generation successful, saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Generation error: {e}", exc_info=True)

        logger.info("\n=== Diagnostic Complete ===")
        logger.info(f"Log file saved to: {log_file}")

    except Exception as e:
        logger.error(f"Diagnostic failed: {e}", exc_info=True)

if __name__ == "__main__":
    run_diagnostics() 