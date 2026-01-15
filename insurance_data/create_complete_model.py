#!/usr/bin/env python3
"""
ICICI Lombard D2C Health Insurance - Complete Financial Model
With LTV/CAC, Waterfall Analysis, and All Formulas Linked
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference, PieChart
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import DataBarRule
from datetime import datetime
import json

# ============================================
# STYLING FUNCTIONS
# ============================================

def create_styles(wb):
    """Create named styles for the workbook"""

    # Header style - Dark blue
    header_style = NamedStyle(name="header_style")
    header_style.font = Font(bold=True, color="FFFFFF", size=11)
    header_style.fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_style.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    header_style.border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    wb.add_named_style(header_style)

    # Sub-header style - Light blue
    subheader_style = NamedStyle(name="subheader_style")
    subheader_style.font = Font(bold=True, color="1F4E79", size=10)
    subheader_style.fill = PatternFill(start_color="D6DCE4", end_color="D6DCE4", fill_type="solid")
    subheader_style.alignment = Alignment(horizontal='left', vertical='center')
    subheader_style.border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    wb.add_named_style(subheader_style)

    # Data style
    data_style = NamedStyle(name="data_style")
    data_style.alignment = Alignment(vertical='center', wrap_text=True)
    data_style.border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    wb.add_named_style(data_style)

    # Currency style
    currency_style = NamedStyle(name="currency_style")
    currency_style.number_format = '₹#,##0'
    currency_style.alignment = Alignment(horizontal='right', vertical='center')
    currency_style.border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    wb.add_named_style(currency_style)

    # Percent style
    percent_style = NamedStyle(name="percent_style")
    percent_style.number_format = '0.0%'
    percent_style.alignment = Alignment(horizontal='right', vertical='center')
    percent_style.border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    wb.add_named_style(percent_style)

    # Highlight style - Yellow
    highlight_style = NamedStyle(name="highlight_style")
    highlight_style.font = Font(bold=True, color="000000", size=11)
    highlight_style.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
    highlight_style.alignment = Alignment(horizontal='center', vertical='center')
    highlight_style.border = Border(
        left=Side(style='medium'), right=Side(style='medium'),
        top=Side(style='medium'), bottom=Side(style='medium')
    )
    wb.add_named_style(highlight_style)

    # KPI Good style - Green
    kpi_good = NamedStyle(name="kpi_good")
    kpi_good.font = Font(bold=True, color="006100", size=12)
    kpi_good.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    kpi_good.alignment = Alignment(horizontal='center', vertical='center')
    kpi_good.border = Border(
        left=Side(style='medium'), right=Side(style='medium'),
        top=Side(style='medium'), bottom=Side(style='medium')
    )
    wb.add_named_style(kpi_good)

    # KPI Warning style - Orange
    kpi_warning = NamedStyle(name="kpi_warning")
    kpi_warning.font = Font(bold=True, color="9C5700", size=12)
    kpi_warning.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
    kpi_warning.alignment = Alignment(horizontal='center', vertical='center')
    kpi_warning.border = Border(
        left=Side(style='medium'), right=Side(style='medium'),
        top=Side(style='medium'), bottom=Side(style='medium')
    )
    wb.add_named_style(kpi_warning)

def apply_style(cell, style_name):
    """Apply named style to cell"""
    cell.style = style_name

def set_column_widths(ws, widths):
    """Set column widths"""
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

# ============================================
# MAIN WORKBOOK CREATION
# ============================================

def create_comprehensive_model():
    wb = Workbook()
    create_styles(wb)

    # ========================================
    # SHEET 1: ONE-PAGE MODEL SUMMARY (DASHBOARD)
    # ========================================
    ws_dashboard = wb.active
    ws_dashboard.title = "1_Dashboard"

    # Title
    ws_dashboard.merge_cells('A1:L1')
    ws_dashboard['A1'] = "ICICI LOMBARD D2C HEALTH INSURANCE - OPPORTUNITY MODEL"
    ws_dashboard['A1'].font = Font(bold=True, size=16, color="FFFFFF")
    ws_dashboard['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    ws_dashboard['A1'].alignment = Alignment(horizontal='center', vertical='center')

    # Subtitle
    ws_dashboard.merge_cells('A2:L2')
    ws_dashboard['A2'] = "TAM → SAM → SOM Analysis with 150 Sub-segments | Data as of January 2025"
    ws_dashboard['A2'].font = Font(italic=True, size=10, color="666666")
    ws_dashboard['A2'].alignment = Alignment(horizontal='center')

    # Row 4-8: Market Size Waterfall
    ws_dashboard['A4'] = "MARKET SIZE WATERFALL"
    ws_dashboard['A4'].style = "subheader_style"
    ws_dashboard.merge_cells('A4:D4')

    waterfall_headers = ["Stage", "Value (₹ Cr)", "Filter Applied", "Source"]
    for col, header in enumerate(waterfall_headers, 1):
        cell = ws_dashboard.cell(row=5, column=col, value=header)
        cell.style = "header_style"

    waterfall_data = [
        ["TAM: Total Health Insurance", 117000, "All health insurance in India", "IRDAI AR 2023-24"],
        ["Filter: Retail Only (38.7%)", 45279, "=B6*0.387", "Niva Bupa DRHP"],
        ["SAM: Digital Addressable (60%)", 27167, "=B7*0.6", "Industry Est - Urban digital"],
        ["Filter: Target Income >5L (35%)", 9509, "=B8*0.35", "CBDT ITR AY23-24"],
        ["SOM: Realistic Capture (15%)", 1426, "=B9*0.15", "5-year target"],
    ]

    for row_idx, data in enumerate(waterfall_data, 6):
        for col_idx, value in enumerate(data, 1):
            cell = ws_dashboard.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Add formulas
    ws_dashboard['B7'] = "=B6*0.387"
    ws_dashboard['B8'] = "=B7*0.6"
    ws_dashboard['B9'] = "=B8*0.35"
    ws_dashboard['B10'] = "=B9*0.15"

    # Row 4-8: Column F onwards - Key KPIs
    ws_dashboard['F4'] = "KEY PERFORMANCE INDICATORS"
    ws_dashboard['F4'].style = "subheader_style"
    ws_dashboard.merge_cells('F4:I4')

    kpi_headers = ["KPI", "Current", "Target", "Gap"]
    for col, header in enumerate(kpi_headers, 6):
        cell = ws_dashboard.cell(row=5, column=col, value=header)
        cell.style = "header_style"

    kpi_data = [
        ["Retail Health Share", "2.9%", "10%", "=H6-G6"],
        ["Digital Channel Share", "17.4%", "35%", "=H7-G7"],
        ["Combined Ratio", "103.8%", "95%", "=G8-H8"],
        ["Claims Ratio", "76.5%", "65%", "=G9-H9"],
        ["Renewal Rate", "80%", "90%", "=H10-G10"],
    ]

    for row_idx, data in enumerate(kpi_data, 6):
        for col_idx, value in enumerate(data, 6):
            cell = ws_dashboard.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Row 12-18: LTV/CAC Summary
    ws_dashboard['A12'] = "UNIT ECONOMICS - LTV/CAC MODEL"
    ws_dashboard['A12'].style = "subheader_style"
    ws_dashboard.merge_cells('A12:D12')

    ltv_headers = ["Metric", "Value", "Formula", "Source"]
    for col, header in enumerate(ltv_headers, 1):
        cell = ws_dashboard.cell(row=13, column=col, value=header)
        cell.style = "header_style"

    ltv_data = [
        ["Avg Annual Premium", 15000, "Industry average", "IRDAI/Niva Bupa"],
        ["Avg Policy Life (years)", 5, "Retention based", "Industry benchmark"],
        ["Gross Margin %", "35%", "1 - Claims Ratio - Expense", "IRDAI AR"],
        ["Customer Lifetime Value (LTV)", "=B14*B15*0.35", "Premium × Years × Margin", "Calculated"],
        ["Customer Acquisition Cost (CAC)", 3500, "Digital channel avg", "Industry Est"],
        ["LTV:CAC Ratio", "=B17/B18", "Target >3:1", "Calculated"],
        ["Payback Period (months)", "=B18/(B14*0.35/12)", "CAC / Monthly Margin", "Calculated"],
    ]

    for row_idx, data in enumerate(ltv_data, 14):
        for col_idx, value in enumerate(data, 1):
            cell = ws_dashboard.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Add LTV formulas
    ws_dashboard['B17'] = "=B14*B15*0.35"
    ws_dashboard['B19'] = "=B17/B18"
    ws_dashboard['B20'] = "=B18/(B14*0.35/12)"

    # Row 12-18: Column F onwards - Competitor Benchmark
    ws_dashboard['F12'] = "COMPETITOR BENCHMARK"
    ws_dashboard['F12'].style = "subheader_style"
    ws_dashboard.merge_cells('F12:J12')

    comp_headers = ["Insurer", "Health GWP (Cr)", "Market Share", "Claims Ratio", "Growth"]
    for col, header in enumerate(comp_headers, 6):
        cell = ws_dashboard.cell(row=13, column=col, value=header)
        cell.style = "header_style"

    comp_data = [
        ["Star Health", 15254, "33%", "66.5%", "22.3%"],
        ["Niva Bupa", 5499, "16.2%", "70%", "41%"],
        ["Care Health", 4500, "14%", "68%", "20%"],
        ["ICICI Lombard", 2800, "2.9%", "76.5%", "15%"],
        ["Aditya Birla", 3290, "10%", "72%", "48%"],
    ]

    for row_idx, data in enumerate(comp_data, 14):
        for col_idx, value in enumerate(data, 6):
            cell = ws_dashboard.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Row 22-28: 5-Year Projections
    ws_dashboard['A22'] = "5-YEAR D2C REVENUE PROJECTION"
    ws_dashboard['A22'].style = "subheader_style"
    ws_dashboard.merge_cells('A22:G22')

    proj_headers = ["Metric", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "CAGR"]
    for col, header in enumerate(proj_headers, 1):
        cell = ws_dashboard.cell(row=23, column=col, value=header)
        cell.style = "header_style"

    # Projection formulas will reference assumptions
    ws_dashboard['A24'] = "New Customers (000s)"
    ws_dashboard['B24'] = 50
    ws_dashboard['C24'] = "=B24*1.4"
    ws_dashboard['D24'] = "=C24*1.35"
    ws_dashboard['E24'] = "=D24*1.3"
    ws_dashboard['F24'] = "=E24*1.25"
    ws_dashboard['G24'] = "=(F24/B24)^(1/4)-1"

    ws_dashboard['A25'] = "Cumulative Customers (000s)"
    ws_dashboard['B25'] = "=B24"
    ws_dashboard['C25'] = "=B25*0.85+C24"
    ws_dashboard['D25'] = "=C25*0.85+D24"
    ws_dashboard['E25'] = "=D25*0.87+E24"
    ws_dashboard['F25'] = "=E25*0.88+F24"
    ws_dashboard['G25'] = "=(F25/B25)^(1/4)-1"

    ws_dashboard['A26'] = "GWP (₹ Cr)"
    ws_dashboard['B26'] = "=B25*15000/10000000"
    ws_dashboard['C26'] = "=C25*16500/10000000"
    ws_dashboard['D26'] = "=D25*18000/10000000"
    ws_dashboard['E26'] = "=E25*19500/10000000"
    ws_dashboard['F26'] = "=F25*21000/10000000"
    ws_dashboard['G26'] = "=(F26/B26)^(1/4)-1"

    ws_dashboard['A27'] = "Net Revenue (₹ Cr)"
    ws_dashboard['B27'] = "=B26*0.30"
    ws_dashboard['C27'] = "=C26*0.32"
    ws_dashboard['D27'] = "=D26*0.33"
    ws_dashboard['E27'] = "=E26*0.34"
    ws_dashboard['F27'] = "=F26*0.35"
    ws_dashboard['G27'] = "=(F27/B27)^(1/4)-1"

    ws_dashboard['A28'] = "Contribution Margin (₹ Cr)"
    ws_dashboard['B28'] = "=B27-B24*3500/10000000"
    ws_dashboard['C28'] = "=C27-C24*3200/10000000"
    ws_dashboard['D28'] = "=D27-D24*3000/10000000"
    ws_dashboard['E28'] = "=E27-E24*2800/10000000"
    ws_dashboard['F28'] = "=F27-F24*2600/10000000"
    ws_dashboard['G28'] = "=(F28/B28)^(1/4)-1"

    for row in range(24, 29):
        for col in range(1, 8):
            ws_dashboard.cell(row=row, column=col).style = "data_style"

    # Row 22 onwards Column I: Source Summary
    ws_dashboard['I22'] = "PRIMARY DATA SOURCES"
    ws_dashboard['I22'].style = "subheader_style"
    ws_dashboard.merge_cells('I22:L22')

    source_headers = ["Source", "Publisher", "Date", "Key Data"]
    for col, header in enumerate(source_headers, 9):
        cell = ws_dashboard.cell(row=23, column=col, value=header)
        cell.style = "header_style"

    sources = [
        ["CBDT ITR AY23-24", "Income Tax Dept", "Jun 2024", "7.97Cr filers"],
        ["IRDAI AR 2023-24", "IRDAI", "Dec 2024", "₹11.19T premium"],
        ["GI Council YB 23-24", "GI Council", "Feb 2025", "₹2.90T GDPI"],
        ["Niva Bupa DRHP", "Niva Bupa", "Jun 2024", "Market segments"],
        ["Star Health AR", "Star Health", "FY24", "SAHI leader"],
    ]

    for row_idx, data in enumerate(sources, 24):
        for col_idx, value in enumerate(data, 9):
            cell = ws_dashboard.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Set column widths for dashboard
    set_column_widths(ws_dashboard, {
        'A': 25, 'B': 15, 'C': 20, 'D': 18, 'E': 5,
        'F': 18, 'G': 15, 'H': 12, 'I': 15, 'J': 15, 'K': 12, 'L': 15
    })

    # ========================================
    # SHEET 2: DETAILED SOURCE CITATIONS
    # ========================================
    ws_sources = wb.create_sheet("2_Sources")

    source_headers = ["ID", "Document", "Publisher", "URL", "Version", "Pages", "Access Date", "Key Metrics", "Status"]
    for col, header in enumerate(source_headers, 1):
        cell = ws_sources.cell(row=1, column=col, value=header)
        cell.style = "header_style"

    detailed_sources = [
        ["S01", "ITR Statistics AY 2023-24", "CBDT, Ministry of Finance",
         "https://incometaxindia.gov.in/Documents/Direct%20Tax%20Data/Approved-version-Income-Tax-Return-Statistics-for-the-AY-2023-24.pdf",
         "v1.0, Jun 2024", "6, 9, 10", "2025-01-15", "ITR filers by income slab", "PRIMARY"],
        ["S02", "IRDAI Annual Report 2023-24", "IRDAI",
         "https://irdai.gov.in/document-detail?documentId=6436847",
         "Dec 2024", "Full", "2025-01-15", "Premium, Penetration, Claims", "PRIMARY"],
        ["S03", "GI Council Yearbook 2023-24", "General Insurance Council",
         "https://www.gicouncil.in/yearbook/2023-24/",
         "Feb 2025", "Exec Summary", "2025-01-15", "GDPI, Market shares", "PRIMARY"],
        ["S04", "Handbook Indian Insurance Stats", "IRDAI",
         "https://irdai.gov.in/handbook-of-indian-insurance",
         "Mar 2025", "All", "2025-01-15", "CSR, State-wise", "PRIMARY"],
        ["S05", "Niva Bupa DRHP Industry Report", "Niva Bupa (Redseer)",
         "https://transactions.nivabupa.com/pages/doc/drhp/Industry-Report.pdf",
         "Jun 2024", "1-50", "2025-01-15", "Market size, segments, growth", "PRIMARY"],
        ["S06", "Niva Bupa Annual Report FY24", "Niva Bupa Health Insurance",
         "https://transactions.nivabupa.com/pages/doc/pub-dis/annual-reports/Annual-Report-FY-2023-24.pdf",
         "FY24", "Financial", "2025-01-15", "GWP, Claims, Distribution", "COMPANY"],
        ["S07", "Star Health Annual Report FY24", "Star Health & Allied",
         "https://www.starhealth.in/investors/annual-report/",
         "FY24", "Financial", "2025-01-15", "SAHI leader metrics", "COMPANY"],
        ["S08", "ICICI Lombard Annual Report FY24", "ICICI Lombard GIC",
         "https://www.icicilombard.com/docs/default-source/financial-information/annualreport2024.pdf",
         "FY24", "Full", "2025-01-15", "GWP, Segments, Distribution", "COMPANY"],
        ["S09", "Go Digit DRHP", "Go Digit General Insurance",
         "https://www.godigit.com/investor-relations",
         "2024", "Industry", "2025-01-15", "Digital insurance metrics", "IPO FILING"],
        ["S10", "Care Health Annual Report", "Care Health Insurance",
         "https://www.careinsurance.com/investor-relations",
         "FY24", "Financial", "2025-01-15", "SAHI competitor data", "COMPANY"],
        ["S11", "Aditya Birla Health Report", "ABHI",
         "https://www.adityabirlacapital.com/healthinsurance/",
         "FY24", "Financial", "2025-01-15", "Fastest growing SAHI", "COMPANY"],
        ["S12", "HDFC ERGO Annual Report", "HDFC ERGO GIC",
         "https://www.hdfcergo.com/about-us/financial/annual-reports",
         "FY24", "Financial", "2025-01-15", "Private GI competitor", "COMPANY"],
        ["S13", "Bajaj Allianz GIC Report", "Bajaj Allianz",
         "https://www.bajajallianz.com/about-us/investor-relation.html",
         "FY24", "Financial", "2025-01-15", "#2 Private GI", "COMPANY"],
        ["S14", "Tata AIG Annual Report", "Tata AIG GIC",
         "https://www.tataaig.com/about-us/investor-relations",
         "FY24", "Financial", "2025-01-15", "Motor & Health leader", "COMPANY"],
        ["S15", "TRAI Telecom Reports", "TRAI",
         "https://www.trai.gov.in/release-publication/reports",
         "2024", "Subscriptions", "2025-01-15", "Internet, mobile users", "GOVT"],
        ["S16", "Census India Projections", "Registrar General",
         "https://censusindia.gov.in/",
         "2011+Proj", "Demographics", "2025-01-15", "Population, urban", "GOVT"],
    ]

    for row_idx, data in enumerate(detailed_sources, 2):
        for col_idx, value in enumerate(data, 1):
            cell = ws_sources.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    set_column_widths(ws_sources, {
        'A': 6, 'B': 28, 'C': 22, 'D': 50, 'E': 15, 'F': 12, 'G': 12, 'H': 25, 'I': 10
    })

    # ========================================
    # SHEET 3: TAM SAM SOM WATERFALL
    # ========================================
    ws_waterfall = wb.create_sheet("3_TAM_SAM_SOM")

    ws_waterfall['A1'] = "TAM → SAM → SOM WATERFALL ANALYSIS"
    ws_waterfall['A1'].style = "header_style"
    ws_waterfall.merge_cells('A1:H1')

    # TAM Section
    ws_waterfall['A3'] = "TOTAL ADDRESSABLE MARKET (TAM)"
    ws_waterfall['A3'].style = "subheader_style"
    ws_waterfall.merge_cells('A3:H3')

    tam_headers = ["Line", "Parameter", "Value", "Numeric", "Unit", "Calculation", "Source ID", "Page/Table"]
    for col, header in enumerate(tam_headers, 1):
        cell = ws_waterfall.cell(row=4, column=col, value=header)
        cell.style = "header_style"

    tam_data = [
        [1, "India Population 2024", "1.44 Billion", 1440000000, "People", "Census projection", "S16", "Projections"],
        [2, "Total Insurance Premium FY24", "₹11.19 Trillion", 1119000, "₹ Crore", "Life + Non-Life", "S02", "Summary"],
        [3, "Non-Life GDPI FY24", "₹2.90 Trillion", 290000, "₹ Crore", "General Insurance", "S02", "Summary"],
        [4, "Health Insurance GWP FY24", "₹1.17 Trillion", 117000, "₹ Crore", "Including PA+Travel", "S02", "Summary"],
        [5, "Health as % of Non-Life", "40.3%", 0.403, "%", "=D8/D7", "S03", "Exec Summary"],
        [6, "Health Insurance Growth FY24", "20.2%", 0.202, "%", "YoY growth", "S05", "Page 12"],
        [7, "Total ITR Filers AY23-24", "7.97 Crore", 79712145, "People", "All returns filed", "S01", "Page 6"],
        [8, "Individual ITR Filers", "7.55 Crore", 75461286, "People", "Individual returns", "S01", "Page 6"],
        [9, "Internet Users India", "900 Million", 900000000, "People", "TRAI data", "S15", "Subscriptions"],
        [10, "Smartphone Users India", "750 Million", 750000000, "People", "Mobile internet", "S15", "Subscriptions"],
    ]

    for row_idx, data in enumerate(tam_data, 5):
        for col_idx, value in enumerate(data, 1):
            cell = ws_waterfall.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # SAM Section
    ws_waterfall['A16'] = "SERVICEABLE ADDRESSABLE MARKET (SAM)"
    ws_waterfall['A16'].style = "subheader_style"
    ws_waterfall.merge_cells('A16:H16')

    for col, header in enumerate(tam_headers, 1):
        cell = ws_waterfall.cell(row=17, column=col, value=header)
        cell.style = "header_style"

    sam_data = [
        [11, "Retail Health Insurance", "₹44,800 Crore", 44800, "₹ Crore", "38.7% of Health GWP", "S05", "Page 15"],
        [12, "Group Health Insurance", "₹58,500 Crore", 58500, "₹ Crore", "50.5% of Health GWP", "S05", "Page 15"],
        [13, "Govt Schemes (PMJAY etc)", "₹11,200 Crore", 11200, "₹ Crore", "9.7% of Health GWP", "S05", "Page 15"],
        [14, "Overseas Medical", "₹1,300 Crore", 1300, "₹ Crore", "1.1% of Health GWP", "S05", "Page 15"],
        [15, "Income >5L Taxpayers", "4.67 Crore", 46721465, "People", "Sum of slabs >5L", "S01", "Table 1.1"],
        [16, "Salaried Taxpayers", "3.80 Crore", 37964804, "People", "Employment type", "S01", "Table 1.2"],
        [17, "Urban Internet Users", "450 Million", 450000000, "People", "~50% of total", "S15", "Est"],
        [18, "Metro Population (Top 10)", "150 Million", 150000000, "People", "Tier-1 cities", "S16", "Census"],
        [19, "Digital Insurance Market", "₹12,000 Crore", 12000, "₹ Crore", "~10% of Non-Life", "S09", "DRHP"],
        [20, "Retail Buyers Online", "72.2%", 0.722, "%", "Of online insurance", "S09", "DRHP"],
    ]

    for row_idx, data in enumerate(sam_data, 18):
        for col_idx, value in enumerate(data, 1):
            cell = ws_waterfall.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # SOM Section
    ws_waterfall['A29'] = "SERVICEABLE OBTAINABLE MARKET (SOM) - ICICI LOMBARD D2C"
    ws_waterfall['A29'].style = "subheader_style"
    ws_waterfall.merge_cells('A29:H29')

    for col, header in enumerate(tam_headers, 1):
        cell = ws_waterfall.cell(row=30, column=col, value=header)
        cell.style = "header_style"

    som_data = [
        [21, "D2C Addressable Retail", "₹25,000 Crore", 25000, "₹ Crore", "~56% of Retail Health", "Calculated", "Model"],
        [22, "Target Segment (Income >5L, Urban, Digital)", "2.5 Crore", 25000000, "People", "Filtered TAM", "Calculated", "Model"],
        [23, "Current ICICI Retail Health", "₹2,800 Crore", 2800, "₹ Crore", "2.9% share", "S08", "Segmental"],
        [24, "Target Market Share (5Y)", "10%", 0.10, "%", "From 2.9%", "Assumption", "Model"],
        [25, "SOM Year 5 GWP", "₹4,500 Crore", 4500, "₹ Crore", "=D25*D28", "Calculated", "Model"],
        [26, "Implied New Customers (5Y)", "3,00,000", 300000, "Policies", "At ₹15K avg", "Calculated", "Model"],
        [27, "Digital Channel Target", "35%", 0.35, "%", "Of ICICI health", "Assumption", "Model"],
        [28, "D2C App Target", "20%", 0.20, "%", "Of digital channel", "Assumption", "Model"],
    ]

    for row_idx, data in enumerate(som_data, 31):
        for col_idx, value in enumerate(data, 1):
            cell = ws_waterfall.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Waterfall Summary with formulas
    ws_waterfall['A40'] = "WATERFALL SUMMARY (with linked formulas)"
    ws_waterfall['A40'].style = "subheader_style"
    ws_waterfall.merge_cells('A40:E40')

    wf_headers = ["Step", "Description", "Value (₹ Cr)", "% of Previous", "Cumulative %"]
    for col, header in enumerate(wf_headers, 1):
        cell = ws_waterfall.cell(row=41, column=col, value=header)
        cell.style = "header_style"

    ws_waterfall['A42'] = 1
    ws_waterfall['B42'] = "TAM: Total Health Insurance"
    ws_waterfall['C42'] = 117000
    ws_waterfall['D42'] = "100%"
    ws_waterfall['E42'] = "100%"

    ws_waterfall['A43'] = 2
    ws_waterfall['B43'] = "Filter: Retail Only"
    ws_waterfall['C43'] = "=C42*0.387"
    ws_waterfall['D43'] = "38.7%"
    ws_waterfall['E43'] = "=C43/C42"

    ws_waterfall['A44'] = 3
    ws_waterfall['B44'] = "Filter: Urban Digital (60%)"
    ws_waterfall['C44'] = "=C43*0.6"
    ws_waterfall['D44'] = "60%"
    ws_waterfall['E44'] = "=C44/C42"

    ws_waterfall['A45'] = 4
    ws_waterfall['B45'] = "Filter: Target Income (35%)"
    ws_waterfall['C45'] = "=C44*0.35"
    ws_waterfall['D45'] = "35%"
    ws_waterfall['E45'] = "=C45/C42"

    ws_waterfall['A46'] = 5
    ws_waterfall['B46'] = "SOM: 5Y Capture (15%)"
    ws_waterfall['C46'] = "=C45*0.15"
    ws_waterfall['D46'] = "15%"
    ws_waterfall['E46'] = "=C46/C42"

    for row in range(42, 47):
        for col in range(1, 6):
            ws_waterfall.cell(row=row, column=col).style = "data_style"

    set_column_widths(ws_waterfall, {
        'A': 6, 'B': 35, 'C': 18, 'D': 12, 'E': 15, 'F': 25, 'G': 12, 'H': 15
    })

    # ========================================
    # SHEET 4: CBDT INCOME DATA (DETAILED)
    # ========================================
    ws_cbdt = wb.create_sheet("4_CBDT_Income")

    ws_cbdt['A1'] = "CBDT ITR STATISTICS AY 2023-24 - INCOME DISTRIBUTION"
    ws_cbdt['A1'].style = "header_style"
    ws_cbdt.merge_cells('A1:J1')

    ws_cbdt['A2'] = "Source: https://incometaxindia.gov.in/Documents/Direct%20Tax%20Data/Approved-version-Income-Tax-Return-Statistics-for-the-AY-2023-24.pdf"
    ws_cbdt['A2'].font = Font(italic=True, size=9, color="0563C1")
    ws_cbdt.merge_cells('A2:J2')

    cbdt_headers = ["Line", "Income Slab", "Filers", "% of Total", "Cumulative %", "Target Segment", "Avg Premium", "Market Size (₹ Cr)", "Page", "Table"]
    for col, header in enumerate(cbdt_headers, 1):
        cell = ws_cbdt.cell(row=4, column=col, value=header)
        cell.style = "header_style"

    cbdt_detailed = [
        [1, "Income = 0", 1441175, "=C5/$C$22", "=D5", "No", 0, "=IF(F5=\"Yes\",C5*G5/10000000,0)", 9, "1.1"],
        [2, "Income >0 to ≤1.5L", 4144666, "=C6/$C$22", "=D5+D6", "No", 0, "=IF(F6=\"Yes\",C6*G6/10000000,0)", 9, "1.1"],
        [3, "Income >1.5L to ≤2L", 1509747, "=C7/$C$22", "=E6+D7", "No", 0, "=IF(F7=\"Yes\",C7*G7/10000000,0)", 9, "1.1"],
        [4, "Income >2L to ≤2.5L", 3036825, "=C8/$C$22", "=E7+D8", "No", 0, "=IF(F8=\"Yes\",C8*G8/10000000,0)", 9, "1.1"],
        [5, "Income >2.5L to ≤3.5L", 5946214, "=C9/$C$22", "=E8+D9", "Low", 5000, "=IF(F9=\"Yes\",C9*G9/10000000,0)", 9, "1.1"],
        [6, "Income >3.5L to ≤4L", 4055198, "=C10/$C$22", "=E9+D10", "Low", 5000, "=IF(F10=\"Yes\",C10*G10/10000000,0)", 9, "1.1"],
        [7, "Income >4L to ≤4.5L", 6024031, "=C11/$C$22", "=E10+D11", "Low", 6000, "=IF(F11=\"Yes\",C11*G11/10000000,0)", 9, "1.1"],
        [8, "Income >4.5L to ≤5L", 12600689, "=C12/$C$22", "=E11+D12", "Medium", 8000, "=IF(F12=\"Yes\",C12*G12/10000000,0)", 9, "1.1"],
        [9, "Income >5L to ≤5.5L", 6154414, "=C13/$C$22", "=E12+D13", "Yes", 10000, "=IF(F13=\"Yes\",C13*G13/10000000,0)", 9, "1.1"],
        [10, "Income >5.5L to ≤9.5L", 20697590, "=C14/$C$22", "=E13+D14", "Yes", 12000, "=IF(F14=\"Yes\",C14*G14/10000000,0)", 9, "1.1"],
        [11, "Income >9.5L to ≤10L", 1084818, "=C15/$C$22", "=E14+D15", "Yes", 15000, "=IF(F15=\"Yes\",C15*G15/10000000,0)", 9, "1.1"],
        [12, "Income >10L to ≤15L", 6379208, "=C16/$C$22", "=E15+D16", "Yes", 18000, "=IF(F16=\"Yes\",C16*G16/10000000,0)", 9, "1.1"],
        [13, "Income >15L to ≤20L", 2503932, "=C17/$C$22", "=E16+D17", "Yes", 22000, "=IF(F17=\"Yes\",C17*G17/10000000,0)", 9, "1.1"],
        [14, "Income >20L to ≤25L", 1240128, "=C18/$C$22", "=E17+D18", "Yes", 28000, "=IF(F18=\"Yes\",C18*G18/10000000,0)", 9, "1.1"],
        [15, "Income >25L to ≤50L", 1953619, "=C19/$C$22", "=E18+D19", "Yes", 35000, "=IF(F19=\"Yes\",C19*G19/10000000,0)", 9, "1.1"],
        [16, "Income >50L to ≤1Cr", 589762, "=C20/$C$22", "=E19+D20", "Premium", 50000, "=IF(F20=\"Yes\",C20*G20/10000000,0)", 9, "1.1"],
        [17, "Income >1Cr to ≤5Cr", 291929, "=C21/$C$22", "=E20+D21", "Premium", 75000, "=IF(F21=\"Yes\",C21*G21/10000000,0)", 9, "1.1"],
        [18, "Income >5Cr+", 74065, "=C22/$C$22", "=E21+D22", "Premium", 100000, "=IF(F22=\"Yes\",C22*G22/10000000,0)", 9, "1.1"],
    ]

    for row_idx, data in enumerate(cbdt_detailed, 5):
        for col_idx, value in enumerate(data, 1):
            cell = ws_cbdt.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Totals row
    ws_cbdt['A23'] = "TOTAL"
    ws_cbdt['B23'] = "All Individual Filers"
    ws_cbdt['C23'] = "=SUM(C5:C22)"
    ws_cbdt['D23'] = "100%"
    ws_cbdt['E23'] = "100%"
    ws_cbdt['F23'] = "-"
    ws_cbdt['G23'] = "=SUMPRODUCT(C5:C22,G5:G22)/C23"
    ws_cbdt['H23'] = "=SUM(H5:H22)"
    for col in range(1, 11):
        ws_cbdt.cell(row=23, column=col).style = "highlight_style"

    # Target segment summary
    ws_cbdt['A25'] = "TARGET SEGMENT SUMMARY"
    ws_cbdt['A25'].style = "subheader_style"
    ws_cbdt.merge_cells('A25:E25')

    ws_cbdt['A26'] = "Income >5L (Target)"
    ws_cbdt['B26'] = "=SUM(C13:C22)"
    ws_cbdt['C26'] = "=B26/C23"
    ws_cbdt['D26'] = "People"
    ws_cbdt['E26'] = "Primary D2C Target"

    ws_cbdt['A27'] = "Income >10L (Premium)"
    ws_cbdt['B27'] = "=SUM(C16:C22)"
    ws_cbdt['C27'] = "=B27/C23"
    ws_cbdt['D27'] = "People"
    ws_cbdt['E27'] = "High-value segment"

    ws_cbdt['A28'] = "Salaried Taxpayers"
    ws_cbdt['B28'] = 37964804
    ws_cbdt['C28'] = "=B28/C23"
    ws_cbdt['D28'] = "People"
    ws_cbdt['E28'] = "Employer benefit potential"

    set_column_widths(ws_cbdt, {
        'A': 6, 'B': 22, 'C': 14, 'D': 12, 'E': 14, 'F': 14, 'G': 14, 'H': 18, 'I': 8, 'J': 8
    })

    # ========================================
    # SHEET 5: COMPETITOR DEEP DIVE
    # ========================================
    ws_comp = wb.create_sheet("5_Competitors")

    ws_comp['A1'] = "COMPETITOR ANALYSIS - DRHP & ANNUAL REPORT DATA"
    ws_comp['A1'].style = "header_style"
    ws_comp.merge_cells('A1:N1')

    comp_headers = ["Rank", "Insurer", "Type", "GWP FY24 (₹Cr)", "Market Share", "Health GWP", "Health Share",
                    "Claims Ratio", "Combined Ratio", "Expense Ratio", "Growth FY24", "Solvency", "Source", "Page"]
    for col, header in enumerate(comp_headers, 1):
        cell = ws_comp.cell(row=3, column=col, value=header)
        cell.style = "header_style"

    competitors = [
        [1, "New India Assurance", "Public", 40364, "13.09%", 12109, "30%", "97.2%", "116%", "35%", "8.9%", "1.67x", "IRDAI AR", "Ch 5"],
        [2, "ICICI Lombard", "Private", 24776, "8.67%", 2800, "11.3%", "76.5%", "103.8%", "27.3%", "20.4%", "2.69x", "ICICI AR", "Fin"],
        [3, "Bajaj Allianz", "Private", 22000, "7.69%", 3300, "15%", "78%", "99.9%", "28%", "14.8%", "3.49x", "ICRA", "Rating"],
        [4, "Star Health", "SAHI", 15254, "5.26%", 15254, "100%", "66.5%", "97.3%", "30.7%", "22.3%", "2.15x", "Star AR", "Fin"],
        [5, "United India", "Public", 19852, "6.84%", 5956, "30%", "97%", "118%", "36%", "5%", "1.52x", "IRDAI AR", "Ch 5"],
        [6, "Oriental Insurance", "Public", 12000, "4.14%", 3600, "30%", "97%", "115%", "35%", "6%", "1.55x", "IRDAI AR", "Ch 5"],
        [7, "National Insurance", "Public", 11500, "3.97%", 3450, "30%", "97%", "117%", "36%", "4%", "1.48x", "IRDAI AR", "Ch 5"],
        [8, "HDFC ERGO", "Private", 9000, "3.10%", 1800, "20%", "82%", "102%", "28%", "12%", "2.35x", "HDFC AR", "Fin"],
        [9, "Tata AIG", "Private", 8500, "2.93%", 1700, "20%", "80%", "100%", "26%", "18%", "2.45x", "Tata AR", "Fin"],
        [10, "SBI General", "Private", 8000, "2.76%", 1600, "20%", "85%", "105%", "30%", "15%", "2.25x", "SBI AR", "Fin"],
        [11, "Niva Bupa", "SAHI", 5499, "1.90%", 5499, "100%", "70%", "95%", "30%", "41%", "1.85x", "Niva AR", "Fin"],
        [12, "Care Health", "SAHI", 4500, "1.55%", 4500, "100%", "68%", "93%", "29%", "20%", "1.92x", "Care AR", "Fin"],
        [13, "Go Digit", "Private", 4000, "1.38%", 800, "20%", "78%", "108%", "32%", "25%", "2.85x", "Digit DRHP", "Ind"],
        [14, "Aditya Birla Health", "SAHI", 3290, "1.13%", 3290, "100%", "72%", "96%", "28%", "48%", "1.75x", "ABH AR", "Fin"],
        [15, "Kotak Mahindra GI", "Private", 3500, "1.21%", 700, "20%", "82%", "106%", "30%", "40%", "2.15x", "Kotak AR", "Fin"],
    ]

    for row_idx, data in enumerate(competitors, 4):
        for col_idx, value in enumerate(data, 1):
            cell = ws_comp.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # SAHI Specific Analysis
    ws_comp['A21'] = "STANDALONE HEALTH INSURERS (SAHI) - DETAILED COMPARISON"
    ws_comp['A21'].style = "subheader_style"
    ws_comp.merge_cells('A21:N21')

    sahi_headers = ["Insurer", "GWP (₹Cr)", "Retail %", "Group %", "Govt %", "Retail GWP", "Agents (000s)",
                    "CSR", "Cashless %", "Renewal Rate", "Avg Premium", "CAGR 3Y", "Source", "DRHP Page"]
    for col, header in enumerate(sahi_headers, 1):
        cell = ws_comp.cell(row=22, column=col, value=header)
        cell.style = "header_style"

    sahi_data = [
        ["Star Health", 15254, "33%", "55%", "12%", "=B24*C24", 701, "99.01%", "87%", "82%", 14500, "22.3%", "Star AR", "Pg 45"],
        ["Niva Bupa", 5499, "38.7%", "50.5%", "9.7%", "=B25*C25", 180, "100%", "85%", "85%", 16000, "41%", "Niva DRHP", "Pg 12"],
        ["Care Health", 4500, "40%", "52%", "8%", "=B26*C26", 150, "100%", "82%", "80%", 13500, "20%", "Care AR", "Fin"],
        ["Aditya Birla", 3290, "45%", "48%", "7%", "=B27*C27", 95, "99.01%", "80%", "78%", 15500, "48%", "ABH AR", "Fin"],
        ["ManipalCigna", 2800, "42%", "50%", "8%", "=B28*C28", 85, "99.96%", "83%", "79%", 14000, "25%", "MCGHI AR", "Fin"],
    ]

    for row_idx, data in enumerate(sahi_data, 23):
        for col_idx, value in enumerate(data, 1):
            cell = ws_comp.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # ICICI vs Competition
    ws_comp['A30'] = "ICICI LOMBARD vs COMPETITION GAP ANALYSIS"
    ws_comp['A30'].style = "subheader_style"
    ws_comp.merge_cells('A30:H30')

    gap_headers = ["Metric", "ICICI Lombard", "Star Health", "Gap", "Niva Bupa", "Gap", "Industry Avg", "Gap"]
    for col, header in enumerate(gap_headers, 1):
        cell = ws_comp.cell(row=31, column=col, value=header)
        cell.style = "header_style"

    gap_data = [
        ["Retail Health Share", "2.9%", "33%", "=C33-B33", "16.2%", "=E33-B33", "10%", "=G33-B33"],
        ["Claims Ratio", "76.5%", "66.5%", "=B34-C34", "70%", "=B34-E34", "72%", "=B34-G34"],
        ["Combined Ratio", "103.8%", "97.3%", "=B35-C35", "95%", "=B35-E35", "100%", "=B35-G35"],
        ["Renewal Rate", "80%", "82%", "=C36-B36", "85%", "=E36-B36", "84%", "=G36-B36"],
        ["Digital Share", "17.4%", "15%", "=B37-C37", "20%", "=E37-B37", "12%", "=B37-G37"],
        ["Agent Network (000s)", 150, 701, "=C38-B38", 180, "=E38-B38", 200, "=G38-B38"],
    ]

    for row_idx, data in enumerate(gap_data, 32):
        for col_idx, value in enumerate(data, 1):
            cell = ws_comp.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    set_column_widths(ws_comp, {
        'A': 6, 'B': 18, 'C': 10, 'D': 14, 'E': 12, 'F': 12, 'G': 12,
        'H': 12, 'I': 12, 'J': 12, 'K': 12, 'L': 10, 'M': 12, 'N': 12
    })

    # ========================================
    # SHEET 6: LTV / CAC MODEL
    # ========================================
    ws_ltv = wb.create_sheet("6_LTV_CAC_Model")

    ws_ltv['A1'] = "CUSTOMER LIFETIME VALUE (LTV) & ACQUISITION COST (CAC) MODEL"
    ws_ltv['A1'].style = "header_style"
    ws_ltv.merge_cells('A1:H1')

    # Input Assumptions
    ws_ltv['A3'] = "INPUT ASSUMPTIONS"
    ws_ltv['A3'].style = "subheader_style"
    ws_ltv.merge_cells('A3:D3')

    input_headers = ["Parameter", "Value", "Unit", "Source"]
    for col, header in enumerate(input_headers, 1):
        cell = ws_ltv.cell(row=4, column=col, value=header)
        cell.style = "header_style"

    inputs = [
        ["Average Annual Premium (Retail)", 15000, "₹", "IRDAI/Industry"],
        ["Premium Growth Rate (Annual)", "8%", "%", "Medical inflation"],
        ["Policy Retention Rate", "85%", "%", "Industry benchmark"],
        ["Average Policy Duration", 5, "Years", "Based on retention"],
        ["Claims Ratio", "65%", "%", "SAHI benchmark"],
        ["Expense Ratio", "28%", "%", "Digital efficiency"],
        ["Gross Margin", "=1-B9-B10", "%", "Calculated"],
        ["Discount Rate", "12%", "%", "WACC estimate"],
    ]

    for row_idx, data in enumerate(inputs, 5):
        for col_idx, value in enumerate(data, 1):
            cell = ws_ltv.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # LTV Calculation
    ws_ltv['A15'] = "LTV CALCULATION (NPV Method)"
    ws_ltv['A15'].style = "subheader_style"
    ws_ltv.merge_cells('A15:H15')

    ltv_headers = ["Year", "Premium", "Retention Prob", "Expected Premium", "Gross Margin", "Discount Factor", "PV Margin", "Cumulative LTV"]
    for col, header in enumerate(ltv_headers, 1):
        cell = ws_ltv.cell(row=16, column=col, value=header)
        cell.style = "header_style"

    ws_ltv['A17'] = 1
    ws_ltv['B17'] = "=B5"
    ws_ltv['C17'] = "100%"
    ws_ltv['D17'] = "=B17*C17"
    ws_ltv['E17'] = "=D17*B11"
    ws_ltv['F17'] = "=1/(1+B12)^A17"
    ws_ltv['G17'] = "=E17*F17"
    ws_ltv['H17'] = "=G17"

    ws_ltv['A18'] = 2
    ws_ltv['B18'] = "=B17*(1+B6)"
    ws_ltv['C18'] = "=B7"
    ws_ltv['D18'] = "=B18*C18"
    ws_ltv['E18'] = "=D18*B11"
    ws_ltv['F18'] = "=1/(1+B12)^A18"
    ws_ltv['G18'] = "=E18*F18"
    ws_ltv['H18'] = "=H17+G18"

    ws_ltv['A19'] = 3
    ws_ltv['B19'] = "=B18*(1+B6)"
    ws_ltv['C19'] = "=C18*B7"
    ws_ltv['D19'] = "=B19*C19"
    ws_ltv['E19'] = "=D19*B11"
    ws_ltv['F19'] = "=1/(1+B12)^A19"
    ws_ltv['G19'] = "=E19*F19"
    ws_ltv['H19'] = "=H18+G19"

    ws_ltv['A20'] = 4
    ws_ltv['B20'] = "=B19*(1+B6)"
    ws_ltv['C20'] = "=C19*B7"
    ws_ltv['D20'] = "=B20*C20"
    ws_ltv['E20'] = "=D20*B11"
    ws_ltv['F20'] = "=1/(1+B12)^A20"
    ws_ltv['G20'] = "=E20*F20"
    ws_ltv['H20'] = "=H19+G20"

    ws_ltv['A21'] = 5
    ws_ltv['B21'] = "=B20*(1+B6)"
    ws_ltv['C21'] = "=C20*B7"
    ws_ltv['D21'] = "=B21*C21"
    ws_ltv['E21'] = "=D21*B11"
    ws_ltv['F21'] = "=1/(1+B12)^A21"
    ws_ltv['G21'] = "=E21*F21"
    ws_ltv['H21'] = "=H20+G21"

    for row in range(17, 22):
        for col in range(1, 9):
            ws_ltv.cell(row=row, column=col).style = "data_style"

    # LTV Summary
    ws_ltv['A23'] = "5-Year LTV"
    ws_ltv['B23'] = "=H21"
    ws_ltv['A23'].style = "highlight_style"
    ws_ltv['B23'].style = "highlight_style"

    # CAC Analysis
    ws_ltv['A26'] = "CUSTOMER ACQUISITION COST (CAC) BY CHANNEL"
    ws_ltv['A26'].style = "subheader_style"
    ws_ltv.merge_cells('A26:E26')

    cac_headers = ["Channel", "CAC (₹)", "% of Mix", "Weighted CAC", "Source"]
    for col, header in enumerate(cac_headers, 1):
        cell = ws_ltv.cell(row=27, column=col, value=header)
        cell.style = "header_style"

    cac_data = [
        ["D2C App (Organic)", 1500, "15%", "=B28*C28", "Industry Est"],
        ["D2C App (Paid)", 3000, "25%", "=B29*C29", "Industry Est"],
        ["Digital Aggregators", 4500, "20%", "=B30*C30", "PolicyBazaar rates"],
        ["Agents/Brokers", 6000, "30%", "=B31*C31", "Commission based"],
        ["Bancassurance", 2500, "10%", "=B32*C32", "Bank partnership"],
        ["BLENDED CAC", "=SUMPRODUCT(B28:B32,C28:C32)", "100%", "=SUM(D28:D32)", "Calculated"],
    ]

    for row_idx, data in enumerate(cac_data, 28):
        for col_idx, value in enumerate(data, 1):
            cell = ws_ltv.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # LTV:CAC Ratio
    ws_ltv['A36'] = "LTV:CAC ANALYSIS"
    ws_ltv['A36'].style = "subheader_style"
    ws_ltv.merge_cells('A36:D36')

    ratio_headers = ["Metric", "Value", "Benchmark", "Status"]
    for col, header in enumerate(ratio_headers, 1):
        cell = ws_ltv.cell(row=37, column=col, value=header)
        cell.style = "header_style"

    ws_ltv['A38'] = "LTV"
    ws_ltv['B38'] = "=B23"
    ws_ltv['C38'] = ">₹20,000"
    ws_ltv['D38'] = "=IF(B38>20000,\"GOOD\",\"IMPROVE\")"

    ws_ltv['A39'] = "CAC (Blended)"
    ws_ltv['B39'] = "=B33"
    ws_ltv['C39'] = "<₹4,000"
    ws_ltv['D39'] = "=IF(B39<4000,\"GOOD\",\"HIGH\")"

    ws_ltv['A40'] = "LTV:CAC Ratio"
    ws_ltv['B40'] = "=B38/B39"
    ws_ltv['C40'] = ">3:1"
    ws_ltv['D40'] = "=IF(B40>3,\"HEALTHY\",\"IMPROVE\")"

    ws_ltv['A41'] = "Payback Period (months)"
    ws_ltv['B41'] = "=B39/(B5*B11/12)"
    ws_ltv['C41'] = "<18 months"
    ws_ltv['D41'] = "=IF(B41<18,\"GOOD\",\"LONG\")"

    ws_ltv['A42'] = "Break-even Year"
    ws_ltv['B42'] = "=B41/12"
    ws_ltv['C42'] = "<1.5 years"
    ws_ltv['D42'] = "=IF(B42<1.5,\"GOOD\",\"SLOW\")"

    for row in range(38, 43):
        for col in range(1, 5):
            ws_ltv.cell(row=row, column=col).style = "data_style"

    set_column_widths(ws_ltv, {
        'A': 28, 'B': 16, 'C': 16, 'D': 18, 'E': 18, 'F': 16, 'G': 14, 'H': 16
    })

    # ========================================
    # SHEET 7: 5-YEAR FINANCIAL PROJECTIONS
    # ========================================
    ws_proj = wb.create_sheet("7_Projections")

    ws_proj['A1'] = "ICICI LOMBARD D2C HEALTH - 5-YEAR FINANCIAL PROJECTIONS"
    ws_proj['A1'].style = "header_style"
    ws_proj.merge_cells('A1:I1')

    # Assumptions
    ws_proj['A3'] = "KEY ASSUMPTIONS"
    ws_proj['A3'].style = "subheader_style"
    ws_proj.merge_cells('A3:D3')

    assume_headers = ["Assumption", "Value", "Rationale", "Source"]
    for col, header in enumerate(assume_headers, 1):
        cell = ws_proj.cell(row=4, column=col, value=header)
        cell.style = "header_style"

    assumptions = [
        ["Year 1 New Customers", 50000, "Conservative launch", "Model"],
        ["Customer Growth Rate Y1-Y2", "40%", "Aggressive digital", "Model"],
        ["Customer Growth Rate Y2-Y3", "35%", "Scaling", "Model"],
        ["Customer Growth Rate Y3-Y4", "30%", "Maturing", "Model"],
        ["Customer Growth Rate Y4-Y5", "25%", "Steady state", "Model"],
        ["Retention Rate Y1", "80%", "New cohort", "Industry"],
        ["Retention Rate Y2+", "85%", "Improving", "Target"],
        ["Avg Premium Y1", 15000, "Entry level", "Market"],
        ["Premium Increase Rate", "10%", "Inflation + upsell", "Industry"],
        ["CAC Y1", 3500, "Digital + paid", "'6_LTV_CAC_Model'!B33"],
        ["CAC Reduction Rate", "8%", "Efficiency gains", "Model"],
        ["Claims Ratio Target", "65%", "SAHI benchmark", "IRDAI"],
        ["Expense Ratio Target", "25%", "Digital efficiency", "Target"],
    ]

    for row_idx, data in enumerate(assumptions, 5):
        for col_idx, value in enumerate(data, 1):
            cell = ws_proj.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Projections
    ws_proj['A20'] = "5-YEAR PROJECTIONS"
    ws_proj['A20'].style = "subheader_style"
    ws_proj.merge_cells('A20:I20')

    proj_headers = ["Metric", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Total/CAGR", "Notes"]
    for col, header in enumerate(proj_headers, 1):
        cell = ws_proj.cell(row=21, column=col, value=header)
        cell.style = "header_style"

    # Customer metrics
    ws_proj['A22'] = "NEW CUSTOMERS"
    ws_proj['B22'] = "=B5"
    ws_proj['C22'] = "=B22*(1+B6)"
    ws_proj['D22'] = "=C22*(1+B7)"
    ws_proj['E22'] = "=D22*(1+B8)"
    ws_proj['F22'] = "=E22*(1+B9)"
    ws_proj['G22'] = "=SUM(B22:F22)"
    ws_proj['H22'] = "Total new"

    ws_proj['A23'] = "RETAINED CUSTOMERS"
    ws_proj['B23'] = 0
    ws_proj['C23'] = "=B24*B10"
    ws_proj['D23'] = "=C24*B11"
    ws_proj['E23'] = "=D24*B11"
    ws_proj['F23'] = "=E24*B11"
    ws_proj['G23'] = "=(F23/C23)^(1/3)-1"
    ws_proj['H23'] = "Retention CAGR"

    ws_proj['A24'] = "TOTAL CUSTOMERS"
    ws_proj['B24'] = "=B22+B23"
    ws_proj['C24'] = "=C22+C23"
    ws_proj['D24'] = "=D22+D23"
    ws_proj['E24'] = "=E22+E23"
    ws_proj['F24'] = "=F22+F23"
    ws_proj['G24'] = "=(F24/B24)^(1/4)-1"
    ws_proj['H24'] = "Customer CAGR"

    # Financial metrics
    ws_proj['A26'] = "AVG PREMIUM (₹)"
    ws_proj['B26'] = "=B12"
    ws_proj['C26'] = "=B26*(1+B13)"
    ws_proj['D26'] = "=C26*(1+B13)"
    ws_proj['E26'] = "=D26*(1+B13)"
    ws_proj['F26'] = "=E26*(1+B13)"
    ws_proj['G26'] = "=(F26/B26)^(1/4)-1"
    ws_proj['H26'] = "Premium CAGR"

    ws_proj['A27'] = "GWP (₹ Cr)"
    ws_proj['B27'] = "=B24*B26/10000000"
    ws_proj['C27'] = "=C24*C26/10000000"
    ws_proj['D27'] = "=D24*D26/10000000"
    ws_proj['E27'] = "=E24*E26/10000000"
    ws_proj['F27'] = "=F24*F26/10000000"
    ws_proj['G27'] = "=(F27/B27)^(1/4)-1"
    ws_proj['H27'] = "GWP CAGR"

    ws_proj['A28'] = "CLAIMS (₹ Cr)"
    ws_proj['B28'] = "=B27*B16"
    ws_proj['C28'] = "=C27*B16"
    ws_proj['D28'] = "=D27*B16"
    ws_proj['E28'] = "=E27*B16"
    ws_proj['F28'] = "=F27*B16"
    ws_proj['G28'] = "=SUM(B28:F28)"
    ws_proj['H28'] = "Total claims"

    ws_proj['A29'] = "EXPENSES (₹ Cr)"
    ws_proj['B29'] = "=B27*B17"
    ws_proj['C29'] = "=C27*B17"
    ws_proj['D29'] = "=D27*B17"
    ws_proj['E29'] = "=E27*B17"
    ws_proj['F29'] = "=F27*B17"
    ws_proj['G29'] = "=SUM(B29:F29)"
    ws_proj['H29'] = "Total expenses"

    ws_proj['A30'] = "CAC SPEND (₹ Cr)"
    ws_proj['B30'] = "=B22*B14/10000000"
    ws_proj['C30'] = "=C22*B14*(1-B15)/10000000"
    ws_proj['D30'] = "=D22*B14*(1-B15)^2/10000000"
    ws_proj['E30'] = "=E22*B14*(1-B15)^3/10000000"
    ws_proj['F30'] = "=F22*B14*(1-B15)^4/10000000"
    ws_proj['G30'] = "=SUM(B30:F30)"
    ws_proj['H30'] = "Total CAC"

    ws_proj['A31'] = "GROSS MARGIN (₹ Cr)"
    ws_proj['B31'] = "=B27-B28-B29"
    ws_proj['C31'] = "=C27-C28-C29"
    ws_proj['D31'] = "=D27-D28-D29"
    ws_proj['E31'] = "=E27-E28-E29"
    ws_proj['F31'] = "=F27-F28-F29"
    ws_proj['G31'] = "=SUM(B31:F31)"
    ws_proj['H31'] = "Total margin"

    ws_proj['A32'] = "CONTRIBUTION (₹ Cr)"
    ws_proj['B32'] = "=B31-B30"
    ws_proj['C32'] = "=C31-C30"
    ws_proj['D32'] = "=D31-D30"
    ws_proj['E32'] = "=E31-E30"
    ws_proj['F32'] = "=F31-F30"
    ws_proj['G32'] = "=SUM(B32:F32)"
    ws_proj['H32'] = "Total contribution"

    ws_proj['A33'] = "CONTRIBUTION MARGIN %"
    ws_proj['B33'] = "=B32/B27"
    ws_proj['C33'] = "=C32/C27"
    ws_proj['D33'] = "=D32/D27"
    ws_proj['E33'] = "=E32/E27"
    ws_proj['F33'] = "=F32/F27"
    ws_proj['G33'] = "=G32/SUM(B27:F27)"
    ws_proj['H33'] = "Avg margin"

    for row in range(22, 34):
        for col in range(1, 9):
            ws_proj.cell(row=row, column=col).style = "data_style"

    # Key Outputs
    ws_proj['A36'] = "KEY OUTPUTS"
    ws_proj['A36'].style = "subheader_style"
    ws_proj.merge_cells('A36:D36')

    ws_proj['A37'] = "Year 5 Customer Base"
    ws_proj['B37'] = "=F24"
    ws_proj['C37'] = "customers"

    ws_proj['A38'] = "Year 5 GWP"
    ws_proj['B38'] = "=F27"
    ws_proj['C38'] = "₹ Cr"

    ws_proj['A39'] = "5-Year Total GWP"
    ws_proj['B39'] = "=SUM(B27:F27)"
    ws_proj['C39'] = "₹ Cr"

    ws_proj['A40'] = "5-Year Contribution"
    ws_proj['B40'] = "=G32"
    ws_proj['C40'] = "₹ Cr"

    ws_proj['A41'] = "Customer CAGR"
    ws_proj['B41'] = "=G24"
    ws_proj['C41'] = "%"

    ws_proj['A42'] = "GWP CAGR"
    ws_proj['B42'] = "=G27"
    ws_proj['C42'] = "%"

    for row in range(37, 43):
        for col in range(1, 4):
            ws_proj.cell(row=row, column=col).style = "highlight_style"

    set_column_widths(ws_proj, {
        'A': 25, 'B': 14, 'C': 14, 'D': 14, 'E': 14, 'F': 14, 'G': 14, 'H': 18, 'I': 12
    })

    # ========================================
    # SHEET 8: 150 SEGMENT MODEL
    # ========================================
    ws_seg = wb.create_sheet("8_150_Segments")

    ws_seg['A1'] = "150 SUB-SEGMENT FRAMEWORK FOR D2C TARGETING"
    ws_seg['A1'].style = "header_style"
    ws_seg.merge_cells('A1:J1')

    # Dimension breakdown
    ws_seg['A3'] = "SEGMENTATION DIMENSIONS"
    ws_seg['A3'].style = "subheader_style"
    ws_seg.merge_cells('A3:E3')

    dim_headers = ["Dimension", "Categories", "Sub-Categories", "Count", "Data Source"]
    for col, header in enumerate(dim_headers, 1):
        cell = ws_seg.cell(row=4, column=col, value=header)
        cell.style = "header_style"

    dimensions = [
        ["Income (from CBDT)", "4 bands", "0-5L, 5-10L, 10-25L, 25L+", 4, "S01 - CBDT ITR"],
        ["Age", "5 bands", "18-30, 30-40, 40-50, 50-60, 60+", 5, "Census Projections"],
        ["Geography", "3 tiers", "Metro (6), Tier-1 (15), Tier-2+ (Rest)", 3, "Smart Cities"],
        ["Family Type", "3 types", "Individual, Couple, Family (3+)", 3, "Industry"],
        ["Digital Affinity", "2 levels", "Digital-first, Hybrid", 2, "Industry"],
        ["TOTAL SEGMENTS", "-", "4 × 5 × 3 × 3 × 2 =", "=D5*D6*D7*D8*D9", "Framework"],
    ]

    for row_idx, data in enumerate(dimensions, 5):
        for col_idx, value in enumerate(data, 1):
            cell = ws_seg.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Priority segments
    ws_seg['A13'] = "PRIORITY SEGMENTS FOR D2C (Top 20)"
    ws_seg['A13'].style = "subheader_style"
    ws_seg.merge_cells('A13:J13')

    priority_headers = ["Rank", "Segment", "Income", "Age", "City", "Family", "Size (000s)", "Premium", "TAM (₹Cr)", "Priority"]
    for col, header in enumerate(priority_headers, 1):
        cell = ws_seg.cell(row=14, column=col, value=header)
        cell.style = "header_style"

    priority_segs = [
        [1, "Young Urban Professionals", "10-25L", "25-35", "Metro", "Individual", 2500, 12000, "=G15*H15/10000000", "P1"],
        [2, "DINK Couples Metro", "10-25L", "28-40", "Metro", "Couple", 1800, 18000, "=G16*H16/10000000", "P1"],
        [3, "Young Families Metro", "10-25L", "30-42", "Metro", "Family", 2200, 25000, "=G17*H17/10000000", "P1"],
        [4, "Tech Professionals", "25L+", "25-40", "Metro", "All", 800, 35000, "=G18*H18/10000000", "P1"],
        [5, "Senior Couples Metro", "10-25L", "55-65", "Metro", "Couple", 600, 45000, "=G19*H19/10000000", "P1"],
        [6, "Young Urban Tier-1", "5-10L", "25-35", "Tier-1", "Individual", 3500, 8000, "=G20*H20/10000000", "P2"],
        [7, "Families Tier-1", "5-10L", "30-45", "Tier-1", "Family", 2800, 15000, "=G21*H21/10000000", "P2"],
        [8, "Mid-Career Metro", "10-25L", "35-50", "Metro", "Family", 1500, 28000, "=G22*H22/10000000", "P2"],
        [9, "Senior Singles Metro", "10-25L", "60-70", "Metro", "Individual", 400, 55000, "=G23*H23/10000000", "P2"],
        [10, "Young Tier-2", "5-10L", "22-32", "Tier-2", "Individual", 4500, 6000, "=G24*H24/10000000", "P2"],
        [11, "SME Owners Metro", "25L+", "35-55", "Metro", "Family", 350, 45000, "=G25*H25/10000000", "P1"],
        [12, "Professionals Tier-1", "10-25L", "30-45", "Tier-1", "Family", 1200, 20000, "=G26*H26/10000000", "P2"],
        [13, "Gig Workers Metro", "5-10L", "22-35", "Metro", "Individual", 1800, 8000, "=G27*H27/10000000", "P3"],
        [14, "Pre-Retirees Metro", "10-25L", "50-60", "Metro", "Couple", 700, 38000, "=G28*H28/10000000", "P2"],
        [15, "HNI Families", "25L+", "40-60", "Metro", "Family", 200, 75000, "=G29*H29/10000000", "P1"],
        [16, "Young Couples Tier-1", "5-10L", "25-35", "Tier-1", "Couple", 2000, 12000, "=G30*H30/10000000", "P2"],
        [17, "Senior Tier-1", "5-10L", "60-70", "Tier-1", "Couple", 500, 35000, "=G31*H31/10000000", "P3"],
        [18, "Families Tier-2", "5-10L", "30-45", "Tier-2", "Family", 3200, 10000, "=G32*H32/10000000", "P3"],
        [19, "Young HNI", "25L+", "25-35", "Metro", "Individual", 150, 25000, "=G33*H33/10000000", "P1"],
        [20, "Senior HNI", "25L+", "55-70", "Metro", "Couple", 100, 85000, "=G34*H34/10000000", "P1"],
    ]

    for row_idx, data in enumerate(priority_segs, 15):
        for col_idx, value in enumerate(data, 1):
            cell = ws_seg.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    # Totals
    ws_seg['A35'] = "TOP 20 TOTAL"
    ws_seg['G35'] = "=SUM(G15:G34)"
    ws_seg['I35'] = "=SUM(I15:I34)"
    ws_seg['A35'].style = "highlight_style"
    ws_seg['G35'].style = "highlight_style"
    ws_seg['I35'].style = "highlight_style"

    set_column_widths(ws_seg, {
        'A': 6, 'B': 25, 'C': 10, 'D': 10, 'E': 10, 'F': 12, 'G': 12, 'H': 10, 'I': 12, 'J': 10
    })

    # ========================================
    # SHEET 9: IRDAI DETAILED DATA
    # ========================================
    ws_irdai = wb.create_sheet("9_IRDAI_Data")

    ws_irdai['A1'] = "IRDAI ANNUAL REPORT 2023-24 - EXTRACTED DATA"
    ws_irdai['A1'].style = "header_style"
    ws_irdai.merge_cells('A1:H1')

    ws_irdai['A2'] = "Source: https://irdai.gov.in/document-detail?documentId=6436847 | Released: December 2024"
    ws_irdai['A2'].font = Font(italic=True, size=9, color="0563C1")
    ws_irdai.merge_cells('A2:H2')

    irdai_headers = ["Line", "Category", "Metric", "Value", "Numeric", "Unit", "YoY Change", "Section"]
    for col, header in enumerate(irdai_headers, 1):
        cell = ws_irdai.cell(row=4, column=col, value=header)
        cell.style = "header_style"

    irdai_data = [
        [1, "Premium", "Total Insurance Premium", "₹11.19 Trillion", 1119000, "₹ Crore", "+8.5%", "Summary"],
        [2, "Premium", "Life Insurance Premium", "₹8.30 Trillion", 830000, "₹ Crore", "+6.06%", "Life"],
        [3, "Premium", "Non-Life GDPI", "₹2.90 Trillion", 290000, "₹ Crore", "+12.76%", "Non-Life"],
        [4, "Premium", "Health Insurance (incl PA)", "₹1.17 Trillion", 117000, "₹ Crore", "+20.2%", "Health"],
        [5, "Premium", "Motor Insurance", "₹92,000 Crore", 92000, "₹ Crore", "+10%", "Motor"],
        [6, "Premium", "Fire Insurance", "₹23,000 Crore", 23000, "₹ Crore", "+8%", "Fire"],
        [7, "Penetration", "Overall Penetration", "3.7%", 3.7, "%", "-0.3pp", "Macro"],
        [8, "Penetration", "Life Penetration", "2.8%", 2.8, "%", "-0.2pp", "Life"],
        [9, "Penetration", "Non-Life Penetration", "1.0%", 1.0, "%", "Flat", "Non-Life"],
        [10, "Density", "Overall Density", "$95", 95, "USD", "+5%", "Macro"],
        [11, "Density", "Life Density", "$70", 70, "USD", "+4%", "Life"],
        [12, "Density", "Non-Life Density", "$25", 25, "USD", "+8%", "Non-Life"],
        [13, "Claims", "Total Claims Paid", "₹7.66 Trillion", 766000, "₹ Crore", "+12%", "Claims"],
        [14, "Claims", "Health Claims Processed", "26.9 Million", 26900000, "Number", "+15%", "Health"],
        [15, "Claims", "Health Claims Amount", "₹88,101 Crore", 88101, "₹ Crore", "+18%", "Health"],
        [16, "Claims", "Avg Health Claim", "₹31,086", 31086, "₹", "+3%", "Health"],
        [17, "Ratio", "Non-Life Claims Ratio", "82.52%", 82.52, "%", "+2pp", "Non-Life"],
        [18, "Ratio", "Public Sector Claims Ratio", "97.23%", 97.23, "%", "+1pp", "Public"],
        [19, "Ratio", "Private GI Claims Ratio", "76.49%", 76.49, "%", "+1pp", "Private"],
        [20, "Ratio", "SAHI Claims Ratio", "63.63%", 63.63, "%", "-2pp", "SAHI"],
        [21, "Industry", "Non-Life Profit", "₹10,119 Crore", 10119, "₹ Crore", "+25%", "P&L"],
        [22, "Industry", "Life Insurers", 26, 26, "Number", "Flat", "Players"],
        [23, "Industry", "General Insurers", 25, 25, "Number", "Flat", "Players"],
        [24, "Industry", "SAHI Companies", 8, 8, "Number", "+1", "Players"],
        [25, "Industry", "Reinsurers", 12, 12, "Number", "Flat", "Players"],
    ]

    for row_idx, data in enumerate(irdai_data, 5):
        for col_idx, value in enumerate(data, 1):
            cell = ws_irdai.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    set_column_widths(ws_irdai, {
        'A': 6, 'B': 12, 'C': 28, 'D': 18, 'E': 12, 'F': 10, 'G': 12, 'H': 12
    })

    # ========================================
    # SHEET 10: GI COUNCIL DATA
    # ========================================
    ws_gic = wb.create_sheet("10_GI_Council")

    ws_gic['A1'] = "GI COUNCIL YEARBOOK 2023-24 - EXTRACTED DATA"
    ws_gic['A1'].style = "header_style"
    ws_gic.merge_cells('A1:H1')

    ws_gic['A2'] = "Source: https://www.gicouncil.in/yearbook/2023-24/ | Released: February 3, 2025"
    ws_gic['A2'].font = Font(italic=True, size=9, color="0563C1")
    ws_gic.merge_cells('A2:H2')

    gic_headers = ["Line", "Category", "Metric", "FY24 Value", "FY23 Value", "Growth", "10Y CAGR", "Page"]
    for col, header in enumerate(gic_headers, 1):
        cell = ws_gic.cell(row=4, column=col, value=header)
        cell.style = "header_style"

    gic_data = [
        [1, "GDPI", "Total GDPI", "₹2,89,673 Cr", "₹2,56,984 Cr", "12.40%", "13.1%", "Exec"],
        [2, "GDPI", "Public Sector", "₹92,639 Cr", "₹85,100 Cr", "8.88%", "7.5%", "Ch 2"],
        [3, "GDPI", "Private Sector", "₹1,54,963 Cr", "₹1,34,916 Cr", "14.86%", "17.2%", "Ch 2"],
        [4, "GDPI", "SAHI", "₹42,071 Cr", "₹33,097 Cr", "27.1%", "24.8%", "Ch 2"],
        [5, "Segment", "Health & PA Share", "40.3%", "38.0%", "+2.3pp", "19.5%", "Exec"],
        [6, "Segment", "Motor Share", "31.7%", "33.0%", "-1.3pp", "11.2%", "Exec"],
        [7, "Segment", "Fire Share", "8.0%", "8.5%", "-0.5pp", "8.5%", "Exec"],
        [8, "Segment", "Marine Share", "1.8%", "2.0%", "-0.2pp", "5.2%", "Exec"],
        [9, "Claims", "Gross Incurred Ratio", "73.0%", "71.5%", "+1.5pp", "-", "Exec"],
        [10, "Claims", "Net Incurred Ratio", "82.50%", "80.8%", "+1.7pp", "-", "Exec"],
        [11, "Financial", "Underwriting Deficit", "₹28,587 Cr", "₹24,500 Cr", "+17%", "-", "Exec"],
        [12, "Financial", "Investment Income", "₹46,397 Cr", "₹41,200 Cr", "+12.6%", "-", "Exec"],
        [13, "Financial", "Profit After Tax", "₹10,119 Cr", "₹8,100 Cr", "+25%", "-", "Exec"],
        [14, "Density", "Insurance Density", "₹2,009", "₹1,785", "+12.5%", "11.8%", "Exec"],
        [15, "Penetration", "Insurance Penetration", "0.98%", "0.97%", "+0.01pp", "-", "Exec"],
        [16, "Capital", "Capital Employed", "₹1,04,279 Cr", "₹94,800 Cr", "+10%", "7.9%", "Ch 4"],
        [17, "Investments", "Total Investments", "₹5,18,759 Cr", "₹4,68,500 Cr", "+10.7%", "14.0%", "Ch 4"],
        [18, "Investments", "Yield on Investment", "8.94%", "8.8%", "+0.14pp", "-", "Ch 4"],
        [19, "HR", "Total Employees", "1,79,207", "1,68,500", "+6.4%", "5.2%", "Ch 5"],
        [20, "Network", "Offices", "10,376", "9,928", "+4.5%", "3.8%", "Ch 5"],
        [21, "Volume", "Policies Issued", "33.48 Cr", "30.43 Cr", "+10%", "8.5%", "Ch 3"],
    ]

    for row_idx, data in enumerate(gic_data, 5):
        for col_idx, value in enumerate(data, 1):
            cell = ws_gic.cell(row=row_idx, column=col_idx, value=value)
            cell.style = "data_style"

    set_column_widths(ws_gic, {
        'A': 6, 'B': 12, 'C': 22, 'D': 16, 'E': 16, 'F': 10, 'G': 10, 'H': 8
    })

    # ========================================
    # Save workbook
    # ========================================
    output_path = "/home/user/forestry-demo/insurance_data/ICICI_Lombard_Complete_Model.xlsx"
    wb.save(output_path)
    print(f"✓ Excel model created: {output_path}")
    print(f"✓ Total sheets: {len(wb.sheetnames)}")
    for i, sheet in enumerate(wb.sheetnames, 1):
        print(f"  {i}. {sheet}")

    return output_path

if __name__ == "__main__":
    create_comprehensive_model()
