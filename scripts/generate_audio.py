#!/usr/bin/env python3
"""
Generate David Attenborough-style narration using ElevenLabs v3 TTS.

Usage:
    python generate_audio.py --text "In the depths of an ancient forest..." --output audio/narration_01.mp3 --segment 1
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

# Load environment variables
load_dotenv()

# Default voice ID for British narrator (similar to Attenborough)
# You can find voice IDs at: https://elevenlabs.io/voice-library
DEFAULT_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam - British narrator


def get_audio_duration(file_path: str) -> float | None:
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
            text=True
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def generate_audio(
    text: str,
    output_path: str,
    segment: int,
    voice_id: str | None = None
) -> bool:
    """
    Generate narration audio using ElevenLabs TTS.

    Args:
        text: Narration text to convert to speech
        output_path: Where to save the audio file
        segment: Segment number (1-18) for logging
        voice_id: Optional custom voice ID

    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in environment variables")
        return False

    # Use custom voice or environment variable or default
    voice = voice_id or os.getenv("ELEVENLABS_VOICE_ID") or DEFAULT_VOICE_ID

    print(f"Generating narration for segment {segment:02d}")
    print(f"  Text: {text[:60]}...")
    print(f"  Voice: {voice}")

    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)

        # Configure voice settings for Attenborough-style delivery
        voice_settings = VoiceSettings(
            stability=0.55,          # Slightly lower for natural variation
            similarity_boost=0.75,   # High to maintain voice character
            style=0.35,              # Moderate expressiveness
            use_speaker_boost=True   # Enhanced clarity
        )

        # Generate audio
        print("  Generating audio...")
        audio_generator = client.text_to_speech.convert(
            voice_id=voice,
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=voice_settings
        )

        # Create output directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save audio file
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        # Check duration
        duration = get_audio_duration(output_path)
        if duration:
            print(f"  Duration: {duration:.2f}s")

            # Warn if outside expected range
            if duration > 8.5:
                print(f"  Warning: Audio is longer than 8.5s - may need trimming")
            elif duration < 5.5:
                print(f"  Warning: Audio is shorter than 5.5s - may need more text")
        else:
            print("  Note: Could not determine duration (ffprobe not available)")

        file_size = Path(output_path).stat().st_size / 1024
        print(f"  Success! Saved to {output_path} ({file_size:.1f} KB)")
        return True

    except Exception as e:
        print(f"Error generating audio: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate David Attenborough-style narration using ElevenLabs"
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Narration text to convert to speech"
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
    parser.add_argument(
        "--voice-id",
        type=str,
        default=None,
        help="Custom ElevenLabs voice ID (optional)"
    )

    args = parser.parse_args()

    if not 1 <= args.segment <= 18:
        print("Error: Segment must be between 1 and 18")
        sys.exit(1)

    success = generate_audio(args.text, args.output, args.segment, args.voice_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
