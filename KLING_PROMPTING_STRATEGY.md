# Kling 2.6 Video Prompting Strategy

**Date:** 2026-01-11
**Purpose:** Best practices for Kling 2.6 image-to-video generation to avoid unwanted behaviors

---

## CRITICAL ISSUE IDENTIFIED

**Problem:** After Flamethrower attack, Charizard runs away in generated video
- ❌ Charizard should maintain position after attacking
- ❌ Unwanted fleeing/retreating behavior
- ❌ Breaks battle logic

**Root Cause:** Kling AI fills in missing context with assumptions
- Without explicit constraints, AI adds "logical" behaviors
- After attack → AI assumes "retreat to safety"
- Must explicitly state what should NOT happen

---

## KLING PROMPTING BEST PRACTICES

### 1. POSITIVE CONSTRAINTS (What SHOULD happen)

**Format:**
```
[Subject] [specific action] [manner/style], [camera work], [visual effects], [quality]
```

**Example:**
```
Charizard maintaining stable hover position after releasing Flamethrower,
wings beating steadily in place, focused expression watching attack,
camera steady side angle, heat distortion from flames,
photorealistic motion, cinematic quality
```

### 2. NEGATIVE CONSTRAINTS (What should NOT happen)

**Critical for Kling 2.6:** Must explicitly state forbidden behaviors

**Format:**
```
NO [unwanted action], NOT [unwanted behavior], AVOID [problem],
character STAYS [position], MAINTAINS [state]
```

**Example:**
```
NO retreating, NO flying away, NO running, NOT moving backward,
Charizard STAYS in attack position, MAINTAINS hover location,
AVOID defensive retreat, target Pokemon STAYS in place receiving attack
```

---

## BATTLE SCENE SPECIFIC CONSTRAINTS

### Attack Scenes (Flamethrower, Fire Blast, etc.)

**Attacker Constraints:**
```
✅ POSITIVE:
- Maintaining attack stance
- Holding position steady
- Focused on target
- Wings beating in place (if airborne)

❌ NEGATIVE (Must include):
- NO retreating after attack
- NO flying away
- NO backward movement
- NOT turning away
- STAYS in attack position
- MAINTAINS original location
```

**Target Constraints:**
```
✅ POSITIVE:
- Taking hit directly
- Recoiling from impact
- Pain expression
- Knockback motion (controlled)

❌ NEGATIVE (Must include):
- NO dodging (unless specified)
- NO defensive barriers
- NO shields
- NOT avoiding attack
- STAYS in frame
- Takes DIRECT hit
```

### Camera Constraints

```
✅ POSITIVE:
- Smooth panning/tracking
- Steady framing
- Following action
- Professional cinematography

❌ NEGATIVE:
- NO jerky movement
- NO sudden jumps
- NOT losing focus
- AVOID shaky cam
- STAYS on both Pokemon
```

---

## COMPREHENSIVE PROMPT TEMPLATE

```
[POSITIVE ACTIONS]
[Character] [specific action] [manner], [secondary actions],
[facial expression], [body position]

[CAMERA WORK]
Camera [movement type] [direction], [framing], [style]

[VISUAL EFFECTS]
[Effect type] [characteristics], [lighting], [atmosphere]

[NEGATIVE CONSTRAINTS - CRITICAL]
NO [forbidden action 1], NO [forbidden action 2], NOT [unwanted behavior],
[Character] STAYS [position], MAINTAINS [state], AVOID [problem],
target STAYS [location], NOT [unwanted reaction]

[QUALITY]
Photorealistic motion, cinematic quality, smooth animation,
realistic physics, 8K detail
```

---

## PANEL-SPECIFIC PROMPTS (CORRECTED)

### Panel 1: Flamethrower Launch

**OLD (Causes retreat):**
```
Camera zooming in on Charizard's open mouth as massive Flamethrower
stream releases, then panning to follow the orange-red flame trajectory
toward Dragonite
```

**NEW (Prevents retreat):**
```
Camera zooming in on Charizard's open mouth as massive Flamethrower
stream releases, Charizard MAINTAINING stable hover position in place,
wings beating steadily NOT moving backward, focused expression watching
attack travel toward Dragonite, camera panning to follow flame trajectory
while Charizard STAYS in attack position,

NO retreating, NO flying away, NOT moving backward after attack,
Charizard HOLDS position firmly, MAINTAINS original location,
STAYS committed to attack stance, AVOID defensive withdrawal,

side tracking shot showing full horizontal attack path, heat distortion
visible, both Pokemon STAY in their positions, photorealistic motion,
smooth camera work, cinematic cinematography, dramatic lighting
```

### Panel 2: Impact with Pain

```
Flamethrower stream STRIKING Dragonite's torso with explosive impact,
Dragonite recoiling in pain with pained expression, body pushed backward
by force but STAYING in frame, taking DIRECT undefended hit,

NO dodging, NO defensive barriers, NO shields appearing, NOT avoiding impact,
Dragonite TAKES full hit, STAYS in camera view, does NOT fly away,
Charizard visible in background MAINTAINING attack position,

flames engulfing torso, photorealistic impact effects, camera slight shake,
dramatic lighting, cinematic quality, smooth motion
```

### Panel 3: Burn Marks Reveal

```
Flames dissipating revealing severe burn marks on Dragonite, smoke rising
from burnt areas, exhausted breathing with slight body movement STAYING in
position, pained expression,

NO rapid movement, NOT flying away, Dragonite MAINTAINS location showing
damage, STAYS visible in frame displaying burn effects, HOLDS exhausted pose,

photorealistic burn damage detail, realistic smoke physics, cinematic lighting,
slow motion reveal, 8K detail quality
```

### Panel 4: Anger Building

```
Dragonite's expression transforming from pain to fierce anger, eyes narrowing
with rage, teeth baring aggressively, fists clenching, body tensing WHILE
STAYING in position, building counter-attack energy,

NO premature movement, NOT lunging forward yet, MAINTAINS current location,
STAYS in frame building rage, burn marks STAY visible throughout,
HOLDS tension before action,

smoke still rising from burns, photorealistic emotion transformation,
dramatic intensity building, cinematic close-up, perfect continuity
```

### Panel 5: Charging TOWARD Charizard (OTS)

```
Over-the-shoulder view from behind Charizard in foreground showing Dragonite
charging FORWARD AGGRESSIVELY from background TOWARD camera and Charizard,
closing distance rapidly, wings beating powerfully FOR FORWARD THRUST,
fierce angry expression, approaching TO ATTACK,

NO lateral movement, NOT flying past, NOT circling, Dragonite CHARGES DIRECTLY
TOWARD target, STAYS on collision course, MAINTAINS forward approach vector,
Charizard in foreground STAYS in position bracing defensively NOT retreating,

over-the-shoulder dynamic shot, motion blur showing forward velocity,
depth movement background to foreground, photorealistic motion,
cinematic aggressive approach, dramatic tension
```

### Panel 6: Thunder Punch Impact

```
Dragonite's electrified fist making FULL CONTACT with Charizard in
devastating Thunder Punch, massive yellow electric explosion at impact,
Charizard recoiling in pain, electric current through body,

NO missing, NOT glancing blow, DIRECT FULL IMPACT, both Pokemon STAY in
frame during hit, NOT flying apart immediately, contact MAINTAINED for
impact moment, HOLDS connection showing force,

bright lightning arcs bursting outward, photorealistic electricity effects,
camera emphasizing connection point, dramatic impact, cinematic quality,
slow motion at contact moment
```

---

## KEY RULES FOR KLING 2.6

### Rule 1: Always Include Negative Constraints
- **Never rely on positive prompts alone**
- AI will fill gaps with assumptions
- Explicitly state what should NOT happen

### Rule 2: Use Position Maintenance Keywords
- **STAYS in position**
- **MAINTAINS location**
- **HOLDS stance**
- **NOT moving away**
- **KEEPS position**

### Rule 3: Be Specific About Directions
- **TOWARD** (approaching)
- **NOT AWAY FROM** (not retreating)
- **FORWARD** (advancing)
- **IN PLACE** (stationary)
- **BACKGROUND TO FOREGROUND** (depth)

### Rule 4: Combat Unwanted "Logical" Behaviors
Common AI assumptions to explicitly negate:
- ❌ Retreat after attack → Add "NO retreating"
- ❌ Dodge incoming attack → Add "NO dodging, takes DIRECT hit"
- ❌ Defensive barriers → Add "NO shields, NO barriers"
- ❌ Flying away from damage → Add "STAYS in position"
- ❌ Circling behavior → Add "CHARGES DIRECTLY TOWARD"

### Rule 5: Maintain Character Commitment
```
Character commits to action FULLY:
- Attacker MAINTAINS attack position until completion
- Target TAKES hit directly without evasion
- Both STAY in frame throughout action
- NO premature movement before action completes
```

---

## VALIDATION CHECKLIST

Before submitting Kling 2.6 prompt:

**Positive Constraints:**
- [ ] Specific action clearly described
- [ ] Camera work specified
- [ ] Visual effects detailed
- [ ] Quality requirements stated

**Negative Constraints (CRITICAL):**
- [ ] Unwanted movements explicitly forbidden
- [ ] Position maintenance keywords included
- [ ] "NO [action]" statements added
- [ ] "STAYS/MAINTAINS" keywords present
- [ ] Direction negations included (NOT away, NOT backward)

**Battle Logic:**
- [ ] Attacker maintains position after attack
- [ ] Target takes hit directly
- [ ] Both stay in frame
- [ ] No defensive behaviors unless specified

**Continuity:**
- [ ] Previous state elements maintained (burn marks, etc.)
- [ ] Character positions consistent
- [ ] No sudden teleportation
- [ ] Smooth transitions

---

## EXAMPLE: COMPLETE CORRECTED PROMPT

**Panel 1 Flamethrower (FULL VERSION):**

```
Camera zooming in dramatically on Charizard's open mouth as massive
orange-red Flamethrower stream releases with intense heat, Charizard
MAINTAINING perfectly stable hover position in mid-air NOT moving,
wings beating steadily in place for stability, fierce determined
expression locked on target, head extended forward directing flames,
camera smoothly panning to follow the horizontal flame trajectory
traveling toward Dragonite while Charizard STAYS committed in attack
position throughout,

CRITICAL CONSTRAINTS:
NO retreating after releasing flames, NO flying away, NO backward movement,
NOT pulling back, NOT flinching, Charizard HOLDS hover position firmly,
MAINTAINS exact original location, STAYS planted in attack stance,
KEEPS wings beating in place, COMMITS to attack fully, AVOID any defensive
withdrawal, does NOT turn away, REMAINS focused on target,

Dragonite on right side STAYING in position preparing to receive attack,
NOT dodging, NOT moving away, MAINTAINS defensive stance, STAYS in target
position, both Pokemon airborne at same height MAINTAINING positions,

side tracking shot showing complete horizontal attack path from source to
target with professional stacking, realistic heat distortion waves visible
around flame stream, photorealistic fire physics, smooth camera work
following flames, cinematic cinematography with dramatic lighting,
8K quality rendering, both Pokemon clearly visible throughout,
battle commitment maintained, realistic motion physics
```

**Length:** ~1500 characters (optimal for Kling 2.6)
**Structure:** Positive → Negative → Context → Technical

---

## COMMON MISTAKES TO AVOID

### Mistake 1: Trusting Positive Prompts Alone
```
❌ BAD: "Charizard hovering after attack"
✅ GOOD: "Charizard hovering after attack, NO retreating, MAINTAINS position"
```

### Mistake 2: Vague Position Descriptions
```
❌ BAD: "Character in position"
✅ GOOD: "Character STAYS in exact attack position, HOLDS hover location"
```

### Mistake 3: Missing Direction Negations
```
❌ BAD: "Moving toward target"
✅ GOOD: "Moving TOWARD target, NOT away, NOT circling, DIRECT approach"
```

### Mistake 4: Assuming Battle Logic
```
❌ BAD: Assuming AI knows attacker shouldn't retreat
✅ GOOD: Explicitly state "NO retreating, STAYS in attack position"
```

---

## STATUS: READY TO IMPLEMENT

**Next Steps:**
1. Update `test_video_from_panel.py` with corrected prompts
2. Regenerate Panel 1 video with negative constraints
3. Validate Charizard maintains position
4. Apply template to all 6 panels

**Expected Result:**
- ✅ Charizard stays in position after Flamethrower
- ✅ No unwanted retreat behavior
- ✅ Battle logic maintained
- ✅ Professional attack commitment

---

**References:**
- Kling 2.6 API Documentation
- Video Generation Best Practices
- Battle Cinematography Standards
- AI Behavior Pattern Analysis
