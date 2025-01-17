"""Configuration management for Text2Pod."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Create necessary directories
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY not found in environment variables")

# Model Configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Processing Configuration
MAX_SEGMENT_LENGTH = int(os.getenv("MAX_SEGMENT_LENGTH", "5000"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1")) 