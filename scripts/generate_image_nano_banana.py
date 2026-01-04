#!/usr/bin/env python3
"""
Generate images using Nano Banana Pro model via KIE.ai API.
"""

import argparse
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_image(prompt: str, output_path: str, aspect_ratio="16:9", resolution="4K"):
    """Generate image using Nano Banana Pro."""

    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Create task
    print(f"🎨 Generating image with Nano Banana Pro...")
    print(f"📝 Prompt: {prompt[:100]}...")

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "image_input": [],
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "output_format": "jpg"
        }
    }

    print(f"🚀 Submitting to KIE.ai API...")
    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return False

    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Task creation failed: {result.get('msg')}")
        return False

    task_id = result["data"]["taskId"]
    print(f"⏳ Task ID: {task_id}")
    print(f"⏳ Waiting for image generation...")

    # Poll for completion
    max_wait = 300  # 5 minutes
    elapsed = 0
    poll_interval = 5

    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval

        status_response = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers,
            timeout=30
        )

        if status_response.status_code != 200:
            print(f"❌ Status check failed: {status_response.status_code}")
            continue

        status_data = status_response.json()
        if status_data.get("code") != 200:
            print(f"❌ Status error: {status_data.get('msg')}")
            return False

        state = status_data["data"]["state"]

        if state == "success":
            print(f"✅ Image generated!")

            # Parse result
            import json
            result_json = json.loads(status_data["data"]["resultJson"])
            image_url = result_json["resultUrls"][0]

            # Download
            print(f"📥 Downloading from: {image_url}")
            img_response = requests.get(image_url, timeout=60)

            if img_response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"✅ Image saved to: {output_path}")
                return True
            else:
                print(f"❌ Failed to download image")
                return False

        elif state == "fail":
            fail_msg = status_data["data"].get("failMsg", "Unknown error")
            print(f"❌ Generation failed: {fail_msg}")
            return False

        elif state == "waiting":
            if elapsed % 15 == 0:
                print(f"⏳ Still processing... ({elapsed}s elapsed)")

    print(f"❌ Timeout: Image generation took too long")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate image with Nano Banana Pro')
    parser.add_argument('--prompt', required=True, help='Image generation prompt')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--aspect-ratio', default='16:9', help='Aspect ratio (default: 16:9)')
    parser.add_argument('--resolution', default='4K', help='Resolution: 1K, 2K, or 4K (default: 4K)')

    args = parser.parse_args()

    success = generate_image(args.prompt, args.output, args.aspect_ratio, args.resolution)
    exit(0 if success else 1)
