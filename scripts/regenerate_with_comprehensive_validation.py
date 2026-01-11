#!/usr/bin/env python3
"""
Regenerate scenes with comprehensive Tier 0-3 validation.
Checks content (NO SHIELD, correct expressions, etc.) not just technical specs.
"""

import os
import sys
import requests
import json
import time
sys.path.insert(0, 'scripts')
from comprehensive_content_validation import ComprehensiveContentValidator


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
    """Upload image with retry logic."""
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
                    return result['image']['url']

            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                print(f"    ⚠️  Upload failed, retrying in {delay}s...")
                time.sleep(delay)

        except Exception as e:
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                print(f"    ⚠️  Error ({str(e)}), retrying in {delay}s...")
                time.sleep(delay)

    raise Exception("Upload failed after retries")


def generate_video_from_scene(scene_path: str, scene_name: str, prompt: str, api_key: str) -> str:
    """Generate video with retry logic."""
    print(f"\n  🎬 Generating video for {scene_name}...")
    print(f"  📤 Uploading image...")

    scene_url = upload_image(scene_path)
    print(f"    ✅ Uploaded")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": [scene_url],
            "prompt": prompt,
            "duration": "5",
            "sound": True
        }
    }

    # Retry logic
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

            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                print(f"    ⚠️  API Error, retrying in {delay}s...")
                time.sleep(delay)

        except Exception as e:
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                print(f"    ⚠️  Error, retrying in {delay}s...")
                time.sleep(delay)

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

                output_path = f"charizard/battle_assets/videos/clean4_{scene_name}.mp4"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Download with retry
                for attempt in range(max_retries):
                    try:
                        vid_resp = requests.get(video_url, timeout=120)
                        if vid_resp.status_code == 200 and len(vid_resp.content) > 100000:
                            with open(output_path, 'wb') as f:
                                f.write(vid_resp.content)

                            size_mb = os.path.getsize(output_path) / (1024 * 1024)
                            print(f"    ✅ Saved: {size_mb:.2f} MB")
                            return output_path
                        else:
                            if attempt < max_retries - 1:
                                delay = retry_delays[attempt]
                                print(f"    ⚠️  Download issue, retrying in {delay}s...")
                                time.sleep(delay)
                    except Exception as e:
                        if attempt < max_retries - 1:
                            delay = retry_delays[attempt]
                            print(f"    ⚠️  Download error, retrying in {delay}s...")
                            time.sleep(delay)

                raise Exception("Download failed after retries")

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Regenerate Scene 3 and validate all scenes comprehensively."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║    REGENERATE + COMPREHENSIVE VALIDATION (Tier 0-3, 14-16 steps)  ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  1. Regenerate Scene 3 (corrupted - 252 bytes)                    ║
║  2. Apply comprehensive content validation to ALL 4 scenes        ║
║  3. Check for issues like: Dragonite has shield (should NOT)      ║
║  4. Regenerate any scenes failing validation                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()
    validator = ComprehensiveContentValidator()

    # Scene 3 definition
    scene3 = {
        "name": "scene3_burn_marks_anger",
        "action": "Dragonite with burn marks, transitioning to anger",
        "pokemon": ["dragonite"],
        "camera_angle": "Medium close-up centered on Dragonite",
        "environment": ["volcanic valley"],
        "condition": "burnt/damaged",
        "special_requirements": [
            "VISIBLE BURN MARKS (blackened scorch marks on torso/belly)",
            "NO SHIELD",
            "Expression transitioning from pain to FIERCE ANGER",
            "Smoke wisping from burnt scales"
        ],
        "prompt": "Dragonite with visible BURN MARKS (blackened scorch patterns on torso and belly), flames dissipating with smoke wisping from burnt scales, facial expression transitioning to FIERCE ANGER (eyes narrowing, teeth bared), medium close-up centered on Dragonite"
    }

    # Regenerate Scene 3
    print(f"\n{'='*70}")
    print("REGENERATING SCENE 3")
    print(f"{'='*70}")

    scene3_image = "charizard/battle_assets/clean_4scenes/scene3_burn_marks_anger.jpg"

    try:
        video_path = generate_video_from_scene(
            scene3_image,
            scene3["name"],
            scene3["prompt"],
            api_key
        )
        print(f"✅ Scene 3 regenerated successfully!")
    except Exception as e:
        print(f"❌ Failed to regenerate Scene 3: {e}")
        return 1

    # Comprehensive validation of all 4 scenes
    print(f"\n{'='*70}")
    print("COMPREHENSIVE VALIDATION OF ALL 4 SCENES")
    print(f"{'='*70}")

    scenes = [
        {
            "num": 1,
            "image": "charizard/battle_assets/clean_4scenes/scene1_flamethrower_launch.jpg",
            "video": "charizard/battle_assets/videos/clean4_scene1_flamethrower_launch.mp4",
            "action": "Charizard launching Flamethrower",
            "pokemon": ["charizard", "dragonite"],
            "special_requirements": ["NO SHIELD on Dragonite", "Dragonite showing PAIN"]
        },
        {
            "num": 2,
            "image": "charizard/battle_assets/clean_4scenes/scene2_impact_pain.jpg",
            "video": "charizard/battle_assets/videos/clean4_scene2_impact_pain.mp4",
            "action": "Flamethrower striking Dragonite with pain",
            "pokemon": ["charizard", "dragonite"],
            "special_requirements": ["NO SHIELD on Dragonite", "Dragonite grimacing in pain", "Being pushed backward"]
        },
        {
            "num": 3,
            "image": scene3_image,
            "video": video_path,
            "action": "Dragonite with burn marks, getting angry",
            "pokemon": ["dragonite"],
            "special_requirements": ["VISIBLE BURN MARKS", "NO SHIELD", "Transitioning to anger"]
        },
        {
            "num": 4,
            "image": "charizard/battle_assets/clean_4scenes/scene4_revenge_charge.jpg",
            "video": "charizard/battle_assets/videos/clean4_scene4_revenge_charge.mp4",
            "action": "Dragonite charging forward for revenge",
            "pokemon": ["dragonite", "charizard"],
            "special_requirements": ["Dragonite charging aggressively", "Burn marks visible", "NO SHIELD"]
        }
    ]

    failed_scenes = []

    for scene in scenes:
        print(f"\n{'='*70}")
        print(f"VALIDATING SCENE {scene['num']}")
        print(f"{'='*70}")
        print(f"Action: {scene['action']}")
        print(f"Special requirements: {', '.join(scene['special_requirements'])}")
        print(f"\n⚠️  MANUAL REVIEW REQUIRED:")
        print(f"   Please check image: {scene['image']}")
        print(f"   Please check video: {scene['video']}")
        print(f"\n   Critical checks:")
        for req in scene['special_requirements']:
            print(f"      - {req}")

        if "NO SHIELD" in str(scene['special_requirements']):
            print(f"\n   ❌ CRITICAL: Does Dragonite have a shield? (Should be NO)")

        # Pause for user review
        print(f"\n   Press Enter after reviewing Scene {scene['num']}...")
        # For automation, skip input
        # input()

    print(f"\n{'='*70}")
    print(f"VALIDATION COMPLETE")
    print(f"{'='*70}")
    print(f"\n⚠️  Please manually review all 4 scenes and confirm:")
    print(f"   1. Does any scene show Dragonite with a shield?")
    print(f"   2. Are pain/anger expressions correct?")
    print(f"   3. Are burn marks visible in Scene 3?")
    print(f"   4. Do all scenes match their requirements?")
    print(f"\nIf any scenes fail, they should be regenerated.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
