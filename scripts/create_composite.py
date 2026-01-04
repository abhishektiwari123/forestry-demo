#!/usr/bin/env python3
"""
Create composite images by layering multiple assets.

Usage:
    python create_composite.py --background "bg.jpg" --foreground "char.png" --position 960,800 --scale 0.6 --output "composite.jpg"
"""

import argparse
import sys
from pathlib import Path
from PIL import Image

def create_composite(
    background_path: str,
    foreground_path: str,
    position: tuple,
    scale: float,
    output_path: str,
    target_size: tuple = (1920, 1080)
) -> bool:
    """
    Composite foreground image onto background.

    Args:
        background_path: Path to background image
        foreground_path: Path to foreground image
        position: (x, y) position for foreground center
        scale: Scale factor for foreground (0.0-1.0+)
        output_path: Where to save composite
        target_size: Target resolution (width, height)

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🖼️  Creating composite...")
        print(f"   Background: {background_path}")
        print(f"   Foreground: {foreground_path}")
        print(f"   Position: {position}")
        print(f"   Scale: {scale}")

        # Load background
        background = Image.open(background_path).convert("RGBA")

        # Resize background to target size
        background = background.resize(target_size, Image.Resampling.LANCZOS)

        # Load foreground
        foreground = Image.open(foreground_path).convert("RGBA")

        # Scale foreground
        fg_width = int(foreground.width * scale)
        fg_height = int(foreground.height * scale)
        foreground = foreground.resize((fg_width, fg_height), Image.Resampling.LANCZOS)

        # Calculate paste position (position is center point)
        x, y = position
        paste_x = x - (fg_width // 2)
        paste_y = y - (fg_height // 2)

        # Create composite
        composite = background.copy()
        composite.paste(foreground, (paste_x, paste_y), foreground)

        # Convert to RGB for JPEG output
        if output_path.lower().endswith(('.jpg', '.jpeg')):
            composite = composite.convert("RGB")

        # Save composite
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        composite.save(output_path, quality=95)

        print(f"✅ Composite saved to: {output_path}")
        print(f"   Resolution: {target_size[0]}x{target_size[1]}")
        return True

    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating composite: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Create composite images by layering assets"
    )
    parser.add_argument(
        "--background",
        required=True,
        help="Background image path"
    )
    parser.add_argument(
        "--foreground",
        required=True,
        help="Foreground image path (supports transparency)"
    )
    parser.add_argument(
        "--position",
        required=True,
        help="Position as 'x,y' (center point of foreground, e.g., '960,800')"
    )
    parser.add_argument(
        "--scale",
        type=float,
        required=True,
        help="Scale factor for foreground (e.g., 0.6 for 60%%)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output composite path"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Target width (default: 1920)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Target height (default: 1080)"
    )

    args = parser.parse_args()

    # Parse position
    try:
        x, y = map(int, args.position.split(','))
        position = (x, y)
    except ValueError:
        print("❌ Error: Position must be in format 'x,y' (e.g., '960,540')")
        sys.exit(1)

    success = create_composite(
        args.background,
        args.foreground,
        position,
        args.scale,
        args.output,
        target_size=(args.width, args.height)
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
