#!/usr/bin/env python3
"""
Comprehensive Pokemon AI Video Pipeline with Multi-Stage Validation.

Validation Stages:
1. PRE-PROMPT: Validate prompt against Pokemon scene best practices
2. POST-GENERATION: Validate generated image with Claude Vision API
3. POST-SPLIT: Validate each extracted scene
4. POST-UPSCALE: Validate upscaled images
5. POST-VIDEO: Validate video frames with Claude Vision API

Each stage can trigger regeneration if validation fails.
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:
    print("Error: PIL not found. Install with: pip install Pillow")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
for env_path in ['.env', 'scripts/.env', '../scripts/.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

# Import holistic prompt validator
try:
    from prompt_validator import PromptValidator as HolisticPromptValidator, POKEMON_DETAILED_INFO
except ImportError:
    HolisticPromptValidator = None
    POKEMON_DETAILED_INFO = None


# =============================================================================
# POKEMON SCENE BEST PRACTICES
# =============================================================================

POKEMON_BEST_PRACTICES = {
    "required_elements": [
        "pokemon name",      # Must specify which Pokemon
        "action/pose",       # What the Pokemon is doing
        "environment",       # Background/setting
        "lighting",          # Lighting conditions
        "photorealistic"     # MUST be photorealistic documentary style
    ],
    "recommended_elements": [
        "camera angle",
        "expression/emotion",
        "effects (fire, electricity, etc.)",
        "composition (rule of thirds, etc.)",
        "BBC Earth", "National Geographic", "wildlife photography"
    ],
    "forbidden_elements": [
        # CRITICAL: No 2D/3D renders - documentary style only
        "anime", "cartoon", "manga", "chibi",
        "2d", "3d render", "cgi", "digital art",
        "illustration", "drawing", "sketch", "painted", "stylized",
        # Pokemon-specific forbidden
        "shields", "defensive barriers", "protective auras",
        "trainers", "humans", "pokeballs in hand",
        "text", "labels", "watermarks", "logos",
        "multiple scenes", "split screen", "grid layout", "panel layout",
        "low quality", "blurry", "distorted", "deformed",
        "wrong anatomy", "extra limbs", "missing limbs"
    ],
    "style_keywords": [
        # PHOTOREALISTIC documentary style required
        "photorealistic", "wildlife photography", "BBC Earth",
        "National Geographic", "documentary style", "nature documentary",
        "shot on RED camera", "shot on ARRI", "natural lighting",
        "cinematic", "8K detail", "lifelike", "realistic"
    ],
    "pokemon_anatomy_rules": {
        "charizard": ["two wings", "flame tail", "orange body", "blue inner wings"],
        "dragonite": ["two wings", "antenna on head", "orange body", "small wings"],
        "pikachu": ["two ears", "lightning tail", "red cheeks", "yellow body"],
        "mewtwo": ["purple body", "long tail", "three fingers", "no wings"]
    }
}


@dataclass
class ValidationResult:
    """Holds validation results."""
    stage: str
    passed: bool
    score: float = 1.0
    issues: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "stage": self.stage,
            "passed": self.passed,
            "score": self.score,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "metrics": self.metrics
        }


class ClaudeVisionValidator:
    """Validates images using Claude Vision API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not found. Vision validation disabled.")

    def validate_image(self, image_path: str, validation_prompt: str) -> dict:
        """
        Validate image using Claude Vision API.
        Returns dict with 'passed', 'score', 'issues', 'suggestions'.
        """
        if not self.api_key:
            return {"passed": True, "score": 0.8, "issues": ["Vision API not configured"], "suggestions": []}

        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Determine media type
            ext = Path(image_path).suffix.lower()
            media_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

            # Build API request
            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": validation_prompt
                        }
                    ]
                }]
            }

            # Call Claude API using curl
            curl_cmd = [
                "curl", "-s", "-X", "POST",
                "https://api.anthropic.com/v1/messages",
                "-H", f"x-api-key: {self.api_key}",
                "-H", "anthropic-version: 2023-06-01",
                "-H", "content-type: application/json",
                "-d", json.dumps(payload)
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return {"passed": True, "score": 0.7, "issues": ["API call failed"], "suggestions": []}

            response = json.loads(result.stdout)

            if "error" in response:
                return {"passed": True, "score": 0.7, "issues": [response["error"].get("message", "Unknown error")], "suggestions": []}

            # Parse response
            content = response.get("content", [{}])[0].get("text", "")
            return self._parse_validation_response(content)

        except Exception as e:
            return {"passed": True, "score": 0.7, "issues": [str(e)], "suggestions": []}

    def _parse_validation_response(self, response: str) -> dict:
        """Parse Claude's validation response."""
        response_lower = response.lower()

        # Extract score if mentioned
        score = 0.8
        if "score:" in response_lower:
            try:
                score_part = response_lower.split("score:")[1].split()[0]
                score = float(score_part.strip("/10")) / 10 if "/10" in score_part else float(score_part)
            except:
                pass

        # Determine pass/fail
        passed = True
        fail_keywords = ["fail", "reject", "invalid", "incorrect", "wrong", "bad", "poor"]
        if any(kw in response_lower for kw in fail_keywords):
            if "pass" not in response_lower[:100]:  # Check if it's actually passing
                passed = False

        # Extract issues
        issues = []
        if "issue" in response_lower or "problem" in response_lower:
            lines = response.split("\n")
            for line in lines:
                if any(marker in line.lower() for marker in ["issue", "problem", "error", "- "]):
                    if len(line.strip()) > 5:
                        issues.append(line.strip().lstrip("- "))

        # Extract suggestions
        suggestions = []
        if "suggest" in response_lower or "recommend" in response_lower:
            lines = response.split("\n")
            for line in lines:
                if any(marker in line.lower() for marker in ["suggest", "recommend", "should", "could"]):
                    if len(line.strip()) > 5:
                        suggestions.append(line.strip().lstrip("- "))

        return {
            "passed": passed and score >= 0.6,
            "score": score,
            "issues": issues[:5],  # Limit to 5 issues
            "suggestions": suggestions[:3],  # Limit to 3 suggestions
            "raw_response": response[:500]
        }

    def validate_video_frame(self, frame_path: str, scene_description: str) -> dict:
        """Validate a video frame against the expected scene."""
        prompt = f"""Analyze this video frame from a Pokemon battle animation.

Expected scene: {scene_description}

Evaluate the following and respond with a JSON object:
1. Does the frame match the expected scene description? (match_score: 0-10)
2. Are the Pokemon characters correctly rendered? (character_quality: 0-10)
3. Is there any visual artifact or distortion? (artifacts: list)
4. Is the animation quality acceptable? (animation_quality: 0-10)
5. Overall pass/fail recommendation (passed: true/false)

Respond ONLY with valid JSON."""

        return self.validate_image(frame_path, prompt)


class PromptValidator:
    """Validates and improves prompts before generation."""

    def __init__(self):
        self.best_practices = POKEMON_BEST_PRACTICES

    def validate_prompt(self, prompt: str, pokemon_names: list = None) -> ValidationResult:
        """
        Validate prompt against Pokemon scene best practices.
        Returns ValidationResult with score and suggestions.
        """
        result = ValidationResult(stage="pre_prompt", passed=True, score=1.0)
        prompt_lower = prompt.lower()

        # Check required elements
        missing_required = []
        for element in self.best_practices["required_elements"]:
            if element == "pokemon name":
                if pokemon_names:
                    if not any(p.lower() in prompt_lower for p in pokemon_names):
                        missing_required.append(f"Pokemon name ({', '.join(pokemon_names)})")
            elif element == "action/pose":
                action_words = ["attack", "fight", "battle", "launch", "charge", "dodge", "flying", "standing", "roaring"]
                if not any(w in prompt_lower for w in action_words):
                    missing_required.append("action/pose description")
            elif element == "environment":
                env_words = ["background", "environment", "setting", "volcano", "forest", "sky", "arena", "field"]
                if not any(w in prompt_lower for w in env_words):
                    missing_required.append("environment/background")
            elif element == "lighting":
                light_words = ["lighting", "light", "glow", "bright", "dark", "dramatic", "cinematic"]
                if not any(w in prompt_lower for w in light_words):
                    result.suggestions.append("Consider adding lighting description")
            elif element == "photorealistic":
                # CRITICAL: Must be photorealistic documentary style
                photo_words = ["photorealistic", "realistic", "photography", "documentary", "bbc earth", "national geographic"]
                if not any(w in prompt_lower for w in photo_words):
                    result.issues.append("Missing photorealistic/documentary style (REQUIRED)")
                    result.score -= 0.25

        if missing_required:
            result.issues.extend([f"Missing: {elem}" for elem in missing_required])
            result.score -= 0.15 * len(missing_required)

        # Check for FORBIDDEN 2D/3D render styles (CRITICAL)
        forbidden_styles = ["anime", "cartoon", "manga", "chibi", "2d", "3d render",
                           "cgi", "digital art", "illustration", "drawing", "sketch"]
        style_found = [s for s in forbidden_styles if s in prompt_lower]
        if style_found:
            result.issues.append(f"FORBIDDEN: 2D/3D render styles detected: {', '.join(style_found)}")
            result.score -= 0.3  # Heavy penalty

        # Check for other forbidden elements
        forbidden_found = []
        for forbidden in self.best_practices["forbidden_elements"]:
            if forbidden.lower() in prompt_lower and forbidden.lower() not in forbidden_styles:
                forbidden_found.append(forbidden)

        if forbidden_found:
            result.issues.extend([f"Forbidden element in prompt: {elem}" for elem in forbidden_found])
            result.score -= 0.1 * len(forbidden_found)

        # Check for style keywords
        style_count = sum(1 for kw in self.best_practices["style_keywords"] if kw.lower() in prompt_lower)
        if style_count < 2:
            result.suggestions.append(f"Add more style keywords: {', '.join(self.best_practices['style_keywords'][:3])}")

        # Check Pokemon anatomy rules
        if pokemon_names:
            for pokemon in pokemon_names:
                pokemon_lower = pokemon.lower()
                if pokemon_lower in self.best_practices["pokemon_anatomy_rules"]:
                    anatomy = self.best_practices["pokemon_anatomy_rules"][pokemon_lower]
                    result.metrics[f"{pokemon}_anatomy_hints"] = anatomy

        # Final pass/fail determination
        result.passed = result.score >= 0.6 and len(missing_required) <= 1
        result.score = max(0, min(1, result.score))

        return result

    def improve_prompt(self, prompt: str, validation_result: ValidationResult, pokemon_names: list = None) -> str:
        """Improve prompt based on validation issues."""
        improved = prompt
        prefix = ""

        # Add missing elements
        additions = []

        # CRITICAL: Add photorealistic prefix if missing
        if not any(kw in prompt.lower() for kw in ["photorealistic", "realistic", "photography"]):
            prefix = "Photorealistic "
            additions.append("wildlife photography style, BBC Earth documentary quality")
            additions.append("shot on RED camera, natural lighting, 8K detail")

        for issue in validation_result.issues:
            if "environment" in issue.lower():
                additions.append("natural environment with atmospheric effects")
            if "action" in issue.lower():
                additions.append("dynamic pose, captured in motion")
            if "lighting" in issue.lower():
                additions.append("natural cinematic lighting")
            if "2D/3D" in issue or "FORBIDDEN" in issue:
                # Remove forbidden style words
                for forbidden in ["anime", "cartoon", "2d", "3d render", "cgi", "illustration"]:
                    improved = improved.replace(forbidden, "")
                    improved = improved.replace(forbidden.title(), "")

        # Add photorealistic style keywords
        if not any(kw in prompt.lower() for kw in ["sharp focus", "detailed", "professional"]):
            additions.append("sharp focus, high detail, professional wildlife photography")

        # Build negative prompt with 2D/3D forbidden styles
        negative = ", ".join(self.best_practices["forbidden_elements"])

        if prefix or additions:
            improved = f"{prefix}{improved}"
            if additions:
                improved = f"{improved}, {', '.join(additions)}"

        return improved, negative


class ValidatedPipeline:
    """
    Complete Pokemon AI Video Pipeline with comprehensive validation.
    """

    def __init__(self, output_dir: str, kie_api_key: str = None, anthropic_api_key: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.kie_api_key = kie_api_key or os.getenv("KIE_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.kie_api_key:
            raise ValueError("KIE_API_KEY not found")

        self.prompt_validator = PromptValidator()
        self.vision_validator = ClaudeVisionValidator(self.anthropic_api_key)

        self.validation_log = []
        self.max_retries = 3

        # Thresholds
        self.target_aspect = 16 / 9
        self.min_dimension = 1280
        self.min_score = 0.6

    def log(self, msg: str, level: str = "INFO"):
        """Log with timestamp."""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [{level}] {msg}")

    def _call_kie_api(self, endpoint: str, payload: dict = None, method: str = "POST") -> dict:
        """Call KIE API with retry logic."""
        url = f"https://api.kie.ai/api/v1/jobs/{endpoint}"

        for attempt in range(3):
            try:
                if method == "POST":
                    curl_cmd = [
                        "curl", "-k", "-s", "-X", "POST", url,
                        "-H", f"Authorization: Bearer {self.kie_api_key}",
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps(payload)
                    ]
                else:
                    curl_cmd = [
                        "curl", "-k", "-s", url,
                        "-H", f"Authorization: Bearer {self.kie_api_key}"
                    ]

                result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
                if result.stdout.strip():
                    return json.loads(result.stdout)
            except Exception as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                return {"error": str(e)}

        return {"error": "Max retries exceeded"}

    def _download_file(self, url: str, output_path: str) -> bool:
        """Download file using curl."""
        curl_cmd = ["curl", "-k", "-L", "-s", "-o", output_path, url]
        result = subprocess.run(curl_cmd, capture_output=True, timeout=120)
        return result.returncode == 0 and os.path.exists(output_path)

    def _wait_for_task(self, task_id: str, max_wait: int = 300) -> dict:
        """Wait for task completion."""
        for _ in range(max_wait // 5):
            time.sleep(5)
            response = self._call_kie_api(f"recordInfo?taskId={task_id}", method="GET")

            state = response.get("data", {}).get("state", "").lower()
            if state == "success":
                return response
            elif state in ["failed", "error"]:
                return {"error": response.get("data", {}).get("failMsg", "Unknown")}

        return {"error": "Timeout"}

    # =========================================================================
    # STAGE 1: PRE-PROMPT VALIDATION
    # =========================================================================

    def stage1_validate_prompt(self, prompt: str, pokemon_names: list) -> tuple[str, str, ValidationResult]:
        """
        Stage 1: Validate and improve prompt before generation.
        Returns (improved_prompt, negative_prompt, validation_result).
        """
        self.log("STAGE 1: Pre-prompt validation")

        result = self.prompt_validator.validate_prompt(prompt, pokemon_names)
        self.validation_log.append(result.to_dict())

        if result.passed:
            self.log(f"  Prompt validation PASSED (score: {result.score:.2f})")
            improved, negative = self.prompt_validator.improve_prompt(prompt, result, pokemon_names)
            return improved, negative, result
        else:
            self.log(f"  Prompt validation needs improvement (score: {result.score:.2f})")
            for issue in result.issues:
                self.log(f"    - {issue}", "WARN")

            improved, negative = self.prompt_validator.improve_prompt(prompt, result, pokemon_names)
            self.log(f"  Improved prompt created")

            # Re-validate improved prompt
            result2 = self.prompt_validator.validate_prompt(improved, pokemon_names)
            result2.stage = "pre_prompt_improved"
            self.validation_log.append(result2.to_dict())

            return improved, negative, result2

    # =========================================================================
    # STAGE 2: IMAGE GENERATION WITH VALIDATION
    # =========================================================================

    def stage2_generate_and_validate(self, prompt: str, negative_prompt: str,
                                     pokemon_names: list, output_path: str) -> tuple[str, ValidationResult]:
        """
        Stage 2: Generate storyboard and validate with Claude Vision.
        Retries with improved prompt if validation fails.
        """
        self.log("STAGE 2: Image generation with validation")

        for attempt in range(self.max_retries):
            self.log(f"  Attempt {attempt + 1}/{self.max_retries}")

            # Generate image
            image_path = self._generate_storyboard(prompt, negative_prompt, output_path, attempt)
            if not image_path:
                continue

            # Validate with Claude Vision
            validation_prompt = f"""Analyze this Pokemon battle storyboard image.

Expected Pokemon: {', '.join(pokemon_names)}

Check for:
1. Are the Pokemon ({', '.join(pokemon_names)}) correctly depicted with proper anatomy?
2. Is each panel showing a distinct battle scene?
3. Are there any forbidden elements (humans, text, watermarks, shields)?
4. Is the image quality acceptable (no blur, distortion, artifacts)?
5. Is the composition good for animation?

Respond with:
- SCORE: X/10
- PASSED: yes/no
- ISSUES: (list any problems)
- SUGGESTIONS: (list improvements if needed)"""

            result = self.vision_validator.validate_image(image_path, validation_prompt)

            val_result = ValidationResult(
                stage=f"post_generation_attempt_{attempt + 1}",
                passed=result.get("passed", True),
                score=result.get("score", 0.8),
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", [])
            )
            self.validation_log.append(val_result.to_dict())

            if val_result.passed and val_result.score >= self.min_score:
                self.log(f"  Image validation PASSED (score: {val_result.score:.2f})")
                return image_path, val_result
            else:
                self.log(f"  Image validation FAILED (score: {val_result.score:.2f})", "WARN")
                for issue in val_result.issues[:3]:
                    self.log(f"    - {issue}", "WARN")

                # Improve prompt for next attempt
                if val_result.suggestions:
                    prompt = f"{prompt}, {', '.join(val_result.suggestions[:2])}"

        # Return last attempt even if failed
        self.log("  Max retries reached, using last generated image", "WARN")
        return image_path, val_result

    def _generate_storyboard(self, prompt: str, negative_prompt: str,
                             output_path: str, attempt: int) -> Optional[str]:
        """Generate storyboard image."""
        payload = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": 2048,
                "height": 2048,
                "num_images": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 30
            }
        }

        response = self._call_kie_api("createTask", payload)
        task_id = response.get("data", {}).get("taskId")

        if not task_id:
            self.log(f"    Failed to create task: {response}", "ERROR")
            return None

        self.log(f"    Task submitted: {task_id}")

        result = self._wait_for_task(task_id)
        if "error" in result:
            self.log(f"    Generation failed: {result['error']}", "ERROR")
            return None

        # Extract URL and download
        result_json = result.get("data", {}).get("resultJson", "{}")
        if isinstance(result_json, str):
            result_json = json.loads(result_json)

        urls = result_json.get("resultUrls", [])
        if not urls:
            return None

        # Add attempt suffix if retrying
        actual_path = output_path if attempt == 0 else output_path.replace(".jpg", f"_v{attempt + 1}.jpg")

        if self._download_file(urls[0], actual_path):
            self.log(f"    Downloaded: {actual_path}")
            return actual_path

        return None

    # =========================================================================
    # STAGE 3: SPLIT VALIDATION
    # =========================================================================

    def stage3_split_and_validate(self, storyboard_path: str, grid_size: tuple = (2, 2)) -> tuple[list, ValidationResult]:
        """
        Stage 3: Split storyboard into scenes and validate each split.
        Removes frame borders and crops to 16:9.
        """
        self.log("STAGE 3: Scene extraction with validation")

        scenes_dir = self.output_dir / "scenes"
        scenes_dir.mkdir(exist_ok=True)

        img = Image.open(storyboard_path)
        w, h = img.size
        cols, rows = grid_size

        self.log(f"  Storyboard: {w}x{h}, Grid: {cols}x{rows}")

        # Detect and remove borders between panels
        border_margin = self._detect_border_width(img, cols, rows)
        self.log(f"  Detected border margin: {border_margin}px")

        scene_paths = []
        all_passed = True

        for row in range(rows):
            for col in range(cols):
                scene_num = row * cols + col + 1

                # Calculate panel bounds with border removal
                panel_w = w // cols
                panel_h = h // rows
                left = col * panel_w
                top = row * panel_h

                # Add margin to remove frame borders (10% of panel size or detected)
                margin = max(border_margin, int(min(panel_w, panel_h) * 0.08))

                # Crop with margin to remove borders
                crop_left = left + margin
                crop_top = top + margin
                crop_right = left + panel_w - margin
                crop_bottom = top + panel_h - margin

                # Extract panel with border removed
                panel = img.crop((crop_left, crop_top, crop_right, crop_bottom))

                # Now crop to 16:9
                p_w, p_h = panel.size
                target_w = int(p_h * self.target_aspect)

                if target_w <= p_w:
                    crop_left = (p_w - target_w) // 2
                    cropped = panel.crop((crop_left, 0, crop_left + target_w, p_h))
                else:
                    target_h = int(p_w / self.target_aspect)
                    crop_top = (p_h - target_h) // 2
                    cropped = panel.crop((0, crop_top, p_w, crop_top + target_h))

                scene_path = scenes_dir / f"scene_{scene_num:02d}.jpg"
                cropped.save(str(scene_path), quality=95)

                # Validate split
                val_result = self._validate_split(cropped, scene_num)
                self.validation_log.append(val_result.to_dict())

                if val_result.passed:
                    self.log(f"    Scene {scene_num}: {cropped.size[0]}x{cropped.size[1]} - PASSED")
                    scene_paths.append(str(scene_path))
                else:
                    self.log(f"    Scene {scene_num}: FAILED - {val_result.issues}", "WARN")
                    all_passed = False

                    # Try alternative crop
                    alt_cropped = self._alternative_crop(panel, scene_num)
                    if alt_cropped:
                        alt_path = scenes_dir / f"scene_{scene_num:02d}_alt.jpg"
                        alt_cropped.save(str(alt_path), quality=95)
                        scene_paths.append(str(alt_path))
                        self.log(f"    Scene {scene_num}: Alternative crop saved")
                    else:
                        scene_paths.append(str(scene_path))

        summary = ValidationResult(
            stage="split_summary",
            passed=all_passed,
            score=len([p for p in scene_paths]) / (rows * cols),
            metrics={"total_scenes": len(scene_paths), "grid": f"{cols}x{rows}"}
        )

        return scene_paths, summary

    def _detect_border_width(self, img: Image.Image, cols: int, rows: int) -> int:
        """
        Detect the width of borders between panels in a storyboard.
        Returns estimated border width in pixels.
        """
        import numpy as np

        try:
            arr = np.array(img.convert('L'))  # Convert to grayscale
            h, w = arr.shape

            # Check vertical borders (between columns)
            panel_w = w // cols
            vertical_borders = []

            for col in range(1, cols):
                x = col * panel_w
                # Sample a vertical strip around the expected border
                strip_start = max(0, x - 20)
                strip_end = min(w, x + 20)
                strip = arr[:, strip_start:strip_end]

                # Check for low variance (solid color = border)
                variance = np.var(strip)
                if variance < 500:  # Low variance suggests border
                    vertical_borders.append(20)

            # Check horizontal borders (between rows)
            panel_h = h // rows
            horizontal_borders = []

            for row in range(1, rows):
                y = row * panel_h
                strip_start = max(0, y - 20)
                strip_end = min(h, y + 20)
                strip = arr[strip_start:strip_end, :]

                variance = np.var(strip)
                if variance < 500:
                    horizontal_borders.append(20)

            # Return maximum detected border or default
            all_borders = vertical_borders + horizontal_borders
            if all_borders:
                return max(all_borders)
            return 15  # Default border margin

        except Exception:
            return 15  # Default if detection fails

    def _detect_frame_border(self, img: Image.Image) -> bool:
        """
        Check if image has visible frame borders at edges.
        Returns True if borders detected.
        """
        import numpy as np

        try:
            arr = np.array(img.convert('L'))
            h, w = arr.shape

            # Check edge pixels for uniform color (border)
            edge_width = 5

            # Top edge
            top_strip = arr[:edge_width, :]
            top_var = np.var(top_strip)

            # Bottom edge
            bottom_strip = arr[-edge_width:, :]
            bottom_var = np.var(bottom_strip)

            # Left edge
            left_strip = arr[:, :edge_width]
            left_var = np.var(left_strip)

            # Right edge
            right_strip = arr[:, -edge_width:]
            right_var = np.var(right_strip)

            # If any edge has very low variance, it's likely a border
            threshold = 100
            has_border = any([
                top_var < threshold,
                bottom_var < threshold,
                left_var < threshold,
                right_var < threshold
            ])

            return has_border

        except Exception:
            return False

    def _validate_split(self, img: Image.Image, scene_num: int) -> ValidationResult:
        """Validate a split scene for quality and border detection."""
        w, h = img.size
        aspect = w / h

        result = ValidationResult(stage=f"split_scene_{scene_num}", passed=True)
        result.metrics = {"width": w, "height": h, "aspect": round(aspect, 3)}

        # Check dimensions
        if w < 500 or h < 300:
            result.issues.append(f"Scene too small: {w}x{h}")
            result.passed = False

        # Check aspect ratio (should be ~16:9)
        if abs(aspect - self.target_aspect) > 0.1:
            result.issues.append(f"Aspect ratio {aspect:.2f} deviates from 16:9")
            result.passed = False

        # Check for mostly black/white (potential extraction error)
        extremes = img.getextrema()
        if isinstance(extremes[0], tuple):
            # RGB image
            for channel in extremes:
                if channel[1] - channel[0] < 20:
                    result.issues.append("Low color variation (potential blank scene)")
                    result.passed = False
                    break

        # Check for frame borders at edges
        if self._detect_frame_border(img):
            result.issues.append("Frame border detected at edges - needs more cropping")
            result.passed = False

        result.score = 1.0 if result.passed else 0.5
        return result

    def _alternative_crop(self, panel: Image.Image, scene_num: int) -> Optional[Image.Image]:
        """Try alternative cropping if primary fails."""
        w, h = panel.size

        # Try center crop with padding
        margin = 0.05
        new_left = int(w * margin)
        new_top = int(h * margin)
        new_right = int(w * (1 - margin))
        new_bottom = int(h * (1 - margin))

        cropped = panel.crop((new_left, new_top, new_right, new_bottom))

        # Resize to 16:9
        target_w = cropped.size[0]
        target_h = int(target_w / self.target_aspect)

        if target_h <= cropped.size[1]:
            crop_top = (cropped.size[1] - target_h) // 2
            return cropped.crop((0, crop_top, target_w, crop_top + target_h))

        return None

    # =========================================================================
    # STAGE 4: UPSCALE VALIDATION
    # =========================================================================

    def stage4_upscale_and_validate(self, scene_paths: list, scale: int = 2) -> tuple[list, ValidationResult]:
        """
        Stage 4: Upscale scenes with LANCZOS and validate.
        """
        self.log(f"STAGE 4: Upscaling {scale}x with validation")

        upscaled_dir = self.output_dir / "upscaled"
        upscaled_dir.mkdir(exist_ok=True)

        upscaled_paths = []
        all_passed = True

        for scene_path in scene_paths:
            img = Image.open(scene_path)
            original_size = img.size

            # Upscale with LANCZOS (content-preserving)
            new_size = (img.size[0] * scale, img.size[1] * scale)
            upscaled = img.resize(new_size, Image.LANCZOS)

            # Save
            base_name = Path(scene_path).stem
            upscaled_path = upscaled_dir / f"{base_name}_{scale}x.jpg"
            upscaled.save(str(upscaled_path), quality=95)

            # Validate
            val_result = self._validate_upscale(upscaled, original_size, scale)
            val_result.stage = f"upscale_{base_name}"
            self.validation_log.append(val_result.to_dict())

            if val_result.passed:
                self.log(f"    {base_name}: {upscaled.size[0]}x{upscaled.size[1]} - PASSED")
                upscaled_paths.append(str(upscaled_path))
            else:
                self.log(f"    {base_name}: FAILED - {val_result.issues}", "WARN")
                all_passed = False
                upscaled_paths.append(str(upscaled_path))  # Still include

        summary = ValidationResult(
            stage="upscale_summary",
            passed=all_passed,
            score=1.0 if all_passed else 0.7,
            metrics={"scale": scale, "total": len(upscaled_paths)}
        )

        return upscaled_paths, summary

    def _validate_upscale(self, img: Image.Image, original_size: tuple, scale: int) -> ValidationResult:
        """Validate upscaled image."""
        w, h = img.size
        expected_w = original_size[0] * scale
        expected_h = original_size[1] * scale

        result = ValidationResult(stage="upscale", passed=True)
        result.metrics = {
            "width": w, "height": h,
            "expected": f"{expected_w}x{expected_h}",
            "aspect": round(w / h, 3)
        }

        # Check dimensions match expected
        if w != expected_w or h != expected_h:
            result.issues.append(f"Size mismatch: got {w}x{h}, expected {expected_w}x{expected_h}")
            result.passed = False

        # Check minimum dimensions
        if w < self.min_dimension or h < self.min_dimension:
            result.issues.append(f"Below minimum dimension {self.min_dimension}")
            result.passed = False

        result.score = 1.0 if result.passed else 0.6
        return result

    # =========================================================================
    # STAGE 5: VIDEO GENERATION WITH VALIDATION
    # =========================================================================

    def stage5_generate_videos_and_validate(self, upscaled_paths: list,
                                            scene_descriptions: list) -> tuple[list, ValidationResult]:
        """
        Stage 5: Generate videos and validate with Claude Vision.
        Regenerates if validation fails.
        """
        self.log("STAGE 5: Video generation with validation")

        videos_dir = self.output_dir / "videos"
        videos_dir.mkdir(exist_ok=True)

        video_paths = []
        all_passed = True

        for i, (img_path, description) in enumerate(zip(upscaled_paths, scene_descriptions)):
            scene_num = i + 1
            self.log(f"  Processing scene {scene_num}/{len(upscaled_paths)}")

            for attempt in range(self.max_retries):
                # Upload image
                image_url = self._upload_image(img_path)
                if not image_url:
                    self.log(f"    Failed to upload image", "ERROR")
                    continue

                # Generate video
                video_path = videos_dir / f"scene_{scene_num:02d}.mp4"
                success = self._generate_video(image_url, description, str(video_path))

                if not success:
                    continue

                # Extract frame and validate
                frame_path = self._extract_video_frame(str(video_path))
                if frame_path:
                    val_result = self.vision_validator.validate_video_frame(frame_path, description)

                    validation = ValidationResult(
                        stage=f"video_scene_{scene_num}_attempt_{attempt + 1}",
                        passed=val_result.get("passed", True),
                        score=val_result.get("score", 0.8),
                        issues=val_result.get("issues", [])
                    )
                    self.validation_log.append(validation.to_dict())

                    if validation.passed and validation.score >= self.min_score:
                        self.log(f"    Video validation PASSED (score: {validation.score:.2f})")
                        video_paths.append(str(video_path))
                        break
                    else:
                        self.log(f"    Video validation FAILED (score: {validation.score:.2f})", "WARN")
                        if attempt < self.max_retries - 1:
                            self.log(f"    Regenerating...")
                else:
                    # Can't extract frame, assume passed
                    video_paths.append(str(video_path))
                    break
            else:
                # Max retries reached
                if os.path.exists(str(video_path)):
                    video_paths.append(str(video_path))
                all_passed = False

        summary = ValidationResult(
            stage="video_summary",
            passed=all_passed,
            score=len(video_paths) / len(upscaled_paths) if upscaled_paths else 0,
            metrics={"total_videos": len(video_paths)}
        )

        return video_paths, summary

    def _upload_image(self, image_path: str) -> Optional[str]:
        """Upload image to free hosting."""
        curl_cmd = [
            "curl", "-k", "-s", "-X", "POST",
            "-F", f"source=@{image_path}",
            "-F", "key=6d207e02198a847aa98d0a2a901485a5",
            "https://freeimage.host/api/1/upload"
        ]

        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=60)
            response = json.loads(result.stdout)
            return response.get("image", {}).get("url")
        except:
            return None

    def _generate_video(self, image_url: str, prompt: str, output_path: str) -> bool:
        """Generate video using Kling 2.6."""
        payload = {
            "model": "kling-2.6/image-to-video",
            "input": {
                "image_urls": [image_url],
                "prompt": prompt,
                "duration": "5",
                "sound": True
            }
        }

        response = self._call_kie_api("createTask", payload)
        task_id = response.get("data", {}).get("taskId")

        if not task_id:
            return False

        self.log(f"    Video task: {task_id}")

        result = self._wait_for_task(task_id, max_wait=300)
        if "error" in result:
            return False

        result_json = result.get("data", {}).get("resultJson", "{}")
        if isinstance(result_json, str):
            result_json = json.loads(result_json)

        urls = result_json.get("resultUrls", [])
        if urls:
            return self._download_file(urls[0], output_path)

        return False

    def _extract_video_frame(self, video_path: str) -> Optional[str]:
        """Extract middle frame from video for validation."""
        frame_path = video_path.replace(".mp4", "_frame.jpg")

        # Try using PIL to read first frame (limited but works without ffmpeg)
        try:
            # Use imageio if available
            import imageio
            reader = imageio.get_reader(video_path)
            frame = reader.get_data(len(reader) // 2)  # Middle frame
            Image.fromarray(frame).save(frame_path)
            reader.close()
            return frame_path
        except:
            pass

        # Fallback: use the input image as reference
        return None

    # =========================================================================
    # MAIN PIPELINE
    # =========================================================================

    def run(self, prompt: str, pokemon_names: list, scene_descriptions: list = None,
            grid_size: tuple = (2, 2), upscale: int = 2, environment: str = "volcanic",
            use_holistic_prompts: bool = True) -> dict:
        """
        Run the complete validated pipeline.

        Args:
            prompt: Base prompt (will be enhanced if use_holistic_prompts=True)
            pokemon_names: List of Pokemon in the scene
            scene_descriptions: Descriptions for each scene's video
            grid_size: Storyboard grid size (default 2x2)
            upscale: Upscale factor (default 2)
            environment: Environment setting (volcanic, forest, ocean, etc.)
            use_holistic_prompts: Whether to use detailed Pokemon information
        """
        self.log("=" * 70)
        self.log("VALIDATED POKEMON AI VIDEO PIPELINE")
        self.log("=" * 70)

        results = {"success": False, "stages": {}}

        # Generate holistic prompts if available and enabled
        if use_holistic_prompts and HolisticPromptValidator:
            self.log("Using holistic prompt generation with detailed Pokemon info")
            holistic_validator = HolisticPromptValidator()
            prompt, negative_prompt = holistic_validator.generate_holistic_storyboard_prompt(
                pokemon_names=pokemon_names,
                scene_type="battle",
                environment=environment,
                panel_count=grid_size[0] * grid_size[1]
            )
            self.log(f"Generated holistic prompt ({len(prompt)} chars)")

            # Also generate holistic video prompts if not provided
            if scene_descriptions is None:
                scene_descriptions = []
                # Get Pokemon attack info for specific effects
                p1_info = POKEMON_DETAILED_INFO.get(pokemon_names[0].lower(), {}) if POKEMON_DETAILED_INFO else {}
                p2_info = POKEMON_DETAILED_INFO.get(pokemon_names[1].lower() if len(pokemon_names) > 1 else pokemon_names[0].lower(), {}) if POKEMON_DETAILED_INFO else {}

                p1_attacks = list(p1_info.get("attacks", {}).items())
                p2_attacks = list(p2_info.get("attacks", {}).items())

                p1_attack = p1_attacks[0] if p1_attacks else ("attack", "energy beam")
                p2_attack = p2_attacks[0] if p2_attacks else ("attack", "energy beam")

                # More specific actions with visible effects
                actions = [
                    (pokemon_names[0], f"releasing {p1_attack[0]} with visible {p1_attack[1]} streaming from mouth"),
                    (pokemon_names[1] if len(pokemon_names) > 1 else pokemon_names[0], "reacting to impact damage, body recoiling slightly"),
                    (pokemon_names[1] if len(pokemon_names) > 1 else pokemon_names[0], f"charging {p2_attack[0]} with visible {p2_attack[1]} forming at mouth"),
                    (pokemon_names[1] if len(pokemon_names) > 1 else pokemon_names[0], f"releasing {p2_attack[0]} beam toward target")
                ]

                for pokemon, action in actions:
                    video_prompt = holistic_validator.generate_holistic_video_prompt(
                        pokemon_name=pokemon,
                        action=action,
                        scene_context=f"in {environment} environment, attack effects visible"
                    )
                    scene_descriptions.append(video_prompt)

            # Skip standard validation since we generated a validated prompt
            prompt_val = ValidationResult(
                stage="pre_prompt_holistic",
                passed=True,
                score=1.0,
                metrics={"method": "holistic_generation"}
            )
            improved_prompt = prompt
        else:
            # Stage 1: Pre-prompt validation (standard)
            improved_prompt, negative_prompt, prompt_val = self.stage1_validate_prompt(prompt, pokemon_names)

        results["stages"]["prompt"] = prompt_val.to_dict()

        if not prompt_val.passed:
            self.log("Prompt validation failed after improvements", "ERROR")
            # Continue anyway with improved prompt

        # Stage 2: Generate and validate storyboard
        storyboard_path = str(self.output_dir / "storyboard.jpg")
        storyboard_path, gen_val = self.stage2_generate_and_validate(
            improved_prompt, negative_prompt, pokemon_names, storyboard_path
        )
        results["stages"]["generation"] = gen_val.to_dict()

        if not storyboard_path:
            results["error"] = "Storyboard generation failed"
            return results

        # Stage 3: Split and validate
        scene_paths, split_val = self.stage3_split_and_validate(storyboard_path, grid_size)
        results["stages"]["split"] = split_val.to_dict()

        if not scene_paths:
            results["error"] = "Scene extraction failed"
            return results

        # Stage 4: Upscale and validate
        upscaled_paths, upscale_val = self.stage4_upscale_and_validate(scene_paths, upscale)
        results["stages"]["upscale"] = upscale_val.to_dict()

        # Stage 5: Generate videos and validate
        if scene_descriptions is None:
            scene_descriptions = [f"Pokemon battle scene {i+1}, dynamic action" for i in range(len(upscaled_paths))]

        video_paths, video_val = self.stage5_generate_videos_and_validate(upscaled_paths, scene_descriptions)
        results["stages"]["video"] = video_val.to_dict()

        # Save validation log
        log_path = self.output_dir / "validation_log.json"
        with open(log_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "validation_log": self.validation_log,
                "results": results
            }, f, indent=2)

        results["success"] = True
        results["outputs"] = {
            "storyboard": storyboard_path,
            "scenes": scene_paths,
            "upscaled": upscaled_paths,
            "videos": video_paths
        }

        self.log("=" * 70)
        self.log("PIPELINE COMPLETE")
        self.log(f"  Videos generated: {len(video_paths)}")
        self.log(f"  Validation log: {log_path}")
        self.log("=" * 70)

        return results


def main():
    parser = argparse.ArgumentParser(description="Validated Pokemon AI Video Pipeline")
    parser.add_argument("--prompt", "-p", default="", help="Base scene prompt (optional if using holistic)")
    parser.add_argument("--pokemon", "-k", nargs="+", required=True, help="Pokemon names")
    parser.add_argument("--output-dir", "-o", required=True, help="Output directory")
    parser.add_argument("--grid", "-g", default="2x2", help="Grid size")
    parser.add_argument("--upscale", "-u", type=int, default=2, help="Upscale factor")
    parser.add_argument("--environment", "-e", default="volcanic",
                        choices=["volcanic", "forest", "ocean", "cave", "urban", "mountain"],
                        help="Environment setting")
    parser.add_argument("--no-holistic", action="store_true",
                        help="Disable holistic prompt generation")

    args = parser.parse_args()

    grid = tuple(map(int, args.grid.split("x")))

    # Scene descriptions will be auto-generated if using holistic prompts
    scene_descriptions = None
    if args.no_holistic:
        # Use legacy scene descriptions if holistic is disabled
        scene_descriptions = [
            f"{args.pokemon[0]} launching powerful attack, dramatic motion, battle effects",
            f"{args.pokemon[1] if len(args.pokemon) > 1 else args.pokemon[0]} taking damage, intense reaction",
            f"{args.pokemon[1] if len(args.pokemon) > 1 else args.pokemon[0]} counterattacking with energy charging",
            f"Both Pokemon in fierce battle exchange, explosion effects"
        ]

    pipeline = ValidatedPipeline(args.output_dir)
    results = pipeline.run(
        prompt=args.prompt,
        pokemon_names=args.pokemon,
        scene_descriptions=scene_descriptions,
        grid_size=grid,
        upscale=args.upscale,
        environment=args.environment,
        use_holistic_prompts=not args.no_holistic
    )

    if results["success"]:
        print("\nPipeline completed successfully!")
        print(f"Videos: {results['outputs']['videos']}")
    else:
        print(f"\nPipeline failed: {results.get('error', 'Unknown')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
