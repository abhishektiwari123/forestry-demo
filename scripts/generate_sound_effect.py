#!/usr/bin/env python3
"""
Generate atmospheric sound effects using ElevenLabs Sound Effects API.

Usage:
    python generate_sound_effect.py --prompt "Ancient forest ambiance..." --duration 8.0 --output sfx/ambiance_01.mp3 --segment 1
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Load environment variables
load_dotenv()


def generate_sound_effect(
    prompt: str,
    duration: float,
    output_path: str,
    segment: int
) -> bool:
    """
    Generate an atmospheric sound effect using ElevenLabs API.

    Args:
        prompt: Description of the sound effect to generate
        duration: Duration in seconds (typically 6-8)
        output_path: Where to save the audio file
        segment: Segment number (1-18) for logging

    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in environment variables")
        return False

    print(f"Generating sound effect for segment {segment:02d}")
    print(f"  Prompt: {prompt[:60]}...")
    print(f"  Duration: {duration}s")

    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)

        # Generate sound effect
        print("  Generating audio...")

        # Note: The exact API method may vary based on ElevenLabs SDK version
        # This uses the sound effects generation endpoint
        audio_generator = client.text_to_sound_effects.convert(
            text=prompt,
            duration_seconds=duration,
            prompt_influence=0.3  # Lower = more creative interpretation
        )

        # Create output directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save audio file
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        file_size = Path(output_path).stat().st_size / 1024
        print(f"  Success! Saved to {output_path} ({file_size:.1f} KB)")
        return True

    except AttributeError:
        # Fallback for different SDK versions
        print("  Note: Trying alternative API method...")
        try:
            # Alternative method name
            audio = client.generate_sound_effects(
                text=prompt,
                duration_seconds=duration,
                prompt_influence=0.3
            )

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(audio)

            file_size = Path(output_path).stat().st_size / 1024
            print(f"  Success! Saved to {output_path} ({file_size:.1f} KB)")
            return True

        except Exception as e2:
            print(f"Error with alternative method: {e2}")
            return False

    except Exception as e:
        print(f"Error generating sound effect: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate atmospheric sound effects using ElevenLabs"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Description of the sound effect to generate"
    )
    parser.add_argument(
        "--duration",
        type=float,
        required=True,
        help="Duration in seconds (typically 6-8)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output audio file path"
    )
    parser.add_argument(
        "--segment",
        type=int,
        required=True,
        help="Segment number (1-18)"
    )

    args = parser.parse_args()

    if not 1 <= args.segment <= 18:
        print("Error: Segment must be between 1 and 18")
        sys.exit(1)

    if args.duration < 1 or args.duration > 22:
        print("Error: Duration must be between 1 and 22 seconds")
        sys.exit(1)

    success = generate_sound_effect(args.prompt, args.duration, args.output, args.segment)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
