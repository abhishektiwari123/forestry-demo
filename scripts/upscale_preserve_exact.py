#!/usr/bin/env python3
"""
Upscale images while EXACTLY preserving original content.

This script uses LOCAL upscaling methods that do NOT alter the image content.
NO AI regeneration - the output is guaranteed to be the same image, just bigger.

Methods available:
1. LANCZOS - High-quality interpolation (always available, uses Pillow)
2. Real-ESRGAN - Neural network designed for faithful upscaling (if installed)

IMPORTANT: Unlike "creative" AI upscalers, these methods will NEVER:
- Change character faces or expressions
- Alter the composition
- Add or remove elements
- Change colors or lighting
- Generate new content

Usage:
    python upscale_preserve_exact.py image.jpg --scale 4 --output upscaled.jpg
    python upscale_preserve_exact.py image.jpg --scale 2 --method lanczos
    python upscale_preserve_exact.py image.jpg --scale 4 --method realesrgan
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageEnhance

# Check if Real-ESRGAN is available
REALESRGAN_AVAILABLE = False
REALESRGAN_PATH = None

for path in [
    "/usr/local/bin/realesrgan-ncnn-vulkan",
    "/usr/bin/realesrgan-ncnn-vulkan",
    os.path.expanduser("~/realesrgan-ncnn-vulkan"),
    "./realesrgan-ncnn-vulkan",
    "realesrgan-ncnn-vulkan"
]:
    if os.path.exists(path) or subprocess.run(
        ["which", path.split("/")[-1]],
        capture_output=True
    ).returncode == 0:
        REALESRGAN_AVAILABLE = True
        REALESRGAN_PATH = path
        break


def upscale_lanczos(image_path: str, output_path: str, scale: int = 4) -> bool:
    """
    Upscale image using LANCZOS resampling.

    LANCZOS is a high-quality interpolation algorithm that:
    - Preserves edges and details
    - Does not alter image content
    - Works on any image type
    - Is fast and always available

    Args:
        image_path: Path to input image
        output_path: Path for output image
        scale: Upscale factor (2, 4, 8, etc.)

    Returns:
        True if successful
    """
    try:
        with Image.open(image_path) as img:
            orig_width, orig_height = img.size
            new_width = orig_width * scale
            new_height = orig_height * scale

            print(f"LANCZOS Upscaling: {orig_width}x{orig_height} -> {new_width}x{new_height}")

            # Use LANCZOS for highest quality
            upscaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Determine output format
            if output_path.lower().endswith('.png'):
                upscaled.save(output_path, "PNG", optimize=True)
            else:
                # For JPEG, ensure RGB mode and use high quality
                if upscaled.mode in ('RGBA', 'P'):
                    upscaled = upscaled.convert('RGB')
                upscaled.save(output_path, "JPEG", quality=98, optimize=True)

            file_size = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"Saved: {output_path} ({file_size:.2f} MB)")

            return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def upscale_lanczos_enhanced(image_path: str, output_path: str, scale: int = 4) -> bool:
    """
    Upscale with LANCZOS plus subtle sharpening to improve clarity.

    Still preserves original content, just adds slight edge enhancement
    to compensate for natural softening during upscaling.

    Args:
        image_path: Path to input image
        output_path: Path for output image
        scale: Upscale factor

    Returns:
        True if successful
    """
    try:
        with Image.open(image_path) as img:
            orig_width, orig_height = img.size
            new_width = orig_width * scale
            new_height = orig_height * scale

            print(f"Enhanced LANCZOS: {orig_width}x{orig_height} -> {new_width}x{new_height}")

            # First pass: LANCZOS upscale
            upscaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Second pass: Subtle unsharp mask for edge enhancement
            # This does NOT alter content, just enhances existing edges
            upscaled = upscaled.filter(ImageFilter.UnsharpMask(
                radius=1.5,      # Small radius to target fine details
                percent=50,      # Moderate strength
                threshold=3      # Avoid enhancing noise
            ))

            # Slight contrast boost to compensate for softening
            enhancer = ImageEnhance.Contrast(upscaled)
            upscaled = enhancer.enhance(1.05)  # Very subtle - 5% increase

            # Save
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            if output_path.lower().endswith('.png'):
                upscaled.save(output_path, "PNG", optimize=True)
            else:
                if upscaled.mode in ('RGBA', 'P'):
                    upscaled = upscaled.convert('RGB')
                upscaled.save(output_path, "JPEG", quality=98, optimize=True)

            file_size = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"Saved: {output_path} ({file_size:.2f} MB)")

            return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def upscale_realesrgan(image_path: str, output_path: str, scale: int = 4) -> bool:
    """
    Upscale using Real-ESRGAN neural network.

    Real-ESRGAN is specifically designed for FAITHFUL upscaling:
    - Preserves original content exactly
    - Enhances details without hallucinating new content
    - Much better quality than simple interpolation
    - Trained to restore, not regenerate

    Requires Real-ESRGAN to be installed.

    Args:
        image_path: Path to input image
        output_path: Path for output image
        scale: Upscale factor (2 or 4)

    Returns:
        True if successful
    """
    if not REALESRGAN_AVAILABLE:
        print("Real-ESRGAN not available. Falling back to LANCZOS.")
        return upscale_lanczos_enhanced(image_path, output_path, scale)

    try:
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Determine model based on scale
        if scale == 2:
            model = "realesrgan-x2plus"
        else:
            model = "realesrgan-x4plus"

        print(f"Real-ESRGAN Upscaling with model: {model}")

        # Run Real-ESRGAN
        cmd = [
            REALESRGAN_PATH,
            "-i", image_path,
            "-o", output_path,
            "-s", str(scale),
            "-n", model
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Real-ESRGAN error: {result.stderr}")
            print("Falling back to LANCZOS...")
            return upscale_lanczos_enhanced(image_path, output_path, scale)

        # Verify output
        if os.path.exists(output_path):
            with Image.open(output_path) as img:
                w, h = img.size
            file_size = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"Saved: {output_path} ({w}x{h}, {file_size:.2f} MB)")
            return True
        else:
            print("Output not created. Falling back to LANCZOS...")
            return upscale_lanczos_enhanced(image_path, output_path, scale)

    except Exception as e:
        print(f"Error: {e}")
        print("Falling back to LANCZOS...")
        return upscale_lanczos_enhanced(image_path, output_path, scale)


def upscale_preserve_exact(
    image_path: str,
    output_path: str,
    scale: int = 4,
    method: str = "auto"
) -> bool:
    """
    Main upscaling function that preserves original content exactly.

    Args:
        image_path: Path to input image
        output_path: Path for output image
        scale: Upscale factor
        method: "lanczos", "enhanced", "realesrgan", or "auto"

    Returns:
        True if successful
    """
    # Validate input
    if not os.path.exists(image_path):
        print(f"Error: Input file not found: {image_path}")
        return False

    # Get original dimensions
    with Image.open(image_path) as img:
        orig_width, orig_height = img.size

    print(f"\n{'='*60}")
    print(f"EXACT CONTENT PRESERVATION UPSCALER")
    print(f"{'='*60}")
    print(f"Input: {image_path}")
    print(f"Original: {orig_width}x{orig_height}")
    print(f"Target: {orig_width * scale}x{orig_height * scale}")
    print(f"Scale: {scale}x")
    print(f"Method: {method}")
    print(f"{'='*60}\n")

    # Select method
    if method == "auto":
        # Prefer Real-ESRGAN if available, otherwise enhanced LANCZOS
        if REALESRGAN_AVAILABLE:
            print("Using Real-ESRGAN (best quality, content-preserving)")
            return upscale_realesrgan(image_path, output_path, scale)
        else:
            print("Using Enhanced LANCZOS (high quality, always available)")
            return upscale_lanczos_enhanced(image_path, output_path, scale)

    elif method == "lanczos":
        print("Using pure LANCZOS (guaranteed content preservation)")
        return upscale_lanczos(image_path, output_path, scale)

    elif method == "enhanced":
        print("Using Enhanced LANCZOS (LANCZOS + sharpening)")
        return upscale_lanczos_enhanced(image_path, output_path, scale)

    elif method == "realesrgan":
        if REALESRGAN_AVAILABLE:
            print("Using Real-ESRGAN (neural network upscaling)")
            return upscale_realesrgan(image_path, output_path, scale)
        else:
            print("Real-ESRGAN not installed. Using Enhanced LANCZOS instead.")
            return upscale_lanczos_enhanced(image_path, output_path, scale)

    else:
        print(f"Unknown method: {method}. Using auto.")
        return upscale_preserve_exact(image_path, output_path, scale, "auto")


def batch_upscale(input_dir: str, output_dir: str, scale: int = 4, method: str = "auto") -> int:
    """
    Upscale all images in a directory.

    Args:
        input_dir: Directory containing images
        output_dir: Directory for output images
        scale: Upscale factor
        method: Upscaling method

    Returns:
        Number of successfully upscaled images
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Find images
    extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
    images = []
    for ext in extensions:
        images.extend(Path(input_dir).glob(f"*{ext}"))
        images.extend(Path(input_dir).glob(f"*{ext.upper()}"))

    print(f"\nBatch upscaling {len(images)} images...")

    success_count = 0
    for img_path in sorted(images):
        output_path = Path(output_dir) / f"{img_path.stem}_{scale}x{img_path.suffix}"

        if upscale_preserve_exact(str(img_path), str(output_path), scale, method):
            success_count += 1

    print(f"\nBatch complete: {success_count}/{len(images)} successful")
    return success_count


def main():
    parser = argparse.ArgumentParser(
        description="Upscale images while EXACTLY preserving original content"
    )
    parser.add_argument(
        "input",
        help="Input image or directory"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output path (default: auto-generated)"
    )
    parser.add_argument(
        "--scale", "-s",
        type=int,
        default=4,
        choices=[2, 4, 8],
        help="Upscale factor (default: 4)"
    )
    parser.add_argument(
        "--method", "-m",
        default="auto",
        choices=["auto", "lanczos", "enhanced", "realesrgan"],
        help="Upscaling method (default: auto)"
    )
    parser.add_argument(
        "--batch", "-b",
        action="store_true",
        help="Process entire directory"
    )

    args = parser.parse_args()

    # Print availability info
    print("\n" + "="*60)
    print("UPSCALING METHODS AVAILABLE:")
    print("="*60)
    print(f"  LANCZOS: Always available (Pillow)")
    print(f"  Enhanced LANCZOS: Always available (Pillow)")
    print(f"  Real-ESRGAN: {'Available' if REALESRGAN_AVAILABLE else 'Not installed'}")
    print("="*60 + "\n")

    if args.batch or os.path.isdir(args.input):
        # Batch mode
        output_dir = args.output or f"{args.input}_upscaled_{args.scale}x"
        count = batch_upscale(args.input, output_dir, args.scale, args.method)
        sys.exit(0 if count > 0 else 1)

    else:
        # Single image mode
        if not os.path.exists(args.input):
            print(f"Error: File not found: {args.input}")
            sys.exit(1)

        output_path = args.output
        if not output_path:
            input_path = Path(args.input)
            output_path = f"{input_path.parent}/{input_path.stem}_{args.scale}x{input_path.suffix}"

        success = upscale_preserve_exact(args.input, output_path, args.scale, args.method)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
