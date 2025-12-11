import threading
import time
import os
from pynput import mouse, keyboard
from handlers.screenshot_handler import capture_screenshot
from handlers.notification_handler import show_notification

# Import handlers
import handlers.groq_handler as groq_handler
import handlers.gemini_handler as gemini_handler
import handlers.lm_studio_handler as lm_studio_handler

# Choose which AI provider to use: 'groq', 'gemini', or 'lm_studio'
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
        self.cmd_pressed = False
        self.shift_pressed = False
        
        # Track drag for area selection
        self.drag_start = None
        
    def on_key_press(self, key):
        """Track keyboard modifier keys."""
        try:
            if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.option_pressed = True
            elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.control_pressed = True
            elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                self.cmd_pressed = True
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.shift_pressed = True
        except:
            pass
    
    def on_key_release(self, key):
        """Track keyboard modifier keys release."""
        try:
            if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.option_pressed = False
            elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.control_pressed = False
            elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                self.cmd_pressed = False
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.shift_pressed = False
        except:
            pass
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        # Handle drag selection (Cmd + Shift + Drag)
        if self.cmd_pressed and self.shift_pressed:
            if pressed:
                self.drag_start = (x, y)
                return
            elif self.drag_start:
                # Drag released
                start_x, start_y = self.drag_start
                self.drag_start = None
                
                # Calculate region
                width = abs(x - start_x)
                height = abs(y - start_y)
                left = min(start_x, x)
                top = min(start_y, y)
                
                # Ignore tiny drags (accidental clicks)
                if width > 10 and height > 10:
                    region = (int(left), int(top), int(width), int(height))
                    
                    if not self.processing:
                        self.processing = True
                        if self.option_pressed:
                            # Cmd+Shift+Option+Drag: Save reference
                            threading.Thread(target=self.save_reference_screenshot, args=(region,), daemon=True).start()
                        elif self.control_pressed:
                            # Cmd+Shift+Control+Drag: Analyze with reference
                            threading.Thread(target=self.process_with_reference, args=(region,), daemon=True).start()
                        else:
                            # Cmd+Shift+Drag: Instant analysis
                            threading.Thread(target=self.process_screenshot, args=(region,), daemon=True).start()
                return

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
    
    def save_reference_screenshot(self, region=None):
        """Capture and save reference screenshot for future use."""
        try:
            action_type = "Area selection" if region else "Option + Triple-click"
            print(f"{action_type} detected! Saving reference image...")
            
            # Remove old reference if exists
            if self.reference_image_path and os.path.exists(self.reference_image_path):
                try:
                    os.remove(self.reference_image_path)
                except:
                    pass
            
            # Capture new reference screenshot
            screenshot_path = capture_screenshot(region)
            if not screenshot_path:
                print("Failed to capture reference screenshot")
                self.processing = False
                return
                return
            
            # Store reference path (don't delete this one)
            self.reference_image_path = screenshot_path
            print(f"Reference image saved: {screenshot_path}")
            show_notification("Reference context saved!")
            
        except Exception as e:
            print(f"Error saving reference screenshot: {e}")
        finally:
            self.processing = False
    
    def process_with_reference(self, region=None):
        """Capture screenshot and analyze with reference context."""
        try:
            if not self.reference_image_path or not os.path.exists(self.reference_image_path):
                print("No reference image available! Use Option+3-tap first.")
                show_notification("⚠ No reference context!\nUse Option+3-tap to save reference text first.")
                self.processing = False
                return
            
            action_type = "Area selection" if region else "Control + Triple-click"
            print(f"{action_type} detected! Analyzing with reference context...")
            
            # Capture current question screenshot
            screenshot_path = capture_screenshot(region)
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
            elif AI_PROVIDER == 'lm_studio':
                print("Analyzing with LM Studio (with reference)...")
                answer = lm_studio_handler.analyze_screenshot(screenshot_path, self.reference_image_path)
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
    
    def process_screenshot(self, region=None):
        """Capture screenshot and process with AI (immediate analysis)."""
        try:
            action_type = "Area selection" if region else "Triple-click"
            print(f"{action_type} detected! Capturing screenshot...")
            
            # Capture screenshot
            screenshot_path = capture_screenshot(region)
            if not screenshot_path:
                print("Failed to capture screenshot")
                self.processing = False
                return
            
            print(f"Screenshot saved: {screenshot_path}")
            
            # Analyze with selected AI provider
            if AI_PROVIDER == 'gemini':
                print("Analyzing with Gemini VLM...")
                answer = gemini_handler.analyze_screenshot(screenshot_path)
            elif AI_PROVIDER == 'lm_studio':
                print("Analyzing with LM Studio...")
                answer = lm_studio_handler.analyze_screenshot(screenshot_path)
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
        print("  • Cmd + Shift + Drag: Instant analysis (Area)")
        print("  • Cmd + Shift + Option + Drag: Save reference context (Area)")
        print("  • Cmd + Shift + Control + Drag: Analyze with saved context (Area)")
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
