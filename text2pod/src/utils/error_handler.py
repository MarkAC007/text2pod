"""Error handling utilities for Text2Pod."""
import logging
from functools import wraps
import time

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

def retry_on_error(max_retries=3, delay=1):
    """Decorator for retrying operations that may fail."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
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