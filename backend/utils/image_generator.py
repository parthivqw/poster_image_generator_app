import requests
import base64
import os
import time

# Load API key securely (fallback to hardcoded if needed)
API_KEY = os.getenv("IMAGEGEN_API_KEY", "ddc-a4f-3085d84aef2847f5a150214d4fe4513d")

# Imagen API endpoint
IMAGEN_API_URL = "https://api.a4f.co/v1/images/generations"

# Model priority list - will try in order
MODELS = [
    "provider-6/qwen-image",      # Primary model
    "provider-4/imagen-4",        # Backup model 1
    "provider-4/imagen-3"         # Backup model 2
]

def generate_poster_image(prompt: str) -> str:
    """
    Calls the Imagen API with fallback models, retrieves the image URL,
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
    
    last_error = None
    
    # Try each model in sequence
    for i, model in enumerate(MODELS):
        print(f"🔄 Trying model {i+1}/{len(MODELS)}: {model}")
        
        data = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        
        try:
            # Step 1: Call the Imagen API
            response = requests.post(IMAGEN_API_URL, headers=headers, json=data)
            response.raise_for_status()
            
            image_url = response.json()['data'][0]['url']
            print(f"✅ Image URL from {model}: {image_url}")
            
            # Step 2: Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Step 3: Convert to base64
            image_bytes = image_response.content
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            
            print(f"✅ Successfully generated image using {model}")
            return base64_string
            
        except requests.RequestException as e:
            last_error = e
            print(f"❌ Model {model} failed: {str(e)}")
            
            # If not the last model, wait a bit before trying next one
            if i < len(MODELS) - 1:
                print("⏳ Waiting 1 second before trying next model...")
                time.sleep(1)
            continue
    
    # If all models failed, raise the last error
    print("❌ All models failed!")
    raise RuntimeError(f"All image generation models failed. Last error: {str(last_error)}") from last_error