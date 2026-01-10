#!/usr/bin/env python3
"""
Test Veo 3.1 First-Last Frame to Video Generation
Using KIE API for smooth transitions between photorealistic Pokemon frames
"""

import os
import sys
import time
import requests
import json

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


def upload_image_to_cdn(image_path):
    """Upload image to imgcdn.dev and return URL."""
    print(f"📤 Uploading {os.path.basename(image_path)}...")

    with open(image_path, 'rb') as f:
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


def generate_veo31_video(first_frame_url, last_frame_url, prompt, output_path, api_key):
    """Generate video using Veo 3.1 first-last frame mode."""
    print(f"\n{'='*70}")
    print("🎬 VEO 3.1 - FIRST & LAST FRAME TO VIDEO")
    print(f"{'='*70}")
    print(f"\n📝 Prompt: {prompt[:150]}...")
    print(f"\n🖼️  First Frame: {first_frame_url}")
    print(f"🖼️  Last Frame: {last_frame_url}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "imageUrls": [first_frame_url, last_frame_url],
        "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO",
        "model": "veo3_fast",
        "aspectRatio": "16:9",
        "seeds": 42000  # Consistent seed for reproducibility
    }

    print("\n🚀 Submitting to Veo 3.1...")
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/veo/generate",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return False

    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        return False

    task_id = result["data"]["taskId"]
    print(f"⏳ Generating video... Task ID: {task_id}")
    print(f"⏳ Progress: ", end="", flush=True)

    # Poll for completion (Veo 3.1 can take 2-5 minutes)
    while time.time() - start_time < 600:  # 10 min timeout
        time.sleep(15)  # Check every 15s
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/veo/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            state = data.get("state")

            if state == "success":
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

            elif state == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print(f"\n❌ Timeout after {int(time.time() - start_time)}s")
    return False


def main():
    print("="*70)
    print("VEO 3.1 FIRST-LAST FRAME TEST")
    print("="*70)
    print("\nTest: Generate smooth transition between two photorealistic frames")
    print("="*70)

    api_key = load_api_key()

    # Test Case: Seg03 to Seg05 transition
    # Seg03 end = face-off complete
    # Seg05 start = Charizard launching Flamethrower

    # For this test, we'll use existing images or need to specify paths
    # Let's test with Seg03 photorealistic version

    print("\n📋 TEST CONFIGURATION")
    print("Scenario: Charizard transitioning from stance to Flamethrower attack")
    print("First Frame: Seg03 photorealistic (face-off)")
    print("Last Frame: Seg05 start (Flamethrower charging)")
    print()

    # Check if test images exist
    first_frame_path = "charizard/battle_assets/test_results/seg03_nanobanana_photorealistic.jpg"

    # For last frame, we'll use Seg05 if it exists, otherwise note for manual test
    # Let's check what we have
    if not os.path.exists(first_frame_path):
        print(f"❌ First frame not found: {first_frame_path}")
        print("\nPlease ensure photorealistic Seg03 test image exists")
        print("Run: python3 scripts/test_nanobanana_photorealistic.py")
        return 1

    # Since we may not have Seg05 yet, let's create a test that uses
    # the same image twice but with different prompt to test the API
    print(f"✅ Found first frame: {first_frame_path}")
    print(f"\n⚠️  Note: Using same image for both frames to test API")
    print("In production, use actual start/end frames from adjacent segments")

    last_frame_path = first_frame_path  # Same for API test

    try:
        # Upload both frames
        print(f"\n{'='*70}")
        print("STEP 1: UPLOAD FRAMES TO CDN")
        print(f"{'='*70}")
        first_url = upload_image_to_cdn(first_frame_path)
        last_url = first_url  # Same for test

        # Generate video
        print(f"\n{'='*70}")
        print("STEP 2: GENERATE VIDEO WITH VEO 3.1")
        print(f"{'='*70}")

        prompt = """Photorealistic CGI: Orange dragon with teal wings transitions from battle-ready stance to launching massive orange-red Flamethrower stream from mouth, flames building and releasing, dramatic lighting, volcanic valley background, realistic reptilian scales, cinematic action, smooth motion"""

        output_path = "charizard/battle_assets/test_results/veo31_first_last_test.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        success = generate_veo31_video(
            first_url,
            last_url,
            prompt,
            output_path,
            api_key
        )

        if success:
            print(f"\n{'='*70}")
            print("🎉 VEO 3.1 TEST COMPLETE!")
            print(f"{'='*70}")
            print(f"\n✅ Video saved: {output_path}")
            print(f"\nValidation Steps:")
            print(f"1. Watch video - does it smoothly transition?")
            print(f"2. Check frame interpolation quality")
            print(f"3. Verify photorealistic quality maintained")
            print(f"4. Compare to Kling 2.6 videos for quality/smoothness")
            print(f"\nNext: If successful, use for all segment transitions!")
        else:
            print(f"\n❌ Video generation failed")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
