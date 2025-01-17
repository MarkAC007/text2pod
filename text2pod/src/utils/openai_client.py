"""OpenAI API client utilities."""
import logging
import time
from typing import Dict, List, Optional

import openai
from openai import OpenAI

from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL
from src.utils.error_handler import APIError, retry_on_error

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

@retry_on_error()
def get_completion(system_prompt: str, user_prompt: str) -> Dict:
    """Get completion from OpenAI API.
    
    Args:
        system_prompt: System role instructions
        user_prompt: User input/request
        
    Returns:
        Parsed JSON response from OpenAI
    """
    try:
        logger.info(f"Getting completion with model: {OPENAI_MODEL}")
        logger.debug(f"System prompt length: {len(system_prompt)} chars")
        logger.debug(f"User prompt length: {len(user_prompt)} chars")
        
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"OpenAI API response received in {elapsed_time:.2f} seconds")
        
        result = response.choices[0].message.content
        logger.debug(f"Raw API response: {result}")
        
        return result

    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise APIError(f"OpenAI API error: {str(e)}")

@retry_on_error()
def analyze_content(content: str) -> Dict:
    """Analyze content using OpenAI to determine best podcast format."""
    try:
        logger.info(f"Starting content analysis with model: {OPENAI_MODEL}")
        logger.debug(f"Content length: {len(content)} characters")
        
        system_prompt = """<purpose>
    You are an expert at analyzing content to determine the optimal podcast format based on content characteristics.
    You follow the instructions perfectly to evaluate content and select the best-suited podcast format.
</purpose>

<instructions>
    <instruction>Evaluate the content based on key factors: Content complexity level, Number of distinct viewpoints present, Technical depth of material, Natural conversation potential.</instruction>
    <instruction>Consider available podcast formats: host_expert: Traditional interview format, two_experts: Dialogue between different perspectives, panel: Multi-expert discussion.</instruction>
    <instruction>Analyze content structure for: Main topics and subtopics, Technical concepts, Contrasting viewpoints, Discussion points.</instruction>
    <instruction>Generate JSON response containing: Recommended format, Detailed reasoning, Suggested content segments.</instruction>
    <instruction>Format output as: { "format": "chosen_format", "reasoning": "detailed explanation", "suggested_segments": ["topic1", "topic2", ...] }</instruction>
    <instruction>Ensure reasoning addresses: Why the format best fits the content, How it handles the complexity, How it manages multiple viewpoints, How it maintains engagement.</instruction>
</instructions>"""

        user_prompt = f"""<content>
    {content[:2000]}...
</content>"""

        return get_completion(system_prompt, user_prompt)

    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise APIError(f"OpenAI API error: {str(e)}") 