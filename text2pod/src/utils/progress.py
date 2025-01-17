"""Progress tracking utilities."""
import logging
from typing import Optional
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Enhanced progress tracker with better formatting."""
    
    def __init__(self, total: int, desc: str, unit: str = "items"):
        """Initialize progress tracker.
        
        Args:
            total: Total number of items to process
            desc: Description of the operation
            unit: Unit name for items being processed
        """
        self.progress = tqdm(
            total=total,
            desc=desc,
            unit=unit,
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        )
        
    def update(self, n: int = 1):
        """Update progress."""
        self.progress.update(n)
        
    def close(self):
        """Close progress bar."""
        self.progress.close()
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 