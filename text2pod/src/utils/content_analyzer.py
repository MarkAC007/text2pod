"""Content analysis utilities."""
import json
import logging
from typing import Dict, List

from src.utils.openai_client import get_completion
from src.utils.error_handler import ContentAnalysisError

logger = logging.getLogger(__name__)

def format_to_markdown(raw_text: str) -> str:
    """Convert raw text to clean, structured markdown.
    
    This function focuses solely on cleaning and formatting the text content,
    without any analysis or JSON structures.
    """
    system_prompt = """You are an expert at converting raw document text into clean, well-structured markdown.
    
    Instructions:
    1. Clean the text:
       - Fix OCR/extraction artifacts
       - Remove unnecessary whitespace
       - Fix common formatting issues
       
    2. Structure the content:
       - Use proper heading levels (# for H1, ## for H2, etc.)
       - Format lists correctly (bulleted and numbered)
       - Preserve tables using markdown table syntax
       - Format code blocks with appropriate language tags
       
    3. Enhance readability:
       - Add appropriate line breaks
       - Ensure consistent spacing
       - Maintain document hierarchy
       
    4. Preserve:
       - Technical terminology
       - Important formatting
       - Document structure
       - Tables and diagrams (as markdown)
       
    Return only the cleaned markdown text, no analysis or JSON structures."""
    
    try:
        markdown_text = get_completion(system_prompt, raw_text, response_format="text")
        
        # Basic validation that we got markdown and not JSON
        if markdown_text.startswith('{') and markdown_text.endswith('}'):
            raise ContentAnalysisError("Received JSON instead of markdown text")
            
        return markdown_text
        
    except Exception as e:
        logger.error(f"Error in markdown formatting: {str(e)}")
        raise ContentAnalysisError(f"Failed to format markdown: {str(e)}")

def analyze_markdown_content(markdown_text: str) -> Dict:
    """Analyze markdown content to plan podcast structure.
    
    This function analyzes the cleaned markdown and returns structured data
    for podcast planning.
    """
    system_prompt = """You are an expert at analyzing technical content for podcast conversion.
    
    Analyze the provided markdown content and create a structured plan with:
    
    1. Content Structure:
       - Main topics and themes
       - Natural segment breaks
       - Key discussion points
       
    2. Technical Elements:
       - Important concepts to explain
       - Technical terms that need definition
       - Complex ideas that need breakdown
       
    3. Conversation Planning:
       - Questions to drive discussion
       - Transition points between topics
       - Engagement opportunities
    
    Return the analysis in the following JSON structure:
    {
        "podcast_format": {
            "recommended": "host_expert|two_experts|panel",
            "reasoning": "explanation of format choice"
        },
        "segments": [
            {
                "title": "segment title",
                "duration": "estimated minutes",
                "key_points": ["main points to cover"],
                "discussion_questions": ["questions to drive conversation"],
                "technical_terms": [
                    {
                        "term": "technical term",
                        "definition": "clear explanation",
                        "context": "when/how to introduce it"
                    }
                ]
            }
        ],
        "overall_notes": {
            "technical_level": "basic|intermediate|advanced",
            "target_duration": "total minutes",
            "special_considerations": ["any special notes"]
        }
    }"""
    
    try:
        response = get_completion(system_prompt, markdown_text, response_format="json_object")
        analysis = json.loads(response)
        
        # Validate the response structure
        required_fields = ['podcast_format', 'segments', 'overall_notes']
        if not all(field in analysis for field in required_fields):
            raise ContentAnalysisError("Incomplete analysis structure")
            
        return analysis
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response: {str(e)}")
        raise ContentAnalysisError("Failed to parse analysis response")
    except Exception as e:
        logger.error(f"Error in content analysis: {str(e)}")
        raise ContentAnalysisError(f"Failed to analyze content: {str(e)}") 