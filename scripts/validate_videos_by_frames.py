#!/usr/bin/env python3
"""
Validate videos by extracting and analyzing key frames.

Since we cannot "play" videos directly, this script:
1. Extracts 3 key frames from each video (start, middle, end)
2. Allows visual inspection of those frames
3. Validates Pokemon features across frames
4. Checks for consistency (no morphing, color shifts, etc.)
"""

import os
import subprocess
import sys
from pathlib import Path

def get_video_duration(video_path):
    """Get video duration in seconds."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration: {e}")
        return None

def extract_key_frames(video_path, output_dir):
    """Extract first, middle, and last frames from video."""
    duration = get_video_duration(video_path)

    if not duration:
        print(f"❌ Could not get duration for {video_path}")
        return []

    video_name = Path(video_path).stem
    os.makedirs(output_dir, exist_ok=True)

    # Frame timestamps
    frames = {
        'first': 0.1,  # Just after start
        'middle': duration / 2,
        'last': max(0, duration - 0.1)  # Just before end
    }

    extracted_frames = []

    for frame_name, timestamp in frames.items():
        output_path = f"{output_dir}/{video_name}_{frame_name}.jpg"

        cmd = [
            'ffmpeg', '-y',
            '-ss', str(timestamp),
            '-i', video_path,
            '-frames:v', '1',
            '-q:v', '2',
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
            file_size = os.path.getsize(output_path) / 1024  # KB
            print(f"  ✅ Extracted {frame_name} frame: {file_size:.1f} KB")
            extracted_frames.append(output_path)
        except Exception as e:
            print(f"  ❌ Failed to extract {frame_name} frame: {e}")

    return extracted_frames

def main():
    print("="*70)
    print("VIDEO VALIDATION VIA FRAME EXTRACTION")
    print("="*70)
    print("\nThis script extracts key frames from each video for validation.")
    print("We'll extract: First frame, Middle frame, Last frame")
    print("="*70)

    # Find all valid videos
    video_dir = "charizard/battle_assets/videos"
    output_dir = "charizard/battle_assets/video_frames_validation"

    if not os.path.exists(video_dir):
        print(f"❌ Video directory not found: {video_dir}")
        return

    # Get all MP4 files
    videos = sorted(Path(video_dir).glob("*.mp4"))

    # Filter out corrupt files (< 1MB)
    valid_videos = []
    for video in videos:
        size_mb = video.stat().st_size / (1024 * 1024)
        if size_mb >= 1:
            valid_videos.append(video)
        else:
            print(f"⚠️  Skipping {video.name} (only {size_mb:.2f} MB - likely corrupt)")

    print(f"\nFound {len(valid_videos)} valid videos to process\n")

    # Process each video
    results = {}

    for i, video in enumerate(valid_videos, 1):
        print(f"\n[{i}/{len(valid_videos)}] Processing: {video.name}")
        print(f"  Size: {video.stat().st_size / (1024*1024):.1f} MB")

        frames = extract_key_frames(str(video), output_dir)
        results[video.name] = frames

        if frames:
            print(f"  ✅ Extracted {len(frames)} frames")
        else:
            print(f"  ❌ Frame extraction failed")

    # Summary
    print(f"\n{'='*70}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*70}")
    print(f"\nProcessed: {len(valid_videos)} videos")
    print(f"Output directory: {output_dir}/")
    print(f"\nNext steps:")
    print(f"1. Review extracted frames in: {output_dir}/")
    print(f"2. Validate each frame set for:")
    print(f"   - Pokemon feature consistency (start → middle → end)")
    print(f"   - Size relationships maintained")
    print(f"   - Wing colors (teal) visible")
    print(f"   - No morphing or distortion")
    print(f"   - Color consistency (no shifts)")
    print(f"3. Document which videos pass validation")

    # Create index file
    index_path = f"{output_dir}/README.md"
    with open(index_path, 'w') as f:
        f.write("# Video Frame Extraction - Validation Index\n\n")
        f.write("## Extracted Frames by Video\n\n")

        for video_name, frames in sorted(results.items()):
            f.write(f"### {video_name}\n")
            if frames:
                f.write(f"- Frames extracted: {len(frames)}\n")
                for frame in frames:
                    frame_name = Path(frame).name
                    f.write(f"  - `{frame_name}`\n")
            else:
                f.write("- ❌ Extraction failed\n")
            f.write("\n")

        f.write("## Validation Checklist\n\n")
        f.write("For each video, check across all 3 frames:\n\n")
        f.write("### Critical Items:\n")
        f.write("- [ ] Pokemon remain recognizable throughout\n")
        f.write("- [ ] Size relationships consistent (if both present)\n")
        f.write("- [ ] Wing colors (teal) visible and consistent\n")
        f.write("- [ ] Body colors accurate and don't shift\n\n")
        f.write("### Technical Quality:\n")
        f.write("- [ ] No morphing or distortion visible\n")
        f.write("- [ ] No color shifts or degradation\n")
        f.write("- [ ] Smooth progression (first → middle → last)\n")
        f.write("- [ ] Features clear and sharp\n\n")

    print(f"\n✅ Created validation index: {index_path}")

if __name__ == "__main__":
    main()
