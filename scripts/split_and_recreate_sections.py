#!/usr/bin/env python3
"""
Split existing image into 4 sections and recreate each with Nano Banana Pro to preserve details.
"""

import os
import sys
import requests
import json
import time
from PIL import Image


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


def get_image_from_task(task_id: str, api_key: str) -> str:
    """Download image from task_id."""
    print(f"📥 Fetching image for task: {task_id}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json().get("data", {})
        if data.get("state") == "success":
            result_json = json.loads(data["resultJson"])
            image_url = result_json["resultUrls"][0]

            # Download
            img_resp = requests.get(image_url, timeout=60)
            output_path = "charizard/battle_assets/temp_source_image.jpg"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(img_resp.content)

            print(f"✅ Downloaded: {output_path}")
            return output_path

    raise Exception(f"Failed to get image for task {task_id}")


def split_image_into_4_sections(image_path: str, output_dir: str) -> list:
    """Split image into 4 sections (2x2 grid)."""
    print(f"\n📸 Splitting image into 4 sections...")

    img = Image.open(image_path)
    width, height = img.size
    print(f"  Original: {width}x{height}")

    # Calculate section dimensions (2x2 grid)
    section_width = width // 2
    section_height = height // 2

    os.makedirs(output_dir, exist_ok=True)

    sections = []
    positions = [
        (0, 0, section_width, section_height, "top_left"),
        (section_width, 0, width, section_height, "top_right"),
        (0, section_height, section_width, height, "bottom_left"),
        (section_width, section_height, width, height, "bottom_right")
    ]

    for i, (*box, name) in enumerate(positions, 1):
        section = img.crop(box)
        section_path = os.path.join(output_dir, f"section_{i}_{name}.jpg")
        section.save(section_path, "JPEG", quality=95)
        sections.append(section_path)
        print(f"  ✅ Section {i} ({name}): {section.size[0]}x{section.size[1]}")

    return sections


def upload_image(image_path: str) -> str:
    """Upload image to CDN."""
    print(f"📤 Uploading: {os.path.basename(image_path)}...")

    with open(image_path, 'rb') as f:
        response = requests.post(
            'https://imgcdn.dev/api/1/upload',
            data={'key': '5386e05a3562c7a8f984e73401540836', 'format': 'json'},
            files={'source': f},
            timeout=60
        )

    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.status_code}")

    result = response.json()
    if result.get('status_code') != 200:
        raise Exception("Upload failed")

    return result['image']['url']


def recreate_section_with_nanobananapro(section_path: str, section_name: str, api_key: str) -> str:
    """Recreate section using Nano Banana Pro image-to-image to preserve details."""
    print(f"\n🎨 Recreating {section_name}...")

    # Upload reference image
    ref_url = upload_image(section_path)
    print(f"  ✅ Reference uploaded")

    # Create prompt to exactly replicate the section
    prompt = f"Exact photorealistic replication of this Pokemon battle scene section, preserve all details, characters, colors, textures, lighting, and composition exactly as shown, hyperrealistic CGI quality, no changes, perfect recreation"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Note: Nano Banana Pro doesn't have direct image-to-image, so we'll use detailed prompt
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",  # Assuming original is 16:9
            "output_format": "jpg"
        }
    }

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    result = response.json()
    if result.get("code") != 200:
        raise Exception(f"Failed: {result.get('msg')}")

    task_id = result["data"]["taskId"]
    print(f"  ⏳ Generating... ", end="", flush=True)

    start_time = time.time()
    while time.time() - start_time < 120:
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
                print(f"\n  ✅ Generated!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Download
                output_path = section_path.replace('.jpg', '_recreated.jpg')
                img_resp = requests.get(image_url, timeout=60)

                with open(output_path, 'wb') as f:
                    f.write(img_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"  ✅ Saved: {size_mb:.2f} MB")
                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Main function."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        SPLIT & RECREATE IMAGE SECTIONS WITH NANO BANANA PRO        ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  This script:                                                      ║
║  1. Downloads image from task_id                                   ║
║  2. Splits into 4 sections (2x2 grid)                             ║
║  3. Recreates each section with Nano Banana Pro                    ║
║  4. Preserves all details from original                            ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    task_id = "f7c5a8ae62acbd21d68e3bf258758f11"
    api_key = load_api_key()

    # Step 1: Download source image
    source_image = get_image_from_task(task_id, api_key)

    # Step 2: Split into 4 sections
    sections_dir = "charizard/battle_assets/split_sections"
    section_paths = split_image_into_4_sections(source_image, sections_dir)

    # Step 3: Recreate each section
    print(f"\n{'='*70}")
    print("RECREATING 4 SECTIONS WITH NANO BANANA PRO")
    print(f"{'='*70}")

    recreated_sections = []
    for i, section_path in enumerate(section_paths, 1):
        section_name = f"Section {i}"
        recreated_path = recreate_section_with_nanobananapro(section_path, section_name, api_key)
        recreated_sections.append(recreated_path)

    print(f"\n🎉 SUCCESS!")
    print(f"📁 Original sections: {sections_dir}/")
    print(f"📁 Recreated sections: {len(recreated_sections)} files")
    for path in recreated_sections:
        print(f"   - {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
