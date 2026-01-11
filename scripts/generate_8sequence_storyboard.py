#!/usr/bin/env python3
"""
Generate 8-Sequence Storyboard (4x2 Grid)

Most detailed battle sequence with maximum progression detail:
1. Pre-Attack Stance
2. Flamethrower Launch
3. Flames Traveling
4. Impact Beginning
5. Full Impact with Pain
6. Burn Marks Visible
7. Anger Building
8. Revenge Charge

Following Nano Banana Pro best practices and complete validation framework.
"""

import os
import sys
import requests
import json
import time
from PIL import Image


def load_api_key():
    """Load API key from .env file."""
    env_paths = ['.env', '/home/user/forestry-demo/.env', 'scripts/.env']
    for path in env_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('KIE_API_KEY='):
                        return line.strip().split('=', 1)[1]
    raise Exception("❌ KIE_API_KEY not found")


def generate_storyboard(prompt: str, output_path: str, api_key: str) -> tuple:
    """Generate storyboard using Nano Banana Pro."""
    print(f"\n🎨 Generating 8-sequence storyboard...")
    print(f"📝 Prompt length: {len(prompt)} characters")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "output_format": "jpg"
        }
    }

    print(f"🚀 Submitting to Nano Banana Pro...")
    start_time = time.time()

    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    result = response.json()
    if result.get("code") != 200:
        raise Exception(f"Failed: {result.get('msg')}")

    task_id = result["data"]["taskId"]
    print(f"Task ID: {task_id}")
    print(f"⏳ Generating... ", end="", flush=True)

    while time.time() - start_time < 120:
        time.sleep(5)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            if data.get("state") == "success":
                print(f"\n✅ Generated!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                img_resp = requests.get(image_url, timeout=60)
                if img_resp.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(img_resp.content)

                    img = Image.open(output_path)
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    duration = time.time() - start_time

                    print(f"✅ Saved: {img.size[0]}x{img.size[1]}, {size_mb:.2f} MB")
                    print(f"⏱️  Time: {duration:.1f}s")

                    return output_path, task_id

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Generate 8-sequence storyboard."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           8-SEQUENCE STORYBOARD (4x2 Grid)                         ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌────────┬────────┬────────┬────────┐                            ║
║  │Panel 1 │Panel 2 │Panel 3 │Panel 4 │                            ║
║  │Stance  │Launch  │Travel  │Begin   │                            ║
║  ├────────┼────────┼────────┼────────┤                            ║
║  │Panel 5 │Panel 6 │Panel 7 │Panel 8 │                            ║
║  │Impact  │Burn    │Anger   │Charge  │                            ║
║  └────────┴────────┴────────┴────────┘                            ║
║                                                                    ║
║  Maximum detail with frame-by-frame progression                    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Extremely detailed 8-panel prompt with complete validation framework
    prompt = """
PROFESSIONAL ANIMATION STORYBOARD: 4x2 grid layout (8 panels) showing maximum detail Pokemon battle sequence,
clean comic-style panels with visible borders separating each panel, professional storyboard format for animation,
photorealistic CGI render quality, cinematic composition, EXTREMELY DETAILED AND LARGE-SCALE rendering

TOP ROW - ATTACK INITIATION AND EXECUTION:

PANEL 1 (Top Far-Left) - PRE-ATTACK BATTLE STANCE:
Charizard (5'7" lean athletic orange dragon with extremely detailed realistic reptilian scales showing individual scale
texture and depth, teal turquoise wing undersides clearly visible with membrane texture, cream belly, bright flaming
tail tip burning, sharp claws visible) on LEFT side in aggressive pre-attack stance with body coiled and tense, wings
partially spread showing readiness, jaws beginning to open, eyes focused intensely on target with fierce determined
expression, significantly larger Dragonite (7'3" bulky stocky muscular ORANGE-TAN body with detailed realistic scales,
teal wing membranes, two thin curved antennae on head clearly visible, cream belly with horizontal stripe pattern,
NO tail flame ever) on RIGHT side in defensive ready stance, both Pokemon facing each other in tense standoff moment
before attack begins, side-angle wide dramatic shot showing both combatants clearly, volcanic valley background with
dramatic lighting and rim light, NO SHIELD on Dragonite, NO defensive barriers anywhere, both completely unprotected,
extremely detailed photorealistic quality, professional animation storyboard composition

PANEL 2 (Top Center-Left) - FLAMETHROWER LAUNCH INITIATION:
Charizard now with jaws WIDE OPEN showing all teeth, throat glowing bright orange-red from building fire energy inside,
flames just beginning to burst forth from open mouth in initial massive explosion of fire, fierce attacking facial
expression at maximum intensity (eyes narrowed to slits, teeth bared fully, face showing aggressive determination),
teal wings spread wide for stability and power, body in full attacking pose, initial bright orange-red Flamethrower
stream just starting to extend from mouth with brilliant glow at origin point, Dragonite on RIGHT watching attack
begin with alert concerned expression starting to show apprehension, body tensing in anticipation, NO SHIELD, NO
defensive barriers, completely exposed and vulnerable, side-angle medium-wide shot capturing attack initiation moment,
volcanic valley, dramatic lighting emphasizing flame brightness at launch, extremely detailed fire rendering starting,
realistic CGI quality

PANEL 3 (Top Center-Right) - FLAMES TRAVELING MID-TRAJECTORY:
Massive sustained orange-red Flamethrower stream now fully formed and TRAVELING across frame from LEFT to RIGHT in
mid-air trajectory, flames showing realistic fire physics with turbulent motion, bright orange-red core with brilliant
yellow-white hottest center, heat distortion waves visibly rippling in air around flame stream, sparks and burning
embers trailing behind, Charizard on LEFT still maintaining powerful attack with jaws wide open and fierce expression,
teal wings spread for stability, Dragonite on RIGHT watching incoming flames with growing concern and fear visible on
face (eyes widening, expression showing apprehension), body beginning to tense and brace for inevitable impact, arms
starting to raise instinctively but NO shields forming, NO defensive barriers appearing, completely undefended against
incoming flames, side-angle medium shot capturing complete flame trajectory in motion between both Pokemon, volcanic
valley background, dramatic lighting, extremely detailed realistic fire rendering with physics, photorealistic quality

PANEL 4 (Top Far-Right) - IMPACT BEGINNING / FIRST CONTACT:
Flamethrower stream making FIRST CONTACT with Dragonite's torso, beginning of impact showing initial bright orange
glow starting to form at contact point on body, flames just starting to engulf torso area, Dragonite's facial expression
showing INITIAL PAIN REACTION beginning (eyes starting to squint from heat, mouth beginning to open, eyebrows starting
to furrow, face showing first moment of distress), body just beginning to react to force with slight backward lean
starting, arms raising higher instinctively but still NO shields or barriers protecting, flames spreading across torso
surface, initial heat distortion at impact point, Charizard on LEFT maintaining full attack power, side-angle medium
shot emphasizing moment of first impact contact, volcanic valley, extremely detailed impact beginning rendering,
realistic CGI quality

BOTTOM ROW - IMPACT PEAK, DAMAGE, AND REVENGE:

PANEL 5 (Bottom Far-Left) - FULL IMPACT WITH MAXIMUM PAIN:
Massive Flamethrower stream now FULLY STRIKING Dragonite's entire torso and belly with maximum force, brilliant bright
orange-yellow-white impact burst explosion at contact zone, intense heat distortion and fire sparks exploding violently
outward in all directions from impact, Dragonite with EXTREME MAXIMUM PAINED FACIAL EXPRESSION at peak intensity (eyes
squeezed completely shut from overwhelming pain and heat, mouth opened to absolute maximum showing all teeth in agonized
roar of suffering, face severely and deeply contorted in extreme distress, eyebrows furrowed to maximum, entire face
showing unbearable intense suffering), body being VIOLENTLY THROWN BACKWARD by overwhelming sustained force of flames
with dramatic knockback motion visible, upper body and head thrown far back, arms raised to absolute maximum in
completely failed desperate defensive gesture but still NO barriers or shields present anywhere, taking full direct
undefended hit at maximum intensity, bright orange-yellow impact glow illuminating entire scene dramatically, Charizard
on LEFT maintaining peak attack power, side-angle medium-close shot emphasizing Dragonite's extreme pain reaction and
violent physical knockback, volcanic valley, NO SHIELD, NO defensive barriers, NO protective elements anywhere,
extremely detailed maximum impact effects and extreme pain expression rendering, photorealistic CGI quality

PANEL 6 (Bottom Center-Left) - BURN MARKS NEWLY VISIBLE:
Flames now dissipating and fading away, smoke and embers still in air, Dragonite in CENTER of frame showing HIGHLY
VISIBLE SEVERE FRESH BURN DAMAGE newly appeared from Flamethrower impact (extensive large blackened burnt scorch marks
and deeply charred patterns across entire ORANGE-TAN torso, severe burn damage across cream belly with dark black scorch
marks, realistic detailed burn texture showing damaged and charred scales with depth), thick heavy smoke wisping and
rising from multiple burnt areas across body showing fresh heat damage aftermath still hot, Dragonite's facial expression
showing residual lingering pain and exhaustion (eyes half-closed wearily, mouth slightly open gasping, face showing
severe exhaustion and hurt from damage received), body slumped and sagging from exhaustion and damage taken, arms
lowered weakly to sides, posture showing defeat momentarily, Charizard visible in background distance having completed
attack successfully, medium close-up shot centered on Dragonite emphasizing extensive severe burn damage detail and
realistic texture, thick smoke effects realistic, volcanic valley background, NO SHIELD on Dragonite, battle damage
clearly visible severe and fresh, extremely detailed burn texture and damage rendering showing char depth, photorealistic
quality

PANEL 7 (Bottom Center-Right) - ANGER BUILDING AND TRANSITIONING:
Same Dragonite still in CENTER, burn marks STILL HIGHLY VISIBLE and persistent from Panel 6 maintaining perfect
continuity (same blackened scorch marks on torso, same burnt cream belly, exact same damage pattern continuing), smoke
still actively wisping from burnt scales showing damage is very fresh and hot, but facial expression now RAPIDLY
TRANSITIONING and TRANSFORMING from exhausted pain to FIERCE BUILDING INTENSE ANGER and vengeful rage (eyes opening
wider and narrowing simultaneously with growing determination and fury, pupils contracting with rage, eyebrows beginning
to furrow deeply and aggressively in building anger, teeth starting to bare in aggressive snarl showing intent to
retaliate and strike back, face transforming dramatically from hurt exhaustion to vengeful burning fury), body language
shifting visibly from slumped exhaustion to tensing with building energy and rage, muscles beginning to tighten visibly,
shoulders rising, fists beginning to clench with building power, energy building for counter-attack visibly, burn marks
remaining prominent and consistent showing battle damage continuity perfectly, medium close-up capturing complete
emotional transformation process and building intensity, Charizard still visible in background now appearing concerned,
volcanic valley, NO SHIELD on Dragonite, burn damage persistent and consistent, extremely detailed facial expression
showing gradual emotional shift from pain exhaustion to building rage, photorealistic quality

PANEL 8 (Bottom Far-Right) - REVENGE CHARGE AT MAXIMUM SPEED:
Dragonite now CHARGING FORWARD AGGRESSIVELY at absolute maximum speed in full dynamic attacking charge pose, teal
wings spread absolutely wide and pulled completely back for maximum acceleration thrust and power, fierce angry facial
expression now at absolute peak maximum intensity (eyes blazing intensely with pure rage and vengeance, teeth fully
completely bared in maximum aggressive snarl showing all teeth, eyebrows furrowed to absolute maximum showing peak
fury, entire face showing complete vengeful determination and rage at highest level), BURN MARKS STILL HIGHLY VISIBLE
and persistent on battle-worn damaged ORANGE-TAN body maintaining perfect damage continuity from Panels 6 and 7 (same
blackened scorch marks clearly visible on torso, same burnt patterns on cream belly, same realistic damage texture
persisting perfectly), body in full forward charging motion at high speed with extremely dynamic pose showing maximum
speed and aggressive intent, motion blur visible on charging body emphasizing extreme velocity, smaller Charizard (5'7"
lean orange dragon with teal wings, cream belly, flaming tail) visible on LEFT side of frame now bracing defensively
for incoming powerful counter-attack with defensive worried stance and concerned alarmed expression showing fear,
side-angle extreme dynamic action shot capturing maximum charge momentum and escalating battle tension, strong motion
blur effects, volcanic valley background, NO SHIELD on Dragonite, NO defensive barriers anywhere, burn marks prominent
consistent and persistent perfectly, extremely detailed motion effects and persistent battle damage rendering,
photorealistic CGI quality at highest level

OVERALL STORYBOARD REQUIREMENTS AND COMPLETE VALIDATION FRAMEWORK:
- Professional 4x2 grid layout with 8 clear panels and highly visible borders separating each panel distinctly
- Reading order: left-to-right top row (1-2-3-4), then left-to-right bottom row (5-6-7-8) clearly defined
- 95%+ character consistency across ALL 8 panels meeting Nano Banana Pro professional standard
- Charizard perfectly consistent all panels: orange body, teal wings, cream belly, flaming tail, lean athletic build, 5'7"
- Dragonite perfectly consistent all panels: ORANGE-TAN body (NEVER green), teal wings, cream belly stripes, two antennae,
  NO tail flame ever, bulky stocky build, 7'3" height (consistently 30% larger than Charizard)
- Frame-by-frame maximum detail action continuity: stance → launch → travel → begin → impact → burn → anger → charge
- Element continuity CRITICAL: burn marks completely ABSENT in Panels 1-2-3-4-5, first APPEAR in Panel 6, then PERSIST
  identically in Panels 7-8 with perfect consistency
- ABSOLUTELY NO SHIELDS in any panel (1, 2, 3, 4, 5, 6, 7, or 8) - CRITICAL VALIDATION
- ABSOLUTELY NO defensive barriers in any panel - CRITICAL VALIDATION
- ABSOLUTELY NO force fields or protective elements in any panel - CRITICAL VALIDATION
- EXTREMELY DETAILED AND LARGE-SCALE rendering for all 8 panels with maximum quality
- Crystal clear narrative progression visible across complete 8-panel sequence
- Smooth professional visual transitions between all adjacent panels
- Photorealistic CGI quality throughout entire storyboard at highest level
- 16:9 aspect ratio maintained, professional animation storyboard composition
- Volcanic valley background perfectly consistent across all 8 panels
- All validation framework requirements met (Tier 0-3, technical specs, NO NEW ELEMENTS, storyboard continuity)
"""

    output_path = "charizard/battle_assets/storyboard_8sequence_4x2grid.jpg"

    try:
        image_path, task_id = generate_storyboard(prompt, output_path, api_key)

        print(f"\n{'='*70}")
        print(f"🎉 8-SEQUENCE STORYBOARD COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  [ ] 4x2 grid with 8 clear panels?")
        print(f"  [ ] Panel borders visible separating each?")
        print(f"  [ ] Panel 1: Pre-attack stance?")
        print(f"  [ ] Panel 2: Flamethrower launch?")
        print(f"  [ ] Panel 3: Flames traveling?")
        print(f"  [ ] Panel 4: Impact beginning?")
        print(f"  [ ] Panel 5: Full impact with pain?")
        print(f"  [ ] Panel 6: Burn marks visible?")
        print(f"  [ ] Panel 7: Anger building?")
        print(f"  [ ] Panel 8: Revenge charge?")
        print(f"  [ ] Character consistency 95%+ across all 8?")
        print(f"  [ ] ❌ NO SHIELDS in ANY of the 8 panels?")
        print(f"  [ ] ❌ NO defensive barriers in ANY panel?")
        print(f"  [ ] Burn marks absent 1-2-3-4-5, appear in 6, persist in 7-8?")
        print(f"  [ ] Narrative flow logical across all 8?")
        print(f"  [ ] Extremely detailed rendering?")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
