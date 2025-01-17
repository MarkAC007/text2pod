"""Command-line interface for Text2Pod."""
import argparse
import json
import logging
import sys
from pathlib import Path

from src.document_processor import DocumentProcessor
from src.script_generator import ScriptGenerator
from src.utils.config import INPUT_DIR, OUTPUT_DIR
from src.utils.error_handler import Text2PodError

logger = logging.getLogger(__name__)

def process_input_directory():
    """Process all PDF files in the input directory."""
    if not INPUT_DIR.exists():
        logger.error(f"Input directory not found: {INPUT_DIR}")
        sys.exit(1)
        
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    
    if not pdf_files:
        logger.error(f"No PDF files found in {INPUT_DIR}")
        sys.exit(1)
        
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        try:
            # Process document
            logger.info(f"Processing: {pdf_file.name}")
            processor = DocumentProcessor(pdf_file)
            content = processor.extract_text()
            print(f"Successfully processed {pdf_file.name}: {len(content)} pages")
            
            # Generate script
            logger.info("Generating script...")
            generator = ScriptGenerator(content)
            script = generator.generate_script()
            
            # Save script
            output_file = OUTPUT_DIR / f"{pdf_file.stem}_script.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(script, f, indent=2, ensure_ascii=False)
            print(f"Script generated: {output_file}")
            
        except Text2PodError as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error processing {pdf_file.name}")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Convert documents to podcast-style audio")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--format", choices=["host_expert", "two_experts", "panel"],
                       help="Override script format")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    try:
        process_input_directory()
    except Exception as e:
        logger.exception("Fatal error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main() 