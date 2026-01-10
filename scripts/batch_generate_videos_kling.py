#!/usr/bin/env python3
"""
Batch generate all 18 battle story videos using Kling AI 2.6 Image-to-Video.

Based on quality analysis, Kling AI produces better results for:
- Camera motion and tracking
- Character physics
- Motion smoothness
- Cinematic feel
"""

import os
import sys
import time
import requests
import json
import glob
from dotenv import load_dotenv

load_dotenv()

# Kling AI optimized prompts - Motion-focused (30-50 words)
# Structure: Subject + Primary Action + Camera Movement
KLING_PROMPTS = {
    1: "Charizard soaring majestically over volcanic peaks, wings beating rhythmically, flying closer toward camera, cinematic aerial tracking shot following patrol flight",

    2: "Dragonite descending powerfully from storm clouds, wings spreading wide as it approaches valley, lightning crackling in background, dramatic low angle emphasizing power",

    3: "Charizard and Dragonite circling each other mid-air, wings beating steadily, sizing up opponent with intense focus, camera slowly orbits maintaining both dragons in frame",

    4: "Charizard roaring powerfully with battle cry, jaws opening wide, wing membranes flaring dramatically, tail flame intensifying from orange to blue, dramatic close-up pulling back to reveal stance",

    5: "Charizard unleashing massive Flamethrower, enormous flames erupting forward from open jaws, wings bracing from recoil, heat distortion rippling through air, side angle capturing blast intensity",

    6: "Dragonite barrel-rolling rapidly to evade flames, wings tucking aerodynamically then spreading wide for Thunder Punch counter, fast tracking shot following evasive maneuver",

    7: "Charizard struck by Thunder Punch, electricity crackling violently across body, grimacing and reeling from impact but staying airborne, handheld camera conveying chaos",

    8: "Charizard shaking off damage powerfully, wings beating with renewed strength, regaining altitude determinedly, dramatic upward angle showing triumphant recovery",

    9: "Both dragons charging Dragon Rage energy in mouths, blue-purple energy building intensely then releasing simultaneously, beams colliding mid-air in violent explosion, wide shot capturing collision",

    10: "Charizard bursting dramatically through smoke cloud, wings spread wide, orange scales glowing, emerging with tactical focus toward opponent, slow-motion revealing opportunity",

    11: "Charizard accelerating rapidly into steep dive, wings tucking tight, tail flame streaming behind in speed blur, volcanic valley approaching fast, following shot capturing escalating velocity",

    12: "Charizard grabbing Dragonite mid-air, both dragons beginning to spin together rapidly, wings intertwining, volcanic valley rotating below, rotating camera around grappling Pokemon",

    13: "Charizard spinning rapidly while ascending skyward, holding Dragonite firmly, spiraling upward violently, building massive momentum for throw, spiraling camera following ascent dramatically",

    14: "Charizard releasing Dragonite with explosive force, hurling rival straight down toward valley, Dragonite plummeting rapidly, massive dust explosion upon impact, following descent then impact",

    15: "Charizard gliding down gracefully from altitude, wings spread wide, tail flame returning to normal, descending peacefully toward crater, aerial shot following victorious descent",

    16: "Dragonite rising slowly from crater, extending arm in warrior salute, Charizard nodding respectfully, mutual acknowledgment between former rivals, ground level emotional shot",

    17: "Multiple Charizards perched on peaks roaring approval, wings spreading in celebration, breathing fire upward triumphantly, valley alive with celebration, wide pan revealing community",

    18: "Charizard and Dragonite flying side by side toward sunset, wings glowing in sunset light, peaceful flight together, camera slowly pulling back revealing epic scale"
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


def generate_video_kling(segment_num: int, duration: str = "5"):
    """Generate video for a specific segment using Kling AI 2.6."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found in .env")
        return False

    # Find start frame only (Kling uses single image + motion description)
    start_frame = f"charizard/battle_assets/frame_pairs/seg{segment_num:02d}_*_start.jpg"
    start_files = glob.glob(start_frame)

    if not start_files:
        print(f"❌ Start frame not found for segment {segment_num}")
        return False

    start_frame = start_files[0]
    prompt = KLING_PROMPTS[segment_num]
    output = f"charizard/battle_assets/videos/seg{segment_num:02d}_video.mp4"

    print(f"\n🎬 Generating Video: Segment {segment_num} (KLING AI 2.6)")
    print(f"━" * 60)
    print(f"📝 Prompt: {prompt}")
    print(f"⏱️  Duration: {duration}s")

    # Upload start frame
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
            "sound": False,  # We'll add audio separately
            "duration": duration  # "5" or "10"
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

    print(f"\n❌ Timeout after {max_wait}s")
    return False


def batch_generate_all(start_from=1, duration="5"):
    """Generate videos for all segments using Kling AI."""
    print("🎬 BATCH VIDEO GENERATION: KLING AI 2.6")
    print("=" * 60)
    print(f"Total segments: 18")
    print(f"Starting from: Segment {start_from}")
    print(f"Duration: {duration}s per video")
    print(f"Estimated time: 40-60 minutes")
    print("=" * 60)

    success_count = 0
    failed_segments = []

    for seg_num in range(start_from, 19):
        result = generate_video_kling(seg_num, duration)

        if result:
            success_count += 1
            print(f"✅ Progress: {success_count}/{18 - start_from + 1} complete")
        else:
            failed_segments.append(seg_num)
            print(f"❌ Failed: Segment {seg_num}")

        # Brief pause between segments
        if seg_num < 18:
            time.sleep(2)

    print(f"\n{'=' * 60}")
    print(f"🎉 BATCH GENERATION COMPLETE!")
    print(f"✅ Success: {success_count}/{18 - start_from + 1}")
    print(f"❌ Failed: {len(failed_segments)}")

    if failed_segments:
        print(f"Failed segments: {failed_segments}")
        print(f"\nTo retry:")
        print(f"  python scripts/batch_generate_videos_kling.py --start-from {failed_segments[0]}")
    else:
        print(f"\n🎊 ALL VIDEOS GENERATED SUCCESSFULLY WITH KLING AI!")
        print(f"Next step: Compare quality with Seedance versions")
        print(f"Then: Sync audio and assemble documentary")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch generate battle videos with Kling AI 2.6")
    parser.add_argument("--segment", type=int, help="Generate specific segment only")
    parser.add_argument("--start-from", type=int, default=1, help="Start from segment number")
    parser.add_argument("--duration", type=str, default="5", choices=["5", "10"], help="Video duration (5s or 10s)")
    parser.add_argument("--all", action="store_true", help="Generate all 18 videos")

    args = parser.parse_args()

    if args.segment:
        if args.segment < 1 or args.segment > 18:
            print("❌ Error: Segment must be between 1 and 18")
            sys.exit(1)
        generate_video_kling(args.segment, args.duration)
    elif args.all:
        batch_generate_all(args.start_from, args.duration)
    else:
        print("Usage:")
        print("  --segment N       Generate video for segment N")
        print("  --all             Generate all 18 videos")
        print("  --start-from N    Start from segment N (with --all)")
        print("  --duration D      Duration: 5 or 10 seconds (default: 5)")
        print("\nExample: python scripts/batch_generate_videos_kling.py --all --duration 5")
        print("Example: python scripts/batch_generate_videos_kling.py --segment 1 --duration 10")
