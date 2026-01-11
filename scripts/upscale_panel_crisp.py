#!/usr/bin/env python3
"""
Recraft Crisp Upscale - True Faithful Image Upscaling
Uses Recraft's dedicated Crisp Upscale mode that increases resolution WITHOUT altering content.

KEY DIFFERENCE:
- Crisp Mode: Increases resolution and sharpness WITHOUT altering structure or content
- Creative Mode: Enhances resolution while subtly regenerating content (we DON'T use this)

Crisp mode maintains "exact visual consistency" by avoiding content regeneration—ideal
when you need higher resolution without modifications to the original image.

Source: https://kie.ai/recraft-crisp-upscale
"""

import os
import sys
import requests
import json
import time
from PIL import Image


def load_api_key():
    """Load API key from .env file."""
    env_paths = ['scripts/.env', '.env', '/home/user/forestry-demo/.env', '/home/user/forestry-demo/scripts/.env']
    for path in env_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('KIE_API_KEY='):
                        return line.strip().split('=', 1)[1]
    raise Exception("❌ KIE_API_KEY not found")


def upload_image(image_path: str) -> str:
    """Upload image to imgcdn.dev."""
    print(f"\n📤 Uploading image: {os.path.basename(image_path)}")

    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.2f} MB")

    with open(image_path, 'rb') as f:
        response = requests.post(
            'https://imgcdn.dev/api/1/upload',
            data={'key': '5386e05a3562c7a8f984e73401540836', 'format': 'json'},
            files={'source': f},
            timeout=60
        )

    if response.status_code == 200:
        result = response.json()
        if result.get('status_code') == 200:
            image_url = result['image']['url']
            print(f"   ✅ Uploaded: {image_url}")
            return image_url

    raise Exception(f"Upload failed: {response.status_code}")


def upscale_crisp(image_url: str, output_path: str, api_key: str, scale: int = 4) -> tuple:
    """Upscale image using Recraft Crisp Upscale (no content changes)."""

    print(f"\n🔍 Recraft Crisp Upscale - Content Preservation Mode")
    print(f"📝 Scale: {scale}x")
    print(f"🔒 Mode: CRISP (no structure/content alterations)")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Recraft Crisp Upscale API payload
    payload = {
        "model": "recraft/crisp-upscale",  # Dedicated upscaling model
        "input": {
            "image_urls": [image_url],
            "scale": scale,  # 2x or 4x
            "mode": "crisp",  # CRISP = preserve content, CREATIVE = regenerate
            "output_format": "jpg"
        }
    }

    print(f"🚀 Submitting to Recraft Crisp Upscale...")
    start_time = time.time()

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
    print(f"Task ID: {task_id}")
    print(f"⏳ Processing... ", end="", flush=True)

    timeout = 120  # 2 minutes (Recraft is faster: 3-10 seconds typically)

    while time.time() - start_time < timeout:
        time.sleep(3)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            state = data.get("state")

            if state == "success":
                print(f"\n✅ Upscaled!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Download upscaled image
                print(f"📥 Downloading crisp upscaled image...")
                img_resp = requests.get(image_url, timeout=120)
                if img_resp.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(img_resp.content)

                    img = Image.open(output_path)
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    duration = time.time() - start_time

                    print(f"✅ Saved: {img.size[0]}x{img.size[1]}, {size_mb:.2f} MB")
                    print(f"⏱️  Total time: {duration:.1f}s")

                    return output_path, task_id, image_url

            elif state == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Upscale image using Recraft Crisp mode (no content changes)."""
    import argparse

    parser = argparse.ArgumentParser(description='Recraft Crisp Upscale - faithful upscaling without content changes')
    parser.add_argument('image', help='Path to image to upscale')
    parser.add_argument('--scale', type=int, default=4, choices=[2, 4], help='Upscale factor (2x or 4x, default: 4)')
    parser.add_argument('--output', help='Output path for upscaled image', default=None)

    args = parser.parse_args()

    print("""
╔════════════════════════════════════════════════════════════════════╗
║           RECRAFT CRISP UPSCALE (True Faithful Mode)               ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  CRISP MODE FEATURES:                                              ║
║  ✓ Increases resolution WITHOUT altering structure                ║
║  ✓ Increases sharpness WITHOUT altering content                   ║
║  ✓ Maintains exact visual consistency                             ║
║  ✓ NO content regeneration (key difference)                       ║
║  ✓ Preserves textures and colors automatically                    ║
║  ✓ Removes noise and artifacts                                    ║
║  ✓ Fast processing (3-10 seconds typical)                         ║
║                                                                    ║
║  WHY CRISP MODE:                                                   ║
║  • CRISP: Resolution ↑ WITHOUT content changes ✓                  ║
║  • CREATIVE: Resolution ↑ WITH content regeneration ✗             ║
║                                                                    ║
║  PERFECT FOR: Storyboard panels where you want higher             ║
║  resolution but need to preserve exact composition                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    if not os.path.exists(args.image):
        print(f"❌ Image not found: {args.image}")
        return 1

    api_key = load_api_key()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        image_basename = os.path.splitext(os.path.basename(args.image))[0]
        image_dir = os.path.dirname(args.image)
        output_dir = image_dir.replace('_extracted', '_crisp_upscaled')
        if output_dir == image_dir:
            output_dir = os.path.join(image_dir, 'crisp_upscaled')
        output_path = os.path.join(output_dir, f"{image_basename}_crisp_{args.scale}x.jpg")

    try:
        # Upload original image
        image_url = upload_image(args.image)

        # Upscale with Recraft Crisp mode
        upscaled_path, task_id, upscaled_url = upscale_crisp(
            image_url, output_path, api_key, args.scale
        )

        print(f"\n{'='*70}")
        print(f"🎉 RECRAFT CRISP UPSCALE COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Original: {args.image}")
        print(f"📁 Upscaled: {upscaled_path}")
        print(f"🔍 Scale: {args.scale}x")
        print(f"⚙️  Mode: CRISP (content preservation)")
        print(f"🆔 Task ID: {task_id}")
        print(f"🔗 URL: {upscaled_url}")
        print(f"\n✅ CRISP MODE GUARANTEES:")
        print(f"  ✓ NO structure alterations")
        print(f"  ✓ NO content regeneration")
        print(f"  ✓ Exact visual consistency maintained")
        print(f"  ✓ Only resolution and sharpness increased")
        print(f"\n💡 This is the recommended method for faithful upscaling")
        print(f"📚 Source: https://kie.ai/recraft-crisp-upscale")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
