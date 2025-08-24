from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()  # Ensure .env variables are loaded

def clean_and_parse_json(raw_response):
    """
    Bulletproof JSON cleaner that handles all the weird stuff AI models throw at us
    """
    print(f"🧠 [generate-fields] Raw response from LLaMA:\n{raw_response}")
    
    try:
        # Step 1: Remove markdown code blocks (```json, ```, etc.)
        cleaned = re.sub(r'```(?:json)?\s*', '', raw_response, flags=re.IGNORECASE)
        cleaned = re.sub(r'```\s*$', '', cleaned, flags=re.MULTILINE)
        
        # Step 2: Remove any leading/trailing text before first { and after last }
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(0)
        else:
            raise ValueError("No JSON object found in response")
        
        # Step 3: Fix common JSON issues
        # Remove trailing commas before closing braces/brackets
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
        
        # Fix single quotes to double quotes (but be careful with content)
        # Only replace single quotes around keys and simple values
        cleaned = re.sub(r"'([^']*?)':", r'"\1":', cleaned)  # Keys
        cleaned = re.sub(r':\s*\'([^\']*?)\'([,}\]])', r': "\1"\2', cleaned)  # Values
        
        
        
        # Step 5: Try to parse
        parsed_json = json.loads(cleaned)
        print(f"✅ [generate-fields] Successfully parsed JSON")
        return parsed_json
        
    except json.JSONDecodeError as e:
        print(f"❌ [generate-fields] JSON parsing error: {e}")
        print(f"🔍 Cleaned response: {cleaned[:500]}...")
        
        # Last resort: try to extract JSON fields manually
        return extract_json_fields_manually(raw_response)
    
    except Exception as e:
        print(f"❌ [generate-fields] Unexpected error: {e}")
        return extract_json_fields_manually(raw_response)

def extract_json_fields_manually(raw_response):
    """
    Manual extraction when JSON parsing completely fails
    """
    print("🔧 [generate-fields] Attempting manual field extraction...")
    
    result = {}
    
    # Common field patterns to extract
    field_patterns = {
        'custom_prompt': r'"custom_prompt":\s*"([^"]*)"',
        'hero_headline': r'"hero_headline":\s*"([^"]*)"',
        'hero_subline': r'"hero_subline":\s*"([^"]*)"',
        'description': r'"description":\s*"([^"]*)"',
        'success_metrics': r'"success_metrics":\s*"([^"]*)"',
        'testimonial': r'"testimonial":\s*"([^"]*)"',
        'target_audience': r'"target_audience":\s*"([^"]*)"',
        'cta': r'"cta":\s*"([^"]*)"',
        'cta_link': r'"cta_link":\s*"([^"]*)"',
        'suggested_theme': r'"suggested_theme":\s*"([^"]*)"'
    }
    
    for field, pattern in field_patterns.items():
        match = re.search(pattern, raw_response, re.IGNORECASE | re.DOTALL)
        if match:
            result[field] = match.group(1).strip()
    
    if result:
        print(f"✅ [generate-fields] Manual extraction found {len(result)} fields")
        return result
    else:
        print("❌ [generate-fields] Manual extraction failed too")
        return None

def call_llama_generate_fields(data):
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    # 🛠️ Coerce all checkbox fields to boolean
    def to_bool(val):
        return str(val).lower() == "true" or val is True

    # ✅ Build selected fields list (CTA freedom enabled)
    selected_fields = []
    if to_bool(data.include_hero_headline):
        selected_fields.append("hero_headline")
    if to_bool(data.include_hero_subline):
        selected_fields.append("hero_subline")
    if to_bool(data.include_description):
        selected_fields.append("description")
    if to_bool(data.include_cta):
        selected_fields.append("cta")
    if to_bool(data.include_cta_link):
        selected_fields.append("cta_link")
    if to_bool(data.include_testimonial):
        selected_fields.append("testimonial")
    if to_bool(data.include_success_metrics):
        selected_fields.append("success_metrics")
    if to_bool(data.include_target_audience):
        selected_fields.append("target_audience")

    # 🎨 Theme Expansion Instruction (ALWAYS Generate Suggested Theme)
    if data.theme:
        theme_msg = (
            f"The user provided a rough theme: '{data.theme}'. "
            "Your task is to expand it into a visually detailed, layout-aware background description for image generation. "
            "Include mood, colors, scene composition, and avoid vague words like 'modern'. "
            "Return the final theme in the key 'suggested_theme'."
        )
    else:
        theme_msg = (
            "The user did not provide a theme. "
            "Based on the enhanced main prompt's intent, generate a vivid scene composition and return it in 'suggested_theme'. "
            "Include background details like mood, lighting, color palette, and visual motifs."
        )

    # 🧠 Compose System Prompt with all Fields in FORMAT EXAMPLE
    system_prompt = f"""
You are a professional poster content generation AI specializing in educational and marketing visuals.

TASK FLOW:
1. Take the user's raw main prompt and expand it into a **vivid, visually-rich, and action-oriented 'custom_prompt'**.
    - The custom_prompt should describe the poster's intent with immersive scene details.
    - Include actions, participants, environment, mood-setting phrases, and visual motifs.
    - Avoid generic terms like "Create a poster for X". Be vivid, descriptive, and scene-aware.
2. Based on the juiced-up custom_prompt, generate content for ONLY the following fields: {', '.join(selected_fields)}.
3. {theme_msg}
4. Output a JSON object with EXACTLY these keys:
    - "custom_prompt"
    - {', '.join([f'"{field}"' for field in selected_fields])}
    - "suggested_theme"

RULES:
- The custom_prompt must be vivid, action-driven, and feel like a visual storyboard.
- For any unselected fields, do NOT include them.
- All field content must strictly follow token limits.
- Return ONLY valid JSON without any markdown formatting, code blocks, or explanations.
- Use double quotes for all strings.

FIELD CONSTRAINTS:
- "hero_headline": max 12 tokens
- "hero_subline": max 15 tokens
- "description": max 25 tokens
- "testimonial": max 25 tokens (short single-quote quote)
- "success_metrics": max 20 tokens (pipe-separated stats)
- "target_audience": max 15 tokens
- "cta" and "cta_link": very short and clean
- 'cta' and 'cta_link' are independent fields.

FORMAT EXAMPLE:
{{
  "custom_prompt": "Design a vibrant poster capturing a dynamic Python Bootcamp scene, where students collaborate on laptops, sharing ideas in a high-energy tech workspace filled with neon code overlays and team brainstorming sessions.",
  "hero_headline": "Code. Collaborate. Succeed!",
  "hero_subline": "Unlock Your Potential in 6 Weeks",
  "description": "Master Python through hands-on projects guided by industry mentors in an intensive 6-week program.",
  "success_metrics": "95% Job Placement | 4.5/5 Rating | 1000+ Alumni",
  "testimonial": "'This bootcamp transformed my career!'",
  "target_audience": "Aspiring developers and data scientists",
  "cta": "Apply Now",
  "cta_link": "https://pythonbootcamp.io",
  "suggested_theme": "A bustling startup workspace with glass walls, digital screens, and energetic collaboration zones bathed in warm lighting and bold color accents."
}}
"""

    # 🧠 Call LLaMA Model
    response = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": data.main_prompt}
        ],
        temperature=0.7
    )

    raw_response = response.choices[0].message.content
    
    # 🧹 Clean and parse JSON with bulletproof method
    parsed_data = clean_and_parse_json(raw_response)
    
    return parsed_data