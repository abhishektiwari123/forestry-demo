#!/usr/bin/env python3
"""
Validate all existing generated images and videos against the validation framework.

This script will:
1. Load each generated image
2. Display it for manual validation
3. Prompt for validation scores
4. Generate validation report
5. Identify which content needs regeneration
"""

import os
import sys
from pathlib import Path
import json

def create_validation_checklist():
    """Return the validation checklist structure."""
    return {
        "critical": {
            "size_accuracy": {
                "question": "Is Dragonite noticeably 30% larger and bulkier than Charizard?",
                "weight": "CRITICAL"
            },
            "wing_color_charizard": {
                "question": "Charizard wings: Are teal/turquoise undersides visible?",
                "weight": "CRITICAL"
            },
            "wing_color_dragonite": {
                "question": "Dragonite wings: Are teal/turquoise membranes visible?",
                "weight": "CRITICAL"
            },
            "character_recognition": {
                "question": "Are both Pokemon clearly recognizable (not generic dragons)?",
                "weight": "CRITICAL"
            }
        },
        "important": {
            "charizard_body_color": "Charizard: Vibrant orange body?",
            "charizard_belly": "Charizard: Cream/tan belly visible?",
            "charizard_tail_flame": "Charizard: Flaming tail visible?",
            "charizard_build": "Charizard: Lean, athletic build?",
            "dragonite_body_color": "Dragonite: Light orange/tan body?",
            "dragonite_belly": "Dragonite: Cream belly visible (stripes if angle allows)?",
            "dragonite_antennae": "Dragonite: Two antennae on head visible (if angle allows)?",
            "dragonite_build": "Dragonite: Bulky, muscular, stocky build?",
            "dragonite_no_tail_flame": "Dragonite: NO tail flame (correct)?",
            "visibility": "Scene is clear and visible (not too dark)?",
            "composition": "Good cinematic composition?"
        }
    }

def print_validation_prompt(segment_name, image_path):
    """Print validation prompts for an image."""
    print(f"\n{'='*70}")
    print(f"VALIDATING: {segment_name}")
    print(f"File: {image_path}")
    print(f"{'='*70}")
    print("\nPlease examine the image and answer the following questions:")
    print("(Answer: y/n/na for yes/no/not-applicable)")

def validate_image_interactive(segment_name, image_path):
    """Interactively validate an image."""
    checklist = create_validation_checklist()
    results = {"critical": {}, "important": {}}

    print_validation_prompt(segment_name, image_path)

    # Critical validation
    print(f"\n🔴 CRITICAL VALIDATION (MUST PASS ALL):")
    for key, item in checklist["critical"].items():
        while True:
            answer = input(f"  {item['question']} (y/n/na): ").strip().lower()
            if answer in ['y', 'n', 'na']:
                results["critical"][key] = answer
                break
            print("    Please answer y, n, or na")

    # Important validation
    print(f"\n🟡 IMPORTANT VALIDATION (Should pass 80%+):")
    for key, question in checklist["important"].items():
        while True:
            answer = input(f"  {question} (y/n/na): ").strip().lower()
            if answer in ['y', 'n', 'na']:
                results["important"][key] = answer
                break
            print("    Please answer y, n, or na")

    # Calculate score
    critical_passed = sum(1 for v in results["critical"].values() if v == 'y')
    critical_total = len([v for v in results["critical"].values() if v != 'na'])

    important_passed = sum(1 for v in results["important"].values() if v == 'y')
    important_total = len([v for v in results["important"].values() if v != 'na'])

    critical_pass_rate = (critical_passed / critical_total * 100) if critical_total > 0 else 0
    important_pass_rate = (important_passed / important_total * 100) if important_total > 0 else 0

    # Determine verdict
    if critical_pass_rate == 100:
        if important_pass_rate >= 80:
            verdict = "PASS"
        elif important_pass_rate >= 60:
            verdict = "CONDITIONAL"
        else:
            verdict = "FAIL"
    else:
        verdict = "FAIL"

    print(f"\n{'='*70}")
    print(f"VALIDATION RESULTS:")
    print(f"  Critical: {critical_passed}/{critical_total} ({critical_pass_rate:.0f}%)")
    print(f"  Important: {important_passed}/{important_total} ({important_pass_rate:.0f}%)")
    print(f"  VERDICT: {verdict}")
    print(f"{'='*70}")

    # Notes
    notes = input("\nNotes (optional, press Enter to skip): ").strip()

    return {
        "segment": segment_name,
        "file": image_path,
        "critical_score": f"{critical_passed}/{critical_total}",
        "important_score": f"{important_passed}/{important_total}",
        "verdict": verdict,
        "notes": notes,
        "details": results
    }

def save_validation_report(validations, output_file):
    """Save validation results to file."""
    with open(output_file, 'w') as f:
        f.write("# Validation Report\n\n")
        f.write(f"Total Images Validated: {len(validations)}\n\n")

        # Summary
        pass_count = sum(1 for v in validations if v['verdict'] == 'PASS')
        conditional_count = sum(1 for v in validations if v['verdict'] == 'CONDITIONAL')
        fail_count = sum(1 for v in validations if v['verdict'] == 'FAIL')

        f.write("## Summary\n\n")
        f.write(f"- ✅ PASS: {pass_count}\n")
        f.write(f"- ⚠️ CONDITIONAL: {conditional_count}\n")
        f.write(f"- ❌ FAIL: {fail_count}\n\n")

        # Detailed results
        f.write("## Detailed Results\n\n")
        for v in validations:
            f.write(f"### {v['segment']}\n")
            f.write(f"- File: `{v['file']}`\n")
            f.write(f"- Critical: {v['critical_score']}\n")
            f.write(f"- Important: {v['important_score']}\n")
            f.write(f"- **Verdict: {v['verdict']}**\n")
            if v['notes']:
                f.write(f"- Notes: {v['notes']}\n")
            f.write("\n")

        # Regeneration needed
        f.write("## Regeneration Needed\n\n")
        need_regen = [v for v in validations if v['verdict'] == 'FAIL']
        if need_regen:
            for v in need_regen:
                f.write(f"- {v['segment']}: {v['file']}\n")
        else:
            f.write("None! All images passed or conditional.\n")

    print(f"\n✅ Validation report saved to: {output_file}")

def main():
    print("="*70)
    print("EXISTING CONTENT VALIDATION")
    print("="*70)
    print("\nThis script will validate key existing images against the framework.")
    print("You'll need to view each image and answer validation questions.")
    print("\nPress Ctrl+C at any time to stop and save progress.\n")

    # Define images to validate (most important ones)
    images_to_validate = [
        # Test results
        ("Test: Nano Banana Pro", "charizard/battle_assets/test_results/nanobanana_photorealistic.jpg"),
        ("Test: Flux 2 Pro", "charizard/battle_assets/test_results/flux2_clean_v3.jpg"),

        # Continuous frames (corrected versions)
        ("Seg01 Continuous Start", "charizard/battle_assets/frame_pairs/seg01_continuous_start.jpg"),
        ("Seg02 Continuous Start", "charizard/battle_assets/frame_pairs/seg02_continuous_start.jpg"),
        ("Seg03 Continuous Start", "charizard/battle_assets/frame_pairs/seg03_continuous_start.jpg"),

        # Size-corrected versions
        ("Seg06 Size Corrected Start", "charizard/battle_assets/frame_pairs/seg06_size_corrected_start.jpg"),
        ("Seg12 Size Corrected Start", "charizard/battle_assets/frame_pairs/seg12_size_corrected_start.jpg"),
        ("Seg13 Size Corrected Start", "charizard/battle_assets/frame_pairs/seg13_size_corrected_start.jpg"),
    ]

    validations = []

    try:
        for segment_name, image_path in images_to_validate:
            if not os.path.exists(image_path):
                print(f"\n⚠️  Skipping {segment_name}: File not found")
                continue

            print(f"\n📸 Please open and view: {image_path}")
            input("Press Enter when ready to validate...")

            result = validate_image_interactive(segment_name, image_path)
            validations.append(result)

            # Ask if want to continue
            cont = input("\nContinue to next image? (y/n): ").strip().lower()
            if cont != 'y':
                break

    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")

    # Save report
    if validations:
        output_file = "charizard/VALIDATION_REPORT.md"
        save_validation_report(validations, output_file)

        # Also save JSON for processing
        json_file = "charizard/validation_results.json"
        with open(json_file, 'w') as f:
            json.dump(validations, f, indent=2)
        print(f"✅ JSON results saved to: {json_file}")
    else:
        print("\n⚠️  No validations completed")

if __name__ == "__main__":
    main()
