# KLING REFERENCE IMAGE CONTINUITY STRATEGY
## Maintaining Seamless Storyboard Flow with Multi-Image References

**Purpose:** Document Kling AI's capabilities for using previous video frames as references in subsequent generations to maintain visual continuity across battle sequence.

---

## KEY KLING FEATURES FOR CONTINUITY

### 1. MULTI-IMAGE REFERENCE (Kling AI 1.6+)
**Feature:** Upload multiple reference images of the same subject for consistent style/appearance
**Capability:** AI analyzes and integrates diverse subjects from multiple images
**Result:** Composite videos with seamless, professional-quality visual consistency

**Source:** [Kuaishou Kling AI Multi-Image Reference Feature](https://ir.kuaishou.com/news-releases/news-release-details/kuaishou-kling-ai-unveils-multi-image-reference-feature-further/)

### 2. ELEMENTS FEATURE (Kling 2.6 Pro)
**Feature:** Upload character/prop reference images to "Element Library"
**Best Practice:** Provide 2-4 high-quality reference images from multiple angles
**Warning:** More than 4 images can confuse model about priorities
**Result:** Model "remembers" character features like human director across shots/angles/lighting

**How to Use:**
- Upload hero character reference images showing key features
- Include multiple angles (front, side, 3/4 view)
- Model maintains wardrobe, hair, face shape, and identity throughout

**Source:** [Kling 2.6 Pro Prompt Guide](https://fal.ai/learn/devs/kling-2-6-pro-prompt-guide)

### 3. KLING O1 REFERENCE (Up to 7 Simultaneous Inputs)
**Feature:** Advanced reference conditioning with up to 7 simultaneous reference images
**Capability:** Stable character/object identity across complex compositions
**Use Cases:**
- Narrative sequences requiring character continuity
- Product demonstrations with consistent styling
- Complex scene transitions where object identity must persist frame-to-frame

**@ Mention System:**
```
"Put the helmet from @Image1 onto the astronaut in @Image2"
```
Model understands geometry and fuses elements logically.

**Source:** [Kling O1 Reference Image to Video](https://fal.ai/models/fal-ai/kling-video/o1/reference-to-video)

### 4. START & END FRAME CONTROL
**Feature:** Define both start frame and end frame for video generation
**Result:** Smooth transformations, controlled pans, seamless loops with ~100% accuracy
**Benefit:** Replaces AI motion randomness with calculated, storyboarded transitions

**Applications for Battle Sequence:**
- **Staging:** Position Pokemon at specific locations for continuity
- **State Transitions:** Animate from one state to another (fresh → damaged)
- **Shot Continuity:** Ensure ending position of Panel N matches starting position of Panel N+1

**Source:** [Kling Start & End Frames Guide](https://higgsfield.ai/blog/Kling-Start-End-Frames)

---

## IMPLEMENTATION FOR POKEMON BATTLE SEQUENCE

### WORKFLOW FOR SEAMLESS 6-PANEL STORYBOARD

#### Phase 1: Extract Final Frames as References
```bash
# Generate Panel 1 video
python3 scripts/test_video_from_panel.py panel_01_enhanced.jpg --duration 5

# Extract final frame from Panel 1 video
ffmpeg -sseof -1 -i panel_01_video.mp4 -vframes 1 panel_01_final_frame.jpg

# Use final frame as START frame reference for Panel 2
```

#### Phase 2: Multi-Reference Generation Strategy

**Panel 1 Generation:**
- Input: Enhanced storyboard Panel 1 (photorealistic)
- References: None (first panel)
- Output: Panel 1 video

**Panel 2 Generation (Impact):**
- Input: Enhanced storyboard Panel 2
- References:
  - `panel_01_final_frame.jpg` (ending position of Charizard)
  - `charizard_character_ref.jpg` (consistent appearance)
  - `dragonite_character_ref.jpg` (consistent appearance)
- Prompt: "Starting from @panel_01_final_frame position, maintaining @charizard appearance..."
- Output: Panel 2 video with seamless transition

**Panel 3 Generation (Damage Aftermath):**
- Input: Enhanced storyboard Panel 3
- References:
  - `panel_02_final_frame.jpg` (Dragonite's damaged state)
  - `dragonite_burn_damage_ref.jpg` (consistent burn marks)
- Prompt: "Maintaining burn marks from @panel_02_final_frame, Dragonite with @dragonite_burn_damage..."
- Output: Panel 3 video with consistent damage

**And so on through Panel 6...**

---

## PROMPT TEXT STRATEGIES FOR CONTINUITY

### Strategy 1: Explicit Reference Mentions
```
"Character appearing EXACTLY as shown in reference image @Image1,
maintaining identical facial features, body proportions, and color palette..."
```

### Strategy 2: State Continuity Keywords
```
"CONTINUING FROM previous scene, character STILL showing [damage/emotion/position],
MAINTAINING [burn marks/expression/pose] from earlier, NO reset to fresh appearance..."
```

### Strategy 3: Cumulative Damage Tracking
```
Panel 2: "Dragonite taking hit, burn marks appearing on torso"
Panel 3: "Dragonite with SAME burn marks from previous scene STILL VISIBLE"
Panel 4: "Dragonite with burn marks CLEARLY VISIBLE getting angry"
Panel 5: "Dragonite charging with burn marks PROMINENTLY DISPLAYED"
Panel 6: "Dragonite attacking, burn marks MAINTAINED throughout"
```

### Strategy 4: Position Anchoring
```
"Charizard positioned at LEFT coordinates matching end position from previous panel,
Dragonite at RIGHT coordinates matching previous ending position..."
```

---

## TECHNICAL SPECIFICATIONS

### Kling 2.6 Pro Image-to-Video with References

**API Parameters:**
```json
{
  "model": "kling-2.6",
  "input": {
    "image_urls": ["main_panel_image.jpg"],
    "reference_images": [
      "previous_final_frame.jpg",
      "character_ref_1.jpg",
      "character_ref_2.jpg"
    ],
    "prompt": "Full prompt with continuity keywords...",
    "duration": 5,
    "mode": "pro"
  }
}
```

**Best Practices:**
1. **Reference Image Quality:** Use highest resolution available (2752x1536 or higher)
2. **Reference Count:** 2-4 references optimal (avoid overloading with >4)
3. **Reference Angles:** Include multiple viewing angles for 3D consistency
4. **Prompt Integration:** Explicitly mention reference images in prompt text
5. **State Keywords:** Use MAINTAINING, CONTINUING, STILL VISIBLE, CARRIES OVER

---

## BENEFITS FOR OUR BATTLE SEQUENCE

### 1. Visual Continuity
✅ Charizard appearance consistent across all 6 panels
✅ Dragonite appearance consistent with evolving damage states
✅ Burn marks persist from Panel 2 → Panel 6

### 2. Position Continuity
✅ Characters don't "teleport" between shots
✅ Smooth transitions from panel ending → next panel beginning
✅ Camera angles flow naturally

### 3. Expression Continuity
✅ Dragonite's expression evolution tracks across panels:
   - Panel 1: Concerned/bracing
   - Panel 2: Extreme pain (taking hit)
   - Panel 3: Exhausted/hurt
   - Panel 4: Building anger
   - Panel 5: Fierce vengeance
   - Panel 6: Satisfied revenge

### 4. Damage State Continuity
✅ Burn marks from Flamethrower persist throughout
✅ No "magical healing" between panels
✅ Battle consequences remain visible

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Character Reference Library
- [ ] Generate hero Charizard reference (front, side, 3/4 view)
- [ ] Generate hero Dragonite reference (front, side, 3/4 view)
- [ ] Generate Dragonite burn damage reference (post-Flamethrower state)

### Phase 2: Video Generation with Frame Extraction
- [ ] Generate Panel 1 video
- [ ] Extract final frame from Panel 1
- [ ] Generate Panel 2 video using Panel 1 final frame as reference
- [ ] Extract final frame from Panel 2
- [ ] Repeat through Panel 6

### Phase 3: Prompt Enhancement
- [ ] Update all prompts to include reference mentions
- [ ] Add state continuity keywords (MAINTAINING, STILL VISIBLE)
- [ ] Add position anchoring coordinates
- [ ] Add cumulative damage tracking language

### Phase 4: Validation
- [ ] Verify character appearance consistency across all panels
- [ ] Verify burn mark continuity (Panel 2-6)
- [ ] Verify expression evolution tracking
- [ ] Verify position/staging continuity

---

## EXPECTED RESULTS

**Before (No References):**
- Characters may look different between panels
- Damage states reset/disappear
- Expressions don't evolve logically
- Positions/staging inconsistent

**After (With References):**
- Characters look identical across all 6 panels
- Burn marks persist from Panel 2 through Panel 6
- Expression evolution flows naturally from concern → pain → anger → revenge
- Smooth positional transitions between panels
- Professional storyboard-quality continuity

---

## SOURCES & DOCUMENTATION

1. [Kuaishou Kling Multi-Image Reference Feature](https://ir.kuaishou.com/news-releases/news-release-details/kuaishou-kling-ai-unveils-multi-image-reference-feature-further/)
2. [Kling 2.6 Pro Prompt Guide](https://fal.ai/learn/devs/kling-2-6-pro-prompt-guide)
3. [Kling Video 2.6 Full Analysis](https://www.cometapi.com/kling-2-6-full-analysis-how-to-use-and-prompt/)
4. [Kling O1 Reference to Video](https://fal.ai/models/fal-ai/kling-video/o1/reference-to-video)
5. [Kling Start & End Frames Guide](https://higgsfield.ai/blog/Kling-Start-End-Frames)
6. [Kling O1 Complete Guide](https://higgsfield.ai/blog/Kling-01-is-Here-A-Complete-Guide-to-Video-Model)

---

**Last Updated:** 2026-01-11
**Status:** Ready for Implementation
**Next Step:** Update video generation script to support multi-image references
