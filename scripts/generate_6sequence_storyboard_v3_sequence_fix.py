#!/usr/bin/env python3
"""
Generate 6-Sequence Storyboard V3 - SEQUENCE FIX

CRITICAL FIXES:
1. Panel 1: Eye Level Side Angle with STACKING ALIGNMENT
   - Both Pokemon at similar heights (both airborne)
   - Flamethrower HORIZONTAL toward Dragonite (NOT downward)
   - Clear visual line: Charizard → flame → Dragonite

2. Panel 5: Over-the-Shoulder (OTS) angle
   - Dragonite charging TOWARD camera/Charizard (depth movement)
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
    print(f"\n🎨 Generating 6-sequence V3 SEQUENCE FIX...")
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
    """Generate sequence-fixed 6-panel storyboard."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║   6-SEQUENCE STORYBOARD V3 (3x2) - SEQUENCE FIX                   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌─────────────┬─────────────┬─────────────┐                      ║
║  │ Panel 1:    │ Panel 2:    │ Panel 3:    │                      ║
║  │ Launch ✓    │ Impact      │ Burn Marks  │                      ║
║  ├─────────────┼─────────────┼─────────────┤                      ║
║  │ Panel 4:    │ Panel 5:    │ Panel 6:    │                      ║
║  │ Anger       │ OTS Charge✓ │ Thunder!    │                      ║
║  └─────────────┴─────────────┴─────────────┘                      ║
║                                                                    ║
║  FIX 1: Panel 1 - Stacking alignment, flame TOWARD Dragonite     ║
║  FIX 2: Panel 5 - OTS angle, charge TOWARD camera                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Fixed prompt with proper camera angles and positioning
    prompt = """
PROFESSIONAL ANIMATION STORYBOARD: 3x2 grid layout (6 panels) showing Pokemon battle sequence with
CORRECTED camera angles and positioning, clean comic-style panels with visible borders, professional
storyboard format, photorealistic CGI quality, EXTREMELY DETAILED large-scale rendering

TOP ROW - CHARIZARD'S FLAMETHROWER ATTACK:

PANEL 1 (Top-Left) - FLAMETHROWER LAUNCH (EYE LEVEL SIDE ANGLE WITH STACKING):
CAMERA ANGLE: Eye Level Side Angle with professional stacking alignment (fight cinematography standard)
POSITIONING: BOTH Pokemon AIRBORNE at similar heights creating horizontal line-of-sight for proper stacking
Charizard (5'7" lean orange dragon, teal wings, cream belly, flaming tail) positioned on LEFT side HOVERING
IN MID-AIR at eye-level height, jaws open wide launching massive orange-red Flamethrower stream from mouth
with fierce determined expression, head/neck extended forward aiming attack, wings spread for aerial stability,
tail flame intensified during attack, significantly larger Dragonite (7'3" bulky ORANGE-TAN body, teal wings
spread, two antennae, cream belly stripes, NO tail flame) positioned on RIGHT side also AIRBORNE at SAME
HEIGHT as Charizard creating perfect horizontal stacking alignment, Dragonite in ready defensive stance seeing
flames approaching with concerned bracing expression, camera positioned at EYE LEVEL showing clear HORIZONTAL
visual line creating professional stacking: Charizard's mouth → orange-red flame stream trajectory → Dragonite's
position, flame traveling HORIZONTALLY through air toward Dragonite (NOT downward, NOT at ground), BOTH Pokemon
at matching heights for proper fight composition, side-angle shot captures full horizontal attack path from
source to target with perfect stacking, volcanic valley background with mountains, clear blue sky showing
aerial positioning, NO SHIELD on either Pokemon, extremely detailed professional stacking composition with
horizontal flame trajectory

PANEL 2 (Top-Center) - IMPACT WITH PAIN:
CAMERA ANGLE: Eye Level medium shot on impact reaction
Massive horizontal Flamethrower stream STRIKING Dragonite's torso center-mass with bright orange explosive
impact burst, Dragonite with EXTREME PAINED EXPRESSION (eyes squeezed shut in agony, mouth wide open roaring
in pain, face severely contorted showing distress), body being VIOLENTLY PUSHED BACKWARD through air by
overwhelming flames force with visible knockback motion, arms raised defensively but NO shields or barriers
present anywhere, taking full direct undefended hit to torso, Charizard on LEFT still airborne maintaining
sustained Flamethrower attack with effort expression, both Pokemon still aerial, side-angle shot capturing
maximum pain reaction and impact effects, bright orange impact glow, NO SHIELD, volcanic valley, extremely
detailed impact and pain expression rendering

PANEL 3 (Top-Right) - BURN MARKS VISIBLE:
CAMERA ANGLE: Medium close-up centered on battle damage detail
Flamethrower attack ending with flames dissipating into smoke, Dragonite in CENTER frame still airborne with
HIGHLY VISIBLE SEVERE BURN DAMAGE across body (large blackened scorch marks covering significant area of
ORANGE-TAN torso, burnt cream belly with dark char marks showing heat damage, realistic burn texture with
damaged scales), thick smoke wisping upward from burnt areas showing fresh heat damage still smoldering,
Dragonite's expression showing residual pain and exhaustion (eyes half-closed from pain, mouth slightly open
gasping for air, face showing hurt and fatigue), body slumped mid-air from damage impact, wings drooping
slightly, Charizard visible in background distance still aerial, medium close-up emphasizing burn damage
detail and realistic burn texture, smoke trails visible, NO SHIELD, volcanic valley, extremely detailed burn
rendering with texture

BOTTOM ROW - DRAGONITE'S COUNTER-ATTACK SEQUENCE:

PANEL 4 (Bottom-Left) - ANGER BUILDING:
CAMERA ANGLE: Medium close-up capturing emotional transformation
Same Dragonite still airborne, BURN MARKS STILL HIGHLY VISIBLE maintaining perfect continuity (blackened
scorch marks prominent on torso, burnt cream belly with char marks, same burn pattern as Panel 3), smoke
still wisping from burns showing damage persistence, facial expression TRANSFORMING dramatically from pain
to FIERCE VENGEFUL ANGER (eyes narrowing intensely with rage building, teeth baring in aggressive snarl
showing fury, eyebrows furrowing deeply, facial muscles tensing), body language shifting from slumped
exhaustion to tensing with building counter-attack energy, fists clenching with determination, preparing
revenge strike, burn marks prominent and consistent with Panel 3 pattern, medium close-up on face showing
dramatic emotional shift from hurt to fury, Charizard in background, NO SHIELD, volcanic valley, extremely
detailed anger expression and burn mark continuity

PANEL 5 (Bottom-Center) - CHARGING TOWARD CHARIZARD (OTS CAMERA ANGLE):
CAMERA ANGLE: Over-the-Shoulder (OTS) from behind Charizard in LEFT FOREGROUND, professional fight
cinematography stacking technique showing depth
Charizard (5'7" lean orange dragon with teal wings, cream belly, flaming tail) positioned in LEFT FOREGROUND
with back partially visible toward camera, bracing defensively with concerned alarmed expression turning head
to look at approaching threat, arms beginning to raise protectively, Dragonite (7'3" bulky ORANGE-TAN dragon
with burn marks STILL CLEARLY VISIBLE on torso from Panels 3-4, teal wings spread wide for maximum acceleration,
two antennae, cream belly stripes with burn damage) positioned in RIGHT BACKGROUND charging FORWARD AGGRESSIVELY
TOWARD camera and toward Charizard in fierce attacking approach creating unmistakable DEPTH MOVEMENT from
background rapidly approaching foreground (NOT lateral movement, NOT flying away, NOT running past), fierce
vengeful angry expression at absolute maximum intensity (eyes blazing with pure rage, teeth fully bared showing
attack intent, face showing fury), BURN MARKS STILL VISIBLE maintaining perfect continuity, body in dynamic
forward charging motion with speed and aggression, wings beating powerfully for thrust, motion blur emphasizing
forward velocity TOWARD target, over-the-shoulder perspective clearly shows Dragonite as threatening figure
rapidly closing distance approaching Charizard who is nearest to camera position, professional stacking creates
clear visual depth alignment showing aggressive charge trajectory moving INTO frame depth (Dragonite traveling
from far → near, background position → foreground position, TOWARD Charizard and viewer creating approach),
side-OTS angle composition makes direction unmistakably clear that Dragonite is attacking forward NOT fleeing
or flying past, volcanic valley background, NO SHIELD on either Pokemon, extremely detailed OTS composition
showing menacing aggressive forward approach with depth

PANEL 6 (Bottom-Right) - THUNDER PUNCH IMPACT:
CAMERA ANGLE: Close-up impact shot emphasizing connection point and electric effect
Dragonite's electrified fist making FULL DIRECT CONTACT with Charizard's shoulder/upper torso in devastating
Thunder Punch counter-attack revenge strike, massive bright YELLOW ELECTRIC EXPLOSION erupting violently at
impact point, intense electricity crackling with bright lightning arcs and electric bolts bursting outward
in all directions, Charizard with EXTREME PAINED EXPRESSION from electric shock (eyes squeezed tightly shut
from pain, mouth open extremely wide roaring in agony from electricity, face severely contorted showing
maximum pain), body being KNOCKED BACKWARD violently through air by combined punch force and electric surge,
bright yellow electric current visibly running through Charizard's entire body causing visible shock effect,
Dragonite on RIGHT with fierce satisfied vengeful expression showing satisfaction landing revenge hit after
taking Flamethrower burn damage, BURN MARKS STILL CLEARLY VISIBLE on Dragonite's body maintaining absolute
perfect continuity from Panels 3-4-5, close-up shot emphasizing maximum electric impact point and Charizard's
extreme pain reaction to electricity, bright yellow electric glow illuminating entire scene dramatically,
electric sparks and lightning everywhere, volcanic valley, NO SHIELD, extremely detailed maximum electric
impact rendering with bright effects

OVERALL STORYBOARD REQUIREMENTS AND VALIDATION:
- Professional 3x2 grid with 6 clear distinct panels and highly visible borders
- Reading order: left-to-right top row (1-2-3), left-to-right bottom row (4-5-6)
- 95%+ character consistency across all 6 panels (Nano Banana Pro standard)
- Charizard consistent: orange body, teal wings, cream belly, flaming tail, lean build, 5'7\" throughout
- Dragonite consistent: ORANGE-TAN body (NEVER green), teal wings, cream belly stripes, two antennae,
  NO tail flame ever, bulky build, 7'3\" (30% larger) throughout
- CRITICAL PANEL 1 FIX: Eye Level Side Angle with stacking alignment, BOTH Pokemon AIRBORNE at same height,
  Flamethrower traveling HORIZONTALLY toward Dragonite (NOT downward at ground), clear horizontal visual
  line from Charizard's mouth → flame → Dragonite creating professional fight stacking
- CRITICAL PANEL 5 FIX: Over-the-Shoulder (OTS) from behind Charizard showing Dragonite charging TOWARD
  camera/Charizard creating depth movement (background→foreground approach), NOT lateral or fleeing
- Professional stacking techniques: Panel 1 horizontal attack alignment, Panel 5 depth charge alignment
- Element continuity: burn marks ABSENT Panels 1-2, APPEAR Panel 3, PERSIST Panels 4-5-6 with perfect
  consistency in pattern and location
- NO SHIELDS in any of 6 panels (1, 2, 3, 4, 5, or 6) - ABSOLUTELY CRITICAL
- NO defensive barriers in any panel ever
- Extremely detailed large-scale rendering for all panels with maximum detail
- Clear narrative progression: horizontal launch → impact → burn → anger → charge TOWARD → electric revenge
- Professional fight cinematography techniques applied throughout all panels
- 16:9 aspect ratio, photorealistic CGI quality throughout
- Volcanic valley background consistent all panels
"""

    output_path = "charizard/battle_assets/storyboard_6sequence_v3_sequence_fix.jpg"

    try:
        image_path, task_id = generate_storyboard(prompt, output_path, api_key)

        print(f"\n{'='*70}")
        print(f"🎉 6-SEQUENCE V3 SEQUENCE FIX COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n✅ CRITICAL FIXES APPLIED:")
        print(f"  ✓ Panel 1: Eye Level Side Angle with STACKING ALIGNMENT")
        print(f"  ✓ Panel 1: Both Pokemon AIRBORNE at SAME HEIGHT")
        print(f"  ✓ Panel 1: Flamethrower HORIZONTAL toward Dragonite (NOT downward)")
        print(f"  ✓ Panel 1: Clear visual line: mouth → flame → target")
        print(f"  ✓ Panel 5: OTS from behind Charizard")
        print(f"  ✓ Panel 5: Dragonite in BACKGROUND charging TOWARD foreground")
        print(f"  ✓ Panel 5: Depth movement showing approach")
        print(f"  ✓ Panel 6: Thunder Punch impact (extended scene)")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  [ ] Panel 1: BOTH Pokemon airborne at SAME HEIGHT?")
        print(f"  [ ] Panel 1: Flamethrower HORIZONTAL (not downward)?")
        print(f"  [ ] Panel 1: Flame aimed AT Dragonite?")
        print(f"  [ ] Panel 1: Clear stacking alignment visible?")
        print(f"  [ ] Panel 5: Camera behind Charizard (OTS)?")
        print(f"  [ ] Panel 5: Dragonite approaching FROM background?")
        print(f"  [ ] Panel 5: Dragonite getting CLOSER (not fleeing)?")
        print(f"  [ ] Burn marks continuous panels 3-4-5-6?")
        print(f"  [ ] ❌ NO SHIELDS in any panel?")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
