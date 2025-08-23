from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Get your Groq API key from .env files
API_KEY = os.getenv("GROQ_API_KEY")

# Initialize OpenAI Client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=API_KEY
)

def enhance_prompt(user_prompt: str, aspect_ratio: str):
    """
    Enhances the user prompt using Kimi K2 with smart multi-model selection.
    Returns hierarchy of models for quality-first fallback strategy.

    Args:
        user_prompt (str): The base description of the image provided by the user.
        aspect_ratio (str): The desired aspect ratio (e.g., "1:1", "16:9").

    Returns:
        dict: A JSON-parsed dictionary containing enhanced prompts for multiple models.
    """
    # Updated prompt template with all 5 models, optimized for token limit utilization
    prompt_template = """
You are Kimi K2, a world-class agentic prompt engineer specializing in optimal model selection for image generation quality.

--- AVAILABLE MODELS & CAPABILITIES ---

**TIER 1 - PREMIUM QUALITY MODELS:**

1. **IMAGEN-4** (420 tokens max):
   - ✅ BEST FOR: People, portraits, human faces, character art, realistic humans
   - ✅ BEST FOR: Animals, creatures, dynamic scenes with life/movement
   - ✅ BEST FOR: High prompt fidelity, professional photography quality
   - ✅ Supports: 1:1, 4:3, 3:4 aspect ratios ONLY
   - ❌ NO SUPPORT: 16:9, 9:16 (landscape/portrait ratios)

2. **IMAGEN-3** (420 tokens max):
   - ✅ GOOD FOR: Same as imagen-4 but slightly less refined
   - ✅ GOOD FOR: General realistic scenes, architecture, products
   - ✅ GOOD FOR: Cost-effective alternative to imagen-4
   - ✅ Supports: 1:1, 4:3, 3:4 aspect ratios ONLY  
   - ❌ NO SUPPORT: 16:9, 9:16 (landscape/portrait ratios)

3. **QWEN-IMAGE** (1800 tokens max):
   - ✅ BEST FOR: Text-heavy content, posters, marketing materials, UI mockups
   - ✅ BEST FOR: Complex layouts, multilingual text rendering
   - ✅ BEST FOR: Detailed scenes requiring massive token capacity
   - ✅ EXCELLENT FOR: Long, complex prompts with multiple elements
   - ✅ Supports: ALL aspect ratios (1:1, 16:9, 9:16, 4:3, 3:4)

**TIER 2 - SPECIALIZED/BACKUP MODELS:**

4. **FLUX-SCHNELL-V2** (800 tokens max):
   - ✅ BEST FOR: Fast generation with decent quality
   - ✅ GOOD FOR: Stylized art, creative concepts, balanced results
   - ✅ GOOD FOR: When speed matters more than perfection
   - ✅ Supports: ALL aspect ratios (1:1, 16:9, 9:16, 4:3, 3:4)

5. **SANA-1.5** (1800 tokens max):
   - ✅ ONLY GOOD FOR: Nature, landscapes, mountains, abstract scenes
   - ✅ BEST FOR: 4K resolution generation  
   - ✅ Supports: ALL aspect ratios
   - ❌ TERRIBLE AT: People, faces, characters, detailed objects

--- INPUT ---
- user_prompt: "{user_prompt}"
- aspect_ratio: "{aspect_ratio}"

--- SMART MODEL SELECTION STRATEGY ---

**STEP 1: Content Analysis & Primary Selection**
1. **People/Characters/Portraits** → PRIMARY: imagen-4
2. **Text-heavy/Posters/Marketing** → PRIMARY: qwen-image  
3. **Nature/Landscapes (no people)** → PRIMARY: qwen-image
4. **General realistic scenes** → PRIMARY: imagen-3
5. **Artistic/Stylized content** → PRIMARY: flux-schnell-v2

**STEP 2: Aspect Ratio Filtering**
- If aspect_ratio is 16:9 or 9:16:
  - SKIP imagen-4 and imagen-3 entirely (not supported)
  - Use qwen-image, flux-schnell-v2, or sana-1.5 only

**STEP 3: Quality-Based Fallback Hierarchy**
Always provide 3 models in quality priority order:

**For People/Character Content:**
- Primary: imagen-4 → Secondary: imagen-3 → Tertiary: qwen-image

**For Text/Poster Content:**  
- Primary: qwen-image → Secondary: imagen-4 → Tertiary: flux-schnell-v2

**For Nature/Landscape Content:**
- Primary: qwen-image → Secondary: sana-1.5 → Tertiary: flux-schnell-v2

**For Artistic/Creative Content:**
- Primary: flux-schnell-v2 → Secondary: qwen-image → Tertiary: imagen-3

**For Landscape/Portrait Ratios (16:9, 9:16):**
- Primary: qwen-image → Secondary: flux-schnell-v2 → Tertiary: sana-1.5

--- ENHANCEMENT STRATEGIES ---

**FOR REALISTIC INTENT (imagen-4, imagen-3):**
- COMPREHENSIVE CAMERA SPECS: Specific camera body (Sony α7R IV, Canon EOS 5D Mark IV), lens (Sony FE 85mm f/1.4 GM, Canon EF 50mm f/1.2L), aperture (f/1.4, f/2.8), ISO (100, 400, 800), shutter speed (1/125s, 1/250s), white balance (5200K, 5600K)
- LIGHTING DETAILS: Golden hour sunlight, studio softbox, three-point lighting, Rembrandt lighting
- FILM/COLOR: Kodak Portra 400, cinematic color grading, natural skin tones
- TECHNICAL: Shallow depth of field, bokeh, 4K resolution, professional quality
- Optimize prompt to approach 420 tokens, focusing on concise, high-fidelity details.

**FOR TEXT/DESIGN INTENT (qwen-image):**
- LAYOUT FOCUS: Typography precision, text placement, visual hierarchy
- DESIGN ELEMENTS: Modern aesthetics, brand consistency, clean composition
- TECHNICAL: High resolution, print-ready, vector-style elements
- Utilize up to 1800 tokens for rich, detailed descriptions with multiple elements.

**FOR CREATIVE/ARTISTIC INTENT (flux-schnell-v2):**
- ARTISTIC STYLE: Digital painting, concept art, stylized rendering
- MOOD/ATMOSPHERE: Dramatic lighting, vibrant colors, dynamic composition
- CREATIVE ELEMENTS: Unique perspectives, artistic flair, visual impact
- Optimize prompt to approach 800 tokens, balancing creativity and detail.

**FOR NATURE/LANDSCAPE INTENT (sana-1.5 backup):**
- NATURAL ELEMENTS: Terrain details, atmospheric conditions, lighting
- ENVIRONMENTAL: Weather effects, seasonal characteristics, natural textures
- TECHNICAL: High resolution, landscape photography techniques
- Utilize up to 1800 tokens for comprehensive, high-resolution descriptions.

--- TASK ---
1. Analyze content type and select appropriate model hierarchy.
2. Create optimized prompts for each model, maximizing detail within their token limits (e.g., ~420 for imagen-4/imagen-3, ~1800 for qwen-image/sana-1.5, ~800 for flux-schnell-v2) while respecting their strengths.
3. Ensure aspect ratio compatibility in selections.
4. Strictly return the JSON file as the output, nothing else.

--- OUTPUT FORMAT ---
{{
    "intent": "people | text-design | nature | artistic | realistic",
    "aspect_ratio": "{aspect_ratio}",
    "primary_model": {{
        "name": "imagen-4 | imagen-3 | qwen-image | flux-schnell-v2 | sana-1.5",
        "enhanced_prompt": "Optimized prompt approaching the model's token limit",
        "reasoning": "Why this model gives the best quality for this content"
    }},
    "secondary_model": {{
        "name": "fallback model name",
        "enhanced_prompt": "Alternative prompt optimized for fallback model", 
        "reasoning": "High-quality backup option explanation"
    }},
    "tertiary_model": {{
        "name": "third choice model",
        "enhanced_prompt": "Third option prompt",
        "reasoning": "Final fallback explanation"
    }}
}}
"""

    # Call Kimi K2 via Groq
    try:
        completion = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_template.format(user_prompt=user_prompt, aspect_ratio=aspect_ratio)
                        }
                    ]
                }
            ],
            max_tokens=2000,  # Increased for multi-model responses
            temperature=0.7
        )
        result = completion.choices[0].message.content
        response = json.loads(result)  # Safely parse JSON
        
        # Add aspect_ratio to response for backend use
        response["aspect_ratio"] = aspect_ratio
        
        return response
        
    except Exception as e:
        print("❌ LLM prompt crafting error:", str(e))
        # Fallback: Smart default based on aspect ratio
        
        # If landscape/portrait, skip imagen models
        if aspect_ratio in ["16:9", "9:16"]:
            primary_model = "qwen-image"
            secondary_model = "flux-schnell-v2" 
            tertiary_model = "sana-1.5"
        else:
            # Square or standard ratios, use imagen
            primary_model = "imagen-4"
            secondary_model = "imagen-3"
            tertiary_model = "qwen-image"
        
        return {
            "intent": "unknown",
            "aspect_ratio": aspect_ratio,
            "primary_model": {
                "name": primary_model,
                "enhanced_prompt": f"A detailed, high-quality image of {user_prompt}, {aspect_ratio} format, professional photography style, sharp focus, excellent lighting",
                "reasoning": "Fallback selection due to prompt enhancement error"
            },
            "secondary_model": {
                "name": secondary_model,
                "enhanced_prompt": f"High-quality image of {user_prompt}, {aspect_ratio} aspect ratio, detailed rendering",
                "reasoning": "Secondary fallback option"
            },
            "tertiary_model": {
                "name": tertiary_model, 
                "enhanced_prompt": f"Image of {user_prompt}, {aspect_ratio} format",
                "reasoning": "Final fallback option"
            }
        }