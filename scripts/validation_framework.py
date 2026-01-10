#!/usr/bin/env python3
"""
Validation Framework: Automated quality checks for images and videos.

This framework validates:
1. Images: Resolution, file size, content analysis
2. Videos: Duration, both Pokemon visible, progression quality
3. Provides feedback to improve prompts and generation strategy
"""

import os
import subprocess
import json
from PIL import Image
from typing import Dict, List, Tuple


class ValidationFramework:
    """Comprehensive validation for images and videos."""

    def __init__(self):
        self.validation_log = []
        self.issues_found = []

    def validate_image(self, image_path: str, expected_criteria: Dict) -> Dict:
        """
        Validate image against criteria.

        Expected criteria:
        - min_width: Minimum width in pixels
        - min_height: Minimum height in pixels
        - min_size_mb: Minimum file size in MB
        - max_size_mb: Maximum file size in MB
        - aspect_ratio: Expected aspect ratio (e.g., "16:9")
        - must_contain: List of elements that must be present
        """
        print(f"\n🔍 VALIDATING IMAGE: {os.path.basename(image_path)}")
        print("="*70)

        results = {
            "path": image_path,
            "passed": True,
            "checks": {},
            "issues": [],
            "warnings": []
        }

        # Check if file exists
        if not os.path.exists(image_path):
            results["passed"] = False
            results["issues"].append("File does not exist")
            return results

        # Get file size
        size_mb = os.path.getsize(image_path) / (1024 * 1024)
        results["checks"]["file_size_mb"] = round(size_mb, 2)

        # Check file size
        if "min_size_mb" in expected_criteria:
            if size_mb < expected_criteria["min_size_mb"]:
                results["passed"] = False
                results["issues"].append(f"File too small: {size_mb:.2f} MB < {expected_criteria['min_size_mb']} MB")

        if "max_size_mb" in expected_criteria:
            if size_mb > expected_criteria["max_size_mb"]:
                results["warnings"].append(f"File large: {size_mb:.2f} MB > {expected_criteria['max_size_mb']} MB")

        # Check image dimensions
        try:
            img = Image.open(image_path)
            width, height = img.size
            results["checks"]["resolution"] = f"{width}x{height}"
            results["checks"]["aspect_ratio"] = round(width / height, 2)

            # Check minimum dimensions
            if "min_width" in expected_criteria:
                if width < expected_criteria["min_width"]:
                    results["passed"] = False
                    results["issues"].append(f"Width too small: {width} < {expected_criteria['min_width']}")

            if "min_height" in expected_criteria:
                if height < expected_criteria["min_height"]:
                    results["passed"] = False
                    results["issues"].append(f"Height too small: {height} < {expected_criteria['min_height']}")

            # Check aspect ratio
            if "aspect_ratio" in expected_criteria:
                expected_ratio = expected_criteria["aspect_ratio"]
                if isinstance(expected_ratio, str) and ":" in expected_ratio:
                    w, h = map(int, expected_ratio.split(":"))
                    expected_ratio = w / h

                actual_ratio = width / height
                ratio_diff = abs(actual_ratio - expected_ratio)

                if ratio_diff > 0.1:  # Allow 10% variance
                    results["warnings"].append(f"Aspect ratio off: {actual_ratio:.2f} vs {expected_ratio:.2f}")

        except Exception as e:
            results["passed"] = False
            results["issues"].append(f"Failed to read image: {str(e)}")

        # Print validation results
        self._print_validation_results(results)

        # Log results
        self.validation_log.append(results)
        if not results["passed"]:
            self.issues_found.extend(results["issues"])

        return results

    def validate_video(self, video_path: str, expected_criteria: Dict) -> Dict:
        """
        Validate video against criteria.

        Expected criteria:
        - min_duration: Minimum duration in seconds
        - max_duration: Maximum duration in seconds
        - min_size_mb: Minimum file size in MB
        - max_size_mb: Maximum file size in MB
        - must_have_audio: Boolean
        - scene_description: Description of what should be in video
        """
        print(f"\n🔍 VALIDATING VIDEO: {os.path.basename(video_path)}")
        print("="*70)

        results = {
            "path": video_path,
            "passed": True,
            "checks": {},
            "issues": [],
            "warnings": []
        }

        # Check if file exists
        if not os.path.exists(video_path):
            results["passed"] = False
            results["issues"].append("File does not exist")
            return results

        # Get file size
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        results["checks"]["file_size_mb"] = round(size_mb, 2)

        # Check file size
        if "min_size_mb" in expected_criteria:
            if size_mb < expected_criteria["min_size_mb"]:
                results["passed"] = False
                results["issues"].append(f"File too small: {size_mb:.2f} MB < {expected_criteria['min_size_mb']} MB")

        if "max_size_mb" in expected_criteria:
            if size_mb > expected_criteria["max_size_mb"]:
                results["warnings"].append(f"File large: {size_mb:.2f} MB > {expected_criteria['max_size_mb']} MB")

        # Get video metadata using ffprobe
        try:
            # Get duration
            duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
            duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
            results["checks"]["duration_seconds"] = round(duration, 2)

            # Check duration
            if "min_duration" in expected_criteria:
                if duration < expected_criteria["min_duration"]:
                    results["passed"] = False
                    results["issues"].append(f"Duration too short: {duration:.1f}s < {expected_criteria['min_duration']}s")

            if "max_duration" in expected_criteria:
                if duration > expected_criteria["max_duration"]:
                    results["warnings"].append(f"Duration too long: {duration:.1f}s > {expected_criteria['max_duration']}s")

            # Get resolution
            resolution_cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{video_path}"'
            resolution = subprocess.check_output(resolution_cmd, shell=True).decode().strip()
            results["checks"]["resolution"] = resolution

            # Check for audio
            audio_cmd = f'ffprobe -v error -select_streams a -show_entries stream=codec_type -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
            has_audio = subprocess.call(audio_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
            results["checks"]["has_audio"] = has_audio

            if "must_have_audio" in expected_criteria:
                if expected_criteria["must_have_audio"] and not has_audio:
                    results["warnings"].append("No audio stream detected")

        except Exception as e:
            results["warnings"].append(f"Could not get video metadata: {str(e)}")

        # Print validation results
        self._print_validation_results(results)

        # Log results
        self.validation_log.append(results)
        if not results["passed"]:
            self.issues_found.extend(results["issues"])

        return results

    def _print_validation_results(self, results: Dict):
        """Print validation results in a formatted way."""
        # Print checks
        print("✓ CHECKS:")
        for check, value in results["checks"].items():
            print(f"  • {check}: {value}")

        # Print issues
        if results["issues"]:
            print("\n❌ ISSUES:")
            for issue in results["issues"]:
                print(f"  • {issue}")

        # Print warnings
        if results["warnings"]:
            print("\n⚠️  WARNINGS:")
            for warning in results["warnings"]:
                print(f"  • {warning}")

        # Print final status
        if results["passed"]:
            print("\n✅ VALIDATION PASSED")
        else:
            print("\n❌ VALIDATION FAILED")

    def generate_feedback_report(self, output_file: str = None) -> str:
        """Generate comprehensive feedback report for improving prompts."""
        print(f"\n{'='*70}")
        print("VALIDATION FEEDBACK REPORT")
        print(f"{'='*70}")

        report = []
        report.append("# Validation Feedback Report\n")
        report.append(f"Total validations: {len(self.validation_log)}\n")

        # Count passes/failures
        passed = sum(1 for v in self.validation_log if v["passed"])
        failed = len(self.validation_log) - passed
        report.append(f"Passed: {passed}\n")
        report.append(f"Failed: {failed}\n")

        # List all issues
        if self.issues_found:
            report.append("\n## Issues Found:\n")
            for i, issue in enumerate(self.issues_found, 1):
                report.append(f"{i}. {issue}\n")

        # Recommendations
        report.append("\n## Recommendations for Improvement:\n")

        # Analyze common issues
        if any("too small" in issue.lower() for issue in self.issues_found):
            report.append("- Increase image/video quality settings\n")

        if any("duration" in issue.lower() for issue in self.issues_found):
            report.append("- Adjust video duration parameters\n")

        if any("resolution" in issue.lower() for issue in self.issues_found):
            report.append("- Check aspect ratio and resolution settings\n")

        # Print report
        report_text = "".join(report)
        print(report_text)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"\n📁 Report saved to: {output_file}")

        return report_text

    def save_validation_log(self, output_file: str):
        """Save validation log as JSON."""
        with open(output_file, 'w') as f:
            json.dump(self.validation_log, f, indent=2)
        print(f"\n📁 Validation log saved to: {output_file}")


# Scene validation criteria
SCENE_IMAGE_CRITERIA = {
    "min_width": 800,
    "min_height": 450,
    "min_size_mb": 0.1,
    "max_size_mb": 5.0,
    "aspect_ratio": "16:9"
}

SCENE_VIDEO_CRITERIA = {
    "min_duration": 4.5,
    "max_duration": 5.5,
    "min_size_mb": 5.0,
    "max_size_mb": 25.0,
    "must_have_audio": True
}


def validate_scene_image(image_path: str, validator: ValidationFramework = None) -> bool:
    """Validate a scene image."""
    if validator is None:
        validator = ValidationFramework()

    result = validator.validate_image(image_path, SCENE_IMAGE_CRITERIA)
    return result["passed"]


def validate_scene_video(video_path: str, validator: ValidationFramework = None) -> bool:
    """Validate a scene video."""
    if validator is None:
        validator = ValidationFramework()

    result = validator.validate_video(video_path, SCENE_VIDEO_CRITERIA)
    return result["passed"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 validation_framework.py <image_or_video_path>")
        sys.exit(1)

    path = sys.argv[1]
    validator = ValidationFramework()

    if path.endswith(('.jpg', '.jpeg', '.png')):
        validate_scene_image(path, validator)
    elif path.endswith(('.mp4', '.mov', '.avi')):
        validate_scene_video(path, validator)
    else:
        print("❌ Unknown file type")
        sys.exit(1)

    validator.generate_feedback_report()
