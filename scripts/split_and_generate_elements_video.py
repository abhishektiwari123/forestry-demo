#!/usr/bin/env python3
"""
Split 4-panel image into 4 separate images and generate 10s video using Kling Elements API.

Usage:
    python3 split_and_generate_elements_video.py <4_panel_image_path>
"""

import os
import sys
import requests
import json
import time
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


def split_4_panel_image(image_path: str, output_dir: str) -> list:
    """
    Split a 4-panel image into 4 separate images.
    Assumes 2x2 grid layout (top-left, top-right, bottom-left, bottom-right).

    Returns:
        List of 4 image file paths
    """
    print(f"\n📸 Splitting 4-panel image: {image_path}")

    # Open the image
    img = Image.open(image_path)
    width, height = img.size

    # Calculate dimensions for each panel (2x2 grid)
    panel_width = width // 2
    panel_height = height // 2

    os.makedirs(output_dir, exist_ok=True)

    panels = []
    positions = [
        (0, 0, panel_width, panel_height),              # Top-left
        (panel_width, 0, width, panel_height),          # Top-right
        (0, panel_height, panel_width, height),         # Bottom-left
        (panel_width, panel_height, width, height)      # Bottom-right
    ]

    for i, box in enumerate(positions, 1):
        panel = img.crop(box)
        panel_path = os.path.join(output_dir, f"panel_{i}.jpg")
        panel.save(panel_path, "JPEG", quality=95)
        panels.append(panel_path)
        print(f"  ✅ Panel {i}: {panel_path} ({panel.size[0]}x{panel.size[1]})")

    print(f"✅ Split into 4 panels")
    return panels


def upload_image(image_path: str) -> str:
    """Upload image to CDN and return URL."""
    print(f"📤 Uploading: {os.path.basename(image_path)}...")

    with open(image_path, 'rb') as f:
        response = requests.post(
            'https://imgcdn.dev/api/1/upload',
            data={'key': '5386e05a3562c7a8f984e73401540836', 'format': 'json'},
            files={'source': f},
            timeout=60
        )

    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.status_code}")

    result = response.json()
    if result.get('status_code') != 200:
        raise Exception("Upload failed")

    image_url = result['image']['url']
    print(f"  ✅ Uploaded: {image_url}")
    return image_url


def generate_video_from_elements(image_urls: list, prompt: str, api_key: str) -> str:
    """
    Generate 10s video using Kling Elements API with multiple images.

    Args:
        image_urls: List of 2-4 image URLs
        prompt: Text prompt for video generation
        api_key: KIE API key

    Returns:
        Path to generated video file
    """
    print(f"\n{'='*70}")
    print(f"GENERATING 10S VIDEO FROM {len(image_urls)} IMAGES (KLING ELEMENTS)")
    print(f"{'='*70}")
    print(f"\n📝 Video Prompt:")
    print(f"{prompt}")
    print(f"\n🎨 Input Images: {len(image_urls)}")
    for i, url in enumerate(image_urls, 1):
        print(f"  {i}. {url}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Kling Elements API uses multiple image_urls
    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": image_urls,  # Multiple images for Elements feature
            "prompt": prompt,
            "duration": "10",
            "sound": True
        }
    }

    print(f"\n🚀 Submitting to Kling 2.6 Elements...")
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    result = response.json()
    if result.get("code") != 200:
        raise Exception(f"Failed: {result.get('msg')}")

    task_id = result["data"]["taskId"]
    print(f"⏳ Generating... ", end="", flush=True)

    while time.time() - start_time < 300:
        time.sleep(10)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            if data.get("state") == "success":
                print(f"\n✅ Video generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                output_path = "charizard/battle_assets/videos/elements_4panel_10s.mp4"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                vid_resp = requests.get(video_url, timeout=120)
                if vid_resp.status_code != 200:
                    raise Exception(f"Video download failed: {vid_resp.status_code}")

                with open(output_path, 'wb') as f:
                    f.write(vid_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                print(f"📁 Location: {output_path}")

                # Save task ID
                with open(output_path.replace('.mp4', '_task_id.txt'), 'w') as f:
                    f.write(task_id)

                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Main function."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║          KLING ELEMENTS: 4-PANEL IMAGE TO VIDEO                    ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  This script:                                                      ║
║  1. Splits a 4-panel image into 4 separate images                 ║
║  2. Uploads all 4 images to CDN                                    ║
║  3. Uses Kling Elements API to generate a cohesive 10s video      ║
║                                                                    ║
║  The Elements feature maintains character/scene consistency        ║
║  across all 4 reference images in the generated video.            ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    if len(sys.argv) < 2:
        print("❌ Usage: python3 split_and_generate_elements_video.py <4_panel_image_path>")
        print("\nExample:")
        print("  python3 split_and_generate_elements_video.py charizard/battle_assets/4panel_sequence.jpg")
        return 1

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return 1

    api_key = load_api_key()

    # Step 1: Split 4-panel image into 4 separate images
    output_dir = "charizard/battle_assets/split_panels"
    panel_paths = split_4_panel_image(image_path, output_dir)

    # Step 2: Upload all 4 panels
    print(f"\n📤 Uploading 4 panels...")
    image_urls = []
    for panel_path in panel_paths:
        url = upload_image(panel_path)
        image_urls.append(url)

    # Step 3: Generate video using Kling Elements with all 4 images
    prompt = """Complete Pokemon battle sequence showing Charizard Flamethrower attack hitting Dragonite causing damage, burn marks appearing, Dragonite's expression changing from pain to fierce anger, and Dragonite charging forward aggressively toward Charizard for revenge counter-attack. Both Pokemon visible throughout with smooth progression, dramatic battle intensity, realistic physics, volcanic valley background, cinematic action"""

    video_path = generate_video_from_elements(image_urls, prompt, api_key)

    print(f"\n🎉 Success!")
    print(f"📊 Generated 10-second video from 4 images")
    print(f"📁 Video: {video_path}")
    print(f"📁 Panels: {output_dir}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
