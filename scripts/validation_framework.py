#!/usr/bin/env python3
"""
Validation Framework for Pokemon AI Video Generator.

Validates images and videos against quality criteria, providing
feedback for iterative prompt improvement.

Usage:
    python validation_framework.py --image path/to/image.jpg
    python validation_framework.py --video path/to/video.mp4
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image


@dataclass
class ImageValidationResult:
    """Result of image validation check."""
    file_path: str
    valid: bool
    width: int
    height: int
    file_size_mb: float
    aspect_ratio: float
    issues: list[str]
    timestamp: str


@dataclass
class VideoValidationResult:
    """Result of video validation check."""
    file_path: str
    valid: bool
    duration_seconds: float
    width: int
    height: int
    file_size_mb: float
    has_audio: bool
    fps: float
    issues: list[str]
    timestamp: str


# Default validation criteria
IMAGE_CRITERIA = {
    "min_width": 800,
    "min_height": 450,
    "min_file_size_mb": 0.1,
    "max_file_size_mb": 50,
    "target_aspect_ratio": 16/9,
    "aspect_ratio_tolerance": 0.1
}

VIDEO_CRITERIA = {
    "min_duration": 4.5,
    "max_duration": 10.5,
    "target_duration": 5.0,
    "min_file_size_mb": 1,
    "max_file_size_mb": 100,
    "require_audio": False,
    "min_fps": 20,
    "min_width": 720,
    "min_height": 480
}


class ValidationFramework:
    """Framework for validating generated images and videos."""

    def __init__(self, criteria_image: dict = None, criteria_video: dict = None):
        self.image_criteria = criteria_image or IMAGE_CRITERIA
        self.video_criteria = criteria_video or VIDEO_CRITERIA
        self.results = []

    def validate_image(self, image_path: str) -> ImageValidationResult:
        """
        Validate an image against quality criteria.

        Args:
            image_path: Path to image file

        Returns:
            ImageValidationResult with validation details
        """
        issues = []

        try:
            # Get file size
            file_size_mb = Path(image_path).stat().st_size / (1024 * 1024)

            # Open and analyze image
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height

            # Check minimum dimensions
            if width < self.image_criteria["min_width"]:
                issues.append(f"Width {width} below minimum {self.image_criteria['min_width']}")
            if height < self.image_criteria["min_height"]:
                issues.append(f"Height {height} below minimum {self.image_criteria['min_height']}")

            # Check file size
            if file_size_mb < self.image_criteria["min_file_size_mb"]:
                issues.append(f"File size {file_size_mb:.2f}MB below minimum {self.image_criteria['min_file_size_mb']}MB")
            if file_size_mb > self.image_criteria["max_file_size_mb"]:
                issues.append(f"File size {file_size_mb:.2f}MB above maximum {self.image_criteria['max_file_size_mb']}MB")

            # Check aspect ratio
            target_ar = self.image_criteria["target_aspect_ratio"]
            tolerance = self.image_criteria["aspect_ratio_tolerance"]
            if abs(aspect_ratio - target_ar) > tolerance:
                issues.append(f"Aspect ratio {aspect_ratio:.2f} differs from target {target_ar:.2f}")

            result = ImageValidationResult(
                file_path=image_path,
                valid=len(issues) == 0,
                width=width,
                height=height,
                file_size_mb=file_size_mb,
                aspect_ratio=aspect_ratio,
                issues=issues,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            result = ImageValidationResult(
                file_path=image_path,
                valid=False,
                width=0,
                height=0,
                file_size_mb=0,
                aspect_ratio=0,
                issues=[f"Error reading image: {e}"],
                timestamp=datetime.now().isoformat()
            )

        self.results.append(asdict(result))
        return result

    def validate_video(self, video_path: str) -> VideoValidationResult:
        """
        Validate a video against quality criteria.

        Args:
            video_path: Path to video file

        Returns:
            VideoValidationResult with validation details
        """
        issues = []

        try:
            # Get file size
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)

            # Get video metadata using ffprobe
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            metadata = json.loads(result.stdout)

            # Extract video stream info
            video_stream = next(
                (s for s in metadata.get("streams", []) if s.get("codec_type") == "video"),
                {}
            )

            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))

            # Parse frame rate
            fps_str = video_stream.get("r_frame_rate", "0/1")
            if "/" in fps_str:
                num, den = map(int, fps_str.split("/"))
                fps = num / den if den else 0
            else:
                fps = float(fps_str)

            # Get duration
            duration = float(metadata.get("format", {}).get("duration", 0))

            # Check for audio stream
            has_audio = any(
                s.get("codec_type") == "audio"
                for s in metadata.get("streams", [])
            )

            # Validate against criteria
            if duration < self.video_criteria["min_duration"]:
                issues.append(f"Duration {duration:.1f}s below minimum {self.video_criteria['min_duration']}s")
            if duration > self.video_criteria["max_duration"]:
                issues.append(f"Duration {duration:.1f}s above maximum {self.video_criteria['max_duration']}s")

            if file_size_mb < self.video_criteria["min_file_size_mb"]:
                issues.append(f"File size {file_size_mb:.1f}MB below minimum")
            if file_size_mb > self.video_criteria["max_file_size_mb"]:
                issues.append(f"File size {file_size_mb:.1f}MB above maximum")

            if self.video_criteria["require_audio"] and not has_audio:
                issues.append("Video has no audio track")

            if fps < self.video_criteria["min_fps"]:
                issues.append(f"Frame rate {fps:.1f} below minimum {self.video_criteria['min_fps']}")

            if width < self.video_criteria["min_width"]:
                issues.append(f"Width {width} below minimum {self.video_criteria['min_width']}")
            if height < self.video_criteria["min_height"]:
                issues.append(f"Height {height} below minimum {self.video_criteria['min_height']}")

            result = VideoValidationResult(
                file_path=video_path,
                valid=len(issues) == 0,
                duration_seconds=duration,
                width=width,
                height=height,
                file_size_mb=file_size_mb,
                has_audio=has_audio,
                fps=fps,
                issues=issues,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            result = VideoValidationResult(
                file_path=video_path,
                valid=False,
                duration_seconds=0,
                width=0,
                height=0,
                file_size_mb=0,
                has_audio=False,
                fps=0,
                issues=[f"Error reading video: {e}"],
                timestamp=datetime.now().isoformat()
            )

        self.results.append(asdict(result))
        return result

    def generate_feedback_report(self, output_path: str) -> str:
        """
        Generate a feedback report with improvement recommendations.

        Args:
            output_path: Path to save the report

        Returns:
            Report content as string
        """
        lines = [
            "=" * 60,
            "VALIDATION FEEDBACK REPORT",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 60,
            ""
        ]

        # Summarize results
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("valid", False))
        failed = total - passed

        lines.extend([
            f"Total Validated: {total}",
            f"Passed: {passed}",
            f"Failed: {failed}",
            f"Success Rate: {passed/total*100:.1f}%" if total > 0 else "N/A",
            ""
        ])

        # List issues
        if failed > 0:
            lines.extend([
                "ISSUES FOUND:",
                "-" * 40
            ])

            for result in self.results:
                if not result.get("valid", True):
                    lines.append(f"\nFile: {result.get('file_path', 'Unknown')}")
                    for issue in result.get("issues", []):
                        lines.append(f"  - {issue}")

            lines.extend([
                "",
                "RECOMMENDATIONS:",
                "-" * 40
            ])

            # Analyze common issues
            all_issues = []
            for r in self.results:
                all_issues.extend(r.get("issues", []))

            if any("aspect ratio" in i.lower() for i in all_issues):
                lines.append("- Adjust image generation to use 16:9 aspect ratio")

            if any("duration" in i.lower() for i in all_issues):
                lines.append("- Review video duration parameters in generation prompts")

            if any("resolution" in i.lower() or "width" in i.lower() or "height" in i.lower() for i in all_issues):
                lines.append("- Increase resolution settings in image/video generation")

            if any("file size" in i.lower() for i in all_issues):
                lines.append("- Check for corrupted downloads or incomplete generations")

        else:
            lines.append("All validations passed! No issues found.")

        report = "\n".join(lines)

        # Save report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)

        return report

    def save_validation_log(self, output_path: str):
        """Save validation results as JSON for analysis."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "total_validations": len(self.results),
            "passed": sum(1 for r in self.results if r.get("valid", False)),
            "failed": sum(1 for r in self.results if not r.get("valid", True)),
            "results": self.results
        }

        with open(output_path, "w") as f:
            json.dump(log_data, f, indent=2)

        print(f"Validation log saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate images and videos against quality criteria"
    )
    parser.add_argument(
        "--image",
        help="Path to image file to validate"
    )
    parser.add_argument(
        "--video",
        help="Path to video file to validate"
    )
    parser.add_argument(
        "--output-report",
        help="Path to save feedback report"
    )
    parser.add_argument(
        "--output-log",
        help="Path to save JSON validation log"
    )

    args = parser.parse_args()

    if not args.image and not args.video:
        print("Error: Specify --image or --video to validate")
        sys.exit(1)

    framework = ValidationFramework()

    if args.image:
        if not os.path.exists(args.image):
            print(f"Error: Image not found: {args.image}")
            sys.exit(1)

        result = framework.validate_image(args.image)

        print(f"\nImage Validation: {'PASSED' if result.valid else 'FAILED'}")
        print(f"  Size: {result.width}x{result.height}")
        print(f"  File: {result.file_size_mb:.2f} MB")
        print(f"  Aspect: {result.aspect_ratio:.2f}")

        if result.issues:
            print("  Issues:")
            for issue in result.issues:
                print(f"    - {issue}")

    if args.video:
        if not os.path.exists(args.video):
            print(f"Error: Video not found: {args.video}")
            sys.exit(1)

        result = framework.validate_video(args.video)

        print(f"\nVideo Validation: {'PASSED' if result.valid else 'FAILED'}")
        print(f"  Size: {result.width}x{result.height}")
        print(f"  Duration: {result.duration_seconds:.1f}s")
        print(f"  File: {result.file_size_mb:.1f} MB")
        print(f"  FPS: {result.fps:.1f}")
        print(f"  Audio: {'Yes' if result.has_audio else 'No'}")

        if result.issues:
            print("  Issues:")
            for issue in result.issues:
                print(f"    - {issue}")

    # Save outputs if requested
    if args.output_report:
        report = framework.generate_feedback_report(args.output_report)
        print(f"\nFeedback report saved to: {args.output_report}")

    if args.output_log:
        framework.save_validation_log(args.output_log)


if __name__ == "__main__":
    main()
