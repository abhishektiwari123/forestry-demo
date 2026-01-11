#!/usr/bin/env python3
"""
Comprehensive Content Validation - Checks WHAT'S IN the image/video, not just technical specs.
Integrates the robust 14-16 step validation process (Tier 0-3).
"""

import os
import sys
from typing import Dict, List

# Import the robust validator
sys.path.insert(0, 'scripts')
from validate_image_robust import RobustImageValidator, ImageValidation

class ComprehensiveContentValidator:
    """
    Comprehensive validator that checks content (not just technical specs).

    Uses Tier 0-3 validation:
    - Tier 0: Photorealism (5 criteria)
    - Tier 1: Pokemon Features (6-8 criteria per Pokemon)
    - Tier 2: Prompt Accuracy (7 criteria)
    - Tier 3: Battle Accuracy (4 criteria)

    Total: ~16-24 validation steps depending on scene
    """

    def __init__(self):
        self.robust_validator = RobustImageValidator()

    def validate_scene_content(self, image_path: str, scene_num: int, scene_def: Dict) -> ImageValidation:
        """
        Validate scene content against comprehensive criteria.

        Args:
            image_path: Path to generated image
            scene_num: Scene number (1-4 for our 4-scene pipeline)
            scene_def: Scene definition with action, pokemon, camera_angle, prompt, etc.

        Returns:
            Comprehensive validation results with improvement suggestions
        """

        # Build scene description for validator
        scene_description = {
            "action": scene_def.get("action", "Unknown"),
            "pokemon_present": scene_def.get("pokemon", ["charizard"]),
            "attack_type": scene_def.get("attack_type"),
            "environment_required": scene_def.get("environment", ["volcanic valley"]),
            "camera_angle": scene_def.get("camera_angle", "Unknown"),
            "pokemon_condition": scene_def.get("condition", "normal"),
            "special_requirements": scene_def.get("special_requirements", []),
            "segment_num": scene_num
        }

        original_prompt = scene_def.get("prompt", "")

        # Run comprehensive validation
        validation = self.robust_validator.validate_image_from_prompt(
            image_path, scene_num, original_prompt, scene_description
        )

        return validation

    def print_validation_summary(self, validation: ImageValidation):
        """Print comprehensive validation summary."""
        print(f"\n{'='*70}")
        print(f"COMPREHENSIVE VALIDATION SUMMARY")
        print(f"{'='*70}")
        print(f"Scene: {validation.segment_num}")
        print(f"Image: {validation.image_path}")
        print(f"Overall Grade: {validation.overall_grade}")
        print(f"\nScores:")
        print(f"  Tier 0 (Photorealism): {validation.tier0_score}/5.0")
        print(f"  Tier 1 (Pokemon Features): {validation.tier1_score}/{len([r for r in validation.results if r.tier == 'Tier 1'])}")
        print(f"  Tier 2 (Prompt Accuracy): {validation.tier2_score}/7.0")
        print(f"  Tier 3 (Battle Accuracy): {validation.tier3_score}/4.0")

        # Show failures
        failures = [r for r in validation.results if not r.passed]
        if failures:
            print(f"\n⚠️  FAILURES FOUND ({len(failures)}):")
            for failure in failures:
                print(f"   [{failure.tier}] {failure.criterion}: {failure.feedback}")

        # Show improvement suggestions
        if validation.improvement_suggestions:
            print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
            for i, suggestion in enumerate(validation.improvement_suggestions, 1):
                print(f"   {i}. {suggestion}")

        print(f"{'='*70}")

    def validate_flamethrower_scene(self, image_path: str) -> Dict:
        """
        Specific validation for Flamethrower attack scene (Scene 1 or 2).

        Critical checks:
        - Charizard on LEFT launching Flamethrower
        - Dragonite on RIGHT taking hit with PAIN expression
        - NO SHIELD on Dragonite (must take direct hit)
        - Flame stream connecting both Pokemon
        - Dragonite being pushed backward by force
        - Impact glow visible where flames strike
        """
        print(f"\n{'='*70}")
        print(f"FLAMETHROWER SCENE VALIDATION")
        print(f"{'='*70}")
        print(f"Image: {image_path}")

        # Manual validation checklist
        print(f"\n📋 CRITICAL CONTENT CHECKS (User must verify):")
        print(f"\n1. CHARIZARD:")
        print(f"   - Position: LEFT side of frame? ⬜")
        print(f"   - Action: Launching Flamethrower from mouth? ⬜")
        print(f"   - Expression: Fierce/determined? ⬜")

        print(f"\n2. DRAGONITE:")
        print(f"   - Position: RIGHT side of frame? ⬜")
        print(f"   - ❌ NO SHIELD (must take direct hit)? ⬜")
        print(f"   - Expression: PAINED (eyes squinting, mouth open, grimacing)? ⬜")
        print(f"   - Action: Being pushed BACKWARD by flames? ⬜")
        print(f"   - Body language: Defensive (arms raised but failing)? ⬜")

        print(f"\n3. ATTACK EFFECTS:")
        print(f"   - Flame stream: Orange-red, connecting both Pokemon? ⬜")
        print(f"   - Impact glow: Visible where flames strike Dragonite? ⬜")
        print(f"   - Heat distortion: Visible around flames? ⬜")
        print(f"   - Knockback: Dragonite visibly recoiling? ⬜")

        print(f"\n4. COMPOSITION:")
        print(f"   - Both Pokemon in frame? ⬜")
        print(f"   - Side-angle wide shot? ⬜")
        print(f"   - Complete attack visible (attacker + target)? ⬜")

        print(f"\n⚠️  USER ACTION REQUIRED:")
        print(f"   Please manually check the image above and answer:")
        print(f"   - Does Dragonite have a shield? (Should be NO)")
        print(f"   - Is Dragonite taking direct hit with pain expression?")
        print(f"   - Are all critical elements present?")

        return {
            "scene": "Flamethrower attack",
            "image": image_path,
            "requires_manual_review": True,
            "critical_checks": [
                "Charizard on LEFT launching Flamethrower",
                "Dragonite on RIGHT with NO SHIELD",
                "Dragonite showing PAIN expression",
                "Dragonite being pushed backward",
                "Flame stream connecting both Pokemon",
                "Impact glow visible"
            ]
        }


def main():
    """Validate Scene 1 with comprehensive content validation."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║         COMPREHENSIVE CONTENT VALIDATION - SCENE 1                 ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Using 14-16 step robust validation framework (Tier 0-3)          ║
║  Checks WHAT'S IN the image, not just technical specs             ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    validator = ComprehensiveContentValidator()

    # Scene 1 definition
    scene1 = {
        "action": "Charizard launching Flamethrower, Dragonite taking hit with pain",
        "pokemon": ["charizard", "dragonite"],
        "attack_type": "Flamethrower",
        "camera_angle": "Side-angle wide shot",
        "environment": ["volcanic valley"],
        "condition": "battle-ready",
        "special_requirements": [
            "Both Pokemon in frame",
            "Charizard on LEFT",
            "Dragonite on RIGHT",
            "NO SHIELD on Dragonite",
            "Dragonite showing PAIN expression",
            "Flame stream connecting both Pokemon",
            "Impact glow where flames strike",
            "Dragonite being pushed backward"
        ],
        "prompt": "Charizard launching massive orange-red Flamethrower stream from jaws with fierce expression, flames beginning to travel toward Dragonite on right, side-angle wide shot, volcanic valley, dramatic battle start"
    }

    scene1_image = "charizard/battle_assets/clean_4scenes/scene1_flamethrower_launch.jpg"

    if not os.path.exists(scene1_image):
        print(f"❌ Scene 1 image not found: {scene1_image}")
        return 1

    # Comprehensive validation
    print(f"\n{'='*70}")
    print("RUNNING TIER 0-3 VALIDATION")
    print(f"{'='*70}")

    validation = validator.validate_scene_content(scene1_image, 1, scene1)
    validator.print_validation_summary(validation)

    # Specific Flamethrower scene validation
    flamethrower_check = validator.validate_flamethrower_scene(scene1_image)

    # Save validation report
    os.makedirs("charizard/validation_reports", exist_ok=True)
    report_path = "charizard/validation_reports/scene1_comprehensive_validation.json"
    validator.robust_validator.save_validation_report(validation, report_path)

    print(f"\n🎉 Validation complete!")
    print(f"📁 Report saved: {report_path}")
    print(f"\n⚠️  Please review the validation results above and confirm:")
    print(f"   - Does Dragonite have a shield in the image?")
    print(f"   - Should we regenerate Scene 1 if validation failed?")

    return 0


if __name__ == "__main__":
    sys.exit(main())
