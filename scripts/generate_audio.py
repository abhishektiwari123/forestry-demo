#!/usr/bin/env python3
"""
Generate narration audio using ElevenLabs v3.

Usage:
    python generate_audio.py --text "Narration text..." --output "segment_01.mp3" --segment 1
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

# Load environment variables
load_dotenv()

def generate_audio(text: str, output_path: str, segment_num: int, voice_id: str = None) -> bool:
    """
    Generate narration audio using ElevenLabs.

    Args:
        text: Narration text
        output_path: Where to save audio file
        segment_num: Segment number for logging
        voice_id: ElevenLabs voice ID (defaults to British narrator)

    Returns:
        True if successful, False otherwise
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ Error: ELEVENLABS_API_KEY not found in environment variables")
        print("Please set it in scripts/.env")
        return False

    # Default to David Attenborough-style voice
    if not voice_id:
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    try:
        print(f"\n🎙️  Generating narration for Segment {segment_num}")
        print(f"📝 Text: {text}")
        print(f"🔊 Voice ID: {voice_id}")

        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)

        # Configure voice settings
        voice_settings = VoiceSettings(
            stability=0.55,         # Balanced natural variation
            similarity_boost=0.75,  # Maintain voice character
            style=0.35,            # Subtle dramatic emphasis
            use_speaker_boost=True  # Enhanced clarity
        )

        # Generate audio using the correct API method
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",  # or "eleven_turbo_v2" for faster
            voice_settings=voice_settings
        )

        # Save audio file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)

        print(f"✅ Audio saved to: {output_path}")

        # Check duration
        try:
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-i', str(output_path), '-show_entries',
                 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
                capture_output=True,
                text=True
            )
            duration = float(result.stdout.strip())
            print(f"⏱️  Duration: {duration:.2f} seconds")

            if duration > 8.5:
                print(f"⚠️  Warning: Audio is longer than 8 seconds!")
                print(f"   Consider shortening the narration text.")
            elif duration < 5.5:
                print(f"⚠️  Warning: Audio is shorter than 6 seconds.")
                print(f"   Consider expanding the narration text.")

        except Exception as e:
            print(f"ℹ️  Could not check duration (ffprobe not available): {e}")

        return True

    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate narration audio using ElevenLabs"
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Narration text (6-8 seconds worth, ~15-26 words)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output audio path (e.g., '../haunter/audio/segment_01.mp3')"
    )
    parser.add_argument(
        "--segment",
        type=int,
        required=True,
        help="Segment number (1-18)"
    )
    parser.add_argument(
        "--voice-id",
        help="ElevenLabs voice ID (optional, defaults to British narrator)"
    )

    args = parser.parse_args()

    success = generate_audio(args.text, args.output, args.segment, args.voice_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
