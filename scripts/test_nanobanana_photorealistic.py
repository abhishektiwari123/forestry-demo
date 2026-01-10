#!/usr/bin/env python3
"""
Test Nano Banana Pro with PHOTOREALISTIC prompt emphasis.
See if adding "photorealistic" keywords can shift from 3D animation to realistic style.
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
    print("🎨 NANO BANANA PRO - PHOTOREALISTIC PROMPT TEST")
    print(f"{'='*70}")
    print(f"\n📝 Prompt (with photorealistic emphasis):")
    print(f"{prompt[:250]}...")

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
    print("NANO BANANA PRO - PHOTOREALISTIC PROMPT TEST")
    print("="*70)
    print("\nHypothesis: Adding 'photorealistic' keywords may shift output style")
    print("="*70)

    api_key = load_api_key()

    # Enhanced prompt with heavy photorealistic emphasis
    prompt = """PHOTOREALISTIC hyperrealistic CGI render: Charizard (5 feet 7 inches, lean athletic orange fire dragon with realistic detailed reptilian scales, teal turquoise wing undersides with leathery texture, cream belly, flaming tail tip always burning) on volcanic ground looking up at significantly larger Dragonite (7 feet 3 inches, 30% bigger, bulky muscular stocky build, light ORANGE-tan body with realistic scales NOT green NOT blue, cream belly with horizontal stripes, teal turquoise wing membranes, two thin antennae on head, NO tail flame) descending from stormy sky with dramatic lightning, PHOTOREALISTIC detailed scale texture like real reptiles, breaks in storm clouds illuminate both Pokemon showing realistic detailed features, natural lighting with physically accurate shadows, weathered battle-worn appearance with scratches and imperfections, organic realistic textures, both Pokemon clearly visible and recognizable, dramatic epic confrontation, HYPERREALISTIC 8K quality cinematic photography, realistic dragon anatomy based on actual reptiles and bats, detailed leathery wings, volcanic valley background"""

    output_path = "charizard/battle_assets/test_results/seg03_nanobanana_photorealistic.jpg"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    success = generate_image(prompt, output_path, api_key)

    if success:
        print(f"\n{'='*70}")
        print("🎉 TEST COMPLETE!")
        print(f"{'='*70}")
        print(f"\n✅ Image saved: {output_path}")
        print(f"\nNext: Validate photorealism level")
        print(f"\nComparison files:")
        print(f"  Original (3D anim): charizard/battle_assets/frame_pairs/seg03_continuous_start_v2.jpg")
        print(f"  This test (photo?): {output_path}")
    else:
        print(f"\n❌ Generation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
