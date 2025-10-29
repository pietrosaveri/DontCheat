import threading
import time
import os
from pynput import mouse
from handlers.screenshot_handler import capture_screenshot
from handlers.notification_handler import show_notification

# Import both handlers
import handlers.groq_handler as groq_handler
import handlers.gemini_handler as gemini_handler

# Choose which AI provider to use: 'groq' or 'gemini'
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'groq').lower()

class ClickDetector:
    def __init__(self, click_threshold=0.3, num_clicks=3):
        """
        Initialize the click detector.
        
        Args:
            click_threshold: Maximum time between clicks (seconds)
            num_clicks: Number of clicks to detect
        """
        self.click_threshold = click_threshold
        self.num_clicks = num_clicks
        self.click_times = []
        self.processing = False
        
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not pressed:  # Only count click releases
            return
            
        current_time = time.time()
        self.click_times.append(current_time)
        
        # Keep only recent clicks
        self.click_times = [t for t in self.click_times 
                           if current_time - t <= self.click_threshold]
        
        # Check if we have enough clicks
        if len(self.click_times) >= self.num_clicks:
            if not self.processing:
                self.processing = True
                self.click_times = []
                # Process in a separate thread to avoid blocking
                threading.Thread(target=self.process_screenshot, daemon=True).start()
    
    def process_screenshot(self):
        """Capture screenshot and process with AI."""
        try:
            print("Triple-click detected! Capturing screenshot...")
            
            # Capture screenshot
            screenshot_path = capture_screenshot()
            if not screenshot_path:
                print("Failed to capture screenshot")
                self.processing = False
                return
            
            print(f"Screenshot saved: {screenshot_path}")
            
            # Analyze with selected AI provider
            if AI_PROVIDER == 'gemini':
                print("Analyzing with Gemini VLM...")
                answer = gemini_handler.analyze_screenshot(screenshot_path)
            else:
                print("Analyzing with Groq VLM...")
                answer = groq_handler.analyze_screenshot(screenshot_path)
            
            if answer:
                print(f"Answer received: {answer[:100]}...")
                # Show notification with answer
                show_notification(answer)
            else:
                print("No answer received from AI")
            
            # Clean up screenshot
            try:
                os.remove(screenshot_path)
            except:
                pass
                
        except Exception as e:
            print(f"Error processing screenshot: {e}")
        finally:
            self.processing = False
    
    def start(self):
        """Start listening for clicks."""
        print("CheatMe is running...")
        print("Triple-click your trackpad to capture and analyze.")
        print("Press Ctrl+C to exit.")
        
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

def main():
    detector = ClickDetector(click_threshold=0.3, num_clicks=3)
    try:
        detector.start()
    except KeyboardInterrupt:
        print("\nCheatMe stopped.")

if __name__ == "__main__":
    main()
