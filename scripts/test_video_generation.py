#!/usr/bin/env python3
"""
Test video generation using start + end frame pairs with Seedance 1.5 Pro.
Following guide best practices for frame-to-frame video generation.
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def upload_image(image_path: str, service_name: str = "imgcdn") -> str:
    """Upload image and return public URL with fallback services."""
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
                print(f"✅ Uploaded to imgcdn.dev: {url}")
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
                print(f"✅ Uploaded to catbox.moe: {url}")
                return url
    except Exception as e:
        print(f"⚠️  catbox.moe failed: {e}")

    raise Exception(f"Failed to upload {image_path} to any service")

def generate_video_from_frames(start_frame: str, end_frame: str, prompt: str, output_path: str, segment_name: str):
    """
    Generate video using start + end frame technique.

    Per guide: "Provide start frame and end frame where only subject changes,
    while entire environment remains same. AI will smoothly transition between them."
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found in .env")
        sys.exit(1)

    print(f"\n🎬 Generating Video: {segment_name}")
    print(f"━" * 60)

    # Upload both frames
    start_url = upload_image(start_frame)
    end_url = upload_image(end_frame)

    print(f"\n📝 Motion Prompt:")
    print(f"   {prompt}")
    print(f"\n🚀 Submitting to Seedance 1.5 Pro API...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Seedance 1.5 Pro payload with start + end frames
    payload = {
        "model": "bytedance/seedance-1.5-pro",
        "input": {
            "prompt": prompt,
            "input_urls": [start_url, end_url],  # Start + End frame technique
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "duration": "8",  # 8 seconds per segment (Seedance supported duration)
            "fixed_lens": False,  # Allow camera movement
            "generate_audio": False
        }
    }

    # Submit generation request
    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

    result = response.json()

    if result.get("code") != 200:
        print(f"❌ Task creation failed: {result.get('msg', 'Unknown error')}")
        sys.exit(1)

    task_id = result["data"]["taskId"]
    print(f"⏳ Task ID: {task_id}")
    print(f"⏳ Generating video (typically 3-5 minutes)...")
    print(f"   Elapsed: ", end="", flush=True)

    # Poll for completion
    max_wait = 600  # 10 minutes max
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
            print(f"\n✅ Video generated successfully!")

            # Download video
            result_json = json.loads(data["resultJson"])
            video_url = result_json["resultUrls"][0]

            print(f"📥 Downloading from: {video_url}")

            video_response = requests.get(video_url, stream=True)
            with open(output_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Saved to: {output_path}")
            print(f"📊 File size: {file_size:.2f} MB")
            print(f"━" * 60)
            return True

        elif state == "failed":
            print(f"\n❌ Video generation failed")
            print(f"Error: {data.get('message', 'Unknown error')}")
            return False

    print(f"\n❌ Timeout after {max_wait}s")
    return False


if __name__ == "__main__":
    # Test with Segment 5: Flamethrower Attack
    # This is the most visually spectacular sequence

    print("🔥 SEGMENT 5 TEST: FLAMETHROWER ATTACK")
    print("=" * 60)

    START_FRAME = "charizard/battle_assets/frame_pairs/seg05_flamethrower_start.jpg"
    END_FRAME = "charizard/battle_assets/frame_pairs/seg05_flamethrower_end.jpg"
    OUTPUT = "charizard/battle_assets/videos/seg05_flamethrower_test.mp4"

    # Prompt following guide structure: [Subject] + [Motion + Intensity] + [Camera]
    # Per guide: Use intensity adverbs, specify teal wings ALWAYS
    PROMPT = """
    Charizard with vibrant orange body and teal turquoise wing membranes
    powerfully unleashing massive Flamethrower attack, jaws opening wide
    as enormous stream of orange-yellow flames erupts violently forward,
    wings bracing back from intense recoil force, volcanic valley background
    with dramatic storm clouds, heat distortion rippling through the air,
    fixed camera capturing the devastating fire blast from side angle,
    cinematic action intensity
    """.strip().replace('\n', ' ')

    # Ensure output directory exists
    os.makedirs("charizard/battle_assets/videos", exist_ok=True)

    # Generate video
    success = generate_video_from_frames(
        start_frame=START_FRAME,
        end_frame=END_FRAME,
        prompt=PROMPT,
        output_path=OUTPUT,
        segment_name="Segment 5: Flamethrower Attack"
    )

    if success:
        print(f"\n🎉 TEST SUCCESSFUL!")
        print(f"Next steps:")
        print(f"  1. Review video quality and character consistency")
        print(f"  2. If good: generate remaining 11 frame pairs")
        print(f"  3. If issues: adjust prompts and retry")
    else:
        print(f"\n❌ Test failed. Check API status and try again.")
