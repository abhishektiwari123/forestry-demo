#!/usr/bin/env python3
"""
Test ALL photorealistic image generation models for Pokemon battle scenes.

Compares:
1. GPT 1.5 Image-to-Image: Transform existing image
2. Nano Banana Pro: Text-to-image generation
3. Flux 2 Pro Text-to-Image: Text-to-image with 16:9 + 2K support

Goal: Determine which produces the best photorealistic Pokemon battle scenes.
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
    """Compress image if needed."""
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


def wait_for_task(task_id: str, api_key: str, timeout: int = 300) -> dict:
    """Wait for task completion and return result."""
    headers = {"Authorization": f"Bearer {api_key}"}

    print(f"⏳ Generating... ", end="", flush=True)
    start_time = time.time()

    while time.time() - start_time < timeout:
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
                return data
            elif data.get("state") == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return None

    print(f"\n❌ Timeout")
    return None


def download_image(url: str, output: str) -> bool:
    """Download image from URL."""
    print(f"📥 Downloading...")

    img_resp = requests.get(url, timeout=30)
    if img_resp.status_code == 200:
        with open(output, 'wb') as f:
            f.write(img_resp.content)

        size_mb = os.path.getsize(output) / (1024 * 1024)
        print(f"✅ Saved: {size_mb:.2f} MB")
        return True
    else:
        print(f"❌ Download failed: {img_resp.status_code}")
        return False


def generate_gpt15_image(input_image_path: str, prompt: str, output: str, api_key: str) -> dict:
    """Generate image using GPT 1.5 Image-to-Image API."""
    print(f"\n{'='*60}")
    print("🎨 TEST 1: GPT 1.5 IMAGE-TO-IMAGE")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt[:100]}...")

    try:
        image_url = upload_image(input_image_path)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return {"success": False, "error": str(e)}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-image/1.5-image-to-image",
        "input": {
            "input_urls": [image_url],
            "prompt": prompt,
            "aspect_ratio": "3:2",
            "quality": "high"
        }
    }

    print("🚀 Submitting to GPT 1.5 Image-to-Image...")
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return {"success": False, "error": f"API Error {response.status_code}"}

    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        return {"success": False, "error": result.get('msg')}

    task_id = result["data"]["taskId"]
    data = wait_for_task(task_id, api_key)

    if data:
        image_url = json.loads(data["resultJson"])["resultUrls"][0]
        if download_image(image_url, output):
            duration = time.time() - start_time
            return {
                "success": True,
                "duration": duration,
                "size_mb": os.path.getsize(output) / (1024 * 1024),
                "output": output
            }

    return {"success": False, "error": "Generation failed"}


def generate_nanobanana_image(prompt: str, output: str, api_key: str) -> dict:
    """Generate image using Nano Banana Pro."""
    print(f"\n{'='*60}")
    print("🎨 TEST 2: NANO BANANA PRO")
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
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return {"success": False, "error": f"API Error {response.status_code}"}

    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        return {"success": False, "error": result.get('msg')}

    task_id = result["data"]["taskId"]
    data = wait_for_task(task_id, api_key)

    if data:
        image_url = json.loads(data["resultJson"])["resultUrls"][0]
        if download_image(image_url, output):
            duration = time.time() - start_time
            return {
                "success": True,
                "duration": duration,
                "size_mb": os.path.getsize(output) / (1024 * 1024),
                "output": output
            }

    return {"success": False, "error": "Generation failed"}


def generate_flux2_image(prompt: str, output: str, api_key: str) -> dict:
    """Generate image using Flux 2 Pro Text-to-Image."""
    print(f"\n{'='*60}")
    print("🎨 TEST 3: FLUX 2 PRO TEXT-TO-IMAGE")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt[:100]}...")
    print("🌟 Features: Native 16:9 support + 2K resolution")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "flux-2/pro-text-to-image",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",  # Perfect for video!
            "resolution": "2K"  # High quality!
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
        return {"success": False, "error": f"API Error {response.status_code}"}

    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        return {"success": False, "error": result.get('msg')}

    task_id = result["data"]["taskId"]
    data = wait_for_task(task_id, api_key)

    if data:
        image_url = json.loads(data["resultJson"])["resultUrls"][0]
        if download_image(image_url, output):
            duration = time.time() - start_time
            return {
                "success": True,
                "duration": duration,
                "size_mb": os.path.getsize(output) / (1024 * 1024),
                "output": output
            }

    return {"success": False, "error": "Generation failed"}


def main():
    print("="*60)
    print("🎯 COMPLETE PHOTOREALISTIC MODEL COMPARISON")
    print("="*60)
    print("\nComparing ALL models for Pokemon battle scenes:")
    print("  Test 1: GPT 1.5 Image-to-Image (transform existing)")
    print("  Test 2: Nano Banana Pro (text-to-image)")
    print("  Test 3: Flux 2 Pro Text-to-Image (16:9 + 2K)")
    print("="*60)

    # Load API key
    api_key = load_api_key()

    # Setup paths
    base_path = "charizard/battle_assets"
    input_image = f"{base_path}/frame_pairs/seg03_continuous_start_compressed.jpg"

    # Output paths
    results_dir = f"{base_path}/test_results"
    os.makedirs(results_dir, exist_ok=True)

    gpt15_output = f"{results_dir}/gpt15_photorealistic.jpg"
    nanobanana_output = f"{results_dir}/nanobanana_photorealistic.jpg"
    flux2_output = f"{results_dir}/flux2_photorealistic.jpg"

    # Test prompt
    prompt = """Photorealistic epic Pokemon battle scene: Charizard (5'7" orange fire dragon with powerful wings) launching massive orange Flamethrower stream at significantly larger Dragonite (7'3", 30% bigger, bulkier muscular body with cream belly) barrel-rolling to evade, intense high-speed aerial combat, fire trails streaming, wings with orange upper surface matching body color and teal turquoise underside membranes visible, dramatic action lighting, smoke and flames, cinematic photography, hyperrealistic details, 8K quality"""

    # Run all tests
    results = {}

    # TEST 1: GPT 1.5
    results['gpt15'] = generate_gpt15_image(input_image, prompt, gpt15_output, api_key)

    # TEST 2: Nano Banana Pro
    results['nanobanana'] = generate_nanobanana_image(prompt, nanobanana_output, api_key)

    # TEST 3: Flux 2 Pro
    results['flux2'] = generate_flux2_image(prompt, flux2_output, api_key)

    # RESULTS SUMMARY
    print(f"\n{'='*60}")
    print("🎉 COMPLETE COMPARISON RESULTS")
    print(f"{'='*60}")

    print("\n📊 GENERATION STATS:")
    print(f"\n{'Model':<25} {'Status':<12} {'Time':<10} {'Size':<10}")
    print("-" * 60)

    for model_name, model_label in [
        ('gpt15', 'GPT 1.5 Image-to-Image'),
        ('nanobanana', 'Nano Banana Pro'),
        ('flux2', 'Flux 2 Pro')
    ]:
        result = results[model_name]
        if result['success']:
            status = "✅ Success"
            duration = f"{result['duration']:.1f}s"
            size = f"{result['size_mb']:.2f} MB"
        else:
            status = "❌ Failed"
            duration = "-"
            size = "-"

        print(f"{model_label:<25} {status:<12} {duration:<10} {size:<10}")

    # Detailed comparison
    successful = [k for k, v in results.items() if v['success']]

    if len(successful) >= 2:
        print("\n🎬 VISUAL COMPARISON:")
        print("  Compare the generated images side-by-side")
        print("  Consider:")
        print("    ✓ Pokemon character accuracy")
        print("    ✓ Size differentiation (Dragonite 30% bigger)")
        print("    ✓ Wing color accuracy (teal undersides)")
        print("    ✓ Photorealism quality")
        print("    ✓ Cinematic lighting and composition")
        print("    ✓ Suitability for video generation")
        print("    ✓ Generation speed and efficiency")

        print("\n💡 KEY FEATURES:")
        print("  • GPT 1.5: Transforms existing images")
        print("  • Nano Banana Pro: Fast text-to-image generation")
        print("  • Flux 2 Pro: Native 16:9 aspect ratio + 2K resolution")

        print("\n📁 OUTPUT FILES:")
        for model_name, model_label in [
            ('gpt15', 'GPT 1.5'),
            ('nanobanana', 'Nano Banana Pro'),
            ('flux2', 'Flux 2 Pro')
        ]:
            if results[model_name]['success']:
                print(f"  • {model_label}: {results[model_name]['output']}")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
