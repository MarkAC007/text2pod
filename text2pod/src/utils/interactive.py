"""Interactive prompt utilities."""
import sys
from typing import Optional

def confirm_step(message: str, default: bool = True) -> bool:
    """Ask user for confirmation to proceed.
    
    Args:
        message: The message to display
        default: Default response if user just hits enter
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    
    if default:
        prompt = " [Y/n] "
    else:
        prompt = " [y/N] "
        
    while True:
        print(f"\n{message}{prompt}", end="")
        choice = input().lower()
        
        if choice == "":
            return default
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').")

def display_cost_warning(estimated_cost: float) -> bool:
    """Display cost warning and get confirmation.
    
    Args:
        estimated_cost: Estimated cost in dollars
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    print("\n=== Cost Warning ===")
    print(f"Estimated cost for this operation: ${estimated_cost:.4f}")
    print("Note: This is an estimate based on token counts.")
    return confirm_step("Do you want to proceed?") 