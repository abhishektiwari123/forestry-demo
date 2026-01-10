# Attack Validation References - Official Pokemon Sources

**Purpose**: Visual references for validating attack appearances against official Pokemon anime/game depictions
**Date**: 2026-01-10

---

## FLAMETHROWER

**Source**: [Bulbapedia - Flamethrower Move](https://bulbapedia.bulbagarden.net/wiki/Flamethrower_(move))

### Official Visual Characteristics
- **Color**: Red-orange stream of fire
- **Form**: Continuous stream from mouth (NOT fireballs)
- **Direction**: Can be aimed up or down
- **Signature Move**: Most frequent attack used by Charizard in anime

### Validation Criteria for Flamethrower
- ✅ Sustained stream of flames (not individual fire blasts)
- ✅ Orange-red color (not blue, yellow, or white flames)
- ✅ Originates from mouth
- ✅ Directed beam/stream shape

### Common Errors to Watch For
- ❌ Fire appearing as disconnected fireballs instead of stream
- ❌ Wrong flame color (blue = Dragon Rage, not Flamethrower)
- ❌ Fire coming from hands or tail instead of mouth

**References**: [Charizard Fire GIFs - Tenor](https://tenor.com/search/charizard-fire-gifs)

---

## THUNDER PUNCH

**Source**: [Bulbapedia - Thunder Punch](https://bulbapedia.bulbagarden.net/wiki/Thunder_Punch_(move))

### Official Visual Characteristics
- **Color**: Yellow/bright golden electricity
- **Location**: Coats fist/claw with electricity before punching
- **Effect**: Electric sparks and crackling around fist
- **Type**: Physical contact attack (punch)

### Validation Criteria for Thunder Punch
- ✅ Yellow/golden electricity (not blue, not white)
- ✅ Electricity centered on fist/claw
- ✅ Crackling sparks visible
- ✅ Physical punching motion

### Common Errors to Watch For
- ❌ Wrong electricity color (blue = Thunderbolt, not Thunder Punch)
- ❌ Electricity beam/projectile (should be melee contact)
- ❌ Electricity on wrong body part (not full body, just fist)

**References**: [Serebii - Thunder Punch](https://www.serebii.net/attackdex-xy/thunderpunch.shtml)

---

## DRAGON RAGE

**Source**: [Bulbapedia - Dragon Rage](https://bulbapedia.bulbagarden.net/wiki/Dragon_Rage_(move))

### Official Visual Characteristics
- **Color**: Blue-purple energy
- **Form**: Sphere/orb forms in mouth, then releases as beam
- **Type**: Shock wave of pure rage energy
- **Visual**: Dragon-type energy (distinct from fire)

### Validation Criteria for Dragon Rage
- ✅ Blue-purple coloration (NOT orange like Flamethrower)
- ✅ Energy sphere visible before release
- ✅ Beam or shock wave form
- ✅ Dragon energy appearance (not fire)

### Common Errors to Watch For
- ❌ Orange/red flames (that's Flamethrower, not Dragon Rage)
- ❌ No energy charge-up phase
- ❌ Wrong energy type visual

**Our Seg09 Result**: ✅ CORRECT - Blue-purple energy beams colliding mid-air

---

## SEISMIC TOSS

**Source**: [Bulbapedia - Seismic Toss](https://bulbapedia.bulbagarden.net/wiki/Seismic_Toss_(move))

### Official Visual Characteristics
**Three Phases**:
1. **Grab**: Pokemon grabs opponent
2. **Ascent**: Spins rapidly while ascending high into air
   - Anime often shows circling the globe
3. **Throw**: Releases with explosive force
4. **Impact**: **MASSIVE CRATER CREATED** when opponent hits ground

### Validation Criteria for Seismic Toss
- ✅ **GRAB visible** (Pokemon physically holding opponent)
- ✅ **SPINNING MOTION** during ascent
- ✅ **HIGH ALTITUDE** reached before throw
- ✅ **CRATER IMPACT** visible after throw

### CRITICAL DETAIL: The Crater
**Source**: [FanVerse - Charizard True Seismic Toss](https://www.fanverse.org/blogs/charizard-shows-a-true-seismic-toss-pokemon-anime.26399/)

The crater is a **SIGNATURE visual element** of Seismic Toss in the anime:
- Large impact crater where opponent lands
- Visible in aftermath/respect scenes
- Demonstrates the power of the throw

**Famous Example**: Charizard vs Magmar (Blaine battle) - Created significant crater on impact

### Common Errors to Watch For
- ❌ **NO CRATER VISIBLE** in aftermath (Seg15/16 current failure)
- ❌ Simple drop instead of spin-throw
- ❌ Low altitude (should reach very high before throw)
- ❌ No physical grab (opponent just floating)

**Our Current Failures**:
- ❌ Seg15: No crater visible below during victory descent
- ❌ Seg16: No crater visible during respect scene - standing on flat ground

**Fix Required**: Explicitly include "impact crater on ground" and "rising from crater" in prompts

**Reference**: [TikTok - Charizard Seismic Toss](https://www.tiktok.com/@pokemon_vibez/video/7186249530302680326)

---

## FIRE SPIN

### Official Visual Characteristics
- **Form**: Swirling tornado/vortex of flames
- **Pattern**: Spiraling, rotating fire
- **Effect**: Traps opponent in vortex

### Validation Criteria
- ✅ Tornado/spiral shape
- ✅ Rotating/spinning motion
- ✅ Multiple layers of flames

### Different from Flamethrower
- Flamethrower = stream
- Fire Spin = vortex/tornado

**Reference**: [Pokemon Community - Fire Spin vs Flamethrower](https://www.pokecommunity.com/threads/fire-spin-vs-flamethrower.76589/)

---

## BATTLE DAMAGE & WEATHERING

**Source**: [Simon Gangl Realistic Pokemon Art](https://pokemonbattleart.artstation.com/projects/w8aPQX)

### Realistic Battle Damage Characteristics
Professional Pokemon artists show:
- **Scratches and scars** from previous battles
- **Worn scales** showing battle history
- **Weathered appearance** not pristine/clean
- **Battle fatigue** in later segments

### Validation Criteria for Battle-Worn Pokemon
- ✅ Visible scratches/scrapes on body
- ✅ Some scales darker/damaged
- ✅ Not perfectly clean and polished
- ✅ Signs of exertion (breathing heavy, tired eyes)

### Progressive Damage
**Early segments (1-4)**: Minimal damage, ready for battle
**Mid segments (5-10)**: Some scratches appearing
**Late segments (11-14)**: Significant battle wear
**Aftermath (15-18)**: Exhausted, battered, but victorious/respectful

**Current Failure - Seg16**: Both Pokemon look **pristine and clean** despite just finishing intense Seismic Toss battle. Should show:
- Scratches on both Pokemon
- Dust/dirt on scales
- Tired expressions
- Battle-worn appearance

**References**:
- [Realistic Pokemon Redesigns](https://icanbecreative.com/article/realistic-pokemon-characters-redesign)
- [Realistic Charizard Art](https://gamerant.com/pokemon-realistic-charizard/)

---

## SIZE RELATIONSHIP VALIDATION

### Official Heights
- **Charizard**: 5 feet 7 inches (1.7m) - Lean, athletic build
- **Dragonite**: 7 feet 3 inches (2.2m) - Bulky, muscular build
- **Size Difference**: **Dragonite is 30% taller AND bulkier**

### Visual Validation Criteria
When both Pokemon are in frame:
- ✅ Dragonite clearly larger (30%+ height difference)
- ✅ Dragonite bulkier/wider body
- ✅ Size difference obvious at first glance
- ❌ FAIL: Both Pokemon similar size
- ❌ FAIL: Charizard larger than Dragonite

**Our Results**: Generally GOOD - Size difference visible in most images

---

## PROMPT ENHANCEMENT CHECKLIST

### Based on Validation Failures

**Always Include in Prompts**:
1. **Photorealism**: "PHOTOREALISTIC hyperrealistic CGI render with detailed realistic scales"
2. **Attack Colors**: Specify exact colors (orange Flamethrower, yellow Thunder Punch, blue-purple Dragon Rage)
3. **Attack Forms**: Specify stream vs projectile vs beam vs tornado
4. **Environmental Effects**: "impact crater", "dust clouds", "debris"
5. **Battle Damage**: "scratches", "weathered", "battle-worn" (for later segments)
6. **Size Emphasis**: "significantly larger Dragonite (30% bigger)"

### Critical Details Often Missed
- Crater from Seismic Toss impact (Seg15-16)
- Battle damage accumulation (Seg16)
- Correct grip position (Seg12 - wings NOT torso)
- Tail flame color changes (blue when intense)

---

## VALIDATION WORKFLOW

### For Each Generated Image

**Step 1: Visual Style (Tier 0)**
- Check: Photorealistic scales vs 3D animation smooth
- Check: Natural lighting vs soft animation lighting
- Check: Battle weathering vs pristine clean

**Step 2: Attack Accuracy (Tier 3)**
- Compare to reference images above
- Verify colors match official sources
- Verify form (stream vs beam vs tornado)
- Check if attack originates from correct body part

**Step 3: Environmental Accuracy (Tier 2)**
- If Seismic Toss involved: CRATER MUST BE VISIBLE
- If late battle: Battle damage MUST BE VISIBLE
- Background elements match prompt

**Step 4: Pokemon Accuracy (Tier 1)**
- Body colors correct
- Size relationship correct
- Wing colors teal (BOTH Pokemon)
- Distinctive features present

---

## SOURCES

### Official Pokemon Sources
- [Bulbapedia - Ash's Charizard](https://bulbapedia.bulbagarden.net/wiki/Ash's_Charizard)
- [Bulbapedia - Flamethrower](https://bulbapedia.bulbagarden.net/wiki/Flamethrower_(move))
- [Bulbapedia - Dragon Rage](https://bulbapedia.bulbagarden.net/wiki/Dragon_Rage_(move))
- [Bulbapedia - Seismic Toss](https://bulbapedia.bulbagarden.net/wiki/Seismic_Toss_(move))
- [Bulbapedia - Thunder Punch](https://bulbapedia.bulbagarden.net/wiki/Thunder_Punch_(move))
- [Serebii - Thunder Punch](https://www.serebii.net/attackdex-xy/thunderpunch.shtml)

### Realistic Pokemon Art References
- [RJ Palmer Realistic Pokemon](https://www.rj-palmer.com/realistic-pokemon)
- [Simon Gangl Pokemon Battle Art](https://pokemonbattleart.artstation.com/projects/w8aPQX)
- [Realistic Pokemon Redesigns](https://icanbecreative.com/article/realistic-pokemon-characters-redesign)
- [Realistic Charizard - GameRant](https://gamerant.com/pokemon-realistic-charizard/)

### Anime References
- [FanVerse - Charizard Seismic Toss](https://www.fanverse.org/blogs/charizard-shows-a-true-seismic-toss-pokemon-anime.26399/)
- [Charizard Fire GIFs - Tenor](https://tenor.com/search/charizard-fire-gifs)
- [TikTok - Charizard Seismic Toss](https://www.tiktok.com/@pokemon_vibez/video/7186249530302680326)
