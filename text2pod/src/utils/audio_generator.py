"""
Audio generation module for Text2Pod.
Handles audio generation and assembly using ElevenLabs API.
"""

import os
import shutil
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pydub import AudioSegment

from utils.error_handler import ProcessingError
from utils.json_processor import PodcastSegment
from utils.voice_mapper import VoiceConfig

logger = logging.getLogger(__name__)

class AudioGenerationError(ProcessingError):
    """Custom error for audio generation issues"""
    pass

class AudioGenerator:
    """Handles audio generation and assembly for podcast segments."""
    
    def __init__(self, api_key: Optional[str] = None, output_dir: Optional[Path] = None):
        """Initialize AudioGenerator."""
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise AudioGenerationError("ELEVENLABS_API_KEY not found")
            
        self.base_url = "https://api.elevenlabs.io/v1"
        self.output_dir = output_dir or Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify ffmpeg installation
        if not self._check_ffmpeg():
            raise AudioGenerationError(
                "ffmpeg not found. Please install ffmpeg:\n"
                "Windows (conda): conda install ffmpeg\n"
                "Windows (chocolatey): choco install ffmpeg\n"
                "Linux: sudo apt-get install ffmpeg\n"
                "Mac: brew install ffmpeg"
            )
    
    def _check_ffmpeg(self) -> bool:
        """Verify ffmpeg is installed and accessible."""
        return shutil.which('ffmpeg') is not None
    
    def generate_segment_audio(
        self,
        segment: PodcastSegment,
        voice_config: VoiceConfig,
        output_path: Optional[Path] = None
    ) -> Path:
        """Generate audio for a single segment."""
        try:
            # Prepare headers and payload
            headers = {
                "Accept": "audio/mpeg",
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": segment.content,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": voice_config.settings
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_config.voice_id}",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise AudioGenerationError(f"TTS request failed: {response.text}")
            
            # Determine output path
            if output_path is None:
                output_path = self.output_dir / f"{segment.id}_{voice_config.name}.mp3"
            
            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Generated audio for segment {segment.id}: {output_path}")
            return output_path
            
        except Exception as e:
            raise AudioGenerationError(f"Failed to generate audio for segment {segment.id}: {e}")
    
    def generate_podcast_audio(
        self,
        segments: List[Tuple[PodcastSegment, VoiceConfig]],
        project_name: str,
        crossfade_ms: int = 500
    ) -> Tuple[Path, List[Path]]:
        """Generate audio for all segments and combine them."""
        try:
            # Create project directory
            project_dir = self.output_dir / project_name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            segment_files = []
            
            # Generate audio for each segment
            for i, (segment, voice_config) in enumerate(segments, 1):
                output_path = project_dir / f"segment_{i:02d}_{segment.speaker}.mp3"
                segment_file = self.generate_segment_audio(
                    segment=segment,
                    voice_config=voice_config,
                    output_path=output_path
                )
                segment_files.append(segment_file)
            
            # Merge segments
            merged_file = project_dir / "complete_podcast.mp3"
            self.merge_audio_segments(
                segment_files=segment_files,
                output_file=merged_file,
                crossfade_ms=crossfade_ms
            )
            
            logger.info(f"Generated complete podcast audio: {merged_file}")
            return merged_file, segment_files
            
        except Exception as e:
            raise AudioGenerationError(f"Failed to generate podcast audio: {e}")
    
    def merge_audio_segments(
        self,
        segment_files: List[Path],
        output_file: Path,
        crossfade_ms: int = 500
    ) -> Path:
        """Merge multiple audio segments with crossfade."""
        try:
            # Verify all files exist
            for file in segment_files:
                if not file.exists():
                    raise FileNotFoundError(f"Audio segment not found: {file}")
            
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
            raise AudioGenerationError(f"Failed to merge audio segments: {e}")
    
    def cleanup_segments(self, segment_files: List[Path]) -> None:
        """Optionally cleanup individual segment files."""
        try:
            for file in segment_files:
                if file.exists():
                    file.unlink()
            logger.info("Cleaned up segment files")
        except Exception as e:
            logger.warning(f"Failed to cleanup some segment files: {e}") 