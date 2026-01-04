#!/usr/bin/env python3
"""
Generate photorealistic image assets using KIE.ai API.

Usage:
    python generate_asset.py --name "charizard_full_body" --prompt "Photorealistic Charizard..." --output "../charizard/assets/charizard.jpg"
"""

import argparse
import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_asset(name: str, prompt: str, output_path: str) -> bool:
    """
    Generate an image asset using KIE.ai text-to-image API.

    Args:
        name: Asset name for logging
        prompt: Image generation prompt
        output_path: Where to save the generated image

    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found in environment variables")
        print("Please set it in scripts/.env")
        return False

    try:
        print(f"🎨 Generating asset: {name}")
        print(f"📝 Prompt: {prompt[:100]}...")

        # KIE.ai API endpoint for text-to-image
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Submit image generation request
        print(f"🚀 Submitting to KIE.ai API...")

        payload = {
            "prompt": prompt,
            "aspect_ratio": "16:9",  # For 1920x1080 output
            "output_format": "jpeg",
            "output_quality": 95
        }

        # Submit generation request
        response = requests.post(
            "https://api.kie.ai/v1/image/generate",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        result = response.json()

        # Check if image URL is directly returned or if we need to poll
        if "image_url" in result:
            # Direct URL returned
            image_url = result["image_url"]
            print(f"✅ Image generated!")

        elif "task_id" in result:
            # Need to poll for completion
            task_id = result["task_id"]
            print(f"⏳ Task ID: {task_id}")
            print(f"⏳ Waiting for image generation...")

            # Poll for completion
            max_attempts = 60  # 5 minutes max
            attempt = 0

            while attempt < max_attempts:
                time.sleep(5)
                attempt += 1

                # Check status
                status_response = requests.get(
                    f"https://api.kie.ai/v1/image/status/{task_id}",
                    headers=headers,
                    timeout=30
                )

                if status_response.status_code != 200:
                    continue

                status_data = status_response.json()
                status = status_data.get("status")

                if status == "completed":
                    image_url = status_data.get("image_url")
                    print(f"✅ Image generated!")
                    break

                elif status == "failed":
                    print(f"❌ Image generation failed")
                    print(f"Error: {status_data.get('error', 'Unknown error')}")
                    return False

                else:
                    # Still processing
                    if attempt % 6 == 0:  # Every 30 seconds
                        print(f"⏳ Still processing... ({attempt * 5}s elapsed)")

            if attempt >= max_attempts:
                print(f"❌ Timeout: Image generation took too long")
                return False
        else:
            print(f"❌ Unexpected response format: {result}")
            return False

        # Download image
        print(f"📥 Downloading image...")
        image_response = requests.get(image_url, timeout=30)

        if image_response.status_code != 200:
            print(f"❌ Failed to download image")
            return False

        # Save image
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(image_response.content)

        print(f"✅ Asset saved to: {output_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error generating asset: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate photorealistic image assets using KIE.ai"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Asset name (e.g., 'charizard_full_body_front')"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Image generation prompt (photorealistic, detailed)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (e.g., '../charizard/assets/charizard.jpg')"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Note: Using KIE.ai API for text-to-image generation.")
    print("If endpoints differ from this implementation, please adjust.")
    print("=" * 70)

    success = generate_asset(args.name, args.prompt, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
