import requests
import base64
import os

# Load API key securely (fallback to hardcoded if needed)
API_KEY = os.getenv("IMAGEGEN_API_KEY", "ddc-a4f-3085d84aef2847f5a150214d4fe4513d")

# Imagen API endpoint
IMAGEN_API_URL = "https://api.a4f.co/v1/images/generations"

def generate_poster_image(prompt: str) -> str:
    """
    Calls the Imagen 4 API using raw POST, retrieves the image URL,
    downloads the image, and returns it as a base64 string.

    Args:
        prompt (str): The full image generation prompt.

    Returns:
        str: Base64-encoded image suitable for frontend rendering.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "provider-6/qwen-image",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }

    try:
        # Step 1: Call the Imagen API
        response = requests.post(IMAGEN_API_URL, headers=headers, json=data)
        response.raise_for_status()

        image_url = response.json()['data'][0]['url']
        print("✅ Image URL:", image_url)

        # Step 2: Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # Step 3: Convert to base64
        image_bytes = image_response.content
        base64_string = base64.b64encode(image_bytes).decode('utf-8')

        return base64_string

    except requests.RequestException as e:
        print("❌ Error during image generation or download:", str(e))
        raise RuntimeError("Poster image generation failed.") from e
