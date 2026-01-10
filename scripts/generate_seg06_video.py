#!/usr/bin/env python3
"""
Generate video for validated Seg06 image using Kling AI 2.6.
"""

import os
import sys
import time
import requests
import json
import subprocess

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


def compress_and_upload_image(image_path):
    """Compress and upload image."""
    print(f"\n📤 Preparing image for upload...")

    # Check size
    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    print(f"Original size: {size_mb:.2f} MB")

    # Compress if needed
    if size_mb > 5:
        compressed = image_path.replace('.jpg', '_compressed.jpg')
        print(f"Compressing to under 5 MB...")
        subprocess.run([
            'ffmpeg', '-y', '-i', image_path,
            '-q:v', '6',
            '-vf', 'scale=\'min(1920,iw)\':\'min(1080,ih)\':force_original_aspect_ratio=decrease',
            compressed
        ], check=True, capture_output=True, timeout=30)

        upload_path = compressed
        size_mb = os.path.getsize(upload_path) / (1024 * 1024)
        print(f"Compressed size: {size_mb:.2f} MB")
    else:
        upload_path = image_path

    # Upload
    print(f"Uploading to imgcdn.dev...")
    with open(upload_path, 'rb') as f:
        response = requests.post(
            'https://imgcdn.dev/api/1/upload',
            data={'key': '5386e05a3562c7a8f984e73401540836', 'format': 'json'},
            files={'source': f},
            timeout=60
        )

    if response.status_code == 200:
        result = response.json()
        if result.get('status_code') == 200:
            url = result['image']['url']
            print(f"✅ Uploaded: {url}")
            return url

    raise Exception(f"Upload failed: {response.status_code}")


def generate_video(image_url, output_path, api_key):
    """Generate video with Kling AI 2.6."""
    print(f"\n{'='*70}")
    print("🎬 GENERATING VIDEO WITH KLING AI 2.6")
    print(f"{'='*70}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": [image_url],
            "prompt": "Dragonite barrel-rolling mid-air dodging flames, then immediately countering with Thunder Punch attack crackling with electricity, fast evasive maneuver to counter-attack, dynamic aerial combat, high-speed action, cinematic camera",
            "duration": "5",
            "sound": False
        }
    }

    print("🚀 Submitting to Kling AI 2.6...")
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return False

    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        return False

    task_id = result["data"]["taskId"]
    print(f"⏳ Generating video... ", end="", flush=True)

    while time.time() - start_time < 600:
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
                print(f"📥 Downloading video...")

                vid_resp = requests.get(video_url, timeout=120)
                if vid_resp.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(vid_resp.content)

                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                    return True

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print(f"\n❌ Timeout")
    return False


def main():
    print("="*70)
    print("SEG06 VIDEO GENERATION FROM VALIDATED IMAGE")
    print("="*70)

    api_key = load_api_key()

    image_path = "charizard/battle_assets/frame_pairs/seg06_continuous_start.jpg"
    output_path = "charizard/battle_assets/videos/seg06_dragonite_counters.mp4"

    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return 1

    # Upload image
    try:
        image_url = compress_and_upload_image(image_path)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return 1

    # Generate video
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    success = generate_video(image_url, output_path, api_key)

    if success:
        print(f"\n{'='*70}")
        print("🎉 SEG06 VIDEO GENERATION COMPLETE!")
        print(f"{'='*70}")
        print(f"\n✅ Video saved: {output_path}")
        print(f"\nNext: Extract frames and validate video")
    else:
        print(f"\n❌ Video generation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
