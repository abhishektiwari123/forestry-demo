#!/usr/bin/env python3
"""
Test the CINEMATIC prompt format with 16:9 aspect ratio.
Uses the user's proven prompt format with timestamps and action sequence.

Usage:
    python scripts/test_cinematic_prompt.py
"""

import subprocess
import json
import os
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import our prompt validator
import sys
sys.path.insert(0, os.path.dirname(__file__))
from prompt_validator import PromptValidator

# API Configuration
def get_api_key():
    """Get API key from environment or .env file."""
    if os.environ.get("KIE_API_KEY"):
        return os.environ.get("KIE_API_KEY")

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("KIE_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return ""

API_KEY = get_api_key()


def generate_cinematic_prompt(pokemon_names: list, environment: str = "volcanic") -> str:
    """
    Generate cinematic prompt using the USER'S PROVEN FORMAT.
    Key features:
    - 10-second action sequence with timestamps
    - OPENING (0-4s), TRANSITION (4-6s), FINALE (6-10s)
    - Very detailed Pokemon descriptions with specific colors
    - Explicit facial expressions and reactions
    """
    p1_name = pokemon_names[0]
    p2_name = pokemon_names[1]

    # Pokemon-specific details matching user's format
    pokemon_details = {
        "Charizard": {
            "height": "5'7\"",
            "desc": "lean orange dragon with realistic detailed reptilian scales, teal wings, cream belly, flaming tail",
            "attack": "orange-red Flamethrower stream",
            "attack_effect": "massive flames",
            "damage_type": "BLACKENED BURNT SCORCH MARKS and charred patterns from Flamethrower impact",
            "wing_color": "teal wings"
        },
        "Dragonite": {
            "height": "7'3\"",
            "desc": "bulky ORANGE-TAN body with realistic scales, teal wings, two antennae, cream belly stripes, NO tail flame",
            "attack": "orange-purple Dragon Pulse beam",
            "attack_effect": "massive energy beam",
            "damage_type": "BLACKENED IMPACT DAMAGE and energy burns",
            "wing_color": "teal wings"
        },
        "Pikachu": {
            "height": "1'4\"",
            "desc": "small yellow electric mouse with red cheek pouches, lightning bolt tail, pointy ears with black tips",
            "attack": "bright yellow Thunderbolt lightning",
            "attack_effect": "massive electrical discharge",
            "damage_type": "ELECTRICAL BURN MARKS and singed fur",
            "wing_color": ""
        },
        "Mewtwo": {
            "height": "6'7\"",
            "desc": "pale purple humanoid with long thick tail, three-fingered hands, piercing purple eyes, psychic aura",
            "attack": "purple Psychic energy waves",
            "attack_effect": "massive telekinetic force",
            "damage_type": "PSYCHIC DAMAGE with visible distortion marks",
            "wing_color": ""
        }
    }

    p1 = pokemon_details.get(p1_name, pokemon_details["Charizard"])
    p2 = pokemon_details.get(p2_name, pokemon_details["Dragonite"])

    # Environment descriptions
    env_map = {
        "volcanic": "volcanic valley background with lava pools and smoke",
        "forest": "ancient forest background with towering trees and dappled sunlight",
        "ocean": "coastal cliffs background with crashing waves and stormy sky",
        "cave": "underground cavern background with glowing crystals",
        "mountain": "mountain peak background above clouds"
    }
    env_desc = env_map.get(environment, env_map["volcanic"])

    # Build prompt using USER'S EXACT FORMAT
    prompt = f"""PHOTOREALISTIC hyperrealistic CGI render: COMPLETE 10-SECOND ACTION SEQUENCE with BOTH Pokemon: OPENING (0-4s): Smaller {p1_name} ({p1['height']}, {p1['desc']}) on LEFT side launching massive sustained {p1['attack']} from open jaws with fierce determined expression, flames traveling across frame toward significantly larger {p2_name} ({p2['height']}, 30% bigger, {p2['desc']}) on RIGHT side, {p2_name} with PAINED FACIAL EXPRESSION (eyes squinting in pain, mouth open wide showing teeth in grimace, eyebrows furrowed in distress, face contorted) being PUSHED BACKWARD by force of {p1['attack_effect']}, body leaning back and recoiling from heat and impact, attempting to brace with arms raised defensively but failing against overwhelming fire stream, flame stream clearly connecting both Pokemon with visible bright orange-red impact glow where flames strike {p2_name}'s torso, intense heat distortion and fire sparks bursting from impact point, physical knockback evident. TRANSITION (4-6s): Flames dissipating, close-up on {p2_name}'s torso and cream belly revealing {p2['damage_type']}, smoke wisping from burnt scales showing realistic heat damage texture, {p2_name}'s facial expression transitioning from PAIN to FIERCE ANGER (eyes narrowing with determination and rage, teeth bared in aggressive snarl, eyebrows furrowed in fury showing intense resolve for revenge). FINALE (6-10s): {p2_name} recovering from knockback and CHARGING FORWARD aggressively toward {p1_name} with {p2['wing_color'] or 'wings'} spread wide pulling back for powerful counter-attack, body accelerating rapidly with building momentum, {p1_name} visible in frame bracing for incoming revenge attack, dramatic battle tension rising, side-angle wide shot capturing complete revenge charge sequence, realistic physics with dynamic motion, camera starts side-angle capturing both Pokemon, zooms into impact showing damage and pain, then pulls back wide as {p2_name} charges forward for revenge, realistic detailed reptilian scales with texture depth, leathery wing texture, natural lighting with physically accurate shadows, organic weathering appearance, dramatic cinematic composition, 8K quality, {env_desc}, battle-worn with scratches and scars visible, weathered appearance"""

    return prompt


def test_cinematic_prompt():
    """Test the cinematic prompt format with 16:9 aspect ratio."""
    print("=" * 60)
    print("CINEMATIC STORYBOARD PROMPT TEST")
    print("Format: 16:9 aspect ratio, JPG output")
    print("=" * 60)

    if not API_KEY:
        print("ERROR: KIE_API_KEY not found!")
        return False

    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")

    # Generate cinematic prompt
    pokemon_names = ["Charizard", "Dragonite"]
    environment = "volcanic"

    print(f"\nPokemon: {pokemon_names[0]} vs {pokemon_names[1]}")
    print(f"Environment: {environment}")

    prompt = generate_cinematic_prompt(pokemon_names, environment)

    print("\n" + "=" * 60)
    print("GENERATED CINEMATIC PROMPT:")
    print("=" * 60)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("\n" + "-" * 60)
    print(f"Prompt length: {len(prompt)} characters")
    print("=" * 60)

    # Build API payload - Nano Banana Pro API format
    # Using 16:9 aspect ratio and JPG (user's proven format)
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "image_input": [],
            "aspect_ratio": "16:9",  # Widescreen format
            "resolution": "2K",
            "output_format": "jpg"  # JPG as per user's format
        }
    }

    print("\n[Step 1] Submitting to API...")
    print(f"Payload: aspect_ratio=16:9, resolution=2K, output_format=jpg")
    print(f"Payload size: {len(json.dumps(payload))} bytes")

    # Submit via curl
    curl_cmd = [
        "curl", "-k", "-s", "-X", "POST",
        "https://api.kie.ai/api/v1/jobs/createTask",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        print(f"ERROR: curl failed: {result.stderr}")
        return False

    try:
        response = json.loads(result.stdout)
        print(f"Response: {json.dumps(response, indent=2)[:500]}")

        if response.get("code") != 200:
            print(f"ERROR: API error: {response.get('msg') or response.get('message')}")
            return False

        task_id = response.get("data", {}).get("taskId")
        if not task_id:
            print("ERROR: No task ID returned")
            return False

        print(f"\n✅ Task submitted: {task_id}")

        # Poll for completion
        print("\n[Step 2] Waiting for completion...")
        for i in range(60):  # Max 5 minutes
            time.sleep(5)

            status_cmd = [
                "curl", "-k", "-s",
                f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                "-H", f"Authorization: Bearer {API_KEY}"
            ]

            status_result = subprocess.run(status_cmd, capture_output=True, text=True, timeout=30)

            if status_result.returncode != 0 or not status_result.stdout.strip():
                print(f"  [{(i+1)*5}s] Waiting... (no response)")
                continue

            try:
                status_json = json.loads(status_result.stdout)
            except json.JSONDecodeError:
                print(f"  [{(i+1)*5}s] Waiting... (invalid response)")
                continue

            state = status_json.get("data", {}).get("state", "").lower()

            print(f"  [{(i+1)*5}s] State: {state}")

            if state == "success":
                result_json = status_json.get("data", {}).get("resultJson", "{}")
                if isinstance(result_json, str):
                    result_json = json.loads(result_json)

                urls = result_json.get("resultUrls", [])
                if urls:
                    print(f"\n✅ SUCCESS!")
                    print(f"Image URL: {urls[0]}")

                    # Download the image
                    output_path = "test_output/cinematic_storyboard.jpg"
                    os.makedirs("test_output", exist_ok=True)

                    dl_cmd = ["curl", "-k", "-L", "-s", "-o", output_path, urls[0]]
                    subprocess.run(dl_cmd, timeout=60)

                    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                        print(f"Downloaded to: {output_path}")
                        print(f"File size: {os.path.getsize(output_path)} bytes")

                    return True

                print("ERROR: No URLs in response")
                return False

            elif state in ["failed", "error"]:
                fail_msg = status_json.get("data", {}).get("failMsg", "Unknown error")
                print(f"\n❌ FAILED: {fail_msg}")
                return False

        print("\n❌ TIMEOUT: Generation took too long")
        return False

    except Exception as e:
        print(f"ERROR: {type(e).__name__} - {e}")
        return False


def main():
    success = test_cinematic_prompt()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - Check test_output/cinematic_storyboard.jpg")
    else:
        print("❌ TEST FAILED")
    print("=" * 60)


if __name__ == "__main__":
    main()
