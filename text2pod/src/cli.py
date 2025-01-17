"""Command-line interface for Text2Pod."""
import argparse
import json
import logging
import sys
from pathlib import Path

from document_processor import DocumentProcessor
from script_generator import ScriptGenerator
from podcast_generator import PodcastGenerator
from utils.config import INPUT_DIR, OUTPUT_DIR
from utils.error_handler import Text2PodError, UserCancelled
from utils.interactive import confirm_step

logger = logging.getLogger(__name__)

def process_input_directory(interactive: bool = False):
    """Process all PDF files in the input directory."""
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

def generate_podcast(json_path: Path, interactive: bool = False, cleanup: bool = False):
    """Generate podcast from JSON specification."""
    try:
        logger.info(f"Generating podcast from: {json_path}")
        
        # Initialize generator
        generator = PodcastGenerator(
            output_dir=OUTPUT_DIR / "podcasts",
            cleanup_segments=cleanup
        )
        
        # Test connections
        logger.info("Testing service connections...")
        status = generator.test_connections()
        
        if "error" in status:
            logger.error(f"Connection test failed: {status['error']}")
            return
            
        if not status["voice_service"]:
            logger.error("Voice service connection failed")
            return
            
        if not status["output_directory"]:
            logger.error("Cannot write to output directory")
            return
            
        logger.info("Service connections verified")
        
        # Generate podcast
        project_name = json_path.stem
        if interactive:
            custom_name = input(f"Enter project name [{project_name}]: ").strip()
            if custom_name:
                project_name = custom_name
        
        podcast_file, metadata = generator.generate_podcast(
            json_path=json_path,
            project_name=project_name
        )
        
        # Save metadata
        metadata_file = podcast_file.parent / f"{project_name}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Generated podcast: {podcast_file}")
        logger.info(f"Metadata saved to: {metadata_file}")
        
        # Print summary
        print("\nPodcast Generation Summary:")
        print(f"Title: {metadata['title']}")
        print(f"Format: {metadata['format']}")
        print(f"Technical Level: {metadata['technical_level']}")
        print(f"Duration: {metadata['duration']}")
        print(f"Segments: {metadata['segments']}")
        print(f"Technical Terms: {metadata['technical_terms']}")
        print(f"\nOutput: {metadata['output_file']}")
        
    except Exception as e:
        logger.error(f"Failed to generate podcast: {e}")
        if interactive:
            logger.debug("Error details:", exc_info=True)

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Convert documents to podcast-style audio")
    
    # Keep existing arguments
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--format", choices=["host_expert", "two_experts", "panel"],
                       help="Override script format")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Enable interactive mode with confirmations")
    
    # Add podcast generation arguments
    parser.add_argument("--podcast", type=Path,
                       help="Generate podcast from JSON file")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up individual audio segments after merging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('text2pod.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Starting Text2Pod")
    logger.debug(f"Arguments: {args}")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    try:
        if args.podcast:
            # Generate podcast from JSON
            generate_podcast(
                json_path=args.podcast,
                interactive=args.interactive,
                cleanup=args.cleanup
            )
        else:
            # Run existing document processing
            process_input_directory(interactive=args.interactive)
            
            # Log final usage report
            from utils.openai_client import token_manager
            token_manager.log_usage_report()
        
        logger.info("Processing complete")
        
    except Exception as e:
        logger.exception("Fatal error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main() 