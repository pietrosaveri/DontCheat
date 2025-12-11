import subprocess
import os
import sys

# Global variable to track the current overlay process
current_overlay_process = None

def show_notification(message, duration=None):
    """
    Show a discreet notification overlay at bottom-center of screen.
    Designed to be hard to spot from a distance (stealth mode).
    
    Args:
        message: The message to display
        duration: Ignored (kept for compatibility), window stays open until closed.
    """
    global current_overlay_process
    
    try:
        # Kill existing overlay if running
        if current_overlay_process is not None:
            if current_overlay_process.poll() is None: # Still running
                try:
                    current_overlay_process.terminate()
                    # Give it a moment to close gracefully
                    try:
                        current_overlay_process.wait(timeout=0.2)
                    except subprocess.TimeoutExpired:
                        current_overlay_process.kill()
                except Exception:
                    pass
        
        # Path to the overlay script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        overlay_script = os.path.join(current_dir, 'overlay.py')
        
        # Run the overlay script in a separate process
        # We use sys.executable to ensure we use the same python interpreter
        current_overlay_process = subprocess.Popen(
            [sys.executable, overlay_script, message],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
    except Exception as e:
        print(f"Error showing notification: {e}")