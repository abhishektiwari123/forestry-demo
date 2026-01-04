#!/usr/bin/env python3
"""
Video Analysis Script - Analyzes all video segments for quality and consistency.

Checks performed:
- File integrity (size, can be opened)
- Technical specs (duration, resolution, frame rate, bitrate)
- Character consistency across segments using AI vision
- Visual quality metrics
- Continuity analysis

Usage:
    python analyze_videos.py --videos-dir /path/to/videos --pokemon charizard
"""

import os
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any
import base64
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_video_metadata(video_path: str) -> Dict[str, Any]:
    """
    Extract technical metadata from video using ffprobe.

    Args:
        video_path: Path to video file

    Returns:
        Dictionary containing video metadata
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            return {'error': 'ffprobe failed', 'details': result.stderr}

        data = json.loads(result.stdout)

        # Extract video stream info
        video_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), None)

        if not video_stream:
            return {'error': 'No video stream found'}

        metadata = {
            'duration': float(data.get('format', {}).get('duration', 0)),
            'size_mb': float(data.get('format', {}).get('size', 0)) / (1024 * 1024),
            'bitrate_kbps': int(data.get('format', {}).get('bit_rate', 0)) / 1000,
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'codec': video_stream.get('codec_name', 'unknown'),
            'fps': eval(video_stream.get('r_frame_rate', '0/1')),
            'pixel_format': video_stream.get('pix_fmt', 'unknown')
        }

        return metadata

    except subprocess.TimeoutExpired:
        return {'error': 'ffprobe timeout'}
    except Exception as e:
        return {'error': str(e)}


def extract_frame(video_path: str, timestamp: float = 2.0) -> str:
    """
    Extract a frame from video at given timestamp and return as base64.

    Args:
        video_path: Path to video file
        timestamp: Time in seconds to extract frame

    Returns:
        Base64 encoded JPEG frame
    """
    try:
        output_path = f"/tmp/frame_{Path(video_path).stem}.jpg"

        cmd = [
            'ffmpeg',
            '-y',
            '-ss', str(timestamp),
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '2',
            output_path
        ]

        subprocess.run(cmd, capture_output=True, timeout=10, check=True)

        with open(output_path, 'rb') as f:
            frame_data = base64.standard_b64encode(f.read()).decode('utf-8')

        # Cleanup
        os.remove(output_path)

        return frame_data

    except Exception as e:
        print(f"⚠️  Failed to extract frame from {video_path}: {e}")
        return None


def analyze_character_consistency(frames: List[Dict[str, str]], pokemon_name: str) -> Dict[str, Any]:
    """
    Analyze character consistency across video segments using Claude Vision.

    Args:
        frames: List of dictionaries with segment_num and base64_frame
        pokemon_name: Name of the Pokemon to check for

    Returns:
        Analysis results including consistency score and issues
    """
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    # Create content list with all frames
    content = [
        {
            "type": "text",
            "text": f"""Analyze these {len(frames)} video frames from a {pokemon_name.title()} nature documentary.

Check for:
1. **Character Consistency**: Does {pokemon_name.title()} maintain consistent appearance (color, size, design) across all frames?
2. **Visual Quality**: Are the frames clear, well-lit, and photorealistic?
3. **Continuity Issues**: Any jarring differences in character model or style between frames?
4. **Color Accuracy**: Does {pokemon_name.title()} match its official design (orange body, blue wings, flame tail)?

For each frame, note the segment number and any issues you observe.

Provide your analysis in this format:
- Overall Consistency Score: X/10
- Character Appearance: [consistent/inconsistent + details]
- Quality Issues: [list any problems]
- Recommendations: [suggestions for improvement]"""
        }
    ]

    # Add all frames as images
    for frame_info in frames:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": frame_info['base64_frame']
            }
        })
        content.append({
            "type": "text",
            "text": f"^ Segment {frame_info['segment_num']}"
        })

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": content
            }]
        )

        analysis_text = response.content[0].text

        # Parse score from response
        score = 0
        for line in analysis_text.split('\n'):
            if 'consistency score' in line.lower():
                import re
                match = re.search(r'(\d+(?:\.\d+)?)/10', line)
                if match:
                    score = float(match.group(1))
                    break

        return {
            'consistency_score': score,
            'full_analysis': analysis_text,
            'frames_analyzed': len(frames)
        }

    except Exception as e:
        return {
            'error': f"AI analysis failed: {str(e)}",
            'consistency_score': 0
        }


def analyze_videos(videos_dir: str, pokemon_name: str) -> Dict[str, Any]:
    """
    Comprehensive analysis of all video segments.

    Args:
        videos_dir: Directory containing video files
        pokemon_name: Name of the Pokemon

    Returns:
        Complete analysis report
    """
    videos_path = Path(videos_dir)
    video_files = sorted(videos_path.glob('segment_*.mp4'))

    if not video_files:
        return {'error': 'No video files found'}

    print(f"🎬 Analyzing {len(video_files)} video segments for {pokemon_name.title()}...\n")

    # Technical analysis
    print("📊 Phase 1: Technical Analysis")
    print("=" * 60)

    technical_results = []
    issues = []

    for video_file in video_files:
        segment_num = int(video_file.stem.split('_')[1])
        file_size_mb = video_file.stat().st_size / (1024 * 1024)

        print(f"Segment {segment_num:02d}: ", end='')

        # Check file integrity
        if file_size_mb < 0.001:
            print(f"❌ CORRUPTED (only {file_size_mb:.3f} MB)")
            issues.append(f"Segment {segment_num}: Corrupted file (too small)")
            continue

        # Get metadata
        metadata = get_video_metadata(str(video_file))

        if 'error' in metadata:
            print(f"❌ ERROR: {metadata['error']}")
            issues.append(f"Segment {segment_num}: {metadata['error']}")
            continue

        # Check duration (should be ~8 seconds)
        duration = metadata['duration']
        if duration < 4:
            print(f"⚠️  SHORT ({duration:.1f}s)")
            issues.append(f"Segment {segment_num}: Too short ({duration:.1f}s)")
        elif duration > 12:
            print(f"⚠️  LONG ({duration:.1f}s)")
            issues.append(f"Segment {segment_num}: Too long ({duration:.1f}s)")
        else:
            print(f"✅ {duration:.1f}s, {metadata['width']}x{metadata['height']}, {metadata['size_mb']:.1f}MB")

        technical_results.append({
            'segment': segment_num,
            'file': video_file.name,
            'metadata': metadata
        })

    # Calculate technical stats
    avg_duration = sum(r['metadata']['duration'] for r in technical_results) / len(technical_results)
    total_duration = sum(r['metadata']['duration'] for r in technical_results)
    avg_size = sum(r['metadata']['size_mb'] for r in technical_results) / len(technical_results)

    print(f"\n📈 Technical Summary:")
    print(f"   Total Duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print(f"   Average Duration: {avg_duration:.1f}s per segment")
    print(f"   Average File Size: {avg_size:.1f} MB")
    print(f"   Total Issues: {len(issues)}")

    # Visual consistency analysis
    print(f"\n🎨 Phase 2: Character Consistency Analysis")
    print("=" * 60)
    print("Extracting frames from videos...")

    frames = []
    for video_file in video_files[:18]:  # Analyze up to 18 segments
        segment_num = int(video_file.stem.split('_')[1])

        # Extract frame at 2 seconds
        frame_b64 = extract_frame(str(video_file), timestamp=2.0)

        if frame_b64:
            frames.append({
                'segment_num': segment_num,
                'base64_frame': frame_b64
            })
            print(f"  ✓ Segment {segment_num:02d}")

    print(f"\nAnalyzing {len(frames)} frames with AI vision...")

    consistency_analysis = analyze_character_consistency(frames, pokemon_name)

    if 'error' not in consistency_analysis:
        print(f"\n{'='*60}")
        print(f"🎯 Consistency Score: {consistency_analysis['consistency_score']}/10")
        print(f"{'='*60}")
        print(consistency_analysis['full_analysis'])
    else:
        print(f"❌ {consistency_analysis['error']}")

    # Final report
    report = {
        'pokemon': pokemon_name,
        'total_segments': len(video_files),
        'technical_analysis': {
            'segments': technical_results,
            'stats': {
                'total_duration_seconds': total_duration,
                'average_duration_seconds': avg_duration,
                'average_file_size_mb': avg_size
            },
            'issues': issues
        },
        'consistency_analysis': consistency_analysis
    }

    return report


def main():
    parser = argparse.ArgumentParser(description='Analyze Pokemon documentary video segments')
    parser.add_argument('--videos-dir', required=True, help='Directory containing video files')
    parser.add_argument('--pokemon', required=True, help='Pokemon name')
    parser.add_argument('--output', help='Output JSON file for report (optional)')

    args = parser.parse_args()

    # Run analysis
    report = analyze_videos(args.videos_dir, args.pokemon)

    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📝 Report saved to: {args.output}")

    # Print summary
    if 'error' not in report:
        print(f"\n{'='*60}")
        print(f"📋 FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"Total Segments: {report['total_segments']}")
        print(f"Total Duration: {report['technical_analysis']['stats']['total_duration_seconds']:.1f}s")
        print(f"Technical Issues: {len(report['technical_analysis']['issues'])}")
        if 'consistency_score' in report.get('consistency_analysis', {}):
            print(f"Consistency Score: {report['consistency_analysis']['consistency_score']}/10")

        if report['technical_analysis']['issues']:
            print(f"\n⚠️  Issues Found:")
            for issue in report['technical_analysis']['issues']:
                print(f"   - {issue}")
        else:
            print(f"\n✅ No technical issues found!")


if __name__ == '__main__':
    main()
