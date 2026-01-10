#!/usr/bin/env python3
"""
Test video-to-video continuity strategy:
1. Generate Scene N video from frame pair
2. Extract LAST FRAME from generated video
3. Use extracted frame as FIRST FRAME for Scene N+1
4. Generate Scene N+1 video from extracted frame
5. Compare continuity between actual video outputs
"""

import os
import sys
import time
import requests
import json
import subprocess
from dotenv import load_dotenv
import urllib3

# Disable SSL warnings since we're using verify=False for download
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()


def compress_image_if_needed(image_path: str, max_size_mb: float = 5.0) -> str:
    """Compress image if it exceeds max_size_mb."""
    size_mb = os.path.getsize(image_path) / (1024 * 1024)

    if size_mb <= max_size_mb:
        return image_path

    print(f"⚠️  Image too large ({size_mb:.2f} MB), compressing...")

    # Create compressed version
    compressed_path = image_path.replace('.jpg', '_compressed.jpg')

    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', image_path,
            '-q:v', '5',  # Quality 5 (good balance)
            '-vf', 'scale=\'min(1920,iw)\':\'min(1080,ih)\':force_original_aspect_ratio=decrease',
            compressed_path
        ], check=True, capture_output=True, timeout=30)

        new_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
        print(f"✅ Compressed: {size_mb:.2f} MB → {new_size_mb:.2f} MB")
        return compressed_path

    except Exception as e:
        print(f"⚠️  Compression failed: {e}, using original")
        return image_path


def upload_image(image_path: str) -> str:
    """Upload image with fallback services."""
    # Compress if needed
    upload_path = compress_image_if_needed(image_path, max_size_mb=5.0)

    print(f"📤 Uploading {os.path.basename(upload_path)}...")

    # Try imgcdn.dev first
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
                print(f"✅ Uploaded to imgcdn.dev")
                return url
    except Exception as e:
        print(f"⚠️  imgcdn.dev failed: {e}")

    # Try catbox.moe as fallback
    try:
        print(f"📤 Trying catbox.moe...")
        with open(upload_path, 'rb') as f:
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

    raise Exception(f"Failed to upload {upload_path}")


def extract_last_frame(video_path: str, output_image: str) -> bool:
    """Extract the last frame from a video using ffmpeg."""
    print(f"\n🎞️  Extracting last frame from {os.path.basename(video_path)}...")

    try:
        # Get video duration
        duration_cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        duration = float(subprocess.check_output(duration_cmd).decode().strip())
        print(f"📏 Video duration: {duration:.2f}s")

        # Extract frame at duration-0.04s (last frame before end)
        extract_time = max(0, duration - 0.04)

        extract_cmd = [
            'ffmpeg', '-y',
            '-ss', str(extract_time),
            '-i', video_path,
            '-frames:v', '1',
            '-q:v', '2',  # High quality
            output_image
        ]

        subprocess.run(extract_cmd, check=True, capture_output=True)

        if os.path.exists(output_image):
            size_mb = os.path.getsize(output_image) / (1024 * 1024)
            print(f"✅ Extracted last frame: {os.path.basename(output_image)} ({size_mb:.2f} MB)")
            return True
        else:
            print(f"❌ Failed to extract frame")
            return False

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False


def generate_video_kling(start_frame: str, prompt: str, output: str) -> bool:
    """Generate video with Kling AI 2.6."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ No API key")
        return False

    print(f"\n{'='*60}")
    print(f"🎬 GENERATING VIDEO: {os.path.basename(output)}")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt}")

    try:
        image_url = upload_image(start_frame)
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

    print(f"🚀 Submitting to Kling AI 2.6...")
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
                print(f"📥 Downloading from: {video_url[:50]}...")

                vid_resp = requests.get(video_url, stream=True, verify=False, timeout=120)
                if vid_resp.status_code == 200:
                    with open(output, 'wb') as f:
                        for chunk in vid_resp.iter_content(8192):
                            if chunk:
                                f.write(chunk)

                    size_mb = os.path.getsize(output) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")

                    if size_mb < 1:
                        print(f"⚠️  Warning: Video file seems too small ({size_mb:.2f} MB)")
                        return False

                    return True
                else:
                    print(f"❌ Download failed: HTTP {vid_resp.status_code}")
                    return False

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print(f"\n❌ Timeout")
    return False


def test_video_continuity():
    """
    Test video-to-video continuity:
    - Generate Seg 1 video
    - Extract last frame from Seg 1
    - Use as start for Seg 2
    - Generate Seg 2 video
    - Compare continuity
    """
    print("🎯 VIDEO-TO-VIDEO CONTINUITY TEST")
    print("="*60)
    print("Strategy: Extract last frame from Video N → Start of Video N+1")
    print("Test: Segments 1 → 2")
    print("="*60)

    # Prompts for video generation
    prompts = {
        1: "Charizard soaring majestically over volcanic peaks, wings beating rhythmically, flying closer toward camera, cinematic aerial tracking shot following patrol flight",
        2: "Charizard noticing dark shadow, looking up alertly, larger Dragonite descending from storm clouds, tension building, camera following gaze upward"
    }

    # STEP 1: Generate Segment 1 video
    seg1_start = "charizard/battle_assets/frame_pairs/seg01_continuous_start.jpg"
    seg1_video = "charizard/battle_assets/videos/seg01_video_continuity_test.mp4"

    print(f"\n{'='*60}")
    print(f"STEP 1: Generate Segment 1 Video")
    print(f"{'='*60}")

    if not generate_video_kling(seg1_start, prompts[1], seg1_video):
        print(f"❌ Failed to generate Segment 1 video")
        return False

    # STEP 2: Extract last frame from Segment 1 video
    seg1_last_extracted = "charizard/battle_assets/frame_pairs/seg01_last_frame_extracted.jpg"

    print(f"\n{'='*60}")
    print(f"STEP 2: Extract Last Frame from Segment 1")
    print(f"{'='*60}")

    if not extract_last_frame(seg1_video, seg1_last_extracted):
        print(f"❌ Failed to extract last frame")
        return False

    # STEP 3: Generate Segment 2 video using extracted frame
    seg2_video = "charizard/battle_assets/videos/seg02_video_continuity_test.mp4"

    print(f"\n{'='*60}")
    print(f"STEP 3: Generate Segment 2 Video from Extracted Frame")
    print(f"{'='*60}")

    if not generate_video_kling(seg1_last_extracted, prompts[2], seg2_video):
        print(f"❌ Failed to generate Segment 2 video")
        return False

    # STEP 4: Summary
    print(f"\n{'='*60}")
    print(f"🎉 VIDEO-TO-VIDEO CONTINUITY TEST COMPLETE!")
    print(f"{'='*60}")

    print(f"\n📊 GENERATED FILES:")
    print(f"  1. {os.path.basename(seg1_video)} - Segment 1 video")
    print(f"  2. {os.path.basename(seg1_last_extracted)} - Extracted last frame")
    print(f"  3. {os.path.basename(seg2_video)} - Segment 2 video (starts from extracted frame)")

    print(f"\n🎬 CONTINUITY EVALUATION:")
    print(f"  Watch both videos in sequence:")
    print(f"    - Seg 1 ending → Seg 2 beginning should be seamless")
    print(f"    - No visual jumps or discontinuities")
    print(f"    - Smooth transition using actual video output")

    print(f"\n💡 COMPARISON:")
    print(f"  IMAGE-TO-IMAGE: Use generated end image as next start image")
    print(f"  VIDEO-TO-VIDEO: Extract actual video last frame as next start")
    print(f"  → Video-to-video may provide better continuity since it uses")
    print(f"     the actual AI-generated video output, not input images")

    print(f"\n✅ If continuity is excellent, use this approach for all 18 segments!")

    return True


if __name__ == "__main__":
    test_video_continuity()
