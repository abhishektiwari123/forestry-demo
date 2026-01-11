#!/usr/bin/env python3
"""
Generate 6-Sequence Storyboard V3 - CAMERA ANGLE FIX

Uses professional cinematography techniques:
- Over-the-Shoulder (OTS) camera positioning
- Stacking (visual alignment)
- Depth movement (TOWARD camera) not lateral movement

CRITICAL FIX: Panel 5 uses OTS angle showing Dragonite charging TOWARD Charizard/camera
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
    print(f"\n🎨 Generating 6-sequence storyboard V3 (CAMERA ANGLE FIX)...")
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
    """Generate camera-angle-corrected 6-sequence storyboard."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║      6-SEQUENCE STORYBOARD V3 (3x2) - CAMERA ANGLE FIX            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌─────────────┬─────────────┬─────────────┐                      ║
║  │ Panel 1:    │ Panel 2:    │ Panel 3:    │                      ║
║  │ Launch      │ Impact      │ Burn Marks  │                      ║
║  ├─────────────┼─────────────┼─────────────┤                      ║
║  │ Panel 4:    │ Panel 5:    │ Panel 6:    │                      ║
║  │ Anger       │ OTS Charge→ │ Thunder!    │                      ║
║  └─────────────┴─────────────┴─────────────┘                      ║
║                                                                    ║
║  FIX: Panel 5 uses Over-the-Shoulder camera angle                 ║
║       Dragonite charging TOWARD Charizard/camera (depth)          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # V3 prompt with professional camera angles from cinematography guide
    prompt = """
PROFESSIONAL ANIMATION STORYBOARD: 3x2 grid layout (6 panels) showing extended Pokemon battle sequence,
clean comic-style panels with visible borders, professional storyboard format for animation,
photorealistic CGI quality, cinematic composition, EXTREMELY DETAILED large-scale rendering

TOP ROW - CHARIZARD'S FLAMETHROWER ATTACK:

PANEL 1 (Top-Left) - FLAMETHROWER LAUNCH:
CAMERA ANGLE: Eye Level Side Angle with stacking alignment (professional fight cinematography)
Charizard (5'7" lean orange dragon, teal wings, cream belly, flaming tail) on LEFT side launching massive
orange-red Flamethrower from open jaws with fierce expression, significantly larger Dragonite (7'3" bulky
ORANGE-TAN body, teal wings, two antennae, cream belly stripes, NO tail flame) on RIGHT side ready stance,
camera positioned to show clear visual line from Charizard's mouth → flame stream → Dragonite creating
professional stacking, side-angle shot, volcanic valley background, NO SHIELD, extremely detailed

PANEL 2 (Top-Center) - IMPACT WITH PAIN:
CAMERA ANGLE: Eye Level medium shot emphasizing impact reaction
Massive Flamethrower stream STRIKING Dragonite's torso with bright orange impact burst, Dragonite with
EXTREME PAINED EXPRESSION (eyes squeezed shut, mouth wide open roaring in agony, face severely contorted
in distress), body being VIOLENTLY PUSHED BACKWARD by overwhelming flames force with visible knockback,
arms raised defensively but NO shields or barriers present, taking full direct undefended hit, Charizard
on LEFT maintaining attack, side-angle shot capturing pain reaction, NO SHIELD, volcanic valley, extremely
detailed impact effects and pain expression

PANEL 3 (Top-Right) - BURN MARKS VISIBLE:
CAMERA ANGLE: Medium close-up centered on damage detail
Flames dissipating, Dragonite in CENTER with HIGHLY VISIBLE SEVERE BURN DAMAGE (large blackened scorch marks
across ORANGE-TAN torso, burnt cream belly with dark char marks, realistic burn texture showing damaged scales),
thick smoke wisping from burnt areas showing fresh heat damage, Dragonite's expression showing residual pain
and exhaustion (eyes half-closed, mouth slightly open gasping, face showing hurt), body slumped from damage,
Charizard visible in background distance, close-up emphasizing burn damage detail and texture, NO SHIELD,
volcanic valley, extremely detailed burn rendering

BOTTOM ROW - DRAGONITE'S COUNTER-ATTACK SEQUENCE:

PANEL 4 (Bottom-Left) - ANGER BUILDING:
CAMERA ANGLE: Medium close-up capturing emotional transformation
Same Dragonite, BURN MARKS STILL VISIBLE maintaining continuity (blackened scorch marks on torso, burnt
cream belly), smoke still wisping from burns, facial expression TRANSFORMING from pain to FIERCE ANGER
(eyes narrowing with rage, teeth baring in aggressive snarl, eyebrows furrowing deeply), body language
shifting from slumped to tensing with building energy, fists clenching, preparing counter-attack, burn
marks prominent and consistent, medium close-up on face showing emotional shift from exhaustion to vengeful
fury, Charizard in background, NO SHIELD, volcanic valley, extremely detailed anger expression transition

PANEL 5 (Bottom-Center) - CHARGING TOWARD CHARIZARD (OTS CAMERA ANGLE):
CAMERA ANGLE: Over-the-Shoulder (OTS) from behind Charizard in LEFT FOREGROUND looking outward, professional
fight cinematography stacking technique
Charizard (5'7" lean orange dragon with teal wings, cream belly, flaming tail) positioned in LEFT FOREGROUND
with back partially toward camera, bracing defensively with concerned alarmed expression seeing incoming threat,
Dragonite (7'3" bulky ORANGE-TAN dragon with burn marks still visible, teal wings spread wide, two antennae,
cream belly stripes) positioned in RIGHT BACKGROUND charging FORWARD TOWARD camera and toward Charizard in
aggressive attacking approach, fierce angry expression at maximum (eyes blazing with rage, teeth fully bared
showing vengeance), BURN MARKS STILL VISIBLE on battle-worn body maintaining continuity, body in dynamic
forward charging motion creating DEPTH MOVEMENT from background approaching foreground (NOT lateral flyby or
running away), wings spread for acceleration thrust, motion blur emphasizing forward velocity TOWARD target,
over-the-shoulder perspective shows Dragonite closing distance rapidly approaching Charizard who is nearest
to camera, professional stacking creates clear visual alignment showing aggressive charge trajectory INTO
frame depth (Dragonite moving from far → near, background → foreground, TOWARD Charizard and viewer), side
OTS angle making it unmistakably clear Dragonite is attacking NOT fleeing, volcanic valley, NO SHIELD on
either Pokemon, extremely detailed OTS composition showing threatening approach

PANEL 6 (Bottom-Right) - THUNDER PUNCH IMPACT:
CAMERA ANGLE: Close-up impact shot emphasizing connection and effect
Dragonite's electrified fist making FULL CONTACT with Charizard's shoulder/torso in devastating Thunder Punch
counter-attack, massive bright YELLOW ELECTRIC EXPLOSION at impact point, intense electricity crackling and
lightning arcs bursting violently outward, Charizard with EXTREME PAINED EXPRESSION from electric shock (eyes
squeezed shut, mouth open wide roaring in pain from electricity, face contorted), body being KNOCKED BACKWARD
by punch force and electric surge, electric current visibly running through Charizard's body, Dragonite on
RIGHT with fierce satisfied expression landing revenge hit, BURN MARKS STILL VISIBLE on Dragonite maintaining
perfect continuity, close-up shot emphasizing maximum electric impact and Charizard's pain reaction, bright
yellow electric glow illuminating scene, volcanic valley, NO SHIELD, extremely detailed electric impact rendering

OVERALL STORYBOARD REQUIREMENTS AND COMPLETE VALIDATION:
- Professional 3x2 grid with 6 clear panels and highly visible borders
- Reading order: left-to-right top row (1-2-3), left-to-right bottom row (4-5-6)
- 95%+ character consistency across all 6 panels (Nano Banana Pro standard)
- Charizard consistent: orange body, teal wings, cream belly, flaming tail, lean build, 5'7"
- Dragonite consistent: ORANGE-TAN body (NOT green), teal wings, cream belly stripes, two antennae, NO tail flame, bulky build, 7'3\"
- CRITICAL CAMERA ANGLES: Panel 5 uses Over-the-Shoulder (OTS) perspective from behind Charizard showing
  Dragonite charging TOWARD camera/Charizard creating depth movement (background→foreground), NOT lateral
  movement or fleeing
- Professional stacking: Panel 5 creates clear visual alignment Dragonite→trajectory→Charizard showing
  aggressive charge
- Element continuity: burn marks ABSENT Panels 1-2, APPEAR Panel 3, PERSIST Panels 4-5-6 with consistency
- NO SHIELDS in any panel (1, 2, 3, 4, 5, or 6) - CRITICAL
- NO defensive barriers in any panel
- Extremely detailed large-scale rendering for all panels
- Clear narrative progression: launch → impact → burn → anger → charge TOWARD → electric hit
- Professional fight cinematography techniques applied throughout
- 16:9 aspect ratio, photorealistic CGI quality
- Volcanic valley background consistent all panels
"""

    output_path = "charizard/battle_assets/storyboard_6sequence_v3_camera_fix.jpg"

    try:
        image_path, task_id = generate_storyboard(prompt, output_path, api_key)

        print(f"\n{'='*70}")
        print(f"🎉 6-SEQUENCE V3 STORYBOARD COMPLETE (CAMERA ANGLE FIX)!")
        print(f"{'='*70}")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n✅ CAMERA ANGLE FIXES APPLIED:")
        print(f"  ✓ Panel 5: Over-the-Shoulder (OTS) from behind Charizard")
        print(f"  ✓ Dragonite in BACKGROUND charging TOWARD FOREGROUND")
        print(f"  ✓ Depth movement (background→foreground) NOT lateral")
        print(f"  ✓ Charizard in LEFT FOREGROUND bracing for impact")
        print(f"  ✓ Professional stacking alignment showing charge trajectory")
        print(f"  ✓ Panel 6: Thunder Punch impact (extended scene)")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  [ ] Panel 5: Camera behind/beside Charizard looking outward?")
        print(f"  [ ] Panel 5: Charizard in FOREGROUND (near camera)?")
        print(f"  [ ] Panel 5: Dragonite in BACKGROUND moving TOWARD foreground?")
        print(f"  [ ] Panel 5: Dragonite getting CLOSER/LARGER (approaching)?")
        print(f"  [ ] Panel 5: Charizard bracing/concerned (seeing threat approach)?")
        print(f"  [ ] Panel 5: NOT flying past - charging INTO depth?")
        print(f"  [ ] Panel 6: Thunder Punch hitting with electricity?")
        print(f"  [ ] Burn marks persist panels 3-4-5-6?")
        print(f"  [ ] ❌ NO SHIELDS in any panel?")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
