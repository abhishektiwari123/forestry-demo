#!/usr/bin/env python3
"""
Upscale extracted scene images to full resolution for better video quality.
"""

import os
from PIL import Image


def upscale_image(input_path: str, output_path: str, target_width: int = 1920, target_height: int = 1080):
    """
    Upscale image to target resolution using high-quality resampling.

    Default target: 1920x1080 (Full HD 16:9)
    """
    print(f"🔍 Upscaling: {os.path.basename(input_path)}")

    img = Image.open(input_path)
    original_size = img.size
    print(f"   Original: {original_size[0]}x{original_size[1]}")

    # Use LANCZOS (high-quality) resampling
    upscaled = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Save with high quality
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    upscaled.save(output_path, "JPEG", quality=95)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   Upscaled: {target_width}x{target_height}")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   ✅ Saved: {output_path}\n")

    return output_path


def upscale_all_scenes(input_dir: str, output_dir: str):
    """Upscale all scene images in directory."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║              UPSCALE SCENE IMAGES TO FULL RESOLUTION               ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    scene_files = [f for f in os.listdir(input_dir) if f.endswith('.jpg')]

    if not scene_files:
        print(f"❌ No scene images found in {input_dir}")
        return []

    print(f"Found {len(scene_files)} scene images to upscale\n")

    upscaled_paths = []
    for scene_file in sorted(scene_files):
        input_path = os.path.join(input_dir, scene_file)
        output_path = os.path.join(output_dir, scene_file.replace('.jpg', '_upscaled.jpg'))

        upscaled_path = upscale_image(input_path, output_path)
        upscaled_paths.append(upscaled_path)

    print(f"✅ Upscaled {len(upscaled_paths)} images to Full HD (1920x1080)")
    return upscaled_paths


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        input_dir = "charizard/battle_assets/storyboard/scenes"
        output_dir = "charizard/battle_assets/upscaled_scenes"

    upscaled = upscale_all_scenes(input_dir, output_dir)

    print(f"\n📁 Upscaled images saved to: {output_dir}")
    print(f"   Use these for video generation to get full resolution")
