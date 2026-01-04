#!/usr/bin/env python3
"""
Assemble final documentary from video segments, narration, and sound effects.

Usage:
    python assemble_video.py --pokemon haunter --project-dir .. --output ../haunter/haunter_final.mp4
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

def get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds."""
    result = subprocess.run(
        ['ffprobe', '-i', audio_path, '-show_entries', 'format=duration',
         '-v', 'quiet', '-of', 'csv=p=0'],
        capture_output=True,
        text=True
    )
    return float(result.stdout.strip())

def sync_segment(video_path: str, audio_path: str, sfx_path: str,
                 output_path: str, sfx_volume: float = 0.35) -> bool:
    """
    Synchronize video with audio and sound effects for one segment.

    Args:
        video_path: Path to video file (10 seconds)
        audio_path: Path to narration audio (6-8 seconds)
        sfx_path: Path to sound effects (same duration as audio)
        output_path: Where to save synced segment
        sfx_volume: Volume level for SFX (0.0-1.0)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get audio duration
        duration = get_audio_duration(audio_path)

        # Build FFmpeg command
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-i', video_path,  # Input video
            '-i', audio_path,  # Input narration
            '-i', sfx_path,    # Input sound effects
            '-t', str(duration),  # Trim to audio duration
            '-filter_complex',
            f'[1:a][2:a]amix=inputs=2:duration=first:weights=1 {sfx_volume}[a]',
            '-map', '0:v',  # Use video from first input
            '-map', '[a]',  # Use mixed audio
            '-c:v', 'libx264',  # Video codec
            '-preset', 'slow',  # Quality preset
            '-crf', '18',  # Quality level (18 = high)
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            output_path
        ]

        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error syncing segment: {e}")
        return False

def concatenate_segments(segment_paths: list, output_path: str) -> bool:
    """
    Concatenate all synced segments into final video.

    Args:
        segment_paths: List of paths to synced segments
        output_path: Where to save final video

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create file list for FFmpeg concat
        filelist_path = Path(output_path).parent / "filelist.txt"

        with open(filelist_path, 'w') as f:
            for path in segment_paths:
                f.write(f"file '{Path(path).absolute()}'\n")

        # Build FFmpeg concat command
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(filelist_path),
            '-c', 'copy',  # Copy streams (no re-encoding)
            output_path
        ]

        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Clean up filelist
        filelist_path.unlink()

        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error concatenating segments: {e}")
        return False

def assemble_documentary(pokemon_name: str, project_dir: str, output_path: str) -> bool:
    """
    Assemble complete documentary from all segments.

    Args:
        pokemon_name: Name of Pokemon (e.g., 'haunter')
        project_dir: Project root directory
        output_path: Where to save final documentary

    Returns:
        True if successful, False otherwise
    """
    project_path = Path(project_dir)
    pokemon_path = project_path / pokemon_name

    # Verify directories exist
    videos_dir = pokemon_path / "videos"
    audio_dir = pokemon_path / "audio"
    sfx_dir = pokemon_path / "sfx"
    processed_dir = pokemon_path / "processed"

    if not videos_dir.exists() or not audio_dir.exists() or not sfx_dir.exists():
        print(f"❌ Error: Required directories not found")
        print(f"   Expected: {videos_dir}, {audio_dir}, {sfx_dir}")
        return False

    # Create processed directory
    processed_dir.mkdir(exist_ok=True)

    print(f"🎬 Assembling {pokemon_name.upper()} documentary")
    print(f"=" * 70)

    # Process each segment
    synced_segments = []

    for i in range(1, 19):  # Segments 1-18
        segment_num = f"{i:02d}"

        video_file = videos_dir / f"segment_{segment_num}.mp4"
        audio_file = audio_dir / f"segment_{segment_num}.mp3"
        sfx_file = sfx_dir / f"segment_{segment_num}.mp3"
        output_file = processed_dir / f"segment_{segment_num}.mp4"

        # Check files exist
        if not video_file.exists():
            print(f"❌ Missing video: {video_file}")
            return False
        if not audio_file.exists():
            print(f"❌ Missing audio: {audio_file}")
            return False
        if not sfx_file.exists():
            print(f"❌ Missing SFX: {sfx_file}")
            return False

        print(f"\n📹 Processing Segment {i}/18")

        # Sync segment
        success = sync_segment(
            str(video_file),
            str(audio_file),
            str(sfx_file),
            str(output_file)
        )

        if not success:
            print(f"❌ Failed to sync segment {i}")
            return False

        # Get duration
        duration = get_audio_duration(str(audio_file))
        print(f"✅ Synced segment {i} ({duration:.2f}s)")

        synced_segments.append(output_file)

    # Calculate total duration
    total_duration = sum(get_audio_duration(str(seg)) for seg in synced_segments)
    print(f"\n📊 Total duration: {total_duration:.2f} seconds")

    if total_duration < 85 or total_duration > 95:
        print(f"⚠️  Warning: Duration is outside target range (85-95 seconds)")

    # Concatenate all segments
    print(f"\n🎞️  Concatenating all segments...")

    success = concatenate_segments(
        [str(seg) for seg in synced_segments],
        output_path
    )

    if not success:
        print(f"❌ Failed to concatenate segments")
        return False

    print(f"\n✅ Documentary assembled successfully!")
    print(f"📁 Output: {output_path}")
    print(f"⏱️  Duration: {total_duration:.2f} seconds")
    print(f"=" * 70)

    return True

def main():
    parser = argparse.ArgumentParser(
        description="Assemble final documentary from segments"
    )
    parser.add_argument(
        "--pokemon",
        required=True,
        help="Pokemon name (e.g., 'haunter')"
    )
    parser.add_argument(
        "--project-dir",
        default="..",
        help="Project root directory (default: ..)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for final documentary"
    )
    parser.add_argument(
        "--sfx-volume",
        type=float,
        default=0.35,
        help="SFX volume level (0.0-1.0, default: 0.35)"
    )

    args = parser.parse_args()

    # Check FFmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: FFmpeg not found")
        print("Please install FFmpeg: brew install ffmpeg")
        sys.exit(1)

    success = assemble_documentary(args.pokemon, args.project_dir, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
