"""Progress tracking utilities for Text2Pod."""
from tqdm import tqdm

class ProgressTracker:
    """Manages progress bars and status updates for long-running processes."""
    
    def __init__(self, total_steps, description="Processing"):
        self.progress_bar = tqdm(total=total_steps, desc=description)
        
    def update(self, steps=1, status=None):
        """Update progress and optionally display a status message."""
        self.progress_bar.update(steps)
        if status:
            self.progress_bar.set_description(status)
            
    def close(self):
        """Close the progress bar."""
        self.progress_bar.close() 