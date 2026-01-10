#!/usr/bin/env python3
"""
Compare Kling Elements API vs Sora 2 Pro Storyboard API for multi-image video generation.

Uses existing progression images:
- Stage 2: Flames hitting Dragonite with pain (2.8MB)
- Stage 3: Dragonite with burn marks, angry (2.7MB)
"""

import os
import sys
import requests
import json
import time


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


def upload_image(image_path: str) -> str:
    """Upload image to CDN."""
    print(f"  📤 Uploading: {os.path.basename(image_path)}...")

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
    print(f"    ✅ {image_url}")
    return image_url


def test_kling_elements(image_urls: list, api_key: str) -> str:
    """Test Kling Elements API with multiple images."""
    print(f"\n{'='*70}")
    print(f"TEST 1: KLING ELEMENTS API (Multi-Image Input)")
    print(f"{'='*70}")
    print(f"Images: {len(image_urls)}")
    print(f"Duration: 10 seconds")
    print(f"Feature: Maintains character consistency across reference images")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = "Complete Pokemon battle showing flames striking Dragonite causing pain and knockback, then burn marks appearing with Dragonite's expression changing to fierce anger, smooth progression, dramatic intensity, realistic physics"

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": image_urls,  # Multiple images
            "prompt": prompt,
            "duration": "10",
            "sound": True
        }
    }

    print(f"\n🚀 Submitting to Kling Elements...")
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
    print(f"Task ID: {task_id}")
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
                print(f"\n✅ Complete!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                output_path = "charizard/battle_assets/videos/test_kling_elements.mp4"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                vid_resp = requests.get(video_url, timeout=120)
                with open(output_path, 'wb') as f:
                    f.write(vid_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                print(f"📁 {output_path}")
                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def test_sora_storyboard(image_urls: list, api_key: str) -> str:
    """Test Sora 2 Pro Storyboard API with multiple images."""
    print(f"\n{'='*70}")
    print(f"TEST 2: SORA 2 PRO STORYBOARD API (Multi-Image Input)")
    print(f"{'='*70}")
    print(f"Images: {len(image_urls)}")
    print(f"Duration: 15 seconds")
    print(f"Feature: Storyboard-based video generation from image sequence")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sora-2-pro-storyboard",
        "input": {
            "n_frames": "15",  # 15 seconds
            "image_urls": image_urls,  # Multiple images
            "aspect_ratio": "landscape"
        }
    }

    print(f"\n🚀 Submitting to Sora 2 Pro Storyboard...")
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
    print(f"Task ID: {task_id}")
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
                print(f"\n✅ Complete!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                output_path = "charizard/battle_assets/videos/test_sora_storyboard.mp4"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                vid_resp = requests.get(video_url, timeout=120)
                with open(output_path, 'wb') as f:
                    f.write(vid_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                print(f"📁 {output_path}")
                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Main comparison test."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           KLING ELEMENTS vs SORA STORYBOARD COMPARISON            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Testing both APIs with the same 2 progression images:            ║
║  - Stage 2: Flames hitting Dragonite with pain                    ║
║  - Stage 3: Dragonite with burn marks, angry                      ║
║                                                                    ║
║  Comparing:                                                        ║
║  1. Kling Elements: 10s video with character consistency          ║
║  2. Sora Storyboard: 15s storyboard-based video                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Use existing progression images (Stage 2 & 3 are good quality)
    print(f"📤 Uploading progression images...")
    image_paths = [
        "charizard/battle_assets/progression/stage2_impact.jpg",
        "charizard/battle_assets/progression/stage3_anger.jpg"
    ]

    image_urls = []
    for path in image_paths:
        if os.path.exists(path):
            url = upload_image(path)
            image_urls.append(url)
        else:
            print(f"  ⚠️  Not found: {path}")

    if len(image_urls) < 2:
        print(f"\n❌ Need at least 2 images")
        return 1

    print(f"\n✅ {len(image_urls)} images uploaded")

    # Test 1: Kling Elements
    try:
        kling_video = test_kling_elements(image_urls, api_key)
        print(f"\n✅ Kling Elements: SUCCESS")
    except Exception as e:
        print(f"\n❌ Kling Elements: {e}")
        kling_video = None

    # Test 2: Sora 2 Pro Storyboard
    try:
        sora_video = test_sora_storyboard(image_urls, api_key)
        print(f"\n✅ Sora Storyboard: SUCCESS")
    except Exception as e:
        print(f"\n❌ Sora Storyboard: {e}")
        sora_video = None

    # Summary
    print(f"\n{'='*70}")
    print(f"COMPARISON RESULTS")
    print(f"{'='*70}")

    if kling_video:
        print(f"✅ Kling Elements: {kling_video}")
        print(f"   Duration: 10s | Character consistency focus")

    if sora_video:
        print(f"✅ Sora Storyboard: {sora_video}")
        print(f"   Duration: 15s | Storyboard-based generation")

    print(f"\n📊 Both APIs support multi-image input")
    print(f"📊 Kling Elements: Optimized for character consistency")
    print(f"📊 Sora Storyboard: Optimized for storyboard sequences")

    return 0


if __name__ == "__main__":
    sys.exit(main())
