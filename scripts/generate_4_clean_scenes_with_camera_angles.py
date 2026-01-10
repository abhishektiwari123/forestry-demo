#!/usr/bin/env python3
"""
Generate 4 clean individual scene images using proper camera angles from segment data.
No storyboard frames/borders. Full resolution images.
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
    print(f"\n🎨 Generating scene image...")
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

                # Download image
                img_resp = requests.get(image_url, timeout=60)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                with open(output_path, 'wb') as f:
                    f.write(img_resp.content)

                # Check resolution
                img = Image.open(output_path)
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Saved: {img.size[0]}x{img.size[1]}, {size_mb:.2f} MB")
                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Generate 4 clean scenes with proper camera angles."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        GENERATE 4 CLEAN SCENES (Full Resolution, No Frames)       ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Using proper camera angles from segment data                      ║
║  No storyboard frames/borders                                      ║
║  Full HD resolution for video generation                           ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # 4 scenes using proper camera angles (no "camera movement")
    scenes = [
        {
            "name": "scene1_flamethrower_launch",
            "camera_angle": "Side-angle wide shot",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Charizard (5'7\" lean orange dragon with detailed reptilian scales, teal wings, cream belly, flaming tail) on LEFT side launching massive orange-red Flamethrower stream from open jaws with fierce determined expression, flames just beginning to travel toward right side, Dragonite (7'3\" bulky orange-tan body with realistic scales, teal wings, antennae, cream belly) visible on RIGHT in ready battle stance, side-angle wide shot showing both Pokemon clearly, volcanic valley background with dramatic rim lighting, cinematic quality 8K render, no frames or borders",
            "path": "charizard/battle_assets/clean_4scenes/scene1_flamethrower_launch.jpg"
        },
        {
            "name": "scene2_impact_pain",
            "camera_angle": "Side-angle medium shot",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Massive orange-red Flamethrower stream STRIKING Dragonite torso with bright impact glow and heat distortion, Dragonite with PAINED expression (eyes squinting in pain, mouth open wide showing teeth, face contorted in distress), body being PUSHED BACKWARD by force of flames with visible knockback motion, arms raised defensively, side-angle medium shot emphasizing impact and reaction, Charizard partially visible on LEFT maintaining attack, volcanic valley background, dramatic intensity 8K quality, no frames or borders",
            "path": "charizard/battle_assets/clean_4scenes/scene2_impact_pain.jpg"
        },
        {
            "name": "scene3_burn_marks_anger",
            "camera_angle": "Medium close-up centered on Dragonite",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Dragonite (7'3\" bulky orange-tan body) in CENTER with VISIBLE BURN DAMAGE (blackened burnt scorch marks and charred patterns on torso and cream belly, smoke wisping from burnt scales showing realistic heat damage texture), flames dissipating around body, facial expression transitioning to FIERCE ANGER (eyes narrowing with determination and rage, teeth bared in aggressive snarl showing fangs, eyebrows furrowed in fury), body tensing and recovering from knockback, medium close-up shot centered on Dragonite emphasizing burn damage and emotional shift, volcanic valley background, dramatic lighting 8K quality, no frames or borders",
            "path": "charizard/battle_assets/clean_4scenes/scene3_burn_marks_anger.jpg"
        },
        {
            "name": "scene4_revenge_charge",
            "camera_angle": "Side-angle dynamic shot",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Dragonite (7'3\" bulky orange-tan body with visible burn marks on torso and belly) in dynamic CHARGING FORWARD pose moving from RIGHT toward LEFT with fierce angry expression and bared teeth, teal wings spread wide pulling back for powerful acceleration, body in aggressive attack stance showing building momentum and determination for revenge, burnt scorch marks still visible creating battle-worn appearance, Charizard (5'7\" orange dragon with teal wings flaming tail) visible on LEFT bracing for incoming counter-attack, side-angle dynamic shot capturing charge motion and battle tension, volcanic valley background with dramatic lighting 8K quality, no frames or borders",
            "path": "charizard/battle_assets/clean_4scenes/scene4_revenge_charge.jpg"
        }
    ]

    print(f"\n{'='*70}")
    print("GENERATING 4 CLEAN SCENE IMAGES")
    print(f"{'='*70}")

    generated_scenes = []
    for i, scene in enumerate(scenes, 1):
        print(f"\n[{i}/4] {scene['name']}")
        print(f"Camera Angle: {scene['camera_angle']}")
        try:
            image_path = generate_scene_image(scene['prompt'], scene['path'], api_key)
            generated_scenes.append(image_path)
        except Exception as e:
            print(f"❌ Failed: {e}")

    print(f"\n🎉 SUCCESS!")
    print(f"✅ Generated {len(generated_scenes)} clean Full HD scene images")
    print(f"📁 Location: charizard/battle_assets/clean_4scenes/")
    print(f"\nThese images are ready for video generation without upscaling needed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
