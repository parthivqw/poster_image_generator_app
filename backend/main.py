from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schema import PosterRequest, PosterImageRequest, TextToImageRequest
from utils.llama_generate_fields import call_llama_generate_fields
from utils.prompt_builder import build_image_generation_prompt
from utils.prompt_refiner import refine_prompt_through_god_template
from utils.image_generator import generate_poster_image
from utils.extended_image_generator import generate_image
from utils.enhance_prompt import enhance_prompt
from dotenv import load_dotenv
import json
import os

load_dotenv()

app = FastAPI()

# ✅ Allow frontend (Angular) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ For dev only. Use specific domain in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Step 1: Generate Poster Fields using Groq LLaMA
@app.post("/generate-fields")
async def generate_fields(data: PosterRequest):
    try:
        print("\n📥 [generate-fields] Received POST with data:", data)

        # 🔁 Call Groq (LLaMA) to generate fields
        raw_response = call_llama_generate_fields(data)
        print("🧠 [generate-fields] Raw response from LLaMA:\n", raw_response)

        # 🧪 Parse JSON string safely
        parsed_json = json.loads(raw_response)

        # ✅ Return clean object to frontend
        return {
            "status": "success",
            "data": parsed_json,
            "message": "Poster fields generated using LLaMA."
        }

    except json.JSONDecodeError as e:
        print("❌ [generate-fields] JSON parsing error:", str(e))
        raise HTTPException(status_code=500, detail="Failed to parse LLaMA response as JSON.")

    except Exception as e:
        print("❌ [generate-fields] General error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# 🖼️ Step 2: Generate Final Poster Image
@app.post("/generate-poster")
async def generate_poster(data: PosterImageRequest):
    try:
        print("\n🎨 [generate-poster] Received fields for poster generation:", data.fields)

        # 🧱 Step 1: Build raw prompt from fields
        raw_prompt = build_image_generation_prompt(data.fields)
        print("📝 [generate-poster] Raw Prompt:\n", raw_prompt)

        # 🖼️ Step 2: Generate base64 poster image
        base64_img = generate_poster_image(raw_prompt)
        print("✅ [generate-poster] Poster image generated. Base64 length:", len(base64_img))

        return {
            "status": "success",
            "image_base64": base64_img,
            "message": "Poster image generated successfully."
        }

    except Exception as e:
        print("❌ [generate-poster] Image generation error:", str(e))
        raise HTTPException(status_code=500, detail="Poster image generation failed.")

# 🖼️ Step 3: Generate Images from Prompt
@app.post("/generate-images")
async def generate_images(data: TextToImageRequest):
    try:
        print("\n📥 [generate-images] Received POST with data:", data)

        # Step 1: Enhance the prompt via Kimi
        print("prepping raw payload to kimi k2")
        enhanced_data = enhance_prompt(
            user_prompt=data.main_prompt,
            aspect_ratio=data.aspect_ratio,
        )

        print("✨ [generate-images] Enhanced Data:\n", json.dumps(enhanced_data, indent=2, ensure_ascii=False))

        # Step 2: Generate images, capped at 3
        data.count = min(data.count, 3)
        images = generate_image(enhanced_data, count=data.count)

        return {
            "status": "success",
            "images": images,
            "message": f"{len(images)} images generated successfully."
        }

    except Exception as e:
        print("❌ [generate-images] Error:", str(e))
        raise HTTPException(status_code=500, detail="Our models are busy right now, try again later.")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Backend is running!"}

@app.get("/healthz")
async def health():
    return {"status": "healthy"}
