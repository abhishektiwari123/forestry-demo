#!/usr/bin/env python3
"""
Generate video clips from images using KIE.ai Kling 2.5 Pro.

Usage:
    python generate_video.py --image scene.png --prompt "Haunter slowly materializes..." --output video.mp4 --segment 1
"""

import argparse
import base64
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


def upload_image_to_hosting(image_path: str) -> str | None:
    """
    Upload image to a temporary hosting service and return the URL.
    Tries multiple fallback services.
    """
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Try imgcdn.dev first
    try:
        response = requests.post(
            "https://imgcdn.dev/api/1/upload",
            files={"source": ("image.png", image_data, "image/png")},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("status_code") == 200:
                return result.get("image", {}).get("url")
    except Exception:
        pass

    # Try catbox.moe as fallback
    try:
        response = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": ("image.png", image_data, "image/png")},
            timeout=30
        )
        if response.status_code == 200 and response.text.startswith("http"):
            return response.text.strip()
    except Exception:
        pass

    # Try returning base64 encoded (some APIs support this)
    return f"data:image/png;base64,{base64.b64encode(image_data).decode()}"


def generate_video(
    image_path: str,
    prompt: str,
    output_path: str,
    segment: int
) -> bool:
    """
    Generate an 8-second video clip from a static image.

    Args:
        image_path: Path to source image
        prompt: Motion description prompt
        output_path: Where to save the generated video
        segment: Segment number (1-18) for logging

    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("Error: KIE_API_KEY not found in environment variables")
        return False

    print(f"Generating video for segment {segment:02d}")
    print(f"  Source: {image_path}")
    print(f"  Motion: {prompt[:80]}...")

    # Verify source image exists
    if not Path(image_path).exists():
        print(f"Error: Source image not found: {image_path}")
        return False

    # Upload image to get a URL
    print("  Uploading image...")
    image_url = upload_image_to_hosting(image_path)
    if not image_url:
        print("Error: Failed to upload image")
        return False

    # KIE.ai API endpoint for image-to-video
    url = "https://api.kie.ai/v1/videos/generations"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.5-pro",  # or "seedance-1.5-pro"
        "image_url": image_url,
        "prompt": prompt,
        "duration": 8,  # 8 seconds per segment
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "audio": False  # We generate audio separately
    }

    try:
        # Submit generation request
        print("  Submitting video generation request...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        result = response.json()
        task_id = result.get("task_id") or result.get("id")

        if not task_id:
            print(f"Error: No task ID in response: {result}")
            return False

        print(f"  Task ID: {task_id}")
        print("  Waiting for generation (this may take 5-8 minutes)...")

        # Poll for completion (up to 10 minutes)
        status_url = f"https://api.kie.ai/v1/videos/generations/{task_id}"

        for attempt in range(120):  # Max 10 minutes
            time.sleep(5)

            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_response.raise_for_status()

            status_data = status_response.json()
            status = status_data.get("status", "").lower()
            progress = status_data.get("progress", 0)

            if status == "completed" or status == "succeeded":
                video_url = status_data.get("output", {}).get("video_url")
                if not video_url:
                    video_url = status_data.get("video_url")
                if not video_url:
                    videos = status_data.get("data", [])
                    if videos:
                        video_url = videos[0].get("url")

                if video_url:
                    return download_video(video_url, output_path, segment)
                else:
                    print(f"Error: No video URL in response: {status_data}")
                    return False

            elif status == "failed" or status == "error":
                error_msg = status_data.get("error", "Unknown error")
                print(f"Error: Video generation failed - {error_msg}")
                return False

            if attempt % 12 == 0:  # Log every minute
                print(f"  Status: {status} | Progress: {progress}% | {attempt * 5}s elapsed")

        print("Error: Video generation timed out after 10 minutes")
        return False

    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed - {e}")
        return False


def download_video(url: str, output_path: str, segment: int) -> bool:
    """Download video from URL and save to disk."""
    try:
        print(f"  Downloading video...")

        # Create output directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"  Success! Segment {segment:02d} saved to {output_path} ({file_size:.1f} MB)")
        return True

    except Exception as e:
        print(f"Error downloading video: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate video clips from images using KIE.ai Kling 2.5 Pro"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to source image"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Motion description prompt"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output video file path"
    )
    parser.add_argument(
        "--segment",
        type=int,
        required=True,
        help="Segment number (1-18)"
    )

    args = parser.parse_args()

    if not 1 <= args.segment <= 18:
        print("Error: Segment must be between 1 and 18")
        sys.exit(1)

    success = generate_video(args.image, args.prompt, args.output, args.segment)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
