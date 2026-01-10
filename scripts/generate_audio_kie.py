#!/usr/bin/env python3
"""
Generate narration audio for all battle story segments using ElevenLabs Text-to-Speech Turbo 2.5 via KIE.ai API.
Consistent with our video generation workflow.
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv
import urllib3

# Disable SSL warnings for tempfile downloads
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# Narration text for all 18 segments extracted from battle story script
SEGMENT_NARRATIONS = {
    1: "In the legendary Charicific Valley, where only the strongest Charizard train, our hero patrols the morning sky.",
    2: "But today, a challenger arrives—Dragonite, the dragon master, seeking worthy opponents.",
    3: "Ancient rivals meet—fire dragon versus dragon master. Only one will claim the sky.",
    4: "Charizard accepts the challenge!",
    5: "Charizard strikes first with a devastating Flamethrower!",
    6: "But Dragonite's speed is incredible—countering with Thunder Punch!",
    7: "The attack connects! Charizard reels from the blow...",
    8: "...but refuses to yield!",
    9: "Both dragons unleash their fury—Dragon Rage!",
    10: "Through the chaos, Charizard sees its opening!",
    11: "With incredible speed, Charizard closes in...",
    12: "...catching Dragonite in an unbreakable grip!",
    13: "Charizard's signature move—the legendary Seismic Toss!",
    14: "The finishing blow!",
    15: "Charizard lands, victorious but honorable.",
    16: "Dragonite rises—no longer rivals, but warriors who've shared battle.",
    17: "The valley's defenders roar their approval. Charizard has proven worthy.",
    18: "In the Valley of Rivals, strength is proven through battle... but greatness is earned through honor."
}

def generate_audio(text: str, segment_num: int, voice: str = "Brian", output_dir: str = "charizard/battle_assets/audio"):
    """
    Generate narration audio using ElevenLabs Text-to-Speech Turbo 2.5 via KIE.ai.

    Args:
        text: Narration text
        segment_num: Segment number
        voice: Voice to use (default: Brian - deep narrator voice)
        output_dir: Directory to save audio files

    Returns:
        Path to generated audio file, or None if failed
    """
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("❌ Error: KIE_API_KEY not found in .env")
        sys.exit(1)

    print(f"\n🎙️  Generating Audio: Segment {segment_num}")
    print(f"━" * 60)
    print(f"📝 Narration: {text}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # ElevenLabs payload - optimized for documentary narration
    payload = {
        "model": "elevenlabs/text-to-speech-turbo-2-5",
        "input": {
            "text": text,
            "voice": voice,  # Brian for deep narrator, Daniel/George for alternatives
            "stability": 0.6,  # Slightly higher for consistent narrator voice
            "similarity_boost": 0.8,  # Higher for better voice clarity
            "style": 0.3,  # Slight dramatic emphasis for documentary style
            "speed": 0.95,  # Slightly slower for clarity and dramatic effect
            "timestamps": False,
            "previous_text": "",
            "next_text": "",
            "language_code": ""
        }
    }

    print(f"🚀 Submitting to ElevenLabs API...")

    # Submit generation request
    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    result = response.json()

    if result.get("code") != 200:
        print(f"❌ Task creation failed: {result.get('msg', 'Unknown error')}")
        return None

    task_id = result["data"]["taskId"]
    print(f"⏳ Task ID: {task_id}")
    print(f"⏳ Generating audio (typically 10-30 seconds)...")
    print(f"   Elapsed: ", end="", flush=True)

    # Poll for completion
    max_wait = 120  # 2 minutes max
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(5)
        elapsed += 5
        print(f"{elapsed}s ", end="", flush=True)

        status_response = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status_response.status_code != 200:
            continue

        status_data = status_response.json()

        if status_data.get("code") != 200:
            continue

        data = status_data.get("data", {})
        state = data.get("state")

        if state == "success":
            print(f"\n✅ Audio generated successfully!")

            # Download audio
            result_json = json.loads(data["resultJson"])
            audio_url = result_json["resultUrls"][0]

            print(f"📥 Downloading from: {audio_url}")

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Download audio file (with SSL verification disabled for tempfile domains)
            audio_response = requests.get(audio_url, stream=True, verify=False, timeout=30)

            if audio_response.status_code != 200:
                print(f"❌ Download failed: {audio_response.status_code}")
                print(f"Response: {audio_response.text[:200]}")
                return None

            output_path = os.path.join(output_dir, f"seg{segment_num:02d}_narration.mp3")

            with open(output_path, 'wb') as f:
                for chunk in audio_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(output_path) / 1024  # KB
            print(f"✅ Saved to: {output_path}")
            print(f"📊 File size: {file_size:.2f} KB")
            print(f"━" * 60)
            return output_path

        elif state == "fail":
            print(f"\n❌ Audio generation failed")
            error_msg = data.get("failMsg", "Unknown error")
            print(f"Error: {error_msg}")
            return None

    print(f"\n❌ Timeout after {max_wait}s")
    return None


def generate_all_narrations(voice: str = "Brian", start_from: int = 1):
    """
    Generate narration audio for all segments.

    Args:
        voice: Voice to use for all narrations
        start_from: Segment number to start from (useful for resuming)
    """
    print("🎙️  BATCH AUDIO GENERATION: ALL SEGMENTS")
    print("=" * 60)
    print(f"Voice: {voice}")
    print(f"Total segments: 18")
    print(f"Starting from: Segment {start_from}")
    print("=" * 60)

    success_count = 0
    failed_segments = []

    for seg_num in range(start_from, 19):
        narration = SEGMENT_NARRATIONS[seg_num]

        result = generate_audio(narration, seg_num, voice)

        if result:
            success_count += 1
            print(f"✅ Progress: {success_count}/{18 - start_from + 1} complete")
        else:
            failed_segments.append(seg_num)
            print(f"❌ Failed: Segment {seg_num}")

        # Brief pause between segments to avoid rate limits
        if seg_num < 18:
            time.sleep(2)

    print(f"\n{'=' * 60}")
    print(f"🎉 BATCH GENERATION COMPLETE!")
    print(f"✅ Success: {success_count}/{18 - start_from + 1}")
    print(f"❌ Failed: {len(failed_segments)}/{18 - start_from + 1}")

    if failed_segments:
        print(f"Failed segments: {failed_segments}")
        print(f"\nTo retry failed segments, run:")
        for seg in failed_segments:
            print(f"  python scripts/generate_audio_kie.py --segment {seg}")
    else:
        print(f"\n🎊 ALL NARRATIONS GENERATED SUCCESSFULLY!")
        print(f"Next step: Generate videos and assemble documentary")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate narration audio for battle story segments")
    parser.add_argument("--segment", type=int, help="Generate audio for specific segment (1-18)")
    parser.add_argument("--voice", default="Brian", help="Voice to use (Brian/Daniel/George/Will)")
    parser.add_argument("--start-from", type=int, default=1, help="Start from segment number")
    parser.add_argument("--test", action="store_true", help="Test with segment 1 only")
    parser.add_argument("--all", action="store_true", help="Generate all 18 narrations")

    args = parser.parse_args()

    if args.test:
        print("🧪 TEST MODE: Generating Segment 1 only")
        generate_audio(SEGMENT_NARRATIONS[1], 1, args.voice)
    elif args.segment:
        if args.segment < 1 or args.segment > 18:
            print("❌ Error: Segment must be between 1 and 18")
            sys.exit(1)
        narration = SEGMENT_NARRATIONS[args.segment]
        generate_audio(narration, args.segment, args.voice)
    elif args.all:
        generate_all_narrations(args.voice, args.start_from)
    else:
        print("Usage:")
        print("  --test          Generate test audio (segment 1)")
        print("  --segment N     Generate audio for segment N")
        print("  --all           Generate all 18 narrations")
        print("  --voice NAME    Voice to use (default: Brian)")
        print("\nExample: python scripts/generate_audio_kie.py --test")
