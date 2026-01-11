#!/usr/bin/env python3
"""
Create composite images by layering multiple assets.

Usage:
    python create_composite.py --background bg.png --foreground char.png --output composite.png
"""

import argparse
import sys
from pathlib import Path

from PIL import Image


def create_composite(
    background_path: str,
    foreground_path: str,
    output_path: str,
    fg_position: tuple[int, int] = None,
    fg_scale: float = 1.0,
    opacity: float = 1.0
) -> bool:
    """
    Create a composite image by layering foreground over background.

    Args:
        background_path: Path to background image
        foreground_path: Path to foreground image (should have transparency)
        output_path: Where to save the composite
        fg_position: (x, y) position for foreground, defaults to center
        fg_scale: Scale factor for foreground (1.0 = original size)
        opacity: Opacity of foreground (0.0 - 1.0)

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Creating composite...")
        print(f"  Background: {background_path}")
        print(f"  Foreground: {foreground_path}")

        # Load images
        background = Image.open(background_path).convert("RGBA")
        foreground = Image.open(foreground_path).convert("RGBA")

        # Scale foreground if needed
        if fg_scale != 1.0:
            new_size = (
                int(foreground.width * fg_scale),
                int(foreground.height * fg_scale)
            )
            foreground = foreground.resize(new_size, Image.Resampling.LANCZOS)
            print(f"  Scaled foreground to {new_size}")

        # Apply opacity if needed
        if opacity < 1.0:
            alpha = foreground.split()[3]
            alpha = alpha.point(lambda x: int(x * opacity))
            foreground.putalpha(alpha)
            print(f"  Applied opacity: {opacity}")

        # Calculate position (center if not specified)
        if fg_position is None:
            fg_position = (
                (background.width - foreground.width) // 2,
                (background.height - foreground.height) // 2
            )
        print(f"  Position: {fg_position}")

        # Create composite
        composite = background.copy()
        composite.paste(foreground, fg_position, foreground)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save as PNG to preserve quality
        composite.save(output_path, "PNG")
        print(f"  Saved to: {output_path}")

        # Also save a JPEG version for smaller file size if needed
        jpeg_path = output_path.replace(".png", ".jpg")
        if jpeg_path != output_path:
            composite_rgb = composite.convert("RGB")
            composite_rgb.save(jpeg_path, "JPEG", quality=95)

        print("Success!")
        return True

    except Exception as e:
        print(f"Error creating composite: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Create composite images by layering assets"
    )
    parser.add_argument(
        "--background",
        required=True,
        help="Path to background image"
    )
    parser.add_argument(
        "--foreground",
        required=True,
        help="Path to foreground image (should have transparency)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for composite image"
    )
    parser.add_argument(
        "--position",
        type=str,
        default=None,
        help="Foreground position as 'x,y' (default: center)"
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Scale factor for foreground (default: 1.0)"
    )
    parser.add_argument(
        "--opacity",
        type=float,
        default=1.0,
        help="Opacity of foreground 0.0-1.0 (default: 1.0)"
    )

    args = parser.parse_args()

    # Parse position if provided
    position = None
    if args.position:
        try:
            x, y = args.position.split(",")
            position = (int(x.strip()), int(y.strip()))
        except ValueError:
            print(f"Error: Invalid position format '{args.position}'. Use 'x,y'")
            sys.exit(1)

    success = create_composite(
        args.background,
        args.foreground,
        args.output,
        fg_position=position,
        fg_scale=args.scale,
        opacity=args.opacity
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
