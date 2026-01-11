#!/usr/bin/env python3
"""
Storyboard-only test script.
Generates storyboard images only (no video) for quick iteration.

Usage:
    python scripts/storyboard_test.py --pokemon Charizard Dragonite --output-dir test_output
"""

import argparse
import subprocess
import json
import os
import time
from datetime import datetime
from PIL import Image

# Import our prompt validator
from prompt_validator import PromptValidator

class StoryboardTester:
    """Generate storyboards only for testing prompts."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.validator = PromptValidator()
        self.kie_api_key = os.environ.get("KIE_API_KEY", "")

        # Try to load from .env file
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        if key == "KIE_API_KEY":
                            self.kie_api_key = value

        os.makedirs(output_dir, exist_ok=True)

    def log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {msg}")

    def generate_storyboard(self, pokemon_names: list, environment: str = "volcanic") -> str:
        """Generate a single storyboard image."""

        # Generate prompt using our improved generator
        prompt, negative_prompt = self.validator.generate_holistic_storyboard_prompt(
            pokemon_names=pokemon_names,
            scene_type="battle",
            environment=environment,
            panel_count=4
        )

        self.log(f"Generated prompt ({len(prompt)} chars)")
        print("\n" + "="*60)
        print("PROMPT:")
        print("="*60)
        print(prompt)
        print("="*60 + "\n")

        # Save prompt for reference
        prompt_path = os.path.join(self.output_dir, "prompt.txt")
        with open(prompt_path, "w") as f:
            f.write(prompt)
            f.write("\n\n--- NEGATIVE PROMPT ---\n")
            f.write(negative_prompt)

        # Generate with Nano Banana Pro
        payload = {
            "model": "nano-banana-pro",
            "prompt": prompt,
            "negativePrompt": negative_prompt,
            "imageCount": 1,
            "imageAspect": "16:9"  # Wide format for 2x2 grid
        }

        self.log("Submitting to Nano Banana Pro API...")

        curl_cmd = [
            "curl", "-k", "-s", "-X", "POST",
            "https://api.kieai.erweima.ai/api/v1/generate",
            "-H", f"Authorization: Bearer {self.kie_api_key}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            self.log(f"API call failed: {result.stderr}", "ERROR")
            return None

        try:
            response = json.loads(result.stdout)
            task_id = response.get("data", {}).get("taskId")

            if not task_id:
                self.log(f"No task ID returned: {result.stdout[:200]}", "ERROR")
                return None

            self.log(f"Task submitted: {task_id}")

            # Wait for completion
            output_path = os.path.join(self.output_dir, "storyboard.jpg")

            for i in range(60):  # Max 5 minutes
                time.sleep(5)

                status_cmd = [
                    "curl", "-k", "-s",
                    f"https://api.kieai.erweima.ai/api/v1/recordInfo?taskId={task_id}",
                    "-H", f"Authorization: Bearer {self.kie_api_key}"
                ]

                status_result = subprocess.run(status_cmd, capture_output=True, text=True, timeout=30)
                status_json = json.loads(status_result.stdout)

                state = status_json.get("data", {}).get("state", "").lower()

                if state == "success":
                    result_json = status_json.get("data", {}).get("resultJson", "{}")
                    if isinstance(result_json, str):
                        result_json = json.loads(result_json)

                    urls = result_json.get("resultUrls", [])
                    if urls:
                        # Download
                        dl_cmd = ["curl", "-k", "-L", "-s", "-o", output_path, urls[0]]
                        subprocess.run(dl_cmd, timeout=60)

                        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                            self.log(f"Downloaded: {output_path}")
                            return output_path

                    self.log("No URLs in response", "ERROR")
                    return None

                elif state in ["failed", "error"]:
                    self.log(f"Generation failed: {status_json.get('data', {}).get('failMsg')}", "ERROR")
                    return None

                self.log(f"Waiting... ({i*5}s)")

            self.log("Timeout waiting for generation", "ERROR")
            return None

        except Exception as e:
            self.log(f"Error: {e}", "ERROR")
            return None

    def analyze_storyboard(self, image_path: str, pokemon_names: list):
        """Analyze generated storyboard for issues."""

        if not image_path or not os.path.exists(image_path):
            self.log("No image to analyze", "ERROR")
            return

        img = Image.open(image_path)
        width, height = img.size

        print("\n" + "="*60)
        print("STORYBOARD ANALYSIS")
        print("="*60)
        print(f"Size: {width}x{height}")
        print(f"Aspect ratio: {width/height:.2f} (target: 1.78 for 16:9)")

        # Extract individual panels
        panels_dir = os.path.join(self.output_dir, "panels")
        os.makedirs(panels_dir, exist_ok=True)

        # Calculate panel positions (2x2 grid)
        panel_w = width // 2
        panel_h = height // 2

        # Add margin to remove borders
        margin = int(min(panel_w, panel_h) * 0.04)  # 4% margin

        panels = []
        for i, (row, col) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
            x1 = col * panel_w + margin
            y1 = row * panel_h + margin
            x2 = (col + 1) * panel_w - margin
            y2 = (row + 1) * panel_h - margin

            panel = img.crop((x1, y1, x2, y2))
            panel_path = os.path.join(panels_dir, f"panel_{i+1}.jpg")
            panel.save(panel_path, "JPEG", quality=95)
            panels.append(panel_path)
            print(f"Panel {i+1}: {panel.size[0]}x{panel.size[1]} saved to {panel_path}")

        print("="*60)
        print(f"\nPanels extracted to: {panels_dir}")
        print("\nMANUAL REVIEW CHECKLIST:")
        print(f"  [ ] Panel 1: {pokemon_names[0]} on LEFT facing RIGHT?")
        print(f"  [ ] Panel 1: {pokemon_names[1]} on RIGHT facing LEFT?")
        print(f"  [ ] Panel 1: Visible attack beam from {pokemon_names[0]}?")
        print(f"  [ ] Panel 2: Both Pokemon facing each other?")
        print(f"  [ ] Panel 2: Impact visible on {pokemon_names[1]}?")
        print(f"  [ ] Panel 3: {pokemon_names[1]} showing burn marks/damage?")
        print(f"  [ ] Panel 3: Energy charging visible at {pokemon_names[1]}'s mouth?")
        print(f"  [ ] Panel 4: Damage continuity maintained?")
        print(f"  [ ] Panel 4: Attack beam from {pokemon_names[1]} visible?")
        print(f"  [ ] All panels: Photorealistic (not anime/cartoon)?")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Test storyboard generation")
    parser.add_argument("--pokemon", nargs=2, default=["Charizard", "Dragonite"],
                        help="Two Pokemon names")
    parser.add_argument("--output-dir", default="storyboard_test",
                        help="Output directory")
    parser.add_argument("--environment", default="volcanic",
                        help="Environment (volcanic, forest, ocean, etc.)")

    args = parser.parse_args()

    tester = StoryboardTester(args.output_dir)

    print("\n" + "="*60)
    print("STORYBOARD TEST - NO VIDEO GENERATION")
    print("="*60)
    print(f"Pokemon: {args.pokemon[0]} vs {args.pokemon[1]}")
    print(f"Environment: {args.environment}")
    print(f"Output: {args.output_dir}")
    print("="*60 + "\n")

    # Generate storyboard
    image_path = tester.generate_storyboard(args.pokemon, args.environment)

    if image_path:
        # Analyze results
        tester.analyze_storyboard(image_path, args.pokemon)
        print(f"\n SUCCESS: Storyboard saved to {image_path}")
        print("Review the image and panels before proceeding to video generation.\n")
    else:
        print("\n FAILED: Could not generate storyboard\n")


if __name__ == "__main__":
    main()
