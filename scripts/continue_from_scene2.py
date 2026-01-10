#!/usr/bin/env python3
"""
Continue generating videos from Scene 2 onwards (Scene 1 already complete).
"""

import os
import sys
sys.path.insert(0, 'scripts')
from generate_videos_from_existing_scenes import (
    load_api_key, generate_video_from_scene, concatenate_videos
)


def main():
    """Continue from Scene 2."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           CONTINUE FROM SCENE 2 (Scene 1 already complete)        ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()

    # Scenes 2-6 (Scene 1 already done)
    scenes_dir = "charizard/battle_assets/storyboard/scenes"
    scene_files = [
        "scene2_flames_traveling.jpg",
        "scene3_impact_pain.jpg",
        "scene4_burn_marks.jpg",
        "scene5_angry_expression.jpg",
        "scene6_charge_forward.jpg"
    ]

    scene_paths = [os.path.join(scenes_dir, f) for f in scene_files]

    # Simplified prompts (no camera/validation terms)
    scene_prompts = [
        "Massive orange-red Flamethrower stream traveling with realistic fire physics and intense heat distortion, dramatic lighting, volcanic valley background",
        "Flames striking Dragonite causing intense pain reaction and knockback, bright impact effects, Dragonite grimacing with arms raised defensively, body pushed backward, dramatic battle intensity",
        "Flames dissipating as burn marks appear on Dragonite body, blackened scorch marks visible on torso, smoke rising from burnt scales, Dragonite recovering from knockback, realistic damage effects",
        "Dragonite expression transitioning from pain to fierce anger, eyes narrowing with rage, teeth bared in aggressive snarl, body tensing for revenge counter-attack, dramatic emotion",
        "Dragonite charging forward aggressively toward Charizard with wings spread wide, fierce attack stance, burn marks visible on battle-worn body, Charizard bracing for incoming revenge attack"
    ]

    # Generate videos from scenes 2-6
    print(f"\n{'='*70}")
    print("GENERATING VIDEOS FOR SCENES 2-6")
    print(f"{'='*70}")

    video_paths = ["charizard/battle_assets/videos/storyboard_scene1_charizard_launch.mp4"]  # Scene 1 already done

    for scene_path, prompt in zip(scene_paths, scene_prompts):
        scene_name = os.path.splitext(os.path.basename(scene_path))[0]
        try:
            video_path = generate_video_from_scene(scene_path, scene_name, prompt, api_key)
            video_paths.append(video_path)
        except Exception as e:
            print(f"\n❌ Failed on {scene_name}: {e}")
            print(f"Continuing with remaining scenes...")

    # Concatenate all videos
    if len(video_paths) >= 2:
        print(f"\n{'='*70}")
        print(f"CONCATENATING {len(video_paths)} VIDEOS")
        print(f"{'='*70}")

        final_output = "charizard/battle_assets/videos/final_6scene_sequence_30s.mp4"
        concatenate_videos(video_paths, final_output)

        print(f"\n🎉 SUCCESS!")
        print(f"✅ Generated {len(video_paths)} videos")
        print(f"📁 Final Video: {final_output}")
    else:
        print(f"\n⚠️  Only {len(video_paths)} video(s) available, need at least 2 for concatenation")

    return 0


if __name__ == "__main__":
    sys.exit(main())
