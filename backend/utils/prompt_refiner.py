from openai import OpenAI
import os
from dotenv import load_dotenv  # 🟥 THIS LINE IS MISSING!

load_dotenv()

# Initialize Groq API Client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def refine_prompt_through_god_template(raw_prompt: str) -> str:
    """
    Takes a raw poster content prompt and refines it based on a God Prompt structure.
    Enforces strict token size limits to avoid Imagen API errors.
    """

    # 🟢 God Prompt Template (Reference)
    god_prompt_template = """
Design a premium 1024x1024 promotional poster for a Java Bootcamp.

📐 Layout:
- Top center: Bold headline in large, clean sans-serif font — "Collaborate, Code, Create: The Java Bootcamp"
- Just below: Subline in smaller, clean font — "Build Real-World Projects with Your Team"
- Center: A short paragraph — "Learn Java fundamentals and develop real-world projects with a team of peers in a dynamic and collaborative environment"
- Bottom left: A concise stat block — "95% Job Placement Rate | 4.5/5 Rating | 500+ Alumni"
- Bottom right: A short persona highlight — "Aspiring Java developers and career changers"
- Bottom center: A glowing button with the text — "Enroll Now"
- Somewhere near center or bottom: A short italicized quote — "Java Bootcamp exceeded my expectations! I landed a job at a top tech firm after graduating"

🧠 Critical Instructions:
- Do **not** include any field labels like “Success Metrics”, “Target Audience”, “Testimonial”.
- The text should appear *naturally* as part of the poster design — not as a form layout.
- Treat all text elements as part of the visual composition.

🎨 Background Theme:
A modern, high-energy collaborative workspace showing a diverse group of students working around a laptop. Include subtle overlays of digital code and network graphics without obscuring text. The background should have a clean gradient of bright blue and green tones.

🖋 Typography & Composition:
- Fonts: Bold, sans-serif, legible.
- Layout: Balanced, white-space aware, no overlaps.
- Avoid gibberish text and field names.
"""

    # 🧠 System Prompt Instructions (Token Limit Enforced)
    system_prompt = f"""
You are a prompt formatting AI. Given a raw poster content prompt, your task is to remodel it into a fully structured, API-safe, layout-aware prompt by using the following God Prompt Template as reference.

God Prompt Template:
{god_prompt_template}

STRICT RULES:
- The remodeled prompt MUST NOT exceed the token count of the God Prompt.
- Use compact, precise, and visually descriptive language.
- Do NOT add extra sentences or unnecessary elaborations.
- Expand vague theme descriptions ONLY if they fit within the token budget.
- Maintain the layout structure and richness of the template.
- Prioritize brevity, clarity, and API-safety.
- Respond with ONLY the formatted prompt. No JSON, no markdown, no explanations.
"""

    # 🟢 Groq API Call (LLaMA/Maverick)
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_prompt}
        ],
        temperature=0.3
    )

    # Extract and return the remodeled prompt
    refined_prompt = response.choices[0].message.content.strip()
    return refined_prompt
