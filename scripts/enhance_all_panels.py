#!/usr/bin/env python3
"""
Enhance All Extracted Panels to Photorealistic Quality

Batch process all panels through Nano Banana Pro for:
- Photorealistic CGI quality
- Dynamic facial expressions
- 8K detail rendering
- Professional animation quality
"""

import os
import sys
import subprocess
import time


def main():
    """Enhance all extracted panels."""
    import argparse

    parser = argparse.ArgumentParser(description='Enhance all extracted panels to photorealistic quality')
    parser.add_argument('extracted_dir', help='Directory containing extracted panels')
    parser.add_argument('--panels', type=int, default=6, help='Number of panels to enhance (default: 6)')
    parser.add_argument('--delay', type=int, default=2, help='Delay between enhancements in seconds (default: 2)')

    args = parser.parse_args()

    print("""
╔════════════════════════════════════════════════════════════════════╗
║        BATCH PANEL ENHANCEMENT (Nano Banana Pro)                   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Enhancing all panels to photorealistic quality with:             ║
║  ✓ 8K CGI rendering                                               ║
║  ✓ Dynamic facial expressions                                     ║
║  ✓ Professional animation quality                                 ║
║  ✓ Maximum detail and sharpness                                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    if not os.path.exists(args.extracted_dir):
        print(f"❌ Directory not found: {args.extracted_dir}")
        return 1

    # Find all panel files
    panel_files = []
    for i in range(1, args.panels + 1):
        panel_file = os.path.join(args.extracted_dir, f"panel_{i:02d}_clean.jpg")
        if os.path.exists(panel_file):
            panel_files.append((i, panel_file))
        else:
            print(f"⚠️  Panel {i:02d} not found: {panel_file}")

    if not panel_files:
        print(f"❌ No panel files found in {args.extracted_dir}")
        return 1

    print(f"📊 Found {len(panel_files)} panels to enhance\n")

    enhanced_count = 0
    failed_panels = []

    for panel_num, panel_file in panel_files:
        print(f"\n{'='*70}")
        print(f"🎨 ENHANCING PANEL {panel_num}/{args.panels}")
        print(f"{'='*70}")

        try:
            result = subprocess.run([
                'python3', 'scripts/enhance_panel_with_nanobananapro.py',
                panel_file,
                '--panel-number', str(panel_num)
            ], check=True)

            enhanced_count += 1
            print(f"✅ Panel {panel_num} enhanced successfully")

            # Delay before next panel
            if panel_num < len(panel_files):
                print(f"\n⏸️  Waiting {args.delay} seconds before next panel...")
                time.sleep(args.delay)

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to enhance Panel {panel_num}: {e}")
            failed_panels.append(panel_num)
            continue

    print(f"\n{'='*70}")
    print(f"🎉 BATCH ENHANCEMENT COMPLETE!")
    print(f"{'='*70}")
    print(f"✅ Successfully enhanced: {enhanced_count}/{len(panel_files)} panels")

    if failed_panels:
        print(f"❌ Failed panels: {', '.join(map(str, failed_panels))}")

    enhanced_dir = args.extracted_dir.replace('_extracted', '_enhanced')
    print(f"\n📁 Enhanced panels location:")
    print(f"   {enhanced_dir}")

    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Review enhanced panels for quality")
    print(f"   2. Generate videos from enhanced panels:")
    print(f"      python3 scripts/test_video_from_panel.py [enhanced_panel] --duration 5")

    return 0 if not failed_panels else 1


if __name__ == "__main__":
    sys.exit(main())
