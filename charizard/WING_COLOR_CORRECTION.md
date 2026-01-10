# Charizard Wing Color Correction

## Issue Identified

**Current prompts:** "teal wing membranes" or "teal turquoise wing membranes"

**Problem:** This is ambiguous and AI generates fully teal wings, which is incorrect.

## Canon Charizard Wing Colors

According to official Pokemon design:

```
Charizard Wing Structure:
├── Upper Surface (top of wing): ORANGE (#F08030) - matches body
└── Underside/Membrane (bottom of wing): TEAL TURQUOISE (#58A8B8)
```

**Key Point:** Wings should be **orange on top, teal underneath**

## Visual Reference

When Charizard flies:
- **Looking from above:** Wings appear ORANGE
- **Looking from below:** Wing membranes appear TEAL
- **From side:** Orange upper surface with teal underside visible at edges

## Corrected Prompt Format

### Old (Incorrect):
```
"Charizard with orange body and teal wing membranes"
```
**Problem:** AI may interpret entire wing as teal

### New (Correct):
```
"Charizard with vibrant orange body (#F08030 scales), wings with
orange upper surface matching body color and teal turquoise (#58A8B8)
underside membranes"
```

## All Segment Prompts Updated

### Simple Format (for most prompts):
```
"Charizard (orange body, wings: orange tops with teal undersides)"
```

### Detailed Format (for key visual segments):
```
"Charizard with vibrant orange body, wings displaying orange upper
surface matching body scales and distinctive teal turquoise underside
membranes visible when spread"
```

## Why This Matters

**Visual Consistency:**
- ✅ Canon-accurate appearance
- ✅ More natural color flow (body → wing tops)
- ✅ Teal acts as accent color, not primary
- ✅ Better lighting (orange catches sunlight, teal in shadows)

**Previous Error Impact:**
- ❌ Wings looked disconnected from body
- ❌ Too much teal (should be accent, not dominant)
- ❌ Unnatural appearance in aerial shots

## Application to All 18 Segments

All prompts updated with correct wing description:

**Solo Charizard scenes:**
- "orange body with wings: orange tops, teal undersides"

**Dual scenes (with Dragonite):**
- "smaller Charizard (orange body, wings: orange upper surface, teal underside)"
- "larger Dragonite (orange body, green wings)"

## Technical Specification

| Wing Part | Color | Hex Code | Description |
|-----------|-------|----------|-------------|
| **Upper Surface** | Orange | #F08030 | Matches body scales, catches light |
| **Underside/Membrane** | Teal Turquoise | #58A8B8 | Visible from below, translucent |
| **Wing Frame/Bones** | Orange | #F08030 | Structural elements match body |

## Updated Segments

All 18 segments require this correction:
- Segments 1-18: Updated wing color specification
- Size-corrected segments (3, 6, 12, 13, 14): Include both size AND color fix
- Single-subject segments: Simpler wing description
- Dual-subject segments: Maintain clarity with detailed colors

## Next Steps

1. ✅ Update KLING_PROMPTS in batch_generate_videos_kling.py
2. ✅ Update SIZE_CORRECTED_PROMPTS in regenerate script
3. 🔄 Regenerate all frame pairs with correct wing colors
4. 🔄 Generate all 18 videos with Kling AI using corrected images
