"""
general_report_engine.py — 100% Pixel-Perfect General Situation Report Generator
==================================================================================
Matches the official General Situation Report sample EXACTLY.

Based on official sample showing:
- Page 1: Header + Incidents by province
- Page 16: Case data table (28 rows)
- Page 17: Distribution list
"""

import os
import re
from datetime import datetime

# 100% PIXEL-PERFECT TEMPLATE FOR GENERAL SITUATION REPORT
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>General Situation Report</title>
    <style>
        @page { size: A4; margin: 25mm 25mm 20mm 25mm; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Times New Roman', Times, serif; 
            margin: 0; 
            padding: 0; 
            background: #ffffff; 
            color: #000000; 
            font-size: 11pt; 
            line-height: 1.15; 
        }
        .page { 
            width: 210mm; 
            min-height: 297mm; 
            padding: 25mm 25mm 20mm 25mm; 
            margin: 0 auto; 
            background: white; 
            position: relative; 
            box-sizing: border-box; 
        }
        
        /* PAGE NUMBER - Top right */
        .page-num { 
            text-align: right; 
            font-family: 'Times New Roman', Times, serif; 
            font-size: 11pt; 
            margin-bottom: 8mm; 
            font-weight: normal;
        }
        
        /* HEADER */
        .header { text-align: center; margin-bottom: 0; }
        .confidential { 
            font-weight: bold; 
            font-size: 14pt; 
            margin-bottom: 3mm; 
            text-align: center;
        }
        .logo { 
            width: 28mm; 
            height: auto; 
            margin: 0 auto 3mm auto; 
            display: block; 
        }
        .ig-address { 
            font-weight: bold; 
            font-size: 11pt; 
            margin-bottom: 0mm; 
            line-height: 1.2;
        }
        .ig-title { 
            font-weight: bold; 
            font-size: 11pt; 
            margin-bottom: 5mm; 
        }
        .report-title { 
            font-size: 18pt; 
            font-weight: bold; 
            margin: 3mm 0 2mm 0; 
            text-align: center; 
            letter-spacing: 0.3pt;
        }
        .date-range { 
            font-weight: bold; 
            font-size: 11pt; 
            text-decoration: underline; 
            margin-bottom: 5mm; 
            text-align: center; 
            display: block; 
        }
        sup { font-size: 0.7em; vertical-align: super; line-height: 0; }

        /* SECTION HEADERS */
        .section-header { 
            font-weight: bold; 
            font-size: 11pt; 
            margin-top: 3mm; 
            margin-bottom: 3mm; 
            text-align: left;
        }
        
        /* PROVINCE HEADING */
        .province-heading { 
            text-align: center; 
            font-weight: bold; 
            font-size: 11pt; 
            margin: 4mm 0 3mm 0; 
            letter-spacing: 0.5pt;
        }
        
        /* INCIDENT LAYOUT - Two column */
        .incident-block { 
            display: table; 
            width: 100%; 
            margin-bottom: 3mm; 
            page-break-inside: avoid;
        }
        .dig-side { 
            display: table-cell; 
            width: 28%; 
            vertical-align: top; 
            font-weight: bold; 
            font-size: 11pt; 
            line-height: 1.15; 
            padding-right: 3mm;
        }
        .dig-district { 
            margin-bottom: 0mm; 
        }
        .dig-division { 
            font-style: italic; 
            margin-top: 0mm;
        }
        .body-side { 
            display: table-cell; 
            width: 72%; 
            vertical-align: top; 
            text-align: justify; 
            font-size: 11pt; 
            line-height: 1.15; 
        }
        .station-name { 
            font-weight: bold; 
        }

        /* CASE DATA TABLE */
        .case-table { 
            width: 100%; 
            border-collapse: collapse; 
            border: 1.5px solid #000; 
            margin: 10mm 0;
        }
        .case-table th, .case-table td { 
            border: 1px solid #000; 
            padding: 3px 6px; 
            font-size: 10pt; 
            text-align: center;
        }
        .case-table th { 
            font-weight: bold; 
            background: #f0f0f0;
        }
        .case-table td.left { 
            text-align: left; 
            padding-left: 8px;
        }

        /* SIGNATURE SECTION */
        .sig-section { 
            margin-top: 10mm; 
            page-break-inside: avoid;
        }
        .sig-prepared { 
            margin-bottom: 15mm;
        }
        .sig-checked { 
            text-align: left; 
            line-height: 1.3;
        }

        /* DISTRIBUTION LIST */
        .distribution { 
            margin-top: 15mm; 
            font-size: 11pt; 
            line-height: 1.3; 
            page-break-inside: avoid;
        }
        .dist-title { 
            font-weight: bold; 
            margin-bottom: 3mm; 
        }
        .dist-item { 
            margin-bottom: 1mm; 
            padding-left: 8mm;
            text-indent: -8mm;
        }

        .no-print { position: fixed; top: 20px; right: 20px; z-index: 9999; }
        @media print { 
            .no-print { display: none; } 
            body { background: white; } 
            .page { 
                margin: 0; 
                box-shadow: none; 
                page-break-after: always; 
            } 
        }
    </style>
</head>
<body>
    <div class="no-print"><button onclick="window.print()" style="padding:10px 20px; cursor:pointer; background:#333; color:white; border-radius:5px; font-weight:bold;">🖨️ Print / Save as PDF</button></div>
    {{ ALL_PAGES }}
</body>
</html>"""

PAGE_TEMPLATE = """<div class="page">
    <div class="page-num">{{ PAGE_NUM }}</div>
    {{ CONTENT }}
</div>"""

HEADER_TEMPLATE = """<div class="header">
    <div class="confidential">Confidential</div>
    <img src="{{ LOGO_PATH }}" class="logo">
    <div class="ig-address">IG's Command / Information Division, Mirihana, Sri Lanka.</div>
    <div class="ig-title">Inspector General of Police.</div>
    <div class="report-title">General Situation Report</div>
    <div class="date-range">{{ DATE_RANGE }}</div>
</div>"""


def extract_hierarchy(hierarchy_data):
    """Extract DIG District and Division."""
    dig_district = ""
    division = ""
    
    if isinstance(hierarchy_data, list):
        for p in hierarchy_data:
            p_clean = str(p).strip()
            if "DIG" in p_clean.upper():
                dig_district = p_clean
            elif "DIV" in p_clean.upper() or "DIVISION" in p_clean.upper():
                division = p_clean
        return dig_district, division

    hierarchy_str = str(hierarchy_data)
    lines = hierarchy_str.split(',')
    
    for line in lines:
        line = line.strip()
        if "DIG" in line.upper():
            dig_district = line
        elif "DIV" in line.upper() or "DIVISION" in line.upper():
            division = line
    
    return dig_district, division


def build_incident_html(inc):
    """Format incidents in two-column layout."""
    station_raw = str(inc.get("station", "")).strip()
    station = re.sub(r'\s*(?:POLICE\s*)?STATION\s*$', '', station_raw, flags=re.IGNORECASE)
    station = station.strip().upper()
    
    summary = str(inc.get("summary", "")).strip()
    body = str(inc.get("body", "")).strip()
    hierarchy = inc.get("hierarchy", "")
    dig_district, division = extract_hierarchy(hierarchy)
    ref = str(inc.get("ctm", inc.get("otm", inc.get("ir", "")))).strip()
    
    dig_html = ""
    if dig_district:
        dig_html += f'<div class="dig-district">{dig_district}</div>'
    if division:
        dig_html += f'<div class="dig-division">{division}</div>'
    
    body_html = f'<span class="station-name">{station}:</span> '
    
    if summary:
        body_html += f'<span style="font-weight:bold;">({summary})</span> '
    
    body_html += body
    
    if ref:
        body_html += f' ({ref})'
    
    return (
        f'<div class="incident-block">'
        f'  <div class="dig-side">{dig_html}</div>'
        f'  <div class="body-side">{body_html}</div>'
        f'</div>'
    )


def build_section_html(sec):
    """Build section HTML with support for showing all provinces with Nil."""
    title = str(sec.get("title", ""))
    provinces = sec.get("provinces", [])
    
    # Check if section has any incidents at all
    has_any_incidents = any(p.get("incidents") for p in provinces)
    
    # If no provinces have data and no "nil" flags, show section-level Nil
    if not has_any_incidents and not any(p.get("nil") for p in provinces):
        return f'<div class="section-header">{title}</div><div style="margin-left:20mm;">Nil</div>'
    
    html = f'<div class="section-header">{title}</div>'
    
    for p in provinces:
        incs = p.get("incidents", [])
        is_nil = p.get("nil", False)
        
        province_name = p["name"].upper()
        if "PROVINCE" not in province_name:
            province_name += " PROVINCE"
        
        # Always show province heading
        html += f'<div class="province-heading">S/DIG  {province_name}</div>'
        
        if is_nil or not incs:
            # Show "Nil" indented below province heading
            html += '<div style="margin-left:20mm;">Nil</div>'
        else:
            # Show incidents
            for i in incs:
                html += build_incident_html(i)
    
    return html


def build_case_table():
    """Build the 28-row case data table (page 16)."""
    cases = [
        ("01", "Serious Crimes Committed", "03", "01", "02"),
        ("02", "Rape, Sexual Assault & Child Abuse", "07", "04", "03"),
        ("03", "Fatal Accidents", "09", "07", "02"),
        ("04", "Police Officers/Vehicles involved in Road Accidents", "02", "-", "-"),
        ("05", "Finding of Dead Bodies under Suspicious Circumstances", "02", "-", "-"),
        ("06", "Serious Injury/Illnesses/Deaths of Police Officers", "02", "-", "-"),
        ("07", "Detect of Narcotic and Illegal Liquor", "14", "14", "-"),
        ("08", "Arrest of Tri-forces Members", "04", "04", "-"),
        ("09", "Other Matters", "05", "-", "-"),
        ("10", "Terrorist Activities", "-", "-", "-"),
        ("11", "Recovery of Arms & Ammunition", "03", "03", "-"),
        ("12", "Protests & Strikes", "-", "-", "-"),
        ("13", "Homicides", "01", "-", "-"),
        ("14", "Robberies", "01", "-", "01"),
        ("15", "Thefts of Vehicles", "01", "-", "01"),
        ("16", "Thefts of Properties", "03", "-", "03"),
        ("17", "House Breaking & Theft", "01", "-", "01"),
        ("18", "Police Accidents", "-", "-", "-"),
        ("19", "Damages to Sri Lanka Police Property", "02", "-", "-"),
        ("20", "Misconducts of Police officers", "05", "-", "-"),
        ("21", "Deaths of Police officers", "02", "-", "-"),
        ("22", "Hospital admission of SGOO", "02", "-", "-"),
        ("23", "Passing away of close Relatives of SGOO", "-", "-", "-"),
        ("24", "Disappearances", "05", "-", "-"),
        ("25", "Suicides", "02", "-", "-"),
        ("26", "Incidents regarding Foreigners", "03", "-", "-"),
        ("27", "Wild elephant attacks & Deaths of wild elephants", "-", "-", "-"),
        ("28", "Deaths due to drowning", "01", "-", "-")
    ]
    
    html = '<table class="case-table">'
    html += '<tr><th>S/Nos.</th><th>Case</th><th>Reported</th><th>Solved</th><th>Unsolved</th></tr>'
    
    for num, case, reported, solved, unsolved in cases:
        html += f'<tr><td>{num}</td><td class="left">{case}</td><td>{reported}</td><td>{solved}</td><td>{unsolved}</td></tr>'
    
    html += '</table>'
    return html


def get_signature_section(report_date="18th March 2026"):
    """Get signature and distribution section."""
    sig_html = f"""
    <div class="sig-section">
        <div class="sig-prepared">
            Prepared by: PS 51258<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;U.G. Ajith Priyantha
        </div>
        <div style="text-align: center; margin-top: 10mm;">
            <div style="text-decoration: underline; display: inline-block; margin-bottom: 3mm;">
                <span style="font-style: italic;">Signature placeholder</span>
            </div>
        </div>
        <div class="sig-checked">
            Checked by: B.A. Sujith Ganganatha<br>
            Chief Inspector of Police<br>
            Duty Officer<br>
            IG's Command & Information Division,<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mirihana<br>
            {report_date}
        </div>
    </div>"""
    
    dist_items = [
        ("(i)", "H.E. the President"),
        ("(ii)", "Hon. Prime Minister"),
        ("(iii)", "Hon. Speaker"),
        ("(iv)", "Hon. Minister of Public Security"),
        ("(v)", "Secretary to H.E the President"),
        ("(vi)", "Secretary to Hon. Prime Minister"),
        ("(vii)", "Secretary to the Cabinet"),
        ("(viii)", "Secretary to the Ministry of Defence"),
        ("(ix)", "Secretary to the Ministry of Public Security"),
        ("(x)", "Advisor to Hon. Minister of Public Security"),
        ("(xi)", "Chairman / Secretary to National Police Commission"),
        ("(xii)", "Chief of Defence Staff"),
        ("(xiii)", "Service Commanders"),
        ("(xiv)", "SDIGG"),
        ("(xv)", "DIGG"),
        ("(xvi)", "Directors"),
        ("(xvii)", "All SSP / SP Divisions (Territorial)"),
        ("(xviii)", "All HQII & OICC (Territorial & Functional) and File")
    ]
    
    dist_html = '<div class="distribution"><div class="dist-title">Copies to:</div>'
    for num, name in dist_items:
        dist_html += f'<div class="dist-item">{num:>6} {name}</div>'
    dist_html += '</div>'
    
    return sig_html + dist_html


def generate_general_report(data, output_path):
    """Generate General Situation Report with 100% pixel-perfect match."""
    
    logo_filename = "police_logo.png"
    if not os.path.exists(logo_filename):
        logo_filename = "police_logo.jpg"
    logo_path = "file:///" + os.path.abspath(logo_filename).replace("\\", "/")
    
    # Build content HTML from sections
    content_html = ""
    for sec in data.get("sections", []):
        content_html += build_section_html(sec)
    
    # Get date range
    date_range = data.get("date_range", "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026")
    date_range = re.sub(r'(\d+)(st|nd|rd|th)', r'\1<sup>\2</sup>', date_range)
    
    # Get report date
    today = datetime.now()
    day = today.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    report_date = f"{day}{suffix} {today.strftime('%B %Y')}"
    
    # Build pages
    pages = []
    
    # Page 1: Header + Content
    header_html = HEADER_TEMPLATE.replace("{{ LOGO_PATH }}", logo_path)
    header_html = header_html.replace("{{ DATE_RANGE }}", date_range)
    
    page1_content = header_html + content_html
    page1 = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "1")
    page1 = page1.replace("{{ CONTENT }}", page1_content)
    pages.append(page1)
    
    # Page 16: Case Data Table
    case_table_html = build_case_table()
    page16 = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "16")
    page16 = page16.replace("{{ CONTENT }}", case_table_html + get_signature_section(report_date))
    pages.append(page16)
    
    # Page 17: Distribution List (already included in page 16)
    
    # Assemble full HTML
    all_pages = "".join(pages)
    full_html = HTML_TEMPLATE.replace("{{ ALL_PAGES }}", all_pages)
    
    # Clean
    full_html = re.sub(r'[\u0D80-\u0DFF]+', '', full_html)
    full_html = full_html.replace(""", '"').replace(""", '"').replace("„", '"')
    
    # Write
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    print(f"✅ General Report generated: {output_path}")
    return output_path


def html_to_pdf(html_path, pdf_path):
    """Convert HTML to PDF using Microsoft Edge."""
    import subprocess
    
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_exe):
        edge_exe = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    
    if not os.path.exists(edge_exe):
        print("❌ Microsoft Edge not found")
        return False
    
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={os.path.abspath(pdf_path)}",
        "--no-pdf-header-footer",
        f"file:///{os.path.abspath(html_path)}"
    ]
    
    try:
        subprocess.run(cmd, check=True, timeout=60)
        print(f"✅ PDF generated: {pdf_path}")
        return True
    except Exception as e:
        print(f"❌ PDF conversion failed: {e}")
        return False


if __name__ == "__main__":
    # Test with sample data matching your image
    sample_data = {
        "date_range": "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026",
        "sections": [
            {
                "title": "01.SERIOUS CRIMES COMMITTED:",
                "provinces": [
                    {
                        "name": "WESTERN",
                        "incidents": [
                            {
                                "station": "KALUTARA SOUTH",
                                "summary": "A case of a theft",
                                "body": "A case of a theft of Rs. 40,000/= and gold jewellery (6 ½ sovereigns) valued Rs. 3,440,000/= was reported to the police station. The offence took place between 1800 hrs on 15th of March 2026 and 1500 hrs on 16th of March 2026 at #08, Central Garden, Pragathi Mawatha, Kalutara south. Complainant named S. S. Malar, (TP 076-9386812). Suspect identified as P. Madushanka and yet to be arrested. The stolen property not recovered and investigations in process. Motive. For illegal gain.",
                                "hierarchy": ["DIG Kalutara District", "Kalutara Div."],
                                "ctm": "CTM.521"
                            }
                        ]
                    },
                    {
                        "name": "SABARAGAMUWA",
                        "incidents": []
                    },
                    {
                        "name": "SOUTHERN",
                        "incidents": [
                            {
                                "station": "SOORIYAWEWA",
                                "summary": "A case of a homicide by assaulting with a club",
                                "body": "A case of a homicide by assaulting with a club was reported to the police station. The offence took place on the 16th of March 2026 around 2100 hrs at #10, Usgala, Andarawewa, Sooriyawewa. Deceased: E. R. Kumara, aged 40, (male). Suspect identified as K. S. Alwis and yet to be arrested. Investigations are being conducted.",
                                "hierarchy": ["DIG Hambantota District", "Tangalle Div."],
                                "otm": "OTM.1400"
                            }
                        ]
                    },
                    {
                        "name": "UVA",
                        "incidents": []
                    }
                ]
            }
        ]
    }
    
    html_path = "General_Report_Official.html"
    pdf_path = "General_Report_Official.pdf"
    
    generate_general_report(sample_data, html_path)
    html_to_pdf(html_path, pdf_path)
