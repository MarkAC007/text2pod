"""Document processing module for Text2Pod."""
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import PyPDF2

from src.utils.config import INPUT_DIR
from src.utils.error_handler import DocumentProcessingError, retry_on_error
from src.utils.progress import ProgressTracker
from src.utils.content_analyzer import format_to_markdown, analyze_markdown_content
from src.utils.interactive import confirm_step, display_cost_warning
from src.utils.openai_client import token_manager

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles the processing of input documents."""
    
    def __init__(self, file_path: Path, interactive: bool = False):
        """Initialize the document processor."""
        self.file_path = file_path if isinstance(file_path, Path) else Path(file_path)
        self.interactive = interactive
            
        if not self.file_path.exists():
            raise DocumentProcessingError(f"File not found: {self.file_path}")
            
        self.file_type = self.file_path.suffix.lower()
        if self.file_type != '.pdf':
            raise DocumentProcessingError(f"Unsupported file type: {self.file_type}")
    
    def extract_raw_text(self) -> str:
        """Extract raw text content from the document."""
        content = []
        
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                with ProgressTracker(total_pages, "Extracting text", "pages") as progress:
                    for page_num in range(total_pages):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if text.strip():  # Only include non-empty pages
                            content.append(text)
                        
                        progress.update(1)
            
            return "\n\n".join(content)
            
        except Exception as e:
            raise DocumentProcessingError(f"Error extracting text: {str(e)}")
    
    @retry_on_error()
    def process_document(self) -> Dict:
        """Process document through the enhanced pipeline."""
        try:
            total_steps = 3
            with ProgressTracker(total_steps, "Processing document", "steps") as progress:
                # Step 1: Extract raw text
                raw_text = self.extract_raw_text()
                progress.update(1)
                
                # Step 2: Convert to clean markdown
                markdown_text = format_to_markdown(raw_text)
                progress.update(1)
                
                # Step 3: Analyze content
                analysis = analyze_markdown_content(markdown_text)
                progress.update(1)
                
                return {
                    'markdown': markdown_text,
                    'analysis': analysis
                }
                
        except Exception as e:
            raise DocumentProcessingError(f"Error processing document: {str(e)}") 