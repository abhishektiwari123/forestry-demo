#!/usr/bin/env python3
"""
Generate single horizontal 16:9 scene using Nano Banana Pro API.

Usage:
    python generate_single_scene.py --prompt "Scene description" --output scene.jpg
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
for env_path in ['.env', 'scripts/.env', '../scripts/.env', '../../scripts/.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break


def generate_single_scene(
    prompt: str,
    output_path: str,
    negative_prompt: str = "",
    width: int = 1920,
    height: int = 1080
) -> bool:
    """
    Generate a single horizontal 16:9 scene using Nano Banana Pro.

    Args:
        prompt: Scene description
        output_path: Where to save the image
        negative_prompt: Elements to avoid
        width: Image width (default 1920 for 16:9)
        height: Image height (default 1080 for 16:9)

    Returns:
        True if successful
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY not found")
        return False

    print(f"\n{'='*60}")
    print(f"SINGLE SCENE GENERATION (16:9 Horizontal)")
    print(f"{'='*60}")
    print(f"Prompt: {prompt[:100]}...")
    print(f"Resolution: {width}x{height}")
    print(f"{'='*60}\n")

    # Default negative prompt for Pokemon scenes
    if not negative_prompt:
        negative_prompt = (
            "shields, defensive barriers, protective auras, trainers, humans, "
            "text, labels, watermarks, low quality, blurry, distorted, "
            "multiple scenes, split screen, grid layout, panel layout"
        )

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_images": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 30
        }
    }

    # Use curl for API call to avoid SSL issues
    curl_cmd = [
        "curl", "-k", "-s", "-X", "POST",
        "https://api.kie.ai/api/v1/jobs/createTask",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    try:
        print("  Submitting scene generation task...")
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"Error: curl failed: {result.stderr}")
            return False

        response = json.loads(result.stdout)
        print(f"  Response: {json.dumps(response)[:200]}")

        task_id = response.get("data", {}).get("taskId")
        if not task_id:
            print(f"Error: No task ID in response")
            return False

        print(f"  Task ID: {task_id}")
        print("  Generating scene (typically 30-90 seconds)...")

        # Poll for completion
        for attempt in range(60):  # Max 5 minutes
            time.sleep(5)

            status_cmd = [
                "curl", "-k", "-s",
                f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                "-H", f"Authorization: Bearer {api_key}"
            ]

            status_result = subprocess.run(status_cmd, capture_output=True, text=True, timeout=30)

            if status_result.returncode != 0:
                continue

            status_data = json.loads(status_result.stdout)
            status = status_data.get("data", {}).get("status", "").lower()

            if status in ["success", "completed"]:
                result_json = status_data.get("data", {}).get("resultJson")
                if result_json:
                    if isinstance(result_json, str):
                        result_json = json.loads(result_json)

                    image_url = None
                    if isinstance(result_json, list) and len(result_json) > 0:
                        image_url = result_json[0].get("url") or result_json[0].get("image_url")
                    elif isinstance(result_json, dict):
                        image_url = result_json.get("url") or result_json.get("image_url")

                    if image_url:
                        return download_image(image_url, output_path)

                print(f"Error: No image URL in result")
                return False

            elif status in ["failed", "error"]:
                error = status_data.get("data", {}).get("error", "Unknown")
                print(f"Error: Generation failed - {error}")
                return False

            if attempt % 6 == 0 and attempt > 0:
                print(f"  Still generating... ({attempt * 5}s)")

        print("Error: Timeout after 5 minutes")
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def download_image(url: str, output_path: str) -> bool:
    """Download image using curl."""
    print(f"  Downloading image...")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    curl_cmd = [
        "curl", "-k", "-L", "-s", "-o", output_path, url
    ]

    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=120)

    if result.returncode == 0 and os.path.exists(output_path):
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n  SUCCESS!")
        print(f"  Saved: {output_path} ({file_size:.2f} MB)")
        return True

    print(f"Error: Download failed")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate single horizontal 16:9 scene"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Scene description")
    parser.add_argument("--output", "-o", required=True, help="Output image path")
    parser.add_argument("--negative", "-n", default="", help="Negative prompt")
    parser.add_argument("--width", "-w", type=int, default=1920, help="Width (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Height (default: 1080)")

    args = parser.parse_args()

    success = generate_single_scene(
        args.prompt, args.output, args.negative,
        args.width, args.height
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
