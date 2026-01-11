#!/usr/bin/env python3
"""
Enhance Extracted Panel with Nano Banana Pro
PHOTOREALISTIC QUALITY ENHANCEMENT

Takes extracted low-quality panel and enhances it to:
- Photorealistic CGI quality
- Maximum detail and sharpness
- Professional rendering
- Dynamic expressions
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


def upload_image(image_path: str) -> str:
    """Upload image to imgcdn.dev for enhancement."""
    print(f"\n📤 Uploading panel for enhancement: {os.path.basename(image_path)}")

    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.2f} MB")

    with open(image_path, 'rb') as f:
        response = requests.post(
            'https://imgcdn.dev/api/1/upload',
            data={'key': '5386e05a3562c7a8f984e73401540836', 'format': 'json'},
            files={'source': f},
            timeout=60
        )

    if response.status_code == 200:
        result = response.json()
        if result.get('status_code') == 200:
            image_url = result['image']['url']
            print(f"   ✅ Uploaded: {image_url}")
            return image_url

    raise Exception(f"Upload failed: {response.status_code}")


def enhance_panel(image_url: str, panel_number: int, output_path: str, api_key: str) -> tuple:
    """Enhance panel to photorealistic quality using Nano Banana Pro."""

    # Panel-specific enhancement prompts with maximum detail
    enhancement_prompts = {
        1: """Photorealistic CGI Pokemon battle scene: Charizard (5'7" lean orange dragon with bright teal wings,
cream belly, intensely burning tail flame) on LEFT hovering in mid-air at eye level with jaws wide open releasing
massive orange-red Flamethrower stream, fierce determined expression with sharp focused eyes, detailed scales texture,
wings spread showing individual feather details, Dragonite (7'3" bulky orange-tan dragon with teal wings, two antennae,
cream belly stripes, no tail flame) on RIGHT also airborne at same height with CONCERNED BRACING EXPRESSION seeing
flames approaching, eyes widening in alarm, body tensing defensively, detailed scale texture, realistic anatomy,
horizontal flame trajectory between them with heat distortion waves, volcanic valley background with mountains,
dramatic lighting with flame glow, extremely high detail 8K photorealistic CGI rendering, professional animation quality,
sharp focus, cinematic composition, realistic physics, perfect character models""",

        2: """Photorealistic CGI Pokemon battle impact scene: massive orange-red Flamethrower stream STRIKING Dragonite's
torso with explosive bright orange impact burst, Dragonite with EXTREME PAINED EXPRESSION (eyes squeezed tightly shut
in agony, mouth wide open roaring in pain showing teeth and tongue detail, face contorted showing severe distress,
facial muscles tensed), body pushed backward violently by flames force, arms raised but no shields, taking full direct
hit, detailed burn beginning on orange-tan scales, Charizard on LEFT maintaining attack with effort expression, flames
engulfing Dragonite's torso with realistic fire physics and heat glow, volcanic valley background, dramatic impact
lighting, extremely high detail 8K photorealistic CGI rendering, professional VFX quality, sharp focus throughout,
realistic pain expression, cinematic action shot""",

        3: """Photorealistic CGI Pokemon damage aftermath scene: Dragonite hovering with SEVERE VISIBLE BURN DAMAGE
(large blackened scorch marks covering significant orange-tan torso area, burnt cream belly with dark char marks,
realistic burn texture with damaged scales showing heat damage detail), thick smoke wisping upward from fresh burns,
EXHAUSTED PAINED EXPRESSION (eyes half-closed from pain showing fatigue, mouth slightly open gasping for air,
face showing hurt and exhaustion), body slumped mid-air from damage, wings drooping, Charizard in background distance,
volcanic valley background, soft smoke lighting, extremely high detail 8K photorealistic CGI rendering, medical-grade
burn detail accuracy, professional quality damage effects, sharp focus on burns, realistic smoke physics, cinematic
aftermath composition""",

        4: """Photorealistic CGI Pokemon emotional transformation scene: Dragonite still airborne with BURN MARKS HIGHLY
VISIBLE (blackened scorch marks prominent on orange-tan torso, burnt cream belly with char marks, consistent burn
pattern), smoke still rising from burns, FACIAL EXPRESSION DRAMATICALLY TRANSFORMING from pain to FIERCE VENGEFUL
ANGER (eyes narrowing intensely with building rage, pupils focused with determination, teeth baring in aggressive
snarl showing fury, eyebrows furrowing deeply, jaw clenched, facial muscles tensing with anger), body language
shifting from exhausted to energized and tense, fists clenching tightly with determination, building counter-attack
energy visibly, burn damage maintaining continuity, volcanic valley background, intense dramatic lighting emphasizing
anger, extremely high detail 8K photorealistic CGI rendering, cinematic emotion capture, perfect facial expression
detail, professional character animation quality, sharp focus on transforming expression""",

        5: """Photorealistic CGI Pokemon aggressive charge scene with over-the-shoulder cinematography: Charizard
(5'7" lean orange dragon with teal wings, cream belly, tail flame) in LEFT FOREGROUND with back partially toward
camera, CONCERNED ALARMED EXPRESSION turning to see incoming threat (eyes widening in alarm, eyebrows raised in
surprise, mouth opening in concern), arms beginning to raise defensively, Dragonite (7'3" bulky orange-tan dragon
with BURN MARKS STILL CLEARLY VISIBLE on torso from previous damage, teal wings spread wide, two antennae, cream
belly with burns) in RIGHT BACKGROUND charging FORWARD AGGRESSIVELY TOWARD camera and Charizard creating depth,
FIERCE VENGEFUL ANGRY EXPRESSION at maximum intensity (eyes blazing with pure rage focused on target, teeth fully
bared showing attack intent, face showing fury and determination), body in dynamic forward charging motion with
motion blur, wings beating powerfully, approaching rapidly from background to foreground, over-the-shoulder dynamic
composition showing approach, volcanic valley background, dramatic chase lighting, extremely high detail 8K
photorealistic CGI rendering, professional fight cinematography, sharp focus on both characters, realistic motion
blur, cinematic OTS composition""",

        6: """Photorealistic CGI Pokemon electric impact scene: Dragonite's electrified fist making FULL DIRECT CONTACT
with Charizard's shoulder in devastating Thunder Punch, massive bright YELLOW ELECTRIC EXPLOSION erupting at impact
point with intense crackling energy, bright lightning arcs and electric bolts bursting outward in all directions,
Charizard with EXTREME PAINED EXPRESSION from electric shock (eyes squeezed tightly shut from pain, mouth open
extremely wide roaring in agony showing throat, face severely contorted in maximum pain), body knocked backward
violently by electric surge, bright yellow electric current visibly running through Charizard's entire body with
shock effect, Dragonite with FIERCE SATISFIED VENGEFUL EXPRESSION (eyes showing satisfaction, slight grin of
revenge, determined face), BURN MARKS STILL VISIBLE on Dragonite maintaining continuity, close-up on impact point,
bright yellow electric glow illuminating everything, electric sparks everywhere with realistic electricity physics,
volcanic valley background, maximum electric lighting effects, extremely high detail 8K photorealistic CGI rendering,
professional Hollywood VFX quality electricity, sharp focus on impact and expressions, realistic electric arcs,
cinematic impact shot"""
    }

    prompt = enhancement_prompts.get(panel_number,
        "Photorealistic CGI Pokemon battle scene with maximum detail, sharp focus, 8K quality, cinematic lighting, professional animation quality")

    print(f"\n🎨 Enhancing Panel {panel_number} with Nano Banana Pro...")
    print(f"📝 Enhancement prompt: {prompt[:150]}...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "image_urls": [image_url],
            "aspect_ratio": "16:9",
            "output_format": "jpg"
        }
    }

    print(f"🚀 Submitting to Nano Banana Pro for photorealistic enhancement...")
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
    print(f"⏳ Enhancing... ", end="", flush=True)

    timeout = 180  # 3 minutes for enhancement

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
                print(f"\n✅ Enhanced!")
                image_url = json.loads(data["resultJson"])["resultUrls"][0]

                # Download enhanced image
                print(f"📥 Downloading enhanced panel...")
                img_resp = requests.get(image_url, timeout=120)
                if img_resp.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(img_resp.content)

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
    """Enhance extracted panel to photorealistic quality."""
    import argparse

    parser = argparse.ArgumentParser(description='Enhance extracted panel with Nano Banana Pro')
    parser.add_argument('panel_image', help='Path to extracted panel image')
    parser.add_argument('--panel-number', type=int, default=1, help='Panel number (1-6) for context-specific enhancement')
    parser.add_argument('--output', help='Output path for enhanced image', default=None)

    args = parser.parse_args()

    print("""
╔════════════════════════════════════════════════════════════════════╗
║         PANEL PHOTOREALISTIC ENHANCEMENT (Nano Banana Pro)        ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ENHANCEMENT FEATURES:                                             ║
║  ✓ Photorealistic CGI quality                                     ║
║  ✓ 8K detail rendering                                            ║
║  ✓ Dynamic facial expressions                                     ║
║  ✓ Professional animation quality                                 ║
║  ✓ Sharp focus and clarity                                        ║
║  ✓ Cinematic lighting                                             ║
║  ✓ Realistic textures (scales, fire, smoke)                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    if not os.path.exists(args.panel_image):
        print(f"❌ Panel image not found: {args.panel_image}")
        return 1

    api_key = load_api_key()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        panel_basename = os.path.splitext(os.path.basename(args.panel_image))[0]
        output_dir = os.path.dirname(args.panel_image).replace('_extracted', '_enhanced')
        output_path = os.path.join(output_dir, f"{panel_basename}_enhanced.jpg")

    try:
        # Upload original panel
        image_url = upload_image(args.panel_image)

        # Enhance with Nano Banana Pro
        enhanced_path, task_id, enhanced_url = enhance_panel(
            image_url, args.panel_number, output_path, api_key
        )

        print(f"\n{'='*70}")
        print(f"🎉 PHOTOREALISTIC ENHANCEMENT COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Original: {args.panel_image}")
        print(f"📁 Enhanced: {enhanced_path}")
        print(f"🆔 Task ID: {task_id}")
        print(f"🔗 URL: {enhanced_url}")
        print(f"\n✅ QUALITY IMPROVEMENTS:")
        print(f"  ✓ Photorealistic CGI rendering")
        print(f"  ✓ Enhanced facial expressions (dynamic emotions)")
        print(f"  ✓ Maximum detail and sharpness")
        print(f"  ✓ Professional animation quality")
        print(f"  ✓ Cinematic lighting and composition")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
