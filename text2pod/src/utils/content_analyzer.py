"""Content analysis utilities."""
import logging
from typing import Dict, List

from src.utils.openai_client import get_completion
from src.utils.error_handler import ContentAnalysisError

logger = logging.getLogger(__name__)

def analyze_document_structure(content: Dict[int, str]) -> Dict:
    """Analyze document structure to identify relevant content.
    
    Args:
        content: Dictionary mapping page numbers to text content
        
    Returns:
        Dictionary containing:
        - main_content: Dict[int, str] - Clean, relevant content
        - metadata: Dict - Information about document structure
    """
    try:
        # Combine first few pages for initial analysis
        sample = "\n".join([text for page, text in content.items()][:10])
        
        system_prompt = """<purpose>
    You are an expert at analyzing document structure and identifying relevant content.
    You excel at distinguishing between core content and supplementary material.
</purpose>

<instructions>
    <instruction>Analyze the document structure to identify:
        - Table of contents location
        - Start of main content
        - Supplementary sections (appendices, references, etc.)
        - Chapter/section patterns
    </instruction>
    <instruction>Evaluate content relevance based on:
        - Relation to main subject matter
        - Information density
        - Technical value
    </instruction>
    <instruction>Provide structural guidance:
        - Where to start content extraction
        - What patterns indicate chapter starts
        - Which sections to exclude
    </instruction>
    <instruction>Return analysis in JSON format:
    {
        "content_start_marker": "text or pattern that indicates main content start",
        "content_end_marker": "text or pattern that indicates main content end",
        "exclude_patterns": ["pattern1", "pattern2"],
        "chapter_patterns": ["pattern1", "pattern2"],
        "irrelevant_sections": ["section names to skip"],
        "structure_notes": "Additional observations about document structure"
    }</instruction>
</instructions>"""

        user_prompt = f"""<content>
    {sample}
</content>"""

        logger.info("Analyzing document structure")
        structure_analysis = get_completion(system_prompt, user_prompt)
        
        # Now use the analysis to clean the content
        return clean_content(content, structure_analysis)
        
    except Exception as e:
        raise ContentAnalysisError(f"Error analyzing document structure: {str(e)}")

def clean_content(content: Dict[int, str], structure_analysis: Dict) -> Dict:
    """Clean content based on structural analysis.
    
    Args:
        content: Original content by page
        structure_analysis: Structure analysis from OpenAI
        
    Returns:
        Dictionary containing cleaned content and metadata
    """
    logger.info("Cleaning content based on structural analysis")
    clean_pages = {}
    in_main_content = False
    
    for page_num, text in content.items():
        # Check if we've reached main content
        if not in_main_content and structure_analysis['content_start_marker'] in text:
            in_main_content = True
            logger.info(f"Main content starts at page {page_num}")
        
        # Check if we've reached the end
        if in_main_content and structure_analysis['content_end_marker'] in text:
            logger.info(f"Main content ends at page {page_num}")
            break
        
        # Skip irrelevant sections
        should_skip = any(
            pattern in text 
            for pattern in structure_analysis['exclude_patterns']
        )
        if should_skip:
            logger.debug(f"Skipping page {page_num} - matches exclude pattern")
            continue
        
        # Include relevant content
        if in_main_content:
            clean_pages[page_num] = text
    
    return {
        'main_content': clean_pages,
        'metadata': {
            'original_pages': len(content),
            'cleaned_pages': len(clean_pages),
            'structure_notes': structure_analysis['structure_notes']
        }
    } 