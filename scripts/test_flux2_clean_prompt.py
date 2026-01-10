#!/usr/bin/env python3
"""
Test Flux 2 Pro with cleaned prompt to avoid NSFW filters.
"""

import os
import time
import requests
import json

def load_api_key() -> str:
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


def generate_flux2_image(prompt: str, output: str, api_key: str) -> dict:
    """Generate image using Flux 2 Pro Text-to-Image."""
    print(f"\n{'='*60}")
    print("🎨 FLUX 2 PRO TEXT-TO-IMAGE (CLEAN PROMPT)")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt}")

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

    print("🚀 Submitting to Flux 2 Pro...")
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return {"success": False}

    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        return {"success": False}

    task_id = result["data"]["taskId"]
    print(f"⏳ Generating (Task: {task_id})... ", end="", flush=True)

    while time.time() - start_time < 300:
        time.sleep(5)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            if data.get("state") == "success":
                print(f"\n✅ Generated!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]
                print(f"📥 Downloading from: {image_url}")

                img_resp = requests.get(image_url, timeout=30)
                if img_resp.status_code == 200:
                    with open(output, 'wb') as f:
                        f.write(img_resp.content)

                    size_mb = os.path.getsize(output) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                    return {"success": True, "duration": duration, "size_mb": size_mb}

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                print(f"Fail Code: {data.get('failCode')}")
                return {"success": False, "error": data.get('failMsg')}

    print(f"\n❌ Timeout")
    return {"success": False}


def main():
    print("="*60)
    print("🧪 FLUX 2 PRO - CLEAN PROMPT TEST")
    print("="*60)

    api_key = load_api_key()

    # Try multiple prompt variations
    prompts = [
        # Prompt 1: Very clean, family-friendly
        {
            "name": "Clean Family-Friendly",
            "text": "Two friendly dragon creatures in an aerial dance, one orange with wings breathing fire, one larger cream-colored with teal wing membranes, beautiful sky background, cinematic lighting, photorealistic 3D render",
            "file": "charizard/battle_assets/test_results/flux2_clean_v1.jpg"
        },
        # Prompt 2: More specific but still safe
        {
            "name": "Pokemon-Style Animation",
            "text": "Charizard and Dragonite Pokemon characters in mid-air, orange fire-type breathing flames, larger dragon-type with teal wings, epic sky battle scene, high quality 3D animation style, dramatic lighting",
            "file": "charizard/battle_assets/test_results/flux2_clean_v2.jpg"
        },
        # Prompt 3: Simplified
        {
            "name": "Simple Description",
            "text": "Orange dragon breathing fire at larger cream-colored dragon with teal wings, flying in sky, cinematic photography, 8K quality",
            "file": "charizard/battle_assets/test_results/flux2_clean_v3.jpg"
        }
    ]

    results = []

    for i, prompt_config in enumerate(prompts, 1):
        print(f"\n{'='*60}")
        print(f"ATTEMPT {i}/3: {prompt_config['name']}")
        print(f"{'='*60}")

        result = generate_flux2_image(
            prompt_config['text'],
            prompt_config['file'],
            api_key
        )

        results.append({
            "name": prompt_config['name'],
            "success": result.get('success', False),
            "file": prompt_config['file'] if result.get('success') else None
        })

        if result.get('success'):
            print(f"\n🎉 SUCCESS! Found working prompt.")
            break
        else:
            print(f"\n⚠️  Attempt {i} failed, trying next prompt...")

    # Summary
    print(f"\n{'='*60}")
    print("📊 FLUX 2 PRO TEST SUMMARY")
    print(f"{'='*60}")

    for i, result in enumerate(results, 1):
        status = "✅ Success" if result['success'] else "❌ Failed"
        print(f"  {i}. {result['name']:<30} {status}")
        if result['file']:
            print(f"     → {result['file']}")

    successful = [r for r in results if r['success']]

    if successful:
        print(f"\n✅ Flux 2 Pro CAN generate Pokemon content with clean prompts!")
        print(f"   Working prompt: {successful[0]['name']}")
    else:
        print(f"\n❌ Flux 2 Pro content filter too strict for Pokemon battles")
        print(f"   Recommendation: Use Nano Banana Pro instead")


if __name__ == "__main__":
    main()
