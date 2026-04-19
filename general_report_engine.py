"""
general_report_engine.py — 100% Pixel-Perfect General Situation Report Generator
==================================================================================
Matches the official General Situation Report sample EXACTLY. (v9)
"""

import html as html_module
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
from web_report_engine_v2 import extract_hierarchy

PAGE_TEMPLATE = """<div class="page">
    <div class="page-num">{{ PAGE_NUM }}</div>
    <div class="content-container">
        {{ CONTENT }}
    </div>
</div>"""

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
                # Flush previous text
                if current_text_block:
                    html += html_module.escape("\n".join(current_text_block)).replace("\n", "<br>")
                    current_text_block = []
                html += "<table>"
                table_started = True

            # Simple row parsing
            cells = [c.strip() for c in line.split("|") if c.strip() or line.strip().startswith("|")]
            if len(cells) == 0: continue
            if "---" in line: continue # Skip separator row

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

    if table_started:
        html += "</table>"
    if current_text_block:
        html += html_module.escape("\n".join(current_text_block)).replace("\n", "<br>")

    return html

def build_incident_html(inc):
    """Format incidents in two-column layout matching official sample (v9)."""
    station_raw = str(inc.get("station", "")).strip()
    station = re.sub(r'\s*(?:POLICE\s*)?STATION\s*$', '', station_raw, flags=re.IGNORECASE)
    station = station.strip().upper()

    summary = str(inc.get("summary", "")).strip()
    body = str(inc.get("body", "")).strip()
    hierarchy = inc.get("hierarchy", "")
    ref = str(inc.get("ctm", inc.get("otm", inc.get("ir", "")))).strip()

    dig_html = ""
    if isinstance(hierarchy, list):
        h_lines = [str(x).strip() for x in hierarchy if str(x).strip()]
    else:
        hs = str(hierarchy or "").strip()
        h_lines = [ln.strip() for ln in hs.split("\n") if ln.strip()] if "\n" in hs else []

    if h_lines:
        for ln in h_lines:
            # Official sample shows these labels in bold
            dig_html += f'<div class="dig-district"><b>{html_module.escape(ln)}</b></div>'
    else:
        dig_district, division = extract_hierarchy(hierarchy)
        if dig_district:
            dig_html += f'<div class="dig-district"><b>{html_module.escape(dig_district)}</b></div>'
        if division:
            dig_html += f'<div class="dig-division"><b>{html_module.escape(division)}</b></div>'

    # Body side: STATION: (BOLD) A case of CRIME (BOLD) ... (REF) (BOLD)
    body_html = f'<span class="station-name"><b>{html_module.escape(station)}:</b></span> '

    # Narrative with bold crime type
    narrative = body.strip()
    crime_type = summary.strip()

    formatted_body = render_markdown_tables(narrative)

    # Simple bolding for the crime type tag if it's there
    if crime_type and crime_type.lower() in formatted_body.lower():
        # Match case-insensitive but preserve original case for replacement
        pattern = re.compile(re.escape(crime_type), re.IGNORECASE)
        formatted_body = pattern.sub(f"<b>{crime_type}</b>", formatted_body, count=1)

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
    """Build section HTML."""
    title = str(sec.get("title", ""))
    provinces = sec.get("provinces", [])

    has_any_incidents = any(p.get("incidents") for p in provinces)
    if not has_any_incidents:
        return f'<div class="section-header">{title} Nil</div>'

    html = f'<div class="section-header">{title}</div>'
    for p in provinces:
        incs = p.get("incidents", [])
        if not incs: continue

        province_name = p["name"].upper()
        if "PROVINCE" not in province_name:
            province_name += " PROVINCE"

        html += f'<div class="province-heading">S/DIG  {province_name}</div>'
        for i in incs:
            html += build_incident_html(i)

    return html

def _get_incident_category(inc):
    """Classify incident for province summary table using category number if available."""
    # Prefer the _cat_num field set during report generation mapping
    cat = str(inc.get("_cat_num", "")).zfill(2) if inc.get("_cat_num") else ""
    if cat:
        cat_map = {
            "06": "Theft", "07": "Theft",
            "08": "HB & Theft",
            "05": "Robberies and Armed Robberies",
            "09": "Rape & Sexual Abuse",
            "01": "Homicide", "04": "Homicide",
            "12": "Police Accidents", "13": "Police Accidents",
            "03": "Fatal Accidents", "10": "Fatal Accidents",
        }
        if cat in cat_map:
            return cat_map[cat]
        return "Others"
    # Fallback: keyword-based classification from summary text
    s = str(inc.get("summary", "")).lower()
    if "rape" in s or "sexual" in s or "abuse" in s: return "Rape & Sexual Abuse"
    if "homicide" in s or "murder" in s: return "Homicide"
    if "robber" in s: return "Robberies and Armed Robberies"
    if "fatal accident" in s: return "Fatal Accidents"
    if "police accident" in s: return "Police Accidents"
    if "house breaking" in s or "hb & theft" in s: return "HB & Theft"
    if "theft" in s: return "Theft"
    return "Others"

def build_province_summary_table(data):
    provinces = ["Western", "Sabaragamuwa", "Southern", "Uva", "Central", "North Western", "North Central", "Eastern", "Northern"]
    columns = ["Theft", "HB & Theft", "Robberies and Armed Robberies", "Rape & Sexual Abuse", "Homicide", "Police Accidents", "Fatal Accidents", "Others"]

    counts = {p: dict.fromkeys(columns, 0) for p in provinces}
    for sec in data.get("sections", []):
        for prov_data in sec.get("provinces", []):
            prov_name = str(prov_data.get("name", "")).title().replace(" Province", "")
            matched_prov = next((p for p in provinces if p.lower() in prov_name.lower()), None)
            if matched_prov:
                for inc in prov_data.get("incidents", []):
                    if not isinstance(inc, dict):
                        inc = {"summary": str(inc), "body": str(inc)}
                    cat = _get_incident_category(inc)
                    counts[matched_prov][cat] += 1

    html = '<div class="summary-title">SUMMARY</div>'
    html += '<table class="prov-summary-table">'
    html += '<tr><th style="width:140pt;"></th>'
    
    # Matching the official sample's rotated headers
    header_cols = [
        "Theft", 
        "HB & Theft", 
        "Robberies and Armed Robberies", 
        "Rape & Sexual Abuse", 
        "Homicide", 
        "Police Accidents", 
        "Fatal Accidents", 
        "Others"
    ]
    for c in header_cols:
        html += f'<th class="header-rotated" style="width:42pt;"><div>{c}</div></th>'
    html += '<th class="header-rotated" style="width:45pt;"><div>Grand total</div></th></tr>'

    col_totals = dict.fromkeys(columns, 0)
    grand_total = 0
    for p in provinces:
        html += f'<tr><td class="left-align">{p} Province</td>'
        row_total = 0
        for c in columns:
            val = counts[p][c]
            col_totals[c] += val
            row_total += val
            html += f'<td>{f"{val:02d}" if val > 0 else "-"}</td>'
        grand_total += row_total
        html += f'<td><b>{f"{row_total:02d}" if row_total > 0 else "-"}</b></td></tr>'

    # Total row
    html += '<tr><td class="left-align">Total</td>'
    for c in columns:
        val = col_totals[c]
        html += f'<td><b>{f"{val:02d}" if val > 0 else "-"}</b></td>'
    html += f'<td><b>{f"{grand_total:02d}" if grand_total > 0 else "-"}</b></td></tr>'
    html += '</table>'
    return html

def _normalize_case_count_row(val):
    """table_counts from routing may be plain ints per category
case table expects dict rows."""
    if val is None:
        return {"reported": 0, "solved": 0, "unsolved": 0}
    if isinstance(val, (int, float)):
        return {"reported": int(val), "solved": 0, "unsolved": 0}
    if isinstance(val, dict):
        # Support the new parse map (total_incidents, resolved, unresolved)
        rep = val.get("total_incidents", val.get("reported", 0))
        sol = val.get("resolved", val.get("solved", 0))
        unsol = val.get("unresolved", val.get("unsolved", 0))

        def _to_int(k):
            if k in ("-", "0", 0, None, "", "නැත"): return 0
            try: return int(k)
            except: return 0
            
        return {"reported": _to_int(rep), "solved": _to_int(sol), "unsolved": _to_int(unsol)}
    # Fallback for any other type
    return {"reported": 0, "solved": 0, "unsolved": 0}


def build_case_table(counts=None):
    from police_patterns import OFFICIAL_CASE_TABLE_CATEGORIES
    if counts is None: counts = {}
    html = '<table class="case-table"><tr><th>S/Nos.</th><th>Case</th><th>Reported</th><th>Solved</th><th>Unsolved</th></tr>'
    for cat_label in OFFICIAL_CASE_TABLE_CATEGORIES:
        num = cat_label.split(".")[0].strip()
        name = cat_label.split(".", 1)[1].strip()
        val = _normalize_case_count_row(counts.get(num))
        r_str = f"{val['reported']:02d}" if val.get("reported", 0) > 0 else "-"
        s_str = f"{val['solved']:02d}" if val.get("solved", 0) > 0 else "-"
        u_str = f"{val['unsolved']:02d}" if val.get("unsolved", 0) > 0 else "-"
        html += f'<tr><td>{num}</td><td class="left">{name}</td><td>{r_str}</td><td>{s_str}</td><td>{u_str}</td></tr>'
    html += '</table>'
    return html

def generate_general_report(data, output_path):
    logo_filename = "police_logo.png" if os.path.exists("police_logo.png") else "police_logo.jpg"
    logo_path = "file:///" + os.path.abspath(logo_filename).replace("\\", "/")

    content_html = "".join(build_section_html(sec) for sec in data.get("sections", []))
    matrix_html = build_province_summary_table(data)

    date_range = format_date_range_for_header(data.get("date_range", ""))
    report_date = signature_report_date_string()
    pages = []
    header_html = build_report_header(logo_path, date_range, "General Situation Report")

    # Page 1
    page1 = PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "1").replace("{{ CONTENT }}", header_html + content_html)
    pages.append(page1)
    # Page 16/17
    pages.append(PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "16").replace("{{ CONTENT }}", matrix_html))
    sig_s, dist_s = get_official_appendices(report_date=report_date)
    case_t = build_case_table(data.get("table_counts"))
    pages.append(PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "17").replace("{{ CONTENT }}", case_t + sig_s))
    pages.append(PAGE_TEMPLATE.replace("{{ PAGE_NUM }}", "18").replace("{{ CONTENT }}", dist_s))

    all_p = "".join(pages)
    full_h = sanitize_html_for_pdf(build_institutional_html_document("General Situation Report", all_p))
    with open(output_path, "w", encoding="utf-8") as f: f.write(full_h)
    print(f"[Done] General Report generated: {output_path}")
    return output_path

if __name__ == "__main__":
    sample_data = {
        "date_range": "From 0400 hrs. on 13th March 2026 to 0400 hrs. on 14th March 2026",
        "sections": [{"title": "01.SERIOUS CRIMES COMMITTED:", "provinces": [{"name": "WESTERN", "incidents": [{"station": "KALUTARA SOUTH", "summary": "theft", "body": "A case of a theft of Rs. 40,000/= and gold jewellery (6 ½ sovereigns) valued Rs. 3,440,000/= was reported to the police station. The offence took place between 1800 hrs on 15th of March 2026 and 1500 hrs on 16th of March 2026 at #08, Central Garden, Pragathi Mawatha, Kalutara south.", "hierarchy": ["DIG Kalutara District", "Kalutara Div."], "ctm": "CTM.521"}]}]}]
    }
    generate_general_report(sample_data, "Security_Report_Official.html")
    html_to_pdf("Security_Report_Official.html", "Security_Report_Official.pdf")
