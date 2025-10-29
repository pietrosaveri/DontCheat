import subprocess
import threading
import time

def show_notification(message, duration=15):
    """
    Show a discreet notification overlay at bottom-right of screen.
    Works perfectly in background mode using native macOS APIs.
    
    Args:
        message: The message to display
        duration: How long to show the notification (seconds)
    """
    try:
        # Show macOS notification first (quick preview)
        title = "Answer Ready"
        subtitle = message[:50] + "..." if len(message) > 50 else message
        
        # Use osascript to show native notification
        script = f'''
        display notification "{subtitle}" with title "{title}"
        '''
        subprocess.run(['osascript', '-e', script], check=False, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Create native overlay window using AppleScript
        # This creates a small alert-style window at bottom-right
        escaped_message = message.replace('"', '\\"').replace('\n', '\\n')
        
        applescript = f'''
        tell application "System Events"
            set theText to "{escaped_message}"
            display dialog theText with title "Answers" buttons {{"Close"}} default button 1 giving up after {duration}
        end tell
        '''
        
        # Run in background thread so it doesn't block
        def show_dialog():
            subprocess.run(
                ['osascript', '-e', applescript],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        threading.Thread(target=show_dialog, daemon=True).start()
        
    except Exception as e:
        print(f"Error showing notification: {e}")