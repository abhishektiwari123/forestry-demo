#!/usr/bin/env python3
"""
Alternative Video Extension - Extract Last Frame & Generate Continuation

Since kie.ai may not support direct Kling video extension API yet,
this script implements extension by:
1. Extracting the last frame from the original video
2. Generating a new 5s video from that last frame with extension prompt
3. Concatenating both videos together for a seamless 10s result
"""

import os
import sys
import subprocess
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


def extract_last_frame(video_path: str, output_path: str):
    """Extract the last frame from a video using ffmpeg."""
    print(f"📸 Extracting last frame from {video_path}...")

    # Get video duration
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
    duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())

    # Extract frame at last second
    cmd = f'ffmpeg -y -i "{video_path}" -ss {duration - 0.1} -vframes 1 "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)

    print(f"✅ Last frame saved: {output_path}")
    return output_path


def upload_image(image_path: str) -> str:
    """Upload image to CDN."""
    print(f"📤 Uploading last frame to CDN...")

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
    print(f"✅ Uploaded: {image_url}")
    return image_url


def generate_continuation_video(image_url: str, prompt: str, api_key: str) -> str:
    """Generate continuation video from last frame."""
    print(f"\n🚀 Generating continuation video...")
    print(f"📝 Prompt: {prompt[:100]}...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.6/image-to-video",
        "input": {
            "image_urls": [image_url],
            "prompt": prompt,
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
                print(f"\n✅ Continuation video generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]

                output_path = "charizard/battle_assets/videos/seg06_continuation.mp4"
                vid_resp = requests.get(video_url, timeout=120)
                with open(output_path, 'wb') as f:
                    f.write(vid_resp.content)

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Saved: {size_mb:.2f} MB")
                return output_path

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def concatenate_videos(video1: str, video2: str, output: str):
    """Concatenate two videos together."""
    print(f"\n🎬 Concatenating videos...")

    # Create file list for ffmpeg
    list_file = "charizard/battle_assets/videos/concat_list.txt"
    with open(list_file, 'w') as f:
        f.write(f"file '{os.path.basename(video1)}'\n")
        f.write(f"file '{os.path.basename(video2)}'\n")

    # Concatenate
    cmd = f'cd charizard/battle_assets/videos && ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy "{os.path.basename(output)}"'
    subprocess.run(cmd, shell=True, check=True)

    # Cleanup
    os.remove(list_file)

    size_mb = os.path.getsize(output) / (1024 * 1024)
    print(f"✅ Extended video saved: {size_mb:.2f} MB")
    print(f"📁 Location: {output}")
    return output


def main():
    """Main function to extend Seg06 video."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║            ALTERNATIVE VIDEO EXTENSION METHOD                      ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  This extends videos by:                                           ║
║  1. Extracting the last frame                                      ║
║  2. Generating new video from that frame                           ║
║  3. Concatenating both videos                                      ║
║                                                                    ║
║  Result: Seamless 10-second extended video                         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Seg06 video path
    video_path = "charizard/battle_assets/videos/seg06_dragonite_counters_-_thunder_punch.mp4"

    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return 1

    # Step 1: Extract last frame
    last_frame_path = "charizard/battle_assets/frame_pairs/seg06_last_frame.jpg"
    extract_last_frame(video_path, last_frame_path)

    # Step 2: Upload frame
    image_url = upload_image(last_frame_path)

    # Step 3: Generate continuation video
    extension_prompt = (
        "Charizard continues reeling backward from Thunder Punch electric impact, "
        "body jerking violently from residual electricity arcing across scales, "
        "wings flailing to regain balance, sparks fading, both Pokemon separating "
        "in mid-air after exchange, dramatic battle tension, realistic physics"
    )

    continuation_video = generate_continuation_video(image_url, extension_prompt, api_key)

    # Step 4: Concatenate videos
    extended_output = "charizard/battle_assets/videos/seg06_extended_10s.mp4"
    concatenate_videos(video_path, continuation_video, extended_output)

    print(f"\n🎉 Success! Extended video saved to: {extended_output}")
    print(f"📊 Original: 5s → Extended: 10s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
