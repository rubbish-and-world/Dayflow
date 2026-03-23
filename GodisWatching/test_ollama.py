import time
import io
import mss
from PIL import Image

from godis_api import analyze_image_ollama

# --- CONFIGURATION ---
SERVER_IP = "http://10.166.38.250:19122"
MODEL = "qwen3-vl:4b"
API_KEY = ""


def run_test():
    print(f"[*] Capturing a test screenshot...")
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            byte_io = io.BytesIO()
            img.save(byte_io, format="PNG")
            image_bytes = byte_io.getvalue()
            print("    -> Screenshot captured successfully.")
    except Exception as e:
        print(f"[!] Failed to capture screenshot: {e}")
        return

    prompt = "Describe exactly what you see on this screen in one short sentence."

    print(f"[*] Sending image to {MODEL} on {SERVER_IP}...")
    start_time = time.time()

    try:
        response_text = analyze_image_ollama(
            image_bytes=image_bytes,
            model=MODEL,
            server_ip=SERVER_IP,
            api_key=API_KEY,
            prompt=prompt,
        )
        end_time = time.time()

        print("\n" + "=" * 40)
        print("✅ TEST SUCCESSFUL")
        print("=" * 40)
        print(f"AI Description : {response_text}")
        print(f"Inference Time : {end_time - start_time:.2f} seconds")
        print("=" * 40 + "\n")

    except Exception as e:
        print("\n" + "=" * 40)
        print("❌ TEST FAILED")
        print("=" * 40)
        print(f"Error Details: {e}")
        print("\nTroubleshooting:")
        print("1. Is the server IP correct?")
        print("2. Is Ollama running on the server?")
        print("3. Did you configure Ollama to listen on 0.0.0.0 instead of just localhost?")


if __name__ == "__main__":
    run_test()
