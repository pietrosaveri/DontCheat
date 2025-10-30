import threading
import time
import os
from pynput import mouse, keyboard
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
        self.reference_image_path = None  # Store reference image for context
        
        # Track keyboard modifiers
        self.option_pressed = False
        self.control_pressed = False
        
    def on_key_press(self, key):
        """Track keyboard modifier keys."""
        try:
            if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.option_pressed = True
            elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.control_pressed = True
        except:
            pass
    
    def on_key_release(self, key):
        """Track keyboard modifier keys release."""
        try:
            if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.option_pressed = False
            elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.control_pressed = False
        except:
            pass
    
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
                clicks_copy = self.click_times.copy()
                self.click_times = []
                
                # Determine action based on modifiers
                if self.option_pressed:
                    # Option + 3 clicks: Save reference image
                    threading.Thread(target=self.save_reference_screenshot, daemon=True).start()
                elif self.control_pressed:
                    # Control + 3 clicks: Analyze with reference
                    threading.Thread(target=self.process_with_reference, daemon=True).start()
                else:
                    # Normal 3 clicks: Immediate analysis
                    threading.Thread(target=self.process_screenshot, daemon=True).start()
    
    def save_reference_screenshot(self):
        """Capture and save reference screenshot for future use."""
        try:
            print("Option + Triple-click detected! Saving reference image...")
            
            # Remove old reference if exists
            if self.reference_image_path and os.path.exists(self.reference_image_path):
                try:
                    os.remove(self.reference_image_path)
                except:
                    pass
            
            # Capture new reference screenshot
            screenshot_path = capture_screenshot()
            if not screenshot_path:
                print("Failed to capture reference screenshot")
                self.processing = False
                return
            
            # Store reference path (don't delete this one)
            self.reference_image_path = screenshot_path
            print(f"Reference image saved: {screenshot_path}")
            show_notification("Reference context saved!")
            
        except Exception as e:
            print(f"Error saving reference screenshot: {e}")
        finally:
            self.processing = False
    
    def process_with_reference(self):
        """Capture screenshot and analyze with reference context."""
        try:
            if not self.reference_image_path or not os.path.exists(self.reference_image_path):
                print("No reference image available! Use Option+3-tap first.")
                show_notification("⚠ No reference context!\nUse Option+3-tap to save reference text first.")
                self.processing = False
                return
            
            print("Control + Triple-click detected! Analyzing with reference context...")
            
            # Capture current question screenshot
            screenshot_path = capture_screenshot()
            if not screenshot_path:
                print("Failed to capture screenshot")
                self.processing = False
                return
            
            print(f"Question screenshot: {screenshot_path}")
            print(f"Using reference: {self.reference_image_path}")
            
            # Analyze with selected AI provider (with reference)
            if AI_PROVIDER == 'gemini':
                print("Analyzing with Gemini VLM (with reference)...")
                answer = gemini_handler.analyze_screenshot(screenshot_path, self.reference_image_path)
            else:
                print("Analyzing with Groq VLM (with reference)...")
                answer = groq_handler.analyze_screenshot(screenshot_path, self.reference_image_path)
            
            if answer:
                print(f"Answer received: {answer[:100]}...")
                show_notification(answer)
            else:
                print("No answer received from AI")
            
            # Clean up question screenshot (keep reference)
            try:
                os.remove(screenshot_path)
            except:
                pass
                
        except Exception as e:
            print(f"Error processing with reference: {e}")
        finally:
            self.processing = False
    
    def process_screenshot(self):
        """Capture screenshot and process with AI (immediate analysis)."""
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
        """Start listening for clicks and keyboard."""
        print("CheatMe is running...")
        print("Gestures:")
        print("  • 3-tap: Instant analysis")
        print("  • Option + 3-tap: Save reference context")
        print("  • Control + 3-tap: Analyze with saved context")
        print("Press Ctrl+C to exit.")
        
        # Start keyboard listener
        keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        keyboard_listener.start()
        
        # Start mouse listener (blocking)
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
