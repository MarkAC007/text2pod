"""Manual test script for voice processing."""
from pathlib import Path
from src.voice_processor import VoiceProcessor

def main():
    """Run manual voice processing test."""
    # Path to your analysis file
    analysis_file = Path("output/your_analysis.json")
    
    # Initialize processor
    processor = VoiceProcessor(analysis_file, use_ssml=True)
    
    # Generate script
    try:
        # Format different parts
        intro = processor._format_intro()
        print("\n=== INTRO ===")
        print(intro)
        
        # Get first segment
        if processor.analysis['segments']:
            segment = processor._format_segment(1, processor.analysis['segments'][0])
            print("\n=== FIRST SEGMENT ===")
            print(segment)
        
        outro = processor._format_outro()
        print("\n=== OUTRO ===")
        print(outro)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 