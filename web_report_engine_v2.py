"""
web_report_engine_v2.py — 100% Pixel-Perfect Security Situation Report Generator
==================================================================================
Matches the official sample EXACTLY: fonts, spacing, layout, formatting.

Based on official sample dated 17th-18th March 2026
"""

import os
import re
from datetime import datetime

# 100% PIXEL-PERFECT TEMPLATE: EXACT MATCH TO OFFICIAL SECURITY SITUATION REPORT
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Situation Report</title>
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
        
        /* PAGE NUMBER - Top right, Times New Roman 11pt */
        .page-num { 
            text-align: right; 
            font-family: 'Times New Roman', Times, serif; 
            font-size: 11pt; 
            margin-bottom: 8mm; 
            font-weight: normal;
        }
        
        /* HEADER - Exact spacing from sample */
        .header { text-align: center; margin-bottom: 0; }
        .confidential { 
            font-weight: bold; 
            font-size: 14pt; 
            margin-bottom: 3mm; 
            text-align: center; 
            font-family: 'Times New Roman', Times, serif;
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

        /* SECTION HEADERS - Bold, 11pt, exact spacing */
        .section-header { 
            font-weight: bold; 
            font-size: 11pt; 
            margin-top: 3mm; 
            margin-bottom: 3mm; 
            text-align: left;
        }
        
        /* PROVINCE HEADING - Centered, bold, 11pt */
        .province-heading { 
            text-align: center; 
            font-weight: bold; 
            font-size: 11pt; 
            margin: 4mm 0 3mm 0; 
            letter-spacing: 0.5pt;
        }
        
        /* INCIDENT LAYOUT - Two column with exact measurements from sample */
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
        .incident-title { 
            font-weight: bold; 
        }

        /* SIGNATURE BLOCK - Exact positioning from sample */
        .sig-section { 
            margin-top: 10mm; 
            page-break-inside: avoid;
        }
        .sig-line { 
            margin-top: 8mm; 
            font-size: 11pt; 
        }
        .sig-prepared { 
            margin-bottom: 15mm;
        }
        .sig-checked { 
            text-align: left; 
            line-height: 1.3;
        }

        /* DISTRIBUTION LIST - Exact formatting from sample */
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
    <div class="header">
        <div class="confidential">Confidential</div>
        <img src="{{ LOGO_PATH }}" class="logo">
        <div class="ig-address">IG's Command / Information Division, Mirihana, Sri Lanka.</div>
        <div class="ig-title">Inspector General of Police.</div>
        <div class="report-title">Security Situation Report</div>
        <div class="date-range">{{ DATE_RANGE }}</div>
    </div>
    {{ CONTENT }}
    {{ APPENDICES }}
</div>"""


def extract_hierarchy(hierarchy_data):
    """Extract DIG District and Division exactly as shown in sample."""
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

    # Fallback for string input
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
    """
    Format incidents EXACTLY as shown in the sample Security Situation Report.
    
    Sample format:
    DIG Ratnapura          EMBILIPITIYA: (Arrest of suspects along with a detonator and
    District               gunpowder) On the 17th March 2026, acting on an information...
    
    Embilipitiya Div.
    """
    station_raw = str(inc.get("station", "")).strip()
    
    # Clean station name - remove "POLICE STATION" suffix
    station = re.sub(r'\s*(?:POLICE\s*)?STATION\s*$', '', station_raw, flags=re.IGNORECASE)
    station = station.strip().upper()
    
    # Get incident title/summary (in parentheses)
    summary = str(inc.get("summary", "")).strip()
    
    # Get body text
    body = str(inc.get("body", "")).strip()
    
    # Get hierarchy
    hierarchy = inc.get("hierarchy", "")
    dig_district, division = extract_hierarchy(hierarchy)
    
    # Get reference code
    ref = str(inc.get("ctm", inc.get("otm", inc.get("ir", "")))).strip()
    
    # Build the left column (DIG side)
    dig_html = ""
    if dig_district:
        dig_html += f'<div class="dig-district">{dig_district}</div>'
    if division:
        dig_html += f'<div class="dig-division">{division}</div>'
    
    # Build the right column (body side)
    # Format: STATION: (Title) Body text (REF)-X
    body_html = f'<span class="station-name">{station}:</span> '
    
    if summary:
        body_html += f'<span class="incident-title">({summary})</span> '
    
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
    """Build section HTML with support for showing all provinces with Nil.
    
    Note: Security Report format shows "Nil" on same line as section header,
    not indented below like General Report.
    """
    title = str(sec.get("title", ""))
    provinces = sec.get("provinces", [])
    
    # Check if section has any incidents
    has_any_incidents = any(p.get("incidents") for p in provinces)
    
    # Section header with "Nil" if empty (Security Report format: same line)
    if not has_any_incidents and not any(p.get("nil") for p in provinces):
        return f'<div class="section-header">{title} Nil</div>'
    
    html = f'<div class="section-header">{title}</div>'
    
    # Process each province
    for p in provinces:
        incs = p.get("incidents", [])
        is_nil = p.get("nil", False)
        
        # Province heading format: "S/DIG  PROVINCE_NAME"
        province_name = p["name"].upper()
        if "PROVINCE" not in province_name:
            province_name += " PROVINCE"
        
        html += f'<div class="province-heading">S/DIG  {province_name}</div>'
        
        if is_nil or not incs:
            # Security Report: Show "Nil" on same line as province heading
            html += '<div class="section-header" style="margin-left:0;">Nil</div>'
        else:
            # Add each incident
            for i in incs:
                html += build_incident_html(i)
    
    return html


def get_official_appendices(report_date="18th March 2026"):
    """Official Signature and Distribution List - EXACT format from sample."""
    
    # Signature section with handwritten signature placeholder
    sig_html = f"""
    <div class="sig-section">
        <div class="section-header">04. OTHER MATTERS OF INTEREST AND IMPORTANCE: Nil</div>
        <div style="text-decoration: underline; margin-top: 5mm; margin-bottom: 3mm;">
            <span style="font-style: italic;">Signature placeholder</span>
        </div>
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
    
    # Distribution list - EXACT format from sample
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


def generate_security_report(data, output_path):
    """Generate Security Situation Report with 100% pixel-perfect match to official sample."""
    
    # Use security logo
    logo_filename = "security_logo.png"
    if not os.path.exists(logo_filename):
        logo_filename = "police_logo.png"
    logo_path = "file:///" + os.path.abspath(logo_filename).replace("\\", "/")
    
    # Build content HTML from sections
    content_html = ""
    for sec in data.get("sections", []):
        content_html += build_section_html(sec)
    
    # Get date range from data
    date_range = data.get("date_range", "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026")
    
    # Format date range with superscript for "th"
    date_range = re.sub(r'(\d+)(st|nd|rd|th)', r'\1<sup>\2</sup>', date_range)
    
    # Get report date for signature
    today = datetime.now()
    day = today.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    report_date = f"{day}{suffix} {today.strftime('%B %Y')}"
    
    # Get official appendices (signature and distribution)
    appendices = get_official_appendices(report_date=report_date)
    
    # Assemble page
    page = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "1")
    page = page.replace("{{ LOGO_PATH }}", logo_path)
    page = page.replace("{{ DATE_RANGE }}", date_range)
    page = page.replace("{{ CONTENT }}", content_html)
    page = page.replace("{{ APPENDICES }}", appendices)
    
    # Assemble full HTML
    full_html = HTML_TEMPLATE.replace("{{ ALL_PAGES }}", page)
    
    # Clean any Sinhala characters or artifacts
    full_html = re.sub(r'[\u0D80-\u0DFF]+', '', full_html)
    full_html = full_html.replace(""", '"').replace(""", '"').replace("„", '"')
    
    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    print(f"✅ Security Report generated: {output_path}")
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
    # Test with sample data
    sample_data = {
        "date_range": "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026",
        "sections": [
            {
                "title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:",
                "provinces": []
            },
            {
                "title": "02. SUBVERSIVE ACTIVITIES:",
                "provinces": []
            },
            {
                "title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:",
                "provinces": [
                    {
                        "name": "SABARAGAMUWA",
                        "incidents": [
                            {
                                "station": "EMBILIPITIYA",
                                "summary": "Arrest of suspects along with a detonator and gunpowder",
                                "body": "On the 17th March 2026, acting on an information received through the 1-1-9 project, police arrested a Buddhist monk named Rev. Embilipitiye Indrarathana thero, aged 68, the chief incumbent of the Sri Darshanagiri viharaya, Darshanagama, Embilipitiya and another person named N.U. Samanchandra, aged 56 of # 896, Mayuragama, Sewanagala along with an electric detonator and 80g of gunpowder, while digging a tunnel with the intention of treasure hunting in the temple premises. The suspects are scheduled to be produced before the Magistrate court, Embilipitiya on the 18th March 2026. (OTM.1421)-A",
                                "hierarchy": ["DIG Ratnapura District", "Embilipitiya Div."],
                                "otm": "OTM.1421"
                            },
                            {
                                "station": "UDAWALAWA",
                                "summary": "Arrest of a person for possession of a firearm",
                                "body": "On the 17th of March 2026, police arrested a person named K.T. Ranathunga, aged 53 of #14/2 Panahaduwa, Kolombage-Ara for possession of a locally made muzzle loading firearm at Panahaduwa in Udawalawa area. Investigations are being conducted. (OTM.1445)-E",
                                "hierarchy": ["DIG Ratnapura District", "Embilipitiya Div."],
                                "otm": "OTM.1445"
                            }
                        ]
                    },
                    {
                        "name": "NORTHERN",
                        "incidents": [
                            {
                                "station": "ADAMPAN",
                                "summary": "Arrest of suspects along with two detonators",
                                "body": "On the 17th of March 2026, officers of the Navy attached to the Wedithalathivu camp arrested the following persons while sailing in a boat in the sea of Wedithalathivu area with the possession of 2 non-electric detonators. (1) A.R.J. Patric, aged 27 (2) A.F. Perera, aged 44 (3) R. Jonindan, aged 44 and (4) A.S. Pihiravo, aged 32 of Pallimune-East, Mannar. Investigations are being conducted. (CTM. 530)- M",
                                "hierarchy": ["DIG Wanni District", "Mannar Div."],
                                "ctm": "CTM. 530"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    html_path = "test_security_report.html"
    pdf_path = "test_security_report.pdf"
    
    generate_security_report(sample_data, html_path)
    html_to_pdf(html_path, pdf_path)
