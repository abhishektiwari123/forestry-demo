#!/usr/bin/env python3
"""
Generate test video from extracted panel using Kling 2.6
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


def upload_image(image_path: str, api_key: str) -> str:
    """Upload image to imgcdn.dev for video generation."""
    print(f"\n📤 Uploading image: {os.path.basename(image_path)}")

    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.2f} MB")

    # Upload to imgcdn.dev (used by other working scripts)
    print(f"   Uploading to imgcdn.dev...")

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


def generate_video(image_url: str, prompt: str, output_path: str, api_key: str, duration: int = 5) -> tuple:
    """Generate video from image using Kling 2.6."""
    print(f"\n🎬 Generating video...")
    print(f"📝 Prompt: {prompt}")
    print(f"⏱️  Duration: {duration}s")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": [image_url],
            "prompt": prompt,
            "duration": str(duration),
            "sound": False
        }
    }

    print(f"🚀 Submitting to Kling 2.6...")
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
    print(f"⏳ Generating... ", end="", flush=True)

    # Poll for completion (Kling can take 2-5 minutes)
    timeout = 600  # 10 minutes max

    while time.time() - start_time < timeout:
        time.sleep(5)
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
                print(f"\n✅ Generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Download video
                print(f"📥 Downloading video...")
                vid_resp = requests.get(video_url, timeout=120)
                if vid_resp.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(vid_resp.content)

                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    duration = time.time() - start_time

                    print(f"✅ Saved: {size_mb:.2f} MB")
                    print(f"⏱️  Total time: {duration:.1f}s")

                    return output_path, task_id, video_url

            elif state == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Generate test video from panel."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate video from extracted panel')
    parser.add_argument('panel_image', help='Path to panel image')
    parser.add_argument('--prompt', help='Video generation prompt', default=None)
    parser.add_argument('--duration', type=int, default=5, help='Video duration in seconds (default: 5)')
    parser.add_argument('--output', help='Output video path', default=None)

    args = parser.parse_args()

    print("""
╔════════════════════════════════════════════════════════════════════╗
║              VIDEO GENERATION FROM PANEL (Kling 2.6)               ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  1. Upload panel image                                             ║
║  2. Generate video with Kling 2.6                                  ║
║  3. Download result                                                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    if not os.path.exists(args.panel_image):
        print(f"❌ Panel image not found: {args.panel_image}")
        return 1

    api_key = load_api_key()

    # Determine panel and create appropriate prompt
    panel_name = os.path.basename(args.panel_image)

    if args.prompt:
        prompt = args.prompt
    elif 'panel_01' in panel_name:
        # CORRECTED: Added negative constraints to prevent unwanted retreat
        prompt = ("Camera zooming in on Charizard's open mouth as massive Flamethrower stream releases, "
                  "Charizard MAINTAINING stable hover position in place, wings beating steadily NOT moving backward, "
                  "focused expression watching attack travel toward Dragonite, camera panning to follow flame trajectory "
                  "while Charizard STAYS in attack position, "
                  "NO retreating, NO flying away, NOT moving backward after attack, Charizard HOLDS position firmly, "
                  "MAINTAINS original location, STAYS committed to attack stance, AVOID defensive withdrawal, "
                  "Dragonite on right STAYING in position, NOT dodging, MAINTAINS defensive stance, "
                  "side tracking shot showing full horizontal attack path, heat distortion visible, "
                  "both Pokemon airborne MAINTAINING positions, photorealistic motion, smooth camera work, "
                  "cinematic cinematography, dramatic lighting, 8K quality")
    elif 'panel_02' in panel_name:
        # Added negative constraints for direct hit
        prompt = ("Flamethrower stream STRIKING Dragonite's torso with explosive impact burst, "
                  "Dragonite recoiling in pain with pained expression, body pushed backward by force but STAYING in frame, "
                  "taking DIRECT undefended hit, NO dodging, NO defensive barriers, NO shields appearing, "
                  "NOT avoiding impact, Dragonite TAKES full hit, STAYS in camera view, does NOT fly away, "
                  "Charizard visible in background MAINTAINING attack position NOT retreating, "
                  "flames engulfing torso, photorealistic impact effects, camera slight shake emphasizing force, "
                  "dramatic lighting, cinematic quality, smooth motion")
    elif 'panel_03' in panel_name:
        # Added position maintenance constraints
        prompt = ("Flames dissipating revealing severe burn marks on Dragonite, smoke rising from burnt areas, "
                  "exhausted breathing with slight body movement STAYING in position, pained expression, "
                  "NO rapid movement, NOT flying away, Dragonite MAINTAINS location showing damage, "
                  "STAYS visible in frame displaying burn effects, HOLDS exhausted pose, "
                  "photorealistic burn damage detail, realistic smoke physics, cinematic lighting, "
                  "slow motion reveal, 8K detail quality")
    elif 'panel_04' in panel_name:
        # Added constraints to prevent premature movement
        prompt = ("Dragonite's expression transforming from pain to fierce anger, eyes narrowing with rage, "
                  "teeth baring aggressively, fists clenching, body tensing WHILE STAYING in position, "
                  "building counter-attack energy, NO premature movement, NOT lunging forward yet, "
                  "MAINTAINS current location, STAYS in frame building rage, burn marks STAY visible throughout, "
                  "HOLDS tension before action, smoke still rising from burns, "
                  "photorealistic emotion transformation, dramatic intensity building, cinematic close-up, perfect continuity")
    elif 'panel_05' in panel_name:
        # Added directional constraints for proper charge
        prompt = ("Over-the-shoulder view from behind Charizard in foreground showing Dragonite charging FORWARD AGGRESSIVELY "
                  "from background TOWARD camera and Charizard, closing distance rapidly, wings beating powerfully FOR FORWARD THRUST, "
                  "fierce angry expression, approaching TO ATTACK, NO lateral movement, NOT flying past, NOT circling, "
                  "Dragonite CHARGES DIRECTLY TOWARD target, STAYS on collision course, MAINTAINS forward approach vector, "
                  "Charizard in foreground STAYS in position bracing defensively NOT retreating, "
                  "over-the-shoulder dynamic shot, motion blur showing forward velocity, depth movement background to foreground, "
                  "photorealistic motion, cinematic aggressive approach, dramatic tension")
    elif 'panel_06' in panel_name:
        # Added impact commitment constraints
        prompt = ("Dragonite's electrified fist making FULL CONTACT with Charizard in devastating Thunder Punch, "
                  "massive yellow electric explosion at impact point, Charizard recoiling in pain, electric current through body, "
                  "NO missing, NOT glancing blow, DIRECT FULL IMPACT, both Pokemon STAY in frame during hit, "
                  "NOT flying apart immediately, contact MAINTAINED for impact moment, HOLDS connection showing force, "
                  "bright lightning arcs bursting outward, photorealistic electricity effects, "
                  "camera emphasizing connection point, dramatic impact, cinematic quality, slow motion at contact moment")
    else:
        prompt = "Photorealistic Pokemon battle scene with cinematic motion, smooth camera work"

    # Set output path
    if args.output:
        output_path = args.output
    else:
        panel_basename = os.path.splitext(panel_name)[0]
        output_path = f"charizard/battle_assets/test_videos/{panel_basename}_video.mp4"

    try:
        # Upload image
        image_url = upload_image(args.panel_image, api_key)

        # Generate video
        video_path, task_id, video_url = generate_video(
            image_url, prompt, output_path, api_key, args.duration
        )

        print(f"\n{'='*70}")
        print(f"🎉 VIDEO GENERATION COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Video: {video_path}")
        print(f"🆔 Task ID: {task_id}")
        print(f"🔗 URL: {video_url}")
        print(f"📝 Prompt: {prompt}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
