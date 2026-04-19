"""
process_and_translate.py — Institutional 4-Stage Pipeline
1. Categorization (28-Split)
2. High-Fidelity Translation (Cloud AI)
3. Intelligent Routing (Ollama GPT)
4. Institutional PDF Generation

System Version: v2.2.0
"""
from __future__ import annotations

import json
import os
import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Local project imports
from ai_engine_manager import get_engine
from general_report_engine import generate_general_report, html_to_pdf
from web_report_engine_v2 import generate_security_report
from police_patterns import GENERAL_SECTIONS, SECURITY_SECTIONS
# Project-specific intelligence
from translation_vocabulary import (
    SECURITY_KEYWORDS, KEYWORDS_SINHALA, 
    is_security_incident
)

# Optional import for robust JSON repair
try:
    from json_repair_tool import repair_json
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False

# ── Configure logging ───────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# English Province exact names used in rendering
OFFICIAL_PROVINCE_ORDER = [
    "WESTERN", "SABARAGAMUWA", "SOUTHERN", "UVA", "CENTRAL",
    "NORTH WESTERN", "NORTH CENTRAL", "EASTERN", "NORTHERN"
]

# ── Utilities ───────────────────────────────────────────────────────────────

def _normalize_province(prov: str) -> str:
    """Normalize province string to uppercase without 'PROVINCE' suffix."""
    return (prov or "").upper().replace(" PROVINCE", "").replace("PROVINCE", "").strip()

def _province_matches_order(inc_prov: str, order_name: str) -> bool:
    """Match 'WESTERN PROVINCE' / 'Western Province' to order key WESTERN."""
    return _normalize_province(inc_prov) == order_name.upper().strip()

def _load_text_resource(filename: str, default: str) -> str:
    """Load text file from 'rules/' directory relative to script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rules_dir = os.path.join(script_dir, "rules")
    filepath = os.path.join(rules_dir, filename)
    
    if os.path.exists(filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            logger.warning(f"Failed to load {filename}: {e}")
    return default

def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Safely extract JSON from LLM response text."""
    if not text:
        return None
    
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            if HAS_JSON_REPAIR:
                try:
                    repaired = repair_json(json_str)
                    if repaired:
                        return json.loads(repaired)
                except Exception:
                    pass
    return None

# ── Rule Loading ────────────────────────────────────────────────────────────

def load_routing_rules() -> str:
    """Load rules for Ollama routing."""
    return _load_text_resource("routing_rules.md", "Route incident to Security or General based on its nature.")

def load_translation_rules(report_type: str = "General") -> str:
    """Load specialized translation rules."""
    filename = "security_rules.md" if report_type == "Security" else "general_rules.md"
    return _load_text_resource(filename, "Translate to professional English narrative.")

# ── Stage 2: Translation ───────────────────────────────────────────────────

def translate_incident(incident_dict: Dict[str, Any], engine_mgr: Any, restricted: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Phase 2: High-Fidelity Translation using Ollama/Kaggle.
    Returns normalized incident dict or None on failure.
    """
    st_raw = incident_dict.get("police_station", "").strip()
    desc_raw = incident_dict.get("description", "").strip()
    date_raw = incident_dict.get("date", "").strip()

    if not desc_raw:
        logger.warning(f"Empty description for station: {st_raw}")
        return None

    gen_rules = load_translation_rules("General")
    sec_rules = load_translation_rules("Security")

    logger.info(f"[Ollama/Kaggle] Translating {st_raw}...")

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
        if not translated or translated.startswith("❌"):
            logger.error(f"Translation failed for {st_raw}: AI returned error")
            return None

        # Structure output
        from police_geo_utils import get_geo_info
        geo = get_geo_info(st_raw)
        prov = _normalize_province(geo.get("province") or "UNKNOWN")
        
        hier = [
            f"S/DIG {prov}",
            geo.get("dig") or "",
            geo.get("division") or "",
        ]
        hier = [x.strip() for x in hier if x.strip()]

        body = enforce_terminology(translated.strip())
        
        return {
            "station": st_raw.upper(),
            "province": f"{prov} PROVINCE" if prov else "UNKNOWN PROVINCE",
            "hierarchy": hier if hier else [f"S/DIG {prov}"],
            "body": body,
            "summary": body[:150] + ("…" if len(body) > 150 else ""),
            "original_category": incident_dict.get("category_num", "28"),
        }
    except Exception as e:
        logger.error(f"Translation exception for {st_raw}: {e}")
        return None

# ── Main Pipeline ──────────────────────────────────────────────────────────

def process_and_translate(data: Dict[str, Any], filename: str, app_config_folder: str) -> Dict[str, Any]:
    """
    Institutional 4-Stage Pipeline: 
    1. Categorization → 2. Translate → 3. Route → 4. Report Generation
    """
    engine_mgr = get_engine()
    cloud_restricted = ["gemini", "github", "aimlapi", "groq", "openrouter"]
    hybrid_engines = ["ollama", "gemini", "github"] # Allow Kaggle + Cloud scaling

    r_rules = load_routing_rules()
    load_translation_rules("General")  # Preload rules

    security_pool: List[Dict] = []
    general_pool: List[Dict] = []

    # ── Stage 1: Gather all incidents ──────────────────────────────────────
    logger.info("📂 [Stage 1] Gathering all incidents from categorized data...")
    all_incidents = []
    for cat_num, cat_data in data.get("categories", {}).items():
        for inc in cat_data.get("incidents", []):
            inc["category_num"] = cat_num
            all_incidents.append(inc)
    logger.info(f"   Found {len(all_incidents)} incidents")

    # ── Stage 2: Translation ───────────────────────────────────────────────
    logger.info("📑 [Stage 2] High-Fidelity Translation (Ollama/Kaggle)...")
    translated_incidents = []
    for idx, inc in enumerate(all_incidents, 1):
        logger.info(f"   Translating {idx}/{len(all_incidents)}: {inc.get('police_station', 'Unknown')}")
        # Use hybrid engines so Kaggle/Ollama can be prioritized but Gemini can fallback
        t_inc = translate_incident(inc, engine_mgr, restricted=hybrid_engines)
        if t_inc:
            translated_incidents.append(t_inc)
    logger.info(f"   Successfully translated {len(translated_incidents)} incidents")

    # ── Stage 3: Intelligent Routing ───────────────────────────────────────
    logger.info("🏹 [Stage 3] High-Fidelity Heuristic Routing (AI-Free)...")
    for idx, t_inc in enumerate(translated_incidents, 1):
        # Category-aware fast-path routing
        # Pass the original category_num extracted in Stage 1
        cat_num = t_inc.get("category_num", "")
        
        if is_security_incident(t_inc['body'], t_inc['station'], cat_num):
            logger.info(f"   [Routing] Heuristic marked {t_inc['station']} (Cat:{cat_num}) as SECURITY")
            security_pool.append(t_inc)
        else:
            logger.info(f"   [Routing] Heuristic marked {t_inc['station']} (Cat:{cat_num}) as GENERAL")
            general_pool.append(t_inc)

    logger.info(f"   Routed: {len(security_pool)} Security, {len(general_pool)} General")

    # ── Stage 4: Report Generation ─────────────────────────────────────────
    logger.info("📊 [Stage 4] Generating Final Reports...")

    gen_matrix = {sec: [] for sec in GENERAL_SECTIONS}
    sec_matrix = {sec: [] for sec in SECURITY_SECTIONS}

    # Map General Pool (10-Section Architecture)
    for inc in general_pool:
        body_lower = inc.get("body", "").lower()
        cat_num = str(inc.get("category_num", "")).zfill(2)
        target_section = GENERAL_SECTIONS[9]  # Default: 10. Others

        # High-fidelity routing logic
        if cat_num in ("04", "05", "06", "07", "08"): # Violent crimes / Robbery / Theft
            target_section = GENERAL_SECTIONS[0]
        elif cat_num == "09" or any(kw in body_lower for kw in ["rape", "sexual", "child", "abuse"]):
            target_section = GENERAL_SECTIONS[1]
        elif cat_num == "10": # Fatal Accidents
            target_section = GENERAL_SECTIONS[2]
        elif cat_num == "11" or any(kw in body_lower for kw in ["unidentified", "dead body"]):
            target_section = GENERAL_SECTIONS[4]
        elif cat_num in ("12", "13") or "police vehicle" in body_lower:
            target_section = GENERAL_SECTIONS[3]
        elif cat_num == "14" or "complaint against police" in body_lower:
            target_section = GENERAL_SECTIONS[5]
        elif cat_num in ("15", "16") or "injury of police" in body_lower:
            target_section = GENERAL_SECTIONS[6]
        elif cat_num == "19" or any(kw in body_lower for kw in ["narcotic", "liquor", "drug"]):
            target_section = GENERAL_SECTIONS[7]
        elif cat_num == "21" or "tri-forces" in body_lower:
            target_section = GENERAL_SECTIONS[8]
        # Overrides by content keyword (Serious crimes list)
        elif any(kw in body_lower for kw in ["murder", "robbery", "homicide", "burglary"]):
            target_section = GENERAL_SECTIONS[0]

        gen_matrix[target_section].append(inc)

    # Map Security Pool (Updated for 5-Section Architecture)
    for inc in security_pool:
        body_lower = inc.get("body", "").lower()
        target_section = SECURITY_SECTIONS[4]  # Others (05)

        if any(kw in body_lower for kw in ["terror", "bomb", "blast", "explosion", "extremist", "subversive"]):
            target_section = SECURITY_SECTIONS[0]
        elif any(kw in body_lower for kw in ["arms", "ammunition", "pistol", "revolver", "weapon", "grenade"]):
            target_section = SECURITY_SECTIONS[1]
        elif any(kw in body_lower for kw in ["protest", "strike", "demonstration", "union", "picketing"]):
            target_section = SECURITY_SECTIONS[2]
        elif any(kw in body_lower for kw in ["pnb", "navy", "coast guard", "stf detection"]):
            target_section = SECURITY_SECTIONS[3]

        sec_matrix[target_section].append(inc)

    # Build Output Folders
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base = os.path.join(app_config_folder, "outputs", timestamp)
    os.makedirs(output_base, exist_ok=True)

    date_range = data.get("header", {}).get("report_period", "Daily Incident Report")

    def format_report_payload(matrix: Dict[str, List], official_order: List[str]) -> Dict:
        sections = []
        for s_title in official_order:
            incs = matrix.get(s_title, [])
            prov_list = []
            for p_name in OFFICIAL_PROVINCE_ORDER:
                p_incidents = [i for i in incs if _province_matches_order(i.get("province", ""), p_name)]
                prov_list.append({
                    "name": f"{p_name} PROVINCE",
                    "incidents": p_incidents,
                    "nil": len(p_incidents) == 0
                })
            sections.append({
                "title": s_title,
                "count": f"{len(incs):02d}",
                "provinces": prov_list
            })
        return {"date_range": date_range, "sections": sections}

    # Generate General Report
    try:
        gen_data = format_report_payload(gen_matrix, GENERAL_SECTIONS)
        gen_data["table_counts"] = data.get("summary_table", {}) # Inject parsed summary table
        gen_html = os.path.join(output_base, "General_Report.html")
        gen_pdf = os.path.join(output_base, "General_Report.pdf")
        generate_general_report(gen_data, gen_html)
        html_to_pdf(gen_html, gen_pdf)
        logger.info(f"✅ General Report generated: {gen_pdf}")
    except Exception as e:
        logger.error(f"❌ General Report generation failed: {e}")

    # Generate Security Report
    try:
        sec_data = format_report_payload(sec_matrix, SECURITY_SECTIONS)
        sec_html = os.path.join(output_base, "Security_Report.html")
        sec_pdf = os.path.join(output_base, "Security_Report.pdf")
        generate_security_report(sec_data, sec_html)
        html_to_pdf(sec_html, sec_pdf)
        logger.info(f"✅ Security Report generated: {sec_pdf}")
    except Exception as e:
        logger.error(f"❌ Security Report generation failed: {e}")

    return {
        "success": True,
        "files": [
            os.path.join(output_base, "General_Report.pdf"),
            os.path.join(output_base, "Security_Report.pdf")
        ],
        "output_dir": output_base,
        "timestamp": timestamp,
        "general_pool": len(general_pool),
        "security_pool": len(security_pool)
    }