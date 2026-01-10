#!/usr/bin/env python3
"""
Test Kling API Video Extension Feature

Extends an existing video by 5 seconds using the /v1/video/extension endpoint.
Based on research from Kling API documentation.
"""

import os
import sys
import time
import requests
import json


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


def extend_video(task_id: str, extension_prompt: str, api_key: str) -> str:
    """
    Extend an existing video using Kling API extension feature.

    Args:
        task_id: The task ID from the original video generation
        extension_prompt: Text prompt describing what happens next in the video
        api_key: KIE API key

    Returns:
        Path to extended video file
    """
    print(f"\n{'='*70}")
    print("KLING VIDEO EXTENSION TEST")
    print(f"{'='*70}")
    print(f"Original Video Task ID: {task_id}")
    print(f"Extension Prompt: {extension_prompt[:100]}...")
    print(f"{'='*70}\n")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # API endpoint for video extension
    # Based on research: model_name should be 'kling-v2-master' and use standard createTask endpoint
    payload = {
        "model": "kling-v2-master",  # Correct model name for extension
        "task_type": "video_extension",  # Specify extension task type
        "input": {
            "task_id": task_id,  # Original video's task ID
            "prompt": extension_prompt,  # Extension prompt (max 2500 chars)
            "duration": "5",  # Extension duration (5 seconds)
            "mode": "standard"  # or "professional"
        }
    }

    print(f"🚀 Submitting extension request to Kling API...")
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"API Error: {response.status_code}")

    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        raise Exception(f"Failed: {result.get('msg')}")

    extension_task_id = result["data"]["taskId"]
    print(f"✅ Extension task created: {extension_task_id}")
    print(f"⏳ Generating extended video (this may take ~2-3 minutes)... ", end="", flush=True)

    # Poll for completion
    while time.time() - start_time < 300:  # 5 minute timeout
        time.sleep(10)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)

        # Check status
        status_response = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo/{extension_task_id}",
            headers=headers
        )

        if status_response.status_code == 200:
            data = status_response.json().get("data", {})
            state = data.get("state")

            if state == "success":
                video_url = data.get("resultVideo")
                print(f"\n✅ Extension complete!")

                # Download extended video
                output_path = "charizard/battle_assets/videos/seg19_extended.mp4"
                print(f"📥 Downloading extended video...")

                video_response = requests.get(video_url)
                with open(output_path, 'wb') as f:
                    f.write(video_response.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                duration = time.time() - start_time
                print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                print(f"📁 Location: {output_path}")

                return output_path

            elif state == "fail":
                print(f"\n❌ Extension failed: {data.get('failMsg')}")
                raise Exception(f"Extension failed: {data.get('failMsg')}")

    raise Exception("Extension timeout after 5 minutes")


def main():
    """Test video extension with most recent video (Seg19)."""
    api_key = load_api_key()

    # We need the task_id from the most recent Seg19 generation
    # For testing, we'll need to extract this from the generation logs
    # or provide it manually

    print("""
╔════════════════════════════════════════════════════════════════════╗
║                KLING VIDEO EXTENSION TEST                          ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  This script tests the Kling API video extension feature.         ║
║  It extends an existing 5-second video by another 5 seconds.      ║
║                                                                    ║
║  Features:                                                         ║
║  - Extends existing video seamlessly                               ║
║  - Maintains visual continuity                                     ║
║  - Text-controlled extension prompt                                ║
║  - Can extend up to 3 minutes total                                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    # TEST CASE: Extend Seg19 (Dragonite charging back)
    # We need the task_id from the Seg19 generation
    # For now, let's create a placeholder that shows how it works

    print("❌ To use video extension, we need the task_id from a previous generation.")
    print("This is returned when generating a video and looks like: 'task_xxxxxxxxxxxxxxx'")
    print()
    print("EXAMPLE USAGE:")
    print("python3 scripts/test_kling_video_extension.py <task_id>")
    print()
    print("Extension Prompt for Seg19:")
    print("'Dragonite continues charging forward at high speed toward Charizard,")
    print(" wings beating powerfully, closing the distance rapidly for Thunder Punch,")
    print(" Charizard bracing for incoming attack, dramatic tension building'")
    print()
    print("This would extend the 5s video to 10s showing the full charge sequence.")

    if len(sys.argv) > 1:
        task_id = sys.argv[1]
        extension_prompt = "Dragonite continues charging forward at high speed toward Charizard, wings beating powerfully, closing the distance rapidly for Thunder Punch, Charizard bracing for incoming attack, dramatic tension building"

        print(f"\n✅ Using provided task_id: {task_id}")
        extended_video = extend_video(task_id, extension_prompt, api_key)
        print(f"\n🎉 Success! Extended video saved to: {extended_video}")
    else:
        print("\n💡 TIP: We can store task IDs during generation and use them later for extensions.")
        print("This would be useful for creating longer battle sequences (up to 3 minutes total).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
