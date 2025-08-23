def build_image_generation_prompt(fields: dict) -> str:
    """
    Dynamically constructs an image generation prompt for a poster based on provided fields JSON.
    
    Args:
        fields (dict): Dictionary containing 'custom_prompt', 'suggested_theme', and other field content.
    
    Returns:
        str: Fully assembled image generation prompt ready for the image model.
    """

    # Extract custom_prompt (First Sentence of the prompt)
    custom_prompt = fields.get('custom_prompt', 'Design a professional educational poster for a tech program.')

    # Extract suggested_theme (Background Theme Section)
    theme_block = fields.get('suggested_theme', 'A clean, tech-inspired background with modern gradients and soft lighting effects.')

    # Build Layout Lines based on available fields
    layout_lines = []

    if 'hero_headline' in fields:
        layout_lines.append(f'- Top center: Large bold heading — "{fields["hero_headline"]}"')

    if 'hero_subline' in fields:
        layout_lines.append(f'- Just below: Smaller subheading — "{fields["hero_subline"]}"')

    if 'description' in fields:
        layout_lines.append(f'- Center area: Short paragraph — "{fields["description"]}"')

    if 'success_metrics' in fields:
        layout_lines.append(f'- Bottom left: Compact highlight of achievements — "{fields["success_metrics"]}"')

    if 'target_audience' in fields:
        layout_lines.append(f'- Bottom right: Brief audience description — "{fields["target_audience"]}"')

    if 'testimonial' in fields:
        layout_lines.append(f'- Lower section: Italicized quote — "{fields["testimonial"]}"')

    if 'cta' in fields:
        layout_lines.append(f'- Bottom center: Button with the text — "{fields["cta"]}"')

    if 'cta_link' in fields:
        layout_lines.append(f'- Very bottom: Minimal hyperlink — "{fields["cta_link"]}"')

    layout_block = "\n".join(layout_lines)

    # Build Final Prompt String
    full_prompt = f"""
{custom_prompt}

📐 Layout:
{layout_block}

🧠 Critical Instructions:
- Do **not** include any field labels like “Success Metrics”, “Target Audience”, or “Testimonial”.
- The text should appear *naturally* as part of the poster design — not as form layout or metadata.
- Treat all text elements as part of the visual composition.
- Avoid overlapping, distortion, and gibberish. Fonts must be clean, sans-serif, and fully legible.

🎨 Background Theme:
{theme_block}

🖋 Typography & Composition:
- Fonts: Bold, sans-serif, clean, fully legible.
- Layout: Balanced, white-space aware, no overlaps.
- No gibberish text, no field names like 'Testimonial' shown.
""".strip()
    return full_prompt