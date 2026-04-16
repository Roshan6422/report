import json
import os
import re
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

# Import local components
from general_report_processor import GeneralReportProcessor
from machine_translator import MachineTranslator
from sinhala_section_splitter import split_by_sections

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB limit

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Render the dashboard/portal."""
    return render_template('index.html')

@app.route('/wizard')
def wizard():
    """Render the 4-step wizard UI."""
    return render_template('wizard.html')

@app.route('/wizard/step1', methods=['POST'])
def wizard_step1():
    """Step 1: OCR & Full Translation."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            translator = MachineTranslator()

            # Use current AI engine if set, otherwise default to Gemini
            engine = os.environ.get("PDF_EXTRACT_AI_ENGINE", "gemini")

            # Get raw Sinhala text
            print(f"--- Wizard Step 1: Extracting Sinhala Text from {filename} ---")
            from machine_translator import _pdf_raw_text_for_ai_pipeline
            sinhala_text = _pdf_raw_text_for_ai_pipeline(filepath)

            # Get full English translation
            print(f"--- Wizard Step 1: Translating to English using {engine} ---")
            english_text = translator._translate_pdf_via_text_ai(filepath, engine)

            return jsonify({
                "success": True,
                "filename": filename,
                "sinhala_text": sinhala_text,
                "english_text": english_text,
                "metadata": {
                    "original_file": filename,
                    "processed_at": datetime.now().isoformat()
                }
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({"success": False, "error": "Invalid file type"}), 400

@app.route('/wizard/step2', methods=['POST'])
def wizard_step2():
    """Step 2: 29-Category Distribution."""
    data = request.json
    english_text = data.get('english_text', '')

    if not english_text:
        return jsonify({"success": False, "error": "No text provided"}), 400

    try:
        # Use AI to categorize the English text into 29 official categories
        from ai_engine_manager import get_engine
        mgr = get_engine()
        engine = os.environ.get("PDF_EXTRACT_AI_ENGINE", "gemini")

        prompt = (
            "Split the following Sri Lanka Police report text into exactly 29 categories. "
            "Categories: 01.Terrorism, 02.Arms, 03.Protests, 04.Homicide, 05.Robbery, 06.Vehicle Theft, "
            "07.Theft, 08.Burglary, 09.Rape, 10.Fatal Accident, 11.Dead Bodies, 12.Police Accidents, "
            "13.Injuries to Police, 14.Misconduct, 15.Deaths of Police, 16.Hospital Admission, "
            "17.Death of Relative, 18.Retired Relative Death, 19.Officers on Leave, 20.Narcotics, "
            "21.Arrests, 22.Tri-Forces, 23.Missing, 24.Suicide, 25.Foreigners, 26.Elephant Attacks, "
            "27.Drowning, 28.Fire, 29.Other.\n\n"
            "Output JSON with category IDs as keys (01-29) and list of incidents as values. "
            "Include every category ID in the JSON, even if empty (incidents: []).\n\n"
            "TEXT:\n" + english_text
        )

        sys_p = "You are an official Police Intelligence Data Classifier. Output ONLY valid JSON."

        print(f"--- Wizard Step 2: Categorizing into 29 Categories using {engine} ---")
        response = mgr._dispatch_engine(engine, prompt, sys_p, 300)

        if not response or str(response).startswith("❌"):
             # Fallback to local regex/string split if AI fails
             parts = split_by_sections(english_text)
             categories = {p[0][:2]: {"name": p[0], "incidents": [{"description": p[1]}] if p[1] else []} for p in parts}
             return jsonify({"success": True, "categories": categories, "mode": "regex_fallback"})

        clean_res = re.sub(r"```json\s*", "", str(response))
        clean_res = re.sub(r"```\s*", "", clean_res).strip()

        try:
            categories_raw = json.loads(clean_res)
            # Normalize structure
            final_categories = {}
            for i in range(1, 30):
                cid = str(i).zfill(2)
                data = categories_raw.get(cid, categories_raw.get(str(i), {"incidents": []}))
                if isinstance(data, list): data = {"incidents": data}
                final_categories[cid] = data

            return jsonify({"success": True, "categories": final_categories})
        except Exception:
             return jsonify({"success": False, "error": "AI returned invalid JSON"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/wizard/step3', methods=['POST'])
def wizard_step3():
    """Step 3: Official Format Grouping (General & Security)."""
    data = request.json
    categories = data.get('categories', {})

    try:
        # Group categories into General and Security sections
        # Mapping:
        # Security: 01, 02, 03
        # General: 04-29 (mapped to 10 sections)

        security_cats = ["01", "02", "03"]
        general_cats = [str(i).zfill(2) for i in range(4, 30)]

        security_groups = []
        for cid in security_cats:
            cat = categories.get(cid, {"incidents": []})
            security_groups.append({
                "id": cid,
                "title": f"{cid}. {cat.get('name', 'Category ' + cid)}",
                "count": len(cat.get('incidents', [])),
                "incidents": cat.get('incidents', [])
            })

        # For General, we use the GeneralReportProcessor logic
        all_general_incidents = []
        for cid in general_cats:
            cat = categories.get(cid, {"incidents": []})
            for inc in cat.get('incidents', []):
                if isinstance(inc, str): inc = {"body": inc}
                inc["cid"] = cid
                all_general_incidents.append(inc)

        processor = GeneralReportProcessor()
        general_sections = processor.categorize_for_general_report(all_general_incidents)

        formatted_general = []
        for title, incs in general_sections.items():
            formatted_general.append({
                "title": title,
                "count": len(incs),
                "incidents": incs
            })

        return jsonify({
            "success": True,
            "groups": {
                "security": security_groups,
                "general": formatted_general
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/wizard/step4', methods=['POST'])
def wizard_step4():
    """Step 4: Final PDF Generation."""
    post_data = request.json
    groups = post_data.get('groups', {})
    metadata = post_data.get('metadata', {})

    try:
        # Generate the two PDFs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(app.config['OUTPUT_FOLDER'], timestamp)
        os.makedirs(folder, exist_ok=True)

        # 1. General Report
        gen_html = os.path.join(folder, "General_Report.html")
        gen_pdf = os.path.join(folder, "General_Report.pdf")

        from general_report_engine import generate_general_report, html_to_pdf

        # Prepare data for general report engine
        # needs "sections" [ { title, provinces [ { name, incidents [ { station, body, reference } ] } ] } ]
        # For simplicity, we just put incidents under a default province if missing

        report_sections = []
        for g in groups.get('general', []):
            provs = [{"name": "ALL PROVINCES", "incidents": []}]
            for inc in g.get('incidents', []):
                provs[0]['incidents'].append({
                    "station": inc.get('station', 'UNKNOWN'),
                    "body": inc.get('description', inc.get('body', '')),
                    "reference": inc.get('reference', '')
                })
            report_sections.append({
                "title": g['title'],
                "provinces": provs
            })

        report_data = {
            "date_range": metadata.get('date_range', 'Official Period'),
            "sections": report_sections
        }

        generate_general_report(report_data, gen_html)
        html_to_pdf(gen_html, gen_pdf)

        # 2. Security Report
        sec_html = os.path.join(folder, "Security_Report.html")
        sec_pdf = os.path.join(folder, "Security_Report.pdf")

        # Similar logic for Security Report
        # Reusing general engine for now or dedicated security if available
        # (Assuming general engine can handle security sections)
        sec_report_sections = []
        for g in groups.get('security', []):
            provs = [{"name": "ALL PROVINCES", "incidents": []}]
            for inc in g.get('incidents', []):
                provs[0]['incidents'].append({
                    "station": inc.get('station', 'UNKNOWN'),
                    "body": inc.get('description', inc.get('body', '')),
                    "reference": inc.get('reference', '')
                })
            sec_report_sections.append({
                "title": g['title'],
                "provinces": provs
            })

        sec_report_data = {
            "date_range": metadata.get('date_range', 'Official Period'),
            "sections": sec_report_sections
        }

        generate_general_report(sec_report_data, sec_html)
        html_to_pdf(sec_html, sec_pdf)

        # Return relative paths with forward slashes for URL compatibility
        files = [
            os.path.relpath(gen_pdf, ".").replace('\\', '/'),
            os.path.relpath(sec_pdf, ".").replace('\\', '/')
        ]

        print(f"--- Wizard Step 4: SUCCESS. Files: {files} ---")
        return jsonify({
            "success": True,
            "files": files
        })

    except Exception as e:
        print("--- Wizard Step 4: FAILED ---")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Serve files for download, handling nested paths and Windows separators."""
    # Sanitize path: allow forward or backward slashes from client
    clean_path = filename.replace('\\', '/')

    # Try absolute path first if it's already full
    if os.path.isabs(clean_path) and os.path.exists(clean_path):
        return send_from_directory(os.path.dirname(clean_path), os.path.basename(clean_path))

    # Try relative to root and specific folders
    search_dirs = [".", "uploads", "outputs"]
    for d in search_dirs:
        target = os.path.normpath(os.path.join(d, clean_path))
        if os.path.exists(target):
            return send_from_directory(os.path.dirname(os.path.abspath(target)),
                                      os.path.basename(target))

    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    print("\n" + "="*50)
    print("   POLICE AI INTELLIGENCE SYSTEM - WEB PORTAL")
    print("   Running on http://localhost:5005")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5005, debug=False)
