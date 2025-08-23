import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# Load API key securely
API_KEY = os.getenv("IMAGEGEN_API_KEY", "ddc-a4f-3085d84aef2847f5a150214d4fe4513d")

# Imagen API endpoint
IMAGEN_API_URL = "https://api.a4f.co/v1/images/generations"

def generate_image(enhanced_data: dict, count: int = 1) -> list:
    """
    Generates images using the Imagen API and returns them
    as a list of base64 strings. Supports up to 3 images per request.
    Uses a 3-tier fallback strategy: primary -> secondary -> tertiary models.

    Args:
        enhanced_data (dict): The full JSON from enhance_prompt, containing:
            - aspect_ratio
            - primary_model: {name, enhanced_prompt}
            - secondary_model: {name, enhanced_prompt}
            - tertiary_model: {name, enhanced_prompt}
        count (int): Number of images (capped at 3).
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Extract aspect_ratio
    aspect_ratio = enhanced_data.get("aspect_ratio", "1:1")

    # Map aspect ratios to sizes
    aspect_map = {
        "1:1": "1024x1024",
        "16:9": "1280x720",
        "9:16": "720x1280",
        "4:3": "1024x768",
        "3:4": "768x1024",
        "3:2": "1024x683",
        "2:3": "683x1024"
    }

    # Model configs with provider prefixes
    model_configs = {
        "imagen-4": {"api_model": "provider-4/imagen-4", "default_size": "1024x1024"},
        "imagen-3": {"api_model": "provider-4/imagen-3", "default_size": "1024x1024"},
        "qwen-image": {"api_model": "provider-5/qwen-image", "default_size": "1024x1024"},
        "flux-schnell-v2": {"api_model": "provider-7/flux-schnell-v2", "default_size": "1024x1024"},
        "sana-1.5": {"api_model": "provider-6/sana-1.5", "default_size": "4096x4096"}
    }

    count = min(count, 3)  # cap at 3

    # Define tiers
    tiers = ["primary_model", "secondary_model", "tertiary_model"]

    for tier_key in tiers:
        if tier_key not in enhanced_data:
            print(f"⚠️ {tier_key} not found in enhanced_data, skipping.")
            continue

        tier = enhanced_data[tier_key]
        model = tier.get("name")
        prompt = tier.get("enhanced_prompt")

        if not model or not prompt:
            print(f"⚠️ Missing model or prompt in {tier_key}, skipping.")
            continue

        print(f"🧪 Trying {tier_key} ({model})...")

        # Skip if model not supported in configs
        if model not in model_configs:
            print(f"⚠️ Model {model} not supported, skipping.")
            continue

        # Check aspect ratio compatibility for imagen models
        if model in ["imagen-4", "imagen-3"] and aspect_ratio in ["16:9", "9:16"]:
            print(f"⚠️ {model} does not support {aspect_ratio}, skipping.")
            continue

        config = model_configs[model]
        size = aspect_map.get(aspect_ratio, config["default_size"])

        data = {
            "model": config["api_model"],
            "prompt": prompt,
            "n": count,
            "size": size
        }

        try:
            # Call the Imagen API
            response = requests.post(IMAGEN_API_URL, headers=headers, json=data)
            response.raise_for_status()

            # Extract image URLs
            image_urls = [item['url'] for item in response.json()['data']]
            print(f"✅ Image URLs for {model}:", image_urls)

            # Download and convert to base64
            images = []
            for url in image_urls:
                image_response = requests.get(url)
                image_response.raise_for_status()
                base64_string = base64.b64encode(image_response.content).decode('utf-8')
                images.append(base64_string)

            return images

        except requests.RequestException as e:
            print(f"❌ Error during image generation for {model}:", str(e))
            continue

    raise RuntimeError("All model tiers failed to generate images.")