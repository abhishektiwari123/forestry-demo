#!/usr/bin/env python3
"""
Generate 8-Sequence Storyboard V2 - CORRECTED VERSION

Extended sequence with proper direction and continuation:
1. Flamethrower Launch
2. Flames Traveling
3. Impact with Pain
4. Burn Marks Visible
5. Anger Building
6. Dragonite Charging TOWARD Charizard (aggressive, not fleeing)
7. Thunder Punch Beginning
8. Thunder Punch Impact (extended scene)

FIXED: Dragonite charges TOWARD Charizard (right to left), NOT running away
EXTENDED: Continues beyond charge with Thunder Punch sequence
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
    print(f"\n🎨 Generating 8-sequence storyboard V2 (CORRECTED)...")
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
    """Generate corrected 8-sequence storyboard."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║      8-SEQUENCE STORYBOARD V2 (4x2 Grid) - CORRECTED              ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌──────────┬──────────┬──────────┬──────────┐                    ║
║  │Panel 1   │Panel 2   │Panel 3   │Panel 4   │                    ║
║  │Launch    │Traveling │Impact    │Burn      │                    ║
║  ├──────────┼──────────┼──────────┼──────────┤                    ║
║  │Panel 5   │Panel 6   │Panel 7   │Panel 8   │                    ║
║  │Anger     │Charge→   │Thunder↗  │Thunder!  │                    ║
║  └──────────┴──────────┴──────────┴──────────┘                    ║
║                                                                    ║
║  FIXED: Panel 6 - Dragonite charging TOWARD Charizard             ║
║  EXTENDED: Panels 7-8 Thunder Punch sequence                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # CORRECTED 8-panel prompt with proper direction and extension
    prompt = """
PROFESSIONAL ANIMATION STORYBOARD: 4x2 grid layout (8 panels) showing complete extended Pokemon battle
sequence with CORRECTED charge direction, clean comic-style panels with visible borders, professional
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

PANEL 6 (Bottom Center-Left) - CHARGING TOWARD CHARIZARD (CORRECTED):
Dragonite CHARGING FORWARD AGGRESSIVELY from RIGHT side TOWARD LEFT side moving RIGHT-TO-LEFT across frame
in attacking charge toward Charizard, teal wings spread wide for acceleration, fierce angry expression at
maximum (eyes blazing rage, teeth fully bared showing vengeance intent), BURN MARKS STILL VISIBLE on
battle-worn body (perfect continuity), dynamic forward charging motion with speed, smaller Charizard visible
on LEFT side of frame seeing Dragonite approaching and starting to brace defensively with concerned alarmed
expression, side-angle dynamic shot capturing charge momentum TOWARD Charizard (NOT away from), motion blur
showing Dragonite closing distance rapidly to strike, burn marks persistent and prominent, NO SHIELD,
volcanic valley, extremely detailed motion capture showing aggressive approach

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
  NO tail flame ever, bulky 7'3" (30% larger)
- CRITICAL DIRECTION FIX: Panel 6 shows Dragonite charging RIGHT-TO-LEFT TOWARD Charizard (attacking approach),
  NOT running away or fleeing, Charizard on LEFT bracing for incoming aggressive charge
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

    output_path = "charizard/battle_assets/storyboard_8sequence_v2_corrected.jpg"

    try:
        image_path, task_id = generate_storyboard(prompt, output_path, api_key)

        print(f"\n{'='*70}")
        print(f"🎉 8-SEQUENCE V2 STORYBOARD COMPLETE (CORRECTED)!")
        print(f"{'='*70}")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n✅ FIXES APPLIED:")
        print(f"  ✓ Panel 6: Dragonite charging TOWARD Charizard (right→left)")
        print(f"  ✓ Panel 7: Thunder Punch charging")
        print(f"  ✓ Panel 8: Thunder Punch devastating impact")
        print(f"  ✓ NOT running away - aggressive counter-attack")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  [ ] Panel 6: Dragonite charging RIGHT-TO-LEFT toward Charizard?")
        print(f"  [ ] Panel 6: Charizard on LEFT side seeing Dragonite approach?")
        print(f"  [ ] Panel 6: NOT fleeing - charging TO ATTACK?")
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
