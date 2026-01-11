#!/usr/bin/env python3
"""
Test the optimized storyboard prompt format.
Uses the proven format with 2048x2048 resolution and additional parameters.

Usage:
    python scripts/test_optimized_prompt.py
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


def test_optimized_prompt():
    """Test the optimized prompt format."""
    print("=" * 60)
    print("OPTIMIZED STORYBOARD PROMPT TEST")
    print("=" * 60)

    if not API_KEY:
        print("ERROR: KIE_API_KEY not found!")
        return False

    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")

    # Create validator
    validator = PromptValidator()

    # Generate optimized prompt
    pokemon_names = ["Charizard", "Dragonite"]
    environment = "volcanic"

    print(f"\nPokemon: {pokemon_names[0]} vs {pokemon_names[1]}")
    print(f"Environment: {environment}")

    # Get optimized config
    prompt_config = validator.generate_optimized_storyboard_prompt(
        pokemon_names=pokemon_names,
        environment=environment
    )

    print("\n" + "=" * 60)
    print("GENERATED PROMPT:")
    print("=" * 60)
    print(prompt_config["prompt"])
    print("\n" + "-" * 60)
    print(f"Prompt length: {len(prompt_config['prompt'])} characters")
    print(f"Model: {prompt_config.get('model', 'nano-banana-pro')}")
    print(f"Resolution: {prompt_config.get('resolution', '2K')}")
    print(f"Aspect Ratio: {prompt_config.get('aspect_ratio', '1:1')}")
    print("=" * 60)

    # Build API payload - Nano Banana Pro API format
    # Model: nano-banana-pro (NOT google/nano-banana)
    # Uses: resolution (1K, 2K, 4K) and aspect_ratio
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt_config["prompt"],
            "image_input": [],
            "aspect_ratio": "1:1",  # Square for 4-panel grid
            "resolution": "2K",  # Higher quality: 2K resolution
            "output_format": "png"
        }
    }

    print("\n[Step 1] Submitting to API...")
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
                    output_path = "test_output/optimized_storyboard.png"
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
    success = test_optimized_prompt()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - Check test_output/optimized_storyboard.png")
    else:
        print("❌ TEST FAILED")
    print("=" * 60)


if __name__ == "__main__":
    main()
