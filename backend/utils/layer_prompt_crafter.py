import os
from dotenv import load_dotenv
import requests
from openai import OpenAI
import json

load_dotenv()

#Initalize OpenAI Client with Open Router
client=OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_API_KEY")
)

def craft_layered_prompts(user_prompt: str,aspect_ratio:str,theme:str=None,fields:dict=None):
    """Crafts layered prompts using grok4 via OpenRouter,enhance the user prompt and identify the layers"""
    #Prepare the prompt for Grok 4
    prompt_template = """
    You are a creative image prompt engineer.

    INPUTS:
    - user_prompt (str): The base description of the image: "{user_prompt}".
    - aspect_ratio (str): Desired aspect ratio: "{aspect_ratio}" (e.g., "16:9", "1:1").
    - theme (str, optional): If provided, enhance the image prompt to align with this theme: "{theme}".
    - fields (dict, optional): Contains specific creative constraints for:
        - background: Explicit description of the background: "{background_field}".
        - text: List of specific words or text to appear in the image: "{text_field}".
        - object: List of specific objects or elements to include: "{object_field}".

    TASK:
    1. Start with the given user_prompt.
    2. If a theme is provided:
        - Enrich the user_prompt with lush, vivid, detailed creativity that strongly reflects the theme, tailored to the aspect_ratio.
    3. If NO theme is provided:
        - Use your own creative authority to visualize and enhance the prompt, tailored to the aspect_ratio.
    4. If fields are provided:
        - Incorporate each specified field exactly into the final prompt.
        - Do NOT override these; treat them as fixed user constraints.
        - For 'text' and 'object', handle them as lists, using all provided items.
    5. If fields are NOT provided:
        - Infer the likely background, and identify multiple potential text elements and objects from the enhanced prompt, ensuring all are populated even for vague inputs.

    OUTPUT:
    Return a JSON object with:
    - "enhanced_prompt": The fully enriched prompt, reflecting the aspect_ratio.
    - "theme": The final theme used (either provided or AI-inferred).
    - "layers": A dictionary with:
        - "background": Detailed description of the background.
        - "text": A list of detailed descriptions for any text elements in the image (or [] if none).
        - "object": A list of detailed descriptions for objects or main elements.

    EXAMPLE OUTPUT:
    {
        "enhanced_prompt": "An epic mountain battle with two warriors clashing under a stormy sky, featuring the text 'Epic Showdown' and 'Round 1', formatted for 16:9 aspect ratio.",
        "theme": "action",
        "layers": {
            "background": "Rugged mountain range under a stormy sky with lightning",
            "text": ["'Epic Showdown' in bold red letters", "'Round 1' in smaller white text"],
            "object": ["A fierce warrior with a glowing sword", "A agile fighter with a shield"]
        }
    }
    """
    #Handle optional inputs
    theme_str=theme if theme else "no specific theme"
    fields_dict=fields or {}
    background_field=fields_dict.get("background","no specific background")
    text_field = str(fields_dict.get("text", "no specific text")) if fields_dict.get("text") else "no specific text"
    object_field = str(fields_dict.get("object", "no specific object")) if fields_dict.get("object") else "no specific object"
    full_prompt = prompt_template.format(
        user_prompt=user_prompt,
        aspect_ratio=aspect_ratio,
        theme=theme_str,
        background_field=background_field,
        text_field=text_field,
        object_field=object_field
    )
    #Call Grok 4 via OpenRouter
    try:
        completion=client.chat.completions.create(
            model="x-ai/grok-4",
            messages=[
                {
                    "role":"user",
                    "content":[{
                        "type":"text",
                        "text":full_prompt
                    }]
                }
            ],
            max_tokens=500,
            temparature=0.7
        )
        result=completion.choices[0].message.content
        return json.loads(result) #Safely parse the JSON
    except Exception as e:
        print("LLM prompt crafting error:",str(e))
        #Fallback: Default layer prompts with multiple support
        return {
            "enhanced_prompt": f"A vibrant {user_prompt} scene with dynamic details, formatted for {aspect_ratio}",
            "theme": theme or "dynamic action",
            "layers": {
                "background": f"A detailed background for {user_prompt}, {aspect_ratio}",
                "text": [f"Bold text related to {user_prompt}, {aspect_ratio}"] if not fields else [],
                "object": [f"Main object from {user_prompt}, {aspect_ratio}"]
            }
        }
    
    
        
        


   