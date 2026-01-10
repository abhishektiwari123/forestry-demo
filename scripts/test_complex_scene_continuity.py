#!/usr/bin/env python3
"""
Test video-to-video continuity with COMPLEX, VISUALLY DISTINCT scenes.

Scene 1: Segment 3 - Aerial clash with Flamethrower (high-speed combat)
Scene 2: Segment 13 - Fire Spin tornado + Seismic Toss (complex particle effects)

This tests if continuity works between two VERY DIFFERENT complex scenes.
"""

import os
import sys
import time
import requests
import json
import subprocess
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment
load_dotenv()

# Complex scene prompts (VERY DIFFERENT from each other)
COMPLEX_SCENES = {
    "scene1": {
        "name": "Aerial Clash + Flamethrower",
        "segment": 3,
        "prompt": "Epic aerial clash, Charizard (5'7\" fire dragon) launching massive orange Flamethrower stream, significantly larger Dragonite (7'3\", 30% bigger, bulkier body) barrel-rolling to evade, intense high-speed combat, fire trails streaming, wings with orange upper surface matching body color and teal turquoise (#58A8B8) underside membranes visible, dramatic action, smoke and flames, cinematic combat photography"
    },
    "scene2": {
        "name": "Fire Spin Tornado + Seismic Toss Grab",
        "segment": 13,
        "prompt": "Charizard (smaller 5'7\" fire dragon) creating massive swirling Fire Spin tornado with orange flames, significantly larger Dragonite (7'3\", 30% bigger, bulkier muscular body) bursting through flames grabbing Charizard for Seismic Toss, intense particle effects, fire vortex swirling, dramatic grab mid-tornado, wings with orange upper surface matching body color and teal turquoise (#58A8B8) underside membranes, explosive energy, cinematic VFX shot"
    }
}


def compress_image(image_path: str, max_size_mb: float = 5.0) -> str:
    """Compress image if needed."""
    size_mb = os.path.getsize(image_path) / (1024 * 1024)

    if size_mb <= max_size_mb:
        return image_path

    print(f"⚠️  Image too large ({size_mb:.2f} MB), compressing...")
    compressed = image_path.replace('.jpg', '_compressed.jpg')

    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', image_path,
            '-q:v', '5',
            '-vf', 'scale=\'min(1920,iw)\':\'min(1080,ih)\':force_original_aspect_ratio=decrease',
            compressed
        ], check=True, capture_output=True, timeout=30)

        new_size = os.path.getsize(compressed) / (1024 * 1024)
        print(f"✅ Compressed: {size_mb:.2f} MB → {new_size:.2f} MB")
        return compressed
    except Exception as e:
        print(f"⚠️  Compression failed: {e}, using original")
        return image_path


def upload_image(image_path: str) -> str:
    """Upload image to imgcdn.dev."""
    upload_path = compress_image(image_path, max_size_mb=5.0)

    print(f"📤 Uploading {os.path.basename(upload_path)}...")

    try:
        with open(upload_path, 'rb') as f:
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
                print(f"✅ Uploaded: {url}")
                return url
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        raise


def extract_last_frame(video_path: str, output_image: str) -> bool:
    """Extract last frame from video."""
    print(f"🎞️  Extracting last frame from {os.path.basename(video_path)}...")

    try:
        # Get duration
        duration_cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
        print(f"📏 Duration: {duration:.2f}s")

        # Extract last frame
        extract_time = max(0, duration - 0.04)
        extract_cmd = [
            'ffmpeg', '-y',
            '-ss', str(extract_time),
            '-i', video_path,
            '-frames:v', '1',
            '-q:v', '2',
            output_image
        ]

        subprocess.run(extract_cmd, check=True, capture_output=True)

        if os.path.exists(output_image):
            size_mb = os.path.getsize(output_image) / (1024 * 1024)
            print(f"✅ Extracted: {os.path.basename(output_image)} ({size_mb:.2f} MB)")
            return True
        return False
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False


def generate_start_frame(prompt: str, output_path: str, scene_name: str) -> bool:
    """Generate starting frame using Nano Banana Pro."""
    print(f"\n{'='*60}")
    print(f"🎨 GENERATING START FRAME: {scene_name}")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt[:100]}...")

    api_key = os.getenv("KIE_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "flux-pro/nano-banana-pro",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "output_format": "jpg"
        }
    }

    print("🚀 Submitting to Nano Banana Pro...")
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
    print(f"⏳ Generating... ", end="", flush=True)

    start_time = time.time()
    while time.time() - start_time < 300:
        time.sleep(5)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            if data.get("state") == "success":
                print(f" Done! ({int(time.time() - start_time)}s)")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Download
                img_resp = requests.get(image_url, timeout=30)
                if img_resp.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(img_resp.content)

                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"✅ Saved: {size_mb:.2f} MB")
                    return True

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print("\n❌ Timeout")
    return False


def generate_video_kling(image_path: str, prompt: str, output: str, scene_name: str) -> bool:
    """Generate video with Kling AI 2.6."""
    api_key = os.getenv("KIE_API_KEY")

    print(f"\n{'='*60}")
    print(f"🎬 GENERATING VIDEO: {scene_name}")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt[:100]}...")

    try:
        image_url = upload_image(image_path)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

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

    print("🚀 Submitting to Kling AI 2.6...")
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
    print(f"⏳ Generating... ", end="", flush=True)

    start_time = time.time()
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
                print(f"\n✅ Generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]
                print(f"📥 Downloading...")

                vid_resp = requests.get(video_url, stream=True, verify=False, timeout=120)
                if vid_resp.status_code == 200:
                    with open(output, 'wb') as f:
                        for chunk in vid_resp.iter_content(8192):
                            if chunk:
                                f.write(chunk)

                    size_mb = os.path.getsize(output) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                    return True
                else:
                    print(f"❌ Download failed: {vid_resp.status_code}")
                    return False

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print(f"\n❌ Timeout")
    return False


def test_complex_continuity():
    """Test continuity with complex, visually distinct scenes."""
    print("="*60)
    print("🎯 COMPLEX SCENE CONTINUITY TEST")
    print("="*60)
    print("\nTesting TWO VISUALLY DISTINCT complex scenes:")
    print(f"  Scene 1: {COMPLEX_SCENES['scene1']['name']}")
    print(f"  Scene 2: {COMPLEX_SCENES['scene2']['name']}")
    print("\nStrategy: Video-to-video continuity")
    print("="*60)

    base_path = "charizard/battle_assets"

    # Scene 1 paths
    scene1_start = f"{base_path}/frame_pairs/seg03_complex_start.jpg"
    scene1_video = f"{base_path}/videos/seg03_complex_test.mp4"
    scene1_extracted = f"{base_path}/frame_pairs/seg03_last_frame_extracted.jpg"

    # Scene 2 paths
    scene2_video = f"{base_path}/videos/seg13_complex_test.mp4"

    # STEP 1: Generate Scene 1 start frame
    print(f"\n{'='*60}")
    print("STEP 1: Generate Scene 1 Start Frame")
    print(f"{'='*60}")

    if not generate_start_frame(
        COMPLEX_SCENES["scene1"]["prompt"],
        scene1_start,
        COMPLEX_SCENES["scene1"]["name"]
    ):
        print("❌ Failed to generate Scene 1 start frame")
        return False

    # STEP 2: Generate Scene 1 video
    print(f"\n{'='*60}")
    print("STEP 2: Generate Scene 1 Video")
    print(f"{'='*60}")

    if not generate_video_kling(
        scene1_start,
        COMPLEX_SCENES["scene1"]["prompt"],
        scene1_video,
        COMPLEX_SCENES["scene1"]["name"]
    ):
        print("❌ Failed to generate Scene 1 video")
        return False

    # STEP 3: Extract last frame from Scene 1
    print(f"\n{'='*60}")
    print("STEP 3: Extract Last Frame from Scene 1")
    print(f"{'='*60}")

    if not extract_last_frame(scene1_video, scene1_extracted):
        print("❌ Failed to extract last frame")
        return False

    # STEP 4: Generate Scene 2 video using extracted frame
    print(f"\n{'='*60}")
    print("STEP 4: Generate Scene 2 Video from Extracted Frame")
    print(f"{'='*60}")
    print("⚠️  This is the KEY TEST:")
    print("   Scene 1 (aerial clash) → Scene 2 (fire tornado)")
    print("   VERY DIFFERENT scenes - will continuity work?")

    if not generate_video_kling(
        scene1_extracted,
        COMPLEX_SCENES["scene2"]["prompt"],
        scene2_video,
        COMPLEX_SCENES["scene2"]["name"]
    ):
        print("❌ Failed to generate Scene 2 video")
        return False

    # SUMMARY
    print(f"\n{'='*60}")
    print("🎉 COMPLEX SCENE CONTINUITY TEST COMPLETE!")
    print(f"{'='*60}")

    print("\n📊 GENERATED FILES:")
    print(f"  1. {os.path.basename(scene1_start)}")
    print(f"     → {COMPLEX_SCENES['scene1']['name']}")
    print(f"  2. {os.path.basename(scene1_video)}")
    print(f"     → Scene 1 video (aerial clash + Flamethrower)")
    print(f"  3. {os.path.basename(scene1_extracted)}")
    print(f"     → Extracted last frame from Scene 1")
    print(f"  4. {os.path.basename(scene2_video)}")
    print(f"     → Scene 2 video (Fire Spin tornado + Seismic Toss)")

    print("\n🎬 EVALUATION:")
    print("  Watch both videos in sequence:")
    print("    Scene 1 ending → Scene 2 beginning")
    print("    ⚠️  These are VERY DIFFERENT scenes!")
    print("    ✓ Does transition look natural?")
    print("    ✓ Is there visual continuity despite different actions?")
    print("    ✓ Does video-to-video approach handle complex scene changes?")

    print("\n💡 WHAT WE'RE TESTING:")
    print("  ✓ Aerial combat → Ground combat transition")
    print("  ✓ Simple fire → Complex particle effects")
    print("  ✓ High-speed action → Grab/grapple action")
    print("  ✓ Can continuity work between DISTINCT complex scenes?")

    print("\n✅ If successful, video-to-video continuity works for ALL scenes!")
    return True


if __name__ == "__main__":
    test_complex_continuity()
