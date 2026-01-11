#!/usr/bin/env python3
"""
Extract individual panels from storyboard grids and upscale them.

Supports 3x2 (6 panel) and 4x2 (8 panel) storyboard layouts.
Automatically detects grid layout, removes text labels, and upscales.

Usage:
    python extract_and_upscale_panels.py storyboard.jpg --panels 6 --scale 2
"""

import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
import requests

# Try loading .env from multiple locations
for env_path in ['.env', 'scripts/.env', '../scripts/.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break


def detect_grid_layout(image: Image.Image) -> tuple[int, int]:
    """
    Detect the grid layout of a storyboard image.

    Args:
        image: PIL Image object

    Returns:
        Tuple of (columns, rows)
    """
    width, height = image.size
    aspect = width / height

    # Common layouts based on aspect ratio
    if aspect > 2.5:  # Very wide - likely 4x2
        return (4, 2)
    elif aspect > 1.3:  # Wide - likely 3x2
        return (3, 2)
    elif aspect > 0.9:  # Square-ish - likely 2x2
        return (2, 2)
    else:  # Tall - likely 2x3 or 2x4
        if height / width > 1.5:
            return (2, 4)
        return (2, 3)


def extract_panels(
    image_path: str,
    output_dir: str,
    num_panels: int = None,
    remove_labels: bool = True
) -> list[str]:
    """
    Extract individual panels from a storyboard grid.

    Args:
        image_path: Path to storyboard image
        output_dir: Directory to save extracted panels
        num_panels: Expected number of panels (auto-detect if None)
        remove_labels: Whether to crop out text labels

    Returns:
        List of paths to extracted panel images
    """
    print(f"\nExtracting panels from: {image_path}")

    # Load image
    with Image.open(image_path) as img:
        width, height = img.size
        print(f"  Original size: {width}x{height}")

        # Detect or verify grid layout
        detected_cols, detected_rows = detect_grid_layout(img)

        if num_panels:
            # User specified panel count
            if num_panels == 6:
                cols, rows = 3, 2
            elif num_panels == 8:
                cols, rows = 4, 2
            elif num_panels == 4:
                cols, rows = 2, 2
            else:
                cols, rows = detected_cols, detected_rows
        else:
            cols, rows = detected_cols, detected_rows

        total_panels = cols * rows
        print(f"  Grid layout: {cols}x{rows} ({total_panels} panels)")

        # Calculate panel dimensions
        panel_width = width // cols
        panel_height = height // rows

        # Estimate border/gap size (typically 1-3% of panel size)
        border_x = int(panel_width * 0.02)
        border_y = int(panel_height * 0.02)

        # Label removal - crop top and bottom of each panel
        label_top = int(panel_height * 0.08) if remove_labels else 0
        label_bottom = int(panel_height * 0.05) if remove_labels else 0

        print(f"  Panel size: {panel_width}x{panel_height}")
        print(f"  Border estimate: {border_x}x{border_y}")
        if remove_labels:
            print(f"  Label removal: top={label_top}px, bottom={label_bottom}px")

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Extract each panel
        extracted_paths = []
        panel_num = 1

        for row in range(rows):
            for col in range(cols):
                # Calculate panel bounds
                left = col * panel_width + border_x
                top = row * panel_height + border_y + label_top
                right = (col + 1) * panel_width - border_x
                bottom = (row + 1) * panel_height - border_y - label_bottom

                # Crop panel
                panel = img.crop((left, top, right, bottom))

                # Save panel
                panel_path = f"{output_dir}/panel_{panel_num:02d}.jpg"
                panel.save(panel_path, "JPEG", quality=98)

                panel_size = panel.size
                print(f"  Panel {panel_num}: {panel_size[0]}x{panel_size[1]} -> {panel_path}")

                extracted_paths.append(panel_path)
                panel_num += 1

    print(f"  Extracted {len(extracted_paths)} panels to {output_dir}")
    return extracted_paths


def upscale_image_lanczos(image_path: str, output_path: str, scale: int = 2) -> bool:
    """
    Upscale image using high-quality LANCZOS resampling.

    This is a local operation that doesn't require API calls.

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

            # Use LANCZOS for high-quality upscaling
            upscaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Save with high quality
            upscaled.save(output_path, "JPEG", quality=98)

            file_size = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"    Upscaled: {orig_width}x{orig_height} -> {new_width}x{new_height} ({file_size:.2f} MB)")

            return True

    except Exception as e:
        print(f"    Error upscaling: {e}")
        return False


def process_storyboard(
    storyboard_path: str,
    output_dir: str,
    num_panels: int = None,
    scale: int = 2,
    remove_labels: bool = True
) -> list[str]:
    """
    Complete pipeline: extract panels from storyboard and upscale them.

    Args:
        storyboard_path: Path to storyboard image
        output_dir: Base output directory
        num_panels: Expected panel count (auto-detect if None)
        scale: Upscale factor for extracted panels
        remove_labels: Whether to remove text labels

    Returns:
        List of paths to upscaled panel images
    """
    # Create subdirectories
    extracted_dir = f"{output_dir}/extracted"
    upscaled_dir = f"{output_dir}/upscaled_{scale}x"

    # Step 1: Extract panels
    print("\n" + "=" * 50)
    print("STEP 1: EXTRACTING PANELS")
    print("=" * 50)

    extracted_paths = extract_panels(
        storyboard_path,
        extracted_dir,
        num_panels,
        remove_labels
    )

    if not extracted_paths:
        print("Error: No panels extracted")
        return []

    # Step 2: Upscale panels
    print("\n" + "=" * 50)
    print(f"STEP 2: UPSCALING PANELS ({scale}x)")
    print("=" * 50)

    Path(upscaled_dir).mkdir(parents=True, exist_ok=True)
    upscaled_paths = []

    for panel_path in extracted_paths:
        panel_name = Path(panel_path).name
        upscaled_path = f"{upscaled_dir}/{panel_name.replace('.jpg', f'_{scale}x.jpg')}"

        if upscale_image_lanczos(panel_path, upscaled_path, scale):
            upscaled_paths.append(upscaled_path)

        # Brief pause between operations
        time.sleep(0.1)

    print(f"\nUpscaled {len(upscaled_paths)} panels to {upscaled_dir}")

    # Summary
    print("\n" + "=" * 50)
    print("PROCESSING COMPLETE")
    print("=" * 50)
    print(f"  Extracted panels: {extracted_dir}")
    print(f"  Upscaled panels: {upscaled_dir}")
    print(f"  Total panels: {len(upscaled_paths)}")

    return upscaled_paths


def main():
    parser = argparse.ArgumentParser(
        description="Extract and upscale panels from storyboard images"
    )
    parser.add_argument(
        "storyboard",
        help="Path to storyboard image"
    )
    parser.add_argument(
        "--panels",
        type=int,
        choices=[4, 6, 8],
        help="Number of panels (4, 6, or 8) - auto-detect if not specified"
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=2,
        help="Upscale factor (default: 2)"
    )
    parser.add_argument(
        "--output",
        help="Output directory (default: auto-generated)"
    )
    parser.add_argument(
        "--keep-labels",
        action="store_true",
        help="Keep text labels in panels (default: remove them)"
    )

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.storyboard):
        print(f"Error: Storyboard not found: {args.storyboard}")
        sys.exit(1)

    # Generate output directory if not specified
    output_dir = args.output
    if not output_dir:
        input_path = Path(args.storyboard)
        output_dir = f"{input_path.parent}/{input_path.stem}_panels"

    # Process storyboard
    upscaled_paths = process_storyboard(
        args.storyboard,
        output_dir,
        args.panels,
        args.scale,
        not args.keep_labels
    )

    sys.exit(0 if upscaled_paths else 1)


if __name__ == "__main__":
    main()
