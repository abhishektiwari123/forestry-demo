#!/usr/bin/env python3
"""
Regenerate Scene 2 (impact_pain) - previous download was corrupted.
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


def generate_scene_image(prompt: str, output_path: str, api_key: str) -> str:
    """Generate full resolution scene image."""
    print(f"\n🎨 Regenerating Scene 2...")
    print(f"📝 Prompt: {prompt[:120]}...")

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
    print(f"⏳ Generating... ", end="", flush=True)

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
                print(f"\n✅ Generated!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Download image with retry logic
                max_retries = 4
                retry_delays = [2, 4, 8, 16]

                for attempt in range(max_retries):
                    try:
                        img_resp = requests.get(image_url, timeout=60)

                        if img_resp.status_code == 200 and len(img_resp.content) > 10000:
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)

                            with open(output_path, 'wb') as f:
                                f.write(img_resp.content)

                            # Check resolution
                            img = Image.open(output_path)
                            size_mb = os.path.getsize(output_path) / (1024 * 1024)
                            print(f"✅ Saved: {img.size[0]}x{img.size[1]}, {size_mb:.2f} MB")
                            return output_path
                        else:
                            if attempt < max_retries - 1:
                                delay = retry_delays[attempt]
                                print(f"⚠️  Download issue (size: {len(img_resp.content)} bytes), retrying in {delay}s...")
                                time.sleep(delay)
                            else:
                                raise Exception(f"Download failed after {max_retries} attempts")

                    except Exception as e:
                        if attempt < max_retries - 1:
                            delay = retry_delays[attempt]
                            print(f"⚠️  Download error ({str(e)}), retrying in {delay}s...")
                            time.sleep(delay)
                        else:
                            raise Exception(f"Download failed after {max_retries} attempts: {str(e)}")

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Regenerate Scene 2 with improved download handling."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                     REGENERATE SCENE 2                             ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Previous Scene 2 download was corrupted (252 bytes)               ║
║  Regenerating with improved retry logic                            ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    scene2 = {
        "name": "scene2_impact_pain",
        "camera_angle": "Side-angle medium shot",
        "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Massive orange-red Flamethrower stream STRIKING Dragonite torso with bright impact glow and heat distortion, Dragonite with PAINED expression (eyes squinting in pain, mouth open wide showing teeth, face contorted in distress), body being PUSHED BACKWARD by force of flames with visible knockback motion, arms raised defensively, side-angle medium shot emphasizing impact and reaction, Charizard partially visible on LEFT maintaining attack, volcanic valley background, dramatic intensity 8K quality, no frames or borders",
        "path": "charizard/battle_assets/clean_4scenes/scene2_impact_pain.jpg"
    }

    print(f"\nCamera Angle: {scene2['camera_angle']}")

    try:
        image_path = generate_scene_image(scene2['prompt'], scene2['path'], api_key)
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Scene 2 regenerated successfully")
        print(f"📁 Location: {image_path}")
        return 0
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
