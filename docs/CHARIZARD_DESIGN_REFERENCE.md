# Charizard Official Design Reference

*Complete color palette and anatomical specifications for video generation consistency*

---

## 🎨 Official Color Palette

### Primary Colors

| Body Part | Color Name | Hex Code | RGB | Description |
|-----------|------------|----------|-----|-------------|
| **Body** | Orange | #F08030 / #EE8329 | (240, 128, 48) / (238, 131, 41) | Primary body color - vibrant orange |
| **Belly/Underside** | Cream | #F8D0A8 / #FFEEB0 | (248, 208, 168) / (255, 238, 176) | Chest to tail tip underside |
| **Wing Membranes** | Teal/Turquoise | #58A8B8 / #419EAF | (88, 168, 184) / (65, 158, 175) | **CRITICAL: Blue-green undersides** |
| **Eyes** | Blue | Small, blue eyes | - | Light blue color |
| **Claws** | White | Three per limb | - | White coloring |
| **Foot Soles** | Cream | Same as belly | - | Cream-colored plantigrade feet |
| **Tail Flame** | Orange/Yellow | Normal state | - | Can intensify to blue when irritated |

### Color Terminology for Prompts

**Precise Descriptors (Use These):**
- Wings: "teal wing membranes", "turquoise-blue undersides", "blue-green wing interiors"
- Body: "vibrant orange body", "burnt orange scales"
- Belly: "cream-colored underside", "pale yellow belly"
- Eyes: "small blue eyes", "light blue irises"

**AVOID These Vague Terms:**
- "Colored wings" (not specific)
- "Wing membranes" (missing color descriptor)
- "Orange" for wings (wings are TEAL, not orange!)

---

## 📐 Anatomical Structure

### Overall Proportions

```
Charizard is a bipedal, draconic Pokémon approximately 5'7" (1.7m) tall
Weight: 199.5 lbs (90.5 kg)
```

### Head & Face

**Shape:** Rectangular head with long neck
**Features:**
- Two horn-like structures protruding from the back of head
- Small blue eyes
- Slightly raised nostrils
- Two visible fangs in upper jaw (when mouth closed)
- Strong jawline

### Wings

**Structure:**
- Two large wings sprouting from back
- **Underside (inside): Blue-green/teal color** ⭐ CRITICAL
- **Top side (outside): Orange matching body**
- Horn-like appendage jutting from top of third joint
- Single wing-finger visible through center membrane
- Wing span significantly larger than body width

**Motion Characteristics:**
- Powerful downward beats for takeoff
- Can glide on thermal currents
- Wings fold against back when resting

### Body

**Torso:**
- Robust, stocky belly
- Cream-colored underside from chest to tail tip
- Orange scales on back and sides
- Short, skinny arms compared to belly

**Limbs:**
- Short arms relative to body
- Three white claws per hand
- Stocky legs
- Plantigrade feet (walks on soles)
- Three claws per foot
- Cream-colored foot soles

### Tail

**Structure:**
- Long and tapering
- Cream underside continuing from belly
- Orange top side
- Flame burning at tip

**Flame:**
- Normal: Orange/yellow flame
- Irritated: Intensifies to blue flame
- Always burning

---

## 🎬 Critical Design Points for Video Generation

### Consistency Checklist

**✅ MUST Include in Every Prompt:**

1. **Wing Color Specification**
   - "teal wing membranes"
   - "blue-green wing undersides"
   - "turquoise wing interiors"
   - Never just "wings" without color!

2. **Body Color Contrast**
   - "vibrant orange body"
   - "cream-colored belly/underside"
   - Mention contrast when visible

3. **Distinctive Features**
   - "Two horns on head"
   - "Flame-tipped tail"
   - "Small blue eyes"
   - "White claws" (when visible)

4. **Size/Proportion Reference**
   - "Large Pokemon"
   - "Wingspan twice body width"
   - "Short arms, robust belly"

### Common Mistakes to Avoid

| ❌ Wrong | ✅ Correct |
|---------|----------|
| "Orange wings" | "Teal wing membranes with orange outer edges" |
| "Flying dragon" | "Charizard with blue-green wing undersides" |
| "Red eyes" | "Small blue eyes" |
| "Yellow belly" | "Cream-colored underside" |
| "Slender build" | "Robust belly, stocky build" |

---

## 🔍 Design Variations to Watch For

### Official vs Common Errors

**Official Design (Correct):**
- Wing undersides: Teal/turquoise
- Belly: Cream/pale yellow (not bright yellow)
- Eyes: Blue (not red, not orange)
- Build: Stocky with robust belly
- Horns: Two on back of head (not forward-facing)

**Common AI Generation Errors:**
- Wings appearing orange/brown instead of teal
- Belly too bright yellow
- Eyes appearing red or yellow
- Body too slender/athletic
- Proportions more Western dragon than Charizard

---

## 📝 Prompt Templates with Design Accuracy

### Template 1: Full Body Shot
```
"Charizard with vibrant orange body and cream belly, teal wing membranes
visible showing blue-green undersides, two horns on head, small blue eyes,
flame-tipped tail burning bright, [action], official Pokemon design proportions
with robust stocky build"
```

### Template 2: Wing Focus
```
"Charizard [action], blue-green teal wing membranes spread wide revealing
turquoise undersides, orange body contrasting against teal wings, wing-fingers
visible through membrane, horn appendages at wing joints, [motion details]"
```

### Template 3: Close-Up
```
"Close-up of Charizard [body part], vibrant orange scales, small blue eyes
with fierce expression, two back-facing horns visible, cream underside
partially visible, white claws [action], maintaining official design colors"
```

### Template 4: Action Shot
```
"Charizard with teal wing membranes [action], orange body with cream belly
visible, powerful stocky build, tail flame streaming [color], blue eyes
focused [direction], [motion] preserving official blue-green wing coloration"
```

---

## 🎨 Lighting Considerations

### How Lighting Affects Perceived Colors

**Proper Lighting Descriptors:**

**Daytime/Neutral:**
- "Bright natural light revealing teal wing membranes"
- "Sunlight highlighting blue-green wing undersides"
- "Clear visibility of orange body and cream belly contrast"

**Dramatic Lighting (Use Carefully):**
- "Side-lit showing teal wing glow"
- "Backlit with wing membranes glowing turquoise"
- ⚠️ Avoid: Heavy backlighting can make teal appear dark/brown

**Fire/Flame Lighting:**
- "Firelight casting warm glow on orange scales, teal wings catching orange reflections but maintaining blue-green base color"
- ⚠️ Fire can overwhelm teal with orange - be explicit about preserving wing color

**Atmospheric:**
- "Volcanic glow lighting scene from below, teal wings contrasting against orange environment"
- "Heat shimmer rising around body, teal wing color clearly visible"

---

## 📊 Color Hex Reference Chart

### For Technical Reference

```
BODY COLORS:
Primary Orange:    #F08030  RGB(240, 128, 48)   - Main body, outer wings
Secondary Orange:  #EE8329  RGB(238, 131, 41)   - Shading variation
Dark Orange:       #CD5241  RGB(205, 82, 65)    - Shadow areas

BELLY/UNDERSIDE:
Cream Primary:     #F8D0A8  RGB(248, 208, 168)  - Chest to tail
Cream Light:       #FFEEB0  RGB(255, 238, 176)  - Highlight areas

WING MEMBRANES (CRITICAL):
Teal Primary:      #58A8B8  RGB(88, 168, 184)   - Main wing interior
Teal Alt:          #419EAF  RGB(65, 158, 175)   - Alternative reference
Verdigris:         #419EAE  RGB(65, 158, 174)   - Blue-green designation

ACCENTS:
Eye Blue:          Light blue (exact hex varies by artwork)
Claw White:        Pure white or off-white
Flame Orange:      #FF4500  RGB(255, 69, 0)     - Normal flame
Flame Blue:        Blue-white                    - Irritated state
```

---

## 🔬 Design Evolution Notes

### Consistency Across Media

**Video Game Sprites:** Teal wings clearly visible in Gen 1-9
**TCG Artwork:** Consistently shows blue-green wing undersides
**Anime:** Wings appear teal/turquoise in official animation
**3D Models:** Pokemon GO, Sword/Shield show teal wing interiors

**Shiny Form (For Reference, Not Used):**
- Body: Black instead of orange
- Belly: Still cream
- Wings: Red instead of teal
- (We're using normal form)

---

## 🎯 Prompting Priority Hierarchy

When writing prompts, include design elements in this priority:

1. **Wing Color** (Most important for consistency)
   - "teal wing membranes" or "blue-green wing undersides"

2. **Body/Belly Contrast**
   - "orange body with cream belly"

3. **Distinctive Features**
   - "flame-tipped tail", "two horns", "blue eyes"

4. **Build/Proportions**
   - "stocky robust build"

5. **Motion/Action**
   - Actual movement description

6. **Camera/Environment**
   - How scene is framed

---

## 📚 Research Sources

This reference compiled from:

- [Bulbapedia - Charizard](https://bulbapedia.bulbagarden.net/wiki/Charizard_(Pok%C3%A9mon)) - Official Pokemon encyclopedia
- [Pokemon Database - Charizard](https://pokemondb.net/pokedex/charizard) - Pokedex entry
- [CyberPost - Wing Colors](https://cyberpost.co/what-color-is-charizards-wings/) - Wing anatomy
- [Vintage is the New Old](https://www.vintageisthenewold.com/faq/what-color-are-charizards-wings) - Design FAQ
- [ColorsWall Palette](https://colorswall.com/palette/191525) - Hex codes
- [iPalettes](https://ipalettes.com/palette/pokemon%20Charizard-3156) - RGB values
- [SchemeColor](https://www.schemecolor.com/charizard-pokemon-colors.php) - Color naming

---

## ✅ Quick Reference Card

**Copy-Paste for Prompts:**

```
COLOR KEYWORDS:
- Wings: teal wing membranes / blue-green wing undersides / turquoise wing interiors
- Body: vibrant orange body / burnt orange scales
- Belly: cream-colored underside / pale yellow belly
- Eyes: small blue eyes
- Tail: flame-tipped tail with orange fire

ANATOMY KEYWORDS:
- two horns on back of head
- stocky robust build
- short arms, powerful legs
- white claws (three per limb)
- long tapering tail
- wingspan twice body width

DESIGN CONSISTENCY:
- official Pokemon design
- maintaining teal wing coloration
- preserving blue-green wing membranes
- canonical Charizard proportions
```

---

*Last Updated: 2026-01-04*
*For: Pokemon AI Video Documentary - Character Consistency Reference*
