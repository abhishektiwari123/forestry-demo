#!/usr/bin/env python3
"""
Continue generating videos from Scene 2 onwards (Scene 1 already complete).
Includes validation framework after each generation.
"""

import os
import sys
sys.path.insert(0, 'scripts')
from generate_videos_from_existing_scenes import (
    load_api_key, generate_video_from_scene, concatenate_videos
)
from validation_framework import ValidationFramework, SCENE_VIDEO_CRITERIA


def main():
    """Continue from Scene 2 with validation."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║     CONTINUE FROM SCENE 2 + VALIDATION FRAMEWORK (Scene 1 done)   ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    api_key = load_api_key()
    validator = ValidationFramework()

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

            # VALIDATE VIDEO after generation
            print(f"\n{'='*70}")
            print(f"VALIDATION: {scene_name}")
            print(f"{'='*70}")
            validation_result = validator.validate_video(video_path, SCENE_VIDEO_CRITERIA)

            if not validation_result["passed"]:
                print(f"\n⚠️  Validation issues found for {scene_name}")
                print("   Consider regenerating with improved prompt")

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

        # Validate final video
        print(f"\n{'='*70}")
        print("FINAL VIDEO VALIDATION")
        print(f"{'='*70}")
        final_criteria = {
            "min_duration": 25.0,  # ~30s for 6 scenes
            "max_duration": 35.0,
            "min_size_mb": 30.0,
            "max_size_mb": 100.0,
            "must_have_audio": True
        }
        validator.validate_video(final_output, final_criteria)

    else:
        print(f"\n⚠️  Only {len(video_paths)} video(s) available, need at least 2 for concatenation")

    # Generate feedback report
    print(f"\n{'='*70}")
    print("GENERATING VALIDATION FEEDBACK REPORT")
    print(f"{'='*70}")
    report_path = "charizard/battle_assets/validation_report.txt"
    validator.generate_feedback_report(report_path)

    # Save validation log
    log_path = "charizard/battle_assets/validation_log.json"
    validator.save_validation_log(log_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
