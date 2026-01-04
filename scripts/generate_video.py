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

def upload_image(image_path: str) -> str:
    """
    Upload image to get public URL. Tries multiple services.

    Args:
        image_path: Path to image file

    Returns:
        Public URL of uploaded image
    """
    import base64

    # Try catbox.moe first
    try:
        print(f"📤 Uploading image to catbox.moe...")
        with open(image_path, 'rb') as f:
            response = requests.post(
                'https://catbox.moe/user/api.php',
                data={'reqtype': 'fileupload'},
                files={'fileToUpload': f},
                timeout=30
            )

        if response.status_code == 200:
            url = response.text.strip()
            if url.startswith('http'):
                print(f"✅ Uploaded to catbox: {url}")
                return url
    except Exception as e:
        print(f"⚠️  Catbox upload failed: {e}")

    # Try imgbb.com as backup
    try:
        print(f"📤 Trying imgbb.com...")
        with open(image_path, 'rb') as f:
            image_b64 = base64.b64encode(f.read()).decode('utf-8')

        response = requests.post(
            'https://api.imgbb.com/1/upload',
            data={
                'key': '7abd1e5ee53456c45ee1e0f0e8a04bc3',  # Public key
                'image': image_b64
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            url = result['data']['url']
            print(f"✅ Uploaded to imgbb: {url}")
            return url
    except Exception as e:
        print(f"⚠️  Imgbb upload failed: {e}")

    raise Exception("Failed to upload image to any service")

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
        image_url = upload_image(image_path)

        # Submit video generation request to KIE.ai
        print(f"🚀 Submitting to Kling API...")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # KIE.ai API for image-to-video (Seedance 1.5 Pro)
        payload = {
            "model": "bytedance/seedance-1.5-pro",
            "input": {
                "prompt": prompt,
                "input_urls": [image_url],  # Array of image URLs (0-2 images)
                "aspect_ratio": "16:9",  # For documentary format
                "resolution": "720p",  # High quality
                "duration": "8",  # 8 seconds per clip
                "fixed_lens": False,  # Allow camera movement as specified in prompts
                "generate_audio": False  # We have our own narration
            }
        }

        # Submit generation request
        response = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        result = response.json()

        # Check for successful task creation
        if result.get("code") != 200:
            print(f"❌ Task creation failed: {result.get('msg', 'Unknown error')}")
            return False

        # Get task ID
        task_id = result.get("data", {}).get("taskId")
        if not task_id:
            print(f"❌ No task ID returned")
            return False

        print(f"⏳ Task ID: {task_id}")
        print(f"⏳ Waiting for video generation (typically 5-8 minutes)...")

        # Poll for completion
        max_attempts = 120  # 10 minutes max
        attempt = 0

        while attempt < max_attempts:
            time.sleep(5)
            attempt += 1

            # Check status
            status_response = requests.get(
                f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                headers=headers,
                timeout=30
            )

            if status_response.status_code != 200:
                continue

            status_data = status_response.json()

            if status_data.get("code") != 200:
                continue

            data = status_data.get("data", {})
            state = data.get("state")

            if state == "success":
                # Parse result JSON to get video URL
                import json
                result_json = json.loads(data.get("resultJson", "{}"))
                result_urls = result_json.get("resultUrls", [])

                if result_urls:
                    video_url = result_urls[0]
                    print(f"✅ Video generated!")
                    print(f"📥 Downloading from: {video_url}")

                    # Download video
                    video_response = requests.get(video_url, timeout=60)
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)

                    print(f"✅ Video saved to: {output_path}")
                    return True
                else:
                    print(f"❌ No video URLs in result")
                    return False

            elif state == "fail":
                print(f"❌ Video generation failed")
                print(f"Error Code: {data.get('failCode', 'Unknown')}")
                print(f"Error Message: {data.get('failMsg', 'Unknown error')}")
                return False

            elif state == "waiting":
                # Still processing
                if attempt % 12 == 0:  # Every minute
                    print(f"⏳ Still processing... ({attempt * 5}s elapsed)")
            else:
                print(f"⚠️  Unknown state: {state}")

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
