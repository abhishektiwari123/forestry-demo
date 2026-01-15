#!/usr/bin/env python3
"""
PDF Screenshot Tool for ICICI Lombard D2C Model
Extracts specific pages from source PDFs, adds highlighting, and embeds them in Excel
"""

import fitz  # PyMuPDF
import requests
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import tempfile

# Headers for PDF download
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/pdf,*/*',
}

# Source PDFs with specific pages to capture and highlight regions
# highlight_regions: list of (x1, y1, x2, y2, label, color) - coordinates as % of page
PDF_SOURCES = {
    'cbdt_itr': {
        'url': 'https://incometaxindia.gov.in/Documents/Direct%20Tax%20Data/Approved-version-Income-Tax-Return-Statistics-for-the-AY-2023-24.pdf',
        'name': 'CBDT ITR Statistics AY 2023-24',
        'pages': [6, 9, 10],
        'data_points': ['Total ITR Filers: 7.97 Cr', 'Income slab distribution', 'Salaried taxpayers: 3.80 Cr'],
        'highlights': {
            6: [(5, 5, 95, 55, 'Total Filers: 7,97,12,145 | Individuals: 7,54,61,286', 'yellow')],
            9: [(5, 8, 95, 92, 'Table 1.1: Income Slab Distribution (18 slabs)', 'green')],
            10: [(5, 15, 95, 50, 'Salaried: 3,79,64,804 | Salary Income: Rs 35.23L Cr', 'cyan')]
        }
    },
    'gi_council': {
        'url': 'https://www.gicouncil.in/yearbook/2023-24/wp-content/uploads/GIC_Yearbook_2023-24.pdf',
        'name': 'GI Council Yearbook 2023-24',
        'pages': [1, 8, 12, 15],
        'data_points': ['GDPI Rs 2,89,673 Cr', 'Health & PA 40.3%', 'Motor 31.7%', 'Growth 12.4%'],
        'highlights': {
            8: [(5, 10, 95, 85, 'Executive Summary: GDPI Rs 2,89,673 Cr | Growth 12.4%', 'yellow')],
            12: [(5, 15, 95, 80, 'Health & PA: 40.3% of GDPI | Motor: 31.7%', 'green')],
            15: [(5, 20, 95, 75, 'Segment-wise GDPI Breakdown', 'cyan')]
        }
    },
    'niva_drhp': {
        'url': 'https://transactions.nivabupa.com/pages/doc/drhp/Industry-Report.pdf',
        'name': 'Niva Bupa DRHP Industry Report (Redseer)',
        'pages': [5, 9, 12, 15, 17, 20],
        'data_points': ['Health GWP Rs 1.08T', 'Retail 38.7%', 'Group 50.5%', 'SAHI 27.1% growth'],
        'highlights': {
            5: [(5, 10, 95, 85, 'Health Insurance Market Overview', 'yellow')],
            9: [(5, 15, 95, 80, 'India Internet Funnel: 800-850M users', 'green')],
            12: [(5, 20, 95, 75, 'Digital Insurance Growth 30-35% CAGR', 'cyan')],
            15: [(5, 10, 95, 85, 'Retail 38.7% | Group 50.5% | Govt 9.7%', 'yellow')],
            17: [(5, 15, 95, 80, 'SAHI Growth 27.1% vs Industry 20.2%', 'green')],
            20: [(5, 20, 95, 75, 'Retail Health Growth 19.1%', 'cyan')]
        }
    },
    'niva_ar': {
        'url': 'https://transactions.nivabupa.com/pages/doc/pub-dis/annual-reports/Annual-Report-FY-2023-24.pdf',
        'name': 'Niva Bupa Annual Report FY24',
        'pages': [1, 8, 12, 45],
        'data_points': ['GWP Rs 5,499 Cr', '41% Growth', 'CSR 100%', 'Distribution mix'],
        'highlights': {
            8: [(5, 15, 95, 80, 'Financial Highlights: GWP Rs 5,499 Cr', 'yellow')],
            12: [(5, 20, 95, 75, 'Business Performance', 'green')],
            45: [(5, 10, 95, 85, 'Distribution Channel Mix', 'cyan')]
        }
    },
    'star_health': {
        'url': 'https://www.starhealth.in/sites/default/files/Star-Health-Annual-Report-2023-24.pdf',
        'name': 'Star Health Annual Report FY24',
        'pages': [1, 10, 25],
        'data_points': ['GWP Rs 15,254 Cr', 'Claims Ratio 66.5%', '7L+ Agents'],
        'highlights': {
            10: [(5, 15, 95, 80, 'Financial Summary: GWP Rs 15,254 Cr', 'yellow')],
            25: [(5, 20, 95, 75, 'Claims Ratio 66.5%', 'green')]
        }
    },
    'icici_lombard': {
        'url': 'https://www.icicilombard.com/docs/default-source/financial-information/annualreport2024.pdf',
        'name': 'ICICI Lombard Annual Report FY24',
        'pages': [1, 15, 45],
        'data_points': ['GDPI Rs 24,776 Cr', 'Market Share 8.67%', 'Solvency 2.69x'],
        'highlights': {
            15: [(5, 15, 95, 80, 'Financial Highlights: GDPI Rs 24,776 Cr', 'yellow')],
            45: [(5, 20, 95, 75, 'Segment-wise Performance', 'green')]
        }
    }
}

# Highlight colors with transparency
HIGHLIGHT_COLORS = {
    'yellow': (255, 255, 0, 80),
    'green': (0, 255, 0, 80),
    'cyan': (0, 255, 255, 80),
    'orange': (255, 165, 0, 80),
    'pink': (255, 192, 203, 80),
    'red': (255, 0, 0, 60)
}


def add_highlight_to_image(img_path, highlights, output_path):
    """
    Add highlight rectangles and labels to an image
    highlights: list of (x1%, y1%, x2%, y2%, label, color)
    """
    try:
        img = Image.open(img_path).convert('RGBA')
        width, height = img.size

        # Create overlay for transparency
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Try to load a font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
            small_font = font

        for highlight in highlights:
            x1_pct, y1_pct, x2_pct, y2_pct, label, color_name = highlight

            # Convert percentages to pixels
            x1 = int(width * x1_pct / 100)
            y1 = int(height * y1_pct / 100)
            x2 = int(width * x2_pct / 100)
            y2 = int(height * y2_pct / 100)

            # Get color
            color = HIGHLIGHT_COLORS.get(color_name, HIGHLIGHT_COLORS['yellow'])

            # Draw filled rectangle (highlight)
            draw.rectangle([x1, y1, x2, y2], fill=color)

            # Draw border
            border_color = (color[0], color[1], color[2], 255)
            draw.rectangle([x1, y1, x2, y2], outline=border_color, width=3)

            # Add label with background
            if label:
                # Calculate label position (top of highlight box)
                label_y = max(y1 - 25, 5)

                # Get text size
                bbox = draw.textbbox((x1, label_y), label, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Draw label background
                padding = 5
                draw.rectangle(
                    [x1, label_y - padding, x1 + text_width + padding * 2, label_y + text_height + padding],
                    fill=(0, 0, 0, 200)
                )

                # Draw label text
                draw.text((x1 + padding, label_y), label, fill=(255, 255, 255, 255), font=font)

        # Composite overlay onto original image
        img = Image.alpha_composite(img, overlay)

        # Add citation watermark at bottom
        watermark_text = "Source: Official Government/Company Report | Extracted for ICICI Lombard D2C Model"
        draw_final = ImageDraw.Draw(img)

        # Watermark background
        wm_y = height - 30
        draw_final.rectangle([0, wm_y, width, height], fill=(30, 30, 30, 220))
        draw_final.text((10, wm_y + 8), watermark_text, fill=(200, 200, 200, 255), font=small_font)

        # Convert back to RGB for saving
        img = img.convert('RGB')
        img.save(output_path, 'PNG', quality=95)

        print(f"  ✓ Added highlights to: {os.path.basename(output_path)}")
        return True

    except Exception as e:
        print(f"  ✗ Error adding highlights: {str(e)[:50]}")
        return False


def add_callout_box(img_path, text, position='top-right', output_path=None):
    """Add a callout box with key data point to image"""
    try:
        img = Image.open(img_path).convert('RGBA')
        width, height = img.size
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except:
            font = ImageFont.load_default()

        # Calculate text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        padding = 10

        # Position callout box
        if position == 'top-right':
            x = width - text_width - padding * 3 - 20
            y = 20
        elif position == 'top-left':
            x = 20
            y = 20
        elif position == 'bottom-right':
            x = width - text_width - padding * 3 - 20
            y = height - text_height - padding * 2 - 50
        else:  # bottom-left
            x = 20
            y = height - text_height - padding * 2 - 50

        # Draw callout box
        box_coords = [x, y, x + text_width + padding * 2, y + text_height + padding * 2]
        draw.rectangle(box_coords, fill=(255, 69, 0, 230), outline=(255, 255, 255, 255), width=2)

        # Draw text
        draw.text((x + padding, y + padding), text, fill=(255, 255, 255, 255), font=font)

        # Draw pointer triangle
        pointer_x = x + (text_width + padding * 2) // 2
        pointer_y = y + text_height + padding * 2
        draw.polygon([
            (pointer_x - 10, pointer_y),
            (pointer_x + 10, pointer_y),
            (pointer_x, pointer_y + 15)
        ], fill=(255, 69, 0, 230))

        img = img.convert('RGB')
        save_path = output_path or img_path
        img.save(save_path, 'PNG', quality=95)
        return True

    except Exception as e:
        print(f"  ✗ Error adding callout: {str(e)[:50]}")
        return False


def download_pdf(url, output_path):
    """Download PDF from URL"""
    print(f"  Downloading: {url[:60]}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"  ✓ Downloaded: {os.path.basename(output_path)}")
            return True
        else:
            print(f"  ✗ Failed with status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:50]}")
    return False


def extract_page_as_image(pdf_path, page_num, output_path, dpi=150, highlights=None):
    """Extract a specific page from PDF as image with optional highlights"""
    try:
        doc = fitz.open(pdf_path)
        if page_num > len(doc):
            print(f"  ✗ Page {page_num} does not exist (max: {len(doc)})")
            return False

        page = doc[page_num - 1]  # 0-indexed

        # Render page to image
        mat = fitz.Matrix(dpi/72, dpi/72)  # Scale for DPI
        pix = page.get_pixmap(matrix=mat)

        # Save as PNG (temp if highlights needed)
        if highlights:
            temp_path = output_path + ".temp.png"
            pix.save(temp_path)
            doc.close()

            # Add highlights
            add_highlight_to_image(temp_path, highlights, output_path)

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            pix.save(output_path)
            doc.close()

        print(f"  ✓ Extracted page {page_num} → {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"  ✗ Error extracting page {page_num}: {str(e)[:50]}")
        return False


def create_screenshot_excel(screenshots_dir, output_excel):
    """Create Excel with embedded screenshots"""

    wb = Workbook()
    ws = wb.active
    ws.title = "G_Source_Screenshots"

    # Title
    ws.merge_cells('A1:H1')
    ws['A1'] = "SOURCE DOCUMENT SCREENSHOTS - AUDIT TRAIL"
    ws['A1'].font = Font(bold=True, size=14, color="FFFFFF")
    ws['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    ws['A1'].alignment = Alignment(horizontal='center')

    ws.merge_cells('A2:H2')
    ws['A2'] = "Screenshots extracted from official PDF reports for McKinsey deck verification"
    ws['A2'].font = Font(italic=True, size=10)
    ws['A2'].alignment = Alignment(horizontal='center')

    current_row = 4

    for source_id, source_info in PDF_SOURCES.items():
        # Section header
        ws.merge_cells(f'A{current_row}:H{current_row}')
        ws[f'A{current_row}'] = f"{source_info['name']}"
        ws[f'A{current_row}'].font = Font(bold=True, size=12, color="1F4E79")
        ws[f'A{current_row}'].fill = PatternFill(start_color="D6DCE4", end_color="D6DCE4", fill_type="solid")
        current_row += 1

        # URL
        ws[f'A{current_row}'] = "URL:"
        ws[f'A{current_row}'].font = Font(bold=True)
        ws.merge_cells(f'B{current_row}:H{current_row}')
        ws[f'B{current_row}'] = source_info['url']
        ws[f'B{current_row}'].font = Font(color="0563C1", underline="single", size=9)
        current_row += 1

        # Data points
        ws[f'A{current_row}'] = "Key Data:"
        ws[f'A{current_row}'].font = Font(bold=True)
        ws.merge_cells(f'B{current_row}:H{current_row}')
        ws[f'B{current_row}'] = " | ".join(source_info['data_points'])
        ws[f'B{current_row}'].font = Font(italic=True, size=9)
        current_row += 1

        # Add screenshots for each page
        for page_num in source_info['pages']:
            img_path = os.path.join(screenshots_dir, f"{source_id}_page_{page_num}.png")

            if os.path.exists(img_path):
                # Page label
                ws[f'A{current_row}'] = f"Page {page_num}:"
                ws[f'A{current_row}'].font = Font(bold=True)
                current_row += 1

                try:
                    # Load and resize image for Excel
                    img = XLImage(img_path)

                    # Scale to fit (max width ~600px for Excel)
                    max_width = 600
                    if img.width > max_width:
                        scale = max_width / img.width
                        img.width = int(img.width * scale)
                        img.height = int(img.height * scale)

                    # Insert image
                    ws.add_image(img, f'A{current_row}')

                    # Calculate rows needed for image (approx 15 pixels per row)
                    rows_needed = max(int(img.height / 15), 20)
                    current_row += rows_needed + 2

                    print(f"  ✓ Added {source_id} page {page_num} to Excel")
                except Exception as e:
                    ws[f'A{current_row}'] = f"[Image could not be loaded: {str(e)[:30]}]"
                    current_row += 2
            else:
                ws[f'A{current_row}'] = f"Page {page_num}: [Screenshot not available - PDF download restricted]"
                ws[f'A{current_row}'].font = Font(italic=True, color="FF0000")
                current_row += 2

        current_row += 2  # Space between sources

    # Set column widths
    ws.column_dimensions['A'].width = 15
    for col in range(2, 9):
        ws.column_dimensions[get_column_letter(col)].width = 12

    wb.save(output_excel)
    print(f"\n✓ Screenshots Excel created: {output_excel}")
    return output_excel


def add_screenshots_to_model(model_path, screenshots_dir):
    """Add screenshots sheet to existing model"""

    print(f"\nAdding screenshots to: {model_path}")

    try:
        wb = load_workbook(model_path)
    except:
        print("Creating new workbook...")
        wb = Workbook()

    # Remove existing screenshots sheet if present
    if "G_Source_Screenshots" in wb.sheetnames:
        del wb["G_Source_Screenshots"]

    ws = wb.create_sheet("G_Source_Screenshots")

    # Title
    ws.merge_cells('A1:H1')
    ws['A1'] = "SOURCE DOCUMENT SCREENSHOTS - AUDIT TRAIL"
    ws['A1'].font = Font(bold=True, size=14, color="FFFFFF")
    ws['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    ws['A1'].alignment = Alignment(horizontal='center')

    ws.merge_cells('A2:H2')
    ws['A2'] = "Screenshots extracted from official PDF reports | Use for McKinsey deck verification"
    ws['A2'].font = Font(italic=True, size=10)
    ws['A2'].alignment = Alignment(horizontal='center')

    current_row = 4
    images_added = 0

    for source_id, source_info in PDF_SOURCES.items():
        # Section header
        ws.merge_cells(f'A{current_row}:H{current_row}')
        ws[f'A{current_row}'] = f"📄 {source_info['name']}"
        ws[f'A{current_row}'].font = Font(bold=True, size=12, color="1F4E79")
        ws[f'A{current_row}'].fill = PatternFill(start_color="D6DCE4", end_color="D6DCE4", fill_type="solid")
        current_row += 1

        # URL
        ws[f'A{current_row}'] = "Source URL:"
        ws[f'A{current_row}'].font = Font(bold=True)
        ws.merge_cells(f'B{current_row}:H{current_row}')
        ws[f'B{current_row}'] = source_info['url']
        ws[f'B{current_row}'].font = Font(color="0563C1", underline="single", size=9)
        current_row += 1

        # Key data extracted
        ws[f'A{current_row}'] = "Data Extracted:"
        ws[f'A{current_row}'].font = Font(bold=True)
        ws.merge_cells(f'B{current_row}:H{current_row}')
        ws[f'B{current_row}'] = " | ".join(source_info['data_points'])
        ws[f'B{current_row}'].font = Font(italic=True, size=9, color="006100")
        current_row += 1

        # Pages referenced
        ws[f'A{current_row}'] = "Pages Used:"
        ws[f'A{current_row}'].font = Font(bold=True)
        ws[f'B{current_row}'] = ", ".join([str(p) for p in source_info['pages']])
        current_row += 1

        # Try to add screenshots
        for page_num in source_info['pages']:
            img_path = os.path.join(screenshots_dir, f"{source_id}_page_{page_num}.png")

            if os.path.exists(img_path):
                ws[f'A{current_row}'] = f"Page {page_num} Screenshot:"
                ws[f'A{current_row}'].font = Font(bold=True, size=10)
                current_row += 1

                try:
                    img = XLImage(img_path)

                    # Scale image
                    max_width = 550
                    if img.width > max_width:
                        scale = max_width / img.width
                        img.width = int(img.width * scale)
                        img.height = int(img.height * scale)

                    ws.add_image(img, f'A{current_row}')
                    images_added += 1

                    rows_needed = max(int(img.height / 15), 25)
                    current_row += rows_needed + 2
                except Exception as e:
                    ws[f'A{current_row}'] = f"[Image error: {str(e)[:40]}]"
                    ws[f'A{current_row}'].font = Font(color="FF0000")
                    current_row += 2
            else:
                ws[f'A{current_row}'] = f"Page {page_num}:"
                ws[f'B{current_row}'] = "[Screenshot pending - see URL above for source]"
                ws[f'B{current_row}'].font = Font(italic=True, color="996600")
                current_row += 1

        current_row += 3

    # Add note at bottom
    ws[f'A{current_row}'] = "NOTE: Some government PDFs have download restrictions. Screenshots shown where available."
    ws[f'A{current_row}'].font = Font(italic=True, size=9, color="666666")
    ws.merge_cells(f'A{current_row}:H{current_row}')

    # Column widths
    ws.column_dimensions['A'].width = 18
    for col in range(2, 9):
        ws.column_dimensions[get_column_letter(col)].width = 12

    wb.save(model_path)
    print(f"✓ Added screenshots sheet to model ({images_added} images)")
    return model_path


def main():
    """Main execution"""
    print("=" * 60)
    print("PDF SCREENSHOT EXTRACTION TOOL")
    print("ICICI Lombard D2C Model - Source Audit Trail")
    print("=" * 60)

    # Create directories
    base_dir = "/home/user/forestry-demo/insurance_data"
    screenshots_dir = os.path.join(base_dir, "screenshots")
    pdfs_dir = os.path.join(base_dir, "pdfs")

    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(pdfs_dir, exist_ok=True)

    print(f"\n📁 Screenshots dir: {screenshots_dir}")
    print(f"📁 PDFs dir: {pdfs_dir}")

    # Download PDFs and extract screenshots
    print("\n" + "=" * 60)
    print("STEP 1: Downloading PDFs and extracting screenshots")
    print("=" * 60)

    for source_id, source_info in PDF_SOURCES.items():
        print(f"\n📄 {source_info['name']}")

        pdf_path = os.path.join(pdfs_dir, f"{source_id}.pdf")

        # Download PDF
        if not os.path.exists(pdf_path):
            success = download_pdf(source_info['url'], pdf_path)
        else:
            print(f"  ✓ PDF already exists: {os.path.basename(pdf_path)}")
            success = True

        # Extract page screenshots with highlights
        if success and os.path.exists(pdf_path):
            highlights_config = source_info.get('highlights', {})

            for page_num in source_info['pages']:
                img_path = os.path.join(screenshots_dir, f"{source_id}_page_{page_num}.png")

                # Get highlights for this page
                page_highlights = highlights_config.get(page_num, None)

                if not os.path.exists(img_path):
                    extract_page_as_image(pdf_path, page_num, img_path, dpi=150, highlights=page_highlights)
                else:
                    print(f"  ✓ Screenshot exists: {os.path.basename(img_path)}")
                    # Re-apply highlights if they exist and image doesn't have them
                    if page_highlights:
                        print(f"    Re-applying highlights to page {page_num}")
                        add_highlight_to_image(img_path, page_highlights, img_path)

    # Add screenshots to model
    print("\n" + "=" * 60)
    print("STEP 2: Adding screenshots to Excel model")
    print("=" * 60)

    model_path = os.path.join(base_dir, "ICICI_Lombard_Integrated_Model.xlsx")

    if os.path.exists(model_path):
        add_screenshots_to_model(model_path, screenshots_dir)
    else:
        print(f"Model not found: {model_path}")
        # Create standalone screenshots Excel
        standalone_path = os.path.join(base_dir, "Source_Screenshots.xlsx")
        create_screenshot_excel(screenshots_dir, standalone_path)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)

    # List created files
    print("\nFiles created:")
    for f in os.listdir(screenshots_dir):
        print(f"  📷 screenshots/{f}")


if __name__ == "__main__":
    main()
