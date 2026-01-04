# Seedance 1.5 Pro Prompting Guide for Character Consistency

*Based on comprehensive research of best practices for KIE.ai Seedance API (2026)*

---

## 🎯 Core Principles

### The Golden Rule
**Negative prompts DO NOT WORK with Seedance.** Always state what you DO want, never what you don't want.

### Optimal Prompt Structure

```
Prompt = [Subject] + [Motion] + [Background] + [Motion] + [Camera] + [Motion]
```

For **Image-to-Video** (our use case):
```
Prompt = [Character] + [Specific Motion] + [Intensity Adverbs] + [Camera Movement]
```

---

## 📋 Character Consistency Checklist

### ✅ Before Generation

1. **Use Consistent Character Descriptions**
   - Lock in specific color details: "orange body, blue wing membranes, cream belly"
   - Include distinctive features: "flame-tipped tail, sharp horns, fierce red eyes"
   - Match official Pokemon design specifications

2. **High-Quality Reference Images**
   - Clear, well-lit images where character is fully visible
   - Consistent angle/pose when possible across segments
   - Hosted on reliable CDN (imgcdn.dev recommended for permanence)

3. **Standardize Environmental Context**
   - Similar lighting conditions across prompts
   - Consistent time of day references
   - Matching atmospheric conditions

### ✅ During Prompting

1. **Minimize Static Descriptions**
   - Focus on MOTION, not appearance (image already shows appearance)
   - ❌ "Charizard with orange body and blue wings"
   - ✅ "wings flapping powerfully, generating downward thrust"

2. **Use Intensity Adverbs**
   - The model cannot infer motion intensity from static images
   - Always specify: fast, slow, gentle, violent, vigorous, subtle
   - ✅ "tail flame flickering gently in wind"
   - ✅ "wings beating powerfully creating dust clouds"

3. **Match Prompt to Source Image**
   - Don't contradict what's visible in the image
   - If image shows Charizard perched, don't prompt "flying through clouds"
   - Extend the scene naturally from the image state

---

## 🎬 Motion Control Best Practices

### Multiple Continuous Actions

List sequential movements in order:
```
"Charizard spreads wings wide, launches from rock with powerful downbeat,
ascends rapidly into sky gaining altitude"
```

### Camera Movement Keywords

**Natural Language Camera Control:**
- `surround` - Orbit around subject
- `aerial` - Bird's eye view, overhead
- `zoom` - Zoom in/out (specify direction)
- `pan` - Horizontal camera movement
- `follow` - Track subject motion
- `handheld` - Shaky, documentary feel
- `dolly` - Smooth forward/backward movement
- `tilt` - Vertical camera angle change

**CRITICAL:** Set `fixed_lens: false` when using ANY camera movement prompts!

### Multi-Shot Sequences

When creating connected segments, use transition keywords:
- "Cut to..."
- "Camera cut to..."
- "Camera switching to..."
- "Shot switch revealing..."

After transition word, describe the NEW scene context.

---

## 🎨 Pokemon Documentary Specific Techniques

### Nature Documentary Camera Styles

Runway (and by extension Seedance) trained heavily on nature documentary footage, making it excellent for Pokemon content.

**Effective documentary prompts:**
```
"close-up tracking shot following Charizard head as it scans horizon,
shallow depth of field, wildlife documentary style"

"wide establishing shot, Charizard perched atop volcanic peak silhouetted
against sunset, slow zoom in revealing detail, cinematic composition"

"ground-level POV as Charizard swoops overhead casting shadow,
camera tilts up following flight path, dramatic low angle"
```

### Character Consistency Across Shots

Based on research, here's the hierarchy for maintaining consistency:

**1. Image Quality (Most Important)**
   - Use same base character model/image when possible
   - Consistent lighting angle
   - Similar distance/scale

**2. Prompt Consistency**
   - Use identical color descriptors: "blue wing membranes" every time
   - Maintain same distinctive features: "flame-tipped tail"
   - Don't vary terminology (don't switch between "wings" and "appendages")

**3. Technical Parameters**
   - Keep `aspect_ratio` consistent (16:9 for all segments)
   - Same `resolution` (720p recommended)
   - Same `duration` (8 seconds optimal)

**4. Environmental Context**
   - Maintain time of day consistency within scenes
   - Similar atmospheric conditions (don't jump from foggy to clear)
   - Consistent environmental scale

---

## ⚙️ KIE.ai API Parameters

### Essential Parameters

```python
{
    "model": "bytedance/seedance-1.5-pro",
    "input": {
        "prompt": str,              # Your motion description
        "input_urls": [str],        # 0-2 image URLs (HTTPS required)
        "aspect_ratio": "16:9",     # Match across all segments
        "resolution": "720p",        # 720p or 1080p
        "duration": "8",            # Seconds (5-10 recommended)
        "fixed_lens": false,        # False = allow camera movement
        "generate_audio": false     # We have separate narration
    }
}
```

### Parameter Effects on Consistency

**`fixed_lens: true`**
- Locks camera position
- Subject can move, camera cannot
- Better for close-ups and stable shots
- Use when: Focus on character detail, facial expressions

**`fixed_lens: false`**
- Enables dynamic camera movement
- Essential for "pan", "zoom", "follow", "aerial" prompts
- Can introduce slight character variations
- Use when: Action shots, dramatic cinematography

**`duration`**
- 8 seconds is the sweet spot
- Shorter (<5s) = limited motion
- Longer (>10s) = potential drift/consistency issues

---

## 📝 Improved Prompt Templates

### Template 1: Action Shot
```
"[Character] [primary action with intensity adverb], [secondary motion detail],
[environmental interaction], [camera movement]"

Example:
"Charizard diving steeply with wings tucked tight, tail flame streaming behind
leaving orange trail, talons extending forward preparing to strike,
camera follows descent with dynamic tracking shot"
```

### Template 2: Breathing Photograph (Subtle Motion)
```
"[Character] [minimal motion with gentle adverbs], [atmospheric effects],
[background movement], [lighting details]"

Example:
"Charizard perched majestically on rock breathing slowly, tail flame flickering
gently casting warm glow, heat distortion rising subtly from scales,
volcanic steam drifting lazily in background"
```

### Template 3: Establishing Shot
```
"[wide/aerial descriptor] showing [character] [action], [environment details],
[atmospheric conditions], [camera movement]"

Example:
"Wide aerial shot revealing Charizard soaring high over volcanic mountain range,
wings spread wide gliding on thermal currents, lava flows glowing far below,
camera slowly panning right following flight path"
```

### Template 4: Close-Up Detail
```
"Close-up of [specific body part] [action with adverbs], [detail emphasis],
[lighting/mood]"

Example:
"Close-up of Charizard fierce face while flying, eyes scanning terrain below
with predatory focus, wind rippling scales subtly, dramatic side lighting
highlighting sharp features"
```

---

## 🔧 Troubleshooting Consistency Issues

### Problem: Wing Colors Vary (Blue vs Orange/Brown)

**Root Causes:**
1. Conflicting color terms in prompt
2. Source image has ambiguous lighting
3. Environmental lighting overriding character colors

**Solutions:**
- ✅ Explicitly state: "blue wing membranes" in EVERY prompt
- ✅ Use reference images with clear blue wing visibility
- ✅ Avoid dramatic backlighting that silhouettes character
- ✅ Add: "maintaining official Charizard coloration"

### Problem: Character Proportions Shift

**Root Causes:**
1. Different camera distances without scale reference
2. Varying image inputs with different perspectives
3. Contradicting size descriptors

**Solutions:**
- ✅ Include scale reference: "large Pokemon", "six-foot wingspan"
- ✅ Maintain consistent camera distance categories (wide/medium/close)
- ✅ Use same base image for similar shot types

### Problem: Missing Character in Output

**Root Causes:**
1. Prompt focused entirely on environment
2. Character too small in source image
3. Motion prompt doesn't reference character

**Solutions:**
- ✅ Always start prompt with character name and action
- ✅ Ensure character occupies significant portion of source image
- ✅ Add: "focus remains on Charizard throughout"

### Problem: Facial Features Inconsistent

**Root Causes:**
1. Low resolution source images
2. Face not clearly visible in reference
3. Varying lighting on face

**Solutions:**
- ✅ Use high-quality close-ups for facial shots
- ✅ Consistent lighting direction: "lit from left", "front-lit"
- ✅ Lock facial features: "fierce red eyes, sharp horns, pronounced fangs"

---

## 📊 Comparison: Our Current vs Improved Prompts

### ❌ Current Approach (Consistency Score: 4/10)

**Segment 3:**
```
Image: charizard_breathing_fire.jpg
Prompt: "Charizard opens jaws wide releasing concentrated stream of fire toward
sky, flame illuminates face and chest, heat distortion visible around blast,
powerful fire breath display"

Issues: No wing color specified, vague "powerful" (no intensity), no camera control
```

**Segment 6:**
```
Image: volcanic_landscape_aerial.jpg
Prompt: "Aerial view of Charizard soaring over volcanic landscape with wings
outstretched, gliding on thermal currents, lava flows visible below, effortless
flight through sky"

Issues: Character too small/unclear in landscape image, "effortless" is vague,
no specific color details, resulted in wrong wing colors
```

### ✅ Improved Approach (Estimated Score: 8-9/10)

**Segment 3:**
```
Image: charizard_breathing_fire.jpg (same)
Prompt: "Charizard jaws opening wide releasing intense concentrated blast of
orange flame upward toward sky, blue wing membranes partially visible catching
firelight, heat distortion rippling violently around flame column,
camera holds steady on powerful display, official Pokemon design colors maintained"

Improvements:
+ Specified blue wings explicitly
+ Added intensity: "intense", "violently"
+ Camera instruction: "holds steady"
+ Design consistency reminder
```

**Segment 6:**
```
Image: charizard_full_body_flying.jpg (better choice - character clearly visible)
Prompt: "Charizard with blue wing membranes spread wide soaring gracefully over
volcanic terrain, wings beating in slow powerful rhythm maintaining altitude,
orange body contrasting against dark volcanic rock below, aerial tracking shot
following from above and behind, smooth cinematic motion"

Improvements:
+ Changed to image with clear character
+ Explicit "blue wing membranes"
+ Motion intensity: "slow powerful rhythm"
+ Clear camera instruction: "aerial tracking shot following"
+ Color contrast specified
```

---

## 🎓 Advanced Techniques

### Multi-Shot Story Continuity

For 18-segment documentary, group into scenes:

**Scene 1: Dawn Ritual (Segments 1-4)**
- Maintain "early morning golden light" in all prompts
- Progress: establishing → detail → action → transition
- Lock wing colors from segment 1 and reference in each

**Scene 2: Hunt Sequence (Segments 5-12)**
- Consistent "midday harsh sunlight" lighting
- Progress motion intensity: gentle → building → climax
- Use "Cut to..." between perspective changes

**Scene 3: Sunset Return (Segments 13-18)**
- "Warm sunset orange glow" throughout
- Decreasing motion intensity: active → settling → rest
- Final segment uses "fade to evening shadows"

### Reference Chaining

Create visual continuity by ending each segment where the next begins:

```
Segment 5 end state: "Charizard launching upward from rock"
Segment 6 start state: "Charizard already airborne ascending rapidly"

Segment 12 end state: "Charizard breathing flame downward"
Segment 13 start state: "Charizard ascending away from strike point"
```

### Atmospheric Continuity

Maintain atmosphere across segments in same scene:
- Consistent particle effects: smoke, steam, heat shimmer
- Matching weather conditions
- Same wind intensity indicators

---

## 📚 Research Sources

This guide is based on comprehensive 2026 research:

- [Seedance 1.5 Pro Official Documentation](https://seed.bytedance.com/en/seedance1_5_pro)
- [WaveSpeed AI Seedance Prompting Guide](https://wavespeed.ai/landing/seedance)
- [KIE.ai Seedance API Documentation](https://docs.kie.ai/market/bytedance/seedance-1.5-pro)
- [Higgsfield Practical Creator Guide](https://higgsfield.ai/blog/Seedance-1.5-Pro-on-Higgsfield-A-Practical-Creator-Guide)
- [Motion Prompting Research](https://motion-prompting.github.io/)
- [Multi-Shot Character Consistency Research](https://arxiv.org/html/2412.07750v1)
- [Runway Gen-4 Character Consistency](https://venturebeat.com/ai/runways-gen-4-ai-solves-the-character-consistency-challenge-making-ai-filmmaking-actually-useful)
- [Pokemon AI Video Evaluation](https://pixelframe.design/evaluating-the-state-of-ai-video-generation-with-pokemon/)

---

## 🚀 Quick Start Checklist

Before generating your next batch:

- [ ] All source images hosted on permanent CDN (imgcdn.dev)
- [ ] Source images show character clearly with blue wings visible
- [ ] Created prompt template with locked color descriptors
- [ ] Added intensity adverbs to all motion descriptions
- [ ] Specified camera movement and set `fixed_lens: false`
- [ ] Grouped segments into scenes with consistent lighting
- [ ] Tested 2-3 segments with new approach before full batch
- [ ] Run `analyze_videos.py` to verify improvements

---

*Last Updated: 2026-01-04*
*For: Pokemon AI Video Documentary Generator*
