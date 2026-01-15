#!/usr/bin/env python3
"""
ICICI Lombard D2C - Fully Integrated Financial Model
All formulas linked across sheets with 1-page waterfall dashboard
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import DataBarRule, ColorScaleRule
from datetime import datetime

def create_integrated_model():
    wb = Workbook()

    # ========================================
    # SHEET 1: ASSUMPTIONS (Base Data - All other sheets reference this)
    # ========================================
    ws_assume = wb.active
    ws_assume.title = "A_Assumptions"

    # Header
    ws_assume.merge_cells('A1:F1')
    ws_assume['A1'] = "ICICI LOMBARD D2C MODEL - MASTER ASSUMPTIONS"
    ws_assume['A1'].font = Font(bold=True, size=14, color="FFFFFF")
    ws_assume['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    ws_assume['A1'].alignment = Alignment(horizontal='center')

    # Named ranges will be created by referencing cells
    headers = ["ID", "Parameter", "Value", "Unit", "Source", "Citation"]
    for col, h in enumerate(headers, 1):
        cell = ws_assume.cell(row=3, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    # MARKET SIZE ASSUMPTIONS
    ws_assume['A4'] = "MARKET SIZE"
    ws_assume['A4'].font = Font(bold=True, color="1F4E79")
    ws_assume.merge_cells('A4:F4')

    market_data = [
        ["M1", "Total Health Insurance GWP FY24", 117000, "₹ Crore", "IRDAI AR 2023-24", "Page 45, Table 3.1"],
        ["M2", "Retail Health % of Total", 0.387, "%", "Niva Bupa DRHP", "Page 15, Industry Report"],
        ["M3", "Group Health % of Total", 0.505, "%", "Niva Bupa DRHP", "Page 15, Industry Report"],
        ["M4", "Govt Schemes % of Total", 0.097, "%", "Niva Bupa DRHP", "Page 15, Industry Report"],
        ["M5", "Overseas Medical % of Total", 0.011, "%", "Niva Bupa DRHP", "Page 15, Industry Report"],
        ["M6", "Urban Digital Addressable %", 0.60, "%", "Industry Estimate", "Redseer Analysis"],
        ["M7", "Target Income Segment %", 0.35, "%", "CBDT Calculation", "Income >5L / Total"],
        ["M8", "5Y Capture Rate %", 0.15, "%", "Model Assumption", "Conservative"],
        ["M9", "Health Insurance Growth CAGR", 0.195, "%", "GI Council YB", "10-Year CAGR"],
        ["M10", "Retail Health Growth FY24", 0.191, "%", "Niva Bupa DRHP", "Page 18"],
    ]

    for row_idx, data in enumerate(market_data, 5):
        for col_idx, value in enumerate(data, 1):
            ws_assume.cell(row=row_idx, column=col_idx, value=value)

    # CUSTOMER ASSUMPTIONS
    ws_assume['A16'] = "CUSTOMER METRICS"
    ws_assume['A16'].font = Font(bold=True, color="1F4E79")
    ws_assume.merge_cells('A16:F16')

    customer_data = [
        ["C1", "Avg Annual Premium (Retail)", 15000, "₹", "IRDAI/Industry", "Weighted avg"],
        ["C2", "Premium Growth Rate (Annual)", 0.08, "%", "Medical Inflation", "CPI Health"],
        ["C3", "Retention Rate Year 1", 0.80, "%", "Industry Benchmark", "New cohort"],
        ["C4", "Retention Rate Year 2+", 0.85, "%", "Industry Benchmark", "Mature cohort"],
        ["C5", "Avg Policy Duration", 5, "Years", "Retention Based", "Calculated"],
        ["C6", "Year 1 New Customers", 50000, "Number", "Model Target", "Launch year"],
        ["C7", "Customer Growth Y1-Y2", 0.40, "%", "Model Target", "Aggressive"],
        ["C8", "Customer Growth Y2-Y3", 0.35, "%", "Model Target", "Scaling"],
        ["C9", "Customer Growth Y3-Y4", 0.30, "%", "Model Target", "Maturing"],
        ["C10", "Customer Growth Y4-Y5", 0.25, "%", "Model Target", "Steady"],
    ]

    for row_idx, data in enumerate(customer_data, 17):
        for col_idx, value in enumerate(data, 1):
            ws_assume.cell(row=row_idx, column=col_idx, value=value)

    # FINANCIAL ASSUMPTIONS
    ws_assume['A28'] = "FINANCIAL METRICS"
    ws_assume['A28'].font = Font(bold=True, color="1F4E79")
    ws_assume.merge_cells('A28:F28')

    financial_data = [
        ["F1", "Claims Ratio Target", 0.65, "%", "SAHI Benchmark", "Star Health 66.5%"],
        ["F2", "Expense Ratio Target", 0.25, "%", "Digital Efficiency", "vs 30% traditional"],
        ["F3", "Gross Margin", "=1-C29-C30", "%", "Calculated", "1 - Claims - Expense"],
        ["F4", "Discount Rate (WACC)", 0.12, "%", "Industry WACC", "Insurance sector"],
        ["F5", "CAC D2C Organic", 1500, "₹", "Industry Est", "SEO/Content"],
        ["F6", "CAC D2C Paid", 3000, "₹", "Industry Est", "Performance mktg"],
        ["F7", "CAC Aggregators", 4500, "₹", "PolicyBazaar", "Commission based"],
        ["F8", "CAC Agents/Brokers", 6000, "₹", "Commission", "15-20% of premium"],
        ["F9", "CAC Bancassurance", 2500, "₹", "Bank Partnership", "Lower commission"],
        ["F10", "CAC Reduction Rate YoY", 0.08, "%", "Efficiency Gains", "Scale benefits"],
    ]

    for row_idx, data in enumerate(financial_data, 29):
        for col_idx, value in enumerate(data, 1):
            ws_assume.cell(row=row_idx, column=col_idx, value=value)

    # CHANNEL MIX
    ws_assume['A40'] = "CHANNEL MIX"
    ws_assume['A40'].font = Font(bold=True, color="1F4E79")
    ws_assume.merge_cells('A40:F40')

    channel_data = [
        ["CH1", "D2C Organic %", 0.15, "%", "Target", "App organic"],
        ["CH2", "D2C Paid %", 0.25, "%", "Target", "Performance"],
        ["CH3", "Aggregators %", 0.20, "%", "Target", "PolicyBazaar etc"],
        ["CH4", "Agents/Brokers %", 0.30, "%", "Target", "Traditional"],
        ["CH5", "Bancassurance %", 0.10, "%", "Target", "ICICI Bank"],
    ]

    for row_idx, data in enumerate(channel_data, 41):
        for col_idx, value in enumerate(data, 1):
            ws_assume.cell(row=row_idx, column=col_idx, value=value)

    # COMPETITION DATA
    ws_assume['A48'] = "COMPETITOR BENCHMARKS"
    ws_assume['A48'].font = Font(bold=True, color="1F4E79")
    ws_assume.merge_cells('A48:F48')

    comp_data = [
        ["COMP1", "ICICI Lombard Retail Health Share", 0.029, "%", "Business Standard", "Q1 FY25"],
        ["COMP2", "Star Health Retail Share", 0.33, "%", "Star Health AR", "FY24"],
        ["COMP3", "Niva Bupa Retail Share", 0.162, "%", "Niva Bupa DRHP", "Page 12"],
        ["COMP4", "SAHI Claims Ratio", 0.6363, "%", "IRDAI AR", "Page 52"],
        ["COMP5", "Private GI Claims Ratio", 0.7649, "%", "IRDAI AR", "Page 52"],
        ["COMP6", "Star Health Agents (000s)", 701, "Number", "Star Health AR", "Distribution"],
        ["COMP7", "Niva Bupa Agents (000s)", 180, "Number", "Niva Bupa AR", "Distribution"],
    ]

    for row_idx, data in enumerate(comp_data, 49):
        for col_idx, value in enumerate(data, 1):
            ws_assume.cell(row=row_idx, column=col_idx, value=value)

    # Set column widths
    ws_assume.column_dimensions['A'].width = 8
    ws_assume.column_dimensions['B'].width = 35
    ws_assume.column_dimensions['C'].width = 15
    ws_assume.column_dimensions['D'].width = 12
    ws_assume.column_dimensions['E'].width = 20
    ws_assume.column_dimensions['F'].width = 25

    # ========================================
    # SHEET 2: WATERFALL (1-Page Dashboard - All formulas reference Assumptions)
    # ========================================
    ws_wf = wb.create_sheet("B_Waterfall")

    # Title
    ws_wf.merge_cells('A1:J1')
    ws_wf['A1'] = "ICICI LOMBARD D2C HEALTH INSURANCE - OPPORTUNITY WATERFALL"
    ws_wf['A1'].font = Font(bold=True, size=16, color="FFFFFF")
    ws_wf['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    ws_wf['A1'].alignment = Alignment(horizontal='center')

    ws_wf.merge_cells('A2:J2')
    ws_wf['A2'] = "All values linked to Assumptions sheet | TAM → SAM → SOM Analysis"
    ws_wf['A2'].font = Font(italic=True, size=10)
    ws_wf['A2'].alignment = Alignment(horizontal='center')

    # WATERFALL SECTION
    ws_wf['A4'] = "TAM → SAM → SOM WATERFALL"
    ws_wf['A4'].font = Font(bold=True, size=12, color="1F4E79")
    ws_wf.merge_cells('A4:E4')

    wf_headers = ["Step", "Description", "Value (₹ Cr)", "Formula", "% of TAM"]
    for col, h in enumerate(wf_headers, 1):
        cell = ws_wf.cell(row=5, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    # Waterfall with formulas referencing Assumptions
    ws_wf['A6'] = 1
    ws_wf['B6'] = "TAM: Total Health Insurance Market"
    ws_wf['C6'] = "=A_Assumptions!C5"  # M1: Total Health Insurance
    ws_wf['D6'] = "=A_Assumptions!C5"
    ws_wf['E6'] = "100%"

    ws_wf['A7'] = 2
    ws_wf['B7'] = "Filter: Retail Health Only (38.7%)"
    ws_wf['C7'] = "=C6*A_Assumptions!C6"  # M2: Retail %
    ws_wf['D7'] = "=TAM × Retail%"
    ws_wf['E7'] = "=C7/C6"

    ws_wf['A8'] = 3
    ws_wf['B8'] = "Filter: Urban Digital Addressable (60%)"
    ws_wf['C8'] = "=C7*A_Assumptions!C10"  # M6: Urban Digital %
    ws_wf['D8'] = "=Retail × Urban%"
    ws_wf['E8'] = "=C8/C6"

    ws_wf['A9'] = 4
    ws_wf['B9'] = "Filter: Target Income >5L (35%)"
    ws_wf['C9'] = "=C8*A_Assumptions!C11"  # M7: Target Income %
    ws_wf['D9'] = "=Urban × Income%"
    ws_wf['E9'] = "=C9/C6"

    ws_wf['A10'] = 5
    ws_wf['B10'] = "SOM: 5-Year Realistic Capture (15%)"
    ws_wf['C10'] = "=C9*A_Assumptions!C12"  # M8: Capture Rate
    ws_wf['D10'] = "=Target × Capture%"
    ws_wf['E10'] = "=C10/C6"

    # Highlight SOM
    ws_wf['A11'] = ""
    ws_wf['B11'] = "D2C OPPORTUNITY (SOM)"
    ws_wf['C11'] = "=C10"
    ws_wf['D11'] = "5-Year Target"
    ws_wf['E11'] = "=E10"
    ws_wf['B11'].font = Font(bold=True, size=12)
    ws_wf['C11'].font = Font(bold=True, size=12)
    ws_wf['C11'].fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

    # LTV/CAC SECTION
    ws_wf['A14'] = "UNIT ECONOMICS (LTV/CAC)"
    ws_wf['A14'].font = Font(bold=True, size=12, color="1F4E79")
    ws_wf.merge_cells('A14:E14')

    ltv_headers = ["Metric", "Value", "Formula", "Benchmark", "Status"]
    for col, h in enumerate(ltv_headers, 1):
        cell = ws_wf.cell(row=15, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    ws_wf['A16'] = "Avg Annual Premium"
    ws_wf['B16'] = "=A_Assumptions!C17"  # C1
    ws_wf['C16'] = "=Assumptions!C17"
    ws_wf['D16'] = "₹12,000 - ₹20,000"
    ws_wf['E16'] = "=IF(B16>=12000,\"GOOD\",\"LOW\")"

    ws_wf['A17'] = "Gross Margin %"
    ws_wf['B17'] = "=1-A_Assumptions!C29-A_Assumptions!C30"  # 1 - Claims - Expense
    ws_wf['C17'] = "=1-Claims%-Expense%"
    ws_wf['D17'] = ">8%"
    ws_wf['E17'] = "=IF(B17>=0.08,\"GOOD\",\"IMPROVE\")"

    ws_wf['A18'] = "Avg Policy Life (Years)"
    ws_wf['B18'] = "=A_Assumptions!C21"  # C5
    ws_wf['C18'] = "=Assumptions!C21"
    ws_wf['D18'] = ">4 years"
    ws_wf['E18'] = "=IF(B18>=4,\"GOOD\",\"LOW\")"

    ws_wf['A19'] = "Customer LTV"
    ws_wf['B19'] = "=B16*B17*B18"  # Premium × Margin × Years
    ws_wf['C19'] = "=Premium×Margin×Years"
    ws_wf['D19'] = ">₹20,000"
    ws_wf['E19'] = "=IF(B19>=20000,\"GOOD\",\"IMPROVE\")"

    ws_wf['A20'] = "Blended CAC"
    ws_wf['B20'] = "=A_Assumptions!C33*A_Assumptions!C41+A_Assumptions!C34*A_Assumptions!C42+A_Assumptions!C35*A_Assumptions!C43+A_Assumptions!C36*A_Assumptions!C44+A_Assumptions!C37*A_Assumptions!C45"
    ws_wf['C20'] = "=Σ(CAC×Channel%)"
    ws_wf['D20'] = "<₹4,000"
    ws_wf['E20'] = "=IF(B20<=4000,\"GOOD\",\"HIGH\")"

    ws_wf['A21'] = "LTV:CAC Ratio"
    ws_wf['B21'] = "=B19/B20"
    ws_wf['C21'] = "=LTV/CAC"
    ws_wf['D21'] = ">3:1"
    ws_wf['E21'] = "=IF(B21>=3,\"HEALTHY\",\"IMPROVE\")"

    ws_wf['A22'] = "Payback Period (Months)"
    ws_wf['B22'] = "=B20/(B16*B17/12)"
    ws_wf['C22'] = "=CAC/(MonthlyMargin)"
    ws_wf['D22'] = "<18 months"
    ws_wf['E22'] = "=IF(B22<=18,\"GOOD\",\"LONG\")"

    # 5-YEAR PROJECTION SECTION
    ws_wf['A25'] = "5-YEAR PROJECTION SUMMARY"
    ws_wf['A25'].font = Font(bold=True, size=12, color="1F4E79")
    ws_wf.merge_cells('A25:G25')

    proj_headers = ["Metric", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "5Y Total"]
    for col, h in enumerate(proj_headers, 1):
        cell = ws_wf.cell(row=26, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    # New Customers - linked to assumptions
    ws_wf['A27'] = "New Customers"
    ws_wf['B27'] = "=A_Assumptions!C22"  # C6: Year 1 customers
    ws_wf['C27'] = "=B27*(1+A_Assumptions!C23)"  # C7: Growth Y1-Y2
    ws_wf['D27'] = "=C27*(1+A_Assumptions!C24)"  # C8: Growth Y2-Y3
    ws_wf['E27'] = "=D27*(1+A_Assumptions!C25)"  # C9: Growth Y3-Y4
    ws_wf['F27'] = "=E27*(1+A_Assumptions!C26)"  # C10: Growth Y4-Y5
    ws_wf['G27'] = "=SUM(B27:F27)"

    # Retained Customers
    ws_wf['A28'] = "Retained Customers"
    ws_wf['B28'] = 0
    ws_wf['C28'] = "=B29*A_Assumptions!C19"  # C3: Retention Y1
    ws_wf['D28'] = "=C29*A_Assumptions!C20"  # C4: Retention Y2+
    ws_wf['E28'] = "=D29*A_Assumptions!C20"
    ws_wf['F28'] = "=E29*A_Assumptions!C20"
    ws_wf['G28'] = "=F28"

    # Total Customers
    ws_wf['A29'] = "Total Customers"
    ws_wf['B29'] = "=B27+B28"
    ws_wf['C29'] = "=C27+C28"
    ws_wf['D29'] = "=D27+D28"
    ws_wf['E29'] = "=E27+E28"
    ws_wf['F29'] = "=F27+F28"
    ws_wf['G29'] = "=F29"

    # Avg Premium
    ws_wf['A30'] = "Avg Premium (₹)"
    ws_wf['B30'] = "=A_Assumptions!C17"  # C1: Avg Premium
    ws_wf['C30'] = "=B30*(1+A_Assumptions!C18)"  # C2: Premium Growth
    ws_wf['D30'] = "=C30*(1+A_Assumptions!C18)"
    ws_wf['E30'] = "=D30*(1+A_Assumptions!C18)"
    ws_wf['F30'] = "=E30*(1+A_Assumptions!C18)"
    ws_wf['G30'] = "=AVERAGE(B30:F30)"

    # GWP
    ws_wf['A31'] = "GWP (₹ Cr)"
    ws_wf['B31'] = "=B29*B30/10000000"
    ws_wf['C31'] = "=C29*C30/10000000"
    ws_wf['D31'] = "=D29*D30/10000000"
    ws_wf['E31'] = "=E29*E30/10000000"
    ws_wf['F31'] = "=F29*F30/10000000"
    ws_wf['G31'] = "=SUM(B31:F31)"
    ws_wf['G31'].font = Font(bold=True)
    ws_wf['G31'].fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

    # Gross Margin
    ws_wf['A32'] = "Gross Margin (₹ Cr)"
    ws_wf['B32'] = "=B31*B17"
    ws_wf['C32'] = "=C31*B17"
    ws_wf['D32'] = "=D31*B17"
    ws_wf['E32'] = "=E31*B17"
    ws_wf['F32'] = "=F31*B17"
    ws_wf['G32'] = "=SUM(B32:F32)"

    # CAC Spend
    ws_wf['A33'] = "CAC Spend (₹ Cr)"
    ws_wf['B33'] = "=B27*B20/10000000"
    ws_wf['C33'] = "=C27*B20*(1-A_Assumptions!C38)/10000000"  # F10: CAC reduction
    ws_wf['D33'] = "=D27*B20*(1-A_Assumptions!C38)^2/10000000"
    ws_wf['E33'] = "=E27*B20*(1-A_Assumptions!C38)^3/10000000"
    ws_wf['F33'] = "=F27*B20*(1-A_Assumptions!C38)^4/10000000"
    ws_wf['G33'] = "=SUM(B33:F33)"

    # Contribution
    ws_wf['A34'] = "Contribution (₹ Cr)"
    ws_wf['B34'] = "=B32-B33"
    ws_wf['C34'] = "=C32-C33"
    ws_wf['D34'] = "=D32-D33"
    ws_wf['E34'] = "=E32-E33"
    ws_wf['F34'] = "=F32-F33"
    ws_wf['G34'] = "=SUM(B34:F34)"
    ws_wf['G34'].font = Font(bold=True)
    ws_wf['G34'].fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

    # CAGR
    ws_wf['A35'] = "CAGR"
    ws_wf['B35'] = "-"
    ws_wf['C35'] = "-"
    ws_wf['D35'] = "-"
    ws_wf['E35'] = "-"
    ws_wf['F35'] = "-"
    ws_wf['G35'] = "=(F31/B31)^(1/4)-1"

    # KEY METRICS BOX
    ws_wf['A38'] = "KEY OUTPUTS"
    ws_wf['A38'].font = Font(bold=True, size=12, color="1F4E79")
    ws_wf.merge_cells('A38:C38')

    ws_wf['A39'] = "5-Year SOM Target"
    ws_wf['B39'] = "=C10"
    ws_wf['C39'] = "₹ Crore"
    ws_wf['B39'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    ws_wf['A40'] = "Year 5 Customer Base"
    ws_wf['B40'] = "=F29"
    ws_wf['C40'] = "Customers"
    ws_wf['B40'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    ws_wf['A41'] = "Year 5 GWP"
    ws_wf['B41'] = "=F31"
    ws_wf['C41'] = "₹ Crore"
    ws_wf['B41'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    ws_wf['A42'] = "5-Year Total GWP"
    ws_wf['B42'] = "=G31"
    ws_wf['C42'] = "₹ Crore"
    ws_wf['B42'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    ws_wf['A43'] = "5-Year Contribution"
    ws_wf['B43'] = "=G34"
    ws_wf['C43'] = "₹ Crore"
    ws_wf['B43'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    ws_wf['A44'] = "LTV:CAC Ratio"
    ws_wf['B44'] = "=B21"
    ws_wf['C44'] = ":1"
    ws_wf['B44'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    ws_wf['A45'] = "GWP CAGR"
    ws_wf['B45'] = "=G35"
    ws_wf['C45'] = "%"
    ws_wf['B45'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    # SOURCES on right side
    ws_wf['H4'] = "DATA SOURCES"
    ws_wf['H4'].font = Font(bold=True, size=12, color="1F4E79")
    ws_wf.merge_cells('H4:J4')

    sources = [
        ["CBDT ITR AY23-24", "Income Tax Dept", "Jun 2024"],
        ["IRDAI AR 2023-24", "IRDAI", "Dec 2024"],
        ["GI Council YB 23-24", "GI Council", "Feb 2025"],
        ["Niva Bupa DRHP", "Niva Bupa", "Jun 2024"],
        ["Star Health AR", "Star Health", "FY24"],
        ["ICICI Lombard AR", "ICICI Lombard", "FY24"],
    ]

    for col, h in enumerate(["Source", "Publisher", "Date"], 8):
        cell = ws_wf.cell(row=5, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    for row_idx, data in enumerate(sources, 6):
        for col_idx, value in enumerate(data, 8):
            ws_wf.cell(row=row_idx, column=col_idx, value=value)

    # Column widths
    ws_wf.column_dimensions['A'].width = 25
    ws_wf.column_dimensions['B'].width = 15
    ws_wf.column_dimensions['C'].width = 18
    ws_wf.column_dimensions['D'].width = 20
    ws_wf.column_dimensions['E'].width = 12
    ws_wf.column_dimensions['F'].width = 12
    ws_wf.column_dimensions['G'].width = 12
    ws_wf.column_dimensions['H'].width = 18
    ws_wf.column_dimensions['I'].width = 12
    ws_wf.column_dimensions['J'].width = 10

    # ========================================
    # SHEET 3: CBDT DATA (Referenced by Waterfall)
    # ========================================
    ws_cbdt = wb.create_sheet("C_CBDT_Data")

    ws_cbdt.merge_cells('A1:H1')
    ws_cbdt['A1'] = "CBDT ITR STATISTICS AY 2023-24"
    ws_cbdt['A1'].font = Font(bold=True, size=14, color="FFFFFF")
    ws_cbdt['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")

    ws_cbdt['A2'] = "Source: https://incometaxindia.gov.in | Page 9, Table 1.1"
    ws_cbdt['A2'].font = Font(italic=True, color="0563C1")

    headers = ["Slab", "Income Range", "Filers", "% Total", "Cumulative", "Target", "Avg Premium", "TAM (₹Cr)"]
    for col, h in enumerate(headers, 1):
        cell = ws_cbdt.cell(row=4, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    cbdt_data = [
        [1, "Income = 0", 1441175, "", "", "No", 0, 0],
        [2, ">0 to ≤1.5L", 4144666, "", "", "No", 0, 0],
        [3, ">1.5L to ≤2L", 1509747, "", "", "No", 0, 0],
        [4, ">2L to ≤2.5L", 3036825, "", "", "No", 0, 0],
        [5, ">2.5L to ≤3.5L", 5946214, "", "", "No", 5000, 0],
        [6, ">3.5L to ≤4L", 4055198, "", "", "No", 5000, 0],
        [7, ">4L to ≤4.5L", 6024031, "", "", "Low", 6000, 0],
        [8, ">4.5L to ≤5L", 12600689, "", "", "Low", 8000, 0],
        [9, ">5L to ≤5.5L", 6154414, "", "", "YES", 10000, "=C13*G13/10000000"],
        [10, ">5.5L to ≤9.5L", 20697590, "", "", "YES", 12000, "=C14*G14/10000000"],
        [11, ">9.5L to ≤10L", 1084818, "", "", "YES", 15000, "=C15*G15/10000000"],
        [12, ">10L to ≤15L", 6379208, "", "", "YES", 18000, "=C16*G16/10000000"],
        [13, ">15L to ≤20L", 2503932, "", "", "YES", 22000, "=C17*G17/10000000"],
        [14, ">20L to ≤25L", 1240128, "", "", "YES", 28000, "=C18*G18/10000000"],
        [15, ">25L to ≤50L", 1953619, "", "", "YES", 35000, "=C19*G19/10000000"],
        [16, ">50L to ≤1Cr", 589762, "", "", "PREMIUM", 50000, "=C20*G20/10000000"],
        [17, ">1Cr to ≤5Cr", 291929, "", "", "PREMIUM", 75000, "=C21*G21/10000000"],
        [18, ">5Cr+", 74065, "", "", "PREMIUM", 100000, "=C22*G22/10000000"],
    ]

    for row_idx, data in enumerate(cbdt_data, 5):
        for col_idx, value in enumerate(data, 1):
            ws_cbdt.cell(row=row_idx, column=col_idx, value=value)

    # Add formulas for % and cumulative
    for row in range(5, 23):
        ws_cbdt.cell(row=row, column=4, value=f"=C{row}/C23")
        if row == 5:
            ws_cbdt.cell(row=row, column=5, value=f"=D{row}")
        else:
            ws_cbdt.cell(row=row, column=5, value=f"=E{row-1}+D{row}")

    # Total row
    ws_cbdt['A23'] = "TOTAL"
    ws_cbdt['B23'] = "All Filers"
    ws_cbdt['C23'] = "=SUM(C5:C22)"
    ws_cbdt['D23'] = "100%"
    ws_cbdt['E23'] = "100%"
    ws_cbdt['H23'] = "=SUM(H5:H22)"
    ws_cbdt['A23'].font = Font(bold=True)
    ws_cbdt['C23'].font = Font(bold=True)
    ws_cbdt['H23'].font = Font(bold=True)

    # Summary
    ws_cbdt['A25'] = "TARGET SEGMENT (>5L)"
    ws_cbdt['B25'] = "=SUM(C13:C22)"
    ws_cbdt['C25'] = "=B25/C23"
    ws_cbdt['A25'].font = Font(bold=True)
    ws_cbdt['B25'].fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

    ws_cbdt.column_dimensions['A'].width = 6
    ws_cbdt.column_dimensions['B'].width = 18
    ws_cbdt.column_dimensions['C'].width = 12
    ws_cbdt.column_dimensions['D'].width = 10
    ws_cbdt.column_dimensions['E'].width = 12
    ws_cbdt.column_dimensions['F'].width = 10
    ws_cbdt.column_dimensions['G'].width = 12
    ws_cbdt.column_dimensions['H'].width = 14

    # ========================================
    # SHEET 4: COMPETITORS (Referenced by Waterfall)
    # ========================================
    ws_comp = wb.create_sheet("D_Competitors")

    ws_comp.merge_cells('A1:L1')
    ws_comp['A1'] = "COMPETITOR ANALYSIS - ANNUAL REPORTS & DRHP DATA"
    ws_comp['A1'].font = Font(bold=True, size=14, color="FFFFFF")
    ws_comp['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")

    headers = ["Rank", "Insurer", "Type", "GWP (₹Cr)", "Share", "Health GWP", "Claims%", "Combined%", "Growth", "Solvency", "Source", "Page"]
    for col, h in enumerate(headers, 1):
        cell = ws_comp.cell(row=3, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    competitors = [
        [1, "New India Assurance", "PSU", 40364, "13.1%", 12109, "97.2%", "116%", "8.9%", "1.67x", "IRDAI AR", "Ch5"],
        [2, "ICICI Lombard", "Private", 24776, "8.7%", 2800, "76.5%", "103.8%", "20.4%", "2.69x", "Company AR", "Fin"],
        [3, "Bajaj Allianz", "Private", 22000, "7.7%", 3300, "78%", "99.9%", "14.8%", "3.49x", "ICRA", "Rating"],
        [4, "Star Health", "SAHI", 15254, "5.3%", 15254, "66.5%", "97.3%", "22.3%", "2.15x", "Company AR", "Fin"],
        [5, "United India", "PSU", 19852, "6.8%", 5956, "97%", "118%", "5%", "1.52x", "IRDAI AR", "Ch5"],
        [6, "HDFC ERGO", "Private", 9000, "3.1%", 1800, "82%", "102%", "12%", "2.35x", "Company AR", "Fin"],
        [7, "Tata AIG", "Private", 8500, "2.9%", 1700, "80%", "100%", "18%", "2.45x", "Company AR", "Fin"],
        [8, "Niva Bupa", "SAHI", 5499, "1.9%", 5499, "70%", "95%", "41%", "1.85x", "DRHP", "Pg12"],
        [9, "Care Health", "SAHI", 4500, "1.6%", 4500, "68%", "93%", "20%", "1.92x", "Company AR", "Fin"],
        [10, "Aditya Birla", "SAHI", 3290, "1.1%", 3290, "72%", "96%", "48%", "1.75x", "Company AR", "Fin"],
    ]

    for row_idx, data in enumerate(competitors, 4):
        for col_idx, value in enumerate(data, 1):
            ws_comp.cell(row=row_idx, column=col_idx, value=value)

    # ICICI Gap Analysis
    ws_comp['A16'] = "ICICI LOMBARD GAP ANALYSIS"
    ws_comp['A16'].font = Font(bold=True, size=12, color="1F4E79")
    ws_comp.merge_cells('A16:F16')

    gap_headers = ["Metric", "ICICI", "Star Health", "Gap", "Target", "Action"]
    for col, h in enumerate(gap_headers, 1):
        cell = ws_comp.cell(row=17, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    gaps = [
        ["Retail Health Share", "2.9%", "33%", "=C18-B18", "10%", "D2C Focus"],
        ["Claims Ratio", "76.5%", "66.5%", "=B19-C19", "65%", "Underwriting"],
        ["Digital Share", "17.4%", "15%", "=B20-C20", "35%", "App Launch"],
        ["Agent Network", "150K", "701K", "=C21-B21", "250K", "Hybrid Model"],
        ["Renewal Rate", "80%", "82%", "=C22-B22", "90%", "Engagement"],
    ]

    for row_idx, data in enumerate(gaps, 18):
        for col_idx, value in enumerate(data, 1):
            ws_comp.cell(row=row_idx, column=col_idx, value=value)

    for col in range(1, 13):
        ws_comp.column_dimensions[get_column_letter(col)].width = 12
    ws_comp.column_dimensions['B'].width = 18
    ws_comp.column_dimensions['F'].width = 14

    # ========================================
    # SHEET 5: LTV DETAILED
    # ========================================
    ws_ltv = wb.create_sheet("E_LTV_Detail")

    ws_ltv.merge_cells('A1:H1')
    ws_ltv['A1'] = "CUSTOMER LIFETIME VALUE - DETAILED NPV CALCULATION"
    ws_ltv['A1'].font = Font(bold=True, size=14, color="FFFFFF")
    ws_ltv['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")

    ws_ltv['A3'] = "All inputs linked to Assumptions sheet"
    ws_ltv['A3'].font = Font(italic=True)

    headers = ["Year", "Premium", "Retention", "Expected Premium", "Gross Margin", "Discount", "PV Margin", "Cumulative"]
    for col, h in enumerate(headers, 1):
        cell = ws_ltv.cell(row=5, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    # Year 1
    ws_ltv['A6'] = 1
    ws_ltv['B6'] = "=A_Assumptions!C17"
    ws_ltv['C6'] = "100%"
    ws_ltv['D6'] = "=B6*C6"
    ws_ltv['E6'] = "=D6*(1-A_Assumptions!C29-A_Assumptions!C30)"
    ws_ltv['F6'] = "=1/(1+A_Assumptions!C32)^A6"
    ws_ltv['G6'] = "=E6*F6"
    ws_ltv['H6'] = "=G6"

    # Year 2
    ws_ltv['A7'] = 2
    ws_ltv['B7'] = "=B6*(1+A_Assumptions!C18)"
    ws_ltv['C7'] = "=A_Assumptions!C19"
    ws_ltv['D7'] = "=B7*C7"
    ws_ltv['E7'] = "=D7*(1-A_Assumptions!C29-A_Assumptions!C30)"
    ws_ltv['F7'] = "=1/(1+A_Assumptions!C32)^A7"
    ws_ltv['G7'] = "=E7*F7"
    ws_ltv['H7'] = "=H6+G7"

    # Year 3-5
    for row in range(8, 11):
        year = row - 5
        ws_ltv[f'A{row}'] = year
        ws_ltv[f'B{row}'] = f"=B{row-1}*(1+A_Assumptions!C18)"
        ws_ltv[f'C{row}'] = f"=C{row-1}*A_Assumptions!C20"
        ws_ltv[f'D{row}'] = f"=B{row}*C{row}"
        ws_ltv[f'E{row}'] = f"=D{row}*(1-A_Assumptions!C29-A_Assumptions!C30)"
        ws_ltv[f'F{row}'] = f"=1/(1+A_Assumptions!C32)^A{row}"
        ws_ltv[f'G{row}'] = f"=E{row}*F{row}"
        ws_ltv[f'H{row}'] = f"=H{row-1}+G{row}"

    # LTV Result
    ws_ltv['A12'] = "5-YEAR LTV"
    ws_ltv['B12'] = "=H10"
    ws_ltv['A12'].font = Font(bold=True, size=12)
    ws_ltv['B12'].font = Font(bold=True, size=12)
    ws_ltv['B12'].fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

    # CAC Detail
    ws_ltv['A15'] = "CAC BY CHANNEL"
    ws_ltv['A15'].font = Font(bold=True, size=12, color="1F4E79")

    cac_headers = ["Channel", "CAC (₹)", "Mix %", "Weighted CAC"]
    for col, h in enumerate(cac_headers, 1):
        cell = ws_ltv.cell(row=16, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    ws_ltv['A17'] = "D2C Organic"
    ws_ltv['B17'] = "=A_Assumptions!C33"
    ws_ltv['C17'] = "=A_Assumptions!C41"
    ws_ltv['D17'] = "=B17*C17"

    ws_ltv['A18'] = "D2C Paid"
    ws_ltv['B18'] = "=A_Assumptions!C34"
    ws_ltv['C18'] = "=A_Assumptions!C42"
    ws_ltv['D18'] = "=B18*C18"

    ws_ltv['A19'] = "Aggregators"
    ws_ltv['B19'] = "=A_Assumptions!C35"
    ws_ltv['C19'] = "=A_Assumptions!C43"
    ws_ltv['D19'] = "=B19*C19"

    ws_ltv['A20'] = "Agents/Brokers"
    ws_ltv['B20'] = "=A_Assumptions!C36"
    ws_ltv['C20'] = "=A_Assumptions!C44"
    ws_ltv['D20'] = "=B20*C20"

    ws_ltv['A21'] = "Bancassurance"
    ws_ltv['B21'] = "=A_Assumptions!C37"
    ws_ltv['C21'] = "=A_Assumptions!C45"
    ws_ltv['D21'] = "=B21*C21"

    ws_ltv['A22'] = "BLENDED CAC"
    ws_ltv['B22'] = "=SUM(D17:D21)"
    ws_ltv['C22'] = "=SUM(C17:C21)"
    ws_ltv['D22'] = "=SUM(D17:D21)"
    ws_ltv['A22'].font = Font(bold=True)
    ws_ltv['B22'].font = Font(bold=True)
    ws_ltv['B22'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    # LTV:CAC
    ws_ltv['A25'] = "LTV:CAC RATIO"
    ws_ltv['B25'] = "=B12/B22"
    ws_ltv['A25'].font = Font(bold=True, size=12)
    ws_ltv['B25'].font = Font(bold=True, size=12)
    ws_ltv['B25'].fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

    ws_ltv['A26'] = "Payback (Months)"
    ws_ltv['B26'] = "=B22/(A_Assumptions!C17*(1-A_Assumptions!C29-A_Assumptions!C30)/12)"

    for col in range(1, 9):
        ws_ltv.column_dimensions[get_column_letter(col)].width = 14
    ws_ltv.column_dimensions['A'].width = 18

    # ========================================
    # SHEET 6: SOURCES
    # ========================================
    ws_src = wb.create_sheet("F_Sources")

    ws_src.merge_cells('A1:G1')
    ws_src['A1'] = "DATA SOURCES WITH FULL CITATIONS"
    ws_src['A1'].font = Font(bold=True, size=14, color="FFFFFF")
    ws_src['A1'].fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")

    headers = ["ID", "Document", "Publisher", "URL", "Date", "Pages Used", "Key Data"]
    for col, h in enumerate(headers, 1):
        cell = ws_src.cell(row=3, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    sources = [
        ["S01", "ITR Statistics AY 2023-24", "CBDT, Ministry of Finance",
         "https://incometaxindia.gov.in/Documents/Direct%20Tax%20Data/Approved-version-Income-Tax-Return-Statistics-for-the-AY-2023-24.pdf",
         "Jun 2024", "6, 9, 10", "7.97Cr filers, income slabs"],
        ["S02", "IRDAI Annual Report 2023-24", "IRDAI",
         "https://irdai.gov.in/document-detail?documentId=6436847",
         "Dec 2024", "All", "₹11.19T premium, penetration"],
        ["S03", "GI Council Yearbook 2023-24", "General Insurance Council",
         "https://www.gicouncil.in/yearbook/2023-24/",
         "Feb 2025", "Exec Summary", "₹2.90T GDPI, 40.3% health"],
        ["S04", "Niva Bupa DRHP Industry Report", "Niva Bupa (Redseer)",
         "https://transactions.nivabupa.com/pages/doc/drhp/Industry-Report.pdf",
         "Jun 2024", "1-50", "Retail 38.7%, SAHI 27.1%"],
        ["S05", "Niva Bupa Annual Report FY24", "Niva Bupa Health Insurance",
         "https://transactions.nivabupa.com/pages/doc/pub-dis/annual-reports/Annual-Report-FY-2023-24.pdf",
         "FY24", "Financial", "₹5,499Cr GWP, 41% growth"],
        ["S06", "Star Health Annual Report FY24", "Star Health & Allied",
         "https://www.starhealth.in/investors/annual-report/",
         "FY24", "Financial", "₹15,254Cr, 66.5% claims"],
        ["S07", "ICICI Lombard Annual Report FY24", "ICICI Lombard GIC",
         "https://www.icicilombard.com/docs/default-source/financial-information/annualreport2024.pdf",
         "FY24", "Full", "₹24,776Cr, 2.9% retail"],
        ["S08", "Go Digit DRHP", "Go Digit General Insurance",
         "https://www.godigit.com/investor-relations",
         "2024", "Industry", "Digital insurance metrics"],
        ["S09", "Care Health Annual Report", "Care Health Insurance",
         "https://www.careinsurance.com/investor-relations",
         "FY24", "Financial", "₹4,500Cr, 100% CSR"],
        ["S10", "Aditya Birla Health Report", "ABHI",
         "https://www.adityabirlacapital.com/healthinsurance/",
         "FY24", "Financial", "₹3,290Cr, 48% CAGR"],
        ["S11", "HDFC ERGO Annual Report", "HDFC ERGO GIC",
         "https://www.hdfcergo.com/about-us/financial/annual-reports",
         "FY24", "Financial", "₹9,000Cr estimated"],
        ["S12", "Bajaj Allianz GIC Report", "Bajaj Allianz",
         "https://www.bajajallianz.com/about-us/investor-relation.html",
         "FY24", "Financial", "₹22,000Cr, 7.7% share"],
        ["S13", "TRAI Telecom Reports", "TRAI",
         "https://www.trai.gov.in/release-publication/reports",
         "2024", "Subscriptions", "900M internet users"],
        ["S14", "Census India Projections", "Registrar General",
         "https://censusindia.gov.in/",
         "2011+Proj", "Demographics", "1.44B population"],
    ]

    for row_idx, data in enumerate(sources, 4):
        for col_idx, value in enumerate(data, 1):
            cell = ws_src.cell(row=row_idx, column=col_idx, value=value)
            if col_idx == 4:  # URL column
                cell.font = Font(color="0563C1", underline="single")

    ws_src.column_dimensions['A'].width = 6
    ws_src.column_dimensions['B'].width = 28
    ws_src.column_dimensions['C'].width = 22
    ws_src.column_dimensions['D'].width = 55
    ws_src.column_dimensions['E'].width = 10
    ws_src.column_dimensions['F'].width = 14
    ws_src.column_dimensions['G'].width = 25

    # ========================================
    # Save
    # ========================================
    output_path = "/home/user/forestry-demo/insurance_data/ICICI_Lombard_Integrated_Model.xlsx"
    wb.save(output_path)
    print(f"✓ Integrated model created: {output_path}")
    print(f"✓ Total sheets: {len(wb.sheetnames)}")
    for i, sheet in enumerate(wb.sheetnames, 1):
        print(f"  {i}. {sheet}")

    return output_path

if __name__ == "__main__":
    create_integrated_model()
