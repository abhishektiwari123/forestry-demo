# Kling AI Testing Instructions

## Current Status

✅ **Kling AI 2.6 support ready:**
- Comprehensive prompting guide created: `KLING_AI_PROMPTING_GUIDE.md`
- Comparison test script ready: `scripts/test_kling_vs_seedance.py`
- API integration complete

⚠️ **Upload services temporarily unavailable** (imgcdn.dev and catbox.moe)

---

## When Upload Services Recover

Run the comparison test to evaluate quality:

```bash
python3 scripts/test_kling_vs_seedance.py
```

This will:
1. Generate Segment 1 with **Kling AI 2.6** (5s, motion-focused)
2. Generate Segment 1 with **Seedance 1.5 Pro** (8s, start+end frame)
3. Save both for side-by-side comparison

**Output:**
- `charizard/battle_assets/videos/seg01_kling_test.mp4`
- `charizard/battle_assets/videos/seg01_seedance_test.mp4`

---

## Alternative: Manual Kling Test via KIE.ai Dashboard

While upload services recover, test Kling directly:

### Option 1: Test via KIE.ai Web Interface
1. Visit https://kie.ai/
2. Select "Kling 2.6 Image-to-Video"
3. Upload: `charizard/battle_assets/frame_pairs/seg01_valley_patrol_start.jpg`
4. Use this optimized Kling prompt:
   ```
   Charizard soaring majestically over volcanic peaks,
   wings beating rhythmically, flying closer toward camera,
   cinematic aerial tracking shot following patrol flight
   ```
5. Duration: 5 seconds
6. Compare quality with existing `seg01_video.mp4` (Seedance version)

## ✅ What's Been Created:

### 1. **Comprehensive Kling AI Prompting Guide**
- `charizard/KLING_AI_PROMPTING_GUIDE.md`
- **Based on 2026 research** from top sources:
  - [Kling AI Prompt Guide - Leonardo.AI](https://leonardo.ai/news/kling-ai-prompts/)
  - [Kling 2.6 Pro Guide - fal.ai](https://fal.ai/learn/devs/kling-2-6-pro-prompt-guide)
  - [Kling 2.1 Guide - ImagineArt](https://www.imagine.art/blogs/kling-2-1-prompting-guide)
  - [Text-to-Video Guide - RunDiffusion](https://learn.rundiffusion.com/text-to-video-prompt-guide-how-to-prompt-with-kling/)
  - [Hidden Secrets - InVideo](https://invideo.io/blog/hidden-secrets-of-kling-ai/)

**Key Kling AI Insights:**
- ✅ **Best for**: Camera motion, character physics, narrative-driven shots
- ✅ **Prompt style**: Motion-focused (30-50 words optimal)
- ✅ **Image-to-Video**: Only describe movement, not the scene
- ✅ **Camera work**: Name specific moves ("slow push-in", "drone follow")

### 2. **Comparison Test Script**
- `scripts/test_kling_vs_seedance.py`
- Automated side-by-side comparison
- Tests same segment with both models
- Evaluation criteria: motion smoothness, camera work, physics

### 3. **Kling vs Seedance Decision Matrix**

| Scene Type | Recommended Model | Why |
|------------|-------------------|-----|
| Aerial motion (Seg 1, 10, 15) | **Kling AI** | Better camera tracking, smooth flight |
| Attack animations (Seg 5, 9, 14) | **Test both** | Kling for camera, Seedance for transitions |
| Rapid movement (Seg 6, 11, 12) | **Kling AI** | Superior character physics |
| Emotional moments (Seg 16, 18) | **Seedance** | Better start+end state control |
| Combat impacts (Seg 7, 8) | **Test both** | Compare distortion handling |

---

## Next Steps

1. **Wait for upload services to recover**
2. **Run automated test**: `python3 scripts/test_kling_vs_seedance.py`
3. **Compare quality** using evaluation criteria
4. **Decide per segment**: Which model works best for each scene type
5. **Update batch script** with chosen model for each segment
6. **Regenerate if needed**: Re-run segments with preferred model

---

## Cost Consideration

- **Kling AI**: 5s or 10s duration
- **Seedance**: Fixed 8s duration
- **Strategy**: Test key segments first, evaluate ROI before full batch

---

## Documentation Complete

All Kling AI integration is ready. Test when upload services recover.