#!/usr/bin/env python3
"""
Generate 5s videos from 4 clean Full HD scene images with validation framework.
Core goal: Robust feedback loop and prompting strategy.
"""

import os
import sys
sys.path.insert(0, 'scripts')
import requests
import json
import time
import subprocess
from validation_framework import ValidationFramework, SCENE_IMAGE_CRITERIA, SCENE_VIDEO_CRITERIA


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
    retry_delays = [2, 4, 8, 16]

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


def generate_video_from_scene(scene_path: str, scene_name: str, scene_prompt: str, api_key: str, validator: ValidationFramework) -> str:
    """Generate 5s video from single scene image using Kling 2.6 with validation."""
    print(f"\n  🎬 Generating video for {scene_name}...")

    # VALIDATE IMAGE FIRST (core requirement)
    print(f"\n  {'='*68}")
    print(f"  IMAGE VALIDATION: {scene_name}")
    print(f"  {'='*68}")
    image_validation = validator.validate_image(scene_path, SCENE_IMAGE_CRITERIA)

    if not image_validation["passed"]:
        print(f"\n  ⚠️  Image validation issues found:")
        for issue in image_validation["issues"]:
            print(f"     - {issue}")
        print(f"  Continuing with video generation...")

    # Upload scene image
    scene_url = upload_image(scene_path)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": [scene_url],
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
                output_path = f"charizard/battle_assets/videos/clean4_{scene_name}.mp4"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                vid_resp = requests.get(video_url, timeout=120)
                with open(output_path, 'wb') as f:
                    f.write(vid_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"    ✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")

                # VALIDATE VIDEO (core requirement)
                print(f"\n  {'='*68}")
                print(f"  VIDEO VALIDATION: {scene_name}")
                print(f"  {'='*68}")
                video_validation = validator.validate_video(output_path, SCENE_VIDEO_CRITERIA)

                if not video_validation["passed"]:
                    print(f"\n  ⚠️  Video validation issues found:")
                    for issue in video_validation["issues"]:
                        print(f"     - {issue}")
                    print(f"  Consider regenerating with improved prompt")
                else:
                    print(f"  ✅ Video passed all validation checks")

                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def concatenate_videos(video_paths: list, output_path: str, validator: ValidationFramework):
    """Concatenate 4 videos into final sequence with validation."""
    print(f"\n{'='*70}")
    print("CONCATENATING 4 VIDEOS INTO FINAL SEQUENCE")
    print(f"{'='*70}")

    # Create concat list file
    concat_dir = os.path.dirname(output_path)
    concat_list_path = os.path.join(concat_dir, "concat_list_4clean_scenes.txt")

    with open(concat_list_path, 'w') as f:
        for video_path in video_paths:
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

    # VALIDATE FINAL VIDEO (core requirement)
    print(f"\n{'='*70}")
    print("FINAL VIDEO VALIDATION")
    print(f"{'='*70}")
    final_criteria = {
        "min_duration": 18.0,  # ~20s for 4 scenes
        "max_duration": 22.0,
        "min_size_mb": 30.0,
        "max_size_mb": 100.0,
        "must_have_audio": True
    }
    validator.validate_video(output_path, final_criteria)

    return output_path


def main():
    """Main pipeline with validation framework."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║     GENERATE 4 VIDEOS FROM CLEAN FULL HD SCENES + VALIDATION      ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Core Goal: Robust feedback loop and prompting strategy           ║
║                                                                    ║
║  Using 4 clean Full HD scene images (2752x1536):                  ║
║  - Scene 1: Flamethrower launch (side-angle wide shot)            ║
║  - Scene 2: Impact with pain (side-angle medium shot)             ║
║  - Scene 3: Burn marks & anger (medium close-up)                  ║
║  - Scene 4: Revenge charge (side-angle dynamic shot)              ║
║                                                                    ║
║  Validation after EVERY generation (images + videos)              ║
║  Generating 5s video from each → Final 20s sequence              ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()
    validator = ValidationFramework()

    # 4 clean Full HD scene paths
    scenes_dir = "charizard/battle_assets/clean_4scenes"
    scene_files = [
        "scene1_flamethrower_launch.jpg",
        "scene2_impact_pain.jpg",
        "scene3_burn_marks_anger.jpg",
        "scene4_revenge_charge.jpg"
    ]

    scene_paths = [os.path.join(scenes_dir, f) for f in scene_files]

    # Verify all scenes exist
    missing = [p for p in scene_paths if not os.path.exists(p)]
    if missing:
        print(f"❌ Missing scene files:")
        for p in missing:
            print(f"   - {p}")
        print(f"\nPlease ensure all 4 scenes are generated first.")
        return 1

    # Check file sizes (detect corrupted downloads)
    for scene_path in scene_paths:
        size_mb = os.path.getsize(scene_path) / (1024 * 1024)
        if size_mb < 0.5:
            print(f"❌ Scene appears corrupted: {scene_path} ({size_mb:.2f} MB)")
            print(f"   Please regenerate this scene.")
            return 1

    print(f"✅ Found all 4 clean Full HD scene images")

    # Video prompts (proper camera angles, no "camera movement")
    scene_prompts = [
        "Charizard launching massive orange-red Flamethrower stream from jaws with fierce expression, flames beginning to travel toward Dragonite on right, side-angle wide shot, volcanic valley, dramatic battle start",
        "Massive Flamethrower stream STRIKING Dragonite torso with bright impact glow and heat distortion, Dragonite grimacing with PAINED expression and arms raised defensively, body being pushed backward by flame force, side-angle medium shot emphasizing impact reaction",
        "Dragonite with visible BURN MARKS (blackened scorch patterns on torso and belly), flames dissipating with smoke wisping from burnt scales, facial expression transitioning to FIERCE ANGER (eyes narrowing, teeth bared), medium close-up centered on Dragonite",
        "Dragonite CHARGING FORWARD aggressively from right to left with fierce angry expression and bared teeth, teal wings spread wide for acceleration, burn marks visible on battle-worn body, Charizard on left bracing for incoming counter-attack, side-angle dynamic shot"
    ]

    # Generate videos from each scene with validation
    print(f"\n{'='*70}")
    print("STEP 1: GENERATING 5S VIDEOS FROM 4 CLEAN HD SCENES")
    print(f"{'='*70}")

    video_paths = []
    for scene_path, prompt in zip(scene_paths, scene_prompts):
        scene_name = os.path.splitext(os.path.basename(scene_path))[0]
        try:
            video_path = generate_video_from_scene(scene_path, scene_name, prompt, api_key, validator)
            video_paths.append(video_path)
        except Exception as e:
            print(f"\n❌ Failed on {scene_name}: {e}")
            print(f"Continuing with remaining scenes...")

    if len(video_paths) < 2:
        print(f"\n⚠️  Only {len(video_paths)} video(s) generated, need at least 2 for concatenation")
        return 1

    # Concatenate all videos with validation
    print(f"\n{'='*70}")
    print(f"STEP 2: CONCATENATING {len(video_paths)} VIDEOS")
    print(f"{'='*70}")

    final_output = "charizard/battle_assets/videos/final_4clean_sequence_20s.mp4"
    final_video = concatenate_videos(video_paths, final_output, validator)

    # Generate comprehensive feedback report
    print(f"\n{'='*70}")
    print("GENERATING VALIDATION FEEDBACK REPORT")
    print(f"{'='*70}")
    report_path = "charizard/battle_assets/validation_report_4clean.txt"
    validator.generate_feedback_report(report_path)

    # Save validation log (JSON)
    log_path = "charizard/battle_assets/validation_log_4clean.json"
    validator.save_validation_log(log_path)

    print(f"\n🎉 SUCCESS!")
    print(f"✅ Generated {len(video_paths)} videos (5s each)")
    print(f"✅ Concatenated into final {len(video_paths) * 5}s sequence")
    print(f"\n📁 Individual Videos: charizard/battle_assets/videos/clean4_*.mp4")
    print(f"📁 Final Video: {final_video}")
    print(f"📁 Validation Report: {report_path}")
    print(f"📁 Validation Log (JSON): {log_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
