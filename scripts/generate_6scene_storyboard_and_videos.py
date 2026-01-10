#!/usr/bin/env python3
"""
Generate 6-scene storyboard image, split into individual scenes, and create 5s videos.

This approach maintains consistency by:
1. Creating 1 complete 6-scene storyboard image (3x2 grid)
2. Splitting into 6 individual scene images
3. Generating 5s video from each scene using Kling 2.6
4. Concatenating into final 30s battle sequence
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


def generate_6scene_storyboard(api_key: str) -> str:
    """Generate 1 image containing 6 battle scenes in 3x2 grid layout."""
    print(f"\n{'='*70}")
    print("STEP 1: GENERATING 6-SCENE STORYBOARD IMAGE")
    print(f"{'='*70}")

    # Detailed prompt for complete 6-scene storyboard
    storyboard_prompt = """PHOTOREALISTIC hyperrealistic CGI storyboard with 6 panels in 3x2 grid layout showing Pokemon battle progression:

PANEL 1 (Top-Left): Charizard (5'7", lean orange dragon with realistic reptilian scales, teal wings, cream belly, flaming tail) on LEFT side launching massive orange-red Flamethrower stream from open jaws, flames just beginning, Dragonite (7'3", bulky ORANGE-TAN body, teal wings, antennae) visible on RIGHT in ready stance, volcanic valley background

PANEL 2 (Top-Center): Massive Flamethrower stream traveling across frame from left to right, intense orange-red flames with realistic fire physics, Charizard on LEFT maintaining attack, Dragonite on RIGHT bracing for impact, dramatic lighting

PANEL 3 (Top-Right): Flames STRIKING Dragonite's torso with bright impact glow, Dragonite with PAINED facial expression (eyes squinting, mouth open wide, face contorted), body being PUSHED BACKWARD by force, arms raised defensively, intense heat distortion at impact point

PANEL 4 (Bottom-Left): Flames fading around Dragonite, BURN MARKS APPEARING on torso and cream belly (blackened scorch marks, charred patterns, smoke wisping from burnt scales), Dragonite recovering from knockback stance, pain still evident in expression

PANEL 5 (Bottom-Center): Dragonite with visible burn damage on body, facial expression transitioning to FIERCE ANGER (eyes narrowing with rage, teeth bared in aggressive snarl, eyebrows furrowed showing intense determination for revenge), body tensing up for counter-attack, Charizard visible in background

PANEL 6 (Bottom-Right): Dragonite in dynamic CHARGING FORWARD pose moving from RIGHT toward LEFT with fierce angry expression, teal wings spread wide for acceleration, body in aggressive attack stance, burn marks still visible on torso, Charizard on LEFT bracing for incoming revenge attack

Consistent characters throughout all 6 panels, cinematic lighting, 8K quality, dramatic battle intensity, volcanic valley background visible in all panels"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": storyboard_prompt,
            "aspect_ratio": "16:9",  # Wide format for 3x2 grid
            "output_format": "jpg"
        }
    }

    print(f"📝 Prompt length: {len(storyboard_prompt)} characters")
    print(f"🚀 Submitting to Nano Banana Pro...")

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
    print(f"⏳ Generating storyboard... ", end="", flush=True)

    start_time = time.time()
    while time.time() - start_time < 180:
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
                print(f"\n✅ Storyboard generated!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                output_path = "charizard/battle_assets/storyboard/6scene_storyboard.jpg"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                img_resp = requests.get(image_url, timeout=60)
                with open(output_path, 'wb') as f:
                    f.write(img_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Saved: {size_mb:.2f} MB")
                print(f"📁 Location: {output_path}")
                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def split_storyboard_into_6_scenes(storyboard_path: str, output_dir: str) -> list:
    """Split 6-scene storyboard into individual scene images (3x2 grid)."""
    print(f"\n{'='*70}")
    print("STEP 2: SPLITTING STORYBOARD INTO 6 SCENES")
    print(f"{'='*70}")

    img = Image.open(storyboard_path)
    width, height = img.size
    print(f"  Storyboard: {width}x{height}")

    # Calculate scene dimensions (3 columns × 2 rows)
    scene_width = width // 3
    scene_height = height // 2

    os.makedirs(output_dir, exist_ok=True)

    scenes = []
    scene_names = [
        "scene1_charizard_launch",
        "scene2_flames_traveling",
        "scene3_impact_pain",
        "scene4_burn_marks",
        "scene5_angry_expression",
        "scene6_charge_forward"
    ]

    positions = [
        (0, 0, scene_width, scene_height),                           # Top-Left
        (scene_width, 0, 2*scene_width, scene_height),              # Top-Center
        (2*scene_width, 0, width, scene_height),                    # Top-Right
        (0, scene_height, scene_width, height),                      # Bottom-Left
        (scene_width, scene_height, 2*scene_width, height),         # Bottom-Center
        (2*scene_width, scene_height, width, height)                # Bottom-Right
    ]

    for i, (name, box) in enumerate(zip(scene_names, positions), 1):
        scene = img.crop(box)
        scene_path = os.path.join(output_dir, f"{name}.jpg")
        scene.save(scene_path, "JPEG", quality=95)
        scenes.append(scene_path)
        print(f"  ✅ Scene {i} ({name}): {scene.size[0]}x{scene.size[1]}")

    return scenes


def upload_image(image_path: str) -> str:
    """Upload image to CDN and return URL with retry logic."""
    print(f"  📤 Uploading: {os.path.basename(image_path)}...")

    max_retries = 4
    retry_delays = [2, 4, 8, 16]  # Exponential backoff

    for attempt in range(max_retries):
        try:
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
                    print(f"    ✅ URL: {image_url}")
                    return image_url

            # If we get here, upload failed
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                print(f"    ⚠️  Upload failed (status {response.status_code}), retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise Exception(f"Upload failed after {max_retries} attempts: {response.status_code}")

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                print(f"    ⚠️  Network error ({str(e)}), retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise Exception(f"Upload failed after {max_retries} attempts: {str(e)}")

    raise Exception("Upload failed")


def generate_video_from_scene(scene_path: str, scene_name: str, scene_prompt: str, api_key: str) -> str:
    """Generate 5s video from single scene image using Kling 2.6."""
    print(f"\n  🎬 Generating video for {scene_name}...")

    # Upload scene image
    scene_url = upload_image(scene_path)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": [scene_url],  # Single image (Kling Elements limitation)
            "prompt": scene_prompt,
            "duration": "5",
            "sound": True
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
    print(f"    Task ID: {task_id}")
    print(f"    ⏳ Generating... ", end="", flush=True)

    start_time = time.time()
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
                print(f"\n    ✅ Video complete!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Save video
                output_path = f"charizard/battle_assets/videos/storyboard_{scene_name}.mp4"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                vid_resp = requests.get(video_url, timeout=120)
                with open(output_path, 'wb') as f:
                    f.write(vid_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"    ✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def concatenate_videos(video_paths: list, output_path: str):
    """Concatenate 6 videos into final sequence."""
    print(f"\n{'='*70}")
    print("STEP 4: CONCATENATING 6 VIDEOS INTO FINAL SEQUENCE")
    print(f"{'='*70}")

    # Create concat list file
    concat_dir = os.path.dirname(output_path)
    concat_list_path = os.path.join(concat_dir, "concat_list_6scenes.txt")

    with open(concat_list_path, 'w') as f:
        for video_path in video_paths:
            # Use relative path from concat_list location
            rel_path = os.path.basename(video_path)
            f.write(f"file '{rel_path}'\n")

    print(f"📝 Concat list created with {len(video_paths)} videos")
    print(f"🎬 Concatenating...")

    import subprocess
    cmd = f'cd "{concat_dir}" && ffmpeg -y -f concat -safe 0 -i "{os.path.basename(concat_list_path)}" -c copy "{os.path.basename(output_path)}"'

    subprocess.run(cmd, shell=True, check=True)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ Final video created: {size_mb:.2f} MB")
    print(f"📁 Location: {output_path}")

    # Get video duration
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{output_path}"'
    duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
    print(f"⏱️  Duration: {duration:.1f}s")

    return output_path


def main():
    """Main pipeline."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║      6-SCENE STORYBOARD → SPLIT → 6 VIDEOS → FINAL SEQUENCE       ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Pipeline:                                                         ║
║  1. Generate 1 image with 6 battle scenes (3x2 grid)              ║
║  2. Split into 6 individual scene images                          ║
║  3. Generate 5s video from each scene (Kling 2.6)                 ║
║  4. Concatenate 6 videos into final 30s sequence                  ║
║                                                                    ║
║  This maintains visual consistency across all scenes!              ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Step 1: Generate 6-scene storyboard
    storyboard_path = generate_6scene_storyboard(api_key)

    # Step 2: Split into 6 scenes
    scenes_dir = "charizard/battle_assets/storyboard/scenes"
    scene_paths = split_storyboard_into_6_scenes(storyboard_path, scenes_dir)

    # Step 3: Generate videos from each scene
    print(f"\n{'='*70}")
    print("STEP 3: GENERATING 5S VIDEOS FROM EACH SCENE")
    print(f"{'='*70}")

    # Video prompts for each scene
    scene_prompts = [
        "Charizard launching massive Flamethrower attack from left side, flames beginning to stream from jaws, Dragonite on right bracing for impact, dramatic battle start, volcanic valley, cinematic camera movement",
        "Massive orange-red Flamethrower stream traveling across frame with realistic fire physics and intense heat distortion, dramatic lighting, volcanic valley background, cinematic intensity",
        "Flames striking Dragonite causing intense pain reaction and knockback, bright impact effects, Dragonite grimacing with arms raised defensively, body pushed backward by force, dramatic battle intensity",
        "Flames dissipating as burn marks appear on Dragonite's body, blackened scorch marks visible on torso, smoke rising from burnt scales, Dragonite recovering from knockback stance, realistic damage effects",
        "Dragonite's expression transitioning from pain to fierce anger, eyes narrowing with rage, teeth bared in aggressive snarl, body tensing for revenge counter-attack, dramatic character emotion",
        "Dragonite charging forward aggressively toward Charizard with wings spread wide, fierce attack stance, burn marks visible on battle-worn body, Charizard bracing for incoming revenge attack, dynamic action movement"
    ]

    video_paths = []
    for scene_path, prompt in zip(scene_paths, scene_prompts):
        scene_name = os.path.splitext(os.path.basename(scene_path))[0]
        video_path = generate_video_from_scene(scene_path, scene_name, prompt, api_key)
        video_paths.append(video_path)

    # Step 4: Concatenate all videos
    final_output = "charizard/battle_assets/videos/final_6scene_sequence_30s.mp4"
    final_video = concatenate_videos(video_paths, final_output)

    print(f"\n🎉 SUCCESS!")
    print(f"✅ Generated 6-scene storyboard")
    print(f"✅ Split into 6 individual scenes")
    print(f"✅ Generated 6 videos (5s each)")
    print(f"✅ Concatenated into final 30s sequence")
    print(f"\n📁 Storyboard: {storyboard_path}")
    print(f"📁 Scenes: {scenes_dir}/")
    print(f"📁 Final Video: {final_video}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
