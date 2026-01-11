#!/usr/bin/env python3
"""
Generate storyboard images using Nano Banana Pro API.

Creates a multi-panel storyboard image (e.g., 4 scenes in 1 image)
that can be extracted and upscaled individually.

Usage:
    python generate_storyboard.py --prompt "Charizard vs Dragonite battle" --panels 4 --output storyboard.jpg
"""

import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import requests

# Try loading .env from multiple locations
for env_path in ['.env', 'scripts/.env', '../scripts/.env', '../../scripts/.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break


def generate_storyboard(
    prompt: str,
    output_path: str,
    panels: int = 4,
    style: str = "photorealistic"
) -> bool:
    """
    Generate a storyboard image with multiple panels using Nano Banana Pro.

    Args:
        prompt: Description of the storyboard scenes
        output_path: Where to save the storyboard image
        panels: Number of panels (2, 4, 6, or 8)
        style: Visual style (photorealistic, anime, etc.)

    Returns:
        True if successful
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY not found in environment")
        return False

    # Determine grid layout based on panel count
    if panels == 2:
        layout = "2x1 horizontal grid"
        aspect = "32:9"
    elif panels == 4:
        layout = "2x2 grid"
        aspect = "16:9"
    elif panels == 6:
        layout = "3x2 grid"
        aspect = "24:9"
    elif panels == 8:
        layout = "4x2 grid"
        aspect = "32:9"
    else:
        print(f"Error: Unsupported panel count {panels}. Use 2, 4, 6, or 8.")
        return False

    # Build storyboard prompt
    storyboard_prompt = f"""Create a {layout} storyboard with {panels} sequential scenes:

{prompt}

Style: {style}, cinematic composition, professional storyboard layout.
Each panel shows a different moment in the sequence.
Clear panel borders, consistent character appearance across all panels.
High detail, dramatic lighting, BBC Earth documentary quality.
"""

    print(f"\n{'='*60}")
    print(f"STORYBOARD GENERATION - Nano Banana Pro")
    print(f"{'='*60}")
    print(f"Prompt: {prompt[:80]}...")
    print(f"Panels: {panels} ({layout})")
    print(f"Style: {style}")
    print(f"Output: {output_path}")
    print(f"{'='*60}\n")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nano-banana-pro",
        "prompt": storyboard_prompt,
        "aspect_ratio": aspect,
        "quality": "high",
        "n": 1
    }

    try:
        print("Submitting storyboard generation request...")
        response = requests.post(
            "https://api.kie.ai/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        task_id = result.get("task_id") or result.get("id")

        if not task_id:
            # Direct response with image
            image_url = result.get("data", [{}])[0].get("url")
            if image_url:
                return download_image(image_url, output_path)
            print(f"Error: Unexpected response: {result}")
            return False

        print(f"Task ID: {task_id}")
        print("Generating storyboard (this may take 30-90 seconds)...")

        # Poll for completion
        status_url = f"https://api.kie.ai/v1/images/generations/{task_id}"

        for attempt in range(90):  # Max 3 minutes
            time.sleep(2)

            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            status = status_data.get("status", "").lower()

            if status in ["completed", "succeeded"]:
                image_url = (
                    status_data.get("output", {}).get("image_url") or
                    status_data.get("image_url") or
                    (status_data.get("data", [{}])[0].get("url") if status_data.get("data") else None)
                )

                if image_url:
                    return download_image(image_url, output_path)
                print(f"Error: No image URL in response")
                return False

            elif status in ["failed", "error"]:
                error = status_data.get("error", "Unknown error")
                print(f"Error: Generation failed - {error}")
                return False

            if attempt % 15 == 0 and attempt > 0:
                print(f"  Still generating... ({attempt * 2}s)")

        print("Error: Timeout after 3 minutes")
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def download_image(url: str, output_path: str) -> bool:
    """Download image from URL and save to disk."""
    print(f"Downloading storyboard...")

    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=120)
        response.raise_for_status()

        # Validate download
        if len(response.content) < 10000:
            print(f"Error: Downloaded file too small ({len(response.content)} bytes)")
            return False

        with open(output_path, 'wb') as f:
            f.write(response.content)

        file_size = Path(output_path).stat().st_size / (1024 * 1024)

        # Get dimensions
        try:
            from PIL import Image
            with Image.open(output_path) as img:
                width, height = img.size
            print(f"\nSuccess!")
            print(f"  File: {output_path}")
            print(f"  Size: {width}x{height}")
            print(f"  File size: {file_size:.2f} MB")
        except:
            print(f"\nSuccess! Saved to {output_path} ({file_size:.2f} MB)")

        return True

    except Exception as e:
        print(f"Error downloading: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate storyboard images using Nano Banana Pro API"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Description of the storyboard scenes"
    )
    parser.add_argument(
        "--panels", "-n",
        type=int,
        default=4,
        choices=[2, 4, 6, 8],
        help="Number of panels (default: 4)"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file path"
    )
    parser.add_argument(
        "--style", "-s",
        default="photorealistic",
        help="Visual style (default: photorealistic)"
    )

    args = parser.parse_args()

    success = generate_storyboard(
        args.prompt,
        args.output,
        args.panels,
        args.style
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
