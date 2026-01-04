#!/usr/bin/env python3
"""
Generate photorealistic image assets using Google Gemini 2.5 Flash.

Usage:
    python generate_asset.py --name "haunter_full_body" --prompt "Photorealistic Haunter..." --output "../haunter/assets/haunter.jpg"
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def generate_asset(name: str, prompt: str, output_path: str) -> bool:
    """
    Generate an image asset using Google Gemini.

    Args:
        name: Asset name for logging
        prompt: Image generation prompt
        output_path: Where to save the generated image

    Returns:
        True if successful, False otherwise
    """
    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        print("Please set it in scripts/.env")
        return False

    genai.configure(api_key=api_key)

    try:
        print(f"🎨 Generating asset: {name}")
        print(f"📝 Prompt: {prompt[:100]}...")

        # Use Gemini's image generation model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Generate image
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                top_p=0.95,
            )
        )

        # Save the generated image
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Note: This is a simplified version. In production, you'd extract
        # the actual image data from the response and save it.
        # Gemini's image generation API may vary - adjust based on actual API.

        if hasattr(response, 'images') and response.images:
            # Save the first image
            with open(output_path, 'wb') as f:
                f.write(response.images[0])
            print(f"✅ Asset saved to: {output_path}")
            return True
        else:
            print("⚠️  Note: Gemini 2.5 Flash may not support direct image generation.")
            print("    Consider using Imagen or another image generation model.")
            print("    This is a template - adjust based on your chosen image generation API.")
            return False

    except Exception as e:
        print(f"❌ Error generating asset: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate photorealistic image assets using Google Gemini"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Asset name (e.g., 'haunter_full_body_front')"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Image generation prompt (photorealistic, detailed)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (e.g., '../haunter/assets/haunter.jpg')"
    )

    args = parser.parse_args()

    success = generate_asset(args.name, args.prompt, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
