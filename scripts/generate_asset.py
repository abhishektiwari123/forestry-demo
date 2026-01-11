#!/usr/bin/env python3
"""
Generate photorealistic image assets using KIE.ai API.

Usage:
    python generate_asset.py --name "haunter_forest" --prompt "Photorealistic Haunter..." --output assets/haunter_forest_01.png
"""

import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


def generate_asset(name: str, prompt: str, output_path: str) -> bool:
    """
    Generate a photorealistic image asset using KIE.ai text-to-image API.

    Args:
        name: Asset name for logging
        prompt: Text description of the image to generate
        output_path: Where to save the generated image

    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY not found in environment variables")
        return False

    print(f"Generating asset: {name}")
    print(f"Prompt: {prompt[:100]}...")

    # KIE.ai API endpoint for text-to-image
    url = "https://api.kie.ai/v1/images/generations"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-v2",
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "quality": "high",
        "n": 1
    }

    try:
        # Submit generation request
        print("Submitting generation request...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        task_id = result.get("task_id") or result.get("id")

        if not task_id:
            # Direct response with image URL
            image_url = result.get("data", [{}])[0].get("url")
            if image_url:
                return download_image(image_url, output_path)
            print(f"Error: Unexpected response format: {result}")
            return False

        # Poll for completion
        print(f"Task ID: {task_id}")
        print("Waiting for generation to complete...")

        status_url = f"https://api.kie.ai/v1/images/generations/{task_id}"

        for attempt in range(60):  # Max 5 minutes
            time.sleep(5)

            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_response.raise_for_status()

            status_data = status_response.json()
            status = status_data.get("status", "").lower()

            if status == "completed" or status == "succeeded":
                image_url = status_data.get("output", {}).get("image_url")
                if not image_url:
                    images = status_data.get("data", [])
                    if images:
                        image_url = images[0].get("url")

                if image_url:
                    return download_image(image_url, output_path)
                else:
                    print(f"Error: No image URL in response: {status_data}")
                    return False

            elif status == "failed" or status == "error":
                error_msg = status_data.get("error", "Unknown error")
                print(f"Error: Generation failed - {error_msg}")
                return False

            print(f"  Status: {status} (attempt {attempt + 1}/60)")

        print("Error: Generation timed out after 5 minutes")
        return False

    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed - {e}")
        return False


def download_image(url: str, output_path: str) -> bool:
    """Download image from URL and save to disk."""
    try:
        print(f"Downloading image to {output_path}...")

        # Create output directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"Success! Image saved to {output_path}")
        return True

    except Exception as e:
        print(f"Error downloading image: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate photorealistic image assets using KIE.ai API"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Asset name (for logging and identification)"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Text description of the image to generate"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path for the generated image"
    )

    args = parser.parse_args()

    success = generate_asset(args.name, args.prompt, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
