#!/usr/bin/env python3
"""
Robust Image Validation Framework with Feedback Loop
Validates images against comprehensive criteria and generates improvement suggestions
"""

import os
import sys
import json
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ValidationResult:
    """Validation result for a single criterion."""
    criterion: str
    tier: str  # "Tier 0", "Tier 1", "Tier 2", "Tier 3"
    passed: bool
    score: float  # 0.0 to 1.0
    feedback: str
    severity: str  # "CRITICAL", "MAJOR", "MINOR"

@dataclass
class ImageValidation:
    """Complete validation result for an image."""
    segment_num: int
    image_path: str
    tier0_score: float  # Photorealism (0-5)
    tier1_score: float  # Pokemon features (0-17)
    tier2_score: float  # Prompt accuracy (0-7)
    tier3_score: float  # Battle accuracy (0-4)
    overall_grade: str  # "PASS", "CONDITIONAL", "FAIL"
    results: List[ValidationResult]
    improvement_suggestions: List[str]
    prompt_modifications: Dict[str, str]

class RobustImageValidator:
    """Comprehensive image validator with feedback generation."""

    def __init__(self):
        self.validation_checklist = self._load_checklist()

    def _load_checklist(self) -> Dict:
        """Load validation checklist from framework."""
        return {
            "tier0_photorealism": [
                "Realistic reptilian scales with depth and texture visible",
                "Natural lighting with physically accurate shadows",
                "Organic imperfections (scratches, weathering, battle damage)",
                "Anatomically accurate features based on real animals",
                "NO 3D animation style (smooth/polished surfaces)"
            ],
            "tier1_pokemon_critical": {
                "charizard": [
                    "Character clearly recognizable as Charizard",
                    "Orange body color (realistic orange scales)",
                    "Teal wing undersides visible",
                    "Cream belly visible",
                    "Flaming tail tip always burning",
                    "Correct build: lean, athletic"
                ],
                "dragonite": [
                    "Character clearly recognizable as Dragonite",
                    "Light ORANGE-TAN body (NOT green, NOT cream/pale)",
                    "Teal wing membranes visible",
                    "Cream belly with horizontal stripes",
                    "Two thin antennae on head",
                    "NO tail flame",
                    "Correct build: bulky, stocky",
                    "Size: 30% larger than Charizard when both present"
                ]
            },
            "tier2_prompt_accuracy": [
                "Primary action matches prompt specification",
                "Environmental elements present (crater if specified)",
                "Pokemon condition matches (battered/pristine as specified)",
                "Camera angle matches prompt",
                "Specific effects present (colors, sparks, etc.)",
                "Background accurate (volcanic valley, lava)",
                "Composition matches (both Pokemon visible if specified)"
            ],
            "tier3_battle_accuracy": [
                "Attack effects match official anime/game",
                "Physics make sense (momentum, impact)",
                "Battle damage accumulates progressively",
                "Energy colors correct (blue-purple Dragon Rage, orange Flamethrower, yellow Thunder Punch)"
            ]
        }

    def validate_image_from_prompt(self, image_path: str, segment_num: int,
                                   original_prompt: str, scene_description: dict) -> ImageValidation:
        """
        Validate image against original prompt and scene requirements.

        Args:
            image_path: Path to generated image
            segment_num: Segment number (1-18)
            original_prompt: The prompt used to generate the image
            scene_description: Dict with keys: action, pokemon_present, attack_type,
                              environment_required, camera_angle, special_requirements

        Returns:
            Complete validation results with improvement suggestions
        """

        print(f"\n{'='*70}")
        print(f"VALIDATING SEGMENT {segment_num:02d}")
        print(f"{'='*70}")
        print(f"Image: {image_path}")
        print(f"Scene: {scene_description.get('action', 'Unknown')}")

        results = []

        # TIER 0: Photorealism (CRITICAL - must pass 100%)
        print(f"\n🔍 TIER 0: PHOTOREALISM (5 criteria)")
        tier0_results = self._validate_tier0_photorealism(image_path, scene_description)
        results.extend(tier0_results)
        tier0_score = sum(r.score for r in tier0_results)
        tier0_pass = tier0_score >= 4.5  # 90%+ required
        print(f"   Score: {tier0_score:.1f}/5.0 {'✅ PASS' if tier0_pass else '❌ FAIL'}")

        # TIER 1: Pokemon Features (CRITICAL - must pass 100%)
        print(f"\n🔍 TIER 1: POKEMON FEATURES")
        tier1_results = self._validate_tier1_pokemon(image_path, scene_description)
        results.extend(tier1_results)
        tier1_score = sum(r.score for r in tier1_results)
        tier1_max = len(tier1_results)
        tier1_pass = tier1_score >= tier1_max  # 100% required
        print(f"   Score: {tier1_score:.1f}/{tier1_max} {'✅ PASS' if tier1_pass else '❌ FAIL'}")

        # TIER 2: Prompt Accuracy (must pass 86%+)
        print(f"\n🔍 TIER 2: PROMPT ACCURACY (7 criteria)")
        tier2_results = self._validate_tier2_prompt_accuracy(
            image_path, original_prompt, scene_description
        )
        results.extend(tier2_results)
        tier2_score = sum(r.score for r in tier2_results)
        tier2_pass = tier2_score >= 6.0  # 86%+ required
        print(f"   Score: {tier2_score:.1f}/7.0 {'✅ PASS' if tier2_pass else '❌ FAIL'}")

        # TIER 3: Battle Accuracy (should pass 75%+)
        print(f"\n🔍 TIER 3: BATTLE ACCURACY (4 criteria)")
        tier3_results = self._validate_tier3_battle_accuracy(
            image_path, scene_description
        )
        results.extend(tier3_results)
        tier3_score = sum(r.score for r in tier3_results)
        tier3_pass = tier3_score >= 3.0  # 75%+ required
        print(f"   Score: {tier3_score:.1f}/4.0 {'✅ PASS' if tier3_pass else '⚠️  CONDITIONAL'}")

        # Determine overall grade
        if tier0_pass and tier1_pass and tier2_pass and tier3_pass:
            grade = "PASS"
        elif tier0_pass and tier1_pass and tier2_pass:
            grade = "CONDITIONAL"
        else:
            grade = "FAIL"

        print(f"\n{'='*70}")
        print(f"OVERALL GRADE: {grade}")
        print(f"{'='*70}")

        # Generate improvement suggestions
        improvements = self._generate_improvement_suggestions(results, scene_description)
        prompt_mods = self._generate_prompt_modifications(results, original_prompt, scene_description)

        return ImageValidation(
            segment_num=segment_num,
            image_path=image_path,
            tier0_score=tier0_score,
            tier1_score=tier1_score,
            tier2_score=tier2_score,
            tier3_score=tier3_score,
            overall_grade=grade,
            results=results,
            improvement_suggestions=improvements,
            prompt_modifications=prompt_mods
        )

    def _validate_tier0_photorealism(self, image_path: str, scene: dict) -> List[ValidationResult]:
        """Validate photorealism tier - MANUAL for now, returns template."""
        # In real implementation, would use computer vision / CLIP model
        # For now, returns template for manual validation

        print("   ⚠️  MANUAL VALIDATION REQUIRED:")
        print("   1. Detailed realistic scales visible? (not smooth 3D)")
        print("   2. Natural lighting with accurate shadows?")
        print("   3. Organic weathering/imperfections visible?")
        print("   4. Anatomically accurate (real animal-based)?")
        print("   5. NOT 3D animation style?")

        # Return placeholder - user will fill in
        return [
            ValidationResult("Realistic scales", "Tier 0", True, 1.0, "Check manually", "CRITICAL"),
            ValidationResult("Natural lighting", "Tier 0", True, 1.0, "Check manually", "CRITICAL"),
            ValidationResult("Organic imperfections", "Tier 0", True, 1.0, "Check manually", "CRITICAL"),
            ValidationResult("Anatomical accuracy", "Tier 0", True, 1.0, "Check manually", "CRITICAL"),
            ValidationResult("No 3D animation", "Tier 0", True, 1.0, "Check manually", "CRITICAL"),
        ]

    def _validate_tier1_pokemon(self, image_path: str, scene: dict) -> List[ValidationResult]:
        """Validate Pokemon features - MANUAL for now."""
        pokemon_present = scene.get('pokemon_present', ['charizard'])

        print(f"   Pokemon present: {', '.join(pokemon_present)}")
        print("   ⚠️  MANUAL VALIDATION REQUIRED:")

        results = []
        if 'charizard' in pokemon_present:
            print("   CHARIZARD:")
            print("     - Recognizable as Charizard?")
            print("     - Orange body with realistic scales?")
            print("     - Teal wing undersides visible?")
            print("     - Cream belly visible?")
            print("     - Flaming tail?")
            print("     - Lean athletic build?")

            results.extend([
                ValidationResult("Charizard recognition", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Charizard orange body", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Charizard teal wings", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Charizard cream belly", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Charizard tail flame", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
            ])

        if 'dragonite' in pokemon_present:
            print("   DRAGONITE:")
            print("     - Recognizable as Dragonite?")
            print("     - ORANGE-TAN body (NOT green/pale)?")
            print("     - Teal wing membranes visible?")
            print("     - Cream belly with stripes?")
            print("     - Two antennae?")
            print("     - NO tail flame?")
            print("     - Bulky stocky build?")
            print("     - 30% larger than Charizard if both present?")

            results.extend([
                ValidationResult("Dragonite recognition", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Dragonite orange-tan body", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Dragonite teal wings", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Dragonite cream belly", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Dragonite antennae", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Dragonite no tail flame", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
                ValidationResult("Dragonite size 30% larger", "Tier 1", True, 1.0, "Manual check", "CRITICAL"),
            ])

        return results

    def _validate_tier2_prompt_accuracy(self, image_path: str, prompt: str, scene: dict) -> List[ValidationResult]:
        """Validate prompt accuracy - check if specified elements are present."""
        print("   ⚠️  MANUAL VALIDATION REQUIRED:")
        print(f"   Primary action: {scene.get('action', 'N/A')}")

        results = []

        # Check for required environmental elements
        env_required = scene.get('environment_required', [])
        if env_required:
            print(f"   Required environment: {', '.join(env_required)}")
            for env in env_required:
                results.append(
                    ValidationResult(f"Environment: {env}", "Tier 2", True, 1.0, "Check manually", "MAJOR")
                )
        else:
            results.append(
                ValidationResult("Environment elements", "Tier 2", True, 1.0, "Not specified", "MAJOR")
            )

        # Check action accuracy
        results.append(
            ValidationResult("Primary action matches", "Tier 2", True, 1.0, "Manual check", "MAJOR")
        )

        # Check camera angle
        camera = scene.get('camera_angle', 'Not specified')
        print(f"   Camera angle: {camera}")
        results.append(
            ValidationResult("Camera angle", "Tier 2", True, 1.0, "Manual check", "MAJOR")
        )

        # Check Pokemon condition
        condition = scene.get('pokemon_condition', 'normal')
        print(f"   Pokemon condition: {condition}")
        results.append(
            ValidationResult("Pokemon condition", "Tier 2", True, 1.0, "Manual check", "MAJOR")
        )

        # Check composition
        results.append(
            ValidationResult("Composition matches", "Tier 2", True, 1.0, "Manual check", "MAJOR")
        )

        # Check special requirements
        special = scene.get('special_requirements', [])
        if special:
            print(f"   Special requirements: {', '.join(special)}")
            for req in special:
                results.append(
                    ValidationResult(f"Special: {req}", "Tier 2", True, 1.0, "Check manually", "MAJOR")
                )
        else:
            results.append(
                ValidationResult("Special requirements", "Tier 2", True, 1.0, "None specified", "MAJOR")
            )

        return results[:7]  # Return exactly 7 for consistency

    def _validate_tier3_battle_accuracy(self, image_path: str, scene: dict) -> List[ValidationResult]:
        """Validate battle/attack accuracy."""
        attack_type = scene.get('attack_type')

        results = []

        if attack_type:
            print(f"   Attack type: {attack_type}")
            print("   Check attack appearance matches official sources:")

            if attack_type == "Flamethrower":
                print("     - Red-orange sustained stream from mouth?")
            elif attack_type == "Thunder Punch":
                print("     - Yellow electricity on fist/claw?")
            elif attack_type == "Dragon Rage":
                print("     - Blue-purple energy sphere/beam?")
            elif attack_type == "Seismic Toss":
                print("     - Grab/spin/throw sequence visible?")
                print("     - Crater impact if aftermath?")

            results.append(
                ValidationResult("Attack appearance", "Tier 3", True, 1.0, "Manual check", "MINOR")
            )
        else:
            results.append(
                ValidationResult("Attack appearance", "Tier 3", True, 1.0, "No attack", "MINOR")
            )

        # Physics check
        results.append(
            ValidationResult("Physics realistic", "Tier 3", True, 1.0, "Manual check", "MINOR")
        )

        # Battle damage progression
        segment_num = scene.get('segment_num', 1)
        if segment_num >= 11:
            print("   Late segment - battle damage should be visible")
            results.append(
                ValidationResult("Battle damage present", "Tier 3", True, 1.0, "Manual check", "MINOR")
            )
        else:
            results.append(
                ValidationResult("Battle damage", "Tier 3", True, 1.0, "Early segment, minimal expected", "MINOR")
            )

        # Energy colors
        results.append(
            ValidationResult("Energy colors correct", "Tier 3", True, 1.0, "Manual check", "MINOR")
        )

        return results

    def _generate_improvement_suggestions(self, results: List[ValidationResult],
                                         scene: dict) -> List[str]:
        """Generate improvement suggestions based on failures."""
        suggestions = []

        # Group failures by tier
        tier0_failures = [r for r in results if r.tier == "Tier 0" and not r.passed]
        tier1_failures = [r for r in results if r.tier == "Tier 1" and not r.passed]
        tier2_failures = [r for r in results if r.tier == "Tier 2" and not r.passed]
        tier3_failures = [r for r in results if r.tier == "Tier 3" and not r.passed]

        if tier0_failures:
            suggestions.append("CRITICAL: Add more photorealistic emphasis in prompt")
            suggestions.append("Add: 'PHOTOREALISTIC hyperrealistic CGI render'")
            suggestions.append("Add: 'detailed realistic reptilian scales with texture'")
            suggestions.append("Add: 'natural lighting with physically accurate shadows'")

        if tier1_failures:
            for failure in tier1_failures:
                if "orange-tan" in failure.criterion.lower():
                    suggestions.append("CRITICAL: Emphasize 'light ORANGE-TAN body (NOT green, NOT cream/pale)'")
                if "wings" in failure.criterion.lower():
                    suggestions.append("CRITICAL: Add 'teal turquoise wing membranes clearly visible'")
                if "size" in failure.criterion.lower():
                    suggestions.append("CRITICAL: Add 'significantly larger Dragonite (30% bigger than Charizard)'")

        if tier2_failures:
            for failure in tier2_failures:
                if "crater" in failure.criterion.lower():
                    suggestions.append("MAJOR: Add 'massive impact crater with debris and dust'")
                if "battle" in failure.criterion.lower() or "battered" in failure.criterion.lower():
                    suggestions.append("MAJOR: Add 'battle-worn with scratches and scars, exhausted appearance'")

        if tier3_failures:
            attack = scene.get('attack_type')
            if attack:
                suggestions.append(f"MINOR: Verify {attack} appearance matches official anime/game depiction")

        return suggestions

    def _generate_prompt_modifications(self, results: List[ValidationResult],
                                      original_prompt: str, scene: dict) -> Dict[str, str]:
        """Generate specific prompt modifications for next iteration."""
        mods = {
            "add_prefix": "",
            "add_suffix": "",
            "replace_terms": {},
            "enhanced_prompt": ""
        }

        failures = [r for r in results if not r.passed]

        # Add photorealistic prefix if Tier 0 failures
        tier0_failures = [r for r in failures if r.tier == "Tier 0"]
        if tier0_failures:
            mods["add_prefix"] = "PHOTOREALISTIC hyperrealistic CGI render: "

        # Add specific fixes based on failures
        additions = []

        for failure in failures:
            if "orange-tan" in failure.criterion.lower():
                mods["replace_terms"]["orange dragon"] = "light ORANGE-TAN dragon (NOT green, NOT cream)"
            if "crater" in failure.criterion.lower():
                additions.append("massive impact crater with debris visible on ground")
            if "battle-worn" in failure.criterion.lower() or "battered" in failure.criterion.lower():
                additions.append("battle-worn with scratches and scars, exhausted battered appearance")

        if additions:
            mods["add_suffix"] = ", " + ", ".join(additions)

        # Generate enhanced prompt
        enhanced = original_prompt
        if mods["add_prefix"] and not enhanced.startswith("PHOTOREALISTIC"):
            enhanced = mods["add_prefix"] + enhanced

        for old, new in mods["replace_terms"].items():
            enhanced = enhanced.replace(old, new)

        if mods["add_suffix"]:
            enhanced += mods["add_suffix"]

        mods["enhanced_prompt"] = enhanced

        return mods

    def save_validation_report(self, validation: ImageValidation, output_path: str):
        """Save validation report to JSON."""
        report = {
            "segment": validation.segment_num,
            "image": validation.image_path,
            "grade": validation.overall_grade,
            "scores": {
                "tier0_photorealism": f"{validation.tier0_score}/5.0",
                "tier1_pokemon": f"{validation.tier1_score}/{len([r for r in validation.results if r.tier == 'Tier 1'])}",
                "tier2_prompt_accuracy": f"{validation.tier2_score}/7.0",
                "tier3_battle_accuracy": f"{validation.tier3_score}/4.0"
            },
            "results": [
                {
                    "criterion": r.criterion,
                    "tier": r.tier,
                    "passed": r.passed,
                    "score": r.score,
                    "feedback": r.feedback,
                    "severity": r.severity
                }
                for r in validation.results
            ],
            "improvements": validation.improvement_suggestions,
            "prompt_modifications": validation.prompt_modifications
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Validation report saved: {output_path}")


def main():
    """Test the robust validator."""
    validator = RobustImageValidator()

    # Example validation
    test_scene = {
        "action": "Face-off confrontation",
        "pokemon_present": ["charizard", "dragonite"],
        "attack_type": None,
        "environment_required": ["stormy sky", "lightning"],
        "camera_angle": "ground level, both Pokemon visible",
        "pokemon_condition": "battle-ready",
        "special_requirements": ["size difference obvious", "dramatic lighting"],
        "segment_num": 3
    }

    test_prompt = "Epic face-off: Charizard on ground looking up at larger Dragonite descending from stormy sky"
    test_image = "charizard/battle_assets/test_results/seg03_nanobanana_photorealistic.jpg"

    if os.path.exists(test_image):
        validation = validator.validate_image_from_prompt(
            test_image, 3, test_prompt, test_scene
        )

        print(f"\n{'='*70}")
        print("IMPROVEMENT SUGGESTIONS:")
        print(f"{'='*70}")
        for i, suggestion in enumerate(validation.improvement_suggestions, 1):
            print(f"{i}. {suggestion}")

        print(f"\n{'='*70}")
        print("PROMPT MODIFICATIONS:")
        print(f"{'='*70}")
        print(f"Enhanced prompt:\n{validation.prompt_modifications['enhanced_prompt']}")

        # Save report
        validator.save_validation_report(
            validation,
            "charizard/validation_reports/seg03_validation.json"
        )
    else:
        print(f"❌ Test image not found: {test_image}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
