#!/usr/bin/env python3
"""
Generate video clips from images using KIE.ai Kling 2.5 Pro API.

Usage:
    python generate_video.py --image "composite.jpg" --prompt "Motion description" --output "video.mp4" --segment 1
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

def upload_to_catbox(image_path: str) -> str:
    """
    Upload image to catbox.moe for public URL.

    Args:
        image_path: Path to image file

    Returns:
        Public URL of uploaded image
    """
    print(f"📤 Uploading image to catbox.moe...")

    with open(image_path, 'rb') as f:
        response = requests.post(
            'https://catbox.moe/user/api.php',
            data={'reqtype': 'fileupload'},
            files={'fileToUpload': f}
        )

    if response.status_code == 200:
        url = response.text.strip()
        print(f"✅ Uploaded: {url}")
        return url
    else:
        raise Exception(f"Failed to upload to catbox: {response.status_code}")

def generate_video(image_path: str, prompt: str, output_path: str, segment_num: int) -> bool:
    """
    Generate video from image using KIE.ai Kling API.

    Args:
        image_path: Path to source image
        prompt: Motion prompt for video generation
        output_path: Where to save generated video
        segment_num: Segment number for logging

    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found in environment variables")
        print("Please set it in scripts/.env")
        return False

    try:
        print(f"\n🎬 Generating video for Segment {segment_num}")
        print(f"📝 Motion prompt: {prompt[:100]}...")

        # Upload image to get public URL
        image_url = upload_to_catbox(image_path)

        # Submit video generation request to KIE.ai
        print(f"🚀 Submitting to Kling API...")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Note: This is a template. Adjust based on actual KIE.ai API specification
        payload = {
            "model": "kling-2.5-pro",
            "image_url": image_url,
            "prompt": prompt,
            "duration": 10,  # 10 seconds (non-configurable for Kling)
            "aspect_ratio": "16:9"
        }

        # Submit generation request
        response = requests.post(
            "https://api.kie.ai/v1/video/generate",  # Placeholder URL
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        result = response.json()
        task_id = result.get("task_id")

        if not task_id:
            print(f"❌ No task ID received")
            return False

        print(f"⏳ Task ID: {task_id}")
        print(f"⏳ Waiting for video generation (typically 5-8 minutes)...")

        # Poll for completion
        max_attempts = 120  # 10 minutes max
        attempt = 0

        while attempt < max_attempts:
            time.sleep(5)  # Check every 5 seconds
            attempt += 1

            # Check status
            status_response = requests.get(
                f"https://api.kie.ai/v1/video/status/{task_id}",
                headers=headers
            )

            if status_response.status_code != 200:
                continue

            status_data = status_response.json()
            status = status_data.get("status")

            if status == "completed":
                video_url = status_data.get("video_url")
                print(f"✅ Video generated!")
                print(f"📥 Downloading from: {video_url}")

                # Download video
                video_response = requests.get(video_url)
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, 'wb') as f:
                    f.write(video_response.content)

                print(f"✅ Video saved to: {output_path}")
                return True

            elif status == "failed":
                print(f"❌ Video generation failed")
                print(f"Error: {status_data.get('error', 'Unknown error')}")
                return False

            else:
                # Still processing
                if attempt % 12 == 0:  # Every minute
                    print(f"⏳ Still processing... ({attempt * 5}s elapsed)")

        print(f"❌ Timeout: Video generation took too long")
        return False

    except Exception as e:
        print(f"❌ Error generating video: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate video clips using KIE.ai Kling 2.5 Pro"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Source image path (composite or single asset)"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Motion prompt following priority hierarchy"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output video path (e.g., '../haunter/videos/segment_01.mp4')"
    )
    parser.add_argument(
        "--segment",
        type=int,
        required=True,
        help="Segment number (1-18)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Note: This script uses placeholder KIE.ai API endpoints.")
    print("Please replace with actual KIE.ai Kling API specification.")
    print("Check KIE.ai documentation for correct endpoints and parameters.")
    print("=" * 70)

    success = generate_video(args.image, args.prompt, args.output, args.segment)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
