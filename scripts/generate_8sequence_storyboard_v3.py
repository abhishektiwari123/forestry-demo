#!/usr/bin/env python3
"""
Generate 8-Sequence Storyboard V3 - CAMERA ANGLE FIX

Uses professional cinematography techniques:
- Over-the-Shoulder (OTS) camera positioning
- Stacking (visual alignment)
- Depth movement (TOWARD camera) not lateral movement

CRITICAL FIX: Panel 6 uses OTS angle showing Dragonite charging TOWARD Charizard/camera
EXTENDED: Panels 7-8 show complete Thunder Punch sequence
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
    print(f"\n🎨 Generating 8-sequence storyboard V3 (CAMERA ANGLE FIX)...")
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
    """Generate camera-angle-corrected 8-sequence storyboard."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║      8-SEQUENCE STORYBOARD V3 (4x2) - CAMERA ANGLE FIX            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌──────────┬──────────┬──────────┬──────────┐                    ║
║  │Panel 1   │Panel 2   │Panel 3   │Panel 4   │                    ║
║  │Launch    │Traveling │Impact    │Burn      │                    ║
║  ├──────────┼──────────┼──────────┼──────────┤                    ║
║  │Panel 5   │Panel 6   │Panel 7   │Panel 8   │                    ║
║  │Anger     │OTS Charge│Thunder↗  │Thunder!  │                    ║
║  └──────────┴──────────┴──────────┴──────────┘                    ║
║                                                                    ║
║  FIX: Panel 6 uses Over-the-Shoulder camera angle                 ║
║       Dragonite charging TOWARD Charizard/camera (depth)          ║
║  EXTENDED: Panels 7-8 Thunder Punch sequence                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # V3 prompt with professional camera angles
    prompt = """
PROFESSIONAL ANIMATION STORYBOARD: 4x2 grid layout (8 panels) showing complete extended Pokemon battle
sequence with CORRECTED camera angles, clean comic-style panels with visible borders, professional
format, photorealistic CGI quality, EXTREMELY DETAILED large-scale rendering

TOP ROW - CHARIZARD'S FLAMETHROWER ATTACK:

PANEL 1 (Top Far-Left) - FLAMETHROWER LAUNCH:
Charizard (5'7" lean orange dragon, teal wings, cream belly, flaming tail) on LEFT launching massive
orange-red Flamethrower from jaws, fierce expression, significantly larger Dragonite (7'3" bulky ORANGE-TAN
body, teal wings, two antennae, cream belly stripes, NO tail flame) on RIGHT ready stance, side-angle wide
shot, NO SHIELD, volcanic valley, extremely detailed

PANEL 2 (Top Center-Left) - FLAMES TRAVELING:
Massive Flamethrower stream TRAVELING mid-air LEFT-TO-RIGHT, realistic fire physics, heat distortion,
Charizard on LEFT maintaining attack, Dragonite on RIGHT watching flames approach with concern, NO SHIELD,
side-angle capturing trajectory, volcanic valley, extremely detailed fire rendering

PANEL 3 (Top Center-Right) - IMPACT WITH PAIN:
Flamethrower STRIKING Dragonite torso with bright orange impact burst, Dragonite with EXTREME PAINED
EXPRESSION (eyes shut, mouth wide open roaring, face contorted), body VIOLENTLY PUSHED BACKWARD, arms
raised but NO shields, Charizard on LEFT maintaining attack, side-angle emphasizing pain, NO SHIELD,
volcanic valley, extremely detailed impact effects

PANEL 4 (Top Far-Right) - BURN MARKS VISIBLE:
Flames dissipating, Dragonite in CENTER with SEVERE BURN DAMAGE (blackened scorch marks on ORANGE-TAN
torso, burnt cream belly, realistic burn texture), thick smoke rising from burns, exhausted pained
expression (eyes half-closed, gasping), body slumped, Charizard in background, medium close-up on burn
damage, NO SHIELD, volcanic valley, extremely detailed burn rendering

BOTTOM ROW - DRAGONITE'S COUNTER-ATTACK SEQUENCE:

PANEL 5 (Bottom Far-Left) - ANGER BUILDING:
Dragonite with BURN MARKS STILL VISIBLE (maintaining continuity from Panel 4), smoke wisping from burns,
facial expression TRANSFORMING from pain to FIERCE ANGER (eyes narrowing with rage, teeth baring, eyebrows
furrowing), body tensing, fists clenching, building energy for revenge, medium close-up capturing emotional
shift, burn marks prominent persistent, NO SHIELD, volcanic valley, extremely detailed anger expression

PANEL 6 (Bottom Center-Left) - CHARGING TOWARD CHARIZARD (OTS CAMERA ANGLE):
CAMERA ANGLE: Over-the-Shoulder (OTS) from behind Charizard in LEFT FOREGROUND looking outward, professional
fight cinematography stacking technique
Charizard (5'7" lean orange dragon with teal wings, cream belly, flaming tail) positioned in LEFT FOREGROUND
with back partially toward camera, bracing defensively with concerned alarmed expression seeing incoming threat
and starting to raise arms protectively, Dragonite (7'3" bulky ORANGE-TAN dragon with burn marks still clearly
visible, teal wings spread wide for acceleration, two antennae, cream belly stripes) positioned in RIGHT
BACKGROUND charging FORWARD TOWARD camera and toward Charizard in aggressive attacking approach creating DEPTH
MOVEMENT from background approaching foreground (NOT lateral flyby or running away), fierce angry expression at
maximum intensity (eyes blazing with rage, teeth fully bared showing vengeance intent), BURN MARKS STILL VISIBLE
on battle-worn body maintaining perfect continuity, body in dynamic forward charging motion with speed, wings
spread for maximum acceleration thrust, motion blur emphasizing forward velocity TOWARD target, over-the-shoulder
perspective clearly shows Dragonite closing distance rapidly as threatening figure approaches Charizard who is
nearest to camera, professional stacking creates clear visual alignment showing aggressive charge trajectory INTO
frame depth (Dragonite moving from far → near, background → foreground, TOWARD Charizard and viewer), side OTS
angle composition makes it unmistakably clear Dragonite is attacking NOT fleeing or flying past, volcanic valley
background, NO SHIELD on either Pokemon, extremely detailed OTS composition showing menacing aggressive approach

PANEL 7 (Bottom Center-Right) - THUNDER PUNCH BEGINNING:
Dragonite now very close to Charizard with electrified fist raised and pulling back, bright YELLOW
ELECTRICITY crackling intensely around Dragonite's clenched fist charging Thunder Punch attack, Dragonite's
fierce expression showing attack intent, BURN MARKS STILL VISIBLE maintaining continuity, Charizard on LEFT
with defensive worried expression seeing electrified fist approaching, arms raising to try blocking, electric
sparks and lightning arcs beginning to form, side-angle medium shot emphasizing electric buildup and incoming
punch, burn marks persistent, NO SHIELD, volcanic valley, extremely detailed electric effects charging

PANEL 8 (Bottom Far-Right) - THUNDER PUNCH FULL IMPACT:
Dragonite's electrified fist making FULL CONTACT with Charizard's shoulder/torso in devastating Thunder Punch,
massive bright YELLOW ELECTRIC EXPLOSION at impact point, intense electricity crackling and lightning arcs
bursting violently outward in all directions, Charizard with EXTREME PAINED EXPRESSION from electric shock
(eyes squeezed shut, mouth open wide roaring in agony from electricity, face severely contorted), body being
KNOCKED BACKWARD violently by combined punch force and electric surge, electric current visibly running through
Charizard's entire body causing spasms, Dragonite on RIGHT with fierce satisfied expression of landing
devastating revenge hit, BURN MARKS STILL VISIBLE on Dragonite maintaining perfect continuity, side-angle
medium-close shot emphasizing maximum electric impact and Charizard's extreme pain reaction, bright yellow
electric glow illuminating entire scene dramatically, volcanic valley, NO SHIELD, extremely detailed maximum
electric impact rendering

OVERALL REQUIREMENTS AND VALIDATION:
- Professional 4x2 grid with 8 clear panels and highly visible borders
- Reading order: left-to-right top (1-2-3-4), left-to-right bottom (5-6-7-8)
- 95%+ character consistency (Nano Banana Pro standard)
- Charizard consistent: orange body, teal wings, cream belly, flaming tail, lean 5'7"
- Dragonite consistent: ORANGE-TAN body (NEVER green), teal wings, cream belly stripes, two antennae,
  NO tail flame ever, bulky 7'3\" (30% larger)
- CRITICAL CAMERA ANGLE FIX: Panel 6 uses Over-the-Shoulder (OTS) perspective from behind Charizard showing
  Dragonite charging TOWARD camera/Charizard creating depth movement (background→foreground), NOT lateral
  movement or fleeing
- Professional stacking: Panel 6 creates clear visual alignment Dragonite→trajectory→Charizard showing
  aggressive charge INTO depth
- Element continuity: burn marks ABSENT Panels 1-2-3, APPEAR Panel 4, PERSIST Panels 5-6-7-8 with perfect
  consistency
- Extended sequence: Panels 7-8 show complete Thunder Punch counter-attack sequence (buildup → impact)
- NO SHIELDS in any of 8 panels (CRITICAL validation)
- NO defensive barriers in any panel
- Extremely detailed large-scale rendering for all panels
- Photorealistic CGI quality throughout
- 16:9 aspect ratio, professional animation storyboard composition
- Volcanic valley background consistent all panels
"""

    output_path = "charizard/battle_assets/storyboard_8sequence_v3_camera_fix.jpg"

    try:
        image_path, task_id = generate_storyboard(prompt, output_path, api_key)

        print(f"\n{'='*70}")
        print(f"🎉 8-SEQUENCE V3 STORYBOARD COMPLETE (CAMERA ANGLE FIX)!")
        print(f"{'='*70}")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n✅ CAMERA ANGLE FIXES APPLIED:")
        print(f"  ✓ Panel 6: Over-the-Shoulder (OTS) from behind Charizard")
        print(f"  ✓ Dragonite in BACKGROUND charging TOWARD FOREGROUND")
        print(f"  ✓ Depth movement (background→foreground) NOT lateral")
        print(f"  ✓ Charizard in LEFT FOREGROUND bracing for impact")
        print(f"  ✓ Professional stacking showing charge trajectory INTO depth")
        print(f"  ✓ Panel 7: Thunder Punch charging")
        print(f"  ✓ Panel 8: Thunder Punch devastating impact")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  [ ] Panel 6: Camera behind/beside Charizard looking outward?")
        print(f"  [ ] Panel 6: Charizard in FOREGROUND (near camera)?")
        print(f"  [ ] Panel 6: Dragonite in BACKGROUND moving TOWARD foreground?")
        print(f"  [ ] Panel 6: Dragonite getting CLOSER/LARGER (approaching)?")
        print(f"  [ ] Panel 6: Charizard bracing/concerned (seeing threat approach)?")
        print(f"  [ ] Panel 6: NOT flying past - charging INTO depth?")
        print(f"  [ ] Panel 7: Electric fist charging Thunder Punch?")
        print(f"  [ ] Panel 8: Thunder Punch hitting Charizard with impact?")
        print(f"  [ ] Burn marks persist panels 4-5-6-7-8?")
        print(f"  [ ] ❌ NO SHIELDS in any of 8 panels?")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
