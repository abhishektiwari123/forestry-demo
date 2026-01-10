# Kling AI 2.6 Prompting Guide for Pokemon Battle Videos

## Overview

Kling AI excels at **camera motion and character physics** with narrative intent. This guide focuses on Image-to-Video generation for our Pokemon battle documentary.

---

## Image-to-Video Prompting Structure

### Core Principle
**For Image-to-Video, you only need TWO elements:**
1. **Subject** - Name the character/object to animate
2. **Movement** - Describe what happens to the subject

❌ **Don't describe the scene** - it's already in the image!

✅ **Do describe motion and camera work**

### Optimal Prompt Length
- **Best**: 30-50 words
- **Max**: 2500 characters
- Keep it concise and clear

---

## Essential Prompt Elements

### 1. Subject Identification
Name the primary subject clearly:
- ✅ "Charizard"
- ✅ "Dragonite with green wings"
- ❌ "The fire Pokemon" (too vague)

### 2. Movement Description
Be specific about motion:
- ✅ "wings beating powerfully, ascending skyward"
- ✅ "spinning rapidly while gripping opponent"
- ❌ "moves around" (too vague)

### 3. Camera Movement (Optional but Powerful)
Specify camera work for narrative impact:
- "slow push-in" - creates intimacy
- "drone follow" - epic tracking
- "lateral track" - reveals environment
- "camera circles around" - dramatic reveal
- "low angle tilt up" - heroic shot

---

## Best Practices for Pokemon Battle Videos

### ✅ DO:

1. **Be Specific About Physics**
   - "wings flapping powerfully against resistance"
   - "tail flame intensifying from orange to blue"
   - "electricity crackling violently across body"

2. **Name Camera Moves**
   - "Camera slowly tracks right maintaining focus"
   - "Cinematic slow-motion during impact"
   - "Wide shot pulling back to reveal scale"

3. **Focus on Single Main Action**
   - One primary movement per prompt
   - Additional subtle movements okay (wind, flames)

4. **Use Sensory Details**
   - "Heat distortion rippling through air"
   - "Dust explosion from impact crater"
   - "Storm energy crackling intensely"

5. **Describe Motion Sequentially**
   - "Charizard inhales deeply, then unleashes Flamethrower"
   - "Dragonite dodges left, then counters with Thunder Punch"

### ❌ DON'T:

1. **Avoid Vague Adjectives**
   - ❌ "beautiful", "cool", "awesome"
   - ✅ Use descriptive visuals instead

2. **Don't Describe What's Already Visible**
   - ❌ "orange body, teal wings, volcanic valley"
   - ✅ Only describe NEW motion/changes

3. **Avoid Complex Multi-Step Physics**
   - ❌ "360-degree rotation while zooming and spinning"
   - ✅ "rotating steadily while ascending"

4. **Don't Use Specific Numbers**
   - ❌ "5 wing beats"
   - ✅ "wings beating rhythmically"

5. **Avoid Style Mixing**
   - ❌ "golden hour studio lighting cyberpunk"
   - ✅ Pick ONE consistent style

---

## Prompt Formula for Battle Scenes

```
[Subject] + [Primary Action] + [Camera Movement] + [Atmospheric Detail]
```

### Examples:

**Attack Scene:**
```
Charizard unleashes massive Flamethrower from open jaws,
intense flames erupting forward with heat distortion,
camera tracks action from side angle
```

**Dodge Scene:**
```
Dragonite barrel-rolls rapidly to evade flames,
wings tucking aerodynamically then spreading wide,
fast tracking shot following the evasive maneuver
```

**Impact Scene:**
```
Charizard struck by Thunder Punch,
electricity crackling violently across body,
camera captures reeling motion from dramatic low angle
```

**Aerial Combat:**
```
Both dragons circle each other mid-air,
wings beating powerfully, sizing up opponent,
camera slowly orbits maintaining both in frame
```

---

## Kling vs Seedance Comparison

| Feature | Kling AI 2.6 | Seedance 1.5 Pro |
|---------|--------------|------------------|
| **Best For** | Camera motion, physics | Start+End frame interpolation |
| **Prompt Style** | Motion-focused | Full scene description |
| **Duration** | 5s or 10s | 8s |
| **Strength** | Character animation | Smooth transitions |
| **Technique** | Single image + motion | Two images (start + end) |

---

## Advanced Tips

### Controlling Unwanted Distortion
If video shows warping:
1. Reduce prompt complexity
2. Add "stable camera movement"
3. Specify "no distortion"
4. Break complex moves into simpler instructions

### Enhancing Consistency
1. Use style-specific terms: "cinematic action", "anime battle"
2. Maintain consistent lighting throughout prompt
3. Specify camera distance: "wide shot", "close-up", "medium shot"

### Narrative-Driven Camera Work
Connect camera movements to story beats:
- **Challenge**: "Dragonite descends from storm, low angle emphasizing power"
- **Struggle**: "Charizard reeling from hit, handheld shaky cam conveys chaos"
- **Victory**: "Charizard lands peacefully, aerial pullback reveals scale"

---

## Image Requirements

Before uploading to Kling:
- ✅ High resolution (1080p or higher)
- ✅ Clear and well-composed
- ✅ Free of text overlays/watermarks
- ✅ Properly lit with good contrast
- ✅ Single primary subject

---

## Testing Workflow

1. **Start with 5-second test** - Check quality and style
2. **Adjust prompt** - Refine based on results
3. **Scale to 10 seconds** - Once satisfied with motion
4. **Compare with Seedance** - Evaluate which technique works best for each scene

---

## Example Prompts for Our Battle Story

### Segment 1 - Valley Patrol
```
Charizard soaring majestically over volcanic peaks,
wings beating rhythmically, flying closer toward camera,
cinematic aerial tracking shot following patrol flight
```

### Segment 4 - Battle Challenge
```
Charizard roaring powerfully with battle cry,
jaws opening wide, wing membranes flaring dramatically,
tail flame intensifying from orange to blue,
dramatic close-up pulling back to reveal stance
```

### Segment 5 - Flamethrower Attack
```
Charizard unleashing massive Flamethrower,
enormous stream of flames erupting violently forward,
wings bracing from recoil force, heat rippling through air,
side angle capturing devastating blast intensity
```

### Segment 13 - Seismic Toss
```
Charizard spinning rapidly while ascending skyward,
holding Dragonite firmly, spiraling upward violently,
building massive momentum for legendary throw,
spiraling camera follows ascent dramatically
```

---

## Sources & Further Reading

- [Kling AI Prompt Guide - Leonardo.AI](https://leonardo.ai/news/kling-ai-prompts/)
- [Kling 2.6 Pro Prompt Guide - fal.ai](https://fal.ai/learn/devs/kling-2-6-pro-prompt-guide)
- [Kling 2.1 Video Generation Guide - ImagineArt](https://www.imagine.art/blogs/kling-2-1-prompting-guide)
- [Text-to-Video Prompt Guide - RunDiffusion](https://learn.rundiffusion.com/text-to-video-prompt-guide-how-to-prompt-with-kling/)
- [Hidden Secrets of Kling AI - InVideo](https://invideo.io/blog/hidden-secrets-of-kling-ai/)

---

## Next Steps

1. Review this guide before creating prompts
2. Use `test_kling_vs_seedance.py` to compare quality
3. Optimize prompts based on results
4. Choose best technique for each battle segment
