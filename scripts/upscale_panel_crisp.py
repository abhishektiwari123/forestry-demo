#!/usr/bin/env python3
"""
Upscale images using Recraft's Crisp Upscale API.

Crisp Mode: Increases resolution and sharpness WITHOUT altering structure or content.
This mode preserves the original composition, faces, and details faithfully.

Usage:
    python upscale_panel_crisp.py image.jpg --scale 4 --output output.jpg
"""

import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
import requests

# Try loading .env from multiple locations
for env_path in ['.env', 'scripts/.env', '../scripts/.env', '../../scripts/.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break


def upload_image(image_path: str) -> str | None:
    """Upload image to imgcdn.dev and return the URL."""
    print(f"  Uploading image to CDN...")

    with open(image_path, 'rb') as f:
        image_data = f.read()

    try:
        response = requests.post(
            "https://imgcdn.dev/api/1/upload",
            files={"source": (os.path.basename(image_path), image_data, "image/jpeg")},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("status_code") == 200:
                url = result.get("image", {}).get("url")
                print(f"  Uploaded: {url}")
                return url
    except Exception as e:
        print(f"  Upload error: {e}")

    return None


def upscale_crisp(image_path: str, output_path: str, scale: int = 4) -> bool:
    """
    Upscale image using Recraft Crisp Upscale API.

    Crisp mode enhances resolution and sharpness while preserving:
    - Original composition
    - Character faces and expressions
    - Fine details and textures
    - Color accuracy

    Args:
        image_path: Path to input image
        output_path: Path to save upscaled image
        scale: Upscale factor (2 or 4)

    Returns:
        True if successful
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY not found in environment")
        return False

    # Validate scale factor
    if scale not in [2, 4]:
        print(f"Error: Scale must be 2 or 4, got {scale}")
        return False

    # Get original dimensions
    with Image.open(image_path) as img:
        orig_width, orig_height = img.size

    print(f"\n{'='*60}")
    print(f"CRISP UPSCALE - Preserving Original Content")
    print(f"{'='*60}")
    print(f"Input: {image_path}")
    print(f"Original size: {orig_width}x{orig_height}")
    print(f"Target size: {orig_width * scale}x{orig_height * scale}")
    print(f"Scale factor: {scale}x")
    print(f"{'='*60}\n")

    # Upload image
    image_url = upload_image(image_path)
    if not image_url:
        print("Error: Failed to upload image")
        return False

    # Submit upscaling job
    print("  Submitting upscaling job...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "recraft-crisp-upscale",
        "image_url": image_url,
        "scale": scale
    }

    try:
        response = requests.post(
            "https://api.kie.ai/v1/images/upscale",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        task_id = result.get("task_id") or result.get("id")
        if not task_id:
            # Direct result
            output_url = result.get("output", {}).get("image_url")
            if output_url:
                return download_result(output_url, output_path)
            print(f"Error: Unexpected response: {result}")
            return False

        print(f"  Task ID: {task_id}")
        print("  Processing (this may take 30-120 seconds)...")

        # Poll for completion
        status_url = f"https://api.kie.ai/v1/images/upscale/{task_id}"

        for attempt in range(60):  # Max 5 minutes
            time.sleep(2)

            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            status = status_data.get("status", "").lower()

            if status in ["completed", "succeeded"]:
                output_url = status_data.get("output", {}).get("image_url")
                if not output_url:
                    output_url = status_data.get("image_url")

                if output_url:
                    return download_result(output_url, output_path)
                print(f"Error: No output URL in response")
                return False

            elif status in ["failed", "error"]:
                error = status_data.get("error", "Unknown error")
                print(f"Error: Upscaling failed - {error}")
                return False

            if attempt % 15 == 0:
                print(f"  Still processing... ({attempt * 2}s)")

        print("Error: Timeout after 2 minutes")
        return False

    except Exception as e:
        print(f"Error: API request failed - {e}")
        return False


def download_result(url: str, output_path: str) -> bool:
    """Download upscaled image and save to disk."""
    print(f"  Downloading result...")

    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=120)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        # Get final dimensions
        with Image.open(output_path) as img:
            width, height = img.size

        file_size = Path(output_path).stat().st_size / (1024 * 1024)

        print(f"\n{'='*60}")
        print(f"SUCCESS!")
        print(f"Output: {output_path}")
        print(f"Final size: {width}x{height}")
        print(f"File size: {file_size:.2f} MB")
        print(f"{'='*60}\n")

        return True

    except Exception as e:
        print(f"Error downloading result: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Upscale images using Recraft Crisp Upscale (preserves content)"
    )
    parser.add_argument(
        "image",
        help="Path to input image"
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=4,
        choices=[2, 4],
        help="Upscale factor (2 or 4, default: 4)"
    )
    parser.add_argument(
        "--output",
        help="Output path (default: auto-generated)"
    )

    args = parser.parse_args()

    # Validate input exists
    if not os.path.exists(args.image):
        print(f"Error: Input file not found: {args.image}")
        sys.exit(1)

    # Generate output path if not specified
    output_path = args.output
    if not output_path:
        input_path = Path(args.image)
        output_dir = str(input_path.parent).replace("_extracted", "_crisp_upscaled")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = f"{output_dir}/{input_path.stem}_crisp_{args.scale}x{input_path.suffix}"

    success = upscale_crisp(args.image, output_path, args.scale)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
