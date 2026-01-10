#!/usr/bin/env python3
"""
Regenerate Seg03 - Face-off scene with improved lighting.

Critical fixes:
- Both Pokemon features MUST be visible (not silhouetted)
- Dramatic storm atmosphere BUT with proper lighting
- Teal wings visible on both Pokemon
- Dragonite: Light ORANGE-tan body (NOT green, NOT silhouetted)
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
                        api_key = line.strip().split('=', 1)[1]
                        print(f"✅ Loaded API key from {path}")
                        return api_key

    raise Exception("❌ KIE_API_KEY not found in .env files")


def generate_image(prompt, output_path, api_key):
    """Generate image with Nano Banana Pro."""
    print(f"\n{'='*70}")
    print("🎨 REGENERATING SEG03 WITH IMPROVED LIGHTING")
    print(f"{'='*70}")
    print(f"\n📝 Prompt (first 200 chars):")
    print(f"{prompt[:200]}...")

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

    print("\n🚀 Submitting to Nano Banana Pro...")
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
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
                    print(f"📁 Output: {output_path}")
                    return True
                else:
                    print(f"❌ Download failed: {img_resp.status_code}")
                    return False

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print(f"\n❌ Timeout")
    return False


def main():
    print("="*70)
    print("SEG03 REGENERATION - IMPROVED LIGHTING VERSION")
    print("="*70)
    print("\nScene: Face-off between Charizard and Dragonite")
    print("Previous issue: Dragonite completely silhouetted (too dark)")
    print("Fix: Dramatic storm BUT with breaks in clouds illuminating features")
    print("="*70)

    api_key = load_api_key()

    # IMPROVED PROMPT with explicit lighting requirements
    prompt = """Epic face-off scene: Charizard (5 feet 7 inches, lean athletic orange fire dragon with teal turquoise wing undersides, cream belly, flaming tail tip always burning) on ground looking up at significantly larger Dragonite (7 feet 3 inches, 30% bigger, bulky muscular stocky build, light ORANGE-tan body NOT green NOT blue, cream belly with horizontal stripes, teal turquoise wing membranes, two thin antennae on head, NO tail flame) descending from stormy sky with dramatic lightning and rain, BUT breaks in storm clouds illuminate BOTH Pokemon showing their features clearly visible, teal turquoise wings must be clearly visible on both Pokemon, orange body on Charizard clearly visible, light orange-tan body on Dragonite clearly visible NOT silhouetted, antennae visible, Pokemon characters Charizard and Dragonite recognizable NOT generic dragons, epic confrontation, intense dramatic atmosphere with proper lighting showing all features, cinematic composition, high quality 3D animation, volcanic valley background"""

    output_path = "charizard/battle_assets/frame_pairs/seg03_continuous_start_v2.jpg"

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    success = generate_image(prompt, output_path, api_key)

    if success:
        print(f"\n{'='*70}")
        print("🎉 SEG03 REGENERATION COMPLETE!")
        print(f"{'='*70}")
        print(f"\n✅ New image saved: {output_path}")
        print(f"\nNext steps:")
        print(f"1. View the image to validate")
        print(f"2. Check critical features:")
        print(f"   - Charizard: Orange body, teal wings, flaming tail")
        print(f"   - Dragonite: Light orange-tan (NOT green!), teal wings, antennae")
        print(f"   - Both Pokemon features VISIBLE (not silhouetted)")
        print(f"   - Size difference obvious (Dragonite 30% larger)")
        print(f"3. If PASS: Generate video from this image")
        print(f"4. If FAIL: Try again with adjusted prompt")
    else:
        print(f"\n❌ Regeneration failed. Check errors above.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
