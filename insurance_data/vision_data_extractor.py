#!/usr/bin/env python3
"""
Vision Data Extractor - Uses Claude Opus 4.5 Vision to analyze screenshots
Extracts specific data points from each PDF screenshot and creates audit trail
"""

import anthropic
import base64
import json
import os
import time
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

# Initialize Anthropic client
client = anthropic.Anthropic()

# Screenshot configurations - what to look for in each
SCREENSHOT_CONFIGS = {
    # CBDT ITR Statistics
    'cbdt_itr_page_6.png': {
        'source': 'CBDT ITR Statistics AY 2023-24',
        'look_for': 'Total ITR filers count, Individual vs Non-Individual breakdown, Summary statistics'
    },
    'cbdt_itr_page_9.png': {
        'source': 'CBDT ITR Statistics AY 2023-24',
        'look_for': 'Income slab distribution table, taxpayers by income bracket (>5L, >10L, >50L, >1Cr)'
    },
    'cbdt_itr_page_10.png': {
        'source': 'CBDT ITR Statistics AY 2023-24',
        'look_for': 'Salaried vs Business income filers, Total salary income reported'
    },

    # Niva Bupa DRHP
    'niva_drhp_page_5.png': {
        'source': 'Niva Bupa DRHP - CRISIL Report',
        'look_for': 'Health insurance market size, CAGR growth rates, Industry overview numbers'
    },
    'niva_drhp_page_9.png': {
        'source': 'Niva Bupa DRHP - CRISIL Report',
        'look_for': 'Retail health insurance market size, Segment breakdown percentages'
    },
    'niva_drhp_page_12.png': {
        'source': 'Niva Bupa DRHP - CRISIL Report',
        'look_for': 'Market share data, Competitor analysis, Star Health share'
    },
    'niva_drhp_page_15.png': {
        'source': 'Niva Bupa DRHP - CRISIL Report',
        'look_for': 'Distribution channel mix, Digital channel growth, Mobile share'
    },
    'niva_drhp_page_17.png': {
        'source': 'Niva Bupa DRHP - CRISIL Report',
        'look_for': 'Claims ratio, Expense ratio, SAHI financial metrics'
    },
    'niva_drhp_page_20.png': {
        'source': 'Niva Bupa DRHP - CRISIL Report',
        'look_for': 'Claim settlement ratio, Cashless claims percentage'
    },

    # Niva Bupa AR
    'niva_ar_page_1.png': {
        'source': 'Niva Bupa Annual Report FY24',
        'look_for': 'Company GWP, Revenue highlights, Cover page metrics'
    },
    'niva_ar_page_8.png': {
        'source': 'Niva Bupa Annual Report FY24',
        'look_for': 'Growth rates, CAGR, Financial highlights'
    },
    'niva_ar_page_12.png': {
        'source': 'Niva Bupa Annual Report FY24',
        'look_for': 'Claims ratio, Expense ratio, Operating metrics'
    },
    'niva_ar_page_45.png': {
        'source': 'Niva Bupa Annual Report FY24',
        'look_for': 'Policy count, Average premium, Business metrics'
    },

    # ICICI Lombard NSE
    'icici_lombard_nse_page_1.png': {
        'source': 'ICICI Lombard NSE Filing 2024',
        'look_for': 'Company GWP, Total revenue, Cover highlights'
    },
    'icici_lombard_nse_page_5.png': {
        'source': 'ICICI Lombard NSE Filing 2024',
        'look_for': 'Market share, Combined ratio, Financial highlights'
    },
    'icici_lombard_nse_page_10.png': {
        'source': 'ICICI Lombard NSE Filing 2024',
        'look_for': 'Distribution channel mix, Broker vs Direct percentages'
    },
    'icici_lombard_nse_page_15.png': {
        'source': 'ICICI Lombard NSE Filing 2024',
        'look_for': 'Health insurance GWP, Segment performance, Retail health share'
    },
    'icici_lombard_nse_page_20.png': {
        'source': 'ICICI Lombard NSE Filing 2024',
        'look_for': 'Claims settlement ratio, Customer metrics'
    },
    'icici_lombard_nse_page_30.png': {
        'source': 'ICICI Lombard NSE Filing 2024',
        'look_for': 'Net profit, Financial statements, P&L data'
    },

    # Star Health AR
    'star_health_ar_page_1.png': {
        'source': 'Star Health Annual Report 2024',
        'look_for': 'Company GWP, Revenue, Cover page highlights'
    },
    'star_health_ar_page_8.png': {
        'source': 'Star Health Annual Report 2024',
        'look_for': 'Market share, Agent network size, Distribution highlights'
    },
    'star_health_ar_page_15.png': {
        'source': 'Star Health Annual Report 2024',
        'look_for': 'GWP growth rate, Growth metrics'
    },
    'star_health_ar_page_25.png': {
        'source': 'Star Health Annual Report 2024',
        'look_for': 'Cashless claims ratio, Claims performance'
    },
    'star_health_ar_page_40.png': {
        'source': 'Star Health Annual Report 2024',
        'look_for': 'Claims ratio, Expense ratio, Operating metrics'
    },
    'star_health_ar_page_60.png': {
        'source': 'Star Health Annual Report 2024',
        'look_for': 'Net profit, Financial statements'
    },

    # Star Health Investor
    'star_health_investor_page_1.png': {
        'source': 'Star Health Investor Presentation Oct 2024',
        'look_for': 'Quarter identification, Latest results header'
    },
    'star_health_investor_page_3.png': {
        'source': 'Star Health Investor Presentation Oct 2024',
        'look_for': 'H1 FY25 GWP, ROE, Key performance indicators'
    },
    'star_health_investor_page_5.png': {
        'source': 'Star Health Investor Presentation Oct 2024',
        'look_for': 'GWP growth rate, Growth metrics'
    },
    'star_health_investor_page_8.png': {
        'source': 'Star Health Investor Presentation Oct 2024',
        'look_for': 'Market share percentage, Market position'
    },
    'star_health_investor_page_12.png': {
        'source': 'Star Health Investor Presentation Oct 2024',
        'look_for': 'Claims ratio, Operating performance'
    },
    'star_health_investor_page_15.png': {
        'source': 'Star Health Investor Presentation Oct 2024',
        'look_for': 'Agent count, Distribution network'
    },

    # GI Council Yearbook
    'gi_council_page_1.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'Report title, Year, Publication details'
    },
    'gi_council_page_5.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'Total GDPI, Industry overview numbers'
    },
    'gi_council_page_10.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'Industry structure, Insurer categories, Company logos'
    },
    'gi_council_page_15.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'Reinsurer branches, Foreign reinsurance presence'
    },
    'gi_council_page_20.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'Motor insurance section, Segment data'
    },
    'gi_council_page_25.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'Growth charts, GDPI growth vs GDP growth, Industry trends'
    },
    'gi_council_page_30.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'State-wise distribution table, Insurance penetration by state'
    },
    'gi_council_page_40.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'GDPI segment split pie chart, Health %, Motor %, Property %'
    },
    'gi_council_page_50.png': {
        'source': 'GI Council Yearbook 2023-24',
        'look_for': 'Industry employment, Investment data'
    },

    # IRDAI AR
    'irdai_ar_page_1.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Report title, Regulatory body identification'
    },
    'irdai_ar_page_10.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Table of contents, Report structure'
    },
    'irdai_ar_page_20.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Life insurance section, Premium data'
    },
    'irdai_ar_page_30.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Total insurance premium, Policy count, Life/Non-Life/Health breakdown, Claims paid'
    },
    'irdai_ar_page_40.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Life insurance charts, Premium trends'
    },
    'irdai_ar_page_50.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Insurance penetration table, Office distribution by tier, Insurer office counts'
    },
    'irdai_ar_page_60.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Regulatory framework, Compliance section'
    },
    'irdai_ar_page_80.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Financial inclusion, Bima Sugam, Digital initiatives'
    },
    'irdai_ar_page_100.png': {
        'source': 'IRDAI Annual Report 2023-24',
        'look_for': 'Statistical appendix, Data tables'
    },

    # ICICI Lombard Full AR
    'icici_lombard_ar_page_1.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'Cover page, Annual report year'
    },
    'icici_lombard_ar_page_10.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'GDPI growth chart, Combined ratio chart, Policy issuance, Claims processed'
    },
    'icici_lombard_ar_page_20.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'Insurance penetration, Density, Industry context'
    },
    'icici_lombard_ar_page_30.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'Business segments, Segment performance'
    },
    'icici_lombard_ar_page_50.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'Health insurance business, TCFD disclosure'
    },
    'icici_lombard_ar_page_70.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'Crop insurance, PMFBY details, Government schemes'
    },
    'icici_lombard_ar_page_90.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'Digital transformation, Technology initiatives'
    },
    'icici_lombard_ar_page_110.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'Risk management, ERM framework'
    },
    'icici_lombard_ar_page_130.png': {
        'source': 'ICICI Lombard Annual Report 2024',
        'look_for': 'Financial statements, P&L, Balance sheet'
    }
}


def encode_image_to_base64(image_path):
    """Read image and encode to base64"""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def analyze_screenshot_with_vision(image_path, source_name, look_for):
    """Use Claude Vision to analyze screenshot and extract data points"""

    print(f"  Analyzing with Claude Vision...")

    # Encode image
    base64_image = encode_image_to_base64(image_path)

    # Determine media type
    if image_path.endswith('.png'):
        media_type = "image/png"
    else:
        media_type = "image/jpeg"

    # Create prompt for extraction
    extraction_prompt = f"""Analyze this screenshot from {source_name}.

Look specifically for: {look_for}

Extract ALL numerical data points you can see in this image. For each data point, provide:
1. The exact value (with units like Rs, %, Cr, Lakh, etc.)
2. What the metric/label is called
3. Any context about what this number represents

Format your response as JSON with this structure:
{{
    "page_description": "Brief description of what this page shows",
    "data_points": [
        {{
            "value": "exact value with units",
            "metric": "name of the metric",
            "context": "what this means and why it matters",
            "confidence": "high/medium/low"
        }}
    ],
    "tables_found": ["list any table names/titles visible"],
    "charts_found": ["list any chart titles visible"]
}}

Be thorough - extract every number, percentage, and statistic visible. If text is in Hindi, translate the labels to English."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": extraction_prompt
                        }
                    ]
                }
            ]
        )

        # Parse response
        response_text = response.content[0].text

        # Try to extract JSON from response
        try:
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Return raw response if JSON parsing fails
        return {
            "page_description": "Analysis completed",
            "data_points": [{"value": "See raw response", "metric": "Raw", "context": response_text, "confidence": "low"}],
            "raw_response": response_text
        }

    except Exception as e:
        print(f"    Error: {e}")
        return {
            "page_description": f"Error analyzing: {str(e)}",
            "data_points": [],
            "error": str(e)
        }


def process_all_screenshots(screenshots_dir, output_dir):
    """Process all screenshots and extract data"""

    results = {}
    total_data_points = 0

    print("=" * 70)
    print("VISION DATA EXTRACTION - Claude Opus 4.5")
    print("=" * 70)

    # Get list of screenshots
    screenshots = sorted([f for f in os.listdir(screenshots_dir) if f.endswith('.png')])

    print(f"\nFound {len(screenshots)} screenshots to analyze\n")

    for i, screenshot in enumerate(screenshots, 1):
        print(f"[{i}/{len(screenshots)}] {screenshot}")

        image_path = os.path.join(screenshots_dir, screenshot)

        # Get config for this screenshot
        config = SCREENSHOT_CONFIGS.get(screenshot, {
            'source': 'Unknown',
            'look_for': 'Any numerical data, statistics, percentages, financial figures'
        })

        # Analyze with vision
        result = analyze_screenshot_with_vision(
            image_path,
            config['source'],
            config['look_for']
        )

        results[screenshot] = {
            'source': config['source'],
            'look_for': config['look_for'],
            'extraction': result
        }

        # Count data points
        if 'data_points' in result:
            num_points = len(result['data_points'])
            total_data_points += num_points
            print(f"    ✓ Extracted {num_points} data points")

        # Rate limiting
        time.sleep(1)

    print(f"\n{'=' * 70}")
    print(f"EXTRACTION COMPLETE: {total_data_points} data points from {len(screenshots)} screenshots")
    print("=" * 70)

    return results


def create_excel_output(results, output_path):
    """Create Excel file with extracted data"""

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vision_Extracted_Data"

    # Styles
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    alt_fill = PatternFill(start_color="E8F4FD", end_color="E8F4FD", fill_type="solid")
    border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # Headers
    headers = ['Screenshot', 'Source', 'Value', 'Metric', 'Context/Why', 'Confidence']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = Alignment(horizontal='center', wrap_text=True)

    # Column widths
    widths = [30, 35, 25, 30, 60, 12]
    for col, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = w

    # Data rows
    row = 2
    for screenshot, data in results.items():
        extraction = data.get('extraction', {})
        data_points = extraction.get('data_points', [])

        if not data_points:
            # Add row even if no data points
            ws.cell(row=row, column=1, value=screenshot).border = border
            ws.cell(row=row, column=2, value=data['source']).border = border
            ws.cell(row=row, column=3, value="No data extracted").border = border
            row += 1
            continue

        first_row = True
        for dp in data_points:
            ws.cell(row=row, column=1, value=screenshot if first_row else "").border = border
            ws.cell(row=row, column=2, value=data['source'] if first_row else "").border = border
            ws.cell(row=row, column=3, value=dp.get('value', '')).border = border
            ws.cell(row=row, column=4, value=dp.get('metric', '')).border = border
            ws.cell(row=row, column=5, value=dp.get('context', '')).border = border
            ws.cell(row=row, column=5).alignment = Alignment(wrap_text=True)
            ws.cell(row=row, column=6, value=dp.get('confidence', '')).border = border

            if row % 2 == 0:
                for c in range(1, 7):
                    ws.cell(row=row, column=c).fill = alt_fill

            first_row = False
            row += 1

    ws.row_dimensions[1].height = 30
    wb.save(output_path)
    print(f"✓ Excel saved: {output_path}")


def save_json_output(results, output_path):
    """Save results as JSON"""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ JSON saved: {output_path}")


def main():
    """Main function"""
    screenshots_dir = '/home/user/forestry-demo/insurance_data/screenshots'
    output_dir = '/home/user/forestry-demo/insurance_data'

    # Check if API key is available
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key'")
        return

    # Process all screenshots
    results = process_all_screenshots(screenshots_dir, output_dir)

    # Save outputs
    excel_path = os.path.join(output_dir, 'Vision_Extracted_Data.xlsx')
    json_path = os.path.join(output_dir, 'vision_extracted_data.json')

    create_excel_output(results, excel_path)
    save_json_output(results, json_path)

    print(f"\n✓ Extraction complete!")
    print(f"  - Excel: {excel_path}")
    print(f"  - JSON: {json_path}")


if __name__ == "__main__":
    main()
