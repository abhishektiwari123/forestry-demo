#!/usr/bin/env python3
"""
Test and compare Kling AI 2.6 vs Seedance 1.5 Pro for Pokemon battle videos.

This script generates the same segment with both models to evaluate:
- Video quality
- Motion smoothness
- Prompt effectiveness
- Which model works best for different types of battle scenes
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Test with Segment 1 - Valley Patrol
# This is a good test case: smooth aerial motion, no complex physics
SEGMENT_TEST = {
    "number": 1,
    "name": "valley_patrol",
    "start_frame": "charizard/battle_assets/frame_pairs/seg01_valley_patrol_start.jpg",
    "end_frame": "charizard/battle_assets/frame_pairs/seg01_valley_patrol_end.jpg",

    # Seedance prompt (full scene description + motion)
    "seedance_prompt": "Charizard with vibrant orange body and teal turquoise wing membranes powerfully soaring over volcanic peaks at dawn, flying closer to camera smoothly, wings beating majestically, golden sunrise light illuminating scales, volcanic valley below, cinematic aerial tracking shot following the patrol flight",

    # Kling prompt (motion-focused, scene already in image)
    "kling_prompt": "Charizard soaring majestically over volcanic peaks, wings beating rhythmically, flying closer toward camera, cinematic aerial tracking shot following patrol flight"
}


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


def generate_with_kling(image_url: str, prompt: str, output_path: str, duration: str = "5"):
    """
    Generate video using Kling AI 2.6 Image-to-Video.

    Kling strengths:
    - Excellent camera motion
    - Realistic character physics
    - Motion-focused prompting
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found")
        return False

    print("\n🎬 KLING AI 2.6 TEST")
    print("=" * 60)
    print(f"📝 Prompt: {prompt}")
    print(f"⏱️  Duration: {duration}s")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "prompt": prompt,
            "image_urls": [image_url],
            "sound": False,  # We'll add audio separately
            "duration": duration  # "5" or "10"
        }
    }

    print(f"🚀 Submitting to Kling AI 2.6...")

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
    if result.get("code") != 200:
        print(f"❌ Task creation failed: {result.get('msg')}")
        return False

    task_id = result["data"]["taskId"]
    print(f"⏳ Task ID: {task_id}")
    print(f"⏳ Generating video...")
    print(f"   Elapsed: ", end="", flush=True)

    # Poll for completion
    max_wait = 600  # 10 minutes
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(10)
        elapsed += 10
        print(f"{elapsed}s ", end="", flush=True)

        status_response = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status_response.status_code != 200:
            continue

        status_data = status_response.json()
        if status_data.get("code") != 200:
            continue

        data = status_data.get("data", {})
        state = data.get("state")

        if state == "success":
            print(f"\n✅ Video generated!")

            result_json = json.loads(data["resultJson"])
            video_url = result_json["resultUrls"][0]

            print(f"📥 Downloading video...")
            video_response = requests.get(video_url, stream=True)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Saved: {output_path} ({file_size:.2f} MB)")
            print("=" * 60)
            return True

        elif state == "fail":
            print(f"\n❌ Generation failed: {data.get('failMsg')}")
            return False

    print(f"\n❌ Timeout after {max_wait}s")
    return False


def generate_with_seedance(start_url: str, end_url: str, prompt: str, output_path: str):
    """
    Generate video using Seedance 1.5 Pro (our current method).

    Seedance strengths:
    - Start + End frame interpolation
    - Smooth transitions between states
    - Full scene description prompting
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found")
        return False

    print("\n🎬 SEEDANCE 1.5 PRO TEST")
    print("=" * 60)
    print(f"📝 Prompt: {prompt[:100]}...")
    print(f"⏱️  Duration: 8s (fixed)")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "bytedance/seedance-1.5-pro",
        "input": {
            "prompt": prompt,
            "input_urls": [start_url, end_url],
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "duration": "8",
            "fixed_lens": False,
            "generate_audio": False
        }
    }

    print(f"🚀 Submitting to Seedance 1.5 Pro...")

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
        print(f"❌ Task creation failed: {result.get('msg')}")
        return False

    task_id = result["data"]["taskId"]
    print(f"⏳ Task ID: {task_id}")
    print(f"⏳ Generating video...")
    print(f"   Elapsed: ", end="", flush=True)

    # Poll for completion
    max_wait = 600
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(10)
        elapsed += 10
        print(f"{elapsed}s ", end="", flush=True)

        status_response = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status_response.status_code != 200:
            continue

        status_data = status_response.json()
        if status_data.get("code") != 200:
            continue

        data = status_data.get("data", {})
        state = data.get("state")

        if state == "success":
            print(f"\n✅ Video generated!")

            result_json = json.loads(data["resultJson"])
            video_url = result_json["resultUrls"][0]

            print(f"📥 Downloading video...")
            video_response = requests.get(video_url, stream=True)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Saved: {output_path} ({file_size:.2f} MB)")
            print("=" * 60)
            return True

        elif state == "fail":
            print(f"\n❌ Generation failed: {data.get('failMsg')}")
            return False

    print(f"\n❌ Timeout after {max_wait}s")
    return False


def run_comparison_test():
    """Run side-by-side comparison test."""
    print("🎯 KLING AI vs SEEDANCE COMPARISON TEST")
    print("=" * 60)
    print(f"Test Segment: {SEGMENT_TEST['number']} - {SEGMENT_TEST['name']}")
    print(f"Start Frame: {SEGMENT_TEST['start_frame']}")
    print(f"End Frame: {SEGMENT_TEST['end_frame']}")
    print("=" * 60)

    # Upload frames
    print("\n📤 Uploading test frames...")
    try:
        start_url = upload_image(SEGMENT_TEST['start_frame'])
        end_url = upload_image(SEGMENT_TEST['end_frame'])
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return

    # Output paths
    kling_output = f"charizard/battle_assets/videos/seg01_kling_test.mp4"
    seedance_output = f"charizard/battle_assets/videos/seg01_seedance_test.mp4"

    # Test Kling AI
    print("\n" + "=" * 60)
    print("TEST 1: KLING AI 2.6 (Image-to-Video)")
    print("=" * 60)
    kling_success = generate_with_kling(
        start_url,
        SEGMENT_TEST['kling_prompt'],
        kling_output,
        duration="5"
    )

    # Test Seedance
    print("\n" + "=" * 60)
    print("TEST 2: SEEDANCE 1.5 PRO (Start + End Frame)")
    print("=" * 60)
    seedance_success = generate_with_seedance(
        start_url,
        end_url,
        SEGMENT_TEST['seedance_prompt'],
        seedance_output
    )

    # Results
    print("\n" + "=" * 60)
    print("🎉 COMPARISON TEST COMPLETE!")
    print("=" * 60)

    if kling_success:
        print(f"✅ Kling AI: {kling_output}")
        print(f"   Duration: 5s")
        print(f"   Prompt Style: Motion-focused")
    else:
        print(f"❌ Kling AI: Failed")

    if seedance_success:
        print(f"✅ Seedance: {seedance_output}")
        print(f"   Duration: 8s")
        print(f"   Prompt Style: Full scene description")
    else:
        print(f"❌ Seedance: Failed")

    print("\n📊 EVALUATION CRITERIA:")
    print("Compare both videos for:")
    print("  1. Motion smoothness and realism")
    print("  2. Character animation quality")
    print("  3. Camera work effectiveness")
    print("  4. Overall cinematic feel")
    print("  5. Color and lighting consistency")

    print("\n💡 NEXT STEPS:")
    print("  1. Watch both videos side-by-side")
    print("  2. Note which aspects each model handles better")
    print("  3. Consider using Kling for aerial/motion scenes")
    print("  4. Consider using Seedance for action transitions")
    print("  5. Update batch script with preferred model")


if __name__ == "__main__":
    run_comparison_test()
