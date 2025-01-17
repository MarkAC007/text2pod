"""Voice processing module for Text2Pod."""
import logging
from pathlib import Path
from typing import Dict, List
import csv
import json

from elevenlabs import Voice, VoiceSettings, generate, save
from elevenlabs import set_api_key as set_elevenlabs_key

from src.utils.config import ELEVENLABS_API_KEY, OUTPUT_DIR
from src.utils.error_handler import VoiceProcessingError
from src.utils.progress import ProgressTracker

logger = logging.getLogger(__name__)

# Initialize ElevenLabs
set_elevenlabs_key(ELEVENLABS_API_KEY)

class VoiceProcessor:
    """Handles voice processing and CSV generation."""
    
    # Voice configurations for different roles
    VOICE_CONFIGS = {
        "host": {
            "voice_id": "your_host_voice_id",
            "settings": VoiceSettings(
                stability=0.5,
                clarity=0.8,
                style=0.3
            )
        },
        "expert": {
            "voice_id": "your_expert_voice_id",
            "settings": VoiceSettings(
                stability=0.6,
                clarity=0.9,
                style=0.2
            )
        }
    }
    
    def __init__(self, analysis_file: Path):
        """Initialize voice processor."""
        self.analysis_file = analysis_file
        self.output_dir = OUTPUT_DIR / analysis_file.stem
        self.output_dir.mkdir(exist_ok=True)
        
        # Load analysis JSON
        try:
            with open(analysis_file, 'r') as f:
                self.analysis = json.load(f)
        except Exception as e:
            raise VoiceProcessingError(f"Failed to load analysis file: {str(e)}")
    
    def generate_csv(self) -> Path:
        """Generate CSV file for voice processing."""
        csv_file = self.output_dir / "voice_segments.csv"
        
        try:
            segments = self.analysis.get("segments", [])
            if not segments:
                raise VoiceProcessingError("No segments found in analysis")
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "segment_id", "voice_id", "text",
                    "stability", "clarity", "style"
                ])
                
                for i, segment in enumerate(segments, 1):
                    # Determine voice based on content
                    voice_config = self._select_voice_config(segment)
                    
                    writer.writerow([
                        f"segment_{i:03d}",
                        voice_config["voice_id"],
                        self._prepare_text(segment),
                        voice_config["settings"].stability,
                        voice_config["settings"].clarity,
                        voice_config["settings"].style
                    ])
            
            logger.info(f"Generated voice CSV: {csv_file}")
            return csv_file
            
        except Exception as e:
            raise VoiceProcessingError(f"Failed to generate CSV: {str(e)}")
    
    def _select_voice_config(self, segment: Dict) -> Dict:
        """Select appropriate voice configuration based on segment content."""
        # TODO: Implement more sophisticated voice selection
        return self.VOICE_CONFIGS["expert"]
    
    def _prepare_text(self, segment: Dict) -> str:
        """Prepare segment text for voice generation."""
        # Combine relevant segment information
        text_parts = [
            segment.get("title", ""),
            *segment.get("key_points", []),
            # Add more segment elements as needed
        ]
        
        return " ".join(filter(None, text_parts)) 