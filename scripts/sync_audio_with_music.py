#!/usr/bin/env python3
"""
Sync narration and background music with video segments.
Creates professional audio mix: narration (clear) + background music (30% volume).
"""

import os
import sys
import glob
import subprocess
from pathlib import Path

def sync_segment_audio(video_path: str, narration_path: str, background_music: str, output_path: str):
    """
    Sync narration and background music with video segment.

    Audio mixing strategy:
    - Narration: 100% volume (clear and prominent)
    - Background music: 30% volume (subtle, doesn't overpower narration)
    - Music loops if shorter than video duration
    """
    print(f"\n🎵 Syncing audio for {os.path.basename(video_path)}")

    # FFmpeg command with audio mixing
    # -stream_loop -1: Loop background music
    # -shortest: Stop when shortest input (video) ends
    # amix filter: Mix narration + music
    # weights: Narration at 1.0 (100%), music at 0.3 (30%)
    cmd = [
        'ffmpeg',
        '-i', video_path,              # Input: video (silent)
        '-i', narration_path,          # Input: narration audio
        '-stream_loop', '-1',          # Loop the background music
        '-i', background_music,        # Input: background music
        '-filter_complex',
        '[1:a]volume=1.0[narration];'  # Narration at 100%
        '[2:a]volume=0.3[music];'      # Background music at 30%
        '[narration][music]amix=inputs=2:duration=shortest[audio]',  # Mix both
        '-map', '0:v',                 # Use video from first input
        '-map', '[audio]',             # Use mixed audio
        '-c:v', 'copy',                # Copy video without re-encoding (fast)
        '-c:a', 'aac',                 # Encode audio as AAC
        '-b:a', '192k',                # Audio bitrate 192kbps (high quality)
        '-shortest',                   # Stop when video ends
        '-y',                          # Overwrite output
        output_path
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Saved with audio: {output_path} ({file_size:.1f} MB)")
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout processing {video_path}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def process_all_segments(background_music: str):
    """
    Process all video segments, adding narration + background music.

    Args:
        background_music: Path to background music file (MP3, WAV, etc.)
    """
    # Find all silent video segments
    videos = sorted(glob.glob("charizard/battle_assets/videos/seg*_video.mp4"))

    # Filter out already processed ones (those with _with_audio suffix)
    videos = [v for v in videos if "_with_audio" not in v and "_test" not in v]

    if not videos:
        print("❌ No silent video segments found!")
        return

    if not os.path.exists(background_music):
        print(f"❌ Background music not found: {background_music}")
        print(f"\nTo continue, you need epic battle music. Options:")
        print(f"  1. Download royalty-free music from:")
        print(f"     - YouTube Audio Library")
        print(f"     - Pixabay Music")
        print(f"     - Incompetech")
        print(f"  2. Save as: {background_music}")
        print(f"  3. Re-run this script")
        return

    print("🎬 AUDIO SYNC: ALL SEGMENTS WITH MUSIC")
    print("=" * 60)
    print(f"Videos to process: {len(videos)}")
    print(f"Background music: {background_music}")
    print("=" * 60)

    os.makedirs("charizard/battle_assets/videos_with_audio", exist_ok=True)

    success_count = 0
    failed = []

    for video_path in videos:
        # Extract segment number from filename
        basename = os.path.basename(video_path)
        seg_num = basename.split("seg")[1].split("_")[0]

        # Find corresponding narration
        narration_path = f"charizard/battle_assets/audio/seg{seg_num}_narration.mp3"

        if not os.path.exists(narration_path):
            print(f"⚠️  Skipping {basename}: narration not found")
            failed.append(seg_num)
            continue

        # Check if video is valid (not corrupted)
        video_size = os.path.getsize(video_path) / (1024 * 1024)
        if video_size < 1.0:  # Less than 1MB = corrupted
            print(f"⚠️  Skipping {basename}: corrupted file ({video_size:.2f} MB)")
            failed.append(seg_num)
            continue

        # Output path
        output_path = f"charizard/battle_assets/videos_with_audio/seg{seg_num}_with_audio.mp4"

        # Process
        if sync_segment_audio(video_path, narration_path, background_music, output_path):
            success_count += 1
            print(f"✅ Progress: {success_count}/{len(videos) - len(failed)}")
        else:
            failed.append(seg_num)

    print(f"\n{'=' * 60}")
    print(f"🎉 AUDIO SYNC COMPLETE!")
    print(f"✅ Success: {success_count}/{len(videos)}")
    print(f"❌ Failed/Skipped: {len(failed)}")

    if failed:
        print(f"Failed segments: {failed}")
    else:
        print(f"\n🎊 ALL SEGMENTS NOW HAVE AUDIO!")
        print(f"Next: Assemble final documentary from segments")


def test_single_segment(segment_num: int, background_music: str):
    """Test audio sync on a single segment."""
    video_path = f"charizard/battle_assets/videos/seg{segment_num:02d}_video.mp4"
    narration_path = f"charizard/battle_assets/audio/seg{segment_num:02d}_narration.mp3"
    output_path = f"charizard/battle_assets/videos_with_audio/seg{segment_num:02d}_with_audio_test.mp4"

    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return

    if not os.path.exists(narration_path):
        print(f"❌ Narration not found: {narration_path}")
        return

    if not os.path.exists(background_music):
        print(f"❌ Background music not found: {background_music}")
        return

    os.makedirs("charizard/battle_assets/videos_with_audio", exist_ok=True)

    print("🧪 TEST MODE: Single Segment Audio Sync")
    print("=" * 60)

    sync_segment_audio(video_path, narration_path, background_music, output_path)

    print(f"\n✅ Test complete!")
    print(f"Preview: {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Sync narration and background music with video segments"
    )
    parser.add_argument(
        "--music",
        default="charizard/battle_assets/background_music.mp3",
        help="Path to background music file"
    )
    parser.add_argument(
        "--test",
        type=int,
        metavar="SEGMENT",
        help="Test with single segment number (1-18)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all segments"
    )

    args = parser.parse_args()

    if args.test:
        test_single_segment(args.test, args.music)
    elif args.all:
        process_all_segments(args.music)
    else:
        print("Usage:")
        print("  --test N        Test audio sync on segment N")
        print("  --all           Process all segments")
        print("  --music PATH    Background music file (default: charizard/battle_assets/background_music.mp3)")
        print("\nExample:")
        print("  python scripts/sync_audio_with_music.py --test 1 --music battle_music.mp3")
        print("  python scripts/sync_audio_with_music.py --all")
