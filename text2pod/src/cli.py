"""Command-line interface for Text2Pod."""
import argparse
import logging
import sys
from pathlib import Path

from .document_processor import DocumentProcessor
from .utils.error_handler import Text2PodError

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Convert documents to podcast-style audio")
    parser.add_argument("input_file", help="Path to input document (PDF)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    
    try:
        # Process document
        processor = DocumentProcessor(args.input_file)
        content = processor.extract_text()
        
        # For testing, just print the number of pages processed
        print(f"Successfully processed {len(content)} pages")
        
    except Text2PodError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main() 