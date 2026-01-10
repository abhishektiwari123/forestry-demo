#!/usr/bin/env python3
"""
Generate Segment 9: Dragon Rage Clash
Scene: Both Pokemon unleash Dragon Rage simultaneously, beams collide creating massive explosion
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


def generate_image(prompt, output_path, api_key):
    """Generate image with Nano Banana Pro."""
    print(f"\n{'='*70}")
    print("🎨 GENERATING SEGMENT 9: DRAGON RAGE CLASH")
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
    print("SEGMENT 9: DRAGON RAGE CLASH")
    print("="*70)

    api_key = load_api_key()

    # Segment 9 prompt from battle script
    prompt = """Epic simultaneous attack: Charizard (5 feet 7 inches, smaller lean athletic orange fire dragon with teal turquoise wing undersides, cream belly, flaming tail tip) and significantly larger Dragonite (7 feet 3 inches, 30% bigger, bulky muscular stocky build, light ORANGE-tan body NOT green NOT blue, cream belly with horizontal stripes, teal turquoise wing membranes, two thin antennae on head, NO tail flame) both charging blue-purple dragon energy spheres in their mouths, then releasing concentrated Dragon Rage beams simultaneously that collide mid-air between them creating massive explosion with blue-purple energy burst, evenly matched power, intense energy collision, both Pokemon visible on opposite sides of explosion, teal wings visible on both, dramatic wide shot showing both attackers and energy collision point, peak battle intensity, Pokemon characters Charizard and Dragonite both clearly recognizable, explosive particle effects, cinematic 3D animation, volcanic valley background"""

    output_path = "charizard/battle_assets/frame_pairs/seg09_continuous_start.jpg"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    success = generate_image(prompt, output_path, api_key)

    if success:
        print(f"\n{'='*70}")
        print("🎉 SEGMENT 9 IMAGE COMPLETE!")
        print(f"{'='*70}")
        print(f"\n✅ Image saved: {output_path}")
        print(f"\nNext: Validate image against framework")
    else:
        print(f"\n❌ Generation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
