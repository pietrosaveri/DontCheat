import tkinter as tk
import sys

def show_overlay(message):
    try:
        root = tk.Tk()
        
        # Style configuration
        # Dark theme that blends with bezels/dark mode
        bg_color = "#000000"    # Pure black
        fg_color = "#444444"    # Dark gray text (stealth default)
        hover_fg_color = "#AAAAAA" # Lighter gray on hover (readable)
        font_style = ("Arial", 10) # Small font
        
        # Setup main frame
        frame = tk.Frame(root, bg=bg_color)
        frame.pack(fill="both", expand=True)

        # Setup label for text
        label = tk.Label(
            frame, 
            text=message, 
            font=font_style, 
            bg=bg_color, 
            fg=fg_color,
            wraplength=800,     # Allow wide text
            justify="center",
            padx=10,
            pady=4,
            cursor="hand2" # Indicate clickable
        )
        label.pack(side="left", fill="both", expand=True)
        
        # Setup close button
        close_btn = tk.Label(
            frame,
            text="×",
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg=fg_color,
            padx=8,
            cursor="hand2"
        )
        close_btn.pack(side="right", fill="y")
        
        # Functionality
        def copy_to_clipboard(event):
            root.clipboard_clear()
            root.clipboard_append(message)
            root.update() # Required for clipboard to work
            
            # Visual feedback
            original_text = label.cget("text")
            label.config(text="Copied!", fg="#00FF00")
            root.after(1000, lambda: label.config(text=original_text, fg=hover_fg_color))

        def close_window(event):
            root.destroy()

        def on_enter(event):
            # Make text readable and window opaque on hover
            label.config(fg=hover_fg_color)
            close_btn.config(fg=hover_fg_color)
            root.attributes("-alpha", 1.0)

        def on_leave(event):
            # Return to stealth mode
            label.config(fg=fg_color)
            close_btn.config(fg=fg_color)
            root.attributes("-alpha", 0.8)

        # Bindings
        label.bind("<Button-1>", copy_to_clipboard)
        close_btn.bind("<Button-1>", close_window)
        
        # Bind hover events to the root window so it triggers anywhere in the window
        root.bind("<Enter>", on_enter)
        root.bind("<Leave>", on_leave)
        
        # Calculate position
        root.update_idletasks()
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Bottom center, very close to edge (2px from bottom)
        x = (screen_width - width) // 2
        y = screen_height - height - 2
        
        # Window configuration
        root.overrideredirect(True)  # Frameless
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.configure(bg=bg_color)
        
        # Ensure window is ready before setting attributes
        root.update()
        
        root.attributes("-topmost", True) # Always on top
        root.attributes("-alpha", 0.8)    # Slight transparency default
        
        # Force window to stay on top (fix for macOS full-screen apps)
        def keep_on_top():
            root.lift()
            root.attributes("-topmost", True)
            root.after(1000, keep_on_top)
            
        keep_on_top()
        
        # Bring to front
        root.lift()
        
        root.mainloop()
    except Exception as e:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = sys.argv[1]
        show_overlay(message)
