"""
Sinhala document helpers for the desktop pipeline.
README / desktop_pipeline.process_pdf_sinhala_split_then_translate expect this module.
"""

from __future__ import annotations

import re

# Likely section headers for the Security half of a dual (General + Security) daily report.
_SECURITY_HEADER_RES = (
    re.compile(
        r"(?m)^\s*(?:[\*\-•\d]+[\.\)\s]+)*(?:"
        r"ආරක්ෂක\s*තත්ත්වය|"
        r"ආරක්ෂක\s*තත්වය|"
        r"පොලිස්\s*ආරක්ෂක\s*තත්ත්වය|"
        r"රාජ්‍ය\s*ආරක්ෂක\s*තත්ත්වය|"
        r"PUBLIC\s+SECURITY\s+SITUATION|"
        r"SECURITY\s+SITUATION\b"
        r")",
        re.IGNORECASE,
    ),
)


def split_sinhala_document(text: str) -> tuple[str, str]:
    """
    Split a full Sinhala police daily report into (general_part, security_part).

    If no clear ආරක්ෂක තත්ත්වය (or English security) heading is found, returns
    (full_text, "") so all extraction applies to the General narrative; the Security
    PDF can still be generated (mostly NIL) from the same structured categories.
    """
    if not text or not str(text).strip():
        return "", ""

    t = str(text)
    best: int | None = None
    for rx in _SECURITY_HEADER_RES:
        m = rx.search(t)
        if not m:
            continue
        pos = m.start()
        if pos == 0:
            continue
        if best is None or pos < best:
            best = pos

    if best is None:
        return t.strip(), ""

    general = t[:best].strip()
    security = t[best:].strip()
    # Very lopsided split → likely a false match inside body text
    if len(general) < 20 and len(security) > max(400, len(general) * 8):
        return t.strip(), ""
    return general, security


def extract_text_with_layout(pdf_path: str) -> str:
    """Compatibility helper for docs; delegates to the main Sinhala PDF extractor."""
    from machine_translator import extract_pdf_to_sinhala

    return (extract_pdf_to_sinhala(pdf_path) or "").strip()
