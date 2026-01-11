# Complete Validation Framework List - All Validation Criteria

## Overview

This document contains **ALL validation frameworks** we have developed:
1. **Original 14-16 Step Framework** (Tier 0-3)
2. **Technical Validation** (File specs)
3. **NO NEW ELEMENTS Framework** (Shield issue fix)
4. **Storyboard Continuity Framework** (Frame-by-frame)
5. **Combined Total: ~50+ validation checks**

---

## FRAMEWORK 1: TIER 0-3 CONTENT VALIDATION (14-24 Steps)

### **TIER 0: PHOTOREALISM** (5 Criteria - CRITICAL)
**Requirement:** Must pass 90%+ (4.5/5.0)

| # | Criterion | Description | Check |
|---|-----------|-------------|-------|
| 1 | **Realistic Scales** | Detailed reptilian scales with depth and texture visible (not smooth 3D animation) | Manual visual check |
| 2 | **Natural Lighting** | Physically accurate shadows, realistic light sources, no artificial glow | Manual visual check |
| 3 | **Organic Imperfections** | Scratches, weathering, battle damage visible, not perfectly smooth | Manual visual check |
| 4 | **Anatomical Accuracy** | Features based on real animals, realistic proportions and movement | Manual visual check |
| 5 | **NO 3D Animation Style** | Not smooth/polished like 3D animation, has texture and realism | Manual visual check |

**Severity:** CRITICAL - If fails, entire image fails validation
**Pass Threshold:** 4.5/5.0 (90%+)

---

### **TIER 1: POKEMON FEATURES** (6-14 Criteria - CRITICAL)
**Requirement:** Must pass 100%

#### **For Charizard** (6 Criteria):

| # | Criterion | Description | Check |
|---|-----------|-------------|-------|
| 1 | **Charizard Recognition** | Character clearly recognizable as Charizard, not generic dragon | Visual identification |
| 2 | **Orange Body Color** | Realistic orange scales (not red, not brown, not yellow) | Color verification |
| 3 | **Teal Wing Undersides** | Wing membranes show teal/turquoise color, clearly visible | Wing color check |
| 4 | **Cream Belly** | Belly/underside is cream colored, not white or orange | Belly color check |
| 5 | **Flaming Tail Tip** | Tail tip ALWAYS burning with flame (critical distinguisher) | Tail flame present |
| 6 | **Lean Athletic Build** | Body is lean, athletic, NOT bulky or stocky | Body proportion check |

#### **For Dragonite** (8 Criteria):

| # | Criterion | Description | Check |
|---|-----------|-------------|-------|
| 7 | **Dragonite Recognition** | Character clearly recognizable as Dragonite | Visual identification |
| 8 | **ORANGE-TAN Body** | Light ORANGE-TAN body (NOT green, NOT cream/pale, NOT yellow) | **CRITICAL color check** |
| 9 | **Teal Wing Membranes** | Wing membranes show teal/turquoise color | Wing color check |
| 10 | **Cream Belly with Stripes** | Cream belly with horizontal stripe pattern | Belly pattern check |
| 11 | **Two Thin Antennae** | Two antennae on head, thin and curved | Antennae count check |
| 12 | **NO Tail Flame** | Dragonite does NOT have flaming tail (key difference from Charizard) | **CRITICAL - No tail flame** |
| 13 | **Bulky Stocky Build** | Body is bulky, stocky, muscular (NOT lean like Charizard) | Body proportion check |
| 14 | **30% Larger Size** | When both present, Dragonite is 30% larger than Charizard | **Size comparison check** |

**Severity:** CRITICAL - These define the characters
**Pass Threshold:** 100% (all must pass)

---

### **TIER 2: PROMPT ACCURACY** (7 Criteria - MAJOR)
**Requirement:** Must pass 86%+ (6.0/7.0)

| # | Criterion | Description | Check |
|---|-----------|-------------|-------|
| 1 | **Primary Action Matches** | Main action in scene matches prompt specification exactly | Action verification |
| 2 | **Environment Elements** | Required environment present (crater if specified, volcanic valley, etc.) | Environment check |
| 3 | **Pokemon Condition** | Character condition matches (battered/pristine/burnt as specified) | Condition check |
| 4 | **Camera Angle Matches** | Camera angle matches prompt (side-angle, close-up, wide shot, etc.) | Angle verification |
| 5 | **Specific Effects Present** | Colors, sparks, flames, impacts as specified in prompt | Effects check |
| 6 | **Background Accurate** | Background matches (volcanic valley, lava, storm clouds, etc.) | Background verification |
| 7 | **Composition Matches** | Both Pokemon visible if specified, positioning correct | Composition check |

**Special Requirements for Our Scenes:**

**Flamethrower Scenes (Scenes 1-2):**
- ❌ **NO SHIELD on Dragonite** (must take direct hit)
- ✅ Dragonite showing **PAIN expression** (eyes squinting, mouth open, grimacing)
- ✅ Dragonite being **pushed BACKWARD** by force of flames
- ✅ **Flame stream connecting** both Pokemon (Charizard mouth → Dragonite torso)
- ✅ **Impact glow** visible where flames strike
- ✅ Dragonite with **defensive body language** (arms raised but failing)

**Burn Scene (Scene 3):**
- ✅ **VISIBLE BURN MARKS** (blackened scorch patterns on torso/belly)
- ✅ **Smoke wisping** from burnt scales
- ✅ Expression **transitioning from pain to anger**

**Charge Scene (Scene 4):**
- ✅ **Burn marks still visible** (continuity from Scene 3)
- ✅ Dragonite **charging forward** aggressively
- ❌ **NO SHIELD** on Dragonite

**Severity:** MAJOR - Ensures prompt is followed
**Pass Threshold:** 6.0/7.0 (86%+)

---

### **TIER 3: BATTLE ACCURACY** (4 Criteria - MINOR)
**Requirement:** Should pass 75%+ (3.0/4.0)

| # | Criterion | Description | Check |
|---|-----------|-------------|-------|
| 1 | **Attack Effects Match** | Attack appearance matches official anime/game depiction | Reference comparison |
| 2 | **Physics Make Sense** | Momentum, impact, knockback are realistic and logical | Physics check |
| 3 | **Battle Damage Progresses** | Damage accumulates across sequence (burn marks persist) | Continuity check |
| 4 | **Energy Colors Correct** | Orange-red (Flamethrower), Yellow (Thunder), Blue-purple (Dragon Rage) | Color verification |

**Attack Color Standards:**
- **Flamethrower:** Orange-red sustained stream from mouth
- **Thunder Punch:** Yellow electricity on fist/contact point
- **Dragon Rage:** Blue-purple energy sphere/beam
- **Fire Spin:** Orange-red swirling tornado

**Severity:** MINOR - Aesthetic accuracy
**Pass Threshold:** 3.0/4.0 (75%+)

---

## FRAMEWORK 2: TECHNICAL VALIDATION (6 Criteria)

### **Image Technical Specs**

| # | Criterion | Requirement | Check Method |
|---|-----------|-------------|--------------|
| 1 | **Minimum Width** | ≥ 800 pixels | Automated check |
| 2 | **Minimum Height** | ≥ 450 pixels | Automated check |
| 3 | **Minimum File Size** | ≥ 0.1 MB | Automated check |
| 4 | **Maximum File Size** | ≤ 5.0 MB | Automated check |
| 5 | **Aspect Ratio** | 16:9 (1.78) | Automated check |
| 6 | **File Not Corrupted** | > 100 KB (not 252 bytes) | Automated check |

**Target Resolution:** 2752x1536 (Full HD 16:9)

### **Video Technical Specs**

| # | Criterion | Requirement | Check Method |
|---|-----------|-------------|--------------|
| 7 | **Minimum Duration** | ≥ 4.5 seconds | ffprobe check |
| 8 | **Maximum Duration** | ≤ 5.5 seconds | ffprobe check |
| 9 | **Minimum File Size** | ≥ 5.0 MB | File size check |
| 10 | **Maximum File Size** | ≤ 25.0 MB | File size check |
| 11 | **Audio Present** | Must have audio stream | ffprobe check |
| 12 | **Resolution Check** | 1920x1080 or higher | ffprobe check |

**Target:** 5 seconds, ~10-15 MB, 1920x1080 with audio

---

## FRAMEWORK 3: NO NEW ELEMENTS VALIDATION (10+ Criteria)

**Based on User Feedback:** Task ID f59fa6b100331a3a049e8ece19c58347 - Dragonite had shield

### **Forbidden Elements Check**

| # | Element | Status | Severity |
|---|---------|--------|----------|
| 1 | **Shields** | ❌ FORBIDDEN - Must NOT appear | CRITICAL |
| 2 | **Defensive Barriers** | ❌ FORBIDDEN - Must NOT appear | CRITICAL |
| 3 | **Force Fields** | ❌ FORBIDDEN - Must NOT appear | CRITICAL |
| 4 | **Protective Auras** | ❌ FORBIDDEN - Must NOT appear | CRITICAL |
| 5 | **Energy Shields** | ❌ FORBIDDEN - Must NOT appear | CRITICAL |
| 6 | **Extra Weapons** | ❌ FORBIDDEN - Unless in prompt | MAJOR |
| 7 | **Additional Pokemon** | ❌ FORBIDDEN - Unless specified | MAJOR |
| 8 | **Background Objects** | ❌ FORBIDDEN - Unless requested | MAJOR |
| 9 | **Props Not Specified** | ❌ FORBIDDEN - Only prompt elements | MAJOR |
| 10 | **Defensive Postures with Barriers** | ❌ FORBIDDEN - Can defend but NO barriers | CRITICAL |

### **Authorized Elements Only**

**For Our 4-Scene Sequence:**

**Authorized (FROM PROMPT):**
- ✅ Charizard
- ✅ Dragonite
- ✅ Flamethrower flames (orange-red)
- ✅ Volcanic valley background
- ✅ Burn marks (Scene 3+)
- ✅ Smoke/heat effects
- ✅ Impact glow
- ✅ Defensive arm gestures (without barriers)

**Unauthorized (NOT IN PROMPT):**
- ❌ Shields (any type)
- ❌ Defensive barriers
- ❌ Force fields
- ❌ Energy shields
- ❌ Protective bubbles
- ❌ Extra Pokemon
- ❌ Weapons beyond natural attacks
- ❌ Props/objects not specified

### **Dragonite Specific Checks**

| # | Check | Expected | Severity |
|---|-------|----------|----------|
| 1 | **Does Dragonite have a SHIELD?** | NO | CRITICAL |
| 2 | **Does Dragonite have defensive barrier?** | NO | CRITICAL |
| 3 | **Is Dragonite taking DIRECT HIT?** | YES | CRITICAL |
| 4 | **Any protective elements visible?** | NO | CRITICAL |
| 5 | **Defensive arm gesture present?** | YES (but no barrier) | MINOR |

**If ANY forbidden element found:** VALIDATION FAILS → REGENERATE

---

## FRAMEWORK 4: STORYBOARD CONTINUITY VALIDATION (5 Main Categories, 20+ Checks)

**Based on:** Nano Banana Pro standards (95%+ consistency)

### **Category 1: Character Consistency** (8 Checks)

| # | Check | Requirement | Target |
|---|-------|-------------|--------|
| 1 | **Charizard Colors Consistent** | Orange body, teal wings, cream belly across ALL frames | 95%+ match |
| 2 | **Charizard Size Consistent** | Same size/proportions in all frames | 95%+ match |
| 3 | **Charizard Tail Flame Consistent** | Always burning in all frames | 100% |
| 4 | **Dragonite Colors Consistent** | ORANGE-TAN body, teal wings, cream belly across ALL frames | 95%+ match |
| 5 | **Dragonite Size Consistent** | Same size/proportions in all frames | 95%+ match |
| 6 | **Relative Size Consistent** | Dragonite always 30% larger than Charizard | 95%+ match |
| 7 | **Feature Consistency** | Antennae, wing shape, body proportions same | 95%+ match |
| 8 | **NO New Character Features** | No sudden appearance of shields, armor, etc. | 100% |

**Standard:** Nano Banana Pro requires **95%+ character consistency**

### **Category 2: Scene Coherence** (4 Checks)

| # | Transition | Logical Flow Check | Pass Criteria |
|---|------------|-------------------|---------------|
| 1 | **Scene 1 → Scene 2** | Attack launch → Impact with pain? | Logical progression |
| 2 | **Scene 2 → Scene 3** | Impact → Burn marks visible? | Cause and effect |
| 3 | **Scene 3 → Scene 4** | Anger → Charging forward? | Emotional progression |
| 4 | **Overall Narrative** | Does complete sequence make sense? | Story coherence |

**Requirement:** Frame-by-frame narrative must flow logically

### **Category 3: Element Continuity** (7 Checks)

| # | Element | Continuity Requirement | Frames |
|---|---------|----------------------|--------|
| 1 | **Burn Marks Appearance** | Absent in Frame 1-2, appear in Frame 3 | Logical cause |
| 2 | **Burn Marks Persistence** | Once appearing (Frame 3), persist in Frame 4 | Continuity |
| 3 | **Shield Absence** | NO shields in ANY frame (1, 2, 3, 4) | 100% compliance |
| 4 | **Flame Effects** | Present in Frames 1-2, dissipating in Frame 3 | Logical flow |
| 5 | **Environmental Consistency** | Volcanic valley in all frames | 100% match |
| 6 | **NO Random Additions** | No new elements appear mid-sequence | 100% compliance |
| 7 | **NO Random Deletions** | Elements don't disappear without reason | 100% compliance |

**Critical:** Elements follow logical cause-effect progression

### **Category 4: Smooth Transitions** (4 Checks)

| # | Aspect | Transition Requirement | Check |
|---|--------|----------------------|-------|
| 1 | **Position/Pose Flow** | Character positions transition naturally | No jarring jumps |
| 2 | **Action Continuity** | Actions connect logically frame-to-frame | Smooth progression |
| 3 | **Camera Angles** | Camera angles consistent with story | No random shifts |
| 4 | **Motion Flow** | Movement appears continuous across frames | Natural motion |

**Requirement:** Professional frame-by-frame smoothness

### **Category 5: Lighting & Environment Consistency** (3 Checks)

| # | Aspect | Consistency Requirement | Check |
|---|--------|------------------------|-------|
| 1 | **Lighting Direction** | Light sources consistent across frames | No random changes |
| 2 | **Fire Glow Effects** | Fire lighting consistent when flames present | Consistent glow |
| 3 | **Environment Lighting** | Volcanic valley lighting consistent throughout | Same time of day |

**Requirement:** Professional lighting continuity

---

## FRAMEWORK 5: STORYBOARD LAYOUT VALIDATION (For Multi-Panel Images)

### **For 2x2 Grid (4 Panels):**

| # | Criterion | Requirement | Check |
|---|-----------|-------------|-------|
| 1 | **Clear Panel Borders** | All 4 panels have visible borders | Visual check |
| 2 | **Panel Separation** | Panels clearly separated, not bleeding together | Visual check |
| 3 | **Equal Panel Sizes** | All 4 panels roughly equal size | Proportion check |
| 4 | **Correct Layout** | Top-left, top-right, bottom-left, bottom-right order | Layout check |
| 5 | **Panel Labels/Numbers** | Panels identifiable as 1, 2, 3, 4 | Label check |

### **For 3x2 Grid (6 Panels):**

| # | Criterion | Requirement | Check |
|---|-----------|-------------|-------|
| 1 | **Clear Panel Borders** | All 6 panels have visible borders | Visual check |
| 2 | **Grid Structure** | 3 columns × 2 rows clearly defined | Grid check |
| 3 | **Reading Order** | Left-to-right, top-to-bottom (1-2-3, 4-5-6) | Order check |
| 4 | **Equal Panel Sizes** | All 6 panels roughly equal size | Proportion check |

### **For 4x2 Grid (8 Panels):**

| # | Criterion | Requirement | Check |
|---|-----------|-------------|-------|
| 1 | **Clear Panel Borders** | All 8 panels have visible borders | Visual check |
| 2 | **Grid Structure** | 4 columns × 2 rows clearly defined | Grid check |
| 3 | **Reading Order** | Left-to-right, top-to-bottom (1-2-3-4, 5-6-7-8) | Order check |
| 4 | **Equal Panel Sizes** | All 8 panels roughly equal size | Proportion check |

---

## COMPLETE VALIDATION CHECKLIST SUMMARY

### **Total Validation Criteria Count:**

| Framework | Criteria Count | Severity |
|-----------|---------------|----------|
| **Tier 0: Photorealism** | 5 | CRITICAL |
| **Tier 1: Pokemon Features** | 6-14 (depends on characters) | CRITICAL |
| **Tier 2: Prompt Accuracy** | 7 | MAJOR |
| **Tier 3: Battle Accuracy** | 4 | MINOR |
| **Technical Validation** | 12 (6 image + 6 video) | MAJOR |
| **NO NEW ELEMENTS** | 10+ | CRITICAL |
| **Storyboard Continuity** | 26 (5 categories) | MAJOR |
| **Storyboard Layout** | 5-8 (depends on grid) | MINOR |
| **TOTAL** | **~60-80 validation checks** | Mixed |

### **Critical Validation Points:**

**Must Pass (100% Required):**
1. ❌ **NO SHIELDS** in any scene
2. ❌ **NO defensive barriers** in any scene
3. ✅ Dragonite ORANGE-TAN color (not green)
4. ✅ Dragonite NO tail flame
5. ✅ Character recognition clear
6. ✅ File not corrupted (> 100 KB)

**High Priority (90%+ Required):**
1. Photorealism (4.5/5.0)
2. Character consistency (95%+)
3. Prompt accuracy (6.0/7.0)
4. Technical specs met

**Medium Priority (75%+ Required):**
1. Battle accuracy (3.0/4.0)
2. Scene coherence
3. Element continuity
4. Smooth transitions

---

## VALIDATION WORKFLOW

### **Step 1: Pre-Generation Validation**

Before generating:
- [ ] Prompt includes all authorized elements
- [ ] Prompt explicitly states "NO SHIELD"
- [ ] Prompt states "NO defensive barriers"
- [ ] Character descriptions detailed and consistent
- [ ] Camera angle specified
- [ ] Action clearly described
- [ ] Forbidden elements explicitly negated

### **Step 2: Post-Generation - Image Validation**

After image generated:
- [ ] Run Tier 0-3 validation (24 checks)
- [ ] Run NO NEW ELEMENTS check (10+ checks)
- [ ] Run Technical validation (6 checks)
- [ ] Manual visual inspection
- [ ] **CRITICAL: Shield check**

### **Step 3: Post-Generation - Video Validation**

After video generated:
- [ ] Run Technical validation (6 checks)
- [ ] Verify action matches image
- [ ] Check for added elements in motion
- [ ] **CRITICAL: Shield check in video**
- [ ] Audio present check
- [ ] Duration check

### **Step 4: Sequence Validation**

After all scenes generated:
- [ ] Run Storyboard Continuity validation (26 checks)
- [ ] Character consistency across all frames (95%+)
- [ ] Element continuity logical
- [ ] Scene coherence flows
- [ ] NO NEW ELEMENTS in any frame
- [ ] Smooth transitions between frames

### **Step 5: Final Validation**

Before accepting sequence:
- [ ] All critical checks passed (100%)
- [ ] All high-priority checks passed (90%+)
- [ ] All medium-priority checks passed (75%+)
- [ ] User manual review complete
- [ ] Shield issue confirmed absent
- [ ] Ready for video generation

---

## REGENERATION TRIGGERS

**Must Regenerate If:**
1. ❌ Shield found on Dragonite (CRITICAL FAIL)
2. ❌ Any defensive barrier found (CRITICAL FAIL)
3. ❌ Dragonite wrong color (green instead of orange-tan) (CRITICAL FAIL)
4. ❌ File corrupted (< 100 KB) (CRITICAL FAIL)
5. ❌ Character not recognizable (CRITICAL FAIL)
6. ❌ Tier 0 < 90% (photorealism fail)
7. ❌ Tier 1 < 100% (character features fail)

**Should Regenerate If:**
- Prompt accuracy < 86% (Tier 2 fail)
- Character consistency < 95% across frames
- Battle accuracy < 75% (Tier 3 fail)
- Technical specs not met
- Element continuity broken

**Can Accept If:**
- Minor lighting inconsistencies
- Small proportion variations (< 5%)
- Battle accuracy 75-90%
- All CRITICAL checks passed

---

## TOOLS FOR VALIDATION

**Automated Tools:**
```bash
# Technical validation
python3 scripts/validation_framework.py

# Content validation (Tier 0-3)
python3 scripts/validate_image_robust.py

# Comprehensive validation
python3 scripts/comprehensive_content_validation.py

# Enhanced validation (NO NEW ELEMENTS + Storyboard)
python3 scripts/validation_framework_enhanced.py
```

**Manual Checks:**
- Visual inspection of each image/video
- Shield/barrier detection (user review)
- Character consistency verification
- Element continuity tracking
- Frame-by-frame comparison

---

## EXAMPLE VALIDATION REPORT

```
SCENE 1 VALIDATION REPORT
========================

Tier 0 (Photorealism): 5.0/5.0 ✅ PASS
Tier 1 (Pokemon Features): 12/12 ✅ PASS
Tier 2 (Prompt Accuracy): 7.0/7.0 ✅ PASS
Tier 3 (Battle Accuracy): 4.0/4.0 ✅ PASS

Technical Validation:
- Resolution: 2752x1536 ✅
- File size: 2.82 MB ✅
- Aspect ratio: 16:9 ✅

NO NEW ELEMENTS:
- Shield present? NO ✅
- Defensive barrier? NO ✅
- Unauthorized elements? NO ✅

OVERALL: PASS ✅

Recommendation: Approved for video generation
```

---

## VALIDATION BEST PRACTICES

1. **Always Validate Before Proceeding**
   - Don't generate video from unvalidated image
   - Don't concatenate unvalidated videos
   - Fix issues early in pipeline

2. **Explicit is Better Than Implicit**
   - State "NO SHIELD" explicitly in prompt
   - List forbidden elements
   - Don't assume AI knows what NOT to add

3. **Document All Failures**
   - Record what failed
   - Identify pattern in failures
   - Improve prompts based on data

4. **Use Validation for Prompt Improvement**
   - Validation feedback → prompt modifications
   - Iterate until validation passes
   - Data-driven prompt engineering

5. **Prioritize Critical Checks**
   - Shield check is #1 priority (user-identified issue)
   - Character recognition is critical
   - File corruption check is critical
   - Can be lenient on minor aesthetic issues

---

## SUMMARY

**Total Validation Frameworks: 5**
**Total Validation Checks: ~60-80 (depending on scene complexity)**

**Critical Focus Areas:**
1. ❌ **NO SHIELDS** (Task ID: f59fa6b100331a3a049e8ece19c58347 issue)
2. ✅ Character features accurate (colors, sizes, anatomy)
3. ✅ Element continuity maintained (burn marks logic)
4. ✅ Technical specs met (resolution, duration, audio)
5. ✅ 95%+ consistency across frames (Nano Banana Pro standard)

**This comprehensive validation framework ensures:**
- No unauthorized elements (shields, barriers)
- Professional quality (photorealism, consistency)
- Logical progression (continuity, coherence)
- Technical standards met (specs, duration)
- Data-driven improvement (feedback loop)
