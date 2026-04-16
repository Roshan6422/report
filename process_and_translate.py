"""
process_and_translate.py — Institutional 4-Stage Pipeline
1. Categorization (28-Split)
2. High-Fidelity Translation (Cloud AI)
3. Intelligent Routing (Ollama GPT)
4. Institutional PDF Generation
"""

import os
import json
import traceback
from datetime import datetime
from ai_engine_manager import get_engine
from general_report_engine import generate_general_report, html_to_pdf
from web_report_engine_v2 import generate_security_report
from police_patterns import OFFICIAL_CASE_TABLE_CATEGORIES, GENERAL_SECTIONS, SECURITY_SECTIONS
import police_geo_utils
from station_mapping import get_institutional_prompt_snippet, SINHALA_TO_ENGLISH, enforce_terminology

# English Province exact names used in rendering
OFFICIAL_PROVINCE_ORDER = [
    "WESTERN", "SABARAGAMUWA", "SOUTHERN", "UVA", "CENTRAL",
    "NORTH WESTERN", "NORTH CENTRAL", "EASTERN", "NORTHERN"
]


def _province_matches_order(inc_prov: str, order_name: str) -> bool:
    """Match 'WESTERN PROVINCE' / 'Western Province' to order key WESTERN."""
    a = (inc_prov or "").upper().replace("PROVINCE", "").replace("  ", " ").strip()
    b = order_name.upper().strip()
    return a == b or a.startswith(b + " ")


def load_routing_rules():
    """Load rules for Ollama routing."""
    r_path = os.path.join("rules", "routing_rules.md")
    if os.path.exists(r_path):
        with open(r_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Route incident to Security or General based on its nature."

def load_translation_rules(report_type="General"):
    """Load specialized translation rules."""
    filename = "security_rules.md" if report_type == "Security" else "general_rules.md"
    rules_path = os.path.join("rules", filename)
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Translate to professional English narrative."

def translate_incident(incident_dict, engine_mgr, restricted=None):
    """Phase 2: High-Fidelity Translation using Ollama/Kaggle."""
    st_raw = incident_dict.get('police_station', '')
    desc_raw = incident_dict.get('description', '')
    date_raw = incident_dict.get('date', '')
    
    # Load all rules to give AI full context of styles
    gen_rules = load_translation_rules("General")
    sec_rules = load_translation_rules("Security")
    
    print(f"    [Ollama/Kaggle] Translating {st_raw}...")
    
    prompt = f"""INSTRUCTIONS:
Translate the Sinhala incident into professional English narrative. 
Strictly follow the institutional styles below. 
NO REPETITION. NO LOOPING. If the text starts to repeat, STOP immediately.

---
STYLE A (GENERAL):
{gen_rules}

---
STYLE B (SECURITY):
{sec_rules}

---
DATA TO TRANSLATE:
STATION: {st_raw}
DATE: {date_raw}
DESCRIPTION: {desc_raw}

{get_institutional_prompt_snippet()}

Result paragraph:"""
    
    system_instr = "You are an Expert Sri Lanka Police Translator. You translate with 100% fidelity. You NEVER repeat phrases. One narrative only."
    
    try:
        translated = engine_mgr.call_ai(prompt, system_prompt=system_instr, restricted_list=restricted)
        
        # Structure it
        geo = police_geo_utils.get_geo_info(st_raw)
        prov = (geo.get("province") or "UNKNOWN").strip()
        hier = [
            f"S/DIG {prov}",
            geo.get("dig") or "",
            geo.get("division") or "",
        ]
        hier = [x for x in hier if x]
        return {
            "station": st_raw.upper(),
            "province": prov,
            "hierarchy": hier if hier else [f"S/DIG {prov}"],
            "body": translated,
            "summary": translated[:150] + ("..." if len(translated) > 150 else ""),
            "original_category": incident_dict.get("category_num", "28"),
        }
    except Exception as e:
        print(f"    ❌ Translation failed for {st_raw}: {e}")
        return None

def process_and_translate(data, filename, app_config_folder):
    """Institutional 4-Stage Pipeline: 28-Split -> Translate -> Route -> Report."""
    engine_mgr = get_engine()
    cloud_restricted = ["gemini", "github", "aimlapi", "groq", "openrouter"]
    ollama_only = ["ollama"]
    
    r_rules = load_routing_rules()
    t_rules = load_translation_rules("General") # Default rules
    
    security_pool = []
    general_pool = []
    
    # 1. CATEGORIZATION (Already partially done in extraction, but we ensure all incidents are listed)
    print(f"📂 [Stage 1] Gathering all incidents from categorized data...")
    all_incidents = []
    for cat_num, cat_data in data.get("categories", {}).items():
        for inc in cat_data.get("incidents", []):
            inc["category_num"] = cat_num
            all_incidents.append(inc)

    # 2. TRANSLATION (OLLAMA/KAGGLE - COST EFFECTIVE)
    print(f"📑 [Stage 2] High-Fidelity Translation (Ollama/Kaggle)...")
    translated_incidents = []
    for inc in all_incidents:
        # Use Ollama for translation to save cloud tokens
        t_inc = translate_incident(inc, engine_mgr, restricted=ollama_only)
        if t_inc:
            t_inc["body"] = enforce_terminology(t_inc["body"])
            translated_incidents.append(t_inc)
            
    # 3. INTELLIGENT ROUTING (CLOUD AI - MAXIMUM INTELLIGENCE)
    print(f"🏹 [Stage 3] Intelligent Routing into Security/General (GitHub/Cloud AI)...")
    for t_inc in translated_incidents:
        print(f"    [Cloud AI] Routing {t_inc['station']}...")
        r_prompt = f"RULES:\n{r_rules}\n\nREPORT SEGMENT:\nStation: {t_inc['station']}\nBody: {t_inc['body']}\n\nDecision?"
        r_res = engine_mgr.call_ai(r_prompt, system_prompt="Institutional Intelligence Router", restricted_list=cloud_restricted)
        
        try:
            # Clean JSON if wrapped in markdown
            if "{" in r_res:
                r_json_str = r_res[r_res.find("{"):r_res.rfind("}")+1]
                r_data = json.loads(r_json_str)
                if r_data.get("routing") == "Security":
                    security_pool.append(t_inc)
                else:
                    general_pool.append(t_inc)
            else:
                general_pool.append(t_inc) # Fallback
        except (json.JSONDecodeError, KeyError, ValueError):
            general_pool.append(t_inc) # Fallback

    # 4. REPORT GENERATION (MAPPING & PDF)
    print(f"📊 [Stage 4] Generating Final Reports...")
    
    gen_matrix = {sec: [] for sec in GENERAL_SECTIONS}
    sec_matrix = {sec: [] for sec in SECURITY_SECTIONS}
    
    G = GENERAL_SECTIONS
    S = SECURITY_SECTIONS

    # Map General Pool → 10 sections
    for inc in general_pool:
        body_lower = inc.get("body", "").lower()
        target_section = G[9] # Others

        if any(kw in body_lower for kw in ["murder", "robbery", "homicide", "theft", "burglary"]):
            target_section = G[0]
        elif any(kw in body_lower for kw in ["rape", "sexual", "child", "abuse"]):
            target_section = G[1]
        elif "accident" in body_lower:
            target_section = G[2] if "fatal" in body_lower else G[3]
        elif "narcotic" in body_lower or "liquor" in body_lower:
            target_section = G[7]
        elif "unidentified" in body_lower or "dead body" in body_lower:
            target_section = G[4]

        gen_matrix[target_section].append(inc)

    # Map Security Pool → 4 sections
    for inc in security_pool:
        body_lower = inc.get("body", "").lower()
        target_section = S[3] # Others

        if any(kw in body_lower for kw in ["terror", "bomb", "blast", "explosion"]):
            target_section = S[0]
        elif any(kw in body_lower for kw in ["protest", "strike", "demonstration", "union"]):
            target_section = S[1]
        elif "weapon" in body_lower or "ammunition" in body_lower or "pistol" in body_lower:
            target_section = S[2]

        sec_matrix[target_section].append(inc)
        
    # Build Output Folders
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base = os.path.join(app_config_folder, "outputs", timestamp)
    os.makedirs(output_base, exist_ok=True)
    
    date_range = data.get("header", {}).get("report_period", "Daily Incident Report")
    
    # Helper for formatting report payload
    def format_report_payload(matrix, official_order):
        sections = []
        for s_title in official_order:
            incs = matrix.get(s_title, [])
            prov_list = []
            for p_name in OFFICIAL_PROVINCE_ORDER:
                p_key = p_name + " PROVINCE"
                p_incidents = [
                    i for i in incs if _province_matches_order(i.get("province", ""), p_name)
                ]
                if p_incidents:
                    prov_list.append({"name": p_key, "incidents": p_incidents, "nil": False})
                else:
                    prov_list.append({"name": p_key, "incidents": [], "nil": True})

            sections.append({
                "title": s_title,
                "count": f"{len(incs):02d}",
                "provinces": prov_list
            })
        return {"date_range": date_range, "sections": sections}

    # Generate General PDF
    gen_data = format_report_payload(gen_matrix, GENERAL_SECTIONS)
    gen_html = os.path.join(output_base, "General_Report.html")
    gen_pdf = os.path.join(output_base, "General_Report.pdf")
    generate_general_report(gen_data, gen_html)
    html_to_pdf(gen_html, gen_pdf)
    
    # Generate Security PDF
    sec_data = format_report_payload(sec_matrix, SECURITY_SECTIONS)
    sec_html = os.path.join(output_base, "Security_Report.html")
    sec_pdf = os.path.join(output_base, "Security_Report.pdf")
    generate_security_report(sec_data, sec_html)
    html_to_pdf(sec_html, sec_pdf)
    
    print(f"✅ Full Institutional Cycle Complete. PDFs in: {output_base}")
    return {
        "success": True, 
        "files": [gen_pdf, sec_pdf], 
        "output_dir": output_base, 
        "timestamp": timestamp,
        "general_pool": len(general_pool),
        "security_pool": len(security_pool)
    }
