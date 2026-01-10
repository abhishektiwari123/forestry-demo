#!/usr/bin/env python3
"""
Generate 10-second video from existing image task_id.
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


def get_image_url_from_task(task_id: str, api_key: str) -> str:
    """Get image URL from task_id."""
    print(f"📥 Fetching image URL for task: {task_id}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json().get("data", {})
        if data.get("state") == "success":
            result_json = json.loads(data["resultJson"])
            image_url = result_json["resultUrls"][0]
            print(f"✅ Image URL: {image_url}")
            return image_url

    raise Exception(f"Failed to get image URL for task {task_id}")


def generate_10s_video(image_url: str, prompt: str, api_key: str) -> str:
    """Generate 10-second video from image."""
    print(f"\n{'='*70}")
    print(f"GENERATING 10-SECOND VIDEO")
    print(f"{'='*70}")
    print(f"\n📝 Video Prompt:")
    print(f"{prompt[:200]}...")
    print(f"\n🚀 Submitting to Kling 2.6...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": [image_url],
            "prompt": prompt,
            "duration": "10",  # 10-second video
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
    print(f"⏳ Generating... ", end="", flush=True)

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
                print(f"\n✅ Video generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                output_path = "charizard/battle_assets/videos/seg20_improved_10s.mp4"
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
    if len(sys.argv) < 2:
        print("Usage: python3 generate_10s_from_image.py <image_task_id>")
        return 1

    image_task_id = sys.argv[1]
    api_key = load_api_key()

    # Get image URL
    image_url = get_image_url_from_task(image_task_id, api_key)

    # Create improved prompt - showing progression properly
    video_prompt = """Charizard (smaller, 5'7\", orange dragon with teal wings, cream belly, flaming tail) on LEFT launching massive orange-red Flamethrower stream from open jaws toward Dragonite (larger, 7'3\", orange-tan body, teal wings, two antennae, cream belly) on RIGHT. PROGRESSION: (0-3s) Flames traveling and striking Dragonite's torso with bright impact, Dragonite's face showing PAIN (eyes squinting, mouth grimacing, teeth showing) and being pushed backward by flames. (3-5s) Flames fading, Dragonite recovering from knockback, BURN MARKS APPEARING on torso showing blackened scorch patterns and smoke wisping. (5-7s) Dragonite's expression shifting from pain to FIERCE ANGER (eyes narrowing with rage, teeth bared in snarl). (7-10s) Dragonite CHARGING FORWARD AGGRESSIVELY TOWARD CHARIZARD with wings spread for revenge attack, body accelerating rapidly, Charizard bracing, dramatic tension. Camera: side-angle showing both Pokemon throughout, smooth cinematic motion with realistic physics"""

    # Generate 10s video
    video_path = generate_10s_video(image_url, video_prompt, api_key)

    print(f"\n🎉 Success! 10-second video generated!")
    print(f"📊 Duration: 10 seconds")
    print(f"📁 File: {video_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
