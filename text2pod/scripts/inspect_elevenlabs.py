"""Inspect ElevenLabs package structure."""
import sys
import logging
import inspect
from datetime import datetime
from pathlib import Path
import elevenlabs

# Set up logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"elevenlabs_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def inspect_package():
    """Inspect the ElevenLabs package structure."""
    try:
        # Package Info
        logger.info("=== Package Information ===")
        logger.info(f"Package Location: {elevenlabs.__file__}")
        logger.info(f"Version: {elevenlabs.__version__}")
        
        # Module Structure
        logger.info("\n=== Module Structure ===")
        for name, obj in inspect.getmembers(elevenlabs):
            if not name.startswith('_'):  # Skip private attributes
                obj_type = type(obj).__name__
                logger.info(f"{name}: {obj_type}")
                
                # If it's a module, inspect it too
                if obj_type == 'module':
                    logger.info(f"\nSubmodule {name} contains:")
                    for subname, subobj in inspect.getmembers(obj):
                        if not subname.startswith('_'):
                            logger.info(f"  {subname}: {type(subobj).__name__}")

        # Available Functions
        logger.info("\n=== Available Functions ===")
        functions = [name for name, obj in inspect.getmembers(elevenlabs) 
                    if inspect.isfunction(obj)]
        logger.info(f"Functions: {functions}")

        # Available Classes
        logger.info("\n=== Available Classes ===")
        classes = [name for name, obj in inspect.getmembers(elevenlabs) 
                  if inspect.isclass(obj)]
        logger.info(f"Classes: {classes}")

    except Exception as e:
        logger.error(f"Inspection failed: {e}", exc_info=True)

if __name__ == "__main__":
    inspect_package() 