"""
prompt_selector.py
==================
Auto-select General or Security report prompt based on incident content.
"""

from typing import Dict, Optional
import os

# ── Import your routing function ─────────────────────────────────────────────
from translation_vocabulary import is_security_incident

# ── Prompt Templates (Store these in separate .txt files for maintainability) ─

def load_prompt(filename):
    path = os.path.join(os.path.dirname(__file__), "rules", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

GENERAL_PROMPT_TEMPLATE = load_prompt("general_rules.md")
SECURITY_PROMPT_TEMPLATE = load_prompt("security_rules.md")

GENERAL_PROMPT = GENERAL_PROMPT_TEMPLATE if GENERAL_PROMPT_TEMPLATE else """[GENERAL REPORT PROMPT]"""
SECURITY_PROMPT = SECURITY_PROMPT_TEMPLATE if SECURITY_PROMPT_TEMPLATE else """[SECURITY REPORT PROMPT]"""


def select_report_prompt(incident_text: str, category_num: Optional[str] = None) -> str:
    """
    Auto-select the correct prompt template based on incident content.
    
    Args:
        incident_text: Sinhala or English incident description
        category_num: Official category number (01-29) if known
        
    Returns:
        The appropriate prompt template string
    """
    # Rule 1: Category-based routing (most reliable)
    # Institutional categories (Terrorism, Weapons, Demos, Heavy Narcotics, Military)
    security_categories = {"01", "02", "03", "20", "22"}
    if str(category_num).zfill(2) in security_categories:
        return SECURITY_PROMPT
    
    # Rule 2: Keyword-based routing (fallback) using our new advanced heuristic
    if is_security_incident(incident_text, category_num=category_num):
        return SECURITY_PROMPT
    
    # Default to General
    return GENERAL_PROMPT


def get_prompt_metadata(prompt: str) -> Dict[str, str]:
    """Extract metadata from prompt for logging/auditing."""
    if "SECURITY" in prompt.upper() or "STF" in prompt:
        return {"type": "Security", "style": "Administrative", "format": "CTM/OTM"}
    elif "GENERAL" in prompt.upper():
        return {"type": "General", "style": "Narrative", "format": "CTM"}
    return {"type": "Unknown", "style": "Unknown", "format": "Unknown"}
