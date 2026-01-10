#!/usr/bin/env python3
"""
Test complex video generation with Veo 3.1 (Quality and Fast models).
Compare with Kling AI for action-heavy scenes with physics/effects.
"""

import os
import sys
import time
import requests
import json
import glob
from dotenv import load_dotenv

load_dotenv()

# Test complex scenes only
COMPLEX_SCENES = {
    5: {
        "name": "Flamethrower Attack",
        "prompt": "Charizard unleashing massive Flamethrower attack, enormous stream of flames erupting violently forward from open jaws, wings bracing from recoil force, heat distortion rippling through air, side angle capturing devastating blast intensity",
        "complexity": "High - Fire particles, heat distortion, recoil physics"
    },
    7: {
        "name": "Thunder Punch Impact",
        "prompt": "Charizard struck by Thunder Punch, electricity crackling violently across orange body and teal wing membranes, grimacing and reeling from impact but staying airborne, handheld camera conveying chaos of the hit",
        "complexity": "High - Electricity effects, impact physics, body reaction"
    },
    9: {
        "name": "Dragon Rage Collision",
        "prompt": "Both dragons charging Dragon Rage energy in mouths, blue-purple energy building intensely then releasing simultaneously, powerful energy beams colliding mid-air in violent explosion, wide shot capturing collision scale",
        "complexity": "Very High - Energy beams, collision, explosion, dual subjects"
    },
    13: {
        "name": "Seismic Toss Spin",
        "prompt": "Charizard spinning rapidly while ascending skyward, holding Dragonite firmly, spiraling upward violently through clouds, building massive momentum for legendary throw, spiraling camera following ascent dramatically",
        "complexity": "Very High - Rotation, dual subjects, complex camera work"
    },
    14: {
        "name": "Seismic Toss Impact",
        "prompt": "Charizard releasing Dragonite with explosive force, hurling rival straight down toward valley floor, Dragonite plummeting rapidly, massive dust explosion erupting upon crater impact, following descent then impact",
        "complexity": "Very High - Physics, falling motion, dust explosion"
    }
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


def generate_with_veo3(segment_num: int, model: str = "veo3_fast", output_suffix: str = ""):
    """
    Generate video using Veo 3.1 (Quality or Fast).

    Veo 3.1 strengths:
    - High resolution (1080p native)
    - Good with complex physics
    - Audio included by default
    - Fast model is cost-efficient
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found in .env")
        return False

    scene = COMPLEX_SCENES[segment_num]

    # Find start frame
    start_frame = f"charizard/battle_assets/frame_pairs/seg{segment_num:02d}_*_start.jpg"
    start_files = glob.glob(start_frame)

    if not start_files:
        print(f"❌ Start frame not found for segment {segment_num}")
        return False

    start_frame = start_files[0]
    prompt = scene["prompt"]
    output = f"charizard/battle_assets/videos/seg{segment_num:02d}_veo3{output_suffix}.mp4"

    print(f"\n🎬 Generating Video: Segment {segment_num} (VEO 3.1 {model.upper()})")
    print(f"━" * 60)
    print(f"📝 Scene: {scene['name']}")
    print(f"📝 Complexity: {scene['complexity']}")
    print(f"📝 Prompt: {prompt}")
    print(f"🤖 Model: {model}")

    # Upload image
    try:
        image_url = upload_image(start_frame)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

    print(f"🚀 Submitting to Veo 3.1 API...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "imageUrls": [image_url],
        "model": model,  # "veo3" or "veo3_fast"
        "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO",
        "aspectRatio": "16:9",
        "enableTranslation": True  # Auto-translate prompts to English
    }

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

        # Query task status
        status_response = requests.get(
            f"https://api.kie.ai/api/v1/veo/detail?taskId={task_id}",
            headers=headers
        )

        if status_response.status_code != 200:
            continue

        status_data = status_response.json()
        if status_data.get("code") != 200:
            continue

        data = status_data.get("data", {})
        state = data.get("status")

        if state == "success":
            print(f"\n✅ Video generated!")

            info = data.get("info", {})
            result_urls = json.loads(info.get("resultUrls", "[]"))

            if not result_urls:
                print(f"❌ No video URL in response")
                return False

            video_url = result_urls[0]

            print(f"📥 Downloading video...")
            video_response = requests.get(video_url, stream=True)

            os.makedirs("charizard/battle_assets/videos", exist_ok=True)
            with open(output, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(output) / (1024 * 1024)
            resolution = info.get("resolution", "Unknown")
            print(f"✅ Saved: {output} ({file_size:.2f} MB)")
            print(f"📺 Resolution: {resolution}")
            print(f"━" * 60)
            return True

        elif state == "fail":
            print(f"\n❌ Generation failed: {data.get('msg')}")
            return False

    print(f"\n❌ Timeout after {max_wait}s")
    return False


def generate_with_kling(segment_num: int, output_suffix: str = ""):
    """Generate with Kling AI for comparison."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found")
        return False

    scene = COMPLEX_SCENES[segment_num]

    start_frame = f"charizard/battle_assets/frame_pairs/seg{segment_num:02d}_*_start.jpg"
    start_files = glob.glob(start_frame)

    if not start_files:
        print(f"❌ Start frame not found")
        return False

    start_frame = start_files[0]
    prompt = scene["prompt"]
    output = f"charizard/battle_assets/videos/seg{segment_num:02d}_kling{output_suffix}.mp4"

    print(f"\n🎬 Generating Video: Segment {segment_num} (KLING AI 2.6)")
    print(f"━" * 60)
    print(f"📝 Scene: {scene['name']}")
    print(f"📝 Complexity: {scene['complexity']}")
    print(f"📝 Prompt: {prompt}")

    try:
        image_url = upload_image(start_frame)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

    print(f"🚀 Submitting to Kling AI 2.6...")

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

            os.makedirs("charizard/battle_assets/videos", exist_ok=True)
            with open(output, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(output) / (1024 * 1024)
            print(f"✅ Saved: {output} ({file_size:.2f} MB)")
            print(f"━" * 60)
            return True

        elif state == "fail":
            print(f"\n❌ Generation failed: {data.get('failMsg')}")
            return False

    print(f"\n❌ Timeout")
    return False


def run_comprehensive_test(segment_num: int):
    """Test all three models on a complex scene."""
    print("🎯 COMPREHENSIVE MODEL COMPARISON TEST")
    print("=" * 60)
    print(f"Testing Segment {segment_num}: {COMPLEX_SCENES[segment_num]['name']}")
    print(f"Complexity: {COMPLEX_SCENES[segment_num]['complexity']}")
    print("=" * 60)

    results = {}

    # Test Kling AI
    print("\n" + "=" * 60)
    print("TEST 1: KLING AI 2.6")
    print("=" * 60)
    results['kling'] = generate_with_kling(segment_num, "_test")

    # Wait between tests
    time.sleep(5)

    # Test Veo 3.1 Fast
    print("\n" + "=" * 60)
    print("TEST 2: VEO 3.1 FAST")
    print("=" * 60)
    results['veo3_fast'] = generate_with_veo3(segment_num, "veo3_fast", "_fast_test")

    # Wait between tests
    time.sleep(5)

    # Test Veo 3.1 Quality
    print("\n" + "=" * 60)
    print("TEST 3: VEO 3.1 QUALITY")
    print("=" * 60)
    results['veo3_quality'] = generate_with_veo3(segment_num, "veo3", "_quality_test")

    # Results summary
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TEST COMPLETE!")
    print("=" * 60)

    for model, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {model.upper()}: {'Success' if success else 'Failed'}")

    print("\n📊 COMPARISON FILES:")
    if results.get('kling'):
        print(f"  - Kling AI: seg{segment_num:02d}_kling_test.mp4")
    if results.get('veo3_fast'):
        print(f"  - Veo 3.1 Fast: seg{segment_num:02d}_veo3_fast_test.mp4")
    if results.get('veo3_quality'):
        print(f"  - Veo 3.1 Quality: seg{segment_num:02d}_veo3_quality_test.mp4")

    print("\n📝 EVALUATION CRITERIA:")
    print("  1. Particle effects quality (fire, electricity, energy)")
    print("  2. Physics realism (movement, impacts, reactions)")
    print("  3. Motion smoothness")
    print("  4. Detail preservation in action")
    print("  5. Overall cinematic quality")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test complex video generation with multiple models")
    parser.add_argument("--segment", type=int, choices=[5, 7, 9, 13, 14], required=True,
                        help="Complex segment to test (5=Flamethrower, 7=Thunder, 9=Collision, 13=Spin, 14=Impact)")
    parser.add_argument("--all-models", action="store_true",
                        help="Test all models (Kling, Veo Fast, Veo Quality)")
    parser.add_argument("--model", choices=["kling", "veo3_fast", "veo3_quality"],
                        help="Test specific model only")

    args = parser.parse_args()

    if args.all_models:
        run_comprehensive_test(args.segment)
    elif args.model == "kling":
        generate_with_kling(args.segment, "_test")
    elif args.model == "veo3_fast":
        generate_with_veo3(args.segment, "veo3_fast", "_fast_test")
    elif args.model == "veo3_quality":
        generate_with_veo3(args.segment, "veo3", "_quality_test")
    else:
        print("Error: Must specify --all-models or --model")
        sys.exit(1)
