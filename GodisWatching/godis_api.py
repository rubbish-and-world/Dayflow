import os
import io
import subprocess
from typing import Optional

import mss
from PIL import Image

from dotenv import load_dotenv

# Optional imports for model backends.
try:
    from google import genai
except ImportError:
    genai = None

try:
    from ollama import Client as OllamaClient
except ImportError:
    OllamaClient = None


def load_environment(env_path: str = ".env") -> None:
    load_dotenv(env_path)


def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise EnvironmentError("GEMINI_API_KEY not found in environment")
    return key


def get_gemini_client(api_key: Optional[str] = None):
    if genai is None:
        raise ImportError("genai library is not installed")

    key = api_key or get_gemini_api_key()
    os.environ["GEMINI_API_KEY"] = key
    return genai.Client()


def capture_screen() -> Image.Image:
    """Captures the primary monitor, optimizes it, and returns a PIL Image."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # 1. Convert raw pixels to a PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # 2. OPTIMIZATION: Shrink the image to a maximum of 1080p
        # This prevents the Nginx 413 error and drastically speeds up the network transfer.
        # thumbnail() maintains the aspect ratio automatically.
        img.thumbnail((1920, 1080))
        
        return img


def analyze_image_gemini(img: Image.Image, client=None, prompt: Optional[str] = None) -> str:
    """Send an image + prompt to Gemini and get a normalized YES/NO string response."""
    if client is None:
        client = get_gemini_client()

    if prompt is None:
        prompt = (
            "You are a strict productivity monitor. Analyze this screenshot of a computer screen. "
            "Is the primary content of this screen showing entertainment content (like YouTube vlogs, gaming videos, movies) "
            "OR erotic/NSFW anime? Ignore standard UI elements, text editors, code, or academic papers. "
            "Respond strictly with a single word: YES or NO."
        )

    response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt, img])
    text = str(response.text).strip().upper()
    if "YES" in text:
        return "YES"
    return "NO"


def analyze_image_ollama(image_bytes: bytes, model: str, server_ip: str, api_key: str, prompt: str) -> str:
    """Send an image byte payload to Ollama and return plain response text."""
    if OllamaClient is None:
        raise ImportError("ollama library is not installed")

    client = OllamaClient(host=server_ip, headers={"Authorization": f"Bearer {api_key}"})
    response = client.generate(model=model, prompt=prompt, images=[image_bytes])
    if isinstance(response, dict):
        return str(response.get("response", "")).strip()
    if hasattr(response, "response"):
        return str(response.response).strip()
    return str(response).strip()


def trigger_system_notification(title: str, message: str, sound_name: str = "Basso") -> None:
    applescript = f'display notification "{message}" with title "{title}" sound name "{sound_name}"'
    subprocess.run(["osascript", "-e", applescript])


import subprocess
import tkinter as tk
import os

def trigger_fullscreen_warning(message: str = "Distraction detected. Close the video and get back to work immediately.") -> None:
    """Displays an aggressive, massive tkinter alert with an audio prompt."""
    
    # 1. Trigger the audio
    subprocess.Popen(["say", message])

    root = tk.Tk()
    root.title("WARNING")
    
    # --- NEW: Big Centered Window instead of Fullscreen ---
    window_width = 1200
    window_height = 800
    
    # Get your Mac's screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate the exact center coordinates
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)
    
    # Apply the size and position
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    # -------------------------------------------------------

    # Keep it strictly above all other apps
    root.attributes("-topmost", True)
    root.configure(bg="#b30000")
    
    # Keep the macOS focus tricks to ensure clicks register
    root.after(1, lambda: root.focus_force())
    subprocess.run(["osascript", "-e", f'tell application "System Events" to set frontmost of the first process whose unix id is {os.getpid()} to true'])

    def close_alert(event=None):
        """Forces the mainloop to stop AND destroys the window."""
        root.quit()    
        root.destroy() 

    # Bindings for keyboard escape hatches
    root.bind("<Escape>", close_alert)
    root.bind("<Return>", close_alert)

    warning_label = tk.Label(
        root,
        text=f"🚨 DISTRACTION DETECTED 🚨\n\n{message.upper()}",
        font=("Helvetica", 60, "bold"),
        bg="#b30000",
        fg="white",
        wraplength=1000 
    )
    warning_label.pack(expand=True)

    close_button = tk.Button(
        root,
        text="I am closing the video now",
        font=("Helvetica", 30),
        highlightbackground="#b30000",
        command=close_alert
    )
    close_button.pack(pady=100)

    # MacOS Hack: Explicitly bind the Left Mouse Click
    close_button.bind("<Button-1>", close_alert)

    root.mainloop()
