#!/usr/bin/env python3
"""
Generate Charizard vs Dragonite Battle Storyboard - SIGNATURE MOVES VERSION
CHARIZARD: Blast Burn (Ultimate Fire-type finisher)
DRAGONITE: Dragon Rush + Outrage (Dragon-type onslaught)

New cinematic 6-panel battle sequence with researched signature moves.
"""

import os
import sys
import requests
import json
import time


def load_api_key():
    """Load API key from .env file."""
    env_paths = ['scripts/.env', '.env', '/home/user/forestry-demo/.env', '/home/user/forestry-demo/scripts/.env']
    for path in env_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('KIE_API_KEY='):
                        return line.strip().split('=', 1)[1]
    raise Exception("❌ KIE_API_KEY not found")


def generate_storyboard(api_key: str, output_path: str) -> tuple:
    """Generate 6-panel battle storyboard with signature moves."""

    # NEW BATTLE SEQUENCE WITH SIGNATURE MOVES
    storyboard_prompt = """PHOTOREALISTIC CGI POKEMON BATTLE STORYBOARD - 6 PANELS (3 columns x 2 rows grid layout):
Professional Pokemon battle animation quality, cinematic fight choreography, 8K CGI rendering, dramatic volcanic valley
setting with rocky cliffs and lava flows.

CHARACTER SPECIFICATIONS:
- Charizard: 5'7" lean orange dragon, bright teal wings, cream-colored belly, intensely burning tail flame, fierce
  determined expression, sharp focused eyes, detailed scale texture
- Dragonite: 7'3" bulky orange-tan body, teal wings, two antennae on head, cream-colored belly with horizontal stripes,
  NO tail flame (key difference), gentle but powerful appearance, detailed scale texture

======================================================================================
PANEL 1 (Top-Left) - BLAST BURN CHARGE-UP (LOW ANGLE HERO SHOT):
======================================================================================
CAMERA ANGLE: Low angle hero shot looking UP at Charizard (empowering perspective)
POSITIONING: Charizard centered in frame hovering mid-air with wings spread majestically, body glowing with intense
building orange-red fire energy, chest and belly cream area glowing bright orange from internal heat building up,
entire body surrounded by spiraling flames and fire particles swirling around, tail flame burning at maximum intensity
(3x normal size), fierce determined expression with eyes glowing orange-red, jaws slightly open showing heat distortion,
charging up BLAST BURN ultimate fire move, visible heat waves radiating outward distorting air, fire energy accumulating
around entire body creating fiery aura, Dragonite visible in background at distance in defensive stance watching warily,
volcanic valley background with mountain peaks, dramatic upward lighting emphasizing power, cinematic hero composition,
photorealistic fire particle effects, 8K CGI quality

======================================================================================
PANEL 2 (Top-Center) - BLAST BURN EXPLOSIVE RUSH (TRACKING SHOT):
======================================================================================
CAMERA ANGLE: Dynamic side tracking shot following Charizard's explosive charge
POSITIONING: Charizard RUSHING FORWARD at extreme speed completely engulfed in massive orange-red fireball (entire body
becomes living comet), leaving trail of fire and smoke behind creating speed lines, wings tucked for aerodynamic rush,
eyes visible through flames showing intense focus, heading DIRECTLY TOWARD Dragonite with devastating force, Dragonite
in foreground bracing for impact with arms raised defensively but body tense knowing hit is unavoidable, Charizard's
fire trail creating arc of flames across entire panel, massive heat distortion between both Pokemon, explosive approach
with fire particles everywhere, camera panning to follow motion blur of charge, volcanic valley background streaking
past, photorealistic fire physics with realistic combustion, cinematic action shot, 8K CGI rendering, professional
VFX quality explosion effect

======================================================================================
PANEL 3 (Top-Right) - BLAST BURN IMPACT EXPLOSION (WIDE ANGLE IMPACT):
======================================================================================
CAMERA ANGLE: Wide angle capturing full explosive impact
POSITIONING: MASSIVE ORANGE-RED EXPLOSION filling majority of frame as Charizard's Blast Burn makes contact with
Dragonite, enormous spherical fireball burst with bright white-orange core, explosive shockwave rippling outward
pushing air and debris, Dragonite's silhouette barely visible within explosion taking full force of ultimate fire
move, body thrown backward violently by explosive impact force, Charizard visible at explosion edge having delivered
attack but showing exhaustion from ultimate move (must recharge), ground cracking from shockwave impact, volcanic
rocks flying outward, intense bright lighting from explosion illuminating everything, heat wave distortion across
entire panel, massive smoke and fire plume rising upward, photorealistic explosion physics with realistic blast
radius, cinematic Hollywood-level VFX explosion, 8K CGI quality, professional destruction effects

======================================================================================
PANEL 4 (Bottom-Left) - OUTRAGE ACTIVATION (CLOSE-UP TRANSFORMATION):
======================================================================================
CAMERA ANGLE: Close-up on Dragonite's face and upper body (emotional intensity shot)
POSITIONING: Dragonite emerging from smoke and flames with SEVERE BURN DAMAGE visible (large blackened scorch marks
covering significant areas of orange-tan torso, burnt cream belly with dark char marks, realistic burn texture), smoke
rising from fresh burns, exhausted pained expression transforming into BERSERKER RAGE, eyes glowing bright PURPLE-RED
with Outrage energy taking over, pupils dilated with uncontrolled fury, facial expression showing loss of control and
pure aggressive instinct, teeth fully bared in savage snarl, body beginning to glow with purple-red dragon-type aura,
OUTRAGE MOVE ACTIVATING (berserker state - uncontrollable rampage attack), purple-red energy crackling around body like
electricity, veins glowing purple showing dragon energy coursing through, fists clenching with building rage energy,
background slightly blurred focusing attention on transformation, dramatic backlighting creating menacing silhouette,
photorealistic emotional intensity, cinematic character transformation shot, 8K CGI rendering, professional anger
expression capture

======================================================================================
PANEL 5 (Bottom-Center) - DRAGON RUSH CHARGE (OVER-SHOULDER FROM CHARIZARD):
======================================================================================
CAMERA ANGLE: Over-the-shoulder from behind exhausted Charizard (vulnerable POV)
POSITIONING: Charizard in LEFT FOREGROUND breathing heavily with exhausted expression from Blast Burn recharge period,
wings drooping slightly from energy drain, back toward camera showing vulnerability, Dragonite in RIGHT BACKGROUND
completely surrounded by BLUE DRAGON-TYPE ENERGY AURA launching Dragon Rush attack, body glowing bright blue with
dragon energy forming dragon-shaped silhouette around body, charging forward AGGRESSIVELY at extreme speed creating
depth movement from background toward foreground, eyes still glowing purple-red from Outrage state (double power combo),
face showing uncontrolled berserker rage, wings creating powerful thrust with motion blur, DRAGON RUSH + OUTRAGE COMBO
creating devastating double dragon energy (blue dragon aura + purple-red rage energy swirling together), approaching
rapidly toward vulnerable Charizard who can't dodge yet, dramatic threatening approach, OTS perspective showing incoming
danger, photorealistic dragon energy effects with blue crackling electricity, cinematic threat composition, 8K CGI
quality, professional motion blur

======================================================================================
PANEL 6 (Bottom-Right) - DRAGON RUSH IMPACT (EXTREME CLOSE-UP IMPACT):
======================================================================================
CAMERA ANGLE: Extreme close-up on impact point (maximum detail on collision)
POSITIONING: Dragonite's blue dragon energy-covered body making FULL DIRECT CONTACT with Charizard's torso in
devastating Dragon Rush tackle, MASSIVE BLUE DRAGON ENERGY EXPLOSION erupting at impact point with bright cyan-blue
core, dragon-type energy burst creating shockwave with visible blue lightning arcs and energy bolts radiating outward,
Charizard's body taking full super-effective hit (Dragon move on Flying-type weakness), Charizard with EXTREME PAINED
EXPRESSION (eyes squeezed shut from agony, mouth open extremely wide roaring in pain, face severely contorted), body
knocked backward violently with ribs visibly compressed from tackle force, blue dragon energy running through
Charizard's body showing super-effective damage, Dragonite's face showing berserker satisfaction with Outrage-controlled
expression (eyes still glowing purple-red, slight aggressive grin), burn marks on Dragonite's body still visible
maintaining continuity, extreme impact detail with scales deforming from collision force, blue energy explosion
illuminating everything with dragon-type glow, energy sparks everywhere, volcanic valley background, maximum impact
lighting effects, photorealistic dragon energy physics with realistic collision, cinematic impact shot, 8K CGI
rendering, professional Hollywood-level impact VFX

======================================================================================
TECHNICAL SPECIFICATIONS:
======================================================================================
- Grid Layout: 3 columns x 2 rows (6 total panels)
- Panel Order: Row 1 (L→R): 1,2,3 | Row 2 (L→R): 4,5,6
- Resolution: Each panel high-detail CGI rendering
- Style: Photorealistic Pokemon battle animation, professional VFX quality
- Aspect Ratio: Wide cinematic composition (16:9 style panels)
- Lighting: Dramatic cinematic lighting with fire/dragon energy glow effects
- Quality: 8K CGI rendering, sharp focus, professional animation studio quality

BATTLE NARRATIVE ARC:
1. Charizard charges ultimate Blast Burn (power-up moment)
2. Charizard unleashes devastating explosive rush attack
3. Massive explosion impact - Dragonite takes super-powered fire damage
4. Dragonite activates Outrage berserker mode (revenge setup)
5. Dragonite launches Dragon Rush on vulnerable recharging Charizard
6. Dragon Rush super-effective impact - Dragonite's comeback strike

Both Pokemon use their signature ultimate moves for balanced cinematic battle!"""

    print("\n🎨 Generating SIGNATURE MOVES battle storyboard...")
    print("📝 Moves featured:")
    print("   🔥 Charizard: BLAST BURN (150 power ultimate Fire move)")
    print("   🐉 Dragonite: DRAGON RUSH + OUTRAGE (dragon-type onslaught)")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": storyboard_prompt,
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

    timeout = 300  # 5 minutes

    while time.time() - start_time < timeout:
        time.sleep(5)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)

        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )

        if status.status_code == 200:
            data = status.json().get("data", {})
            state = data.get("state")

            if state == "success":
                print(f"\n✅ Generated!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Download storyboard
                print(f"📥 Downloading storyboard...")
                img_resp = requests.get(image_url, timeout=120)
                if img_resp.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(img_resp.content)

                    from PIL import Image
                    img = Image.open(output_path)
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    duration = time.time() - start_time

                    print(f"✅ Saved: {img.size[0]}x{img.size[1]}, {size_mb:.2f} MB")
                    print(f"⏱️  Total time: {duration:.1f}s")

                    return output_path, task_id, image_url

            elif state == "fail":
                raise Exception(f"Failed: {data.get('failMsg')}")

    raise Exception("Timeout")


def main():
    """Generate signature moves battle storyboard."""

    print("""
╔════════════════════════════════════════════════════════════════════╗
║     CHARIZARD VS DRAGONITE - SIGNATURE MOVES BATTLE                ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  CHARIZARD SIGNATURE MOVE:                                         ║
║  🔥 BLAST BURN - Ultimate Fire-type move (150 power)              ║
║     • Charges up fiery aura                                        ║
║     • Explosive rush attack                                        ║
║     • Massive fireball impact                                      ║
║     • Requires recharge (vulnerability period)                     ║
║                                                                    ║
║  DRAGONITE SIGNATURE MOVES:                                        ║
║  🐉 OUTRAGE - Berserker rage (120 power)                          ║
║     • Purple-red dragon energy aura                                ║
║     • Loss of control state                                        ║
║     • Multiple turn rampage                                        ║
║                                                                    ║
║  🐉 DRAGON RUSH - Charging dive (100 power)                       ║
║     • Blue dragon energy surrounding body                          ║
║     • High-speed tackle attack                                     ║
║     • Super-effective on Flying-types                              ║
║                                                                    ║
║  BATTLE NARRATIVE:                                                 ║
║  1. Charizard charges Blast Burn (power buildup)                   ║
║  2. Charizard unleashes explosive fire rush                        ║
║  3. Massive explosion - Dragonite heavily damaged                  ║
║  4. Dragonite activates Outrage (berserker revenge)                ║
║  5. Dragonite launches Dragon Rush (vulnerable target)             ║
║  6. Super-effective dragon impact (comeback strike)                ║
║                                                                    ║
║  CINEMATOGRAPHY: Professional fight choreography with              ║
║  low angle hero shots, dynamic tracking, wide explosions,          ║
║  close-up transformations, OTS vulnerability, extreme impacts      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    try:
        api_key = load_api_key()

        output_path = "charizard/battle_assets/storyboard_signature_moves_blastburn_dragonrush.jpg"

        storyboard_path, task_id, storyboard_url = generate_storyboard(api_key, output_path)

        print(f"\n{'='*70}")
        print(f"🎉 SIGNATURE MOVES STORYBOARD COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Storyboard: {storyboard_path}")
        print(f"🆔 Task ID: {task_id}")
        print(f"🔗 URL: {storyboard_url}")
        print(f"\n📊 BATTLE SUMMARY:")
        print(f"   Panel 1: Charizard charges Blast Burn (hero buildup)")
        print(f"   Panel 2: Blast Burn explosive rush (devastating approach)")
        print(f"   Panel 3: Massive explosion impact (ultimate fire damage)")
        print(f"   Panel 4: Dragonite activates Outrage (berserker transformation)")
        print(f"   Panel 5: Dragon Rush charge (combo attack on vulnerable foe)")
        print(f"   Panel 6: Dragon Rush impact (super-effective comeback)")
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Extract panels: python3 scripts/extract_and_upscale_panels.py {storyboard_path}")
        print(f"   2. Enhance quality: python3 scripts/enhance_all_panels.py [extracted_dir]")
        print(f"   3. Generate videos: python3 scripts/test_video_from_panel.py [panel]")
        print(f"\n✅ RESEARCH SOURCES:")
        print(f"   • Blast Burn: https://bulbapedia.bulbagarden.net/wiki/Blast_Burn_(move)")
        print(f"   • Dragon Rush: https://bulbapedia.bulbagarden.net/wiki/Dragon_Rush_(move)")
        print(f"   • Best Charizard Battles: https://www.cbr.com/best-charizard-battles-pokemon-franchise/")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
