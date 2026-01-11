# Image Upscaling Guide - Preserving Original Content

## The Problem

Many AI upscaling services (including some API-based ones) use **generative** AI that tries to "enhance" or "reimagine" the image rather than simply upscaling it. This results in:

- Changed character faces and expressions
- Altered composition and layout
- Added or removed elements
- Different colors and lighting
- Completely different images in extreme cases

**This is unacceptable for our use case** where we need the exact same image at higher resolution.

## The Solution

Use upscaling methods that are designed to **preserve content exactly**:

### 1. LANCZOS Resampling (Recommended - Always Available)

Pure mathematical interpolation that **cannot** alter content.

```bash
python scripts/upscale_preserve_exact.py image.jpg --method lanczos --scale 4
```

**Pros:**
- 100% content preservation guaranteed
- Fast
- Always available (built into Pillow)
- No API calls needed

**Cons:**
- May appear slightly softer than AI upscaling
- No "enhancement" (but that's a feature, not a bug!)

### 2. Enhanced LANCZOS (Recommended for Production)

LANCZOS plus subtle sharpening to compensate for softness.

```bash
python scripts/upscale_preserve_exact.py image.jpg --method enhanced --scale 4
```

**Pros:**
- 100% content preservation
- Sharper than pure LANCZOS
- Fast and offline

**Cons:**
- Slightly more processing time

### 3. Real-ESRGAN (Best Quality - If Installed)

Neural network specifically designed for **faithful** upscaling (not regeneration).

```bash
# Install Real-ESRGAN first (see below)
python scripts/upscale_preserve_exact.py image.jpg --method realesrgan --scale 4
```

**Pros:**
- Best visual quality
- Designed to preserve content
- Adds realistic detail without hallucinating

**Cons:**
- Requires separate installation
- Slower than LANCZOS
- Needs GPU for best performance

## Installing Real-ESRGAN

### macOS/Linux:
```bash
# Download from https://github.com/xinntao/Real-ESRGAN/releases
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip
unzip realesrgan-ncnn-vulkan-*.zip
chmod +x realesrgan-ncnn-vulkan
sudo mv realesrgan-ncnn-vulkan /usr/local/bin/
```

### Windows:
Download from releases and add to PATH.

## What NOT to Use

Avoid these services for content-critical upscaling:

- **Generative AI upscalers** (DALL-E, Stable Diffusion based)
- **"Creative" upscaling modes** (Recraft Creative, etc.)
- **Services that "enhance" or "improve" images**
- **Any service that requires a text prompt for upscaling**

These will regenerate your image rather than upscale it.

## Quick Comparison

| Method | Content Preservation | Quality | Speed | Availability |
|--------|---------------------|---------|-------|--------------|
| LANCZOS | 100% | Good | Fast | Always |
| Enhanced LANCZOS | 100% | Better | Fast | Always |
| Real-ESRGAN | 99%+ | Best | Medium | Install required |
| Recraft Crisp | ~95% | Good | Slow | API |
| Generative AI | 0-50% | N/A | Slow | API |

## Usage Examples

### Single Image:
```bash
# Auto-select best available method
python scripts/upscale_preserve_exact.py scene1.jpg -s 4

# Force LANCZOS (guaranteed preservation)
python scripts/upscale_preserve_exact.py scene1.jpg -m lanczos -s 4

# With custom output path
python scripts/upscale_preserve_exact.py scene1.jpg -o upscaled/scene1_4x.jpg -s 4
```

### Batch Processing:
```bash
# Upscale all images in a directory
python scripts/upscale_preserve_exact.py ./scenes/ --batch -s 4

# Output to specific directory
python scripts/upscale_preserve_exact.py ./scenes/ -o ./upscaled_scenes/ --batch
```

## Verifying Preservation

After upscaling, verify content is preserved:

1. **Visual comparison** - Side-by-side with original
2. **Structural similarity** - Should be >0.99 SSIM
3. **Color histogram** - Should be nearly identical

```python
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import numpy as np

original = np.array(Image.open("original.jpg"))
upscaled = np.array(Image.open("upscaled.jpg").resize(original.shape[:2][::-1]))

similarity = ssim(original, upscaled, multichannel=True)
print(f"SSIM: {similarity}")  # Should be > 0.99
```

## Troubleshooting

### Upscaled image looks different from original
- You're using a generative upscaler
- Switch to `--method lanczos` for guaranteed preservation

### Upscaled image is too soft/blurry
- Use `--method enhanced` for sharpening
- Or install Real-ESRGAN for better detail

### File size is very large
- Use JPEG output with quality setting
- Large files are normal for 4x upscaling

### Colors look slightly different
- Check color profile handling
- Use PNG for lossless color preservation

## Summary

**For Pokemon AI Video Generator, always use:**

```bash
python scripts/upscale_preserve_exact.py image.jpg --method enhanced --scale 4
```

This guarantees your character faces, expressions, and scene composition remain exactly as generated, just at higher resolution.
