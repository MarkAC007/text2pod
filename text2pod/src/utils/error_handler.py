"""Error handling utilities for Text2Pod."""
import logging
from functools import wraps
import time
from typing import Callable, Type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('text2pod.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def retry_on_error(
    max_retries: int = 3,
    delay: int = 1,
    exceptions: tuple = (Exception,)
) -> Callable:
    """Decorator to retry a function on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. Retrying..."
                    )
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class Text2PodError(Exception):
    """Base exception class for Text2Pod."""
    pass

class DocumentProcessingError(Text2PodError):
    """Raised when there's an error processing input documents."""
    pass

class APIError(Text2PodError):
    """Raised when there's an error with API calls."""
    pass

class ContentAnalysisError(Text2PodError):
    """Raised when there's an error analyzing document content."""
    pass

class TokenError(Text2PodError):
    """Raised when there's an error with token management."""
    pass

class UserCancelled(Text2PodError):
    """Raised when user cancels an operation."""
    pass

class VoiceProcessingError(Text2PodError):
    """Raised when there's an error with voice processing."""
    pass 