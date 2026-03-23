import os
import time
from io import BytesIO
from godis_api import (
    load_environment,
    capture_screen,
    analyze_image_ollama,
    analyze_image_gemini,
    get_gemini_client,
    trigger_system_notification,
    trigger_fullscreen_warning,
)


def main():
    load_environment()

    backend = os.getenv("MODEL_BACKEND", "ollama").strip().lower()
    print(f"Starting lightweight background monitor using backend: {backend}")
    print("Press Ctrl+C to stop.")

    server_ip = os.getenv("OLLAMA_SERVER", "http://10.166.38.250:19122")
    model = os.getenv("OLLAMA_MODEL", "qwen3-vl:4b")
    api_key = os.getenv("OLLAMA_API_KEY", "")
    gemini_client = None

    if backend == "gemini":
        gemini_client = get_gemini_client()

    prompt = (
        "You are a strict productivity monitor. Analyze this screenshot of a computer screen. "
        "Is the primary content of this screen showing entertainment content (like YouTube vlogs, gaming videos, movies) "
        "OR erotic/NSFW anime? Ignore standard UI elements, text editors, code, or academic papers. "
        "Respond strictly with a single word: YES or NO."
    )

    check_interval = 30

    while True:
        print("capture screen ...")
        try:
            img = capture_screen()

            if backend == "ollama":
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_bytes = buffer.getvalue()
                result = analyze_image_ollama(
                    image_bytes=image_bytes,
                    model=model,
                    server_ip=server_ip,
                    api_key=api_key,
                    prompt=prompt,
                ).strip().upper()
            elif backend == "gemini":
                result = analyze_image_gemini(img=img, client=gemini_client, prompt=prompt).strip().upper()
            else:
                raise ValueError(f"Unsupported MODEL_BACKEND: {backend}. Must be ollama or gemini.")

            timestamp = time.strftime("%X")
            print(f"[{timestamp}] Analysis Result: {result}")

            if result == "YES":
                # trigger_system_notification(
                #     title="Focus Alert",
                #     message="Entertainment or distracting content detected. Get back to work!",
                # )
                trigger_fullscreen_warning()

            time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\nMonitor stopped.")
            break


if __name__ == "__main__":
    main()
