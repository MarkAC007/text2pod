"""
Main podcast generation pipeline for Text2Pod.
Coordinates JSON processing, voice mapping, and audio generation.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .utils.json_processor import JSONProcessor, PodcastData
from .utils.voice_mapper import VoiceMapper, VoiceConfig
from .utils.audio_generator import AudioGenerator
from .utils.error_handler import ProcessingError

logger = logging.getLogger(__name__)

class PodcastGenerationError(ProcessingError):
    """Custom error for podcast generation issues"""
    pass

class PodcastGenerator:
    """Main podcast generation pipeline."""
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        api_key: Optional[str] = None,
        cleanup_segments: bool = False
    ):
        """Initialize podcast generator."""
        self.output_dir = output_dir or Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cleanup_segments = cleanup_segments
        
        # Initialize components
        try:
            self.json_processor = JSONProcessor()
            self.voice_mapper = VoiceMapper(api_key=api_key)
            self.audio_generator = AudioGenerator(
                api_key=api_key,
                output_dir=self.output_dir
            )
        except Exception as e:
            raise PodcastGenerationError(f"Failed to initialize components: {e}")
    
    def generate_podcast(
        self,
        json_path: Path,
        project_name: str,
        crossfade_ms: int = 500
    ) -> Tuple[Path, Dict[str, str]]:
        """
        Generate a complete podcast from JSON specification.
        
        Args:
            json_path: Path to the JSON specification file
            project_name: Name of the podcast project (used for output files)
            crossfade_ms: Crossfade duration between segments in milliseconds
            
        Returns:
            Tuple of (podcast_file_path, metadata)
        """
        try:
            logger.info(f"Starting podcast generation for {project_name}")
            
            # Process JSON
            logger.info("Processing JSON specification")
            podcast_data = self.json_processor.process_json(json_path)
            
            # Get pronunciation guide
            pronunciations = self.json_processor.get_pronunciation_guide(podcast_data)
            logger.info(f"Generated pronunciations for {len(pronunciations)} terms")
            
            # Map voices
            logger.info("Mapping voices to segments")
            voice_mappings = self.voice_mapper.map_voices(podcast_data)
            
            # Generate audio
            logger.info("Generating audio segments")
            merged_file, segment_files = self.audio_generator.generate_podcast_audio(
                segments=voice_mappings,
                project_name=project_name,
                crossfade_ms=crossfade_ms
            )
            
            # Optional cleanup
            if self.cleanup_segments:
                logger.info("Cleaning up segment files")
                self.audio_generator.cleanup_segments(segment_files)
            
            # Prepare metadata
            metadata = {
                "title": project_name,
                "format": podcast_data.podcast_format.style,
                "technical_level": podcast_data.podcast_format.technical_level,
                "duration": podcast_data.podcast_format.estimated_duration,
                "segments": len(podcast_data.segments),
                "technical_terms": len(podcast_data.technical_glossary),
                "output_file": str(merged_file)
            }
            
            logger.info(f"Podcast generation complete: {merged_file}")
            return merged_file, metadata
            
        except Exception as e:
            raise PodcastGenerationError(f"Failed to generate podcast: {e}")
    
    def test_connections(self) -> Dict[str, bool]:
        """Test connections to required services."""
        results = {}
        
        try:
            # Test voice service
            results["voice_service"] = self.voice_mapper.test_voice_connection()
            
            # Test output directory
            try:
                test_file = self.output_dir / ".test_write"
                test_file.touch()
                test_file.unlink()
                results["output_directory"] = True
            except Exception:
                results["output_directory"] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Connection testing failed: {e}")
            return {"error": str(e)} 