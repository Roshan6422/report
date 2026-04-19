"""
institutional_report_pdf.py — Core Styling and Shared PDF Components
======================================================================
"""

import os
import re
from datetime import datetime

import pdfkit

# 100% Pixel-Perfect Institutional CSS
INSTITUTIONAL_REPORT_CSS = """
        @font-face {
            font-family: 'Noto Sans Sinhala';
            src: url('file:///{{ FONT_PATH }}');
        }
        @page {
            size: A4;
            margin: 0;
        }
        body {
            font-family: 'Noto Sans Sinhala', 'Times New Roman', Times, serif;
            margin: 0;
            padding: 0;
            background-color: transparent;
            font-size: 12.00pt;
            color: black;
            line-height: 1.32;
        }
        .page {
            width: 595.32pt;
            min-height: 841.92pt;
            padding: 0;
            margin: 0 auto;
            background: transparent;
            position: relative;
            box-sizing: border-box;
            border: none;
            box-shadow: none;
            page-break-after: always;
        }
        .page-num {
            position: absolute;
            top: 38.00pt;
            left: 0;
            width: 100%;
            text-align: center;
            font-family: Calibri, sans-serif;
            font-weight: bold;
            font-size: 11.04pt;
            z-index: 1000; /* Ensure it stays above everything */
        }
        .header { position: relative; width: 100%; height: 342.68pt; }
        .confidential {
            position: absolute;
            top: 82.07pt;
            left: 0;
            width: 100%;
            text-align: center;
            font-weight: bold;
            font-size: 14.04pt;
            text-transform: capitalize;
            letter-spacing: -0.1 pt;
        }
        .logo {
            position: absolute;
            top: 102.36pt; /* EXACT match from Gold Standard coordinate analysis */
            left: 50%;
            transform: translateX(-50%);
            width: 70pt;    /* EXACT match width */
            height: auto;
        }
        .ig-address {
            position: absolute;
            top: 196.19pt;
            left: 0;
            width: 100%;
            text-align: center;
            font-weight: bold;
            font-size: 14.04pt;
            letter-spacing: -0.1 pt;
        }
        .ig-title {
            font-weight: bold;
            font-size: 14.04pt;
            margin-top: 18pt; /* Vertical space for 'Inspector General of Police' */
            text-align: center;
        }
        .report-title {
            position: absolute;
            top: 229.09pt;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 24.96pt;
            font-weight: bold;
            letter-spacing: -0.15 pt;
        }
        .date-range-box {
            position: absolute;
            top: 262.94pt;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            text-align: center;
        }
        .date-range {
            font-weight: bold;
            font-size: 14.04pt;
            text-decoration: underline;
            text-decoration-thickness: 1.2pt; /* Thicker underline to match sample */
            text-underline-offset: 2pt;
            letter-spacing: -0.05 pt;
        }
        .sup {
            font-size: 9.00pt;
            vertical-align: baseline;
            position: relative;
            top: -5.00pt;
            font-weight: bold;
        }
        .content-container {
            position: relative;
            margin-top: 0;
            padding: 0 40.00pt 0 36.00pt;
        }
        .section-header {
            font-weight: bold;
            font-size: 14.04pt;
            margin-top: 18pt; /* Matches gap from date range box */
            margin-bottom: 5pt;
            text-align: left;
            text-transform: uppercase;
        }
        .province-heading {
            font-family: 'Times New Roman', Times, serif;
            font-weight: bold;
            font-size: 14.04pt;
            margin: 10pt 0 8pt 0; /* Refined gaps based on analysis */
            text-align: center;
            text-transform: uppercase;
            width: 100%;
        }
        .incident-block {
            display: table;
            width: 100%;
            margin-bottom: 10pt;
            border-bottom: none;
            page-break-inside: avoid;
        }
        .dig-side {
            width: 108.86pt;
            padding-right: 15pt;
            font-weight: bold;
            font-size: 12.00pt;
            vertical-align: top;
            box-sizing: border-box;
            display: table-cell;
        }
        .body-side {
            width: 414.14pt;
            vertical-align: top;
            text-align: justify;
            box-sizing: border-box;
            display: table-cell;
        }
        .station-name {
            font-weight: bold;
            font-size: 14.04pt;
            text-transform: uppercase;
            margin-right: 1mm;
        }
        .case-table {
            width: 100%;
            border-collapse: collapse;
            border: none;
            margin: 10mm 0;
        }
        .case-table th, .case-table td {
            border: none;
            padding: 3px 6px;
            font-size: 10.5pt;
            text-align: center;
        }
        .case-table th {
            font-weight: bold;
            background: transparent;
            border-bottom: 0.5pt solid black;
        }
        .case-table td.left {
            text-align: left;
            padding-left: 8px;
        }
        .sig-section {
            margin-top: 10mm;
            page-break-inside: avoid;
        }
        .sig-prepared { margin-bottom: 15mm; }
        .sig-checked {
            text-align: left;
            line-height: 1.3;
        }
        .summary-title {
            font-family: 'Times New Roman', Times, serif;
            font-weight: bold;
            font-size: 14.04pt;
            text-align: center;
            padding-top: 100pt; /* Using padding instead of margin to prevent pushing absolute parent */
            margin-bottom: 20pt;
            text-transform: uppercase;
        }
        .prov-summary-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12.00pt;
            border: 0.5pt solid black;
            page-break-inside: avoid;
        }
        .prov-summary-table th, .prov-summary-table td {
            border: 0.5pt solid black;
            padding: 2pt;
            text-align: center;
            vertical-align: middle;
            height: 28pt;
        }
        .prov-summary-table th {
            font-weight: bold;
            background-color: transparent;
        }
        .prov-summary-table td.left-align {
            text-align: left;
            padding-left: 5pt;
            font-weight: bold;
        }
        .header-rotated {
            height: 160pt; /* Increased height to match official sample categories */
            vertical-align: bottom;
            padding-bottom: 5pt;
        }
        .header-rotated div {
            writing-mode: vertical-rl;
            transform: rotate(180deg);
            text-align: left;
            height: 150pt; /* Explicit height for text container */
            margin: 0 auto;
            font-weight: bold;
            font-size: 11.00pt; /* Slightly smaller to fit triple-line headers */
            white-space: nowrap;
        }
        .dist-item {
            display: flex;
            margin-bottom: 2pt;
            font-size: 11pt;
        }
        .dist-num {
            width: 35pt;
            flex-shrink: 0;
            text-align: right;
            padding-right: 10pt;
        }
        .dist-name {
            flex-grow: 1;
        }
        
        /* Markdown Table Styling */
        .body-side table {
            width: 100%;
            border-collapse: collapse;
            margin: 5pt 0;
            font-size: 10.5pt;
        }
        .body-side table th, .body-side table td {
            border: 0.5pt solid #888;
            padding: 3pt 5pt;
            text-align: left;
        }
        .body-side table th {
            font-weight: bold;
            background-color: #f2f2f2;
        }

        @media print {
            .no-print { display: none; }
            body { background: white; }
            .page {
                margin: 0;
                box-shadow: none;
                page-break-after: always;
            }
        }
"""

HTML_DOCUMENT_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ DOC_TITLE }}</title>
    <style>
""" + INSTITUTIONAL_REPORT_CSS + """
    </style>
</head>
<body>
    <div class="no-print"><button onclick="window.print()" style="padding:10px 20px; cursor:pointer; background:#333; color:white; border-radius:5px; font-weight:bold;">Print / Save as PDF</button></div>
    {{ ALL_PAGES }}
</body>
</html>"""

INSTITUTIONAL_HEADER_HTML = """<div class="header">
    <div class="confidential">Confidential</div>
    <img src="{{ LOGO_PATH }}" class="logo" alt="">
    <div class="ig-address">
        IG’s Command / Information Division, Mirihana, Sri Lanka.<br>
        <span style="font-weight: normal;">Inspector General of Police.</span>
    </div>
    <div class="report-title">{{ REPORT_TITLE }}</div>
    <div class="date-range-box">
        <span class="date-range">{{ DATE_RANGE }}</span>
    </div>
</div>"""

def build_institutional_html_document(doc_title: str, all_pages_html: str) -> str:
    font_path = os.path.abspath("NotoSansSinhala-Regular.ttf").replace("\\", "/")
    return (
        HTML_DOCUMENT_SHELL
        .replace("{{ DOC_TITLE }}", doc_title)
        .replace("{{ ALL_PAGES }}", all_pages_html)
        .replace("{{ FONT_PATH }}", font_path)
    )

def build_report_header(logo_path, date_range, report_title):
    return (
        INSTITUTIONAL_HEADER_HTML.replace("{{ LOGO_PATH }}", logo_path)
        .replace("{{ DATE_RANGE }}", date_range)
        .replace("{{ REPORT_TITLE }}", report_title)
    )


def format_date_range_for_header(date_range: str) -> str:
    """
    Period line under the report title (General + Security must match).
    Ordinals use .sup from INSTITUTIONAL_REPORT_CSS (not raw <sup>).
    """
    if not date_range:
        return ""
    return re.sub(
        r"(\d+)(st|nd|rd|th)",
        r'\1<span class="sup">\2</span>',
        date_range,
    )


def signature_report_date_string(when=None):
    """Signing date at Mirihana (same string on General and Security appendices)."""
    today = when or datetime.now()
    day = today.day
    if 10 <= (day % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix} {today.strftime('%B %Y')}"


def get_official_appendices(report_date=None):
    """
    Canonical signature + distribution blocks for both Situation Reports.
    (Previously General used a shorter list and ignored the live signing date.)
    """
    if report_date is None:
        report_date = signature_report_date_string()

    sig_html = f"""
    <div class="sig-section">
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
        ("(xviii)", "All HQII & OICC (Territorial & Functional) and File"),
    ]

    dist_html = '<div class="distribution" style="margin-top:0;"><div class="dist-title" style="font-weight:bold; margin-bottom:5pt;">Copies to:</div>'
    for num, name in dist_items:
        dist_html += f'<div class="dist-item"><div class="dist-num">{num}</div><div class="dist-name">{name}</div></div>'
    dist_html += "</div>"

    return sig_html, dist_html


def sanitize_html_for_pdf(html):
    return html

def html_to_pdf(html_path, pdf_path):
    # This requires wkhtmltopdf installed
    config = None
    wk_path = os.getenv("WKHTMLTOPDF_PATH")

    if not wk_path:
        # Common Windows paths
        possible_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        ]
        for p in possible_paths:
            if os.path.exists(p):
                wk_path = p
                break

    if wk_path and os.path.exists(wk_path):
        config = pdfkit.configuration(wkhtmltopdf=wk_path)

    try:
        options = {
            'page-size': 'A4',
            'margin-top': '0',
            'margin-right': '0',
            'margin-bottom': '0',
            'margin-left': '0',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        pdfkit.from_file(html_path, pdf_path, options=options, configuration=config)
        print(f"[Done] PDF generated via pdfkit: {pdf_path}")
    except Exception as e:
        # Fallback to Edge if pdfkit fails
        import subprocess
        try:
            print(f"  [PDF] pdfkit attempt failed ({e}). Trying browser-based PDF generation (MS Edge)...")

            # Use absolute path for Edge if possible
            edge_cmd = os.getenv("EDGE_PATH", "msedge.exe")
            if edge_cmd == "msedge.exe":
                possible_edge_paths = [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                ]
                for p in possible_edge_paths:
                    if os.path.exists(p):
                        edge_cmd = p
                        break

            # Note: msedge.exe --print-to-pdf is a reliable headless fallback on Windows
            subprocess.run([
                edge_cmd, "--headless", "--disable-gpu",
                f"--print-to-pdf={os.path.abspath(pdf_path)}",
                f"file:///{os.path.abspath(html_path)}"
            ], check=True, capture_output=True)

            if os.path.exists(pdf_path):
                 print(f"[Done] PDF generated via Edge: {pdf_path}")
            else:
                 raise RuntimeError("Edge command finished but output file not found.")
        except Exception as edge_err:
            print(f"[Error] PDF generation failed: pdfkit error: {e}")
            print(f"[Error] PDF generation failed: Edge fallback error: {edge_err}")
