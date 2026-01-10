#!/usr/bin/env python3
"""
Real-time progress viewer for batch video generation.
Monitors log file and displays current status.
"""

import os
import sys
import time
import glob
from datetime import datetime

def get_video_count():
    """Count generated videos."""
    videos = glob.glob("charizard/battle_assets/videos/seg*_video.mp4")
    return len(videos)

def get_total_size():
    """Get total size of generated videos in MB."""
    videos = glob.glob("charizard/battle_assets/videos/*.mp4")
    total = sum(os.path.getsize(v) for v in videos)
    return total / (1024 * 1024)

def parse_log_for_current_segment():
    """Parse log to find current segment being generated."""
    log_file = "charizard/battle_assets/video_generation_log.txt"

    if not os.path.exists(log_file):
        return None, 0

    with open(log_file, 'r') as f:
        lines = f.readlines()

    current_segment = None
    elapsed = 0

    # Read backwards to find most recent segment
    for line in reversed(lines):
        if "Generating Video: Segment" in line:
            try:
                current_segment = int(line.split("Segment")[1].strip())
                break
            except:
                pass
        elif "Elapsed:" in line and "s " in line:
            # Extract last elapsed time
            parts = line.split("Elapsed:")[-1].strip().split()
            if parts:
                try:
                    elapsed = int(parts[-1].rstrip('s'))
                except:
                    pass

    return current_segment, elapsed

def display_progress(clear_screen=True):
    """Display current progress."""
    if clear_screen:
        os.system('clear' if os.name != 'nt' else 'cls')

    print("🎬 " + "="*70)
    print("   POKEMON AI VIDEO GENERATOR - BATCH PROGRESS")
    print("="*72)
    print()

    # Get current stats
    video_count = get_video_count()
    total_size = get_total_size()
    current_seg, elapsed = parse_log_for_current_segment()

    # Calculate progress
    total_segments = 18
    progress_pct = (video_count / total_segments) * 100

    # Display main stats
    print(f"📊 OVERALL PROGRESS")
    print(f"   Videos Complete: {video_count}/{total_segments} ({progress_pct:.1f}%)")
    print(f"   Total Size: {total_size:.1f} MB")
    print()

    # Progress bar
    bar_width = 50
    filled = int(bar_width * video_count / total_segments)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"   [{bar}] {progress_pct:.1f}%")
    print()

    # Current segment status
    if current_seg:
        print(f"⏳ CURRENT: Segment {current_seg}")
        print(f"   Elapsed: {elapsed}s")

        if elapsed > 0:
            # Estimate based on elapsed time
            if elapsed < 60:
                status = "🟡 Uploading/Initializing..."
            elif elapsed < 150:
                status = "🟢 Generating video..."
            else:
                status = "🔵 Downloading..."
            print(f"   Status: {status}")
    else:
        if video_count == total_segments:
            print("✅ ALL VIDEOS COMPLETE!")
        else:
            print("⏸️  Waiting to start...")

    print()

    # List completed videos
    print(f"✅ COMPLETED VIDEOS:")
    videos = sorted(glob.glob("charizard/battle_assets/videos/seg*_video.mp4"))
    if videos:
        for video in videos:
            seg_num = video.split("seg")[1].split("_")[0]
            size = os.path.getsize(video) / (1024 * 1024)
            print(f"   • Segment {seg_num}: {size:.1f} MB")
    else:
        print("   (none yet)")

    print()

    # Remaining segments
    remaining = total_segments - video_count
    if remaining > 0:
        avg_time_per_video = 2.5  # minutes
        est_remaining = remaining * avg_time_per_video
        print(f"⏱️  ESTIMATED TIME REMAINING: {est_remaining:.0f} minutes")
        print(f"   ({remaining} videos @ ~{avg_time_per_video} min each)")

    print()
    print("="*72)
    print(f"📅 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    print("="*72)
    print()
    print("Press Ctrl+C to exit viewer (generation continues in background)")

def watch_progress(interval=5):
    """Watch progress with auto-refresh."""
    print("Starting video generation progress viewer...")
    print(f"Refreshing every {interval} seconds...")
    print()
    time.sleep(2)

    try:
        while True:
            display_progress()

            # Check if complete
            if get_video_count() >= 18:
                print("\n🎉 All videos generated! Exiting viewer...")
                break

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n⏸️  Progress viewer stopped (generation still running in background)")
        print("Run this script again to resume monitoring.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Monitor video generation progress")
    parser.add_argument("--once", action="store_true", help="Show status once and exit")
    parser.add_argument("--interval", type=int, default=5, help="Refresh interval in seconds")

    args = parser.parse_args()

    if args.once:
        display_progress(clear_screen=False)
    else:
        watch_progress(args.interval)
