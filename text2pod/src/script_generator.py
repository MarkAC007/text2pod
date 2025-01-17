"""Script generation module for Text2Pod."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from src.utils.error_handler import Text2PodError, retry_on_error
from src.utils.openai_client import analyze_content
from src.utils.progress import ProgressTracker
from src.utils.config import MAX_SEGMENT_LENGTH

logger = logging.getLogger(__name__)

class ScriptFormat:
    """Available script formats."""
    HOST_EXPERT = "host_expert"
    TWO_EXPERTS = "two_experts"
    PANEL = "panel"

class ScriptGenerationError(Text2PodError):
    """Raised when there's an error generating the script."""
    pass

class ScriptGenerator:
    """Handles the generation of dialogue scripts from processed text."""
    
    def __init__(self, content: Dict[int, str]):
        """Initialize the script generator."""
        logger.info("Initializing script generator")
        logger.debug(f"Content received: {len(content)} pages")
        
        self.content = content
        self.format = None
        self.segments = []
        
        # Combine all content for analysis
        self.full_text = "\n".join(content.values())
        logger.debug(f"Combined text length: {len(self.full_text)} characters")
    
    def analyze_content(self) -> str:
        """Analyze content using OpenAI to suggest best script format."""
        logger.info("Starting content analysis")
        
        # Get OpenAI's analysis
        analysis = json.loads(analyze_content(self.full_text))
        
        # Store the suggested segments for later use
        self.suggested_segments = analysis.get('suggested_segments', [])
        logger.info(f"Received {len(self.suggested_segments)} suggested segments")
        logger.debug(f"Suggested segments: {self.suggested_segments}")
        
        # Log the reasoning
        logger.info(f"Format recommendation: {analysis['format']}")
        logger.info(f"Reasoning: {analysis['reasoning']}")
        
        self.format = analysis['format']
        return self.format
    
    def segment_content(self) -> List[Dict]:
        """Break content into logical segments based on OpenAI suggestions."""
        logger.info("Starting content segmentation")
        
        if not self.suggested_segments:
            logger.debug("No segments found, running content analysis")
            self.analyze_content()
        
        segments = []
        current_segment = {"content": "", "key_points": []}
        segment_index = 0
        
        for page_num, text in self.content.items():
            logger.debug(f"Processing page {page_num}")
            current_segment["content"] += f"\n{text}"
            
            # Use suggested segments as titles and break points
            if len(current_segment["content"]) > MAX_SEGMENT_LENGTH and segment_index < len(self.suggested_segments):
                current_segment["title"] = self.suggested_segments[segment_index]
                segments.append(current_segment)
                logger.info(f"Created segment: {current_segment['title']} ({len(current_segment['content'])} chars)")
                current_segment = {"content": "", "key_points": []}
                segment_index += 1
        
        # Add remaining content as final segment
        if current_segment["content"]:
            current_segment["title"] = (
                self.suggested_segments[segment_index]
                if segment_index < len(self.suggested_segments)
                else f"Segment {len(segments) + 1}"
            )
            segments.append(current_segment)
            logger.info(f"Created final segment: {current_segment['title']} ({len(current_segment['content'])} chars)")
        
        logger.info(f"Content segmentation complete. Created {len(segments)} segments")
        self.segments = segments
        return segments
    
    @retry_on_error()
    def generate_script(self, format: Optional[str] = None) -> Dict:
        """Generate dialogue script from content.
        
        Args:
            format: Optional format override (defaults to analyzed format)
            
        Returns:
            Dictionary containing:
            - format: str
            - segments: List[Dict]
            - characters: List[str]
            - script: List[Dict]
        """
        if not self.content:
            raise ScriptGenerationError("No content to generate script from")
        
        # Determine format
        self.format = format or self.analyze_content()
        
        # Segment content if not already done
        if not self.segments:
            self.segment_content()
        
        # TODO: Implement actual script generation
        # For now, create a basic host/expert dialogue
        script = {
            "format": self.format,
            "characters": ["Host", "Expert"],
            "segments": self.segments,
            "script": []
        }
        
        for segment in self.segments:
            script["script"].extend([
                {
                    "speaker": "Host",
                    "text": f"Let's talk about {segment['title']}. What are the key points here?"
                },
                {
                    "speaker": "Expert",
                    "text": segment["content"][:200] + "..."  # Truncated for now
                }
            ])
        
        return script 