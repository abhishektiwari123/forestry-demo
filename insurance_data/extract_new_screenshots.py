#!/usr/bin/env python3
"""
Extract screenshots from newly downloaded PDFs:
- ICICI Lombard NSE Filing
- Star Health Annual Report
- Star Health Investor Presentation
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import os

# PDF configurations
PDF_CONFIGS = {
    'icici_lombard_nse': {
        'path': '/home/user/forestry-demo/insurance_data/pdfs/icici_lombard_nse.pdf',
        'name': 'ICICI Lombard NSE Filing 2024',
        'pages': [1, 5, 10, 15, 20, 30],  # Key financial pages
        'highlights': {
            1: [(5, 5, 95, 30, 'ICICI Lombard Annual Report Cover', 'yellow')],
            5: [(5, 10, 95, 90, 'Financial Highlights & Key Metrics', 'green')],
            10: [(5, 10, 95, 90, 'Business Segment Performance', 'cyan')],
            15: [(5, 10, 95, 90, 'Health Insurance Business', 'magenta')],
            20: [(5, 10, 95, 90, 'Distribution Channel Mix', 'yellow')],
            30: [(5, 10, 95, 90, 'Financial Statements', 'green')]
        }
    },
    'star_health_ar': {
        'path': '/home/user/forestry-demo/insurance_data/pdfs/star_health_ar.pdf',
        'name': 'Star Health Annual Report 2024',
        'pages': [1, 8, 15, 25, 40, 60],  # Key sections
        'highlights': {
            1: [(5, 5, 95, 30, 'Star Health - Market Leader in Retail Health', 'yellow')],
            8: [(5, 10, 95, 90, 'Financial Performance FY24', 'green')],
            15: [(5, 10, 95, 90, 'Business Highlights & Growth', 'cyan')],
            25: [(5, 10, 95, 90, 'Distribution Network & Agents', 'magenta')],
            40: [(5, 10, 95, 90, 'Claims Performance & Settlement', 'yellow')],
            60: [(5, 10, 95, 90, 'Operating Metrics & Ratios', 'green')]
        }
    },
    'star_health_investor': {
        'path': '/home/user/forestry-demo/insurance_data/pdfs/star_health_investor_pres.pdf',
        'name': 'Star Health Investor Presentation Oct 2024',
        'pages': [1, 3, 5, 8, 12, 15],  # Investor deck pages
        'highlights': {
            1: [(5, 5, 95, 30, 'Star Health Q2 FY25 Results', 'yellow')],
            3: [(5, 10, 95, 90, 'Key Performance Indicators', 'green')],
            5: [(5, 10, 95, 90, 'GWP Growth & Market Share', 'cyan')],
            8: [(5, 10, 95, 90, 'Retail Health Dominance', 'magenta')],
            12: [(5, 10, 95, 90, 'Claims Ratio & Expense Ratio', 'yellow')],
            15: [(5, 10, 95, 90, 'Agent Network & Distribution', 'green')]
        }
    }
}

HIGHLIGHT_COLORS = {
    'yellow': (255, 255, 0, 80),
    'green': (0, 255, 0, 80),
    'cyan': (0, 255, 255, 80),
    'magenta': (255, 0, 255, 80),
    'orange': (255, 165, 0, 80)
}

def extract_page_screenshot(pdf_path, page_num, output_path, highlights=None, source_name=""):
    """Extract a page from PDF and add highlights"""
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        # Adjust page number if exceeds total
        actual_page = min(page_num - 1, total_pages - 1)
        if actual_page < 0:
            actual_page = 0

        page = doc[actual_page]

        # Render at high resolution
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Add highlights if provided
        if highlights:
            overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)

            for h in highlights:
                x1_pct, y1_pct, x2_pct, y2_pct, label, color = h
                x1 = int(img.width * x1_pct / 100)
                y1 = int(img.height * y1_pct / 100)
                x2 = int(img.width * x2_pct / 100)
                y2 = int(img.height * y2_pct / 100)

                fill_color = HIGHLIGHT_COLORS.get(color, HIGHLIGHT_COLORS['yellow'])
                draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=(0, 0, 0, 200), width=2)

                # Add label
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
                except:
                    font = ImageFont.load_default()
                draw.text((x1 + 5, y1 + 5), label, fill=(0, 0, 0, 255), font=font)

            # Merge overlay
            img = img.convert('RGBA')
            img = Image.alpha_composite(img, overlay)
            img = img.convert('RGB')

        # Add source watermark
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()

        watermark = f"Source: {source_name} | Page {actual_page + 1}/{total_pages}"
        draw.rectangle([0, img.height - 25, img.width, img.height], fill=(50, 50, 50))
        draw.text((10, img.height - 22), watermark, fill=(255, 255, 255), font=font)

        img.save(output_path, 'PNG')
        doc.close()

        print(f"  ✓ Page {actual_page + 1}: {output_path}")
        return True

    except Exception as e:
        print(f"  ✗ Error on page {page_num}: {e}")
        return False


def main():
    screenshots_dir = '/home/user/forestry-demo/insurance_data/screenshots'

    print("=" * 60)
    print("Extracting Screenshots from New PDFs")
    print("=" * 60)

    total_extracted = 0

    for pdf_key, config in PDF_CONFIGS.items():
        pdf_path = config['path']

        if not os.path.exists(pdf_path):
            print(f"\n⚠ Skipping {pdf_key}: File not found")
            continue

        print(f"\n📄 {config['name']}")
        print(f"   Path: {pdf_path}")

        for page_num in config['pages']:
            output_file = f"{pdf_key}_page_{page_num}.png"
            output_path = os.path.join(screenshots_dir, output_file)

            highlights = config['highlights'].get(page_num, [])

            success = extract_page_screenshot(
                pdf_path,
                page_num,
                output_path,
                highlights,
                config['name']
            )

            if success:
                total_extracted += 1

    print("\n" + "=" * 60)
    print(f"Total screenshots extracted: {total_extracted}")
    print("=" * 60)

    # List all screenshots
    print("\nAll screenshots in folder:")
    for f in sorted(os.listdir(screenshots_dir)):
        if f.endswith('.png'):
            size = os.path.getsize(os.path.join(screenshots_dir, f))
            print(f"  - {f} ({size:,} bytes)")


if __name__ == "__main__":
    main()
