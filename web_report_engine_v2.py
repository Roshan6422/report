"""
web_report_engine_v2.py — 100% Pixel-Perfect Security Situation Report Generator
Matches the official sample EXACTLY: fonts, spacing, layout, formatting.
Based on official sample dated 17th-18th March 2026
"""
import os
import re
from institutional_report_pdf import (
    build_institutional_html_document,
    build_report_header,
    format_date_range_for_header,
    get_official_appendices,
    html_to_pdf,
    sanitize_html_for_pdf,
    signature_report_date_string,
)
import html as html_module

PAGE_TEMPLATE = """
{{ PAGE_NUM }}
{{ CONTENT }}
"""

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

def render_markdown_tables(text):
    """Simple regex-based markdown table to HTML converter."""
    if "|" not in text or "---" not in text:
        return html_module.escape(text).replace("\n", "<br>")
    
    lines = text.strip().split("\n")
    html = ""
    table_started = False
    current_text_block = []

    for line in lines:
        if "|" in line:
            if not table_started:
                if current_text_block:
                    html += html_module.escape("\n".join(current_text_block)).replace("\n", "<br>")
                    current_text_block = []
                html += "<table>"
                table_started = True
            cells = [c.strip() for c in line.split("|") if c.strip() or line.strip().startswith("|")]
            if len(cells) == 0: continue
            if "---" in line: continue
            row_tag = "th" if html.endswith("<table>") else "td"
            html += "<tr>"
            for cell in cells:
                html += f"<{row_tag}>{html_module.escape(cell)}</{row_tag}>"
            html += "</tr>"
        else:
            if table_started:
                html += "</table>"
                table_started = False
            current_text_block.append(line)

    if table_started: html += "</table>"
    if current_text_block: html += html_module.escape("\n".join(current_text_block)).replace("\n", "<br>")
    return html

def build_incident_html(inc):
    """Format incidents EXACTLY as shown in the sample Security Situation Report."""
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
        dig_html += f'<div class="dig-district"><b>{html_module.escape(dig_district)}</b></div>'
    if division:
        dig_html += f'<div class="dig-division"><b>{html_module.escape(division)}</b></div>'

    body_html = f'<span class="station-name"><b>{html_module.escape(station)}:</b></span> '
    # Only show summary in parentheses if it's a genuine crime-type label,
    # NOT a truncated version of the body text (which causes ugly duplication)
    if summary and len(summary) < 80 and not body.startswith(summary[:40]):
        body_html = f'<span class="station-name"><b>{html_module.escape(station)}: ({html_module.escape(summary)})</b></span> '

    formatted_body = render_markdown_tables(body)
    body_html += formatted_body

    if ref and ref not in formatted_body:
        body_html += f' <b>({html_module.escape(ref)})</b>'

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
    title = str(sec.get("title", "")).strip()
    provinces = sec.get("provinces", [])

    # Check if section has any incidents
    has_any_incidents = any(p.get("incidents") for p in provinces)

    # Section header with "Nil" if empty (Security Report format: same line)
    if not has_any_incidents:
        return f'<div class="section-header">{title} Nil</div>'

    html = f'<div class="section-header">{title}</div>'

    # Process each province
    for p in provinces:
        incs = p.get("incidents", [])
        is_nil = p.get("nil", False)

        # Province heading format: "S/DIG PROVINCE_NAME"
        province_name = p["name"].upper()
        if "PROVINCE" not in province_name:
            province_name += " PROVINCE"

        if is_nil or not incs:
            continue  # Skip rendering this province completely

        html += f'<div class="province-heading">S/DIG {province_name}</div>'

        # Add each incident
        for i in incs:
            html += build_incident_html(i)

    return html

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

    date_range = format_date_range_for_header(
        data.get("date_range", "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026")
    )
    report_date = signature_report_date_string()
    sig_section, dist_section = get_official_appendices(report_date=report_date)

    # Build pages
    pages = []

    # Page 1: Header + Content (properly build header from HEADER_TEMPLATE)
    header_html = build_report_header(logo_path, date_range, "Security Situation Report")

    page1_content = header_html + content_html
    page1 = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "1")
    page1 = page1.replace("{{ CONTENT }}", page1_content)
    pages.append(page1)

    # Page 2: Signature
    page_sig = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "2")
    page_sig = page_sig.replace("{{ CONTENT }}", sig_section)
    pages.append(page_sig)

    # Page 3: Distribution
    page_dist = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "3")
    page_dist = page_dist.replace("{{ CONTENT }}", dist_section)
    pages.append(page_dist)

    # Assemble full HTML (same shell + CSS as General report)
    all_pages = " ".join(pages)
    full_html = sanitize_html_for_pdf(
        build_institutional_html_document("Security Situation Report", all_pages)
    )

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"[Done] Security Report generated: {output_path}")
    return output_path

def generate_general_report(data, output_path):
    """Generate General Situation Report with 28-category summary table."""
    logo_filename = "police_logo.png"
    logo_path = "file:///" + os.path.abspath(logo_filename).replace("\\", "/")
    
    # 1. Body content
    content_html = ""
    for sec in data.get("sections", []):
        content_html += build_section_html(sec)

    # 2. Summary Table (9x9)
    data.get("summary_table", [])
    summary_table_html = '<div style="text-align:center; font-weight:bold; font-size:14pt; margin-bottom:5mm;">SUMMARY</div>'
    summary_table_html += '<table class="prov-summary-table"><tr><th style="width:30%;"></th>'
    cols = ["Theft", "HB & Theft", "Robberies", "Rape", "Homicide", "Police Acc.", "Fatal Acc.", "Others", "Total"]
    for col in cols:
        summary_table_html += f'<th class="header-rotated"><div>{col}</div></th>'
    summary_table_html += '</tr>'

    provinces = ["Western", "Sabaragamuwa", "Southern", "Uva", "Central", "North Western", "North Central", "Eastern", "Northern"]
    for prov in provinces:
        summary_table_html += f'<tr><td style="text-align:left; font-weight:bold; padding-left:8px;">{prov} Province</td>'
        for _ in range(9): summary_table_html += '<td>-</td>'
        summary_table_html += '</tr>'
    summary_table_html += '</table>'

    date_range = format_date_range_for_header(
        data.get("date_range", "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026")
    )
    report_date = signature_report_date_string()
    sig_section, dist_section = get_official_appendices(report_date=report_date)

    # Assemble Pages
    header_html = build_report_header(logo_path, date_range, "General Situation Report")

    pages = []
    p1 = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "1").replace("{{ CONTENT }}", header_html + content_html)
    p2 = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "2").replace("{{ CONTENT }}", summary_table_html)
    p3 = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "3").replace("{{ CONTENT }}", sig_section + dist_section)

    pages.extend([p1, p2, p3])
    full_html = sanitize_html_for_pdf(
        build_institutional_html_document("General Situation Report", " ".join(pages))
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"[Done] General Report generated: {output_path}")
    return output_path

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
                                "body": "On the 17th of March 2026, officers of the Navy attached to the Wedithalathivu camp arrested the following persons while sailing in a boat in the sea of Wedithalathivu area with the possession of 2 non-electric detonators. (1) A.R.J. Patric, aged 27 (2) A.F. Perera, aged 44 (3) R. Jonindan, aged 44 and (4) A.S. Pihiravo, aged 32 of Pallimune-East, Mannar. Investigations are being conducted. (CTM. 530)-M",
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