"""OpenAI API client utilities."""
import logging
from typing import Dict, List, Optional

import openai
from openai import OpenAI

from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL
from src.utils.error_handler import APIError, retry_on_error

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

@retry_on_error()
def analyze_content(content: str) -> Dict:
    """Analyze content using OpenAI to determine best podcast format."""
    try:
        prompt = f"""Analyze this content and recommend the best podcast format. Consider:
1. Content complexity
2. Number of distinct viewpoints
3. Technical depth
4. Natural conversation flow

Available formats:
- host_expert: Traditional interview with host and subject expert
- two_experts: Dialogue between two experts with different perspectives
- panel: Multiple experts discussing various aspects

Provide your response in JSON format:
{{
    "format": "chosen_format",
    "reasoning": "detailed explanation",
    "suggested_segments": ["topic1", "topic2", ...]
}}

Content to analyze:
{content[:2000]}...
"""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a podcast format analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return response.choices[0].message.content

    except Exception as e:
        raise APIError(f"OpenAI API error: {str(e)}") 