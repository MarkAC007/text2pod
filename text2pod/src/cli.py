"""Command-line interface for Text2Pod."""
import argparse
import json
import logging
import sys
from pathlib import Path

from src.document_processor import DocumentProcessor
from src.script_generator import ScriptGenerator
from src.utils.config import INPUT_DIR, OUTPUT_DIR
from src.utils.error_handler import Text2PodError, UserCancelled
from src.utils.interactive import confirm_step

logger = logging.getLogger(__name__)

def process_input_directory(interactive: bool = False):
    """Process all PDF files in the input directory.
    
    Args:
        interactive: Whether to run in interactive mode
    """
    if not INPUT_DIR.exists():
        logger.error(f"Input directory not found: {INPUT_DIR}")
        sys.exit(1)
        
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    
    if not pdf_files:
        logger.error(f"No PDF files found in {INPUT_DIR}")
        sys.exit(1)
        
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    if interactive and len(pdf_files) > 1:
        print(f"\nFound {len(pdf_files)} PDF files:")
        for i, pdf in enumerate(pdf_files, 1):
            print(f"{i}. {pdf.name} ({pdf.stat().st_size / 1024:.1f} KB)")
        if not confirm_step("Process all files?"):
            logger.info("Operation cancelled by user")
            return
    
    for pdf_file in pdf_files:
        try:
            # Process document
            logger.info(f"Processing: {pdf_file.name}")
            logger.info(f"File size: {pdf_file.stat().st_size / 1024:.2f} KB")
            
            processor = DocumentProcessor(pdf_file, interactive=interactive)
            result = processor.process_document()
            
            # Save markdown
            markdown_file = OUTPUT_DIR / f"{pdf_file.stem}_content.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(result['markdown'])
            logger.info(f"Markdown content saved to: {markdown_file}")
            
            if interactive and not confirm_step(f"Save analysis for {pdf_file.name}?"):
                continue
                
            # Save analysis
            analysis_file = OUTPUT_DIR / f"{pdf_file.stem}_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(result['analysis'], f, indent=2, ensure_ascii=False)
            logger.info(f"Content analysis saved to: {analysis_file}")
            
        except UserCancelled as e:
            logger.info(f"Processing cancelled for {pdf_file.name}: {str(e)}")
            if interactive and not confirm_step("Continue with next file?", default=False):
                logger.info("Stopping processing")
                break
        except Text2PodError as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")
            if interactive and not confirm_step("Continue with next file?", default=False):
                logger.info("Stopping processing")
                break
        except Exception as e:
            logger.exception(f"Unexpected error processing {pdf_file.name}")
            if interactive and not confirm_step("Continue with next file?", default=False):
                logger.info("Stopping processing")
                break

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Convert documents to podcast-style audio")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--format", choices=["host_expert", "two_experts", "panel"],
                       help="Override script format")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Enable interactive mode with confirmations")
    
    args = parser.parse_args()
    
    # Configure logging with more detailed format
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('text2pod.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Starting Text2Pod processing")
    logger.debug(f"Debug mode: {args.debug}")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    try:
        process_input_directory(interactive=args.interactive)
        logger.info("Processing complete")
        
        # Log final usage report
        from src.utils.openai_client import token_manager
        token_manager.log_usage_report()
        
    except Exception as e:
        logger.exception("Fatal error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main() 