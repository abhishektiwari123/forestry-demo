#!/usr/bin/env python3
"""
Test GPT 1.5 Image-to-Image vs Nano Banana Pro for photorealistic image generation.

Compares:
1. GPT 1.5 Image-to-Image: Transform existing image to photorealistic version
2. Nano Banana Pro: Generate photorealistic image from prompt

Goal: Determine which produces better photorealistic Pokemon battle scenes.
"""

import os
import sys
import time
import requests
import json
import subprocess
from pathlib import Path

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


def compress_image(image_path: str, max_size_mb: float = 10.0) -> str:
    """Compress image if needed (GPT 1.5 max 10MB)."""
    size_mb = os.path.getsize(image_path) / (1024 * 1024)

    if size_mb <= max_size_mb:
        print(f"✅ Image size OK: {size_mb:.2f} MB")
        return image_path

    print(f"⚠️  Image too large ({size_mb:.2f} MB), compressing...")
    compressed = image_path.replace('.jpg', '_compressed.jpg')

    subprocess.run([
        'ffmpeg', '-y', '-i', image_path,
        '-q:v', '5',
        '-vf', 'scale=\'min(1920,iw)\':\'min(1080,ih)\':force_original_aspect_ratio=decrease',
        compressed
    ], check=True, capture_output=True, timeout=30)

    new_size = os.path.getsize(compressed) / (1024 * 1024)
    print(f"✅ Compressed: {size_mb:.2f} MB → {new_size:.2f} MB")
    return compressed


def upload_image(image_path: str) -> str:
    """Upload image to imgcdn.dev."""
    upload_path = compress_image(image_path, max_size_mb=10.0)

    print(f"📤 Uploading {os.path.basename(upload_path)}...")

    with open(upload_path, 'rb') as f:
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
            print(f"✅ Uploaded: {url}")
            return url

    raise Exception(f"Upload failed: {response.status_code}")


def generate_gpt15_image(input_image_path: str, prompt: str, output: str, api_key: str) -> bool:
    """Generate image using GPT 1.5 Image-to-Image API."""
    print(f"\n{'='*60}")
    print("🎨 GPT 1.5 IMAGE-TO-IMAGE API")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt[:100]}...")

    # Upload input image
    try:
        image_url = upload_image(input_image_path)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-image/1.5-image-to-image",
        "input": {
            "input_urls": [image_url],
            "prompt": prompt,
            "aspect_ratio": "3:2",  # Closest to 16:9
            "quality": "high"  # Best quality for photorealism
        }
    }

    print("🚀 Submitting to GPT 1.5 Image-to-Image...")
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

    start_time = time.time()
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
                    with open(output, 'wb') as f:
                        f.write(img_resp.content)

                    size_mb = os.path.getsize(output) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                    return True
                else:
                    print(f"❌ Download failed: {img_resp.status_code}")
                    return False

            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False

    print(f"\n❌ Timeout")
    return False


def generate_nanobanana_image(prompt: str, output: str, api_key: str) -> bool:
    """Generate image using Nano Banana Pro (text-to-image)."""
    print(f"\n{'='*60}")
    print("🎨 NANO BANANA PRO")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt[:100]}...")

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

    start_time = time.time()
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
                    with open(output, 'wb') as f:
                        f.write(img_resp.content)

                    size_mb = os.path.getsize(output) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
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
    print("="*60)
    print("🎯 GPT 1.5 IMAGE-TO-IMAGE vs NANO BANANA PRO TEST")
    print("="*60)
    print("\nGoal: Compare photorealistic image generation")
    print("  Test 1: GPT 1.5 Image-to-Image (transform existing)")
    print("  Test 2: Nano Banana Pro (generate from text)")
    print("="*60)

    # Load API key
    api_key = load_api_key()

    # Define test
    base_path = "charizard/battle_assets"
    # Use compressed image to avoid upload issues
    input_image = f"{base_path}/frame_pairs/seg03_continuous_start_compressed.jpg"

    # Check if input exists
    if not os.path.exists(input_image):
        print(f"❌ Input image not found: {input_image}")
        print("\nAvailable images:")
        for img in Path(f"{base_path}/frame_pairs").glob("*.jpg"):
            print(f"  - {img}")
        return

    print(f"\n📸 Input Image: {os.path.basename(input_image)}")
    input_size = os.path.getsize(input_image) / (1024 * 1024)
    print(f"   Size: {input_size:.2f} MB")

    # Output paths
    gpt15_output = f"{base_path}/test_results/gpt15_photorealistic.jpg"
    nanobanana_output = f"{base_path}/test_results/nanobanana_photorealistic.jpg"

    # Create output directory
    os.makedirs(f"{base_path}/test_results", exist_ok=True)

    # Test prompt - photorealistic Pokemon battle
    prompt = """Photorealistic epic Pokemon battle scene: Charizard (5'7" orange fire dragon with powerful wings) launching massive orange Flamethrower stream at significantly larger Dragonite (7'3", 30% bigger, bulkier muscular body with cream belly) barrel-rolling to evade, intense high-speed aerial combat, fire trails streaming, wings with orange upper surface matching body color and teal turquoise underside membranes visible, dramatic action lighting, smoke and flames, cinematic photography, hyperrealistic details, 8K quality"""

    # TEST 1: GPT 1.5 Image-to-Image
    print(f"\n{'='*60}")
    print("TEST 1: GPT 1.5 IMAGE-TO-IMAGE")
    print(f"{'='*60}")

    gpt15_success = generate_gpt15_image(input_image, prompt, gpt15_output, api_key)

    # TEST 2: Nano Banana Pro
    print(f"\n{'='*60}")
    print("TEST 2: NANO BANANA PRO")
    print(f"{'='*60}")

    nanobanana_success = generate_nanobanana_image(prompt, nanobanana_output, api_key)

    # RESULTS
    print(f"\n{'='*60}")
    print("🎉 COMPARISON TEST COMPLETE!")
    print(f"{'='*60}")

    print("\n📊 RESULTS:")
    print(f"  GPT 1.5 Image-to-Image: {'✅ Success' if gpt15_success else '❌ Failed'}")
    if gpt15_success:
        print(f"    → {gpt15_output}")

    print(f"  Nano Banana Pro:        {'✅ Success' if nanobanana_success else '❌ Failed'}")
    if nanobanana_success:
        print(f"    → {nanobanana_output}")

    if gpt15_success and nanobanana_success:
        print("\n🎬 EVALUATION:")
        print("  Compare both images side-by-side:")
        print("  ✓ Which looks more photorealistic?")
        print("  ✓ Which maintains Pokemon character accuracy?")
        print("  ✓ Which has better lighting and detail?")
        print("  ✓ Which is better for video generation?")

        print("\n💡 NEXT STEPS:")
        print("  1. View both images")
        print("  2. Choose best model for photorealistic generation")
        print("  3. Use chosen model for all 18 segments")


if __name__ == "__main__":
    main()
