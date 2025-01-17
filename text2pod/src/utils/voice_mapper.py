"""
Voice mapping module for Text2Pod.
Maps podcast speakers to ElevenLabs voices and manages voice settings.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
from pathlib import Path

from utils.error_handler import ProcessingError
from utils.json_processor import PodcastData, PodcastSegment

logger = logging.getLogger(__name__)

@dataclass
class VoiceConfig:
    voice_id: str
    name: str
    settings: Dict[str, float]

class VoiceMappingError(ProcessingError):
    """Custom error for voice mapping issues"""
    pass

class VoiceMapper:
    """Maps podcast speakers to ElevenLabs voices and manages voice settings."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize VoiceMapper with API key."""
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise VoiceMappingError("ELEVENLABS_API_KEY not found")
            
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Default voice assignments
        self.default_voices = {
            "host": "Jessica",  # Friendly, engaging host voice
            "expert": "Daniel", # Authoritative expert voice
            "panelist": "Adam"  # Clear, neutral panelist voice
        }
        
        # Default voice settings per role
        self.default_settings = {
            "host": {
                "stability": 0.71,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "expert": {
                "stability": 0.75,  # More stable for technical content
                "similarity_boost": 0.6,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "panelist": {
                "stability": 0.71,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        # Cache for voice IDs
        self.voice_id_cache: Dict[str, str] = {}
        
    def get_available_voices(self) -> List[Dict]:
        """Fetch available voices from ElevenLabs."""
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["voices"]
        except Exception as e:
            raise VoiceMappingError(f"Failed to fetch voices: {e}")
    
    def get_voice_id(self, voice_name: str) -> str:
        """Get voice ID for a given voice name."""
        # Check cache first
        if voice_name in self.voice_id_cache:
            return self.voice_id_cache[voice_name]
            
        # Fetch from API
        voices = self.get_available_voices()
        for voice in voices:
            if voice["name"] == voice_name:
                self.voice_id_cache[voice_name] = voice["voice_id"]
                return voice["voice_id"]
                
        raise VoiceMappingError(f"Voice not found: {voice_name}")
    
    def get_voice_config(self, speaker: str, tone: str) -> VoiceConfig:
        """Get voice configuration for a speaker."""
        if speaker not in self.default_voices:
            raise VoiceMappingError(f"Unsupported speaker type: {speaker}")
            
        voice_name = self.default_voices[speaker]
        voice_id = self.get_voice_id(voice_name)
        
        # Start with default settings
        settings = self.default_settings[speaker].copy()
        
        # Adjust settings based on tone
        if tone == "authoritative":
            settings["stability"] = 0.8
            settings["similarity_boost"] = 0.7
        elif tone == "welcoming":
            settings["stability"] = 0.65
            settings["style"] = 0.1
            
        return VoiceConfig(
            voice_id=voice_id,
            name=voice_name,
            settings=settings
        )
    
    def map_voices(self, podcast_data: PodcastData) -> List[Tuple[PodcastSegment, VoiceConfig]]:
        """Map all segments to voice configurations."""
        voice_mappings = []
        
        for segment in podcast_data.segments:
            voice_config = self.get_voice_config(
                speaker=segment.speaker,
                tone=segment.tone
            )
            voice_mappings.append((segment, voice_config))
            
        return voice_mappings
    
    def test_voice_connection(self) -> bool:
        """Test connection to ElevenLabs API."""
        try:
            self.get_available_voices()
            return True
        except Exception as e:
            logger.error(f"Voice connection test failed: {e}")
            return False 