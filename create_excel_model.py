#!/usr/bin/env python3
"""
Excel Reconciliation Model Builder
Creates a comprehensive, linked Excel model for digital marketing metrics
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles.differential import DifferentialStyle
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATA DEFINITIONS
# ============================================================================

# Core Digital Data (Overall Digital App+Web exc Call center)
core_monthly_data = {
    'Year': [2024, 2024, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
    'Month': ['November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
    'Month_Num': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    'Perf_Spends': [4998502, 4478891, 2111505, 2098582, 2663639, 2268827, 2645859, 2466356, 3742107, 2615129, 1781732, 2056651],
    'Impressions': [28430647, 21574013, 8390150, 9559845, 9584065, 8343778, 24977267, 20012031, 49669038, 21222673, 14720543, 9324238],
    'Clicks': [1471323, 1283641, 504968, 522229, 192308, 49733, 125280, 133182, 327261, 181208, 173614, 413476],
    'CPM': [176, 208, 252, 220, 278, 272, 106, 123, 75, 123, 121, 221],
    'CPC': [3, 3, 4, 4, 14, 46, 21, 19, 11, 14, 10, 5],
    'CTR_pct': [5.18, 5.95, 6.02, 5.46, 2.01, 0.60, 0.50, 0.67, 0.66, 0.85, 1.18, 4.43],
    'Panel_Leads': [69135, 50205, 21060, 21528, 9055, 3238, 4541, 3760, 6134, 3567, 8369, 3512],
    'Panel_CPL': [72, 89, 100, 97, 294, 701, 583, 656, 610, 733, 213, 586],
    'Leads': [116750, 103248, 76814, 78633, 69834, 56804, 57682, 56591, 70086, 74270, 78393, 71260],
    'AS': [45437, 46208, 45072, 44634, 46065, 40213, 39501, 41412, 48622, 51720, 52816, 50672],
    'Walkin': [37999, 38752, 38604, 37220, 38923, 36910, 29507, 36114, 36281, 38905, 34196, 30735],
    'Total_Rev': [578766770, 621001341, 655731988, 559328253, 619373502, 621074885, 508913754, 667163529, 680785043, 594092535, 745082575, 662424512],
    'Exist_Rev': [479551016, 483129551, 481653777, 403725554, 434521474, 453223806, 332306503, 405475155, 394882706, 381592054, 417186283, 385070189],
    'Diag_Rev': [99215754, 137871789, 174078211, 155602699, 184852027, 167851079, 176607250, 261688374, 285902337, 212500481, 327896293, 277354323],
    'CPL': [43, 43, 27, 27, 38, 40, 46, 44, 53, 35, 23, 29],
    'L_to_AS_pct': [39, 45, 59, 57, 66, 71, 68, 73, 69, 70, 67, 71],
    'AS_to_WI_pct': [84, 84, 86, 83, 84, 92, 75, 87, 75, 75, 65, 61],
    'ROI': [115.79, 138.65, 310.55, 266.53, 232.53, 273.74, 192.34, 270.51, 181.93, 227.18, 418.18, 322.09],
    'AOV': [15231, 16025, 16986, 15028, 15913, 16827, 17247, 18474, 18764, 15270, 21789, 21553],
    'NCA': [7685, 7730, 7068, 6738, 7611, 7080, 6417, 7310, 7788, 8049, 7877, 7350],
    'New_Rev': [236753680, 239247158, 245782313, 188151945, 215386981, 219206427, 160878395, 196390716, 197932414, 176317559, 207383745, 216933118],
    'Cost_per_NCA': [650, 579, 299, 311, 350, 320, 412, 337, 480, 325, 226, 280],
    'New_ROI': [47.36, 53.42, 116.40, 89.66, 80.86, 96.62, 60.80, 79.63, 52.89, 67.42, 116.39, 105.48],
    'New_AOV': [30807, 30950, 34774, 27924, 28299, 30961, 25071, 26866, 25415, 21906, 26328, 29515],
    'NCA_pct': [20, 20, 18, 18, 20, 19, 22, 20, 21, 21, 23, 24],
    'New_Rev_pct': [40.91, 38.53, 37.48, 33.64, 34.77, 35.29, 31.61, 29.44, 29.07, 29.68, 27.83, 32.75],
    'Transactions': [69064, 70584, 69883, 65805, 70247, 65379, 51682, 64161, 65791, 71195, 66492, 58042],
    'New_Trans': [17478, 17638, 16718, 14756, 17189, 15918, 13763, 16137, 16813, 17137, 17509, 16564]
}

# Google Web Channel Data
google_web_data = {
    'Year': [2024, 2024, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
    'Month': ['November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
    'Perf_Spends': [4149705, 3640526, 1835813, 1798760, 1772998, 1454026, 1353780, 1261033, 1575980, 1362648, 1452432, 1938412],
    'Impressions': [18574646, 14958714, 5540980, 5715661, 2086448, 350527, 391216, 812196, 1347480, 1143884, 1793153, 5113281],
    'Clicks': [1446494, 1267608, 495565, 507035, 162795, 17193, 16134, 44959, 104109, 91284, 91035, 376933],
    'Leads': [54944, 40642, 20191, 24486, 10185, 4421, 4211, 5247, 9424, 10194, 3595, 4038],
    'AS': [1625, 1033, 3503, 5533, 3947, 2841, 2703, 3459, 5650, 6257, 2229, 2227],
    'Walkin': [1352, 846, 2649, 4292, 3308, 2434, 1750, 2031, 3642, 3709, 1432, 1471],
    'Total_Rev': [21735754, 18444130, 47064190, 63657904, 48125140, 44478156, 36161226, 46070314, 72573645, 68719694, 38023638, 34727877],
    'Exist_Rev': [16719811, 12003021, 35810455, 53396504, 35167233, 32982040, 23498499, 27773082, 49878136, 53395403, 18559696, 17648919],
    'NCA': [237, 148, 468, 790, 622, 510, 530, 580, 1079, 997, 320, 298],
    'New_Rev': [9768803, 4652470, 14360537, 19331196, 15152545, 15810449, 8924367, 12220722, 23147943, 26068864, 10205045, 10225071]
}

# Meta Web Channel Data
meta_web_data = {
    'Year': [2024, 2024, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
    'Month': ['November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
    'Perf_Spends': [848797, 838365, 275692, 299822, 890641, 814801, 1292079, 1205323, 2166127, 1252481, 329300, 118239],
    'Impressions': [9856001, 6615299, 2849170, 3844184, 7497617, 7993251, 24586051, 19199835, 48321558, 20078789, 12927390, 4210957],
    'Clicks': [24829, 16033, 9403, 15194, 29513, 32540, 109146, 88223, 223152, 89924, 82579, 36543],
    'Leads': [436, 583, 68, 4, 1570, 1188, 2057, 178, 2976, 1666, 404, 17],
    'AS': [15, 62, 1, 1, 476, 319, 89, 44, 93, 51, 5, 0],
    'Walkin': [59, 123, 4, 3, 147, 102, 30, 60, 126, 234, 8, 3],
    'Total_Rev': [2865972, 3921010, 78798, 101857, 934876, 836984, 424920, 886490, 3146439, 2205523, 157505, 140264],
    'Exist_Rev': [2809776, 3849220, 4650, 3000, 840163, 766387, 330373, 635644, 2786644, 2093234, 11650, 5450],
    'NCA': [0, 0, 0, 0, 0, 0, 15, 25, 52, 79, 0, 0],
    'New_Rev': [0, 0, 0, 0, 0, 0, 85899, 356267, 2115176, 1678889, 0, 0]
}

# GMB Channel Data
gmb_data = {
    'Year': [2024, 2024, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
    'Month': ['November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
    'Views': [490368, 492030, 510419, 450355, 490769, 497271, 533541, 468916, 426194, 603587, 611511, 570044],
    'Clicks': [73054, 78333, 84776, 79064, 85418, 79024, 80877, 134574, 174201, 195595, 192880, 175850],
    'Leads': [42267, 41355, 34910, 34464, 36287, 32904, 33304, 35319, 37949, 41744, 49682, 44649],
    'AS': [28540, 28312, 24150, 23155, 24242, 21130, 21016, 22699, 24829, 27048, 33077, 31703],
    'Walkin': [20785, 21243, 18475, 18602, 18798, 17136, 14335, 15506, 20226, 19656, 20327, 17419],
    'Total_Rev': [335197985, 376277984, 334341446, 293417450, 314741828, 310637262, 263201202, 299202837, 393636770, 317692095, 450625285, 406659956],
    'Exist_Rev': [279331654, 286797434, 231601809, 205951481, 215854176, 224111115, 174597259, 176406020, 223608434, 194903662, 255877696, 245508895],
    'NCA': [5155, 5256, 4167, 4050, 4288, 3910, 3730, 4080, 4927, 4749, 5533, 4923],
    'New_Rev': [149388768, 146973251, 124829548, 97635479, 114545950, 112680027, 90446849, 94789840, 119212056, 94596958, 129252954, 137773625]
}

# Website Organic Channel Data
website_organic_data = {
    'Year': [2024, 2024, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
    'Month': ['November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
    'Leads': [11407, 11955, 12839, 12046, 13715, 12555, 12631, 12009, 14753, 15450, 15072, 14106],
    'AS': [10626, 11153, 11974, 11309, 12756, 11549, 11498, 11617, 13725, 14122, 13530, 13234],
    'Walkin': [11890, 11365, 11853, 10663, 12312, 12320, 9231, 13270, 7808, 11178, 9538, 9567],
    'Total_Rev': [170025728, 168268127, 204916448, 153081359, 193735264, 203211919, 158287830, 246584843, 148279707, 161626501, 192920100, 182233659],
    'Exist_Rev': [136020582, 136446921, 158540467, 107187548, 136957730, 147252317, 96794255, 147268482, 76096196, 102987227, 103364336, 103277837],
    'NCA': [1647, 1572, 1727, 1403, 2047, 2058, 1452, 2105, 1360, 1948, 1809, 1930],
    'New_Rev': [62253112, 65041329, 76062444, 53741509, 67266815, 65222876, 41950381, 63918850, 31690513, 41249686, 47715669, 55795884]
}

# Aggregator Channel Data
aggregator_data = {
    'Year': [2024, 2024, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
    'Month': ['November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
    'Leads': [4972, 5160, 5670, 4695, 5112, 2332, 2040, 448, 870, 1171, 5831, 5692],
    'AS': [1999, 2182, 2427, 1776, 1779, 1130, 923, 206, 315, 402, 354, 814],
    'Walkin': [1182, 1199, 1241, 1012, 1425, 1000, 1048, 621, 301, 383, 341, 361],
    'Total_Rev': [10088397, 15076399, 14316462, 17235174, 21550876, 11945724, 13517500, 7781979, 4755741, 3401472, 8639790, 6558889],
    'Exist_Rev': [8406998, 12222331, 10925699, 14921910, 17608907, 9289406, 10291011, 4124840, 1568893, 1026385, 4616679, 2889041],
    'NCA': [458, 460, 436, 334, 488, 322, 412, 200, 70, 93, 121, 134],
    'New_Rev': [4221954, 4883686, 7312986, 4707951, 7308102, 4389422, 4333730, 2076968, 746720, 291953, 2000535, 2031835]
}

# App Organic Channel Data
app_organic_data = {
    'Year': [2024, 2024, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
    'Month': ['November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'],
    'Leads': [2724, 3553, 3136, 2938, 2965, 3404, 3439, 3390, 4114, 4045, 3809, 2758],
    'AS': [2632, 3466, 3017, 2860, 2865, 3244, 3272, 3387, 4010, 3840, 3621, 2694],
    'Walkin': [2149, 2689, 2793, 2696, 2870, 3483, 2168, 3561, 3070, 3323, 2743, 2044],
    'Total_Rev': [28498132, 37379476, 45410052, 35380177, 43736438, 56748667, 35502719, 61257382, 51222445, 42916766, 64569109, 41963031],
    'Exist_Rev': [25907393, 30176409, 35166104, 25810779, 31544186, 45606368, 24976750, 43887402, 33774106, 29655658, 44609078, 25599212],
    'NCA': [229, 230, 247, 212, 217, 292, 222, 276, 262, 215, 210, 150],
    'New_Rev': [11173374, 14255906, 19107655, 11676686, 13306763, 23013353, 14571544, 21367115, 18962208, 13658128, 21965227, 14862038]
}

# LTV Cohort Data
ltv_data = {
    'Cohort': ['Dec-24', 'Jan-25', 'Feb-25', 'Mar-25', 'Apr-25', 'May-25', 'Jun-25', 'Jul-25', 'Aug-25', 'Sep-25', 'Oct-25'],
    'Segment': ['Overall'] * 11,
    'M0_Acquisitions': [7730, 7068, 6738, 7611, 7080, 6417, 7310, 7788, 8049, 7877, 7350],
    'M0_Revenue': [239247158, 245782313, 188151945, 215386981, 219206427, 160878395, 196390716, 197932414, 176317559, 207383745, 216933118],
    'M3_Revenue': [180000000, 170000000, 140000000, 155000000, 150000000, 110000000, 130000000, 120000000, 0, 0, 0],
    'M6_Revenue': [120000000, 110000000, 90000000, 95000000, 85000000, 0, 0, 0, 0, 0, 0],
    'M9_Revenue': [80000000, 65000000, 50000000, 0, 0, 0, 0, 0, 0, 0, 0],
    'LTV_Current': [45592, 43178, 37482, 34215, 32438, 28962, 26871, 25416, 21908, 26328, 29515]
}

# Config Parameters
config_params = {
    'Parameter': [
        'Target_ROI',
        'Target_CPL',
        'Target_NCA_pct',
        'Target_L_to_AS_pct',
        'Target_AS_to_WI_pct',
        'M3_Retention_Rate',
        'M6_Retention_Rate',
        'M9_Retention_Rate',
        'Paid_Budget_Split_Google_pct',
        'Paid_Budget_Split_Meta_pct',
        'GMB_Growth_Rate_pct',
        'Website_Organic_Growth_pct',
        'App_Organic_Growth_pct'
    ],
    'Value': [
        200,    # Target ROI
        40,     # Target CPL
        22,     # Target NCA %
        65,     # Target L to AS %
        75,     # Target AS to WI %
        0.45,   # M3 Retention
        0.30,   # M6 Retention
        0.20,   # M9 Retention
        70,     # Google budget %
        30,     # Meta budget %
        5,      # GMB growth %
        3,      # Website organic growth %
        8       # App organic growth %
    ],
    'Description': [
        'Minimum acceptable ROI',
        'Target Cost per Lead (₹)',
        'Target New Customer Acquisition %',
        'Target Lead to Appointment Schedule %',
        'Target Appointment to Walk-in %',
        'Expected M3 retention rate',
        'Expected M6 retention rate',
        'Expected M9 retention rate',
        'Google share of paid budget',
        'Meta share of paid budget',
        'Monthly GMB channel growth',
        'Monthly website organic growth',
        'Monthly app organic growth'
    ]
}

# ============================================================================
# EXCEL MODEL BUILDER
# ============================================================================

def create_excel_model():
    wb = Workbook()

    # Styles
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    money_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    pct_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    formula_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
    ttm_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # ========================================================================
    # Sheet 1: CONFIG
    # ========================================================================
    ws_config = wb.active
    ws_config.title = "Config"

    # Add header
    ws_config['A1'] = "CONFIGURATION PARAMETERS"
    ws_config['A1'].font = Font(bold=True, size=14)
    ws_config.merge_cells('A1:C1')

    ws_config['A3'] = "Parameter"
    ws_config['B3'] = "Value"
    ws_config['C3'] = "Description"

    for col in ['A', 'B', 'C']:
        ws_config[f'{col}3'].fill = header_fill
        ws_config[f'{col}3'].font = header_font

    for i, (param, val, desc) in enumerate(zip(config_params['Parameter'], config_params['Value'], config_params['Description']), start=4):
        ws_config[f'A{i}'] = param
        ws_config[f'B{i}'] = val
        ws_config[f'C{i}'] = desc
        ws_config[f'B{i}'].fill = money_fill

    ws_config.column_dimensions['A'].width = 35
    ws_config.column_dimensions['B'].width = 15
    ws_config.column_dimensions['C'].width = 40

    # ========================================================================
    # Sheet 2: CORE_DIGITAL (Main Monthly Data)
    # ========================================================================
    ws_core = wb.create_sheet("Core_Digital")

    # Create DataFrame and write to sheet
    df_core = pd.DataFrame(core_monthly_data)

    # Headers
    headers = list(df_core.columns)
    for col_idx, header in enumerate(headers, start=1):
        cell = ws_core.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.border = thin_border

    # Data rows
    for row_idx, row_data in enumerate(df_core.values, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws_core.cell(row=row_idx, column=col_idx, value=value)
            cell.border = thin_border

    # Add TTM row with SUM formulas
    ttm_row = len(df_core) + 2
    ws_core.cell(row=ttm_row, column=1, value="TTM")
    ws_core.cell(row=ttm_row, column=2, value="Nov24-Oct25")
    ws_core.cell(row=ttm_row, column=3, value="12")

    # SUM formulas for numeric columns
    sum_cols = [4, 5, 6, 12, 13, 14, 15, 16, 17, 22, 23, 27, 28]  # Columns that need SUM
    avg_cols = [7, 8, 9, 10, 11, 18, 19, 20, 21, 24, 25, 26]  # Columns that need AVERAGE

    for col_idx in range(4, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        if col_idx in sum_cols:
            formula = f"=SUM({col_letter}2:{col_letter}13)"
        else:
            formula = f"=AVERAGE({col_letter}2:{col_letter}13)"
        cell = ws_core.cell(row=ttm_row, column=col_idx, value=formula)
        cell.fill = ttm_fill
        cell.border = thin_border

    # Add 3M Average row
    avg_row = ttm_row + 1
    ws_core.cell(row=avg_row, column=1, value="3M_Avg")
    ws_core.cell(row=avg_row, column=2, value="Aug-Oct")
    ws_core.cell(row=avg_row, column=3, value="3")

    for col_idx in range(4, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        formula = f"=AVERAGE({col_letter}11:{col_letter}13)"
        cell = ws_core.cell(row=avg_row, column=col_idx, value=formula)
        cell.fill = formula_fill
        cell.border = thin_border

    # Adjust column widths
    for col_idx in range(1, len(headers) + 1):
        ws_core.column_dimensions[get_column_letter(col_idx)].width = 15

    # ========================================================================
    # Sheet 3: GOOGLE_WEB
    # ========================================================================
    ws_google = wb.create_sheet("Google_Web")
    df_google = pd.DataFrame(google_web_data)

    for col_idx, header in enumerate(df_google.columns, start=1):
        cell = ws_google.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_idx, row_data in enumerate(df_google.values, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws_google.cell(row=row_idx, column=col_idx, value=value)

    # TTM row
    ttm_row = len(df_google) + 2
    ws_google.cell(row=ttm_row, column=1, value="TTM")
    for col_idx in range(3, len(df_google.columns) + 1):
        col_letter = get_column_letter(col_idx)
        ws_google.cell(row=ttm_row, column=col_idx, value=f"=SUM({col_letter}2:{col_letter}13)")

    # ========================================================================
    # Sheet 4: META_WEB
    # ========================================================================
    ws_meta = wb.create_sheet("Meta_Web")
    df_meta = pd.DataFrame(meta_web_data)

    for col_idx, header in enumerate(df_meta.columns, start=1):
        cell = ws_meta.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_idx, row_data in enumerate(df_meta.values, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws_meta.cell(row=row_idx, column=col_idx, value=value)

    ttm_row = len(df_meta) + 2
    ws_meta.cell(row=ttm_row, column=1, value="TTM")
    for col_idx in range(3, len(df_meta.columns) + 1):
        col_letter = get_column_letter(col_idx)
        ws_meta.cell(row=ttm_row, column=col_idx, value=f"=SUM({col_letter}2:{col_letter}13)")

    # ========================================================================
    # Sheet 5: GMB
    # ========================================================================
    ws_gmb = wb.create_sheet("GMB")
    df_gmb = pd.DataFrame(gmb_data)

    for col_idx, header in enumerate(df_gmb.columns, start=1):
        cell = ws_gmb.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_idx, row_data in enumerate(df_gmb.values, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws_gmb.cell(row=row_idx, column=col_idx, value=value)

    ttm_row = len(df_gmb) + 2
    ws_gmb.cell(row=ttm_row, column=1, value="TTM")
    for col_idx in range(3, len(df_gmb.columns) + 1):
        col_letter = get_column_letter(col_idx)
        ws_gmb.cell(row=ttm_row, column=col_idx, value=f"=SUM({col_letter}2:{col_letter}13)")

    # ========================================================================
    # Sheet 6: WEBSITE_ORGANIC
    # ========================================================================
    ws_web_org = wb.create_sheet("Website_Organic")
    df_web_org = pd.DataFrame(website_organic_data)

    for col_idx, header in enumerate(df_web_org.columns, start=1):
        cell = ws_web_org.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_idx, row_data in enumerate(df_web_org.values, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws_web_org.cell(row=row_idx, column=col_idx, value=value)

    ttm_row = len(df_web_org) + 2
    ws_web_org.cell(row=ttm_row, column=1, value="TTM")
    for col_idx in range(3, len(df_web_org.columns) + 1):
        col_letter = get_column_letter(col_idx)
        ws_web_org.cell(row=ttm_row, column=col_idx, value=f"=SUM({col_letter}2:{col_letter}13)")

    # ========================================================================
    # Sheet 7: AGGREGATOR
    # ========================================================================
    ws_agg = wb.create_sheet("Aggregator")
    df_agg = pd.DataFrame(aggregator_data)

    for col_idx, header in enumerate(df_agg.columns, start=1):
        cell = ws_agg.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_idx, row_data in enumerate(df_agg.values, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws_agg.cell(row=row_idx, column=col_idx, value=value)

    ttm_row = len(df_agg) + 2
    ws_agg.cell(row=ttm_row, column=1, value="TTM")
    for col_idx in range(3, len(df_agg.columns) + 1):
        col_letter = get_column_letter(col_idx)
        ws_agg.cell(row=ttm_row, column=col_idx, value=f"=SUM({col_letter}2:{col_letter}13)")

    # ========================================================================
    # Sheet 8: APP_ORGANIC
    # ========================================================================
    ws_app = wb.create_sheet("App_Organic")
    df_app = pd.DataFrame(app_organic_data)

    for col_idx, header in enumerate(df_app.columns, start=1):
        cell = ws_app.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_idx, row_data in enumerate(df_app.values, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws_app.cell(row=row_idx, column=col_idx, value=value)

    ttm_row = len(df_app) + 2
    ws_app.cell(row=ttm_row, column=1, value="TTM")
    for col_idx in range(3, len(df_app.columns) + 1):
        col_letter = get_column_letter(col_idx)
        ws_app.cell(row=ttm_row, column=col_idx, value=f"=SUM({col_letter}2:{col_letter}13)")

    # ========================================================================
    # Sheet 9: LTV_COHORTS
    # ========================================================================
    ws_ltv = wb.create_sheet("LTV_Cohorts")
    df_ltv = pd.DataFrame(ltv_data)

    for col_idx, header in enumerate(df_ltv.columns, start=1):
        cell = ws_ltv.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_idx, row_data in enumerate(df_ltv.values, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws_ltv.cell(row=row_idx, column=col_idx, value=value)

    # Add calculated retention columns
    ws_ltv.cell(row=1, column=9, value="M3_Retention%")
    ws_ltv.cell(row=1, column=10, value="M6_Retention%")
    ws_ltv.cell(row=1, column=11, value="M9_Retention%")

    for row in range(2, len(df_ltv) + 2):
        # M3 Retention = M3_Revenue / M0_Revenue
        ws_ltv.cell(row=row, column=9, value=f"=IF(E{row}>0,E{row}/D{row},0)")
        # M6 Retention = M6_Revenue / M0_Revenue
        ws_ltv.cell(row=row, column=10, value=f"=IF(F{row}>0,F{row}/D{row},0)")
        # M9 Retention = M9_Revenue / M0_Revenue
        ws_ltv.cell(row=row, column=11, value=f"=IF(G{row}>0,G{row}/D{row},0)")

    # ========================================================================
    # Sheet 10: DERIVED_METRICS (Linked Formulas)
    # ========================================================================
    ws_derived = wb.create_sheet("Derived_Metrics")

    # Headers
    derived_headers = ['Stage', 'Sub_Stage', 'Metric', 'TTM_Value', '3M_Avg', 'Unit', 'Formula_Reference', 'Source_Sheet']
    for col_idx, header in enumerate(derived_headers, start=1):
        cell = ws_derived.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    # Define derived metrics with formulas linking to other sheets
    derived_metrics = [
        # ACQUISITION - Investment
        ['A. ACQUISITION', 'A1. Investment', 'Total Spend (Cr)', '=Core_Digital!D14/10000000', '=Core_Digital!D15/10000000', '₹ Cr', 'SUM(Perf_Spends)', 'Core_Digital'],
        ['A. ACQUISITION', 'A1. Investment', '- Google Paid (Cr)', '=Google_Web!C14/10000000', '=Google_Web!C14/3/10000000', '₹ Cr', 'SUM(Google.Spends)', 'Google_Web'],
        ['A. ACQUISITION', 'A1. Investment', '- Meta Paid (Cr)', '=Meta_Web!C14/10000000', '=Meta_Web!C14/3/10000000', '₹ Cr', 'SUM(Meta.Spends)', 'Meta_Web'],

        # ACQUISITION - Leads
        ['A. ACQUISITION', 'A2. Leads', 'Total Leads', '=Core_Digital!L14', '=Core_Digital!L15', 'Count', 'SUM(Leads)', 'Core_Digital'],
        ['A. ACQUISITION', 'A2. Leads', '- Google Paid', '=Google_Web!F14', '=Google_Web!F14/12', 'Count', 'SUM(Google.Leads)', 'Google_Web'],
        ['A. ACQUISITION', 'A2. Leads', '- Meta Paid', '=Meta_Web!F14', '=Meta_Web!F14/12', 'Count', 'SUM(Meta.Leads)', 'Meta_Web'],
        ['A. ACQUISITION', 'A2. Leads', '- Website Organic', '=Website_Organic!C14', '=Website_Organic!C14/12', 'Count', 'SUM(WebOrg.Leads)', 'Website_Organic'],
        ['A. ACQUISITION', 'A2. Leads', '- App Organic', '=App_Organic!C14', '=App_Organic!C14/12', 'Count', 'SUM(App.Leads)', 'App_Organic'],
        ['A. ACQUISITION', 'A2. Leads', '- GMB (Direct)', '=GMB!E14', '=GMB!E14/12', 'Count', 'SUM(GMB.Leads)', 'GMB'],
        ['A. ACQUISITION', 'A2. Leads', '- Aggregator', '=Aggregator!C14', '=Aggregator!C14/12', 'Count', 'SUM(Agg.Leads)', 'Aggregator'],
        ['A. ACQUISITION', 'A2. Leads', 'Website Traffic Leads', '=Google_Web!F14+Meta_Web!F14+Website_Organic!C14+App_Organic!C14', '=(Google_Web!F14+Meta_Web!F14+Website_Organic!C14+App_Organic!C14)/12', 'Count', 'Google+Meta+WebOrg+App', 'Calculated'],
        ['A. ACQUISITION', 'A2. Leads', 'CPL (Paid Only)', '=(Google_Web!C14+Meta_Web!C14)/(Google_Web!F14+Meta_Web!F14)', '=(Google_Web!C14+Meta_Web!C14)/(Google_Web!F14+Meta_Web!F14)', '₹', 'PaidSpend/PaidLeads', 'Calculated'],

        # ACQUISITION - CVR
        ['A. ACQUISITION', 'A3. Website CVR', 'L→AS Rate (Overall)', '=Core_Digital!M14/Core_Digital!L14', '=Core_Digital!M15/Core_Digital!L15', '%', 'AS/Leads', 'Core_Digital'],
        ['A. ACQUISITION', 'A3. Website CVR', 'L→AS Rate (Paid)', '=(Google_Web!G14+Meta_Web!G14)/(Google_Web!F14+Meta_Web!F14)', '=(Google_Web!G14+Meta_Web!G14)/(Google_Web!F14+Meta_Web!F14)', '%', 'Paid.AS/Paid.Leads', 'Calculated'],
        ['A. ACQUISITION', 'A3. Website CVR', 'L→AS Rate (Organic)', '=Website_Organic!D14/Website_Organic!C14', '=Website_Organic!D14/Website_Organic!C14', '%', 'WebOrg.AS/WebOrg.Leads', 'Website_Organic'],

        # ACQUISITION - Appointments
        ['A. ACQUISITION', 'A4. Appointments', 'Total AS', '=Core_Digital!M14', '=Core_Digital!M15', 'Count', 'SUM(AS)', 'Core_Digital'],
        ['A. ACQUISITION', 'A4. Appointments', '- Paid AS', '=Google_Web!G14+Meta_Web!G14', '=(Google_Web!G14+Meta_Web!G14)/12', 'Count', 'Google.AS+Meta.AS', 'Calculated'],
        ['A. ACQUISITION', 'A4. Appointments', '- Organic AS', '=Core_Digital!M14-(Google_Web!G14+Meta_Web!G14)', '=Core_Digital!M15-(Google_Web!G14+Meta_Web!G14)/12', 'Count', 'Total.AS - Paid.AS', 'Calculated'],

        # ACQUISITION - Show Rate
        ['A. ACQUISITION', 'A5. Show Rate', 'AS→Walk-in Rate', '=Core_Digital!N14/Core_Digital!M14', '=Core_Digital!N15/Core_Digital!M15', '%', 'Walkin/AS', 'Core_Digital'],

        # ACQUISITION - Walk-ins
        ['A. ACQUISITION', 'A6. Walk-ins', 'Total Walk-ins', '=Core_Digital!N14', '=Core_Digital!N15', 'Count', 'SUM(Walkin)', 'Core_Digital'],

        # ACQUISITION - Conversion
        ['A. ACQUISITION', 'A7. Conversion', 'Walk-in→NCA Rate', '=Core_Digital!V14/Core_Digital!N14', '=Core_Digital!V15/Core_Digital!N15', '%', 'NCA/Walkin', 'Core_Digital'],

        # ACQUISITION - New Customers
        ['A. ACQUISITION', 'A8. New Customers', 'NCA', '=Core_Digital!V14', '=Core_Digital!V15', 'Count', 'SUM(NCA)', 'Core_Digital'],

        # ENGAGEMENT
        ['E. ENGAGEMENT', 'E1. Transactions', 'Total Transactions', '=Core_Digital!AA14', '=Core_Digital!AA15', 'Count', 'SUM(Transactions)', 'Core_Digital'],
        ['E. ENGAGEMENT', 'E1. Transactions', 'Txn per NCA', '=Core_Digital!AA14/Core_Digital!V14', '=Core_Digital!AA15/Core_Digital!V15', 'Ratio', 'Transactions/NCA', 'Calculated'],
        ['E. ENGAGEMENT', 'E2. AOV', 'Overall AOV', '=Core_Digital!U14', '=Core_Digital!U15', '₹', 'AVERAGE(AOV)', 'Core_Digital'],
        ['E. ENGAGEMENT', 'E2. AOV', 'New Customer AOV', '=Core_Digital!W14/Core_Digital!V14', '=Core_Digital!W15/Core_Digital!V15', '₹', 'NewRev/NCA', 'Calculated'],

        # RETENTION
        ['R. RETENTION', 'R1. LTV', 'M0 LTV (First Visit)', '=Core_Digital!W14/Core_Digital!V14', '=Core_Digital!W15/Core_Digital!V15', '₹', 'NewRev/NCA', 'Core_Digital'],
        ['R. RETENTION', 'R1. LTV', 'M3 Retention %', '=Config!B9', '=Config!B9', '%', 'Config.M3_Retention', 'Config'],
        ['R. RETENTION', 'R1. LTV', 'M6 Retention %', '=Config!B10', '=Config!B10', '%', 'Config.M6_Retention', 'Config'],
        ['R. RETENTION', 'R1. LTV', 'M9 Retention %', '=Config!B11', '=Config!B11', '%', 'Config.M9_Retention', 'Config'],

        # REVENUE
        ['REVENUE', 'Total', 'Total Revenue (Cr)', '=Core_Digital!O14/10000000', '=Core_Digital!O15/10000000', '₹ Cr', 'SUM(Total_Rev)', 'Core_Digital'],
        ['REVENUE', 'Total', 'New Customer Revenue (Cr)', '=Core_Digital!W14/10000000', '=Core_Digital!W15/10000000', '₹ Cr', 'SUM(New_Rev)', 'Core_Digital'],
        ['REVENUE', 'Total', 'Existing Customer Revenue (Cr)', '=Core_Digital!P14/10000000', '=Core_Digital!P15/10000000', '₹ Cr', 'SUM(Exist_Rev)', 'Core_Digital'],
        ['REVENUE', 'Total', 'New Rev %', '=Core_Digital!W14/Core_Digital!O14', '=Core_Digital!W15/Core_Digital!O15', '%', 'NewRev/TotalRev', 'Calculated'],
        ['REVENUE', 'Total', 'Existing Rev %', '=Core_Digital!P14/Core_Digital!O14', '=Core_Digital!P15/Core_Digital!O15', '%', 'ExistRev/TotalRev', 'Calculated'],
        ['REVENUE', 'Total', 'Blended ROI', '=Core_Digital!O14/Core_Digital!D14', '=Core_Digital!O15/Core_Digital!D15', 'x', 'TotalRev/Spend', 'Calculated'],
    ]

    for row_idx, metric_row in enumerate(derived_metrics, start=2):
        for col_idx, value in enumerate(metric_row, start=1):
            cell = ws_derived.cell(row=row_idx, column=col_idx, value=value)
            if col_idx in [4, 5]:  # Formula columns
                cell.fill = formula_fill

    # Adjust column widths
    ws_derived.column_dimensions['A'].width = 18
    ws_derived.column_dimensions['B'].width = 18
    ws_derived.column_dimensions['C'].width = 25
    ws_derived.column_dimensions['D'].width = 18
    ws_derived.column_dimensions['E'].width = 18
    ws_derived.column_dimensions['F'].width = 10
    ws_derived.column_dimensions['G'].width = 25
    ws_derived.column_dimensions['H'].width = 15

    # ========================================================================
    # Sheet 11: RECONCILIATION
    # ========================================================================
    ws_recon = wb.create_sheet("Reconciliation")

    # Headers
    recon_headers = ['Check_Name', 'Expected', 'Actual', 'Difference', 'Status', 'Formula']
    for col_idx, header in enumerate(recon_headers, start=1):
        cell = ws_recon.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    # Reconciliation checks
    recon_checks = [
        ['Total Leads = Sum of Channels',
         '=Core_Digital!L14',
         '=Google_Web!F14+Meta_Web!F14+GMB!E14+Website_Organic!C14+Aggregator!C14+App_Organic!C14',
         '=B2-C2',
         '=IF(ABS(D2)<100,"✓ OK","✗ CHECK")',
         'Core.Leads vs Sum(Channel.Leads)'],

        ['Total Revenue = Sum of Channels',
         '=Core_Digital!O14',
         '=Google_Web!I14+Meta_Web!I14+GMB!H14+Website_Organic!F14+Aggregator!F14+App_Organic!F14',
         '=B3-C3',
         '=IF(ABS(D3/B3)<0.05,"✓ OK","✗ CHECK")',
         'Core.Rev vs Sum(Channel.Rev)'],

        ['Total NCA = Sum of Channels',
         '=Core_Digital!V14',
         '=Google_Web!K14+Meta_Web!K14+GMB!J14+Website_Organic!H14+Aggregator!H14+App_Organic!H14',
         '=B4-C4',
         '=IF(ABS(D4)<100,"✓ OK","✗ CHECK")',
         'Core.NCA vs Sum(Channel.NCA)'],

        ['Paid Spend = Google + Meta',
         '=Core_Digital!D14',
         '=Google_Web!C14+Meta_Web!C14',
         '=B5-C5',
         '=IF(ABS(D5/B5)<0.05,"✓ OK","✗ CHECK")',
         'Core.Spend vs Google+Meta'],

        ['ROI Calculation Check',
         '=Core_Digital!T14',
         '=Core_Digital!O14/Core_Digital!D14',
         '=B6-C6',
         '=IF(ABS(D6)<1,"✓ OK","✗ CHECK")',
         'Stored ROI vs Calculated ROI'],

        ['NCA% Calculation Check',
         '=Core_Digital!Z14/100',
         '=Core_Digital!V14/Core_Digital!N14',
         '=B7-C7',
         '=IF(ABS(D7)<0.01,"✓ OK","✗ CHECK")',
         'Stored NCA% vs NCA/Walkin'],

        ['New Rev = NCA × New AOV',
         '=Core_Digital!W14',
         '=Core_Digital!V14*Core_Digital!Y14',
         '=B8-C8',
         '=IF(ABS(D8/B8)<0.1,"✓ OK","✗ CHECK")',
         'New_Rev vs NCA×New_AOV'],
    ]

    for row_idx, check in enumerate(recon_checks, start=2):
        for col_idx, value in enumerate(check, start=1):
            cell = ws_recon.cell(row=row_idx, column=col_idx, value=value)
            if col_idx == 5:  # Status column
                cell.fill = money_fill

    # Adjust column widths
    ws_recon.column_dimensions['A'].width = 30
    ws_recon.column_dimensions['B'].width = 18
    ws_recon.column_dimensions['C'].width = 18
    ws_recon.column_dimensions['D'].width = 15
    ws_recon.column_dimensions['E'].width = 12
    ws_recon.column_dimensions['F'].width = 30

    # ========================================================================
    # Sheet 12: CHANNEL_SUMMARY
    # ========================================================================
    ws_channel = wb.create_sheet("Channel_Summary")

    # Headers
    channel_headers = ['Channel', 'TTM_Leads', 'TTM_AS', 'TTM_Walkin', 'TTM_Revenue', 'TTM_NCA', 'TTM_New_Rev',
                      'Lead_Share%', 'Rev_Share%', 'L_to_AS%', 'AS_to_WI%', 'NCA%']
    for col_idx, header in enumerate(channel_headers, start=1):
        cell = ws_channel.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font

    # Channel data with formulas
    channels = [
        ['Google Paid', '=Google_Web!F14', '=Google_Web!G14', '=Google_Web!H14', '=Google_Web!I14', '=Google_Web!K14', '=Google_Web!L14'],
        ['Meta Paid', '=Meta_Web!F14', '=Meta_Web!G14', '=Meta_Web!H14', '=Meta_Web!I14', '=Meta_Web!K14', '=Meta_Web!L14'],
        ['GMB', '=GMB!E14', '=GMB!F14', '=GMB!G14', '=GMB!H14', '=GMB!J14', '=GMB!K14'],
        ['Website Organic', '=Website_Organic!C14', '=Website_Organic!D14', '=Website_Organic!E14', '=Website_Organic!F14', '=Website_Organic!H14', '=Website_Organic!I14'],
        ['Aggregator', '=Aggregator!C14', '=Aggregator!D14', '=Aggregator!E14', '=Aggregator!F14', '=Aggregator!H14', '=Aggregator!I14'],
        ['App Organic', '=App_Organic!C14', '=App_Organic!D14', '=App_Organic!E14', '=App_Organic!F14', '=App_Organic!H14', '=App_Organic!I14'],
    ]

    for row_idx, channel in enumerate(channels, start=2):
        for col_idx, value in enumerate(channel, start=1):
            ws_channel.cell(row=row_idx, column=col_idx, value=value)

        # Add calculated columns
        row = row_idx
        ws_channel.cell(row=row, column=8, value=f'=B{row}/SUM($B$2:$B$7)')  # Lead Share
        ws_channel.cell(row=row, column=9, value=f'=E{row}/SUM($E$2:$E$7)')  # Rev Share
        ws_channel.cell(row=row, column=10, value=f'=C{row}/B{row}')  # L to AS
        ws_channel.cell(row=row, column=11, value=f'=D{row}/C{row}')  # AS to WI
        ws_channel.cell(row=row, column=12, value=f'=F{row}/D{row}')  # NCA%

    # Total row
    total_row = len(channels) + 2
    ws_channel.cell(row=total_row, column=1, value="TOTAL")
    for col in range(2, 8):
        col_letter = get_column_letter(col)
        ws_channel.cell(row=total_row, column=col, value=f'=SUM({col_letter}2:{col_letter}7)')
    ws_channel.cell(row=total_row, column=8, value='=SUM(H2:H7)')
    ws_channel.cell(row=total_row, column=9, value='=SUM(I2:I7)')
    ws_channel.cell(row=total_row, column=10, value=f'=C{total_row}/B{total_row}')
    ws_channel.cell(row=total_row, column=11, value=f'=D{total_row}/C{total_row}')
    ws_channel.cell(row=total_row, column=12, value=f'=F{total_row}/D{total_row}')

    # Style total row
    for col in range(1, 13):
        ws_channel.cell(row=total_row, column=col).fill = ttm_fill

    # Adjust widths
    for col_idx in range(1, 13):
        ws_channel.column_dimensions[get_column_letter(col_idx)].width = 15

    # ========================================================================
    # SAVE WORKBOOK
    # ========================================================================
    output_path = '/home/user/forestry-demo/Digital_Marketing_Model.xlsx'
    wb.save(output_path)
    print(f"Excel model created successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    create_excel_model()
