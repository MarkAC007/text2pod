"""Voice processing module for Text2Pod."""
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
import csv
import json

from src.utils.config import OUTPUT_DIR
from src.utils.error_handler import VoiceProcessingError
from src.utils.progress import ProgressTracker

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Handles voice script preparation for ElevenLabs."""
    
    # Voice role configurations
    VOICE_ROLES = {
        "HOST": {
            "name": "Host",
            "style": "conversational",
            "ssml_settings": {
                "rate": "medium",
                "pitch": "medium",
                "volume": "loud"
            }
        },
        "EXPERT": {
            "name": "Expert",
            "style": "professional",
            "ssml_settings": {
                "rate": "medium-slow",
                "pitch": "low",
                "volume": "medium"
            }
        },
        "PANELIST": {
            "name": "Panelist",
            "style": "casual",
            "ssml_settings": {
                "rate": "medium",
                "pitch": "medium",
                "volume": "medium"
            }
        }
    }
    
    def __init__(self, analysis_file: Path, use_ssml: bool = True):
        """Initialize voice processor.
        
        Args:
            analysis_file: Path to the analysis JSON file
            use_ssml: Whether to include SSML tags
        """
        self.analysis_file = analysis_file
        self.use_ssml = use_ssml
        self.output_dir = OUTPUT_DIR / analysis_file.stem
        self.output_dir.mkdir(exist_ok=True)
        
        # Load and validate analysis JSON
        try:
            with open(analysis_file, 'r') as f:
                self.analysis = json.load(f)
            self._validate_analysis()
        except Exception as e:
            raise VoiceProcessingError(f"Failed to load/validate analysis file: {str(e)}")
    
    def _validate_analysis(self):
        """Validate the analysis JSON structure."""
        required_fields = ['podcast_format', 'segments']
        if not all(field in self.analysis for field in required_fields):
            raise VoiceProcessingError("Missing required fields in analysis")
        
        if not isinstance(self.analysis['segments'], list):
            raise VoiceProcessingError("Segments must be a list")
        
        for segment in self.analysis['segments']:
            if not isinstance(segment, dict):
                raise VoiceProcessingError("Each segment must be a dictionary")
            if 'title' not in segment:
                raise VoiceProcessingError("Each segment must have a title")
    
    def _add_ssml(self, text: str, role: str) -> str:
        """Add SSML tags to text.
        
        Args:
            text: Text to wrap in SSML
            role: Speaker role for voice settings
        """
        if not self.use_ssml:
            return text
            
        settings = self.VOICE_ROLES[role]["ssml_settings"]
        
        # Clean text for SSML
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        ssml = f"""<speak>
    <prosody rate="{settings['rate']}" 
             pitch="{settings['pitch']}" 
             volume="{settings['volume']}">
        {text}
    </prosody>
</speak>"""
        
        return ssml
    
    def _format_line(self, role: str, text: str) -> str:
        """Format a single line of dialogue.
        
        Args:
            role: Speaker role (HOST, EXPERT, etc.)
            text: Line of dialogue
        """
        if role not in self.VOICE_ROLES:
            raise VoiceProcessingError(f"Invalid role: {role}")
            
        formatted_text = text.strip()
        if self.use_ssml:
            formatted_text = self._add_ssml(formatted_text, role)
            
        return f"[{role}]\n{formatted_text}\n"
    
    def _format_intro(self) -> str:
        """Format podcast introduction."""
        podcast_format = self.analysis.get("podcast_format", {})
        format_type = podcast_format.get("recommended", "host_expert")
        
        intro_text = [
            self._format_line("HOST", 
                "Welcome to this episode where we'll be discussing an important technical topic."),
            self._format_line("HOST",
                f"We'll be using a {format_type} format to explore this subject in detail."),
            self._format_line("HOST", "Let's get started.")
        ]
        
        return "\n".join(intro_text)
    
    def _format_segment(self, index: int, segment: Dict) -> str:
        """Format a podcast segment with enhanced structure."""
        title = segment.get("title", f"Segment {index}")
        key_points = segment.get("key_points", [])
        discussion = segment.get("discussion_questions", [])
        terms = segment.get("technical_terms", [])
        
        segment_parts = [
            f"\n=== SEGMENT {index} ===\n",
            self._format_line("HOST", f"Let's move on to {title}.")
        ]
        
        # Add key points with transitions
        for i, point in enumerate(key_points, 1):
            if i == 1:
                segment_parts.append(self._format_line("EXPERT", 
                    f"Let me start by explaining {point}"))
            else:
                segment_parts.append(self._format_line("EXPERT",
                    f"Furthermore, {point}"))
        
        # Add interactive discussion
        for question in discussion:
            segment_parts.append(self._format_line("HOST", question))
            # Add expert response placeholder
            segment_parts.append(self._format_line("EXPERT",
                "That's an interesting question. Let me address that..."))
        
        # Add technical terms with clear structure
        for term in terms:
            term_text = (
                f"Let me explain {term['term']}. {term['definition']}"
            )
            segment_parts.append(self._format_line("EXPERT", term_text))
        
        return "\n".join(segment_parts)
    
    def _format_outro(self) -> str:
        """Format podcast conclusion with enhanced structure."""
        outro_parts = [
            "\n=== OUTRO ===\n",
            self._format_line("HOST",
                "That brings us to the end of our discussion."),
            self._format_line("EXPERT",
                "Thank you for having me. I hope this information has been helpful."),
            self._format_line("HOST",
                "Thank you for listening, and we'll see you in the next episode.")
        ]
        
        return "\n".join(outro_parts)
    
    def validate_script(self, script_text: str) -> bool:
        """Validate the generated script.
        
        Args:
            script_text: The script to validate
            
        Returns:
            bool: True if valid, raises exception if invalid
        """
        # Check for balanced SSML tags if used
        if self.use_ssml:
            if not self._validate_ssml(script_text):
                raise VoiceProcessingError("Invalid SSML tags in script")
        
        # Check for valid role markers
        role_pattern = r'\[(HOST|EXPERT|PANELIST)\]'
        roles = re.findall(role_pattern, script_text)
        if not roles:
            raise VoiceProcessingError("No valid role markers found in script")
        
        # Check for segment structure
        if "=== SEGMENT 1 ===" not in script_text:
            raise VoiceProcessingError("Missing segment structure")
        
        return True
    
    def _validate_ssml(self, text: str) -> bool:
        """Validate SSML tags in text."""
        if not self.use_ssml:
            return True
            
        # Check for balanced speak tags
        speak_count = text.count("<speak>")
        speak_end_count = text.count("</speak>")
        if speak_count != speak_end_count:
            return False
            
        # Check for balanced prosody tags
        prosody_count = text.count("<prosody")
        prosody_end_count = text.count("</prosody>")
        if prosody_count != prosody_end_count:
            return False
            
        return True 