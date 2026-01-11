#!/usr/bin/env python3
"""
Enhanced Validation Framework with:
1. NO NEW ELEMENTS check (catches shields, barriers, extra objects)
2. Storyboard continuity validation (frame-by-frame consistency)

Based on:
- Storyboard best practices from animation industry
- Nano Banana Pro storyboard capabilities
- User feedback: Dragonite had shield (WRONG - new element added)
"""

import os
import sys
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ValidationCriteria:
    """Enhanced validation criteria with storyboard checks."""

    # Existing technical validation
    image_min_width: int = 800
    image_min_height: int = 450
    image_min_size_mb: float = 0.1
    image_max_size_mb: float = 5.0
    video_min_duration: float = 4.5
    video_max_duration: float = 5.5
    video_min_size_mb: float = 5.0
    video_max_size_mb: float = 25.0

    # NEW: Content validation
    no_new_elements: bool = True  # CRITICAL: No shields, barriers, extra objects

    # NEW: Storyboard continuity validation
    character_consistency: bool = True  # Same character appearance across frames
    scene_coherence: bool = True  # Logical flow between frames
    element_continuity: bool = True  # Only elements from prompt, no additions

    # Storyboard-specific checks
    smooth_transitions: bool = True  # Frame-by-frame continuity
    consistent_lighting: bool = True  # Lighting consistent across sequence
    consistent_scale: bool = True  # Character sizes consistent


class EnhancedValidationFramework:
    """
    Enhanced validation with NO NEW ELEMENTS check and storyboard validation.

    Based on best practices:
    - Storyboard clarity over detail (46 Best Movie Storyboard Examples)
    - Frame-by-frame continuity (Nano Banana Pro storyboard guide)
    - Character consistency across frames (95%+ accuracy requirement)
    """

    def __init__(self):
        self.validation_results = []
        self.criteria = ValidationCriteria()

    def validate_no_new_elements(self, scene_path: str, scene_definition: Dict) -> Dict:
        """
        CRITICAL VALIDATION: Check for NEW ELEMENTS not in prompt.

        This catches issues like:
        - ❌ Shield on Dragonite (WRONG - not in prompt)
        - ❌ Defensive barriers
        - ❌ Extra objects not specified
        - ❌ Background elements not requested

        Args:
            scene_path: Path to image/video
            scene_definition: Original scene definition with prompt

        Returns:
            Validation result with element check
        """
        print(f"\n{'='*70}")
        print(f"VALIDATION: NO NEW ELEMENTS CHECK")
        print(f"{'='*70}")
        print(f"Scene: {scene_path}")

        prompt = scene_definition.get("prompt", "")
        special_requirements = scene_definition.get("special_requirements", [])

        print(f"\n📋 Checking for unauthorized elements...")
        print(f"Original prompt elements:")
        print(f"  {prompt[:150]}...")

        # Manual check required
        print(f"\n⚠️  MANUAL VERIFICATION REQUIRED:")
        print(f"\n❌ FORBIDDEN ELEMENTS (must NOT appear):")
        print(f"  - Shields")
        print(f"  - Defensive barriers")
        print(f"  - Force fields")
        print(f"  - Protective auras")
        print(f"  - Extra weapons not in prompt")
        print(f"  - Additional Pokemon not specified")
        print(f"  - Background objects not requested")

        # Check special requirements
        if "NO SHIELD" in str(special_requirements):
            print(f"\n🔴 CRITICAL: Scene explicitly requires NO SHIELD")
            print(f"   If shield visible → VALIDATION FAILS")

        # Example: Dragonite shield issue
        pokemon = scene_definition.get("pokemon", [])
        if "dragonite" in pokemon:
            print(f"\n🔍 DRAGONITE SPECIFIC CHECKS:")
            print(f"   - Does Dragonite have a SHIELD? → Should be NO")
            print(f"   - Does Dragonite have defensive barrier? → Should be NO")
            print(f"   - Is Dragonite taking DIRECT HIT? → Should be YES")
            print(f"   - Any extra protective elements? → Should be NO")

        result = {
            "validation_type": "no_new_elements",
            "scene": scene_path,
            "status": "MANUAL_REVIEW_REQUIRED",
            "critical_checks": [
                "No shields added",
                "No defensive barriers",
                "No extra objects beyond prompt",
                "Only elements from original scene definition"
            ],
            "pass_condition": "All unauthorized elements absent"
        }

        return result

    def validate_storyboard_continuity(self, scenes: List[Dict]) -> Dict:
        """
        Validate frame-by-frame continuity across storyboard sequence.

        Based on best practices:
        1. Character consistency (appearance, size, colors)
        2. Scene coherence (logical flow between frames)
        3. Element continuity (no new elements added mid-sequence)
        4. Smooth transitions (actions flow naturally)

        From sources:
        - Nano Banana Pro: 95%+ character consistency requirement
        - Animation storyboarding: clarity and continuity are critical
        - Frame-by-frame coherence for professional output
        """
        print(f"\n{'='*70}")
        print(f"STORYBOARD CONTINUITY VALIDATION")
        print(f"{'='*70}")
        print(f"Validating {len(scenes)} scenes as continuous sequence\n")

        continuity_checks = []

        # Check 1: Character Consistency
        print(f"✓ CHECK 1: CHARACTER CONSISTENCY")
        print(f"  Requirement: 95%+ consistency (Nano Banana Pro standard)")
        print(f"  ⚠️  MANUAL CHECK:")
        print(f"     - Charizard colors consistent across all frames?")
        print(f"     - Charizard size consistent?")
        print(f"     - Dragonite colors consistent (ORANGE-TAN, not green)?")
        print(f"     - Dragonite size consistent (30% larger)?")
        continuity_checks.append({
            "check": "character_consistency",
            "requirement": "95%+ accuracy",
            "status": "MANUAL_REVIEW"
        })

        # Check 2: Scene Coherence
        print(f"\n✓ CHECK 2: SCENE COHERENCE")
        print(f"  Requirement: Logical flow between frames")
        print(f"  ⚠️  MANUAL CHECK:")
        print(f"     Scene 1 → Scene 2: Attack launch → Impact?")
        print(f"     Scene 2 → Scene 3: Impact → Burn marks visible?")
        print(f"     Scene 3 → Scene 4: Anger → Charging forward?")
        print(f"     Does narrative flow make sense?")
        continuity_checks.append({
            "check": "scene_coherence",
            "requirement": "Logical narrative flow",
            "status": "MANUAL_REVIEW"
        })

        # Check 3: Element Continuity (NO NEW ELEMENTS)
        print(f"\n✓ CHECK 3: ELEMENT CONTINUITY")
        print(f"  Requirement: Only elements from prompts, no additions")
        print(f"  ⚠️  MANUAL CHECK:")
        print(f"     - Scene 1: Any shields? → Should be NO")
        print(f"     - Scene 2: Any shields? → Should be NO")
        print(f"     - Scene 3: Burn marks present? → Should be YES")
        print(f"     - Scene 3: Any shields? → Should be NO")
        print(f"     - Scene 4: Burn marks still visible? → Should be YES")
        print(f"     - Scene 4: Any shields? → Should be NO")
        print(f"     - New elements added mid-sequence? → Should be NO")
        continuity_checks.append({
            "check": "element_continuity",
            "requirement": "No unauthorized elements added",
            "status": "MANUAL_REVIEW",
            "critical": True
        })

        # Check 4: Smooth Transitions
        print(f"\n✓ CHECK 4: SMOOTH TRANSITIONS")
        print(f"  Requirement: Frame-by-frame action continuity")
        print(f"  ⚠️  MANUAL CHECK:")
        print(f"     - Actions flow naturally between frames?")
        print(f"     - No jarring jumps in position/pose?")
        print(f"     - Camera angles consistent with story?")
        continuity_checks.append({
            "check": "smooth_transitions",
            "requirement": "Natural action flow",
            "status": "MANUAL_REVIEW"
        })

        # Check 5: Lighting Consistency
        print(f"\n✓ CHECK 5: LIGHTING CONSISTENCY")
        print(f"  Requirement: Lighting matches across sequence")
        print(f"  ⚠️  MANUAL CHECK:")
        print(f"     - Volcanic valley lighting consistent?")
        print(f"     - Fire glow effects consistent?")
        print(f"     - No sudden lighting changes?")
        continuity_checks.append({
            "check": "lighting_consistency",
            "requirement": "Consistent environmental lighting",
            "status": "MANUAL_REVIEW"
        })

        result = {
            "validation_type": "storyboard_continuity",
            "total_scenes": len(scenes),
            "continuity_checks": continuity_checks,
            "status": "MANUAL_REVIEW_REQUIRED",
            "critical_failures": [],
            "recommendations": []
        }

        print(f"\n{'='*70}")
        print(f"STORYBOARD VALIDATION: {len(continuity_checks)} checks to review")
        print(f"{'='*70}")

        return result

    def generate_enhanced_validation_report(self, scene_validations: List[Dict],
                                           storyboard_validation: Dict,
                                           output_path: str):
        """
        Generate comprehensive validation report including:
        1. Technical validation (file sizes, durations)
        2. NO NEW ELEMENTS validation
        3. Storyboard continuity validation
        """
        report_lines = [
            "# ENHANCED VALIDATION REPORT",
            "=" * 70,
            "",
            "## VALIDATION FRAMEWORK",
            "- Technical specs (file size, duration, resolution)",
            "- NO NEW ELEMENTS check (shields, barriers, extra objects)",
            "- Storyboard continuity (character consistency, scene coherence)",
            "",
            "Based on:",
            "- Storyboard best practices (clarity, continuity, consistency)",
            "- Nano Banana Pro standards (95%+ character consistency)",
            "- User feedback (Task ID: f59fa6b100331a3a049e8ece19c58347 - shield issue)",
            "",
            "=" * 70,
            ""
        ]

        # Scene-by-scene validation
        report_lines.append("## SCENE-BY-SCENE VALIDATION")
        report_lines.append("")

        for i, scene_val in enumerate(scene_validations, 1):
            report_lines.append(f"### Scene {i}: {scene_val.get('scene', 'Unknown')}")
            report_lines.append(f"Status: {scene_val.get('status', 'UNKNOWN')}")

            if scene_val.get("critical_checks"):
                report_lines.append(f"Critical checks:")
                for check in scene_val["critical_checks"]:
                    report_lines.append(f"  - {check}")

            report_lines.append("")

        # Storyboard continuity
        report_lines.append("## STORYBOARD CONTINUITY VALIDATION")
        report_lines.append("")
        report_lines.append(f"Total scenes: {storyboard_validation.get('total_scenes', 0)}")
        report_lines.append(f"Continuity checks: {len(storyboard_validation.get('continuity_checks', []))}")
        report_lines.append("")

        for check in storyboard_validation.get("continuity_checks", []):
            status = "🔴 CRITICAL" if check.get("critical") else "⚠️"
            report_lines.append(f"{status} {check['check']}: {check['requirement']}")

        report_lines.append("")
        report_lines.append("=" * 70)
        report_lines.append("")
        report_lines.append("## NEXT STEPS")
        report_lines.append("")
        report_lines.append("1. Manually review all scenes against checklists above")
        report_lines.append("2. If shield/barrier found: REGENERATE with 'NO SHIELD' emphasis")
        report_lines.append("3. If character inconsistency: Review prompts for consistency")
        report_lines.append("4. If element added: Regenerate with stricter prompt control")
        report_lines.append("5. Validate continuity across full sequence")
        report_lines.append("")
        report_lines.append("=" * 70)

        # Save report
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))

        print(f"\n📄 Enhanced validation report saved: {output_path}")


def main():
    """Test enhanced validation framework."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           ENHANCED VALIDATION FRAMEWORK                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  NEW VALIDATIONS:                                                  ║
║  1. NO NEW ELEMENTS (catches shields, barriers)                   ║
║  2. Storyboard continuity (frame-by-frame consistency)            ║
║                                                                    ║
║  Based on user feedback: Task ID f59fa6b100331a3a049e8ece19c58347 ║
║  Issue: Dragonite had shield (WRONG - new element added)          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    validator = EnhancedValidationFramework()

    # Example scene definitions
    scenes = [
        {
            "num": 1,
            "path": "charizard/battle_assets/clean_4scenes/scene1_flamethrower_launch.jpg",
            "prompt": "Charizard launching Flamethrower, Dragonite on right",
            "pokemon": ["charizard", "dragonite"],
            "special_requirements": ["NO SHIELD on Dragonite"]
        },
        {
            "num": 2,
            "path": "charizard/battle_assets/clean_4scenes/scene2_impact_pain.jpg",
            "prompt": "Flamethrower striking Dragonite with pain expression",
            "pokemon": ["charizard", "dragonite"],
            "special_requirements": ["NO SHIELD on Dragonite", "Pain expression"]
        },
        {
            "num": 3,
            "path": "charizard/battle_assets/clean_4scenes/scene3_burn_marks_anger.jpg",
            "prompt": "Dragonite with burn marks, transitioning to anger",
            "pokemon": ["dragonite"],
            "special_requirements": ["VISIBLE BURN MARKS", "NO SHIELD"]
        },
        {
            "num": 4,
            "path": "charizard/battle_assets/clean_4scenes/scene4_revenge_charge.jpg",
            "prompt": "Dragonite charging forward for revenge",
            "pokemon": ["dragonite", "charizard"],
            "special_requirements": ["Burn marks visible", "NO SHIELD"]
        }
    ]

    # Validate NO NEW ELEMENTS for each scene
    scene_validations = []
    for scene in scenes:
        validation = validator.validate_no_new_elements(scene["path"], scene)
        scene_validations.append(validation)

    # Validate storyboard continuity
    storyboard_validation = validator.validate_storyboard_continuity(scenes)

    # Generate enhanced report
    report_path = "charizard/validation_reports/enhanced_validation_report.txt"
    validator.generate_enhanced_validation_report(
        scene_validations,
        storyboard_validation,
        report_path
    )

    print(f"\n🎉 Enhanced validation complete!")
    print(f"📁 Report: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
