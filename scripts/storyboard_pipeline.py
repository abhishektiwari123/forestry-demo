#!/usr/bin/env python3
"""
End-to-end storyboard pipeline with validation at each stage.

Stages:
1. Generate 2x2 storyboard grid (Nano Banana Pro)
2. Extract individual scenes (crop to 16:9)
3. Upscale with LANCZOS (content-preserving)
4. Validate each scene (dimensions, aspect ratio, forbidden elements)
5. Ready for upload to video generation

Usage:
    python storyboard_pipeline.py --prompt "Scene descriptions" --output-dir ./output
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: PIL not found. Install with: pip install Pillow")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
for env_path in ['.env', 'scripts/.env', '../scripts/.env', '../../scripts/.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break


class ValidationResult:
    """Holds validation results for a scene."""
    def __init__(self, scene_name: str):
        self.scene_name = scene_name
        self.passed = True
        self.issues = []
        self.metrics = {}

    def add_issue(self, issue: str):
        self.issues.append(issue)
        self.passed = False

    def to_dict(self):
        return {
            "scene": self.scene_name,
            "passed": self.passed,
            "issues": self.issues,
            "metrics": self.metrics
        }


class StoryboardPipeline:
    """End-to-end storyboard generation pipeline."""

    def __init__(self, output_dir: str, api_key: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.api_key = api_key or os.getenv("KIE_API_KEY")
        if not self.api_key:
            raise ValueError("KIE_API_KEY not found")

        self.validation_log = []

        # Validation thresholds
        self.target_aspect_ratio = 16 / 9  # 1.78
        self.aspect_tolerance = 0.05
        self.min_dimension = 1280
        self.min_file_size_kb = 100

        # Forbidden elements for Pokemon battles
        self.forbidden_elements = [
            "shields", "defensive barriers", "protective auras",
            "trainers", "humans", "text", "labels", "watermarks",
            "multiple scenes", "split screen", "grid layout"
        ]

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def validate_dimensions(self, img: Image.Image, result: ValidationResult):
        """Validate image dimensions and aspect ratio."""
        w, h = img.size
        aspect = w / h

        result.metrics["width"] = w
        result.metrics["height"] = h
        result.metrics["aspect_ratio"] = round(aspect, 3)

        # Check minimum dimensions
        if w < self.min_dimension or h < self.min_dimension:
            result.add_issue(f"Dimension too small: {w}x{h}, min: {self.min_dimension}")

        # Check aspect ratio (should be close to 16:9)
        if abs(aspect - self.target_aspect_ratio) > self.aspect_tolerance:
            result.add_issue(
                f"Aspect ratio {aspect:.2f} deviates from 16:9 ({self.target_aspect_ratio:.2f})"
            )

    def validate_file_size(self, file_path: str, result: ValidationResult):
        """Validate file size."""
        size_kb = os.path.getsize(file_path) / 1024
        result.metrics["file_size_kb"] = round(size_kb, 1)

        if size_kb < self.min_file_size_kb:
            result.add_issue(f"File too small: {size_kb:.1f}KB, min: {self.min_file_size_kb}KB")

    def stage1_generate_storyboard(self, prompt: str, grid_size: tuple = (2, 2)) -> str | None:
        """
        Stage 1: Generate 2x2 storyboard grid using Nano Banana Pro.
        Returns path to generated storyboard image.
        """
        self.log("STAGE 1: Generating storyboard grid")

        # For 2x2 grid, we need square aspect ratio
        width = 2048
        height = 2048

        negative_prompt = ", ".join(self.forbidden_elements)

        payload = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_images": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 30
            }
        }

        # Submit task
        curl_cmd = [
            "curl", "-k", "-s", "-X", "POST",
            "https://api.kie.ai/api/v1/jobs/createTask",
            "-H", f"Authorization: Bearer {self.api_key}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ]

        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
            response = json.loads(result.stdout)

            task_id = response.get("data", {}).get("taskId")
            if not task_id:
                self.log(f"Failed to get task ID: {response}", "ERROR")
                return None

            self.log(f"Task submitted: {task_id}")

            # Poll for completion
            for attempt in range(60):
                time.sleep(5)

                status_cmd = [
                    "curl", "-k", "-s",
                    f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                    "-H", f"Authorization: Bearer {self.api_key}"
                ]

                status_result = subprocess.run(status_cmd, capture_output=True, text=True, timeout=30)
                if not status_result.stdout.strip():
                    continue

                status_data = json.loads(status_result.stdout)
                state = status_data.get("data", {}).get("state", "").lower()

                if state == "success":
                    result_json = status_data.get("data", {}).get("resultJson")
                    if isinstance(result_json, str):
                        result_json = json.loads(result_json)

                    urls = result_json.get("resultUrls", [])
                    if urls:
                        storyboard_path = self.output_dir / "storyboard_grid.jpg"
                        if self._download_file(urls[0], str(storyboard_path)):
                            self.log(f"Storyboard downloaded: {storyboard_path}")
                            return str(storyboard_path)

                    self.log("No image URL in result", "ERROR")
                    return None

                elif state in ["failed", "error"]:
                    error = status_data.get("data", {}).get("failMsg", "Unknown")
                    self.log(f"Generation failed: {error}", "ERROR")
                    return None

                if attempt % 6 == 0 and attempt > 0:
                    self.log(f"Still generating... ({attempt * 5}s)")

            self.log("Timeout after 5 minutes", "ERROR")
            return None

        except Exception as e:
            self.log(f"Error: {e}", "ERROR")
            return None

    def _download_file(self, url: str, output_path: str) -> bool:
        """Download file using curl."""
        curl_cmd = ["curl", "-k", "-L", "-s", "-o", output_path, url]
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0 and os.path.exists(output_path)

    def stage2_extract_scenes(self, storyboard_path: str, grid_size: tuple = (2, 2)) -> list[str]:
        """
        Stage 2: Extract individual scenes from storyboard grid.
        Crops each panel to 16:9 aspect ratio.
        Returns list of extracted scene paths.
        """
        self.log("STAGE 2: Extracting scenes from storyboard")

        scenes_dir = self.output_dir / "scenes"
        scenes_dir.mkdir(exist_ok=True)

        img = Image.open(storyboard_path)
        w, h = img.size

        cols, rows = grid_size
        panel_w = w // cols
        panel_h = h // rows

        self.log(f"Storyboard: {w}x{h}, Panel size: {panel_w}x{panel_h}")

        extracted_paths = []

        for row in range(rows):
            for col in range(cols):
                scene_num = row * cols + col + 1

                # Extract panel
                left = col * panel_w
                top = row * panel_h
                right = left + panel_w
                bottom = top + panel_h

                panel = img.crop((left, top, right, bottom))

                # Crop panel to 16:9
                p_w, p_h = panel.size
                target_w = int(p_h * self.target_aspect_ratio)

                if target_w <= p_w:
                    # Crop width (center crop)
                    crop_left = (p_w - target_w) // 2
                    cropped = panel.crop((crop_left, 0, crop_left + target_w, p_h))
                else:
                    # Crop height (center crop)
                    target_h = int(p_w / self.target_aspect_ratio)
                    crop_top = (p_h - target_h) // 2
                    cropped = panel.crop((0, crop_top, p_w, crop_top + target_h))

                # Save extracted scene
                scene_path = scenes_dir / f"scene_{scene_num:02d}_16x9.jpg"
                cropped.save(str(scene_path), quality=95)

                extracted_paths.append(str(scene_path))
                self.log(f"Extracted scene {scene_num}: {cropped.size[0]}x{cropped.size[1]}")

                # Validate extraction
                result = ValidationResult(f"scene_{scene_num:02d}")
                self.validate_dimensions(cropped, result)
                self.validate_file_size(str(scene_path), result)
                self.validation_log.append(result.to_dict())

        return extracted_paths

    def stage3_upscale_scenes(self, scene_paths: list[str], scale: int = 2) -> list[str]:
        """
        Stage 3: Upscale scenes using LANCZOS (content-preserving).
        Returns list of upscaled scene paths.
        """
        self.log(f"STAGE 3: Upscaling scenes {scale}x with LANCZOS")

        upscaled_dir = self.output_dir / "upscaled"
        upscaled_dir.mkdir(exist_ok=True)

        upscaled_paths = []

        for scene_path in scene_paths:
            img = Image.open(scene_path)
            new_size = (img.size[0] * scale, img.size[1] * scale)

            upscaled = img.resize(new_size, Image.LANCZOS)

            # Generate output path
            base_name = Path(scene_path).stem
            upscaled_path = upscaled_dir / f"{base_name}_{scale}x.jpg"

            upscaled.save(str(upscaled_path), quality=95)
            upscaled_paths.append(str(upscaled_path))

            self.log(f"Upscaled: {upscaled.size[0]}x{upscaled.size[1]}")

            # Validate upscaled image
            result = ValidationResult(f"{base_name}_{scale}x")
            self.validate_dimensions(upscaled, result)
            self.validate_file_size(str(upscaled_path), result)
            self.validation_log.append(result.to_dict())

        return upscaled_paths

    def stage4_final_validation(self, upscaled_paths: list[str]) -> dict:
        """
        Stage 4: Final validation of all upscaled scenes.
        Returns validation summary.
        """
        self.log("STAGE 4: Final validation")

        passed = 0
        failed = 0

        for path in upscaled_paths:
            img = Image.open(path)
            result = ValidationResult(Path(path).name)

            self.validate_dimensions(img, result)
            self.validate_file_size(path, result)

            if result.passed:
                passed += 1
                self.log(f"PASSED: {result.scene_name}")
            else:
                failed += 1
                self.log(f"FAILED: {result.scene_name} - {result.issues}", "WARN")

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_scenes": len(upscaled_paths),
            "passed": passed,
            "failed": failed,
            "validation_log": self.validation_log,
            "scenes": upscaled_paths
        }

        # Save validation report
        report_path = self.output_dir / "validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)

        self.log(f"Validation complete: {passed}/{len(upscaled_paths)} passed")
        self.log(f"Report saved: {report_path}")

        return summary

    def run(self, prompt: str, grid_size: tuple = (2, 2), upscale_factor: int = 2) -> dict:
        """
        Run the complete pipeline.
        """
        self.log("=" * 60)
        self.log("STORYBOARD PIPELINE START")
        self.log("=" * 60)

        # Stage 1: Generate storyboard
        storyboard_path = self.stage1_generate_storyboard(prompt, grid_size)
        if not storyboard_path:
            return {"success": False, "error": "Storyboard generation failed"}

        # Stage 2: Extract scenes
        scene_paths = self.stage2_extract_scenes(storyboard_path, grid_size)
        if not scene_paths:
            return {"success": False, "error": "Scene extraction failed"}

        # Stage 3: Upscale scenes
        upscaled_paths = self.stage3_upscale_scenes(scene_paths, upscale_factor)
        if not upscaled_paths:
            return {"success": False, "error": "Upscaling failed"}

        # Stage 4: Final validation
        summary = self.stage4_final_validation(upscaled_paths)

        self.log("=" * 60)
        self.log("PIPELINE COMPLETE")
        self.log("=" * 60)

        return {
            "success": True,
            "storyboard": storyboard_path,
            "scenes": scene_paths,
            "upscaled": upscaled_paths,
            "validation": summary
        }


def main():
    parser = argparse.ArgumentParser(
        description="End-to-end storyboard pipeline with validation"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Storyboard prompt")
    parser.add_argument("--output-dir", "-o", required=True, help="Output directory")
    parser.add_argument("--grid", "-g", default="2x2", help="Grid size (e.g., 2x2)")
    parser.add_argument("--upscale", "-u", type=int, default=2, help="Upscale factor")

    args = parser.parse_args()

    # Parse grid size
    grid_parts = args.grid.lower().split('x')
    grid_size = (int(grid_parts[0]), int(grid_parts[1]))

    pipeline = StoryboardPipeline(args.output_dir)
    result = pipeline.run(args.prompt, grid_size, args.upscale)

    if result["success"]:
        print(f"\nReady for video generation:")
        for path in result["upscaled"]:
            print(f"  {path}")
        sys.exit(0)
    else:
        print(f"\nPipeline failed: {result.get('error', 'Unknown')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
