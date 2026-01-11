#!/usr/bin/env python3
"""
Generate 6-Sequence Storyboard (3x2 Grid)

Extended battle sequence with more detailed progression:
1. Flamethrower Launch
2. Flames Traveling
3. Impact with Pain
4. Burn Marks Visible
5. Transitioning to Anger
6. Revenge Charge

Following Nano Banana Pro best practices and validation framework.
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
    print(f"\n🎨 Generating 6-sequence storyboard...")
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
    """Generate 6-sequence storyboard."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           6-SEQUENCE STORYBOARD (3x2 Grid)                         ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌───────────┬───────────┬───────────┐                            ║
║  │ Panel 1:  │ Panel 2:  │ Panel 3:  │                            ║
║  │ Launch    │ Traveling │ Impact    │                            ║
║  ├───────────┼───────────┼───────────┤                            ║
║  │ Panel 4:  │ Panel 5:  │ Panel 6:  │                            ║
║  │ Burn      │ Anger     │ Charge    │                            ║
║  └───────────┴───────────┴───────────┘                            ║
║                                                                    ║
║  Extended sequence with more detail and progression                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Extremely detailed 6-panel prompt with validation framework integrated
    prompt = """
PROFESSIONAL ANIMATION STORYBOARD: 3x2 grid layout (6 panels) showing extended Pokemon battle sequence,
clean comic-style panels with visible borders separating each panel, professional storyboard format,
photorealistic CGI render quality, cinematic composition, extremely detailed and large-scale

TOP ROW - ATTACK SEQUENCE:

PANEL 1 (Top-Left) - FLAMETHROWER LAUNCH:
Charizard (5'7" lean athletic orange dragon with detailed realistic reptilian scales showing texture depth,
teal turquoise wing undersides clearly visible and glowing, cream belly, bright orange flaming tail tip
burning intensely) positioned on LEFT side of frame in aggressive attacking stance, jaws wide open showing
teeth, fierce determined facial expression with eyes narrowed intensely, launching massive sustained orange-red
Flamethrower stream from open mouth with flames just beginning to form and extend, initial flame burst with
bright glow at mouth, significantly larger Dragonite (7'3" bulky stocky ORANGE-TAN body with realistic scales,
teal wing membranes, two thin curved antennae on head, cream belly with horizontal stripes, NO tail flame)
positioned on RIGHT side in ready defensive stance bracing for incoming attack, side-angle wide shot showing
complete battlefield, volcanic valley background with dramatic rim lighting, NO SHIELD on Dragonite, NO defensive
barriers, taking direct undefended stance, extremely detailed photorealistic quality

PANEL 2 (Top-Center) - FLAMES TRAVELING:
Same battlefield continuation, massive orange-red Flamethrower stream now TRAVELING across frame from LEFT to RIGHT,
flames in mid-trajectory between Charizard (still on LEFT maintaining attack with jaws open, fierce expression,
teal wings spread for stability) and Dragonite (on RIGHT watching flames approach with concerned expression starting
to show, body tensing, arms beginning to raise instinctively), flame stream showing realistic fire physics with heat
distortion waves visible in air, bright orange-red core with yellow-white hottest center, sparks and embers trailing,
Dragonite still NO SHIELD, NO defensive barriers, completely exposed to incoming flames, side-angle medium-wide shot
capturing complete flame trajectory and both Pokemon's expressions, volcanic valley, dramatic lighting emphasizing
flame brightness, extremely detailed fire rendering with realistic physics

PANEL 3 (Top-Right) - IMPACT WITH PAIN:
Massive Flamethrower stream STRIKING Dragonite's torso and belly directly with brilliant bright orange-yellow impact
glow burst at contact point, intense heat distortion and fire sparks exploding outward from impact, Dragonite with
EXTREME PAINED FACIAL EXPRESSION (eyes squinting shut tightly from pain and heat, mouth open wide in agonized roar
showing all teeth, face severely contorted in distress, eyebrows furrowed deeply, entire face showing intense suffering),
body being VIOLENTLY PUSHED BACKWARD by overwhelming force of sustained flames with visible knockback motion and recoil,
upper body and head thrown back, arms raised high in failed defensive gesture but NO barriers or shields present,
completely vulnerable taking full direct undefended hit, Charizard on LEFT still maintaining powerful attack stream,
bright orange impact glow illuminating entire scene, side-angle medium shot emphasizing Dragonite's pain reaction and
physical knockback, volcanic valley, NO SHIELD on Dragonite, NO defensive barriers, NO protective elements, extremely
detailed impact effects and pain expression

BOTTOM ROW - AFTERMATH AND REVENGE:

PANEL 4 (Bottom-Left) - BURN MARKS VISIBLE:
Flames dissipating and fading, Dragonite in CENTER of frame with HIGHLY VISIBLE SEVERE BURN DAMAGE newly appeared from
Flamethrower impact (large blackened burnt scorch marks and charred patterns across ORANGE-TAN torso, extensive burn
damage on cream belly with dark scorch marks, realistic burn texture showing damaged scales), thick smoke wisping and
rising from multiple burnt areas on body showing heat damage aftermath, Dragonite's facial expression still showing
residual pain (eyes half-closed, mouth slightly open, face exhausted and hurt), body slightly slumped from exhaustion
and damage, arms lowered to sides, Charizard visible in background having finished attack, medium close-up shot centered
on Dragonite emphasizing extensive burn damage detail and texture, smoke effects realistic, volcanic valley background,
NO SHIELD on Dragonite, battle damage clearly visible and severe, extremely detailed burn texture and damage rendering

PANEL 5 (Bottom-Center) - TRANSITIONING TO ANGER:
Same Dragonite in CENTER, burn marks STILL HIGHLY VISIBLE and persistent from Panel 4 (maintaining continuity), smoke
still wisping from burnt scales showing damage is fresh, but facial expression now RAPIDLY TRANSITIONING from pain to
FIERCE INTENSE ANGER and rage (eyes opening wider and narrowing with determination and fury, eyebrows furrowing deeply
in aggressive anger, teeth becoming bared in aggressive snarl showing intent to retaliate, face transforming from hurt
to vengeful fury), body language shifting from slumped to tensing with building energy and rage, muscles tightening
visibly, fists clenching, preparing to counter-attack, burn marks still prominent showing battle damage continuity,
medium close-up capturing emotional transformation and building intensity, Charizard still visible in background on guard,
volcanic valley, NO SHIELD on Dragonite, burn damage persistent, extremely detailed facial expression showing emotional
shift from pain to rage

PANEL 6 (Bottom-Right) - REVENGE CHARGE:
Dragonite CHARGING FORWARD AGGRESSIVELY at high speed from right to left in dynamic attacking pose, teal wings spread
wide and pulled back for maximum acceleration thrust, fierce angry facial expression at peak intensity (eyes blazing
with rage, teeth fully bared in aggressive snarl, eyebrows furrowed showing maximum fury, entire face showing vengeful
determination), BURN MARKS STILL HIGHLY VISIBLE on battle-worn ORANGE-TAN body maintaining damage continuity from Panels
4 and 5 (blackened scorch marks on torso, burnt cream belly, realistic damage texture persistent), body in full forward
charge motion with dynamic pose showing speed and aggression, smaller Charizard (5'7" lean orange dragon with teal wings,
cream belly, flaming tail) visible on LEFT side of frame bracing for incoming counter-attack with defensive stance and
concerned expression, side-angle dynamic action shot capturing charge momentum and battle tension escalation, motion blur
on charging Dragonite emphasizing speed, volcanic valley background, NO SHIELD on Dragonite, NO defensive barriers, burn
marks prominent and consistent, extremely detailed motion and battle damage, photorealistic CGI quality

OVERALL STORYBOARD REQUIREMENTS AND VALIDATION:
- Professional 3x2 grid layout with 6 clear panels and visible borders separating each panel
- Reading order: left-to-right top row (1-2-3), then left-to-right bottom row (4-5-6)
- 95%+ character consistency across all 6 panels (Nano Banana Pro standard)
- Charizard consistent: orange body, teal wings, cream belly, flaming tail, lean build, 5'7"
- Dragonite consistent: ORANGE-TAN body (NOT green), teal wings, cream belly stripes, two antennae, NO tail flame, bulky build, 7'3" (30% larger)
- Frame-by-frame action continuity: launch → traveling → impact → burn marks → anger → charge
- Element continuity critical: burn marks ABSENT in Panels 1-2-3, APPEAR in Panel 4, PERSIST in Panels 5-6
- NO SHIELDS in any panel (1, 2, 3, 4, 5, or 6)
- NO defensive barriers in any panel
- NO force fields or protective elements in any panel
- Extremely detailed and large-scale rendering for all panels
- Clear narrative progression visible across sequence
- Smooth visual transitions between adjacent panels
- Photorealistic CGI quality throughout
- 16:9 aspect ratio, professional animation storyboard composition
- Volcanic valley background consistent across all panels
"""

    output_path = "charizard/battle_assets/storyboard_6sequence_3x2grid.jpg"

    try:
        image_path, task_id = generate_storyboard(prompt, output_path, api_key)

        print(f"\n{'='*70}")
        print(f"🎉 6-SEQUENCE STORYBOARD COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Location: {image_path}")
        print(f"🆔 Task ID: {task_id}")

        print(f"\n📋 VALIDATION CHECKLIST:")
        print(f"  [ ] 3x2 grid with 6 clear panels?")
        print(f"  [ ] Panel borders visible separating each?")
        print(f"  [ ] Panel 1: Flamethrower launch?")
        print(f"  [ ] Panel 2: Flames traveling mid-air?")
        print(f"  [ ] Panel 3: Impact with pain?")
        print(f"  [ ] Panel 4: Burn marks visible?")
        print(f"  [ ] Panel 5: Transitioning to anger?")
        print(f"  [ ] Panel 6: Charging forward?")
        print(f"  [ ] Character consistency 95%+ across all 6?")
        print(f"  [ ] ❌ NO SHIELDS in ANY panel?")
        print(f"  [ ] ❌ NO defensive barriers in ANY panel?")
        print(f"  [ ] Burn marks absent in 1-2-3, appear in 4, persist in 5-6?")
        print(f"  [ ] Narrative flow logical?")
        print(f"  [ ] Extremely detailed rendering?")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
