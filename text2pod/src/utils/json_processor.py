"""
JSON Processing module for Text2Pod.
Handles parsing and validation of podcast JSON data structures.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from utils.error_handler import ProcessingError

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
    
    def convert_analysis_to_podcast_format(self, analysis_data: Dict) -> Dict:
        """Convert analysis JSON to podcast format."""
        try:
            # Extract format information
            podcast_format = {
                "style": analysis_data.get("podcast_format", {}).get("recommended", "panel"),
                "technical_level": analysis_data.get("overall_notes", {}).get("technical_level", "intermediate"),
                "estimated_duration": analysis_data.get("overall_notes", {}).get("target_duration", "60") + "min"
            }
            
            # Build segments
            segments = []
            technical_glossary = {}
            
            # Add host introduction
            segments.append({
                "id": "intro_001",
                "speaker": "host",
                "content": "Welcome to our podcast on artificial intelligence. Today, we'll be discussing important insights from the European Commission's White Paper on AI.",
                "tone": "welcoming",
                "technical_terms": []
            })
            
            # Process each segment
            for i, seg in enumerate(analysis_data.get("segments", []), 1):
                # Host introduction for segment
                segments.append({
                    "id": f"host_{i:03d}",
                    "speaker": "host",
                    "content": f"Let's discuss {seg['title']}. {seg['discussion_questions'][0]}",
                    "tone": "curious",
                    "technical_terms": []
                })
                
                # Expert response
                key_points = ". ".join(seg["key_points"])
                segments.append({
                    "id": f"expert_{i:03d}",
                    "speaker": "expert",
                    "content": f"{key_points}",
                    "tone": "authoritative",
                    "technical_terms": [term["term"] for term in seg.get("technical_terms", [])]
                })
                
                # Add technical terms to glossary
                for term_data in seg.get("technical_terms", []):
                    technical_glossary[term_data["term"]] = term_data["definition"]
            
            # Add closing
            segments.append({
                "id": "closing_001",
                "speaker": "host",
                "content": "Thank you for joining us for this discussion on artificial intelligence and its implications for Europe.",
                "tone": "welcoming",
                "technical_terms": []
            })
            
            return {
                "podcast_format": podcast_format,
                "segments": segments,
                "technical_glossary": technical_glossary
            }
            
        except Exception as e:
            raise JSONProcessingError(f"Failed to convert analysis to podcast format: {e}")
    
    def process_json(self, json_path: Path) -> PodcastData:
        """Process JSON file and return validated PodcastData"""
        data = self.load_json(json_path)
        
        # Check if this is an analysis JSON and convert if needed
        if "podcast_format" in data and isinstance(data["podcast_format"], dict) and "recommended" in data["podcast_format"]:
            data = self.convert_analysis_to_podcast_format(data)
        
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