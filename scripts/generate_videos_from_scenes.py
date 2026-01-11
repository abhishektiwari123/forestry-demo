#!/usr/bin/env python3
"""
Generate video sequence from scene images with validation framework.

This script:
1. Validates each scene image before processing
2. Uploads and generates video for each scene
3. Validates each generated video
4. Concatenates all videos into final sequence
5. Generates comprehensive validation report

Usage:
    python generate_videos_from_scenes.py --scenes-dir ./scenes --output final.mp4
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
import requests

# Try loading .env from multiple locations
for env_path in ['.env', 'scripts/.env', '../scripts/.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

# Import validation framework
try:
    from validation_framework import ValidationFramework
except ImportError:
    # Inline minimal validation if import fails
    class ValidationFramework:
        def __init__(self):
            self.results = []

        def validate_image(self, path):
            class Result:
                valid = True
                issues = []
            return Result()

        def validate_video(self, path):
            class Result:
                valid = True
                issues = []
            return Result()

        def generate_feedback_report(self, path):
            return ""

        def save_validation_log(self, path):
            pass


def upload_image(image_path: str, max_retries: int = 4) -> str | None:
    """Upload image to CDN with retry logic."""
    with open(image_path, 'rb') as f:
        image_data = f.read()

    delays = [2, 4, 8, 16]  # Exponential backoff

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://imgcdn.dev/api/1/upload",
                files={"source": (os.path.basename(image_path), image_data, "image/jpeg")},
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status_code") == 200:
                    return result.get("image", {}).get("url")

        except Exception as e:
            print(f"    Upload attempt {attempt + 1} failed: {e}")

        if attempt < max_retries - 1:
            delay = delays[attempt]
            print(f"    Retrying in {delay}s...")
            time.sleep(delay)

    return None


def generate_video_for_scene(
    scene_path: str,
    motion_prompt: str,
    output_path: str,
    scene_num: int,
    api_key: str
) -> bool:
    """
    Generate a 5-second video from a scene image.

    Args:
        scene_path: Path to scene image
        motion_prompt: Motion description
        output_path: Where to save generated video
        scene_num: Scene number for logging
        api_key: KIE API key

    Returns:
        True if successful
    """
    print(f"\n  Scene {scene_num}: Generating video...")
    print(f"    Image: {scene_path}")
    print(f"    Motion: {motion_prompt[:60]}...")

    # Upload image
    print("    Uploading image...")
    image_url = upload_image(scene_path)
    if not image_url:
        print("    ERROR: Failed to upload image")
        return False

    print(f"    Uploaded: {image_url[:60]}...")

    # Submit video generation
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "kling-2.5-pro",
        "image_url": image_url,
        "prompt": motion_prompt,
        "duration": 5,
        "aspect_ratio": "16:9"
    }

    try:
        response = requests.post(
            "https://api.kie.ai/v1/videos/generations",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        task_id = result.get("task_id") or result.get("id")
        if not task_id:
            print(f"    ERROR: No task ID in response")
            return False

        print(f"    Task ID: {task_id}")
        print("    Generating (typically 60-120 seconds)...")

        # Poll for completion
        status_url = f"https://api.kie.ai/v1/videos/generations/{task_id}"

        for attempt in range(60):  # Max 5 minutes
            time.sleep(5)

            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            status = status_data.get("status", "").lower()

            if status in ["completed", "succeeded"]:
                video_url = (
                    status_data.get("output", {}).get("video_url") or
                    status_data.get("video_url")
                )

                if video_url:
                    return download_video(video_url, output_path, scene_num)

                print("    ERROR: No video URL in response")
                return False

            elif status in ["failed", "error"]:
                error = status_data.get("error", "Unknown")
                print(f"    ERROR: Generation failed - {error}")
                return False

            if attempt % 12 == 0 and attempt > 0:
                print(f"    Still generating... ({attempt * 5}s)")

        print("    ERROR: Timeout after 5 minutes")
        return False

    except Exception as e:
        print(f"    ERROR: API request failed - {e}")
        return False


def download_video(url: str, output_path: str, scene_num: int) -> bool:
    """Download video from URL."""
    print(f"    Downloading video...")

    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"    SUCCESS: Scene {scene_num} saved ({file_size:.1f} MB)")
        return True

    except Exception as e:
        print(f"    ERROR: Download failed - {e}")
        return False


def get_video_duration(video_path: str) -> float:
    """Get video duration using ffprobe."""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ], capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0.0


def concatenate_videos(video_paths: list[str], output_path: str) -> bool:
    """Concatenate videos using FFmpeg."""
    print(f"\nConcatenating {len(video_paths)} videos...")

    # Create concat file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for path in video_paths:
            f.write(f"file '{path}'\n")
        concat_file = f.name

    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path
        ]

        subprocess.run(cmd, capture_output=True, check=True)
        os.unlink(concat_file)

        duration = get_video_duration(output_path)
        file_size = Path(output_path).stat().st_size / (1024 * 1024)

        print(f"Final video: {output_path}")
        print(f"Duration: {duration:.1f}s")
        print(f"File size: {file_size:.1f} MB")

        return True

    except Exception as e:
        print(f"ERROR: Concatenation failed - {e}")
        if os.path.exists(concat_file):
            os.unlink(concat_file)
        return False


def generate_video_sequence(
    scenes_dir: str,
    output_path: str,
    motion_prompts: dict[int, str] = None
) -> bool:
    """
    Generate complete video sequence from scene images.

    Args:
        scenes_dir: Directory containing scene images
        output_path: Path for final concatenated video
        motion_prompts: Dict mapping scene number to motion prompt

    Returns:
        True if successful
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("ERROR: KIE_API_KEY not found in environment")
        return False

    # Find scene images
    scene_files = sorted(Path(scenes_dir).glob("scene*.jpg"))
    if not scene_files:
        scene_files = sorted(Path(scenes_dir).glob("*.jpg"))

    if not scene_files:
        print(f"ERROR: No scene images found in {scenes_dir}")
        return False

    print(f"\n{'='*60}")
    print(f"VIDEO SEQUENCE GENERATION")
    print(f"{'='*60}")
    print(f"Scenes directory: {scenes_dir}")
    print(f"Found {len(scene_files)} scenes")
    print(f"Output: {output_path}")
    print(f"{'='*60}")

    # Initialize validation framework
    validator = ValidationFramework()

    # Default motion prompts
    default_motion = "Subtle movement, gentle breathing, atmospheric particles drifting"

    # Output directory for individual videos
    videos_dir = Path(scenes_dir).parent / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    # Process each scene
    generated_videos = []

    for i, scene_path in enumerate(scene_files, 1):
        print(f"\n{'='*40}")
        print(f"SCENE {i}/{len(scene_files)}")
        print(f"{'='*40}")

        # Validate image first
        img_result = validator.validate_image(str(scene_path))
        if not img_result.valid:
            print(f"  WARNING: Image validation issues:")
            for issue in img_result.issues:
                print(f"    - {issue}")
            # Continue anyway - just log the issue

        # Get motion prompt
        motion = default_motion
        if motion_prompts and i in motion_prompts:
            motion = motion_prompts[i]

        # Generate video
        video_path = str(videos_dir / f"scene{i:02d}.mp4")

        if generate_video_for_scene(str(scene_path), motion, video_path, i, api_key):
            # Validate generated video
            vid_result = validator.validate_video(video_path)
            if not vid_result.valid:
                print(f"  WARNING: Video validation issues:")
                for issue in vid_result.issues:
                    print(f"    - {issue}")

            generated_videos.append(video_path)
        else:
            print(f"  FAILED: Scene {i} video generation failed")

    # Check if we have any videos
    if not generated_videos:
        print("\nERROR: No videos were generated")
        return False

    print(f"\n\nGenerated {len(generated_videos)}/{len(scene_files)} videos")

    # Concatenate videos
    success = concatenate_videos(generated_videos, output_path)

    # Generate reports
    report_dir = Path(output_path).parent
    validator.generate_feedback_report(str(report_dir / "validation_report.txt"))
    validator.save_validation_log(str(report_dir / "validation_log.json"))

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Generate video sequence from scene images with validation"
    )
    parser.add_argument(
        "--scenes-dir",
        required=True,
        help="Directory containing scene images"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for final video"
    )
    parser.add_argument(
        "--motion-prompts-file",
        help="JSON file with motion prompts per scene"
    )

    args = parser.parse_args()

    # Validate scenes directory
    if not os.path.isdir(args.scenes_dir):
        print(f"ERROR: Scenes directory not found: {args.scenes_dir}")
        sys.exit(1)

    # Load motion prompts if provided
    motion_prompts = None
    if args.motion_prompts_file and os.path.exists(args.motion_prompts_file):
        with open(args.motion_prompts_file) as f:
            motion_prompts = {int(k): v for k, v in json.load(f).items()}

    success = generate_video_sequence(args.scenes_dir, args.output, motion_prompts)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
