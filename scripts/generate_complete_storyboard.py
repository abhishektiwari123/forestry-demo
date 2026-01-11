#!/usr/bin/env python3
"""
Generate Complete Storyboard Image - All 4 Scenes in One Frame

Based on:
- Nano Banana Pro storyboard capabilities
- Frame-by-frame continuity best practices
- Professional storyboard layout (2x2 grid)

Storyboard shows complete sequence:
Panel 1: Flamethrower Launch
Panel 2: Impact with Pain
Panel 3: Burn Marks & Anger
Panel 4: Revenge Charge
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


def generate_storyboard_image(prompt: str, output_path: str, api_key: str) -> str:
    """
    Generate storyboard image using Nano Banana Pro.

    Following best practices:
    - Clarity over detail
    - Frame-by-frame continuity
    - 2x2 grid layout for 4 scenes
    - Clear annotations for each panel
    """
    print(f"\n🎨 Generating complete storyboard image...")
    print(f"📝 Prompt length: {len(prompt)} characters")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",  # Wide format for storyboard
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
    print(f"⏳ Generating storyboard... ", end="", flush=True)

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
                print(f"\n✅ Storyboard generated!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Download image
                img_resp = requests.get(image_url, timeout=60)
                if img_resp.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    with open(output_path, 'wb') as f:
                        f.write(img_resp.content)

                    # Check image
                    img = Image.open(output_path)
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    duration = time.time() - start_time

                    print(f"✅ Saved: {img.size[0]}x{img.size[1]}, {size_mb:.2f} MB")
                    print(f"⏱️  Generation time: {duration:.1f}s")
                    print(f"📁 Location: {output_path}")

                    return output_path, task_id

            elif data.get("state") == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout after 120s")


def main():
    """Generate complete storyboard with all 4 scenes."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║              COMPLETE STORYBOARD GENERATION                        ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Creating professional 2x2 storyboard with frame-by-frame flow:   ║
║                                                                    ║
║  ┌──────────────────┬──────────────────┐                          ║
║  │ Panel 1:         │ Panel 2:         │                          ║
║  │ Flamethrower     │ Impact &         │                          ║
║  │ Launch           │ Pain             │                          ║
║  ├──────────────────┼──────────────────┤                          ║
║  │ Panel 3:         │ Panel 4:         │                          ║
║  │ Burn Marks &     │ Revenge          │                          ║
║  │ Anger            │ Charge           │                          ║
║  └──────────────────┴──────────────────┘                          ║
║                                                                    ║
║  Following best practices:                                         ║
║  - Clarity over artistic detail                                    ║
║  - Frame-by-frame continuity (95%+ character consistency)          ║
║  - Clear action progression                                        ║
║  - NO NEW ELEMENTS (no shields, barriers)                          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Complete storyboard prompt with 2x2 layout
    # Following best practices: clarity, continuity, explicit negation
    storyboard_prompt = """
PROFESSIONAL STORYBOARD LAYOUT: 2x2 grid showing 4-panel Pokemon battle sequence,
clean comic-style panels with clear borders, professional animation storyboard format,
cinematic composition, realistic CGI style

TOP-LEFT PANEL (Scene 1 - Flamethrower Launch):
Charizard (5'7" lean orange dragon, teal wings, cream belly, flaming tail) on LEFT
side launching massive orange-red Flamethrower stream from open jaws with fierce
determined expression, flames beginning to travel toward significantly larger
Dragonite (7'3" bulky ORANGE-TAN dragon, teal wings, two antennae, cream belly,
NO tail flame) on RIGHT side in ready stance, side-angle wide shot, volcanic valley
background, dramatic battle start, NO SHIELD on Dragonite, NO defensive barriers

TOP-RIGHT PANEL (Scene 2 - Impact with Pain):
Same characters, massive Flamethrower stream STRIKING Dragonite torso with bright
orange impact glow and heat distortion, Dragonite with PAINED expression (eyes
squinting, mouth open grimacing, face contorted in distress), body being PUSHED
BACKWARD by force of flames, arms raised defensively but failing against fire,
Charizard on LEFT maintaining attack, side-angle medium shot emphasizing impact,
NO SHIELD on Dragonite, NO defensive barriers, taking DIRECT HIT

BOTTOM-LEFT PANEL (Scene 3 - Burn Marks & Anger):
Dragonite in CENTER with VISIBLE BURN DAMAGE (blackened scorch marks on ORANGE-TAN
torso and cream belly), flames dissipating with smoke wisping from burnt scales,
facial expression transitioning from pain to FIERCE ANGER (eyes narrowing with rage,
teeth bared in aggressive snarl, eyebrows furrowed showing intense fury), body
recovering from knockback, medium close-up centered on Dragonite showing burn
damage detail and emotional shift, NO SHIELD, battle damage realistic

BOTTOM-RIGHT PANEL (Scene 4 - Revenge Charge):
Dragonite CHARGING FORWARD aggressively from right to left with fierce angry
expression and bared teeth, teal wings spread wide for acceleration, BURN MARKS
still visible on battle-worn ORANGE-TAN body (continuity from Panel 3), smaller
Charizard on LEFT bracing for incoming counter-attack, side-angle dynamic shot
capturing charge motion and battle tension, volcanic valley, NO SHIELD on Dragonite,
NO defensive barriers

OVERALL STORYBOARD REQUIREMENTS:
- Clean 2x2 grid layout with visible panel borders
- Professional animation storyboard style
- 95%+ character consistency across all 4 panels
- Frame-by-frame action continuity (launch → impact → damage → charge)
- Clear narrative progression visible
- Character sizes consistent (Dragonite 30% larger than Charizard)
- Colors consistent (Charizard orange with teal wings, Dragonite ORANGE-TAN with teal wings)
- NO shields in any panel
- NO defensive barriers in any panel
- Burn marks appear in Panel 3 and persist in Panel 4 (element continuity)
- Realistic photorealistic CGI render quality
- 16:9 aspect ratio, professional storyboard composition
"""

    output_path = "charizard/battle_assets/storyboard_complete_4panel.jpg"

    print(f"\n{'='*70}")
    print("GENERATING COMPLETE STORYBOARD")
    print(f"{'='*70}")
    print(f"\nStoryboard structure:")
    print(f"  Format: 2x2 grid (4 panels)")
    print(f"  Style: Professional animation storyboard")
    print(f"  Continuity: 95%+ character consistency")
    print(f"  Validation: NO NEW ELEMENTS (shields, barriers)")

    try:
        image_path, task_id = generate_storyboard_image(
            storyboard_prompt,
            output_path,
            api_key
        )

        print(f"\n{'='*70}")
        print(f"🎉 SUCCESS!")
        print(f"{'='*70}")
        print(f"✅ Complete storyboard generated")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  Please verify:")
        print(f"  [ ] 2x2 grid layout with 4 clear panels?")
        print(f"  [ ] Panel 1: Charizard launching Flamethrower?")
        print(f"  [ ] Panel 2: Flames striking Dragonite with pain?")
        print(f"  [ ] Panel 3: Dragonite with burn marks, getting angry?")
        print(f"  [ ] Panel 4: Dragonite charging forward?")
        print(f"  [ ] Character consistency across all panels (95%+)?")
        print(f"  [ ] ❌ NO SHIELDS in any panel?")
        print(f"  [ ] ❌ NO defensive barriers in any panel?")
        print(f"  [ ] Burn marks appear in Panel 3 and persist in Panel 4?")
        print(f"  [ ] Narrative flow clear and logical?")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
