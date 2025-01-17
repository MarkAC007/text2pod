"""Token management utilities."""
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import tiktoken
from tabulate import tabulate

from src.utils.config import OPENAI_MODEL, MAX_TOKENS
from src.utils.error_handler import TokenError
from src.utils.progress import ProgressTracker

logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Track token usage for a request."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float

class TokenManager:
    """Manages token counting and text chunking for OpenAI API calls."""
    
    PRICING = {
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
        "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002}
    }
    
    # Reserve tokens for system message and response
    SYSTEM_TOKENS_RESERVE = 1000
    RESPONSE_TOKENS_RESERVE = 4000
    
    def __init__(self, model: str = OPENAI_MODEL):
        """Initialize token manager."""
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)
        self.max_tokens = MAX_TOKENS
        self.usage_history: List[TokenUsage] = []
        self.total_cost = 0.0
        
        # Print initial token capacity
        self._print_token_capacity()
        logger.debug(f"Initialized TokenManager for model {model}")
    
    def _print_token_capacity(self):
        """Display token capacity information."""
        capacity_info = [
            ["Total Context Length", f"{self.max_tokens:,}"],
            ["System Reserve", f"{self.SYSTEM_TOKENS_RESERVE:,}"],
            ["Response Reserve", f"{self.RESPONSE_TOKENS_RESERVE:,}"],
            ["Available for Content", f"{int(self.max_tokens * 0.9):,}"],
        ]
        
        print("\n=== Token Capacity ===")
        print(tabulate(capacity_info, tablefmt="grid"))
        print()
    
    def get_max_chunk_tokens(self, system_prompt: str) -> int:
        """Calculate maximum tokens available for content chunks."""
        system_tokens = self.count_tokens(system_prompt)
        available_tokens = (
            self.max_tokens 
            - system_tokens 
            - self.SYSTEM_TOKENS_RESERVE 
            - self.RESPONSE_TOKENS_RESERVE
        ) * 0.9  # Add 10% safety margin
        
        if available_tokens <= 0:
            raise TokenError(
                f"System prompt too long ({system_tokens} tokens). "
                f"Maximum allowed: {self.max_tokens - self.SYSTEM_TOKENS_RESERVE - self.RESPONSE_TOKENS_RESERVE}"
            )
        
        logger.debug(f"Available tokens for content: {int(available_tokens)}")
        return int(available_tokens)

    def chunk_text(self, text: str, max_chunk_tokens: int) -> List[str]:
        """Split text into chunks that fit within token limit."""
        chunks = []
        current_chunk = []
        current_length = 0
        
        # Split into paragraphs first
        paragraphs = text.split('\n\n')
        
        with ProgressTracker(len(paragraphs), "Chunking content", "paragraphs") as progress:
            for paragraph in paragraphs:
                paragraph_tokens = self.count_tokens(paragraph)
                
                if paragraph_tokens > max_chunk_tokens:
                    # If paragraph is too long, split into sentences
                    sentences = paragraph.split('. ')
                    for sentence in sentences:
                        sentence_tokens = self.count_tokens(sentence)
                        
                        if sentence_tokens > max_chunk_tokens:
                            logger.warning(f"Sentence too long ({sentence_tokens} tokens), truncating...")
                            # Split into smaller chunks if needed
                            words = sentence.split()
                            current_sentence = []
                            current_sentence_tokens = 0
                            
                            for word in words:
                                word_tokens = self.count_tokens(word)
                                if current_sentence_tokens + word_tokens <= max_chunk_tokens:
                                    current_sentence.append(word)
                                    current_sentence_tokens += word_tokens
                                else:
                                    if current_sentence:
                                        current_chunk.append(' '.join(current_sentence))
                                        chunks.append('\n\n'.join(current_chunk))
                                        current_chunk = []
                                        current_length = 0
                                        current_sentence = [word]
                                        current_sentence_tokens = word_tokens
                            
                            if current_sentence:
                                current_chunk.append(' '.join(current_sentence))
                        else:
                            if current_length + sentence_tokens <= max_chunk_tokens:
                                current_chunk.append(sentence + '.')
                                current_length += sentence_tokens
                            else:
                                chunks.append('\n\n'.join(current_chunk))
                                current_chunk = [sentence + '.']
                                current_length = sentence_tokens
                else:
                    if current_length + paragraph_tokens <= max_chunk_tokens:
                        current_chunk.append(paragraph)
                        current_length += paragraph_tokens
                    else:
                        chunks.append('\n\n'.join(current_chunk))
                        current_chunk = [paragraph]
                        current_length = paragraph_tokens
                        
                progress.update(1)
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        # Display chunking information
        chunk_info = []
        for i, chunk in enumerate(chunks, 1):
            chunk_tokens = self.count_tokens(chunk)
            chunk_info.append([
                f"Chunk {i}",
                f"{chunk_tokens:,}",
                f"{(chunk_tokens/max_chunk_tokens)*100:.1f}%"
            ])
        
        print("\n=== Content Chunks ===")
        print(tabulate(
            chunk_info,
            headers=["Chunk", "Tokens", "% of Limit"],
            tablefmt="grid"
        ))
        print()
        
        return chunks

    def prepare_messages(self, system_prompt: str, user_content: str) -> List[List[Dict[str, str]]]:
        """Prepare messages for API calls, splitting if necessary."""
        max_chunk_tokens = self.get_max_chunk_tokens(system_prompt)
        content_chunks = self.chunk_text(user_content, max_chunk_tokens)
        
        message_chunks = []
        for chunk in content_chunks:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk}
            ]
            
            # Verify total tokens with extra safety margin
            total_tokens = self.count_messages_tokens(messages)
            if total_tokens > self.max_tokens * 0.95:  # Stay under 95% of limit
                logger.warning(f"Chunk too large ({total_tokens} tokens), reducing...")
                continue
            
            message_chunks.append(messages)
            logger.debug(f"Prepared chunk with {total_tokens} tokens")
        
        if not message_chunks:
            raise TokenError("Failed to create any valid message chunks")
        
        return message_chunks

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for token usage."""
        model_base = self.model.split('-')[0]  # Handle model variants
        pricing = self.PRICING.get(model_base, self.PRICING["gpt-3.5-turbo"])
        
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        
        return prompt_cost + completion_cost
    
    def track_usage(self, response: Any) -> TokenUsage:
        """Track token usage from an API response."""
        usage = response.usage
        usage_data = TokenUsage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            cost=self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)
        )
        
        self.usage_history.append(usage_data)
        self.total_cost += usage_data.cost
        
        # Create usage table for this request
        usage_table = [
            ["Prompt Tokens", f"{usage_data.prompt_tokens:,}"],
            ["Completion Tokens", f"{usage_data.completion_tokens:,}"],
            ["Total Tokens", f"{usage_data.total_tokens:,}"],
            ["Cost", f"${usage_data.cost:.4f}"]
        ]
        
        print("\n=== Request Token Usage ===")
        print(tabulate(usage_table, tablefmt="grid"))
        print()
        
        # Log to file
        logger.info(f"Token usage - Prompt: {usage_data.prompt_tokens}, " +
                   f"Completion: {usage_data.completion_tokens}, " +
                   f"Cost: ${usage_data.cost:.4f}")
        
        return usage_data
    
    def get_usage_report(self) -> Dict:
        """Generate a usage report."""
        total_prompt_tokens = sum(u.prompt_tokens for u in self.usage_history)
        total_completion_tokens = sum(u.completion_tokens for u in self.usage_history)
        total_tokens = sum(u.total_tokens for u in self.usage_history)
        
        return {
            "requests": len(self.usage_history),
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens,
            "total_cost": self.total_cost,
            "average_tokens_per_request": total_tokens / len(self.usage_history) if self.usage_history else 0,
            "model": self.model
        }
    
    def log_usage_report(self):
        """Log a detailed usage report."""
        report = self.get_usage_report()
        
        # Create usage table
        usage_table = [
            ["Model", report['model']],
            ["Total Requests", f"{report['requests']}"],
            ["Total Tokens", f"{report['total_tokens']:,}"],
            ["Prompt Tokens", f"{report['total_prompt_tokens']:,}"],
            ["Completion Tokens", f"{report['total_completion_tokens']:,}"],
            ["Avg Tokens/Request", f"{report['average_tokens_per_request']:,.0f}"],
            ["Total Cost", f"${report['total_cost']:.4f}"]
        ]
        
        print("\n=== Token Usage Report ===")
        print(tabulate(usage_table, tablefmt="grid"))
        print()
        
        # Also log to file
        logger.info("=== Token Usage Report ===")
        for row in usage_table:
            logger.info(f"{row[0]}: {row[1]}")
        logger.info("=======================")
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in a message list for chat completion."""
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # Every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))
                if key == "name":  # If there's a name, the role is omitted
                    num_tokens += -1  # Role is always required and always 1 token
        num_tokens += 2  # Every reply is primed with <im_start>assistant
        return num_tokens 
    
    def estimate_cost(self, text: str) -> float:
        """Estimate cost for processing text."""
        text_tokens = self.count_tokens(text)
        # Estimate completion tokens as 10% of input tokens
        estimated_completion_tokens = int(text_tokens * 0.1)
        
        return self.calculate_cost(text_tokens, estimated_completion_tokens) 