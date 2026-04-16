"""
Split combined English narratives and route incidents to the correct institutional
28-category buckets so General vs Security PDFs receive the right written format.

Examples:
- PNB / Navy / bulk narcotics + firearms → category 02 (Security: recoveries).
- Motorcycle theft / MADAMPITIYA / CTM vehicle case → category 06 (General: vehicle theft).
"""

from __future__ import annotations

import os
import re
from copy import deepcopy
from typing import Any


def _env_flag(name: str, default: bool = False) -> bool:
    v = (os.getenv(name) or "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    try:
        return int((os.getenv(name) or "").strip() or default)
    except ValueError:
        return default


def split_glued_english_incident_paragraphs(body: str) -> list[str]:
    """
    One translation/OCR blob may contain several institutional narratives separated
    after '(CTM.xxx) AH'. Split so each gets its own PDF row (DIG/Div/station layout).
    (Cannot use variable-width look-behind in re.split; use explicit start indices.)
    """
    t = (body or "").strip()
    if len(t) < 40:
        return [t]
    rx = re.compile(r"\)\s*AH\b", re.I)
    starts: list[int] = [0]
    for m in rx.finditer(t):
        s = m.end()
        while s < len(t) and t[s].isspace():
            s += 1
        if s < len(t):
            starts.append(s)
    if len(starts) < 2:
        return [t]
    out: list[str] = []
    for i in range(len(starts)):
        a = starts[i]
        b = starts[i + 1] if i + 1 < len(starts) else len(t)
        chunk = t[a:b].strip()
        if len(chunk) >= 8:
            out.append(chunk)
    return out if len(out) > 1 else [t]


def split_combined_english_incidents(body: str) -> list[str]:
    """
    When one OCR/translation block contains two separate narratives (e.g. PNB block
    then MADAMPITIYA:), split so each can be routed independently.
    """
    t = (body or "").strip()
    if not t:
        return []

    if re.search(r"POLICE\s+NARCOTICS\s+BUREAU", t, re.I) and re.search(r"\bMADAMPITIYA\s*:", t, re.I):
        parts = re.split(r"(?=\bMADAMPITIYA\s*:)", t, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]

    # e.g. OTM. 1035) .... MADAMPITIYA:
    if re.search(r"OTM\.\s*\d+", t, re.I) and re.search(r"\bMADAMPITIYA\s*:", t, re.I):
        parts = re.split(r"(?=\bMADAMPITIYA\s*:)", t, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]

    return [t]


def classify_english_incident_body(body: str) -> str | None:
    """
    Return target category id "01".."29" when content clearly belongs there; else None
    (caller keeps original bucket).
    """
    b = (body or "").strip()
    if len(b) < 30:
        return None

    # Security institutional: PNB / Navy / harbour handover + bulk drugs + firearms
    if re.search(r"POLICE\s+NARCOTICS\s+BUREAU", b, re.I):
        return "02"
    if re.search(r"Sri\s+Lanka\s+Navy", b, re.I) and re.search(
        r"handed\s+over\s+to\s+the\s+PNB|PNB\s+at\s+the\s+fisher", b, re.I
    ):
        return "02"
    if re.search(r"heroin|methamphetamine|\bice\b.*firearm|fishing\s+vessels", b, re.I) and re.search(
        r"T-56|M-16|pistols.*magazine|magazines", b, re.I
    ):
        return "02"

    # General: vehicle / motorcycle theft (distinct from security PNB block)
    if re.search(r"theft\s+of\s+a\s+motorcycle|motorcycle\s+bearing", b, re.I):
        return "06"
    if re.search(r"^MADAMPITIYA\s*:", b, re.I) and re.search(r"theft|motorcycle|Rs\.\s*[\d,]+", b, re.I):
        return "06"
    if re.search(r"CTM\.\s*370", b, re.I) and re.search(r"theft|motorcycle", b, re.I):
        return "06"

    return None


def _station_line_match(line: str) -> re.Match[str] | None:
    """Line is 'STATION: A case of …' (institutional narrative start)."""
    return re.match(
        r"^([A-Z][A-Za-z0-9\s\.'-]{1,44}):\s*(A case of\b.*)$",
        line.strip(),
        re.I | re.DOTALL,
    )


def _parse_inline_div_and_station(text: str) -> dict[str, Any] | None:
    """
    'Colombo (S) Div. BAMBALAPITIYA: A case of …' → hierarchy left = division, station, body.
    """
    m = re.match(
        r"^(.+?\bDiv\.)\s+([A-Z][A-Za-z0-9\s]{1,40}):\s*(A case of\b.*)$",
        text.strip(),
        re.I | re.DOTALL,
    )
    if not m:
        return None
    return {
        "hierarchy": m.group(1).strip(),
        "station": m.group(2).strip().upper(),
        "body": m.group(3).strip(),
    }


def _parse_multiline_hierarchy_station(piece: str) -> dict[str, Any] | None:
    """
    DIG / District / … Div. lines then 'KATANA: A case of …' on its own line.
    """
    lines = [ln.rstrip() for ln in piece.splitlines()]
    lines = [ln for ln in lines if ln.strip()]
    if len(lines) < 2:
        return None
    idx = None
    for i, ln in enumerate(lines):
        if _station_line_match(ln):
            idx = i
            break
    if idx is None:
        return None
    hier_lines = [lines[j].strip() for j in range(idx)]
    if not hier_lines:
        return None
    sm = _station_line_match(lines[idx])
    if not sm:
        return None
    station = sm.group(1).strip().upper()
    rest = sm.group(2).strip()
    tail = "\n".join(lines[idx + 1 :]).strip()
    body = (rest + ("\n" + tail if tail else "")).strip()
    return {
        "hierarchy": "\n".join(hier_lines),
        "station": station,
        "body": body,
    }


def enhance_incident_display_fields(inc: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize station/summary/body for official written formats (PNB block vs station-first).
    """
    out = dict(inc)
    body = (out.get("body") or out.get("description") or "").strip()
    if not body:
        return out

    m = re.match(
        r"^\s*(POLICE\s+NARCOTICS\s+BUREAU)\s*:\s*(\([^)]+\))\s*(.*)$",
        body,
        re.I | re.DOTALL,
    )
    if m:
        out["station"] = "POLICE NARCOTICS BUREAU"
        out["summary"] = m.group(2).strip()
        out["body"] = m.group(3).strip()
        out["description"] = out["body"]
        return out

    m2 = re.match(r"^\s*(MADAMPITIYA)\s*:\s*(.*)$", body, re.I | re.DOTALL)
    if m2:
        out["station"] = "MADAMPITIYA"
        rest = m2.group(2).strip()
        out["body"] = rest
        out["description"] = rest
        if not out.get("summary"):
            out["summary"] = rest[:140] + ("…" if len(rest) > 140 else "")
        return out

    parsed = _parse_multiline_hierarchy_station(body)
    if parsed:
        out["hierarchy"] = parsed["hierarchy"]
        out["station"] = parsed["station"]
        out["body"] = parsed["body"]
        out["description"] = parsed["body"]
        if not out.get("summary"):
            b = parsed["body"]
            out["summary"] = b[:160] + ("…" if len(b) > 160 else "")
        return out

    inline = _parse_inline_div_and_station(body)
    if inline:
        out["hierarchy"] = inline["hierarchy"]
        out["station"] = inline["station"]
        out["body"] = inline["body"]
        out["description"] = inline["body"]
        if not out.get("summary"):
            b = inline["body"]
            out["summary"] = b[:160] + ("…" if len(b) > 160 else "")
        return out

    if "\n" not in body:
        sm = _station_line_match(body)
        if sm:
            out["station"] = sm.group(1).strip().upper()
            rest = sm.group(2).strip()
            out["body"] = rest
            out["description"] = rest
            if not out.get("summary"):
                out["summary"] = rest[:160] + ("…" if len(rest) > 160 else "")
            return out

    return out


def apply_institutional_incident_routing(category_summary: dict[str, Any]) -> dict[str, Any]:
    """
    Re-bucket raw incidents: split glued paragraphs, optionally reclassify English bodies,
    rebuild formatted lines and table_counts. Preserves date_range when present.

    By default (INSTITUTIONAL_ENGLISH_REROUTE unset/0) the extractor/AI category is kept
    so General vs Security PDF mapping stays aligned — aggressive English re-routing
    was moving many narratives into cat 02 (Security recoveries).

    Set INSTITUTIONAL_ENGLISH_REROUTE=1 to restore PNB/Navy/motor-heuristic re-bucketing.
    """
    meta_date = category_summary.get("date_range", "")
    out: dict[str, Any] = {
        str(i).zfill(2): {"count": 0, "incidents": [], "raw_incidents": []} for i in range(1, 30)
    }
    english_reroute = _env_flag("INSTITUTIONAL_ENGLISH_REROUTE", default=False)
    min_piece = max(1, min(500, _env_int("INSTITUTIONAL_MIN_PIECE_CHARS", 8)))

    for pad in [str(i).zfill(2) for i in range(1, 30)]:
        block = category_summary.get(pad) or {}
        for raw in block.get("raw_incidents") or []:
            base = deepcopy(raw) if isinstance(raw, dict) else {"body": str(raw)}
            body = (base.get("body") or base.get("description") or "").strip()
            if not body:
                continue

            pieces = split_combined_english_incidents(body) or [body]
            expanded: list[str] = []
            for p in pieces:
                expanded.extend(split_glued_english_incident_paragraphs(p.strip()) or [p.strip()])
            for piece in expanded:
                piece = piece.strip()
                if len(piece) < min_piece:
                    continue
                rr = {**base, "body": piece, "description": piece}
                if english_reroute:
                    tgt = classify_english_incident_body(piece) or pad
                else:
                    tgt = pad
                if tgt not in out:
                    tgt = pad
                rr = enhance_incident_display_fields(rr)
                out[tgt]["raw_incidents"].append(rr)

    for pad in [str(i).zfill(2) for i in range(1, 30)]:
        raws = out[pad]["raw_incidents"]
        out[pad]["count"] = len(raws)
        formatted = []
        for inc in raws:
            b = inc.get("body", "")
            st = inc.get("station", "Unknown")
            formatted.append(f"STATION: {st}\n{b}")
        out[pad]["incidents"] = formatted

    out["date_range"] = meta_date

    # If a custom table_counts was provided (e.g. from the manual dashboard), preserve it fully!
    if category_summary.get("table_counts"):
        out["table_counts"] = category_summary["table_counts"]
    else:
        out["table_counts"] = {k: out[k]["count"] for k in out if k not in ("date_range", "table_counts")}

    return out
