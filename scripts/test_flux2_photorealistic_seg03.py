#!/usr/bin/env python3
"""
Test Flux 2 Pro for photorealistic Seg03 regeneration.
Using simplified prompts to avoid NSFW filters while maintaining photorealism.
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
    """Generate image with Flux 2 Pro."""
    print(f"\n{'='*70}")
    print("🎨 FLUX 2 PRO - PHOTOREALISTIC SEG03 TEST")
    print(f"{'='*70}")
    print(f"\n📝 Simplified prompt (to avoid NSFW filter):")
    print(f"{prompt[:200]}...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "flux-2/pro-text-to-image",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "resolution": "2K"
        }
    }

    print("\n🚀 Submitting to Flux 2 Pro...")
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
                    return True

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                print(f"Fail Code: {data.get('failCode')}")
                return False

    print(f"\n❌ Timeout")
    return False


def main():
    print("="*70)
    print("FLUX 2 PRO PHOTOREALISTIC TEST - SEG03")
    print("="*70)
    print("\nGoal: Generate photorealistic dragon battle scene")
    print("Challenge: Avoid NSFW filter while maintaining realism")
    print("="*70)

    api_key = load_api_key()

    # Simplified prompt avoiding Pokemon-specific terms
    # Focus on photorealistic dragon description
    prompt = """Photorealistic CGI render: small athletic orange dragon with teal turquoise wing membranes standing on volcanic ground looking up at significantly larger bulky orange-tan dragon with teal wings and two antennae descending from dramatic stormy sky with lightning and dark clouds, both dragons have realistic reptilian scales texture, detailed leathery wings, cream colored belly with scales, fierce battle-ready expressions, breaks in storm clouds creating dramatic lighting that illuminates both creatures showing detailed features and textures, epic confrontation scene, cinematic photography, 8K quality, hyperrealistic dragon anatomy based on reptiles and bats, natural lighting, detailed scale patterns, weathered battle-worn appearance, volcanic valley background with rocky terrain"""

    output_path = "charizard/battle_assets/test_results/seg03_flux2_photorealistic.jpg"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    success = generate_image(prompt, output_path, api_key)

    if success:
        print(f"\n{'='*70}")
        print("🎉 FLUX 2 PRO TEST COMPLETE!")
        print(f"{'='*70}")
        print(f"\n✅ Image saved: {output_path}")
        print(f"\nNext: Compare with Nano Banana Pro version")
        print(f"\nComparison:")
        print(f"  3D Animated: charizard/battle_assets/frame_pairs/seg03_continuous_start_v2.jpg")
        print(f"  Photorealistic: {output_path}")
    else:
        print(f"\n❌ Generation failed")
        print(f"\nTroubleshooting:")
        print(f"  - If NSFW filter triggered: Simplify prompt further")
        print(f"  - If timeout: Retry (Flux 2 Pro takes 90-120s)")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
