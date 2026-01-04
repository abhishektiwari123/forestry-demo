#!/usr/bin/env python3
"""
Generate sound effects using ElevenLabs Sound Effects API.

Usage:
    python generate_sound_effect.py --prompt "Atmospheric sound description" --duration 7.0 --output "segment_01.mp3" --segment 1
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Load environment variables
load_dotenv()

def generate_sound_effect(prompt: str, duration: float, output_path: str, segment_num: int) -> bool:
    """
    Generate sound effect using ElevenLabs.

    Args:
        prompt: Sound effect description
        duration: Duration in seconds (should match narration)
        output_path: Where to save audio file
        segment_num: Segment number for logging

    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ Error: ELEVENLABS_API_KEY not found in environment variables")
        print("Please set it in scripts/.env")
        return False

    try:
        print(f"\n🔊 Generating sound effect for Segment {segment_num}")
        print(f"📝 Prompt: {prompt[:100]}...")
        print(f"⏱️  Duration: {duration}s")

        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)

        # Generate sound effect
        # Note: Adjust based on actual ElevenLabs Sound Effects API
        audio = client.generate_sound_effects(
            text=prompt,
            duration_seconds=duration,
            prompt_influence=0.3  # How strictly to follow prompt
        )

        # Save audio file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)

        print(f"✅ Sound effect saved to: {output_path}")
        return True

    except AttributeError:
        print("⚠️  Note: ElevenLabs Sound Effects API method may differ.")
        print("    Please check ElevenLabs documentation for the correct API.")
        print("    This is a template - adjust based on actual API specification.")
        return False

    except Exception as e:
        print(f"❌ Error generating sound effect: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate sound effects using ElevenLabs"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Sound effect description (atmospheric, detailed)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        required=True,
        help="Duration in seconds (match corresponding narration)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output audio path (e.g., '../haunter/sfx/segment_01.mp3')"
    )
    parser.add_argument(
        "--segment",
        type=int,
        required=True,
        help="Segment number (1-18)"
    )

    args = parser.parse_args()

    success = generate_sound_effect(args.prompt, args.duration, args.output, args.segment)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
