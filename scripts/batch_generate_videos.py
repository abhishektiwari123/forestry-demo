#!/usr/bin/env python3
"""
Batch generate all 18 battle story videos from frame pairs using Seedance 1.5 Pro.
Based on successful test_video_generation.py workflow.
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Video generation prompts for all 18 segments
# Structure: [Subject] + [Motion with Intensity] + [Camera] per guide
SEGMENT_PROMPTS = {
    1: "Charizard with vibrant orange body and teal turquoise wing membranes powerfully soaring over volcanic peaks at dawn, flying closer to camera smoothly, wings beating majestically, golden sunrise light illuminating scales, volcanic valley below, cinematic aerial tracking shot following the patrol flight",

    2: "Dark ominous shadow rapidly descending from storm clouds, Dragonite with orange body and green wings emerging powerfully through lightning, approaching volcanic valley with determination, storm energy crackling intensely, dramatic descent revealing the challenger, low angle cinematic shot",

    3: "Charizard with teal wing membranes and Dragonite circling each other slowly mid-air, sizing up opponent with intense focus, both dragons hovering face to face, steam rising from Charizard dramatically, pre-battle tension building palpably, volcanic valley backdrop, cinematic circling camera keeping both Pokemon in frame",

    4: "Charizard roaring powerfully with battle challenge, jaws opening wide fiercely, teal wing membranes flaring dramatically outward, tail flame intensifying brilliantly to blue, accepting the challenge with determination, storm clouds gathering ominously, dramatic close-up pulling back to reveal full battle stance",

    5: "Charizard with vibrant orange body and teal turquoise wing membranes powerfully unleashing massive Flamethrower attack, jaws opening wide as enormous stream of orange-yellow flames erupts violently forward, wings bracing back from intense recoil force, volcanic valley background with dramatic storm clouds, heat distortion rippling through the air, fixed camera capturing the devastating fire blast from side angle, cinematic action intensity",

    6: "Dragonite with green wings barrel-rolling rapidly to dodge flames, tucking wings aerodynamically then countering violently with crackling Thunder Punch, electric energy building intensely on fist, speed and agility displayed dramatically, volcanic landscape blurring, fast tracking shot following Dragonite's explosive counter-attack maneuver",

    7: "Charizard struck powerfully by electric Thunder Punch attack, electricity crackling violently over orange body and teal wings, grimacing in pain but staying airborne determinedly, struggling against damage, volcanic valley spinning below, dramatic impact captured with intensity, camera showing reeling motion",

    8: "Charizard shaking off electric damage powerfully, teal wing membranes beating with renewed strength, refusing to yield dramatically, cream belly visible as wings spread wide, regaining altitude determinedly with fierce resilience, volcanic valley below, dramatic upward angle showing triumphant recovery flight",

    9: "Charizard and Dragonite both charging blue-purple dragon energy spheres intensely in mouths, releasing Dragon Rage beams that collide mid-air creating massive violent explosion, energy dispersing dramatically with smoke and light, volcanic valley shaking from impact, wide cinematic shot capturing both attacks meeting explosively",

    10: "Charizard bursting dramatically through dissipating smoke cloud, teal wing membranes spread wide powerfully, orange scales glowing from residual energy, diving toward Dragonite below with tactical focus, seeing opening clearly, smoke trailing behind majestically, slow-motion emergence through chaos revealing opportunity",

    11: "Charizard beginning steep dive then accelerating rapidly to maximum speed, wings tucking tight aerodynamically, blue flame tail streaming behind in speed blur, diving toward target with incredible velocity, volcanic valley approaching fast below, cinematic shot following intense dive from above showing escalating speed",

    12: "Charizard grabbing Dragonite mid-air with white claws gripping firmly, both Pokemon beginning to spin together rapidly, grapple locked in powerfully, wings intertwining dramatically, volcanic valley rotating below, rotating camera shot around grappling Pokemon showing unbreakable grip intensifying",

    13: "Charizard spinning rapidly while ascending higher powerfully, teal wings beating with tremendous force, holding Dragonite firmly in grip, gaining massive altitude spiraling upward violently, building momentum for legendary throw, volcanic valley shrinking far below, spiraling upward shot showing ascent to peak altitude dramatically",

    14: "Charizard at maximum altitude releasing Dragonite with explosive force, hurling rival straight down violently toward valley floor, Dragonite plummeting rapidly creating massive impact crater upon landing, ground shattering dramatically with dust explosion, devastating Seismic Toss finishing blow, following descent then impact captured cinematically",

    15: "Charizard with teal wing membranes gliding down gracefully from altitude, tail flame returning to normal orange, exhausted but victorious, descending toward impact crater peacefully, landing softly at crater edge with honor, volcanic landscape quiet after battle, aerial shot following victorious but humble descent",

    16: "Dragonite rising slowly from crater battered but respectful, extending arm in warrior salute gesture, Charizard with teal wings nodding back respectfully, mutual acknowledgment building between former rivals, no longer enemies but warriors who shared honorable combat, ground level emotional shot showing respect earned through battle",

    17: "Multiple Charizards with teal wing membranes perched on volcanic peaks roaring approval dramatically, wings spreading wide in celebration, breathing fire upward triumphantly, our hero Charizard acknowledged in valley center, community acceptance growing palpably, wide pan showing valley defenders celebrating warrior's victory, cinematic scope revealing full community",

    18: "Charizard and Dragonite flying side by side peacefully toward vibrant orange sunset, teal and green wing membranes glowing in sunset light, distant silhouettes becoming closer revealing heroic partnership, volcanic valley peaks below bathed in golden light, greatness earned through honor, camera slowly pulling back revealing epic scale of peaceful flight together, cinematic closure"
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

def generate_video(segment_num: int):
    """Generate video for a specific segment."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found in .env")
        return False

    # File paths
    start_frame = f"charizard/battle_assets/frame_pairs/seg{segment_num:02d}_*_start.jpg"
    end_frame = f"charizard/battle_assets/frame_pairs/seg{segment_num:02d}_*_end.jpg"
    output = f"charizard/battle_assets/videos/seg{segment_num:02d}_video.mp4"

    # Find actual filenames
    import glob
    start_files = glob.glob(start_frame)
    end_files = glob.glob(end_frame)

    if not start_files or not end_files:
        print(f"❌ Frame pair files not found for segment {segment_num}")
        return False

    start_frame = start_files[0]
    end_frame = end_files[0]
    prompt = SEGMENT_PROMPTS[segment_num]

    print(f"\n🎬 Generating Video: Segment {segment_num}")
    print(f"━" * 60)
    print(f"📝 Prompt: {prompt[:100]}...")

    # Upload frames
    try:
        start_url = upload_image(start_frame)
        end_url = upload_image(end_frame)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

    print(f"🚀 Submitting to Seedance 1.5 Pro API...")

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

def batch_generate_all(start_from=1):
    """Generate videos for all segments."""
    print("🎬 BATCH VIDEO GENERATION: ALL SEGMENTS")
    print("=" * 60)
    print(f"Total segments: 18")
    print(f"Starting from: Segment {start_from}")
    print(f"Estimated time: 40-60 minutes")
    print("=" * 60)

    success_count = 0
    failed_segments = []

    for seg_num in range(start_from, 19):
        result = generate_video(seg_num)

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
        print(f"  python scripts/batch_generate_videos.py --start-from {failed_segments[0]}")
    else:
        print(f"\n🎊 ALL VIDEOS GENERATED SUCCESSFULLY!")
        print(f"Next step: Assemble documentary with audio sync")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch generate all battle story videos")
    parser.add_argument("--segment", type=int, help="Generate specific segment only")
    parser.add_argument("--start-from", type=int, default=1, help="Start from segment number")
    parser.add_argument("--all", action="store_true", help="Generate all 18 videos")

    args = parser.parse_args()

    if args.segment:
        if args.segment < 1 or args.segment > 18:
            print("❌ Error: Segment must be between 1 and 18")
            sys.exit(1)
        generate_video(args.segment)
    elif args.all:
        batch_generate_all(args.start_from)
    else:
        print("Usage:")
        print("  --segment N     Generate video for segment N")
        print("  --all           Generate all 18 videos")
        print("  --start-from N  Start from segment N (with --all)")
        print("\nExample: python scripts/batch_generate_videos.py --all")
