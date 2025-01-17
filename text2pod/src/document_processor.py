"""Document processing module for Text2Pod."""
import logging
from pathlib import Path
from typing import Dict, Optional

import PyPDF2

from .utils.config import INPUT_DIR
from .utils.error_handler import DocumentProcessingError, retry_on_error
from .utils.progress import ProgressTracker

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles the processing of input documents."""
    
    def __init__(self, file_path: str):
        """Initialize the document processor.
        
        Args:
            file_path: Path to the input document
        """
        self.file_path = Path(file_path)
        if not self.file_path.is_absolute():
            self.file_path = INPUT_DIR / self.file_path
            
        if not self.file_path.exists():
            raise DocumentProcessingError(f"File not found: {self.file_path}")
            
        self.file_type = self.file_path.suffix.lower()
        if self.file_type != '.pdf':
            raise DocumentProcessingError(f"Unsupported file type: {self.file_type}")
    
    @retry_on_error()
    def extract_text(self) -> Dict[int, str]:
        """Extract text content from the document.
        
        Returns:
            Dict mapping page numbers to text content
        """
        content = {}
        progress = None
        
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                progress = ProgressTracker(total_pages, "Extracting text")
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Basic cleanup
                    text = self._clean_text(text)
                    
                    if text.strip():  # Only store non-empty pages
                        content[page_num + 1] = text
                    
                    progress.update(1)
                
        except Exception as e:
            raise DocumentProcessingError(f"Error extracting text: {str(e)}")
        
        finally:
            if progress:
                progress.close()
        
        if not content:
            raise DocumentProcessingError("No text content extracted from document")
            
        return content
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text content.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Basic cleaning operations
        text = text.replace('\x00', '')  # Remove null bytes
        text = ' '.join(text.split())    # Normalize whitespace
        
        return text.strip() 