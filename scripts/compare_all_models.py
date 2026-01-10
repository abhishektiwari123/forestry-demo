#!/usr/bin/env python3
"""
Compare Kling AI 2.6, Veo 3.1, and Hailuo 2.3 on continuous frames.
Test complex segment to determine best model for final production.
"""

import os
import sys
import time
import requests
import json
import glob
from dotenv import load_dotenv

load_dotenv()


def upload_image(image_path: str) -> str:
    """Upload image with fallback services."""
    print(f"📤 Uploading {os.path.basename(image_path)}...")

    # Try imgcdn.dev first
    try:
        with open(image_path, 'rb') as f:
            response = requests.post(
                'https://imgcdn.dev/api/1/upload',
                data={'key': '5386e05a3562c7a8f984e73401540836', 'format': 'json'},
                files={'source': f},
                timeout=30
            )

        if response.status_code == 200:
            result = response.json()
            if result.get('status_code') == 200:
                url = result['image']['url']
                print(f"✅ Uploaded to imgcdn.dev")
                return url
    except Exception as e:
        print(f"⚠️  imgcdn.dev failed: {e}")

    # Try catbox.moe as fallback
    try:
        print(f"📤 Trying catbox.moe...")
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
                print(f"✅ Uploaded to catbox.moe")
                return url
    except Exception as e:
        print(f"⚠️  catbox.moe failed: {e}")

    raise Exception(f"Failed to upload {image_path}")


def test_kling(start_frame: str, prompt: str, output: str):
    """Test Kling AI 2.6 (5s, 2K quality)."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        return False, "No API key"

    print(f"\n{'='*60}")
    print(f"🎬 KLING AI 2.6 TEST")
    print(f"{'='*60}")

    try:
        image_url = upload_image(start_frame)
    except Exception as e:
        return False, f"Upload failed: {e}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "prompt": prompt,
            "image_urls": [image_url],
            "sound": False,
            "duration": "5"
        }
    }

    print(f"🚀 Submitting...")
    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return False, f"API Error: {response.status_code}"

    result = response.json()
    if result.get("code") != 200:
        return False, result.get('msg')

    task_id = result["data"]["taskId"]
    print(f"⏳ Generating... ", end="", flush=True)

    start_time = time.time()
    while time.time() - start_time < 600:
        time.sleep(10)
        print(f"{int(time.time() - start_time)}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            if data.get("state") == "success":
                print(f"\n✅ Generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                vid_resp = requests.get(video_url, stream=True)
                with open(output, 'wb') as f:
                    for chunk in vid_resp.iter_content(8192):
                        f.write(chunk)

                size_mb = os.path.getsize(output) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                return True, f"{size_mb:.2f}MB in {duration:.1f}s"

            elif data.get("state") == "fail":
                return False, data.get("failMsg")

    return False, "Timeout"


def test_veo3(start_frame: str, prompt: str, output: str, model="veo3_fast"):
    """Test Veo 3.1 (Fast or Quality)."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        return False, "No API key"

    print(f"\n{'='*60}")
    print(f"🎬 VEO 3.1 {model.upper()} TEST")
    print(f"{'='*60}")

    try:
        image_url = upload_image(start_frame)
    except Exception as e:
        return False, f"Upload failed: {e}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "imageUrls": [image_url],
        "model": model,
        "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO",
        "aspectRatio": "16:9",
        "enableTranslation": True
    }

    print(f"🚀 Submitting...")
    response = requests.post(
        "https://api.kie.ai/api/v1/veo/generate",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return False, f"API Error: {response.status_code}"

    result = response.json()
    if result.get("code") != 200:
        return False, result.get('msg')

    task_id = result["data"]["taskId"]
    print(f"⏳ Generating... ", end="", flush=True)

    start_time = time.time()
    while time.time() - start_time < 600:
        time.sleep(10)
        print(f"{int(time.time() - start_time)}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/veo/detail?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            if data.get("status") == "success":
                print(f"\n✅ Generated!")
                info = data.get("info", {})
                video_url = json.loads(info.get("resultUrls", "[]"))[0]

                vid_resp = requests.get(video_url, stream=True)
                with open(output, 'wb') as f:
                    for chunk in vid_resp.iter_content(8192):
                        f.write(chunk)

                size_mb = os.path.getsize(output) / (1024 * 1024)
                duration = time.time() - start_time
                resolution = info.get("resolution", "Unknown")
                print(f"✅ Saved: {size_mb:.2f} MB | {resolution} | Time: {duration:.1f}s")
                return True, f"{size_mb:.2f}MB {resolution} in {duration:.1f}s"

            elif data.get("status") == "fail":
                return False, data.get("msg")

    return False, "Timeout"


def test_hailuo(start_frame: str, prompt: str, output: str):
    """Test Hailuo 2.3 Pro (6s, 768P or 1080P)."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        return False, "No API key"

    print(f"\n{'='*60}")
    print(f"🎬 HAILUO 2.3 PRO TEST")
    print(f"{'='*60}")

    try:
        image_url = upload_image(start_frame)
    except Exception as e:
        return False, f"Upload failed: {e}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "hailuo/2-3-image-to-video-pro",
        "input": {
            "prompt": prompt,
            "image_url": image_url,
            "duration": "6",
            "resolution": "768P"  # or "1080P"
        }
    }

    print(f"🚀 Submitting...")
    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return False, f"API Error: {response.status_code}"

    result = response.json()
    if result.get("code") != 200:
        return False, result.get('msg')

    task_id = result["data"]["taskId"]
    print(f"⏳ Generating... ", end="", flush=True)

    start_time = time.time()
    while time.time() - start_time < 600:
        time.sleep(10)
        print(f"{int(time.time() - start_time)}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            if data.get("state") == "success":
                print(f"\n✅ Generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                vid_resp = requests.get(video_url, stream=True)
                with open(output, 'wb') as f:
                    for chunk in vid_resp.iter_content(8192):
                        f.write(chunk)

                size_mb = os.path.getsize(output) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"✅ Saved: {size_mb:.2f} MB | 768P | Time: {duration:.1f}s")
                return True, f"{size_mb:.2f}MB 768P in {duration:.1f}s"

            elif data.get("state") == "fail":
                return False, data.get("failMsg")

    return False, "Timeout"


def run_comprehensive_comparison(segment_num: int):
    """Test all models on a continuous frame segment."""
    start_frame = f"charizard/battle_assets/frame_pairs/seg{segment_num:02d}_continuous_start.jpg"

    if not os.path.exists(start_frame):
        print(f"❌ Start frame not found: {start_frame}")
        return

    # Use appropriate prompt for the segment
    prompts = {
        3: "Both dragons facing each other mid-air, Charizard and Dragonite circling slowly, sizing up opponent, wings beating steadily, building tension before battle begins",
        4: "Charizard roaring powerfully with battle cry, jaws opening wide, wings flaring dramatically, tail flame intensifying, preparing to attack",
        5: "Charizard unleashing massive Flamethrower attack, enormous flames erupting forward, wings bracing from recoil, heat distortion visible, devastating blast"
    }

    prompt = prompts.get(segment_num, "Pokemon battle scene, dynamic action, cinematic movement")

    print(f"\n🎯 COMPREHENSIVE MODEL COMPARISON")
    print(f"="*60)
    print(f"Segment: {segment_num}")
    print(f"Start Frame: {os.path.basename(start_frame)}")
    print(f"Prompt: {prompt}")
    print(f"="*60)

    results = {}

    # Test Kling AI
    output_kling = f"charizard/battle_assets/videos/seg{segment_num:02d}_compare_kling.mp4"
    results['kling'] = test_kling(start_frame, prompt, output_kling)
    time.sleep(5)

    # Test Veo 3 Fast
    output_veo_fast = f"charizard/battle_assets/videos/seg{segment_num:02d}_compare_veo3_fast.mp4"
    results['veo3_fast'] = test_veo3(start_frame, prompt, output_veo_fast, "veo3_fast")
    time.sleep(5)

    # Test Veo 3 Quality
    output_veo_quality = f"charizard/battle_assets/videos/seg{segment_num:02d}_compare_veo3_quality.mp4"
    results['veo3_quality'] = test_veo3(start_frame, prompt, output_veo_quality, "veo3")
    time.sleep(5)

    # Test Hailuo
    output_hailuo = f"charizard/battle_assets/videos/seg{segment_num:02d}_compare_hailuo.mp4"
    results['hailuo'] = test_hailuo(start_frame, prompt, output_hailuo)

    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 COMPARISON COMPLETE - SEGMENT {segment_num}")
    print(f"{'='*60}")

    for model, (success, info) in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {model.upper()}: {info}")

    print(f"\n📊 COMPARISON FILES:")
    for model, (success, _) in results.items():
        if success:
            filename = f"seg{segment_num:02d}_compare_{model}.mp4"
            print(f"  - {model.upper()}: {filename}")

    print(f"\n📝 EVALUATION CRITERIA:")
    print(f"  1. Motion smoothness")
    print(f"  2. Size consistency (Dragonite larger)")
    print(f"  3. Wing colors (orange tops, teal undersides)")
    print(f"  4. Physics realism")
    print(f"  5. Overall quality")
    print(f"  6. Generation speed")

    print(f"\n💡 Watch all 4 videos and choose best model for production!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare all models on continuous frames")
    parser.add_argument("--segment", type=int, choices=[3, 4, 5], required=True,
                        help="Segment to test (3=Faceoff, 4=Roar, 5=Flamethrower)")

    args = parser.parse_args()

    run_comprehensive_comparison(args.segment)
