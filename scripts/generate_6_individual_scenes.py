#!/usr/bin/env python3
"""
Generate 6 individual scene images directly (no storyboard split to avoid frames/borders).
"""

import os
import sys
import requests
import json
import time


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
    """Generate individual scene image using Nano Banana Pro."""
    print(f"\n🎨 Generating scene image...")
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

                # Download image
                img_resp = requests.get(image_url, timeout=60)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                with open(output_path, 'wb') as f:
                    f.write(img_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Saved: {size_mb:.2f} MB")
                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Generate 6 individual scene images."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           GENERATE 6 INDIVIDUAL SCENE IMAGES (NO FRAMES)           ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Generating each scene as a separate clean image                   ║
║  No storyboard frames/borders/text                                 ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Scene definitions (clean images without frames)
    scenes = [
        {
            "name": "scene1_charizard_launch",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Charizard (5'7\" lean orange dragon with detailed reptilian scales, teal wings, cream belly, flaming tail) on LEFT side launching massive orange-red Flamethrower stream from open jaws, fierce determined expression, Dragonite (7'3\" bulky orange-tan body, teal wings, antennae) visible on RIGHT in ready battle stance, volcanic valley background, cinematic lighting, 8K quality, clean image no frames or borders",
            "path": "charizard/battle_assets/clean_scenes/scene1_charizard_launch.jpg"
        },
        {
            "name": "scene2_flames_traveling",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Massive orange-red Flamethrower stream traveling across frame from left to right, intense flames with realistic fire physics, heat distortion waves, Charizard on LEFT maintaining attack, Dragonite on RIGHT bracing, volcanic valley background, dramatic lighting, 8K quality, clean image no frames or borders",
            "path": "charizard/battle_assets/clean_scenes/scene2_flames_traveling.jpg"
        },
        {
            "name": "scene3_impact_pain",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Massive flames STRIKING Dragonite torso with bright impact glow, Dragonite with PAINED expression (eyes squinting, mouth open wide, face contorted), body being PUSHED BACKWARD by force, arms raised defensively, intense heat distortion at impact point, volcanic valley background, dramatic intensity, 8K quality, clean image no frames or borders",
            "path": "charizard/battle_assets/clean_scenes/scene3_impact_pain.jpg"
        },
        {
            "name": "scene4_burn_marks",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Flames dissipating around Dragonite, BURN MARKS APPEARING on torso and cream belly (blackened scorch marks, charred patterns, smoke wisping from burnt scales), Dragonite recovering from knockback stance, pain still evident in expression, Charizard visible in background LEFT, volcanic valley, 8K quality, clean image no frames or borders",
            "path": "charizard/battle_assets/clean_scenes/scene4_burn_marks.jpg"
        },
        {
            "name": "scene5_angry_expression",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Dragonite with visible burn damage on body, facial expression transitioning to FIERCE ANGER (eyes narrowing with rage, teeth bared in aggressive snarl, eyebrows furrowed showing intense determination), body tensing up for counter-attack, Charizard visible in background, volcanic valley, dramatic lighting, 8K quality, clean image no frames or borders",
            "path": "charizard/battle_assets/clean_scenes/scene5_angry_expression.jpg"
        },
        {
            "name": "scene6_charge_forward",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Dragonite in dynamic CHARGING FORWARD pose moving from RIGHT toward LEFT, fierce angry expression, teal wings spread wide for acceleration, aggressive attack stance, burn marks visible on battle-worn body, Charizard on LEFT bracing for incoming revenge attack, dramatic battle tension, volcanic valley, 8K quality, clean image no frames or borders",
            "path": "charizard/battle_assets/clean_scenes/scene6_charge_forward.jpg"
        }
    ]

    print(f"\n{'='*70}")
    print("GENERATING 6 CLEAN SCENE IMAGES")
    print(f"{'='*70}")

    generated_scenes = []
    for i, scene in enumerate(scenes, 1):
        print(f"\n[{i}/6] {scene['name']}")
        try:
            image_path = generate_scene_image(scene['prompt'], scene['path'], api_key)
            generated_scenes.append(image_path)
        except Exception as e:
            print(f"❌ Failed: {e}")

    print(f"\n🎉 SUCCESS!")
    print(f"✅ Generated {len(generated_scenes)} clean scene images (no frames/borders)")
    print(f"📁 Location: charizard/battle_assets/clean_scenes/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
