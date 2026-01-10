#!/usr/bin/env python3
"""
Download image from task_id and check if it's a 4-panel image.
"""

import os
import sys
import requests
import json
from PIL import Image


def load_api_key():
    """Load API key from .env file."""
    env_paths = ['.env', '/home/user/forestry-demo/.env', 'scripts/.env']
    for path in env_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('KIE_API_KEY='):
                        return line.strip().split('=', 1)[1]
    raise Exception("❌ KIE_API_KEY not found")


def get_and_download_image(task_id: str, api_key: str, output_path: str):
    """Get image URL from task_id and download it."""
    print(f"📥 Fetching image for task: {task_id}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json().get("data", {})
        if data.get("state") == "success":
            result_json = json.loads(data["resultJson"])
            image_url = result_json["resultUrls"][0]
            print(f"✅ Image URL: {image_url}")

            # Download image
            print(f"📥 Downloading image...")
            img_resp = requests.get(image_url, timeout=60)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(img_resp.content)

            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Downloaded: {size_mb:.2f} MB")
            print(f"📁 Location: {output_path}")
            return output_path

    raise Exception(f"Failed to get image for task {task_id}")


def analyze_image(image_path: str):
    """Analyze if image appears to be a 4-panel split screen."""
    img = Image.open(image_path)
    width, height = img.size

    print(f"\n📊 Image Analysis:")
    print(f"  Resolution: {width}x{height}")
    print(f"  Aspect Ratio: {width/height:.2f}:1")
    print(f"  Format: {img.format}")

    # Check if it looks like a 4-panel (roughly square or 2:1 ratio)
    aspect = width / height
    if 0.9 <= aspect <= 1.1:
        print(f"  ✅ Looks like a 4-panel image (2x2 grid)")
        return True
    elif 1.8 <= aspect <= 2.2:
        print(f"  ✅ Might be a 4-panel image (horizontal layout)")
        return True
    else:
        print(f"  ℹ️  Single image (not 4-panel grid)")
        return False


if __name__ == "__main__":
    task_id = sys.argv[1] if len(sys.argv) > 1 else "f7c5a8ae62acbd21d68e3bf258758f11"

    api_key = load_api_key()
    output_path = "charizard/battle_assets/temp_downloaded_image.jpg"

    # Download image
    image_path = get_and_download_image(task_id, api_key, output_path)

    # Analyze if it's 4-panel
    is_4panel = analyze_image(image_path)

    if is_4panel:
        print(f"\n✅ This appears to be a 4-panel image!")
        print(f"📝 You can now run:")
        print(f"   python3 scripts/split_and_generate_elements_video.py {image_path}")
    else:
        print(f"\nℹ️  This is a single image, not a 4-panel grid.")
        print(f"💡 To use the 4-panel script, you need a 2x2 grid image with 4 sequential frames.")
