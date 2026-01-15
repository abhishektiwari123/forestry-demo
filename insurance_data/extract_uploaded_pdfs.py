#!/usr/bin/env python3
"""
Extract screenshots from user-uploaded PDFs:
- GI Council Yearbook 2023-24
- IRDAI Annual Report 2023-24
- ICICI Lombard Annual Report 2024
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import os

# PDF configurations for uploaded files
PDF_CONFIGS = {
    'gi_council': {
        'path': '/home/user/forestry-demo/insurance_data/pdfs/gi_council.pdf.pdf',
        'name': 'GI Council Yearbook 2023-24',
        'pages': [1, 5, 10, 15, 20, 25, 30, 40, 50],  # Key pages
        'highlights': {
            1: [(5, 5, 95, 30, 'GI Council Yearbook Cover - Industry Overview', 'yellow')],
            5: [(5, 10, 95, 90, 'GDPI Overview - Rs 2,89,673 Crore', 'green')],
            10: [(5, 10, 95, 90, 'Segment-wise GDPI Breakdown', 'cyan')],
            15: [(5, 10, 95, 90, 'Health Insurance Statistics', 'magenta')],
            20: [(5, 10, 95, 90, 'Motor Insurance Statistics', 'yellow')],
            25: [(5, 10, 95, 90, 'Claims Ratio Analysis', 'green')],
            30: [(5, 10, 95, 90, 'Distribution Channel Mix', 'cyan')],
            40: [(5, 10, 95, 90, 'Insurance Penetration & Density', 'magenta')],
            50: [(5, 10, 95, 90, 'Industry Employment Data', 'yellow')]
        }
    },
    'irdai_ar': {
        'path': '/home/user/forestry-demo/insurance_data/pdfs/irdai_ar.pdf.pdf',
        'name': 'IRDAI Annual Report 2023-24',
        'pages': [1, 10, 20, 30, 40, 50, 60, 80, 100],  # Key regulatory pages
        'highlights': {
            1: [(5, 5, 95, 30, 'IRDAI Annual Report - Regulatory Overview', 'yellow')],
            10: [(5, 10, 95, 90, 'Insurance Industry Performance', 'green')],
            20: [(5, 10, 95, 90, 'Life Insurance Statistics', 'cyan')],
            30: [(5, 10, 95, 90, 'Non-Life Insurance Statistics', 'magenta')],
            40: [(5, 10, 95, 90, 'Health Insurance Overview', 'yellow')],
            50: [(5, 10, 95, 90, 'Insurance Penetration & Density', 'green')],
            60: [(5, 10, 95, 90, 'Regulatory Developments', 'cyan')],
            80: [(5, 10, 95, 90, 'Financial Inclusion Initiatives', 'magenta')],
            100: [(5, 10, 95, 90, 'Statistical Appendix', 'yellow')]
        }
    },
    'icici_lombard_ar': {
        'path': '/home/user/forestry-demo/insurance_data/pdfs/icici_lombard_ar.pdf.pdf',
        'name': 'ICICI Lombard Annual Report 2024',
        'pages': [1, 10, 20, 30, 50, 70, 90, 110, 130],  # Key company pages
        'highlights': {
            1: [(5, 5, 95, 30, 'ICICI Lombard AR - Company Overview', 'yellow')],
            10: [(5, 10, 95, 90, 'Chairman Message & Strategy', 'green')],
            20: [(5, 10, 95, 90, 'Financial Highlights FY24', 'cyan')],
            30: [(5, 10, 95, 90, 'Business Segment Performance', 'magenta')],
            50: [(5, 10, 95, 90, 'Health Insurance Business', 'yellow')],
            70: [(5, 10, 95, 90, 'Distribution Channel Analysis', 'green')],
            90: [(5, 10, 95, 90, 'Digital Transformation', 'cyan')],
            110: [(5, 10, 95, 90, 'Risk Management', 'magenta')],
            130: [(5, 10, 95, 90, 'Financial Statements', 'yellow')]
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
        return True, actual_page + 1, total_pages

    except Exception as e:
        print(f"  ✗ Error on page {page_num}: {e}")
        return False, 0, 0


def main():
    screenshots_dir = '/home/user/forestry-demo/insurance_data/screenshots'

    print("=" * 60)
    print("Extracting Screenshots from Uploaded PDFs")
    print("=" * 60)

    total_extracted = 0
    pdf_info = {}

    for pdf_key, config in PDF_CONFIGS.items():
        pdf_path = config['path']

        if not os.path.exists(pdf_path):
            print(f"\n⚠ Skipping {pdf_key}: File not found at {pdf_path}")
            continue

        print(f"\n📄 {config['name']}")
        print(f"   Path: {pdf_path}")
        print(f"   Size: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB")

        extracted_pages = []
        for page_num in config['pages']:
            output_file = f"{pdf_key}_page_{page_num}.png"
            output_path = os.path.join(screenshots_dir, output_file)

            highlights = config['highlights'].get(page_num, [])

            success, actual_page, total = extract_page_screenshot(
                pdf_path,
                page_num,
                output_path,
                highlights,
                config['name']
            )

            if success:
                total_extracted += 1
                extracted_pages.append(actual_page)

        pdf_info[pdf_key] = {
            'name': config['name'],
            'pages_extracted': extracted_pages,
            'total_pages': total
        }

    print("\n" + "=" * 60)
    print(f"Total screenshots extracted: {total_extracted}")
    print("=" * 60)

    # Summary
    print("\nPDF Summary:")
    for key, info in pdf_info.items():
        print(f"  {info['name']}: {len(info['pages_extracted'])} pages from {info['total_pages']} total")

    # List all screenshots
    print("\nAll screenshots in folder:")
    screenshots = sorted([f for f in os.listdir(screenshots_dir) if f.endswith('.png')])
    print(f"  Total: {len(screenshots)} screenshots")


if __name__ == "__main__":
    main()
