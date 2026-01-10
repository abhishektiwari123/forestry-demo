#!/usr/bin/env python3
"""
Generate frame pairs with continuity strategy:
- Scene N's LAST frame becomes Scene N+1's FIRST frame
- Creates seamless visual flow between all 18 segments
- Tests consistency before full generation
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

# Continuous scene descriptions with proper transitions
# Each scene flows into the next
CONTINUOUS_SCENES = {
    1: {
        "first": "Charizard (5'7\", orange body, wings with orange upper surface and teal undersides) soaring majestically over volcanic peaks at dawn, distant view, wings beating rhythmically, volcanic valley below, golden sunrise light, photorealistic anime style, 4K",

        "last": "Same Charizard much closer to camera, wings spread wide showing orange tops and teal undersides, flying confidently, volcanic valley visible below, about to notice approaching threat, photorealistic anime style, 4K"
    },

    2: {
        "first": "[REUSE SEG01 LAST FRAME]",

        "last": "Charizard (smaller, foreground) now alerted, looking up at dark shadow in storm clouds, larger Dragonite (7'3\", bulkier) descending from clouds in background, lightning crackling, tension building, photorealistic anime style, 4K"
    },

    3: {
        "first": "[REUSE SEG02 LAST FRAME]",

        "last": "Both dragons now facing each other mid-air, eye to eye, smaller Charizard (orange wings) and larger Dragonite (green wings, 30% bigger) circling, battle about to begin, tense standoff, photorealistic anime style, 4K"
    },

    4: {
        "first": "[REUSE SEG03 LAST FRAME]",

        "last": "Charizard roaring powerfully with battle cry complete, jaws wide open, wings (orange tops, teal undersides) fully spread in attack stance, tail flame blazing blue-white, ready to strike, photorealistic anime style, 4K"
    },

    5: {
        "first": "[REUSE SEG04 LAST FRAME]",

        "last": "Charizard unleashing massive Flamethrower, enormous flames erupting forward, wings bracing against recoil, heat distortion waves, Dragonite visible in smoke attempting to dodge, photorealistic anime style, 4K"
    },

    6: {
        "first": "[REUSE SEG05 LAST FRAME]",

        "last": "Larger Dragonite (7'3\") emerging from smoke evasion, green wings extended, electrical energy crackling around fist (Thunder Punch ready), bulky body coiled to counter-attack, photorealistic anime style, 4K"
    },

    7: {
        "first": "[REUSE SEG06 LAST FRAME]",

        "last": "Charizard reeling from Thunder Punch impact, electricity dissipating across body and wings, grimacing but recovering, maintaining altitude, determination visible, photorealistic anime style, 4K"
    },

    8: {
        "first": "[REUSE SEG07 LAST FRAME]",

        "last": "Charizard fully recovered, wings (orange tops) beating powerfully, climbing altitude, tail flame burning bright, renewed determination, ready to continue battle, photorealistic anime style, 4K"
    },

    9: {
        "first": "[REUSE SEG08 LAST FRAME]",

        "last": "Massive energy explosion from Dragon Rage collision, blue-purple beams colliding violently mid-air between both dragons, shock waves expanding, smoke and energy clouds forming, photorealistic anime style, 4K"
    },

    10: {
        "first": "[REUSE SEG09 LAST FRAME]",

        "last": "Charizard bursting dramatically through smoke cloud, wings spread wide, orange body glowing, emerging victorious from explosion, smoke parting around, photorealistic anime style, 4K"
    },

    11: {
        "first": "[REUSE SEG10 LAST FRAME]",

        "last": "Charizard in high-speed dive, wings partially tucked, velocity increasing, closing rapidly on larger Dragonite below, speed blur effects, preparing to grapple, photorealistic anime style, 4K"
    },

    12: {
        "first": "[REUSE SEG11 LAST FRAME]",

        "last": "Smaller Charizard and larger Dragonite (30% bigger) spinning rapidly together, both grappling mid-air, wings intertwined (orange/teal and green), rotation increasing, valley blurred below, photorealistic anime style, 4K"
    },

    13: {
        "first": "[REUSE SEG12 LAST FRAME]",

        "last": "Both dragons at peak altitude, smaller Charizard still gripping larger Dragonite, spinning rapidly high above valley, storm clouds swirling, maximum height reached, about to release throw, photorealistic anime style, 4K"
    },

    14: {
        "first": "[REUSE SEG13 LAST FRAME]",

        "last": "Larger Dragonite's bulky body crashing into valley floor, massive dust and rock explosion erupting from impact crater, shock waves radiating, debris mushrooming upward, photorealistic anime style, 4K"
    },

    15: {
        "first": "[REUSE SEG14 LAST FRAME]",

        "last": "Charizard landing gracefully near crater edge, wings (orange tops, teal undersides) folding, tail flame returning to normal orange, standing victorious but respectful, photorealistic anime style, 4K"
    },

    16: {
        "first": "[REUSE SEG15 LAST FRAME]",

        "last": "Larger Dragonite (7'3\") and smaller Charizard exchanging warrior salute, mutual nod of respect, both standing ground level, size difference visible, former rivals now equals, photorealistic anime style, 4K"
    },

    17: {
        "first": "[REUSE SEG16 LAST FRAME]",

        "last": "Multiple valley Charizards (wings: orange tops, teal undersides) roaring approval from surrounding peaks, breathing fire upward in celebration, valley alive with celebration, wide panoramic view, photorealistic anime style, 4K"
    },

    18: {
        "first": "[REUSE SEG17 LAST FRAME]",

        "last": "Smaller Charizard and larger Dragonite flying side by side toward sunset, silhouetted together, wings glowing in golden light, peaceful flight, camera pulling back revealing epic scale, friendship forged, photorealistic anime style, 4K"
    }
}


def generate_frame(prompt: str, output_path: str, segment_num: int, frame_type: str):
    """Generate single frame with Nano Banana Pro."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"\n🎨 Generating Seg{segment_num:02d} {frame_type.upper()}")
    print(f"📝 {prompt[:100]}...")

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
        print(f"❌ Failed: {result.get('msg')}")
        return False

    task_id = result["data"]["taskId"]
    print(f"⏳ Generating... ", end="", flush=True)

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

            img_response = requests.get(image_url, timeout=60)
            if img_response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)

                size_mb = len(img_response.content) / (1024 * 1024)
                print(f"✅ Saved: {os.path.basename(output_path)} ({size_mb:.2f} MB)")
                return True

        elif state == "fail":
            print(f"\n❌ Failed")
            return False

    print(f"\n❌ Timeout")
    return False


def analyze_continuity(prev_last_path: str, curr_first_path: str, segment_num: int):
    """Analyze visual continuity between consecutive frames using Claude Vision."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    with open(prev_last_path, "rb") as f:
        prev_data = base64.standard_b64encode(f.read()).decode("utf-8")

    with open(curr_first_path, "rb") as f:
        curr_data = base64.standard_b64encode(f.read()).decode("utf-8")

    prompt = f"""Compare these two consecutive frames from Pokemon battle story:
1. PREVIOUS scene's LAST frame (Scene {segment_num-1} end)
2. CURRENT scene's FIRST frame (Scene {segment_num} start)

Analyze visual continuity:

1. **POSITION/POSE CONSISTENCY**:
   - Do Charizard/Dragonite maintain consistent position/orientation?
   - Natural progression or jarring jump?

2. **SIZE CONSISTENCY**:
   - Pokemon sizes match between frames?
   - Dragonite still larger than Charizard (if both visible)?

3. **ENVIRONMENTAL CONSISTENCY**:
   - Background elements (volcanic valley, clouds, lighting) consistent?
   - Smooth transition or discontinuity?

4. **VISUAL FLOW**:
   - Does it feel like a natural progression?
   - Could these be consecutive video frames?

Rate each category: EXCELLENT / GOOD / ACCEPTABLE / POOR

Overall: SEAMLESS / SMOOTH / ACCEPTABLE / JARRING"""

    print(f"\n🔍 Analyzing continuity: Seg{segment_num-1}→Seg{segment_num}")

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "PREVIOUS (Last frame):"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": prev_data,
                        },
                    },
                    {"type": "text", "text": "CURRENT (First frame):"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": curr_data,
                        },
                    },
                    {"type": "text", "text": prompt}
                ],
            }],
        )

        analysis = message.content[0].text
        print(f"\n📊 CONTINUITY ANALYSIS:")
        print(analysis)
        print(f"{'='*60}")

        return "SEAMLESS" in analysis or "SMOOTH" in analysis

    except Exception as e:
        print(f"\n⚠️  Analysis failed: {e}")
        return True


def generate_continuous_strategy():
    """
    Generate frames with continuity strategy.
    TEST MODE: Generate first 5 segments to verify strategy works.
    """
    print("🎯 CONTINUOUS FRAME GENERATION STRATEGY")
    print("="*60)
    print("Strategy: Scene N's LAST frame → Scene N+1's FIRST frame")
    print("Test: Generating Segments 1-5 to verify continuity")
    print("="*60)

    continuity_scores = []

    for seg_num in range(1, 6):  # Test first 5 segments
        scene = CONTINUOUS_SCENES[seg_num]

        print(f"\n{'='*60}")
        print(f"SEGMENT {seg_num}")
        print(f"{'='*60}")

        # FIRST frame
        if seg_num == 1:
            # Generate first frame of Seg 1
            first_path = f"charizard/battle_assets/frame_pairs/seg{seg_num:02d}_continuous_start.jpg"
            if not generate_frame(scene["first"], first_path, seg_num, "first"):
                print(f"❌ Failed to generate Seg{seg_num} first frame")
                return
        else:
            # Copy previous segment's last frame as this segment's first frame
            prev_last = f"charizard/battle_assets/frame_pairs/seg{seg_num-1:02d}_continuous_end.jpg"
            curr_first = f"charizard/battle_assets/frame_pairs/seg{seg_num:02d}_continuous_start.jpg"

            print(f"\n📋 Reusing Seg{seg_num-1} LAST → Seg{seg_num} FIRST")
            os.system(f"cp {prev_last} {curr_first}")
            print(f"✅ Copied: {os.path.basename(curr_first)}")

        time.sleep(2)

        # LAST frame
        last_path = f"charizard/battle_assets/frame_pairs/seg{seg_num:02d}_continuous_end.jpg"
        if not generate_frame(scene["last"], last_path, seg_num, "last"):
            print(f"❌ Failed to generate Seg{seg_num} last frame")
            return

        # Analyze continuity (except for first segment)
        if seg_num > 1:
            prev_last = f"charizard/battle_assets/frame_pairs/seg{seg_num-1:02d}_continuous_end.jpg"
            curr_first = f"charizard/battle_assets/frame_pairs/seg{seg_num:02d}_continuous_start.jpg"

            continuity_ok = analyze_continuity(prev_last, curr_first, seg_num)
            continuity_scores.append({
                'transition': f"Seg{seg_num-1}→Seg{seg_num}",
                'status': '✅ GOOD' if continuity_ok else '⚠️ NEEDS WORK'
            })

        time.sleep(2)

    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 TEST COMPLETE - FIRST 5 SEGMENTS")
    print(f"{'='*60}")

    print(f"\n📊 CONTINUITY RESULTS:")
    for score in continuity_scores:
        print(f"  {score['transition']}: {score['status']}")

    good_count = sum(1 for s in continuity_scores if '✅' in s['status'])
    total = len(continuity_scores)

    print(f"\n✅ Good transitions: {good_count}/{total}")

    if good_count == total:
        print(f"\n🎊 EXCELLENT! Continuity strategy works perfectly!")
        print(f"   Ready to generate all 18 segments with this approach.")
    elif good_count >= total * 0.75:
        print(f"\n👍 GOOD! Most transitions smooth, minor adjustments needed.")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT: Refine transition descriptions.")

    print(f"\n📁 Test frames: charizard/battle_assets/frame_pairs/seg*_continuous_*.jpg")
    print(f"\n🎬 If satisfied, run full generation for all 18 segments")


if __name__ == "__main__":
    generate_continuous_strategy()
