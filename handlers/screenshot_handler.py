import os
import time
from datetime import datetime
import mss

def capture_screenshot():
    """
    Capture a silent screenshot of the entire screen.
    
    Returns:
        str: Path to the saved screenshot, or None if failed
    """
    try:
        # Create screenshots directory if it doesn't exist
        screenshots_dir = os.path.join(os.path.dirname(__file__), '.screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screen_{timestamp}.png'
        filepath = os.path.join(screenshots_dir, filename)
        
        # Capture screenshot using mss (silent, no shutter sound)
        with mss.mss() as sct:
            # Capture the primary monitor
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            # Save to file
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
        
        return filepath
        
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None
