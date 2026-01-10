#!/usr/bin/env python3
"""
Generate 4 separate progression images and create 10s video using Kling Elements API.

This creates:
1. Image 1: Charizard launching Flamethrower
2. Image 2: Flames hitting Dragonite with pain expression
3. Image 3: Dragonite with burn marks, angry expression
4. Image 4: Dragonite charging forward for revenge

Then uses Kling Elements to generate a cohesive 10s video from all 4 images.
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


def generate_image(prompt: str, output_path: str, api_key: str) -> str:
    """Generate image using Nano Banana Pro."""
    print(f"\n🎨 Generating image...")
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


def upload_image(image_path: str) -> str:
    """Upload image to CDN and return URL."""
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

    image_url = result['image']['url']
    print(f"  ✅ Uploaded: {image_url}")
    return image_url


def generate_video_from_elements(image_urls: list, prompt: str, api_key: str) -> str:
    """Generate 10s video using Kling Elements API with 4 images."""
    print(f"\n{'='*70}")
    print(f"GENERATING 10S VIDEO FROM 4 IMAGES (KLING ELEMENTS)")
    print(f"{'='*70}")
    print(f"\n📝 Video Prompt:")
    print(f"{prompt}")
    print(f"\n🎨 Input Images: {len(image_urls)}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": image_urls,  # All 4 images for Elements
            "prompt": prompt,
            "duration": "10",
            "sound": True
        }
    }

    print(f"\n🚀 Submitting to Kling 2.6 Elements...")
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
    print(f"⏳ Generating... ", end="", flush=True)

    while time.time() - start_time < 300:
        time.sleep(10)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            if data.get("state") == "success":
                print(f"\n✅ Video generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                output_path = "charizard/battle_assets/videos/elements_4images_10s.mp4"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                vid_resp = requests.get(video_url, timeout=120)
                if vid_resp.status_code != 200:
                    raise Exception(f"Video download failed: {vid_resp.status_code}")

                with open(output_path, 'wb') as f:
                    f.write(vid_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                print(f"📁 Location: {output_path}")

                # Save task ID
                with open(output_path.replace('.mp4', '_task_id.txt'), 'w') as f:
                    f.write(task_id)

                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Main function."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║     KLING ELEMENTS: 4 PROGRESSION IMAGES TO 10S VIDEO              ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  This script:                                                      ║
║  1. Generates 4 separate images showing battle progression         ║
║  2. Uploads all 4 images to CDN                                    ║
║  3. Uses Kling Elements API to create cohesive 10s video          ║
║                                                                    ║
║  Elements maintains consistency across all 4 reference images.     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Define the 4 progression stages
    stages = [
        {
            "name": "Stage 1: Charizard Launching Flamethrower",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Charizard (5'7\", lean orange dragon with realistic detailed reptilian scales, teal wings, cream belly, flaming tail) on LEFT side launching massive orange-red Flamethrower stream from open jaws with fierce determined expression, flames just beginning to travel across frame toward right side, Dragonite (7'3\", bulky ORANGE-TAN body with realistic scales, teal wings, two antennae, cream belly stripes) visible on RIGHT side in ready battle stance, dramatic volcanic valley background, cinematic lighting, 8K quality, side-angle wide shot",
            "path": "charizard/battle_assets/progression/stage1_launch.jpg"
        },
        {
            "name": "Stage 2: Flames Hitting Dragonite with Pain",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Massive orange-red Flamethrower stream connecting from Charizard (5'7\", orange dragon on LEFT) to Dragonite (7'3\", ORANGE-TAN body on RIGHT) with flames STRIKING Dragonite's torso creating bright impact glow, Dragonite with PAINED FACIAL EXPRESSION (eyes squinting in pain, mouth open wide showing teeth in grimace, eyebrows furrowed, face contorted in distress), body being PUSHED BACKWARD by force of flames, arms raised defensively, physical knockback evident with body leaning back, intense heat distortion and fire sparks at impact point, dramatic battle intensity, volcanic valley background, cinematic lighting, 8K quality, side-angle wide shot",
            "path": "charizard/battle_assets/progression/stage2_impact.jpg"
        },
        {
            "name": "Stage 3: Dragonite with Burn Marks and Anger",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Dragonite (7'3\", bulky ORANGE-TAN body with realistic scales, teal wings, two antennae) in CENTER-RIGHT with VISIBLE BURN DAMAGE (blackened burnt scorch marks and charred patterns on torso and cream belly, smoke wisping from burnt scales showing realistic heat damage texture), flames dissipating around body, facial expression transitioning to FIERCE ANGER (eyes narrowing with determination and rage, teeth bared in aggressive snarl, eyebrows furrowed in fury showing intense resolve for revenge), body recovering from knockback stance, Charizard (5'7\", orange dragon) visible in background LEFT watching, dramatic lighting emphasizing damage and rage, volcanic valley background, 8K quality, side-angle shot",
            "path": "charizard/battle_assets/progression/stage3_anger.jpg"
        },
        {
            "name": "Stage 4: Dragonite Charging Forward for Revenge",
            "prompt": "PHOTOREALISTIC hyperrealistic CGI render: Dragonite (7'3\", bulky ORANGE-TAN body with visible burn marks on torso) in dynamic CHARGING FORWARD pose moving from RIGHT toward LEFT with fierce angry expression, teal wings spread wide pulling back for powerful acceleration, body in aggressive attack stance showing building momentum, burnt scorch marks still visible on torso creating battle-worn appearance, Charizard (5'7\", orange dragon with teal wings, flaming tail) visible on LEFT bracing for incoming revenge counter-attack, dramatic battle tension rising, volcanic valley background, cinematic lighting showing dramatic movement, 8K quality, side-angle wide shot capturing charge motion",
            "path": "charizard/battle_assets/progression/stage4_charge.jpg"
        }
    ]

    print(f"\n{'='*70}")
    print(f"STEP 1: GENERATING 4 PROGRESSION IMAGES")
    print(f"{'='*70}")

    image_paths = []
    for i, stage in enumerate(stages, 1):
        print(f"\n[{i}/4] {stage['name']}")
        image_path = generate_image(stage['prompt'], stage['path'], api_key)
        image_paths.append(image_path)

    print(f"\n{'='*70}")
    print(f"STEP 2: UPLOADING 4 IMAGES")
    print(f"{'='*70}")

    image_urls = []
    for image_path in image_paths:
        url = upload_image(image_path)
        image_urls.append(url)

    print(f"\n{'='*70}")
    print(f"STEP 3: GENERATING 10S VIDEO FROM 4 IMAGES")
    print(f"{'='*70}")

    video_prompt = """Complete Pokemon battle sequence showing smooth progression: Charizard launching Flamethrower attack, flames striking Dragonite causing pain and knockback, burn marks appearing on Dragonite's body with smoke, Dragonite's expression changing from pain to fierce anger, and Dragonite charging forward aggressively toward Charizard for revenge counter-attack. Maintain character consistency throughout, both Pokemon visible, smooth transitions between stages, dramatic battle intensity, realistic physics, volcanic valley background, cinematic action with dynamic camera movement"""

    video_path = generate_video_from_elements(image_urls, video_prompt, api_key)

    print(f"\n🎉 SUCCESS!")
    print(f"📊 Generated 10-second video from 4 progression images")
    print(f"📁 Video: {video_path}")
    print(f"📁 Images: charizard/battle_assets/progression/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
