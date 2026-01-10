#!/usr/bin/env python3
"""
Test complex scene continuity using EXISTING seg03 frame.
Generate two VERY DIFFERENT videos to test if continuity works.

Video 1: Aerial clash with Flamethrower (from existing seg03 frame)
Video 2: Fire Spin tornado + Seismic Toss (using extracted last frame from Video 1)
"""

import os
import time
import requests
import json
import subprocess
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()


def compress_image(image_path: str) -> str:
    """Compress image if >5MB."""
    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if size_mb <= 5.0:
        return image_path

    print(f"⚠️  Compressing {size_mb:.2f} MB image...")
    compressed = image_path.replace('.jpg', '_compressed.jpg')

    subprocess.run([
        'ffmpeg', '-y', '-i', image_path, '-q:v', '5',
        '-vf', 'scale=\'min(1920,iw)\':\'min(1080,ih)\':force_original_aspect_ratio=decrease',
        compressed
    ], check=True, capture_output=True, timeout=30)

    new_size = os.path.getsize(compressed) / (1024 * 1024)
    print(f"✅ Compressed: {size_mb:.2f} MB → {new_size:.2f} MB")
    return compressed


def upload_image(image_path: str) -> str:
    """Upload image."""
    path = compress_image(image_path)
    print(f"📤 Uploading {os.path.basename(path)}...")

    with open(path, 'rb') as f:
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
    raise Exception(f"Upload failed: {response.status_code}")


def extract_last_frame(video_path: str, output_image: str) -> bool:
    """Extract last frame."""
    print(f"🎞️  Extracting last frame...")

    duration_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    duration = float(subprocess.check_output(duration_cmd).decode().strip())

    extract_cmd = [
        'ffmpeg', '-y', '-ss', str(max(0, duration - 0.04)),
        '-i', video_path, '-frames:v', '1', '-q:v', '2', output_image
    ]
    subprocess.run(extract_cmd, check=True, capture_output=True)

    if os.path.exists(output_image):
        size_mb = os.path.getsize(output_image) / (1024 * 1024)
        print(f"✅ Extracted: {size_mb:.2f} MB")
        return True
    return False


def generate_video(image_path: str, prompt: str, output: str) -> bool:
    """Generate video with Kling AI 2.6."""
    api_key = os.getenv("KIE_API_KEY")

    print(f"\n{'='*60}")
    print(f"🎬 GENERATING: {os.path.basename(output)}")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt[:80]}...")

    image_url = upload_image(image_path)

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
                    print(f"✅ Saved: {size_mb:.2f} MB | {duration:.1f}s")
                    return True

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print("\n❌ Timeout")
    return False


def main():
    print("="*60)
    print("🎯 COMPLEX SCENE CONTINUITY TEST (SEG03)")
    print("="*60)
    print("\nVideo 1: Aerial clash + Flamethrower")
    print("Video 2: Fire Spin tornado + Seismic Toss (VERY DIFFERENT!)")
    print("\nStrategy: Video-to-video continuity")
    print("="*60)

    # Paths
    seg03_start = "charizard/battle_assets/frame_pairs/seg03_continuous_start.jpg"
    video1 = "charizard/battle_assets/videos/seg03_compare_kling.mp4"
    extracted = "charizard/battle_assets/frame_pairs/seg03_last_extracted.jpg"
    video2 = "charizard/battle_assets/videos/seg03_to_seg13_continuity.mp4"

    # Prompts - VERY DIFFERENT scenes
    prompt1 = "Epic aerial clash, Charizard (5'7\" fire dragon) launching massive orange Flamethrower stream at significantly larger Dragonite (7'3\", 30% bigger, bulkier body) barrel-rolling to evade, intense high-speed combat, fire trails streaming, wings with orange upper surface matching body color and teal turquoise underside membranes visible, dramatic action, smoke and flames"

    prompt2 = "Charizard (smaller 5'7\" fire dragon) creating massive swirling Fire Spin tornado with orange flames, significantly larger Dragonite (7'3\", 30% bigger, bulkier muscular body) bursting through flames grabbing Charizard for Seismic Toss, intense particle effects, fire vortex swirling, dramatic grab mid-tornado, wings with orange upper surface matching body color and teal turquoise underside membranes, explosive energy"

    # STEP 1: Generate Video 1
    print(f"\n{'='*60}")
    print("STEP 1: Generate Video 1 (Aerial Clash)")
    print(f"{'='*60}")

    if not generate_video(seg03_start, prompt1, video1):
        print("❌ Failed at Step 1")
        return

    # STEP 2: Extract last frame
    print(f"\n{'='*60}")
    print("STEP 2: Extract Last Frame from Video 1")
    print(f"{'='*60}")

    if not extract_last_frame(video1, extracted):
        print("❌ Failed at Step 2")
        return

    # STEP 3: Generate Video 2 with DIFFERENT prompt
    print(f"\n{'='*60}")
    print("STEP 3: Generate Video 2 (Fire Tornado - DIFFERENT SCENE!)")
    print(f"{'='*60}")
    print("⚠️  KEY TEST: Transition from aerial combat → fire tornado")

    if not generate_video(extracted, prompt2, video2):
        print("❌ Failed at Step 3")
        return

    # SUCCESS
    print(f"\n{'='*60}")
    print("🎉 COMPLEX SCENE CONTINUITY TEST COMPLETE!")
    print(f"{'='*60}")

    print("\n📊 GENERATED FILES:")
    print(f"  1. {os.path.basename(video1)}")
    print(f"     → Aerial clash + Flamethrower")
    print(f"  2. {os.path.basename(extracted)}")
    print(f"     → Extracted last frame from Video 1")
    print(f"  3. {os.path.basename(video2)}")
    print(f"     → Fire Spin tornado + Seismic Toss")

    print("\n🎬 CRITICAL EVALUATION:")
    print("  Watch videos in sequence:")
    print("  ✓ Video 1 ending → Video 2 beginning")
    print("  ✓ These are COMPLETELY DIFFERENT actions!")
    print("  ✓ Does continuity work despite scene change?")
    print("  ✓ Is transition visually smooth?")

    print("\n💡 IF THIS WORKS:")
    print("  ✅ Video-to-video continuity handles ANY scene transition")
    print("  ✅ Can proceed with full 18-segment generation")
    print("  ✅ Complex particle effects won't break continuity")


if __name__ == "__main__":
    main()
