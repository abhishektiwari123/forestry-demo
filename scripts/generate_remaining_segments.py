#!/usr/bin/env python3
"""
Batch generate remaining segment images: 11, 12, 15, 16, 17, 18
"""

import os
import sys
import time
import requests
import json

def load_api_key():
    """Load API key from .env file."""
    env_paths = ['.env', '/home/user/forestry-demo/.env', 'scripts/.env']

    for path in env_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('KIE_API_KEY='):
                        return line.strip().split('=', 1)[1]
    raise Exception("❌ KIE_API_KEY not found")


def generate_image(segment_num, prompt, output_path, api_key):
    """Generate image with Nano Banana Pro."""
    print(f"\n{'='*70}")
    print(f"🎨 GENERATING SEGMENT {segment_num}")
    print(f"{'='*70}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "output_format": "jpg"
        }
    }

    print("🚀 Submitting to Nano Banana Pro...")
    start_time = time.time()

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

    while time.time() - start_time < 300:
        time.sleep(5)
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
                image_url = json.loads(data["resultJson"])["resultUrls"][0]
                print(f"📥 Downloading...")

                img_resp = requests.get(image_url, timeout=30)
                if img_resp.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(img_resp.content)

                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                    return True

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print(f"\n❌ Timeout")
    return False


def main():
    print("="*70)
    print("BATCH GENERATE REMAINING SEGMENTS")
    print("="*70)

    api_key = load_api_key()

    # Define remaining segments with prompts
    segments = [
        {
            "num": 11,
            "name": "Speed Dive",
            "prompt": """Charizard (5 feet 7 inches, lean athletic orange fire dragon with teal turquoise wing undersides, cream belly, flaming tail tip) diving at maximum speed in steep attack angle, wings tucked tightly against body for aerodynamics, tail flame streaming blue behind showing intense speed, targeting downward toward unseen opponent below, streamlined dive position, motion blur showing velocity, dramatic POV from above and behind following dive, volcanic valley far below, speed lines and air distortion, intense focused expression, Pokemon character Charizard clearly recognizable, cinematic 3D animation, high-speed action""",
            "output": "charizard/battle_assets/frame_pairs/seg11_continuous_start.jpg"
        },
        {
            "num": 12,
            "name": "Grab",
            "prompt": """Epic mid-air grapple: Charizard (5 feet 7 inches, lean athletic orange fire dragon with teal turquoise wing undersides, cream belly, flaming tail) seizing significantly larger Dragonite (7 feet 3 inches, 30% bigger, bulky muscular stocky build, light ORANGE-tan body NOT green NOT blue, cream belly with horizontal stripes, teal turquoise wing membranes, two thin antennae on head, NO tail flame) mid-air, white claws gripping Dragonite's wings firmly, both Pokemon locked in grapple spinning together, dynamic rotating composition, Charizard triumphant expression capturing opponent, Dragonite surprised by grab, both Pokemon clearly visible and recognizable, teal wings on both visible, size difference obvious with Dragonite larger, setup for finishing move, cinematic 3D animation, volcanic valley background""",
            "output": "charizard/battle_assets/frame_pairs/seg12_continuous_start.jpg"
        },
        {
            "num": 15,
            "name": "Victory Descent",
            "prompt": """Charizard (5 feet 7 inches, lean athletic orange fire dragon with teal turquoise wing undersides, cream belly, flaming tail) gliding down gracefully with teal wing membranes spread wide showing both orange upper surface and teal undersides, descending toward impact crater on ground, tail flame returning to normal orange glow from intense blue, exhausted but victorious posture, gentle controlled descent, dramatic aerial shot following from above, volcanic valley with visible impact crater below, smoke rising from crater, peaceful resolution after intense battle, Pokemon character Charizard clearly recognizable, cinematic 3D animation, golden late afternoon lighting""",
            "output": "charizard/battle_assets/frame_pairs/seg15_continuous_start.jpg"
        },
        {
            "num": 16,
            "name": "Respect",
            "prompt": """Ground level warrior's salute: Significantly larger battered Dragonite (7 feet 3 inches, 30% bigger, bulky muscular stocky build, light ORANGE-tan body NOT green NOT blue, cream belly with horizontal stripes, teal turquoise wing membranes, two thin antennae on head, NO tail flame) rising slowly from impact crater extending arm/wing forward in respectful warrior salute, and smaller Charizard (5 feet 7 inches, lean athletic orange fire dragon with teal turquoise wings, cream belly, flaming tail) standing on crater edge nodding back in mutual respect, both Pokemon battered but honorable, face-to-face ground level shot showing both clearly, size difference obvious with Dragonite taller and bulkier, no longer rivals but warriors who shared battle, dust settling, both Pokemon clearly recognizable, cinematic 3D animation, volcanic valley background""",
            "output": "charizard/battle_assets/frame_pairs/seg16_continuous_start.jpg"
        },
        {
            "num": 17,
            "name": "Valley Recognition",
            "prompt": """Multiple Charizards celebrating victory: Wide panoramic shot of volcanic valley with multiple Charizards (each 5'7\", lean athletic orange dragons with teal turquoise wing undersides, cream bellies, flaming tails) perched on different rocky peaks and cliff edges throughout valley, all with teal wings spread wide, some breathing fire upward in celebration, all roaring approval, our hero Charizard in foreground center being acknowledged by valley defenders, sense of community acceptance and earned respect, dramatic valley vista with multiple Pokemon visible, volcanic peaks and lava streams, all Charizards clearly recognizable with consistent orange bodies and teal wings, epic wide cinematic shot, Pokemon character Charizard design consistent across all""",
            "output": "charizard/battle_assets/frame_pairs/seg17_continuous_start.jpg"
        },
        {
            "num": 18,
            "name": "Sunset Flight Home",
            "prompt": """Peaceful sunset silhouette: Charizard (5 feet 7 inches, orange dragon with teal turquoise wing membranes glowing translucent against sunset) and significantly larger Dragonite (7 feet 3 inches, 30% bigger, light orange-tan body, teal wing membranes also glowing) flying side by side in perfect formation toward vibrant orange-red sunset, both silhouetted but teal wing undersides catching sunset glow appearing luminous, peaceful flight together after battle, size difference visible in silhouettes, volcanic valley below in shadow, dramatic sunset sky with orange-red-purple gradient, both Pokemon recognizable by distinctive shapes (Charizard's flaming tail, Dragonite's antennae and bulkier build), heroic cinematic composition, slow pull back revealing valley landscape, Pokemon characters Charizard and Dragonite, resolution and peace""",
            "output": "charizard/battle_assets/frame_pairs/seg18_continuous_start.jpg"
        }
    ]

    # Create output directory
    os.makedirs("charizard/battle_assets/frame_pairs", exist_ok=True)

    results = []

    for segment in segments:
        result = generate_image(
            segment["num"],
            segment["prompt"],
            segment["output"],
            api_key
        )
        results.append({
            "num": segment["num"],
            "name": segment["name"],
            "success": result
        })

        if not result:
            print(f"\n⚠️  Segment {segment['num']} failed, continuing with next...")

    # Summary
    print(f"\n{'='*70}")
    print("📊 BATCH GENERATION SUMMARY")
    print(f"{'='*70}")

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\n✅ Successful: {len(successful)}/{len(segments)}")
    for r in successful:
        print(f"   Seg{r['num']:02d}: {r['name']}")

    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(segments)}")
        for r in failed:
            print(f"   Seg{r['num']:02d}: {r['name']}")

    print(f"\nNext: Validate all generated images")

    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
