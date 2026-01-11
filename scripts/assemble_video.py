#!/usr/bin/env python3
"""
Assemble final documentary from video segments, narration, and sound effects.

Usage:
    python assemble_video.py --pokemon haunter --project-dir ./haunter --output haunter_final.mp4
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_audio_duration(file_path: str) -> float:
    """Get audio duration using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Warning: Could not get duration for {file_path}: {e}")
        return 7.0  # Default fallback


def sync_segment(
    video_path: str,
    audio_path: str,
    sfx_path: str,
    output_path: str,
    segment: int,
    sfx_volume: float = 0.35
) -> bool:
    """
    Synchronize a single segment: trim video to audio length and mix audio tracks.

    Args:
        video_path: Path to video segment
        audio_path: Path to narration audio
        sfx_path: Path to sound effect audio
        output_path: Where to save the processed segment
        segment: Segment number for logging
        sfx_volume: Volume level for sound effects (0.0-1.0)

    Returns:
        True if successful, False otherwise
    """
    print(f"  Processing segment {segment:02d}...")

    # Get audio duration to trim video
    audio_duration = get_audio_duration(audio_path)
    print(f"    Narration duration: {audio_duration:.2f}s")

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Build FFmpeg command
    # Trim video to audio length, mix narration at full volume with SFX at reduced volume
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-i", sfx_path,
        "-filter_complex",
        f"[0:v]trim=0:{audio_duration},setpts=PTS-STARTPTS[v];"
        f"[1:a]volume=1.0[narration];"
        f"[2:a]volume={sfx_volume}[sfx];"
        f"[narration][sfx]amix=inputs=2:duration=first[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"    Saved: {output_path}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"    Error processing segment {segment}: {e.stderr}")
        return False


def concatenate_segments(segment_paths: list[str], output_path: str) -> bool:
    """
    Concatenate all processed segments into final documentary.

    Args:
        segment_paths: List of paths to processed segments
        output_path: Where to save the final video

    Returns:
        True if successful, False otherwise
    """
    print("\nConcatenating segments into final documentary...")

    # Create a temporary file list for FFmpeg concat
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for path in segment_paths:
            # FFmpeg concat requires escaped paths
            escaped_path = path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
        concat_file = f.name

    try:
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

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Clean up temp file
        os.unlink(concat_file)

        # Get final duration
        final_duration = get_audio_duration(output_path)
        file_size = Path(output_path).stat().st_size / (1024 * 1024)

        print(f"\n{'='*50}")
        print(f"Final documentary created: {output_path}")
        print(f"Duration: {final_duration:.2f}s")
        print(f"File size: {file_size:.1f} MB")
        print(f"{'='*50}")

        # Warn if outside target range
        if final_duration < 85:
            print("Warning: Documentary is shorter than 85 seconds target")
        elif final_duration > 95:
            print("Warning: Documentary is longer than 95 seconds target")
        else:
            print("Duration is within target range (85-95 seconds)")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error concatenating segments: {e.stderr}")
        os.unlink(concat_file)
        return False


def assemble_documentary(
    pokemon: str,
    project_dir: str,
    output_path: str,
    sfx_volume: float = 0.35
) -> bool:
    """
    Assemble the complete documentary from all segments.

    Args:
        pokemon: Pokemon name for file naming
        project_dir: Project directory containing all assets
        output_path: Where to save the final documentary
        sfx_volume: Volume level for sound effects

    Returns:
        True if successful, False otherwise
    """
    project = Path(project_dir)

    # Define expected directories
    videos_dir = project / "videos"
    audio_dir = project / "audio"
    sfx_dir = project / "sfx"
    processed_dir = project / "processed"

    # Validate directories exist
    for dir_path, name in [(videos_dir, "videos"), (audio_dir, "audio"), (sfx_dir, "sfx")]:
        if not dir_path.exists():
            print(f"Error: {name} directory not found at {dir_path}")
            return False

    # Create processed directory
    processed_dir.mkdir(exist_ok=True)

    print(f"Assembling {pokemon.title()} Documentary")
    print(f"Project directory: {project_dir}")
    print(f"SFX volume: {sfx_volume}")
    print("=" * 50)

    # Process each of the 18 segments
    processed_segments = []
    success_count = 0

    for seg in range(1, 19):
        seg_str = f"{seg:02d}"

        # Find input files
        video_file = videos_dir / f"segment_{seg_str}.mp4"
        audio_file = audio_dir / f"narration_{seg_str}.mp3"
        sfx_file = sfx_dir / f"ambiance_{seg_str}.mp3"
        output_file = processed_dir / f"processed_{seg_str}.mp4"

        # Check files exist
        missing = []
        if not video_file.exists():
            missing.append(f"video: {video_file}")
        if not audio_file.exists():
            missing.append(f"audio: {audio_file}")
        if not sfx_file.exists():
            missing.append(f"sfx: {sfx_file}")

        if missing:
            print(f"  Segment {seg_str}: Missing files - {', '.join(missing)}")
            continue

        # Process segment
        if sync_segment(
            str(video_file),
            str(audio_file),
            str(sfx_file),
            str(output_file),
            seg,
            sfx_volume
        ):
            processed_segments.append(str(output_file))
            success_count += 1

    print(f"\nProcessed {success_count}/18 segments")

    if success_count == 0:
        print("Error: No segments were successfully processed")
        return False

    if success_count < 18:
        print(f"Warning: Only {success_count} segments will be included in final video")

    # Concatenate all processed segments
    return concatenate_segments(processed_segments, output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Assemble final documentary from video segments, narration, and sound effects"
    )
    parser.add_argument(
        "--pokemon",
        required=True,
        help="Pokemon name (for labeling)"
    )
    parser.add_argument(
        "--project-dir",
        required=True,
        help="Project directory containing videos/, audio/, and sfx/ subdirectories"
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
        help="Sound effects volume 0.0-1.0 (default: 0.35)"
    )

    args = parser.parse_args()

    if not 0.0 <= args.sfx_volume <= 1.0:
        print("Error: SFX volume must be between 0.0 and 1.0")
        sys.exit(1)

    success = assemble_documentary(
        args.pokemon,
        args.project_dir,
        args.output,
        args.sfx_volume
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
