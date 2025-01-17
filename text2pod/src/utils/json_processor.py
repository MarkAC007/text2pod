"""
JSON Processing module for Text2Pod.
Handles parsing and validation of podcast JSON data structures.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from .error_handler import ProcessingError

@dataclass
class PodcastFormat:
    style: str
    technical_level: str
    estimated_duration: str

@dataclass
class PodcastSegment:
    id: str
    speaker: str
    content: str
    tone: str
    technical_terms: List[str]

@dataclass
class PodcastData:
    podcast_format: PodcastFormat
    segments: List[PodcastSegment]
    technical_glossary: Dict[str, str]

class JSONProcessingError(ProcessingError):
    """Custom error for JSON processing issues"""
    pass

class JSONProcessor:
    """Handles parsing and validation of podcast JSON data"""
    
    def __init__(self):
        self.supported_styles = ["interview", "panel", "monologue"]
        self.supported_levels = ["beginner", "intermediate", "advanced"]
        self.supported_speakers = ["host", "expert", "panelist"]
        
    def load_json(self, json_path: Path) -> Dict:
        """Load JSON file and return dictionary"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise JSONProcessingError(f"Failed to load JSON file: {e}")
    
    def validate_format(self, format_data: Dict) -> PodcastFormat:
        """Validate podcast format section"""
        if not isinstance(format_data, dict):
            raise JSONProcessingError("Podcast format must be a dictionary")
            
        style = format_data.get('style')
        if style not in self.supported_styles:
            raise JSONProcessingError(f"Unsupported podcast style: {style}")
            
        level = format_data.get('technical_level')
        if level not in self.supported_levels:
            raise JSONProcessingError(f"Unsupported technical level: {level}")
            
        return PodcastFormat(
            style=style,
            technical_level=level,
            estimated_duration=format_data.get('estimated_duration', 'unknown')
        )
    
    def validate_segment(self, segment_data: Dict) -> PodcastSegment:
        """Validate a single podcast segment"""
        if not isinstance(segment_data, dict):
            raise JSONProcessingError("Segment must be a dictionary")
            
        segment_id = segment_data.get('id')
        if not segment_id:
            raise JSONProcessingError("Segment must have an ID")
            
        speaker = segment_data.get('speaker')
        if speaker not in self.supported_speakers:
            raise JSONProcessingError(f"Unsupported speaker type: {speaker}")
            
        content = segment_data.get('content')
        if not content:
            raise JSONProcessingError("Segment must have content")
            
        return PodcastSegment(
            id=segment_id,
            speaker=speaker,
            content=content,
            tone=segment_data.get('tone', 'neutral'),
            technical_terms=segment_data.get('technical_terms', [])
        )
    
    def process_json(self, json_path: Path) -> PodcastData:
        """Process JSON file and return validated PodcastData"""
        data = self.load_json(json_path)
        
        # Validate required sections
        if not all(k in data for k in ['podcast_format', 'segments']):
            raise JSONProcessingError("JSON must contain podcast_format and segments")
            
        # Process format
        podcast_format = self.validate_format(data['podcast_format'])
        
        # Process segments
        segments = [self.validate_segment(s) for s in data['segments']]
        
        # Process glossary (optional)
        glossary = data.get('technical_glossary', {})
        
        return PodcastData(
            podcast_format=podcast_format,
            segments=segments,
            technical_glossary=glossary
        )
    
    def get_pronunciation_guide(self, data: PodcastData) -> Dict[str, str]:
        """Extract technical terms and their pronunciations from glossary"""
        pronunciations = {}
        for term, definition in data.technical_glossary.items():
            # For now, just use the term as pronunciation
            # TODO: Implement proper pronunciation generation
            pronunciations[term] = term
        return pronunciations 