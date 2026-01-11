#!/usr/bin/env python3
"""
Generate 6-Sequence Storyboard V2 - CORRECTED VERSION

Extended sequence BEYOND the charge:
1. Flamethrower Launch
2. Impact with Pain
3. Burn Marks Visible
4. Anger Building
5. Dragonite Charging TOWARD Charizard (aggressive attack)
6. Thunder Punch Counter-Attack (extended beyond original)

FIXED: Dragonite charges TOWARD Charizard (right to left), NOT running away
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
    print(f"\n🎨 Generating 6-sequence storyboard V2 (CORRECTED)...")
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
    """Generate corrected 6-sequence storyboard."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║      6-SEQUENCE STORYBOARD V2 (3x2 Grid) - CORRECTED              ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌─────────────┬─────────────┬─────────────┐                      ║
║  │ Panel 1:    │ Panel 2:    │ Panel 3:    │                      ║
║  │ Launch      │ Impact      │ Burn Marks  │                      ║
║  ├─────────────┼─────────────┼─────────────┤                      ║
║  │ Panel 4:    │ Panel 5:    │ Panel 6:    │                      ║
║  │ Anger       │ Charge→Char │ Thunder Hit │                      ║
║  └─────────────┴─────────────┴─────────────┘                      ║
║                                                                    ║
║  FIXED: Panel 5 shows Dragonite charging TOWARD Charizard         ║
║  EXTENDED: Panel 6 shows Thunder Punch counter-attack             ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # CORRECTED prompt - Dragonite charges TOWARD Charizard, extended with Thunder Punch
    prompt = """
PROFESSIONAL ANIMATION STORYBOARD: 3x2 grid layout (6 panels) showing extended Pokemon battle sequence
with CORRECTED direction, clean comic-style panels with visible borders, professional storyboard format,
photorealistic CGI render quality, extremely detailed large-scale rendering

TOP ROW - CHARIZARD'S ATTACK:

PANEL 1 (Top-Left) - FLAMETHROWER LAUNCH:
Charizard (5'7" lean orange dragon, teal wings, cream belly, flaming tail) on LEFT side launching massive
orange-red Flamethrower stream from open jaws with fierce expression, flames extending toward significantly
larger Dragonite (7'3" bulky ORANGE-TAN body, teal wings, two antennae, cream belly stripes, NO tail flame)
on RIGHT side ready stance, side-angle wide shot, volcanic valley, NO SHIELD on Dragonite, NO defensive
barriers, extremely detailed photorealistic quality

PANEL 2 (Top-Center) - IMPACT WITH PAIN:
Massive Flamethrower stream STRIKING Dragonite torso with bright orange impact burst, Dragonite with EXTREME
PAINED EXPRESSION (eyes squeezed shut, mouth open wide roaring in agony, face contorted), body VIOLENTLY
PUSHED BACKWARD by flame force, arms raised desperately but NO shields or barriers, Charizard on LEFT
maintaining attack, side-angle medium shot emphasizing pain reaction, NO SHIELD, NO barriers, volcanic valley,
extremely detailed impact effects

PANEL 3 (Top-Right) - BURN MARKS VISIBLE:
Flames dissipating, Dragonite in CENTER showing SEVERE VISIBLE BURN DAMAGE (large blackened scorch marks
across ORANGE-TAN torso, burnt cream belly, realistic burn texture), thick smoke rising from burnt scales,
facial expression showing exhaustion and pain (eyes half-closed, mouth open gasping), body slumped from
damage, Charizard in background completed attack, medium close-up emphasizing burn damage detail, NO SHIELD,
volcanic valley, extremely detailed burn rendering

BOTTOM ROW - DRAGONITE'S COUNTER-ATTACK:

PANEL 4 (Bottom-Left) - ANGER BUILDING:
Same Dragonite still showing VISIBLE BURN MARKS persistent from Panel 3 (maintaining continuity), smoke
still wisping from burns, facial expression TRANSFORMING from pain to FIERCE ANGER (eyes opening and narrowing
with rage, teeth baring in snarl, eyebrows furrowing deeply), body tensing with building energy, fists
clenching, preparing to counter-attack, medium close-up capturing emotional shift, burn marks prominent,
NO SHIELD, volcanic valley, extremely detailed anger expression

PANEL 5 (Bottom-Center) - CHARGING TOWARD CHARIZARD (CORRECTED DIRECTION):
Dragonite now CHARGING FORWARD AGGRESSIVELY from RIGHT side TOWARD LEFT side where Charizard is positioned,
moving RIGHT-TO-LEFT across frame in attacking charge, teal wings spread wide for acceleration, fierce angry
expression at maximum (eyes blazing with rage, teeth fully bared, face showing vengeance), BURN MARKS STILL
VISIBLE on battle-worn body (continuity), body in dynamic forward charging motion with speed toward target,
smaller Charizard visible on LEFT side of frame seeing Dragonite approaching and bracing defensively with
concerned expression, side-angle dynamic shot capturing charge momentum TOWARD Charizard (NOT away), motion
showing Dragonite closing distance to attack, burn marks persistent, NO SHIELD, volcanic valley, extremely
detailed motion capture

PANEL 6 (Bottom-Right) - THUNDER PUNCH COUNTER-ATTACK (EXTENDED SCENE):
Dragonite's electrified fist making contact with Charizard in powerful Thunder Punch counter-attack, bright
yellow electricity crackling violently from Dragonite's fist at impact point on Charizard's shoulder/torso,
electric sparks and lightning arcs exploding outward dramatically, Charizard with PAINED EXPRESSION (eyes
squinting from electric shock, mouth open shouting in pain, face grimacing), body being knocked backward
by punch force, Dragonite on RIGHT with fierce attacking expression showing satisfaction of landing hit,
burn marks STILL VISIBLE on Dragonite maintaining continuity, side-angle medium shot emphasizing electric
impact and Charizard's pain reaction, bright yellow electric effects illuminating scene, volcanic valley,
extremely detailed electric rendering and impact effects

OVERALL REQUIREMENTS AND VALIDATION:
- Professional 3x2 grid with 6 clear panels and visible borders
- Reading order: left-to-right top (1-2-3), left-to-right bottom (4-5-6)
- 95%+ character consistency (Nano Banana Pro standard)
- Charizard consistent: orange body, teal wings, cream belly, flaming tail, lean 5'7"
- Dragonite consistent: ORANGE-TAN body (NOT green), teal wings, cream belly stripes, two antennae,
  NO tail flame, bulky 7'3" (30% larger)
- CRITICAL DIRECTION FIX: Panel 5 shows Dragonite charging RIGHT-TO-LEFT TOWARD Charizard (attacking),
  NOT running away, Charizard on LEFT bracing for incoming charge
- Element continuity: burn marks ABSENT Panel 1-2, APPEAR Panel 3, PERSIST Panels 4-5-6
- NO SHIELDS in any panel (CRITICAL validation)
- NO defensive barriers in any panel
- Extended sequence includes Thunder Punch counter-attack (Panel 6)
- Extremely detailed large-scale rendering
- Photorealistic CGI quality
- 16:9 aspect ratio, professional storyboard composition
"""

    output_path = "charizard/battle_assets/storyboard_6sequence_v2_corrected.jpg"

    try:
        image_path, task_id = generate_storyboard(prompt, output_path, api_key)

        print(f"\n{'='*70}")
        print(f"🎉 6-SEQUENCE V2 STORYBOARD COMPLETE (CORRECTED)!")
        print(f"{'='*70}")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n✅ FIXES APPLIED:")
        print(f"  ✓ Panel 5: Dragonite charging TOWARD Charizard (right→left)")
        print(f"  ✓ Panel 6: Extended with Thunder Punch counter-attack")
        print(f"  ✓ NOT running away - aggressive attack direction")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  [ ] Panel 5: Dragonite charging RIGHT-TO-LEFT toward Charizard?")
        print(f"  [ ] Panel 5: Charizard on LEFT side bracing for impact?")
        print(f"  [ ] Panel 5: NOT running away - charging TO ATTACK?")
        print(f"  [ ] Panel 6: Thunder Punch hitting Charizard?")
        print(f"  [ ] Burn marks persist in panels 3-4-5-6?")
        print(f"  [ ] ❌ NO SHIELDS in any panel?")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
