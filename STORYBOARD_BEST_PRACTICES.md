# Storyboard Best Practices & Nano Banana Pro Guide

## Issue Identified: Task ID f59fa6b100331a3a049e8ece19c58347

**Problem:** Dragonite has a SHIELD in generated video
- ❌ **Shield is a NEW ELEMENT** not in original prompt
- ❌ Breaks continuity (shield appears, then disappears)
- ❌ Changes battle dynamics (defensive vs offensive)

**Root Cause:** No validation for "unauthorized elements" added during generation

---

## Storyboard Creation Best Practices (2025)

### 1. Clarity Over Detail

> "Storyboards aren't meant to be works of art - focus on conveying the action and layout clearly"
> — [46 Best Movie Storyboard Examples](https://www.studiobinder.com/blog/storyboard-examples-film/)

**Key Principle:**
- Simple drawings > Polished artwork
- Action clarity > Artistic detail
- Easy-to-read annotations critical

**Application to Our Project:**
- Prompts should be CLEAR about what's in scene
- No ambiguity that could lead to extra elements
- Explicit "NO SHIELD" requirements

### 2. Essential Elements for Each Frame

> "Break up the script by highlighting major beats: actions, locations, wardrobe, staging, narrative arches"
> — [How To Make a Film Storyboard](https://milanote.com/guide/film-storyboards)

**For Each Storyboard Frame:**
1. **Action:** What's happening? (Flamethrower launch, impact, pain reaction)
2. **Location:** Where? (Volcanic valley, specific positioning)
3. **Characters:** Who's visible? (Charizard left, Dragonite right)
4. **Expressions:** Emotions? (Fierce, pained, angry)
5. **Special Effects:** What elements? (Flames, burn marks, NO shields)
6. **Camera:** Angle and movement (Side-angle wide shot)

**Critical Addition:**
- **7. FORBIDDEN ELEMENTS:** Explicitly list what should NOT appear (shields, barriers)

### 3. Frame-by-Frame Continuity

> "In animation, storyboarding holds greater importance because animators must create everything from scratch"
> — [How to Storyboard for Animation](https://beverlyboy.com/filmmaking/how-to-storyboard-for-animation/)

**Continuity Requirements:**
- Character appearance consistent across frames
- Element continuity (burn marks persist)
- No new objects appear mid-sequence
- Logical action flow between frames

**Our 4-Scene Sequence:**
```
Frame 1: Flamethrower Launch
  ✓ Charizard LEFT, Dragonite RIGHT
  ✓ Flames beginning
  ❌ NO SHIELD on either

Frame 2: Impact with Pain
  ✓ Flames STRIKING Dragonite
  ✓ Pain expression visible
  ✓ Knockback motion
  ❌ NO SHIELD (must take direct hit)

Frame 3: Burn Marks & Anger
  ✓ BURN MARKS visible (from Frame 2 impact)
  ✓ Transition pain → anger
  ✓ Smoke from burns
  ❌ NO SHIELD

Frame 4: Revenge Charge
  ✓ Dragonite charging forward
  ✓ BURN MARKS still visible (continuity)
  ✓ Angry expression maintained
  ❌ NO SHIELD
```

### 4. Annotations and Notes

> "Arrows or lines indicate motion, while facial expressions and posture convey emotions"
> — [How to Storyboard?](https://localeyesit.com/how-to-storyboard/)

**Essential Annotations:**
- Motion indicators (flames traveling, knockback direction)
- Expression notes (pain, anger, fierce)
- Camera movement (zoom in, wide shot, close-up)
- **Forbidden elements** (NO SHIELD, NO barriers)

---

## Nano Banana Pro Storyboard Features

### Overview

> "Nano Banana Pro supports 14 reference image inputs and maintains 95%+ character consistency"
> — [Nano Banana Pro Storyboard Generation Guide](https://help.apiyi.com/nano-banana-pro-storyboard-generation-guide-en.html)

**Release:** November 2025 (Google DeepMind)
**Key Feature:** Frame-by-frame continuous scene generation

### Frame-by-Frame Continuous Scenes

**Best Way to Create Continuous Scenes:**

1. **Initial Frame Setup**
   ```
   - Generate first frame with clear character definitions
   - Ensure all elements explicitly stated
   - List forbidden elements (NO shields, NO barriers)
   ```

2. **Subsequent Frame Generation**
   > "Nano Banana can generate subsequent frame photos from initial frame, maintaining scene elements"
   > — [Nano Banana Pro Storyboard Creation Guide](https://sider.ai/blog/ai-image/nano-banana-pro-storyboard-creation-guide-for-video)

   **Method:**
   - Reference previous frame
   - Maintain character consistency (95%+ accuracy target)
   - Change only specified elements (action, expression)
   - Keep environment consistent

3. **Scene Coherence Control**
   > "Conversational editing allows maintaining previous shot's scene elements while changing character actions"
   > — [Nano Banana Pro Guide](https://help.apiyi.com/nano-banana-pro-storyboard-generation-guide-en.html)

   **Process:**
   ```
   Frame 1 → Frame 2: Keep characters, change to "impact" action
   Frame 2 → Frame 3: Keep Dragonite, add burn marks, change expression
   Frame 3 → Frame 4: Keep burn marks, change to charging pose
   ```

### Character Consistency Standards

**Nano Banana Pro Requirements:**
- **95%+ character appearance consistency**
- Same clothing/features throughout
- Consistent action style
- Accurate character proportions

**Our Pokemon Battle Application:**
```
Charizard Consistency:
✓ 5'7" lean athletic build
✓ Orange body with realistic scales
✓ Teal wing undersides
✓ Cream belly
✓ Flaming tail

Dragonite Consistency:
✓ 7'3" bulky build (30% larger)
✓ ORANGE-TAN body (NOT green)
✓ Teal wing membranes
✓ Cream belly with stripes
✓ Two antennae
✓ NO tail flame
❌ NO SHIELD (critical!)
```

### Professional Output Standards

> "Native 2K resolution ensures every visual output is sharp and ready for professional use"
> — [Nano Banana Pro for Cinematic Storyboarding](https://www.geeky-gadgets.com/high-resolution-2k-output-in-nano-banana-pro-image-generator/)

**Quality Requirements:**
- 2K resolution minimum (2048×1080 or higher)
- Professional-grade output
- No upscaling needed
- Cinematic composition

---

## Storyboard Validation Framework

### NEW: Element Control Validation

**Problem:** Task ID f59fa6b100331a3a049e8ece19c58347 - Shield appeared

**Solution:** 3-Tier Element Validation

#### Tier 1: Authorized Elements Check
```python
def validate_authorized_elements(frame, prompt):
    """
    Ensure ONLY elements from prompt appear.

    Authorized (from prompt):
    ✓ Charizard
    ✓ Dragonite
    ✓ Flamethrower flames
    ✓ Volcanic valley background
    ✓ Burn marks (Frame 3+)

    Unauthorized (not in prompt):
    ❌ Shields
    ❌ Defensive barriers
    ❌ Force fields
    ❌ Extra weapons
    ❌ Additional Pokemon
    ❌ Props not specified
    """
    return check_only_prompt_elements_present(frame)
```

#### Tier 2: Forbidden Elements Check
```python
def validate_no_forbidden_elements(frame, forbidden_list):
    """
    Explicit check for elements that must NOT appear.

    Forbidden for our scenes:
    ❌ Shields (any type)
    ❌ Defensive barriers
    ❌ Protective auras
    ❌ Energy shields
    ❌ Force fields
    ❌ Defensive postures with barriers
    """
    for element in forbidden_list:
        if element_detected_in_frame(frame, element):
            return FAIL
    return PASS
```

#### Tier 3: Continuity Element Check
```python
def validate_element_continuity(frames):
    """
    Elements should only appear when prompted.

    Frame 1: No burn marks (attack just starting)
    Frame 2: No burn marks yet (impact happening)
    Frame 3: BURN MARKS appear (consequence of Frames 1-2)
    Frame 4: Burn marks PERSIST (continuity)

    Violations:
    ❌ New element appears without cause
    ❌ Required element disappears
    ❌ Inconsistent element presence
    """
    return check_element_logic_flow(frames)
```

---

## Best Practices Summary

### DO's ✓

1. **Clarity First**
   - Clear action descriptions
   - Explicit element lists
   - Unambiguous annotations

2. **Explicit Negation**
   - State "NO SHIELD" explicitly
   - List forbidden elements
   - Prevent AI assumptions

3. **Continuity Control**
   - Reference previous frames
   - Maintain character consistency (95%+)
   - Logical element progression

4. **Frame-by-Frame Logic**
   - Action flows naturally
   - Elements appear/persist logically
   - No unexplained additions

5. **Professional Standards**
   - 2K+ resolution
   - Cinematic composition
   - Production-ready output

### DON'Ts ❌

1. **Never Assume**
   - Don't assume AI knows "no shield"
   - Must explicitly state negations
   - Can't rely on implicit understanding

2. **Never Skip Validation**
   - Check each frame individually
   - Validate full sequence continuity
   - Verify no unauthorized elements

3. **Never Ignore Continuity**
   - Elements must persist (burn marks)
   - Character features consistent
   - No random appearance/disappearance

4. **Never Accept New Elements**
   - If shield appears → REGENERATE
   - If barrier appears → REGENERATE
   - If any unauthorized element → REGENERATE

---

## Validation Checklist for Each Frame

### Pre-Generation Checklist

Before generating each frame:

- [ ] Authorized elements listed explicitly?
- [ ] Forbidden elements stated ("NO SHIELD")?
- [ ] Character descriptions consistent with previous frames?
- [ ] Camera angle specified?
- [ ] Action clearly described?
- [ ] Expression/emotion stated?
- [ ] Continuity elements from previous frame?

### Post-Generation Validation

After generating each frame:

- [ ] ❌ **CRITICAL:** Any shields present? (Should be NO)
- [ ] ❌ **CRITICAL:** Any defensive barriers? (Should be NO)
- [ ] ✓ Only authorized elements visible?
- [ ] ✓ All required elements present?
- [ ] ✓ Character appearance consistent (95%+)?
- [ ] ✓ Continuity elements maintained?
- [ ] ✓ Action matches prompt?
- [ ] ✓ Expression/emotion correct?

### Sequence Validation

After generating full sequence:

- [ ] Character consistency across all frames?
- [ ] Logical element progression (burn marks appear → persist)?
- [ ] No unauthorized elements in ANY frame?
- [ ] Smooth transitions between frames?
- [ ] Narrative coherence maintained?

---

## Example: Correcting the Shield Issue

### Original Prompt (WRONG - Led to Shield)
```
"Dragonite taking Flamethrower hit"
```

**Problem:** Ambiguous, AI added defensive shield

### Corrected Prompt (RIGHT - Explicit Negation)
```
"Dragonite taking DIRECT HIT from Flamethrower with NO SHIELD,
NO defensive barriers, NO protective elements, taking full impact
with pained expression, body recoiling backward from flame force,
completely undefended against attack"
```

**Improvements:**
- ✓ "NO SHIELD" explicit
- ✓ "NO defensive barriers" explicit
- ✓ "DIRECT HIT" emphasizes no protection
- ✓ "completely undefended" reinforces
- ✓ Describes pain/recoil (natural reaction without defense)

---

## Implementation in Our Pipeline

### Updated Scene Generation

```python
scene2_prompt = """
Massive orange-red Flamethrower stream STRIKING Dragonite torso with
bright impact glow, Dragonite with PAINED expression and NO SHIELD,
NO defensive barriers, NO protective elements, taking DIRECT UNDEFENDED
HIT, body being pushed backward by flame force, arms raised in failed
defensive gesture but NO barriers or shields present, completely vulnerable
to attack, side-angle medium shot
"""
```

### Updated Validation

```python
# After generation, validate:
validator.validate_no_new_elements(scene2_image, scene2_def)
validator.validate_forbidden_elements(scene2_image, [
    "shield", "barrier", "force field", "defensive aura",
    "energy shield", "protective element"
])
```

---

## Sources

1. [46 Best Movie Storyboard Examples (Updated 2025)](https://www.studiobinder.com/blog/storyboard-examples-film/)
2. [How To Make a Film Storyboard: Step-By-Step Guide](https://milanote.com/guide/film-storyboards)
3. [How to Storyboard for Animation?](https://beverlyboy.com/filmmaking/how-to-storyboard-for-animation/)
4. [How to Storyboard? - Ultimate Guide for 2025](https://localeyesit.com/how-to-storyboard/)
5. [Nano Banana Pro Storyboard Generation Guide](https://help.apiyi.com/nano-banana-pro-storyboard-generation-guide-en.html)
6. [Nano Banana Pro Storyboard Creation Guide](https://sider.ai/blog/ai-image/nano-banana-pro-storyboard-creation-guide-for-video)
7. [How to Storyboard with Consistent AI Characters in Nano Banana](https://emerge.fibre2fashion.com/blogs/10815/how-to-storyboard-a-product-launch-with-consistent-characters-across-10-images-in-nano-banana)
8. [Nano Banana Pro for Cinematic AI Storyboarding](https://www.geeky-gadgets.com/high-resolution-2k-output-in-nano-banana-pro-image-generator/)

---

## Key Takeaways

1. **Explicit Negation is Critical**
   - AI may add "helpful" elements (shields for defense)
   - Must explicitly state "NO SHIELD" in prompt
   - List forbidden elements, not just desired ones

2. **Frame-by-Frame Continuity**
   - Nano Banana Pro supports 95%+ character consistency
   - Use reference images and conversational editing
   - Maintain element logic across sequence

3. **Validation at Every Step**
   - Check authorized elements only
   - Check forbidden elements absent
   - Check continuity maintained

4. **Professional Standards**
   - 2K+ resolution
   - Cinematic composition
   - Production-ready quality

**Next Step:** Run enhanced validation on all 4 scenes to detect shield issue and regenerate if needed.
