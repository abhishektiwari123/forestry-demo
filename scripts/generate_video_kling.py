#!/usr/bin/env python3
"""
Generate video from image using Kling 2.6 via KIE API.

Usage:
    python generate_video_kling.py --image scene.jpg --prompt "Motion description" --output video.mp4
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import requests

# Load environment variables
for env_path in ['.env', 'scripts/.env', '../scripts/.env', '../../scripts/.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break


def upload_image(image_path: str, max_retries: int = 4) -> str | None:
    """Upload image to CDN and return URL."""
    print(f"  Uploading image to CDN...")

    with open(image_path, 'rb') as f:
        image_data = f.read()

    delays = [2, 4, 8, 16]

    for attempt in range(max_retries):
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
            print(f"  Upload attempt {attempt + 1} failed: {e}")

        if attempt < max_retries - 1:
            delay = delays[attempt]
            print(f"  Retrying in {delay}s...")
            time.sleep(delay)

    return None


def generate_video(
    image_path: str,
    prompt: str,
    output_path: str,
    duration: int = 5
) -> bool:
    """
    Generate video from image using Kling 2.6 via KIE API.

    Args:
        image_path: Path to source image
        prompt: Motion/video description
        output_path: Where to save the video
        duration: Video duration in seconds (5 or 10)

    Returns:
        True if successful
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY not found")
        return False

    print(f"\n{'='*60}")
    print(f"KLING 2.6 VIDEO GENERATION")
    print(f"{'='*60}")
    print(f"Image: {image_path}")
    print(f"Prompt: {prompt[:80]}...")
    print(f"Duration: {duration}s")
    print(f"{'='*60}\n")

    # Verify image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return False

    # Upload image
    image_url = upload_image(image_path)
    if not image_url:
        print("Error: Failed to upload image")
        return False

    # Create video generation task
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": [image_url],
            "prompt": prompt,
            "duration": str(duration),
            "sound": True
        }
    }

    try:
        print("  Submitting video generation task...")
        response = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"  Response status: {response.status_code}")
        result = response.json()
        print(f"  Response: {json.dumps(result)[:200]}")

        if response.status_code != 200:
            print(f"Error: API returned {response.status_code}")
            return False

        task_id = result.get("data", {}).get("taskId")
        if not task_id:
            print(f"Error: No task ID in response: {result}")
            return False

        print(f"  Task ID: {task_id}")
        print("  Generating video (typically 60-180 seconds)...")

        # Poll for completion
        status_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"

        for attempt in range(120):  # Max 10 minutes
            time.sleep(5)

            try:
                status_response = requests.get(status_url, headers=headers, timeout=30)
                status_data = status_response.json()

                status = status_data.get("data", {}).get("status", "").lower()

                if status == "success" or status == "completed":
                    # Get result URL
                    result_json = status_data.get("data", {}).get("resultJson")
                    if result_json:
                        if isinstance(result_json, str):
                            result_json = json.loads(result_json)

                        video_url = None
                        if isinstance(result_json, list) and len(result_json) > 0:
                            video_url = result_json[0].get("url") or result_json[0].get("video_url")
                        elif isinstance(result_json, dict):
                            video_url = result_json.get("url") or result_json.get("video_url")

                        if video_url:
                            return download_video(video_url, output_path)

                    print(f"Error: No video URL in result: {status_data}")
                    return False

                elif status == "failed" or status == "error":
                    error = status_data.get("data", {}).get("error", "Unknown error")
                    print(f"Error: Generation failed - {error}")
                    return False

                if attempt % 12 == 0 and attempt > 0:
                    print(f"  Still generating... ({attempt * 5}s)")

            except Exception as e:
                print(f"  Status check error: {e}")

        print("Error: Timeout after 10 minutes")
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def download_video(url: str, output_path: str) -> bool:
    """Download video from URL."""
    print(f"  Downloading video...")

    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"\n  SUCCESS!")
        print(f"  Saved: {output_path} ({file_size:.1f} MB)")

        return True

    except Exception as e:
        print(f"Error downloading: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate video from image using Kling 2.6"
    )
    parser.add_argument("--image", "-i", required=True, help="Source image path")
    parser.add_argument("--prompt", "-p", required=True, help="Motion/video description")
    parser.add_argument("--output", "-o", required=True, help="Output video path")
    parser.add_argument("--duration", "-d", type=int, default=5, choices=[5, 10],
                       help="Video duration in seconds (default: 5)")

    args = parser.parse_args()

    success = generate_video(args.image, args.prompt, args.output, args.duration)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
