#!/usr/bin/env python3
"""
Generate 8-Sequence Storyboard V3 - SEQUENCE FIX

CRITICAL FIXES:
1. Panel 1: Eye Level Side Angle with STACKING ALIGNMENT
   - Both Pokemon at similar heights (both airborne)
   - Flamethrower HORIZONTAL toward Dragonite (NOT downward)
   - Clear visual line: Charizard → flame → Dragonite

2. Panel 6: Over-the-Shoulder (OTS) angle
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
    print(f"\n🎨 Generating 8-sequence V3 SEQUENCE FIX...")
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
    """Generate sequence-fixed 8-panel storyboard."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║   8-SEQUENCE STORYBOARD V3 (4x2) - SEQUENCE FIX                   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌──────────┬──────────┬──────────┬──────────┐                    ║
║  │Panel 1✓  │Panel 2   │Panel 3   │Panel 4   │                    ║
║  │Launch    │Traveling │Impact    │Burn      │                    ║
║  ├──────────┼──────────┼──────────┼──────────┤                    ║
║  │Panel 5   │Panel 6✓  │Panel 7   │Panel 8   │                    ║
║  │Anger     │OTS Charge│Thunder↗  │Thunder!  │                    ║
║  └──────────┴──────────┴──────────┴──────────┘                    ║
║                                                                    ║
║  FIX 1: Panel 1 - Stacking alignment, flame TOWARD Dragonite     ║
║  FIX 2: Panel 6 - OTS angle, charge TOWARD camera                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Fixed prompt with proper camera angles and positioning
    prompt = """
PROFESSIONAL ANIMATION STORYBOARD: 4x2 grid layout (8 panels) showing complete Pokemon battle sequence with
CORRECTED camera angles and positioning, clean comic-style panels with visible borders, professional storyboard
format, photorealistic CGI quality, EXTREMELY DETAILED large-scale rendering

TOP ROW - CHARIZARD'S FLAMETHROWER ATTACK SEQUENCE:

PANEL 1 (Top Far-Left) - FLAMETHROWER LAUNCH (EYE LEVEL SIDE ANGLE WITH STACKING):
CAMERA ANGLE: Eye Level Side Angle with professional stacking alignment (fight cinematography standard)
POSITIONING: BOTH Pokemon AIRBORNE at similar heights creating horizontal line-of-sight for proper stacking
Charizard (5'7" lean orange dragon, teal wings, cream belly, flaming tail) positioned on LEFT side HOVERING
IN MID-AIR at eye-level height, jaws opening wide launching massive orange-red Flamethrower stream from mouth
with fierce determined expression, head/neck extended forward aiming attack horizontally, wings spread for
aerial stability, significantly larger Dragonite (7'3" bulky ORANGE-TAN body, teal wings, two antennae, cream
belly stripes, NO tail flame) positioned on RIGHT side also AIRBORNE at SAME HEIGHT as Charizard creating
perfect horizontal stacking alignment, Dragonite in ready stance, camera at EYE LEVEL showing clear HORIZONTAL
visual line: Charizard's mouth → orange-red flame stream beginning → Dragonite's position, flame traveling
HORIZONTALLY through air toward target (NOT downward, NOT at ground), side-angle shot, NO SHIELD, volcanic
valley, extremely detailed horizontal stacking composition

PANEL 2 (Top Center-Left) - FLAMES TRAVELING:
CAMERA ANGLE: Eye Level Side Angle continuing stacking
Massive Flamethrower stream TRAVELING through air horizontally LEFT-TO-RIGHT between Pokemon, realistic fire
physics with heat distortion and glow, continuous orange-red flame beam mid-trajectory, Charizard on LEFT
still airborne maintaining sustained attack with effort expression, Dragonite on RIGHT watching flames approach
rapidly with concerned expression beginning to brace, both Pokemon still aerial at similar heights, side-angle
capturing full horizontal trajectory of attack, NO SHIELD, volcanic valley, extremely detailed fire rendering
showing horizontal travel

PANEL 3 (Top Center-Right) - IMPACT WITH PAIN:
CAMERA ANGLE: Eye Level medium shot on impact
Horizontal Flamethrower stream STRIKING Dragonite's torso with bright orange explosive impact burst, Dragonite
with EXTREME PAINED EXPRESSION (eyes squeezed shut, mouth wide open roaring in agony, face contorted), body
being VIOLENTLY PUSHED BACKWARD by flames force, arms raised but NO shields present, taking direct undefended
hit, Charizard on LEFT airborne still maintaining attack, side-angle capturing pain reaction and impact, NO
SHIELD, volcanic valley, extremely detailed impact effects

PANEL 4 (Top Far-Right) - BURN MARKS VISIBLE:
CAMERA ANGLE: Medium close-up on damage
Flames dissipating, Dragonite in CENTER airborne with SEVERE BURN DAMAGE (blackened scorch marks on ORANGE-TAN
torso, burnt cream belly, realistic burn texture), thick smoke rising from burns, exhausted pained expression
(eyes half-closed, gasping), body slumped mid-air, Charizard in background distance, close-up emphasizing burn
damage detail, NO SHIELD, volcanic valley, extremely detailed burn rendering

BOTTOM ROW - DRAGONITE'S COUNTER-ATTACK SEQUENCE:

PANEL 5 (Bottom Far-Left) - ANGER BUILDING:
CAMERA ANGLE: Medium close-up capturing emotion
Dragonite airborne, BURN MARKS STILL VISIBLE (blackened scorch marks on torso, burnt belly, same pattern as
Panel 4), smoke wisping from burns, facial expression TRANSFORMING from pain to FIERCE ANGER (eyes narrowing
with rage, teeth baring, eyebrows furrowing), body tensing, fists clenching, building counter-attack energy,
burn marks prominent maintaining continuity, close-up on emotional shift, NO SHIELD, volcanic valley, extremely
detailed anger expression and burn continuity

PANEL 6 (Bottom Center-Left) - CHARGING TOWARD CHARIZARD (OTS CAMERA ANGLE):
CAMERA ANGLE: Over-the-Shoulder (OTS) from behind Charizard in LEFT FOREGROUND, professional fight
cinematography stacking showing depth
Charizard (5'7" lean orange dragon with teal wings, cream belly, flaming tail) positioned in LEFT FOREGROUND
with back partially toward camera, bracing defensively with concerned alarmed expression seeing incoming threat,
arms beginning to raise, Dragonite (7'3" bulky ORANGE-TAN dragon with burn marks STILL CLEARLY VISIBLE, teal
wings spread wide, two antennae, cream belly stripes) positioned in RIGHT BACKGROUND charging FORWARD
AGGRESSIVELY TOWARD camera and toward Charizard creating unmistakable DEPTH MOVEMENT from background approaching
foreground (NOT lateral, NOT fleeing), fierce angry expression at maximum (eyes blazing with rage, teeth fully
bared), BURN MARKS VISIBLE maintaining continuity, body in dynamic forward charging motion, wings beating for
thrust, motion blur showing forward velocity TOWARD target, OTS perspective shows Dragonite as threatening
figure rapidly closing distance approaching Charizard nearest camera, professional stacking creates clear depth
alignment showing charge trajectory INTO frame depth (background → foreground, TOWARD viewer creating approach),
side-OTS angle makes direction unmistakably clear Dragonite is attacking forward NOT fleeing, NO SHIELD,
volcanic valley, extremely detailed OTS composition showing aggressive forward approach

PANEL 7 (Bottom Center-Right) - THUNDER PUNCH BEGINNING:
CAMERA ANGLE: Medium shot emphasizing electric buildup
Dragonite now very close to Charizard with electrified fist raised and pulling back for strike, bright YELLOW
ELECTRICITY crackling intensely around Dragonite's clenched fist charging Thunder Punch attack, fierce expression
showing attack intent, BURN MARKS STILL VISIBLE maintaining continuity, Charizard on LEFT with defensive worried
expression seeing electrified fist approaching at close range, arms raising to attempt blocking, electric sparks
and lightning arcs beginning to form around fist, side-angle medium shot emphasizing electric energy buildup and
imminent punch, burn marks persistent on Dragonite, NO SHIELD, volcanic valley, extremely detailed electric
effects charging

PANEL 8 (Bottom Far-Right) - THUNDER PUNCH FULL IMPACT:
CAMERA ANGLE: Close-up impact shot emphasizing connection
Dragonite's electrified fist making FULL DIRECT CONTACT with Charizard's shoulder/upper torso in devastating
Thunder Punch, massive bright YELLOW ELECTRIC EXPLOSION erupting violently at impact point, intense electricity
crackling with bright lightning arcs bursting outward in all directions, Charizard with EXTREME PAINED EXPRESSION
from electric shock (eyes squeezed shut, mouth open extremely wide roaring in agony, face severely contorted),
body being KNOCKED BACKWARD violently by punch force and electric surge, electric current visibly running through
Charizard's entire body, Dragonite on RIGHT with fierce satisfied expression landing revenge hit, BURN MARKS
STILL VISIBLE on Dragonite maintaining perfect continuity, close-up emphasizing maximum electric impact and
Charizard's extreme pain, bright yellow electric glow illuminating scene, electric sparks everywhere, NO SHIELD,
volcanic valley, extremely detailed maximum electric impact rendering

OVERALL REQUIREMENTS AND VALIDATION:
- Professional 4x2 grid with 8 clear panels and highly visible borders
- Reading order: left-to-right top (1-2-3-4), left-to-right bottom (5-6-7-8)
- 95%+ character consistency (Nano Banana Pro standard)
- Charizard consistent: orange body, teal wings, cream belly, flaming tail, lean 5'7\" throughout
- Dragonite consistent: ORANGE-TAN body (NEVER green), teal wings, cream belly stripes, two antennae,
  NO tail flame ever, bulky 7'3\" (30% larger) throughout
- CRITICAL PANEL 1 FIX: Eye Level Side Angle with stacking alignment, BOTH Pokemon AIRBORNE at same height,
  Flamethrower traveling HORIZONTALLY toward Dragonite (NOT downward), clear horizontal visual line creating
  professional stacking
- CRITICAL PANEL 6 FIX: Over-the-Shoulder (OTS) from behind Charizard showing Dragonite charging TOWARD
  camera/Charizard creating depth movement (background→foreground), NOT lateral or fleeing
- Professional stacking: Panel 1 horizontal attack alignment, Panel 6 depth charge alignment
- Element continuity: burn marks ABSENT Panels 1-2-3, APPEAR Panel 4, PERSIST Panels 5-6-7-8 with perfect
  consistency
- Extended sequence: Panels 7-8 show complete Thunder Punch counter-attack (buildup → impact)
- NO SHIELDS in any of 8 panels (ABSOLUTELY CRITICAL)
- NO defensive barriers in any panel
- Extremely detailed large-scale rendering all panels
- Professional fight cinematography throughout
- 16:9 aspect ratio, photorealistic CGI quality
- Volcanic valley background consistent
"""

    output_path = "charizard/battle_assets/storyboard_8sequence_v3_sequence_fix.jpg"

    try:
        image_path, task_id = generate_storyboard(prompt, output_path, api_key)

        print(f"\n{'='*70}")
        print(f"🎉 8-SEQUENCE V3 SEQUENCE FIX COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n✅ CRITICAL FIXES APPLIED:")
        print(f"  ✓ Panel 1: Eye Level Side Angle with STACKING ALIGNMENT")
        print(f"  ✓ Panel 1: Both Pokemon AIRBORNE at SAME HEIGHT")
        print(f"  ✓ Panel 1: Flamethrower HORIZONTAL toward Dragonite (NOT downward)")
        print(f"  ✓ Panel 1: Clear visual line: mouth → flame → target")
        print(f"  ✓ Panel 6: OTS from behind Charizard")
        print(f"  ✓ Panel 6: Dragonite in BACKGROUND charging TOWARD foreground")
        print(f"  ✓ Panel 6: Depth movement showing approach")
        print(f"  ✓ Panel 7: Thunder Punch charging")
        print(f"  ✓ Panel 8: Thunder Punch devastating impact")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  [ ] Panel 1: BOTH Pokemon airborne at SAME HEIGHT?")
        print(f"  [ ] Panel 1: Flamethrower HORIZONTAL (not downward)?")
        print(f"  [ ] Panel 1: Flame aimed AT Dragonite?")
        print(f"  [ ] Panel 1: Clear stacking alignment visible?")
        print(f"  [ ] Panel 6: Camera behind Charizard (OTS)?")
        print(f"  [ ] Panel 6: Dragonite approaching FROM background?")
        print(f"  [ ] Panel 6: Dragonite getting CLOSER (not fleeing)?")
        print(f"  [ ] Panel 7: Electric fist charging?")
        print(f"  [ ] Panel 8: Thunder Punch hitting with impact?")
        print(f"  [ ] Burn marks continuous panels 4-5-6-7-8?")
        print(f"  [ ] ❌ NO SHIELDS in any of 8 panels?")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
