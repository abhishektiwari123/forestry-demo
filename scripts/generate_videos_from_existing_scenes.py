#!/usr/bin/env python3
"""
Generate 5s videos from existing 6 scene images and concatenate into final sequence.
"""

import os
import sys
import requests
import json
import time
import subprocess


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

    # Retry logic for API submission
    max_retries = 4
    retry_delays = [2, 4, 8, 16]
    task_id = None

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.kie.ai/api/v1/jobs/createTask",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    task_id = result["data"]["taskId"]
                    break
                else:
                    raise Exception(f"Failed: {result.get('msg')}")

            # Retry on 503 or other errors
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                print(f"    ⚠️  API Error ({response.status_code}), retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise Exception(f"API Error after {max_retries} attempts: {response.status_code}")

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                print(f"    ⚠️  Network error ({str(e)}), retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise Exception(f"API Error after {max_retries} attempts: {str(e)}")

    if not task_id:
        raise Exception("Failed to get task_id")
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
    print("STEP 2: CONCATENATING 6 VIDEOS INTO FINAL SEQUENCE")
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
║           GENERATE 6 VIDEOS FROM EXISTING SCENES                   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Using existing 6 scene images:                                    ║
║  - Scene 1: Charizard launching Flamethrower                       ║
║  - Scene 2: Flames traveling                                       ║
║  - Scene 3: Impact with pain reaction                              ║
║  - Scene 4: Burn marks appearing                                   ║
║  - Scene 5: Angry expression                                       ║
║  - Scene 6: Charging forward                                       ║
║                                                                    ║
║  Generating 5s video from each → Final 30s sequence               ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Existing scene paths
    scenes_dir = "charizard/battle_assets/storyboard/scenes"
    scene_files = [
        "scene1_charizard_launch.jpg",
        "scene2_flames_traveling.jpg",
        "scene3_impact_pain.jpg",
        "scene4_burn_marks.jpg",
        "scene5_angry_expression.jpg",
        "scene6_charge_forward.jpg"
    ]

    scene_paths = [os.path.join(scenes_dir, f) for f in scene_files]

    # Verify all scenes exist
    missing = [p for p in scene_paths if not os.path.exists(p)]
    if missing:
        print(f"❌ Missing scene files:")
        for p in missing:
            print(f"   - {p}")
        return 1

    print(f"✅ Found all 6 scene images")

    # Video prompts for each scene (simplified, no camera/validation terms)
    scene_prompts = [
        "Charizard launching massive Flamethrower attack, flames streaming from jaws, Dragonite bracing for impact, dramatic battle start, volcanic valley",
        "Massive orange-red Flamethrower stream traveling with realistic fire physics and intense heat distortion, dramatic lighting, volcanic valley background",
        "Flames striking Dragonite causing intense pain reaction and knockback, bright impact effects, Dragonite grimacing with arms raised defensively, body pushed backward, dramatic battle intensity",
        "Flames dissipating as burn marks appear on Dragonite body, blackened scorch marks visible on torso, smoke rising from burnt scales, Dragonite recovering from knockback, realistic damage effects",
        "Dragonite expression transitioning from pain to fierce anger, eyes narrowing with rage, teeth bared in aggressive snarl, body tensing for revenge counter-attack, dramatic emotion",
        "Dragonite charging forward aggressively toward Charizard with wings spread wide, fierce attack stance, burn marks visible on battle-worn body, Charizard bracing for incoming revenge attack"
    ]

    # Generate videos from each scene
    print(f"\n{'='*70}")
    print("STEP 1: GENERATING 5S VIDEOS FROM 6 SCENES")
    print(f"{'='*70}")

    video_paths = []
    for scene_path, prompt in zip(scene_paths, scene_prompts):
        scene_name = os.path.splitext(os.path.basename(scene_path))[0]
        video_path = generate_video_from_scene(scene_path, scene_name, prompt, api_key)
        video_paths.append(video_path)

    # Concatenate all videos
    final_output = "charizard/battle_assets/videos/final_6scene_sequence_30s.mp4"
    final_video = concatenate_videos(video_paths, final_output)

    print(f"\n🎉 SUCCESS!")
    print(f"✅ Generated 6 videos (5s each)")
    print(f"✅ Concatenated into final 30s sequence")
    print(f"\n📁 Videos: charizard/battle_assets/videos/storyboard_scene*.mp4")
    print(f"📁 Final Video: {final_video}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
