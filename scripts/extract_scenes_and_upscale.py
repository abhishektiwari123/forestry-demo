#!/usr/bin/env python3
"""
Extract individual scenes from a storyboard image and upscale them.

This script:
1. Detects the grid layout of the storyboard
2. Extracts each panel as a separate image
3. Upscales each panel using LANCZOS (content-preserving)

IMPORTANT: Uses LOCAL upscaling only - NO AI regeneration.
The upscaled images are EXACTLY the same content, just at higher resolution.

Usage:
    python extract_scenes_and_upscale.py storyboard.jpg --panels 4 --scale 4
    python extract_scenes_and_upscale.py storyboard.jpg --output-dir ./scenes/
"""

import argparse
import os
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageEnhance


def detect_grid_layout(image: Image.Image, expected_panels: int = None) -> tuple[int, int]:
    """
    Detect the grid layout of a storyboard image.

    Args:
        image: PIL Image object
        expected_panels: Expected number of panels (helps accuracy)

    Returns:
        Tuple of (columns, rows)
    """
    width, height = image.size
    aspect = width / height

    # If expected panels specified, determine layout
    if expected_panels:
        if expected_panels == 2:
            return (2, 1) if aspect > 1.5 else (1, 2)
        elif expected_panels == 4:
            return (2, 2)
        elif expected_panels == 6:
            return (3, 2) if aspect > 1.2 else (2, 3)
        elif expected_panels == 8:
            return (4, 2) if aspect > 1.5 else (2, 4)

    # Auto-detect based on aspect ratio
    if aspect > 3.0:  # Very wide - likely 4x1 or 4x2
        return (4, 2) if height > width / 5 else (4, 1)
    elif aspect > 2.0:  # Wide - likely 3x2 or 3x1
        return (3, 2) if height > width / 4 else (3, 1)
    elif aspect > 1.3:  # Somewhat wide - likely 2x2
        return (2, 2)
    elif aspect > 0.7:  # Square-ish - likely 2x2
        return (2, 2)
    else:  # Tall - likely 2x3 or 1x4
        return (2, 3) if width > height / 4 else (1, 4)


def find_panel_borders(image: Image.Image, cols: int, rows: int) -> tuple[int, int]:
    """
    Detect border/gap size between panels.

    Args:
        image: PIL Image
        cols: Number of columns
        rows: Number of rows

    Returns:
        (border_x, border_y) in pixels
    """
    width, height = image.size
    panel_width = width // cols
    panel_height = height // rows

    # Check for dark lines at expected border positions
    # Default to small percentage if detection fails
    border_x = int(panel_width * 0.01)
    border_y = int(panel_height * 0.01)

    # Try to detect actual borders by looking for dark vertical/horizontal lines
    try:
        gray = image.convert('L')

        # Check vertical borders
        for offset in range(1, min(20, panel_width // 10)):
            for col in range(1, cols):
                x = col * panel_width
                # Sample pixels along the border line
                dark_count = 0
                for y in range(0, height, height // 20):
                    for dx in [-offset, offset]:
                        if 0 <= x + dx < width:
                            pixel = gray.getpixel((x + dx, y))
                            if pixel < 50:  # Dark pixel
                                dark_count += 1
                if dark_count > height // 40:  # Significant dark line
                    border_x = max(border_x, offset + 2)
                    break

        # Check horizontal borders
        for offset in range(1, min(20, panel_height // 10)):
            for row in range(1, rows):
                y = row * panel_height
                dark_count = 0
                for x in range(0, width, width // 20):
                    for dy in [-offset, offset]:
                        if 0 <= y + dy < height:
                            pixel = gray.getpixel((x, y + dy))
                            if pixel < 50:
                                dark_count += 1
                if dark_count > width // 40:
                    border_y = max(border_y, offset + 2)
                    break

    except Exception:
        pass  # Use defaults if detection fails

    return (border_x, border_y)


def extract_panels(
    image_path: str,
    output_dir: str,
    panels: int = None,
    remove_labels: bool = True
) -> list[str]:
    """
    Extract individual panels from a storyboard image.

    Args:
        image_path: Path to storyboard image
        output_dir: Directory to save extracted panels
        panels: Expected number of panels (auto-detect if None)
        remove_labels: Crop out text labels from top/bottom

    Returns:
        List of paths to extracted panel images
    """
    print(f"\n{'='*60}")
    print(f"EXTRACTING PANELS FROM STORYBOARD")
    print(f"{'='*60}")
    print(f"Input: {image_path}")

    with Image.open(image_path) as img:
        width, height = img.size
        print(f"Storyboard size: {width}x{height}")

        # Detect grid layout
        cols, rows = detect_grid_layout(img, panels)
        total_panels = cols * rows
        print(f"Detected layout: {cols}x{rows} ({total_panels} panels)")

        # Detect borders
        border_x, border_y = find_panel_borders(img, cols, rows)
        print(f"Border detection: {border_x}px x {border_y}px")

        # Calculate panel dimensions
        panel_width = width // cols
        panel_height = height // rows

        # Label removal margins (if storyboards have text labels)
        label_top = int(panel_height * 0.06) if remove_labels else 0
        label_bottom = int(panel_height * 0.04) if remove_labels else 0

        print(f"Panel size: {panel_width}x{panel_height}")
        if remove_labels:
            print(f"Label removal: top={label_top}px, bottom={label_bottom}px")

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Extract each panel
        extracted_paths = []
        panel_num = 1

        for row in range(rows):
            for col in range(cols):
                # Calculate crop boundaries
                left = col * panel_width + border_x
                top = row * panel_height + border_y + label_top
                right = (col + 1) * panel_width - border_x
                bottom = (row + 1) * panel_height - border_y - label_bottom

                # Ensure valid boundaries
                left = max(0, left)
                top = max(0, top)
                right = min(width, right)
                bottom = min(height, bottom)

                # Crop panel
                panel = img.crop((left, top, right, bottom))

                # Save panel
                output_path = f"{output_dir}/scene_{panel_num:02d}.jpg"
                panel.save(output_path, "JPEG", quality=98)

                extracted_paths.append(output_path)
                print(f"  Panel {panel_num}: {panel.size[0]}x{panel.size[1]} -> {output_path}")
                panel_num += 1

    print(f"\nExtracted {len(extracted_paths)} panels to {output_dir}")
    return extracted_paths


def upscale_lanczos_enhanced(image_path: str, output_path: str, scale: int = 4) -> bool:
    """
    Upscale image using LANCZOS with subtle enhancement.

    PRESERVES ORIGINAL CONTENT EXACTLY - only increases resolution.

    Args:
        image_path: Input image path
        output_path: Output image path
        scale: Upscale factor

    Returns:
        True if successful
    """
    try:
        with Image.open(image_path) as img:
            orig_width, orig_height = img.size
            new_width = orig_width * scale
            new_height = orig_height * scale

            # LANCZOS upscale (content-preserving)
            upscaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Subtle unsharp mask to restore sharpness lost in upscaling
            upscaled = upscaled.filter(ImageFilter.UnsharpMask(
                radius=1.5,
                percent=40,
                threshold=3
            ))

            # Very subtle contrast boost
            enhancer = ImageEnhance.Contrast(upscaled)
            upscaled = enhancer.enhance(1.03)

            # Save with high quality
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            if upscaled.mode in ('RGBA', 'P'):
                upscaled = upscaled.convert('RGB')

            upscaled.save(output_path, "JPEG", quality=98)

            file_size = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"  {orig_width}x{orig_height} -> {new_width}x{new_height} ({file_size:.2f} MB)")

            return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


def extract_and_upscale(
    storyboard_path: str,
    output_dir: str,
    panels: int = None,
    scale: int = 4,
    remove_labels: bool = True
) -> list[str]:
    """
    Complete pipeline: extract panels and upscale them.

    Args:
        storyboard_path: Path to storyboard image
        output_dir: Base output directory
        panels: Expected panel count
        scale: Upscale factor
        remove_labels: Remove text labels

    Returns:
        List of paths to upscaled images
    """
    # Create subdirectories
    extracted_dir = f"{output_dir}/extracted"
    upscaled_dir = f"{output_dir}/upscaled_{scale}x"

    # Step 1: Extract panels
    extracted_paths = extract_panels(
        storyboard_path,
        extracted_dir,
        panels,
        remove_labels
    )

    if not extracted_paths:
        print("Error: No panels extracted")
        return []

    # Step 2: Upscale each panel
    print(f"\n{'='*60}")
    print(f"UPSCALING PANELS ({scale}x) - CONTENT PRESERVING")
    print(f"{'='*60}")
    print("Using LANCZOS - guaranteed to preserve original content exactly")
    print("")

    Path(upscaled_dir).mkdir(parents=True, exist_ok=True)
    upscaled_paths = []

    for panel_path in extracted_paths:
        panel_name = Path(panel_path).stem
        upscaled_path = f"{upscaled_dir}/{panel_name}_{scale}x.jpg"

        print(f"Upscaling {panel_name}...")
        if upscale_lanczos_enhanced(panel_path, upscaled_path, scale):
            upscaled_paths.append(upscaled_path)

    # Summary
    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Extracted panels: {extracted_dir}")
    print(f"Upscaled panels:  {upscaled_dir}")
    print(f"Total: {len(upscaled_paths)} scenes ready for video generation")

    return upscaled_paths


def main():
    parser = argparse.ArgumentParser(
        description="Extract scenes from storyboard and upscale (content-preserving)"
    )
    parser.add_argument(
        "storyboard",
        help="Path to storyboard image"
    )
    parser.add_argument(
        "--panels", "-n",
        type=int,
        help="Number of panels (auto-detect if not specified)"
    )
    parser.add_argument(
        "--scale", "-s",
        type=int,
        default=4,
        help="Upscale factor (default: 4)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory (default: auto-generated)"
    )
    parser.add_argument(
        "--keep-labels",
        action="store_true",
        help="Keep text labels in panels (default: remove them)"
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Only extract, don't upscale"
    )

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.storyboard):
        print(f"Error: File not found: {args.storyboard}")
        sys.exit(1)

    # Generate output directory
    output_dir = args.output_dir
    if not output_dir:
        input_path = Path(args.storyboard)
        output_dir = f"{input_path.parent}/{input_path.stem}_scenes"

    if args.extract_only:
        # Extract only
        paths = extract_panels(
            args.storyboard,
            output_dir,
            args.panels,
            not args.keep_labels
        )
    else:
        # Extract and upscale
        paths = extract_and_upscale(
            args.storyboard,
            output_dir,
            args.panels,
            args.scale,
            not args.keep_labels
        )

    sys.exit(0 if paths else 1)


if __name__ == "__main__":
    main()
