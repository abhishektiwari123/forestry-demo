#!/usr/bin/env python3
"""
Regenerate 5 key images with corrected Pokemon size proportions.
Dragonite should be 30% LARGER than Charizard (not smaller).
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Size-corrected prompts for dual-subject scenes
# Key: Dragonite is 7'3" (2.2m), Charizard is 5'7" (1.7m)
# Dragonite should be 30% taller and bulkier

SIZE_CORRECTED_PROMPTS = {
    3: {
        "start": """Epic mid-air standoff in volcanic valley: smaller Charizard (5'7" tall, vibrant orange body with #F08030 scales, teal turquoise #58A8B8 wing membranes, cream belly) facing significantly larger, intimidating Dragonite (7'3" tall, 30% bigger and bulkier build, orange body with green wings, antennae), Dragonite looming imposingly over smaller Charizard emphasizing dramatic size difference, David vs Goliath moment, both circling mid-air sizing each other up, volcanic peaks and lava flows far below, storm clouds gathering, cinematic wide shot capturing size contrast, photorealistic anime style, 4K quality""",

        "end": """Same epic standoff continued: smaller Charizard and larger Dragonite now closer together mid-air, Dragonite's 30% larger size more apparent, both dragons maintaining intense eye contact, wings spread in battle-ready stance, Dragonite's bulkier muscular build contrasting with Charizard's leaner frame, teal and green wing membranes catching dramatic light, volcanic valley backdrop, tension building, size difference emphasizing courage of smaller Charizard, photorealistic anime style, 4K quality"""
    },

    6: {
        "start": """Larger Dragonite (7'3" tall, bulkier orange body, powerful green wings spread wide, 30% bigger than Charizard) rapidly barrel-rolling through air to evade flames, wings tucking aerodynamically showing impressive wingspan, muscular build evident in motion, smoke trails from dodged fire attack, volcanic valley blurred in background, dynamic action shot emphasizing Dragonite's size and power, photorealistic anime style, 4K quality""",

        "end": """Same larger Dragonite completing evasive roll and counter-attacking, green wings fully extended revealing impressive size, electrical energy crackling around large fist preparing Thunder Punch, bulky muscular body coiled with power, yellow electricity sparks intensifying, determined expression, ready to strike smaller opponent, dramatic lighting from electricity, volcanic backdrop, action-packed moment, photorealistic anime style, 4K quality"""
    },

    12: {
        "start": """Impressive feat: smaller Charizard (5'7" tall, orange body, teal wing membranes) grabbing and lifting significantly larger, heavier Dragonite (7'3" tall, 30% bigger, bulkier orange body, green wings) mid-air, Charizard's muscles straining visibly from weight of bigger opponent, teal wings working hard to maintain altitude, claws firmly gripping Dragonite's bulkier frame, size difference making feat remarkable, both beginning to spin together, volcanic valley rotating far below, dramatic angle emphasizing size contrast and physical challenge, photorealistic anime style, 4K quality""",

        "end": """Both dragons spinning rapidly together mid-air, smaller Charizard maintaining grip on larger Dragonite despite size disadvantage, rotation speed increasing, wings of both intertwining (teal and green membranes), Dragonite's heavier bulk creating momentum, Charizard showing incredible strength holding bigger opponent, volcanic valley now blurred circle below from rotation, centrifugal force visible, determination on Charizard's face, impressive display of power over larger foe, photorealistic anime style, 4K quality"""
    },

    13: {
        "start": """Legendary Seismic Toss setup: smaller Charizard (5'7", orange body, teal wings) spinning rapidly while ascending skyward, firmly holding significantly larger, heavier Dragonite (7'3", 30% bigger, bulkier build, orange body, green wings), both spiraling upward violently through storm clouds, Charizard's wings beating powerfully despite carrying weight of bigger opponent, Dragonite's heavier mass building tremendous rotational momentum, size difference emphasizing incredible feat of strength, clouds rushing past, dramatic spiraling ascent, photorealistic anime style, 4K quality""",

        "end": """Peak of ascent: smaller Charizard still spinning while holding larger Dragonite at maximum altitude, both dragons now high above valley, Dragonite's bulkier body creating massive momentum from spin, Charizard preparing to release, storm clouds swirling around from rotation, size contrast dramatic at height, building to legendary throw of bigger opponent, tension at maximum, photorealistic anime style, 4K quality"""
    },

    14: {
        "start": """Climax of Seismic Toss: smaller Charizard at peak altitude releasing larger, heavier Dragonite (30% bigger) with explosive force, hurling bulkier rival straight down toward valley floor below, Dragonite's larger body beginning rapid plummet, Charizard's wings spread wide from release effort showing exertion of throwing bigger opponent, size difference making throw more impressive, storm clouds in background, dramatic vertical composition following descent, photorealistic anime style, 4K quality""",

        "end": """Impact moment: larger Dragonite's bulkier body crashing into volcanic valley floor, massive dust and rock explosion erupting from crater, shock waves radiating outward, Dragonite's larger size making impact more devastating, debris cloud mushrooming upward, volcanic rocks shattered from force, dramatic crater formation, smaller Charizard visible descending in background, scale of impact emphasized by size of fallen Dragonite, cinematic wide shot of destruction, photorealistic anime style, 4K quality"""
    }
}


def generate_image(prompt: str, output_path: str):
    """Generate single image with Nano Banana Pro."""
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"\n🎨 Generating: {os.path.basename(output_path)}")
    print(f"📝 Prompt length: {len(prompt)} chars")

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
                # Backup old image
                if os.path.exists(output_path):
                    backup_path = output_path.replace(".jpg", "_old.jpg")
                    os.rename(output_path, backup_path)
                    print(f"📦 Old image backed up: {os.path.basename(backup_path)}")

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)

                size_mb = len(img_response.content) / (1024 * 1024)
                print(f"✅ Saved: {output_path} ({size_mb:.2f} MB)")
                return True
            else:
                print(f"\n❌ Failed to download")
                return False

        elif state == "fail":
            print(f"\n❌ Generation failed: {status_data['data'].get('failMsg')}")
            return False

    print(f"\n❌ Timeout")
    return False


def regenerate_all():
    """Regenerate all 5 segments with size corrections."""
    print("🎯 REGENERATING SIZE-CORRECTED IMAGES")
    print("=" * 60)
    print("Fixing Pokemon sizes: Dragonite 30% LARGER than Charizard")
    print("Segments: 3, 6, 12, 13, 14 (10 images total)")
    print("=" * 60)

    results = {}
    total = 0
    success_count = 0

    for seg_num in [3, 6, 12, 13, 14]:
        print(f"\n{'=' * 60}")
        print(f"SEGMENT {seg_num}")
        print(f"{'=' * 60}")

        prompts = SIZE_CORRECTED_PROMPTS[seg_num]

        # Generate START frame
        start_path = f"charizard/battle_assets/frame_pairs/seg{seg_num:02d}_size_corrected_start.jpg"
        total += 1
        if generate_image(prompts["start"], start_path):
            success_count += 1
            results[f"seg{seg_num:02d}_start"] = True
        else:
            results[f"seg{seg_num:02d}_start"] = False

        time.sleep(3)  # Brief pause between requests

        # Generate END frame
        end_path = f"charizard/battle_assets/frame_pairs/seg{seg_num:02d}_size_corrected_end.jpg"
        total += 1
        if generate_image(prompts["end"], end_path):
            success_count += 1
            results[f"seg{seg_num:02d}_end"] = True
        else:
            results[f"seg{seg_num:02d}_end"] = False

        time.sleep(3)

    print(f"\n{'=' * 60}")
    print(f"🎉 REGENERATION COMPLETE!")
    print(f"{'=' * 60}")
    print(f"✅ Success: {success_count}/{total}")
    print(f"❌ Failed: {total - success_count}/{total}")

    if success_count < total:
        print(f"\n⚠️  Some images failed. Failed segments:")
        for name, success in results.items():
            if not success:
                print(f"  - {name}")

    print(f"\n📁 New images saved to: charizard/battle_assets/frame_pairs/")
    print(f"📦 Old images backed up with '_old.jpg' suffix")

    print(f"\n🎬 Next: Generate videos with Kling AI using corrected images")
    print(f"   python3 scripts/batch_generate_videos_kling.py --all --duration 5")


if __name__ == "__main__":
    regenerate_all()
