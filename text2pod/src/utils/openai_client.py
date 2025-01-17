"""OpenAI API client utilities."""
import json
import logging
import time
from typing import Dict, List, Optional

from openai import OpenAI

from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL
from src.utils.error_handler import APIError, retry_on_error
from src.utils.token_manager import TokenManager

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)
token_manager = TokenManager()

@retry_on_error()
def get_completion(
    system_prompt: str, 
    user_prompt: str, 
    response_format: str = "text"
) -> str:
    """Get completion from OpenAI API with token management.
    
    Args:
        system_prompt: System role instructions
        user_prompt: User input/request
        response_format: Either "text" or "json_object"
    """
    try:
        logger.info(f"Getting completion with model: {OPENAI_MODEL}")
        
        # Prepare messages with token management
        message_chunks = token_manager.prepare_messages(system_prompt, user_prompt)
        responses = []
        
        for chunk_index, messages in enumerate(message_chunks):
            logger.info(f"Processing chunk {chunk_index + 1}/{len(message_chunks)}")
            
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                response_format={"type": response_format} if response_format == "json_object" else None
            )
            
            token_manager.track_usage(response)
            responses.append(response.choices[0].message.content)
            
        if len(responses) > 1:
            if response_format == "json_object":
                return combine_responses(responses)
            else:
                return "\n\n".join(responses)
        
        return responses[0]

    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise APIError(f"OpenAI API error: {str(e)}")

def combine_responses(responses: List[str]) -> str:
    """Combine multiple JSON responses intelligently."""
    try:
        combined_data = {
            "format": None,
            "reasoning": "",
            "segments": [],
            "technical_terms": [],
            "discussion_points": []
        }
        
        # Parse all responses first
        parsed_responses = []
        for response in responses:
            try:
                data = json.loads(response)
                parsed_responses.append(data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse response: {response[:200]}...")
                continue
        
        if not parsed_responses:
            raise APIError("No valid responses to combine")
        
        # Use first response for base data
        combined_data["format"] = parsed_responses[0].get("format")
        combined_data["reasoning"] = parsed_responses[0].get("reasoning", "")
        
        # Combine lists from all responses
        for data in parsed_responses:
            # Combine segments
            if "segments" in data:
                combined_data["segments"].extend(data["segments"])
            elif "suggested_segments" in data:  # Handle alternate key
                combined_data["segments"].extend(data["suggested_segments"])
                
            # Combine technical terms if present
            if "technical_terms" in data:
                combined_data["technical_terms"].extend(data["technical_terms"])
                
            # Combine discussion points if present
            if "discussion_points" in data:
                combined_data["discussion_points"].extend(data["discussion_points"])
        
        # Remove duplicates while preserving order
        combined_data["segments"] = list(dict.fromkeys(combined_data["segments"]))
        if combined_data["technical_terms"]:
            combined_data["technical_terms"] = list({
                term["term"]: term for term in combined_data["technical_terms"]
            }.values())
        if combined_data["discussion_points"]:
            combined_data["discussion_points"] = list(dict.fromkeys(combined_data["discussion_points"]))
        
        logger.debug(f"Combined response: {json.dumps(combined_data, indent=2)}")
        return json.dumps(combined_data)
        
    except Exception as e:
        logger.error(f"Error combining responses: {str(e)}")
        logger.debug(f"Responses to combine: {responses}")
        raise APIError(f"Error combining responses: {str(e)}")

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