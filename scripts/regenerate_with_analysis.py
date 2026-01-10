#!/usr/bin/env python3
"""
Regenerate all 18 frame pairs with:
1. Corrected Pokemon sizes (Dragonite 30% larger)
2. Corrected wing colors (orange tops, teal undersides)
3. Automatic Claude vision analysis after each image
"""

import os
import sys
import time
import requests
import json
import base64
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# Wing color correction: Orange upper surface, teal underside
WING_DESC = "wings with orange upper surface matching body color and teal turquoise underside membranes"

# All 18 segments with size AND wing color corrections
CORRECTED_PROMPTS = {
    1: {
        "start": f"Charizard (5'7\" tall, vibrant orange body #F08030, {WING_DESC}, cream belly) soaring majestically over volcanic peaks at dawn, wings beating rhythmically, flying toward camera, golden sunrise light, cinematic aerial shot, photorealistic anime style, 4K",

        "end": f"Same Charizard closer to camera, {WING_DESC} fully spread wide, orange wing tops catching golden light with teal undersides visible at edges, volcanic valley far below, dramatic close-up, photorealistic anime style, 4K"
    },

    2: {
        "start": f"Dark ominous shadow descending from storm clouds, larger Dragonite (7'3\" tall, 30% bigger than Charizard, bulkier orange body, powerful green wings, antennae) approaching valley, lightning crackling, dramatic arrival, photorealistic anime style, 4K",

        "end": f"Larger Dragonite (7'3\", bulky build, green wings fully extended showing impressive size) landing powerfully in valley, creating dust cloud, intimidating presence, photorealistic anime style, 4K"
    },

    3: {
        "start": f"Epic mid-air standoff: smaller Charizard (5'7\", orange body, {WING_DESC}) facing significantly larger Dragonite (7'3\", 30% bigger and bulkier, orange body, green wings), Dragonite looming over smaller Charizard, David vs Goliath moment, both circling, volcanic valley below, photorealistic anime style, 4K",

        "end": f"Same standoff closer together, Dragonite's larger size more apparent, both maintaining eye contact, wings spread in battle stance, size difference emphasizing courage of smaller Charizard, volcanic backdrop, photorealistic anime style, 4K"
    },

    4: {
        "start": f"Charizard (orange body, {WING_DESC}) roaring powerfully with battle cry, jaws opening wide, wing membranes (orange tops, teal undersides) flaring dramatically, tail flame intensifying blue-white, dramatic close-up, photorealistic anime style, 4K",

        "end": f"Same Charizard, battle stance with {WING_DESC} fully spread showing color pattern, tail flame blazing intensely, ready for combat, volcanic valley background, photorealistic anime style, 4K"
    },

    5: {
        "start": f"Charizard (orange body, {WING_DESC}) inhaling deeply preparing Flamethrower, chest expanding, orange glow building in throat, wings (orange tops) bracing for recoil, photorealistic anime style, 4K",

        "end": f"Same Charizard unleashing massive Flamethrower, enormous flames erupting forward, heat distortion, {WING_DESC} working against recoil, devastating blast, side angle, photorealistic anime style, 4K"
    },

    6: {
        "start": f"Larger Dragonite (7'3\", bulkier, 30% bigger, orange body, powerful green wings) barrel-rolling rapidly to evade flames, wings tucking aerodynamically, muscular build in motion, smoke trails, dynamic action, photorealistic anime style, 4K",

        "end": f"Same larger Dragonite completing roll, green wings extended showing size, electrical energy crackling around fist (Thunder Punch), bulky body coiled with power, ready to strike, photorealistic anime style, 4K"
    },

    7: {
        "start": f"Charizard (orange body, {WING_DESC}) struck by Thunder Punch, electricity crackling violently across body and wing membranes, grimacing from impact, staying airborne, handheld camera, photorealistic anime style, 4K",

        "end": f"Same Charizard reeling from hit, electricity dissipating, {WING_DESC} working to regain stability, determination visible despite damage, volcanic backdrop, photorealistic anime style, 4K"
    },

    8: {
        "start": f"Charizard (orange body, {WING_DESC}) shaking off electrical damage, wings beating with renewed strength, orange upper surfaces catching light, regaining altitude, photorealistic anime style, 4K",

        "end": f"Same Charizard recovered and climbing, {WING_DESC} fully spread showing power, tail flame burning bright, determined expression, triumphant recovery, dramatic upward angle, photorealistic anime style, 4K"
    },

    9: {
        "start": f"Both dragons: smaller Charizard (5'7\", {WING_DESC}) and larger Dragonite (7'3\", green wings) charging Dragon Rage energy in mouths, blue-purple energy building, facing each other, size difference visible, photorealistic anime style, 4K",

        "end": f"Energy beams released simultaneously from both dragons, powerful beams colliding mid-air violently, explosion starting, size contrast maintained, wide shot capturing collision scale, photorealistic anime style, 4K"
    },

    10: {
        "start": f"Massive smoke cloud from energy collision, volcanic valley obscured, dramatic aftermath, photorealistic anime style, 4K",

        "end": f"Charizard (orange body, {WING_DESC}) bursting through smoke dramatically, wings spread wide, orange scales glowing, emerging with focus, slow-motion reveal, photorealistic anime style, 4K"
    },

    11: {
        "start": f"Charizard ({WING_DESC}) accelerating into steep dive, wings tucking tight, orange upper surfaces streamlined, tail flame trailing, volcanic valley approaching fast, photorealistic anime style, 4K",

        "end": f"Same Charizard in high-speed dive, velocity increasing, {WING_DESC} partially tucked, speed blur effect, closing on larger Dragonite below, following shot, photorealistic anime style, 4K"
    },

    12: {
        "start": f"Smaller Charizard (5'7\", {WING_DESC}) grabbing significantly larger Dragonite (7'3\", 30% bigger, bulkier), muscles straining from weight, wings working hard to maintain altitude, size difference making feat impressive, beginning to spin, photorealistic anime style, 4K",

        "end": f"Both spinning rapidly together, smaller Charizard maintaining grip on larger Dragonite, wings intertwining (orange/teal and green), rotation increasing, valley blurred below, size contrast clear, photorealistic anime style, 4K"
    },

    13: {
        "start": f"Legendary Seismic Toss: smaller Charizard (5'7\", {WING_DESC}) spinning rapidly while ascending, firmly holding larger Dragonite (7'3\", 30% bigger, bulkier), both spiraling upward through clouds, wings beating powerfully, size difference emphasizing feat, photorealistic anime style, 4K",

        "end": f"Peak altitude: smaller Charizard still spinning with larger Dragonite, both high above valley, massive momentum built, storm clouds swirling, preparing legendary throw of bigger opponent, photorealistic anime style, 4K"
    },

    14: {
        "start": f"Climax: smaller Charizard releasing larger Dragonite (30% bigger) with explosive force, hurling bulkier rival downward, {WING_DESC} spread from effort, dramatic vertical composition, photorealistic anime style, 4K",

        "end": f"Larger Dragonite's bulkier body crashing into valley, massive dust explosion erupting, shock waves, crater forming, Dragonite's size making impact devastating, wide shot, photorealistic anime style, 4K"
    },

    15: {
        "start": f"Charizard ({WING_DESC}) gliding down gracefully from altitude, wings spread wide showing orange tops and teal undersides, tail flame normal, descending peacefully toward crater, aerial shot, photorealistic anime style, 4K",

        "end": f"Same Charizard landing near crater, {WING_DESC} folding, orange upper surfaces prominent, victorious but respectful stance, photorealistic anime style, 4K"
    },

    16: {
        "start": f"Larger Dragonite (7'3\", bulkier) rising slowly from crater dust, impressive size visible despite battle damage, extending arm in warrior salute, photorealistic anime style, 4K",

        "end": f"Charizard (5'7\", {WING_DESC}) and larger Dragonite exchanging nods, mutual respect, size difference maintained, both acknowledging worthy battle, ground level shot, photorealistic anime style, 4K"
    },

    17: {
        "start": f"Multiple Charizards ({WING_DESC} on each) perched on volcanic peaks witnessing battle resolution, wings spread in celebration, orange upper surfaces catching light, photorealistic anime style, 4K",

        "end": f"Valley Charizards roaring approval, breathing fire upward, {WING_DESC} flaring, celebrating victory, valley alive with celebration, wide pan, photorealistic anime style, 4K"
    },

    18: {
        "start": f"Charizard (5'7\", {WING_DESC}) and larger Dragonite (7'3\", green wings) flying side by side toward sunset, size difference clear but equals now, wings glowing in sunset light, photorealistic anime style, 4K",

        "end": f"Both dragons silhouetted against sunset, size contrast visible in silhouette, peaceful flight together, camera pulling back revealing scale, friendship forged, photorealistic anime style, 4K"
    }
}


def analyze_image_with_claude(image_path: str, segment_num: int, frame_type: str):
    """Analyze generated image using Claude vision to verify size and colors."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Determine what to check based on segment
    if segment_num in [3, 6, 12, 13, 14, 16, 18]:
        # Dual-subject scenes - check size relationship
        analysis_prompt = f"""Analyze this Pokemon battle image (Segment {segment_num}, {frame_type} frame).

Check the following:

1. **SIZE VERIFICATION** (Critical):
   - Is Dragonite visibly LARGER than Charizard (should be ~30% bigger)?
   - Is Dragonite bulkier and more massive looking?
   - Score: CORRECT if Dragonite is clearly larger, INCORRECT if same size or smaller

2. **CHARIZARD WING COLORS**:
   - Upper wing surface: Should be ORANGE (matching body)
   - Underside/membrane: Should be TEAL/TURQUOISE
   - Score: CORRECT if orange tops visible, INCORRECT if fully teal

3. **OVERALL QUALITY**:
   - Image clarity and detail
   - Proper Pokemon anatomy
   - Appropriate scene composition

Respond in this format:
SIZE: [CORRECT/INCORRECT] - [brief explanation]
WINGS: [CORRECT/INCORRECT] - [brief explanation]
QUALITY: [score 1-10] - [brief comment]
RECOMMENDATION: [ACCEPT/REGENERATE] - [reason if regenerate needed]"""
    else:
        # Single Charizard scenes - check wing colors only
        analysis_prompt = f"""Analyze this Charizard image (Segment {segment_num}, {frame_type} frame).

Check the following:

1. **CHARIZARD WING COLORS** (Critical):
   - Upper wing surface: Should be ORANGE (matching body #F08030)
   - Underside/membrane: Should be TEAL/TURQUOISE (#58A8B8)
   - Score: CORRECT if orange tops visible, INCORRECT if fully teal

2. **OVERALL QUALITY**:
   - Image clarity and detail
   - Proper Charizard anatomy
   - Appropriate scene composition

Respond in this format:
WINGS: [CORRECT/INCORRECT] - [brief explanation]
QUALITY: [score 1-10] - [brief comment]
RECOMMENDATION: [ACCEPT/REGENERATE] - [reason if regenerate needed]"""

    print(f"\n🔍 Analyzing with Claude Vision...")

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": analysis_prompt
                    }
                ],
            }],
        )

        analysis = message.content[0].text
        print(f"\n📊 ANALYSIS RESULTS:")
        print(analysis)

        # Check if regeneration recommended
        if "REGENERATE" in analysis:
            print(f"\n⚠️  REGENERATION RECOMMENDED")
            return False
        else:
            print(f"\n✅ IMAGE ACCEPTED")
            return True

    except Exception as e:
        print(f"\n⚠️  Analysis failed: {e}")
        print(f"   Proceeding anyway...")
        return True


def generate_image_with_analysis(prompt: str, output_path: str, segment_num: int, frame_type: str):
    """Generate image and analyze it automatically."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"\n{'='*60}")
    print(f"🎨 SEGMENT {segment_num:02d} - {frame_type.upper()} FRAME")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt[:150]}...")

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "image_input": [],
            "aspect_ratio": "16:9",
            "resolution": "4K",
            "output_format": "jpg"
        }
    }

    print(f"🚀 Submitting to Nano Banana Pro...")
    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload,
        timeout=60
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
    print(f"⏳ Generating... ", end="", flush=True)

    # Poll for completion
    max_wait = 300
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(5)
        elapsed += 5
        print(f"{elapsed}s ", end="", flush=True)

        status_response = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers,
            timeout=30
        )

        if status_response.status_code != 200:
            continue

        status_data = status_response.json()
        if status_data.get("code") != 200:
            continue

        state = status_data["data"]["state"]

        if state == "success":
            print(f"\n✅ Generated!")

            result_json = json.loads(status_data["data"]["resultJson"])
            image_url = result_json["resultUrls"][0]

            print(f"📥 Downloading...")
            img_response = requests.get(image_url, timeout=60)

            if img_response.status_code == 200:
                # Backup old if exists
                if os.path.exists(output_path):
                    backup_path = output_path.replace(".jpg", "_old.jpg")
                    os.rename(output_path, backup_path)

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)

                size_mb = len(img_response.content) / (1024 * 1024)
                print(f"✅ Saved: {os.path.basename(output_path)} ({size_mb:.2f} MB)")

                # ANALYZE IMAGE
                accepted = analyze_image_with_claude(output_path, segment_num, frame_type)

                return accepted
            else:
                print(f"\n❌ Download failed")
                return False

        elif state == "fail":
            print(f"\n❌ Generation failed")
            return False

    print(f"\n❌ Timeout")
    return False


def regenerate_all():
    """Regenerate all 36 images (18 segments × 2 frames) with analysis."""
    print("🎯 FULL REGENERATION WITH AUTOMATIC ANALYSIS")
    print("="*60)
    print("Fixing: Size (Dragonite 30% larger) + Wing Colors (orange tops)")
    print("All 18 segments: 36 images total")
    print("Each image analyzed by Claude Vision")
    print("="*60)

    results = {}
    total = 36
    success_count = 0

    for seg_num in range(1, 19):
        prompts = CORRECTED_PROMPTS[seg_num]

        # START frame
        start_path = f"charizard/battle_assets/frame_pairs/seg{seg_num:02d}_corrected_start.jpg"
        if generate_image_with_analysis(prompts["start"], start_path, seg_num, "start"):
            success_count += 1
            results[f"seg{seg_num:02d}_start"] = True
        else:
            results[f"seg{seg_num:02d}_start"] = False

        time.sleep(2)

        # END frame
        end_path = f"charizard/battle_assets/frame_pairs/seg{seg_num:02d}_corrected_end.jpg"
        if generate_image_with_analysis(prompts["end"], end_path, seg_num, "end"):
            success_count += 1
            results[f"seg{seg_num:02d}_end"] = True
        else:
            results[f"seg{seg_num:02d}_end"] = False

        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"🎉 REGENERATION COMPLETE!")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}/{total} ({success_count/total*100:.1f}%)")

    failed = [name for name, success in results.items() if not success]
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for name in failed:
            print(f"  - {name}")

    print(f"\n📁 Images: charizard/battle_assets/frame_pairs/seg*_corrected_*.jpg")
    print(f"\n🎬 Next: Generate videos with Kling AI")


if __name__ == "__main__":
    regenerate_all()
