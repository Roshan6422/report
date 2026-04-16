import os

from dotenv import load_dotenv

load_dotenv()
import json
import logging
import re
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from ai_engine_manager import _split_large_text, get_engine
from app import SinhalaPoliceReportExtractor
from db_manager import log_generated_file, save_translated_incident
from json_repair_tool import repair_json
from machine_translator import (
    extract_pdf_to_sinhala,
    sanitize_police_translation_output,
    translate_sinhala_to_english,
)
from sinhala_section_splitter import split_by_sections
from station_mapping import get_station_info
from word_report_engine import WordReportEngine

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ── Thread-safe progress lock ─────────────────────────────────────────────────
_progress_lock = threading.Lock()


def _safe_callback(callback, *args, **kwargs):
    """Thread-safe progress callback wrapper that never crashes the pipeline."""
    if not callback:
        return
    try:
        with _progress_lock:
            callback(*args, **kwargs)
    except Exception as cb_err:
        logger.warning(f"Progress callback failed (non-fatal): {cb_err}")


def strip_sinhala_forcefully(text):
    if not text:
        return text
    clean = re.sub(r'[\u0D80-\u0DFF]+', '', str(text))
    clean = re.sub(r'\(\s*\)', '', clean)
    clean = re.sub(r'\s{2,}', ' ', clean)
    return clean.strip(' \n\t\r,-:')


def _translate_pool_workers(default: int) -> int:
    try:
        return max(1, int(os.getenv("TRANSLATE_WORKERS", str(default)).strip()))
    except ValueError:
        return default


def _extract_summary_table(category_results: dict, full_text: str = "") -> dict:
    """
    Build the 29-row summary table shown on the last page of every PDF.
    Returns: {cat_num: {"reported": int, "solved": int, "unsolved": int}}
    """
    from police_patterns import OFFICIAL_CASE_TABLE_CATEGORIES

    table: dict = {}
    for cat_label in OFFICIAL_CASE_TABLE_CATEGORIES:
        num = cat_label.split(".")[0].strip().zfill(2)
        table[num] = {"reported": 0, "solved": 0, "unsolved": 0}

    if full_text:
        row_re = re.compile(
            r"^\s*\|?\s*(\d{1,2})[\.\s\|:]+([^\|\t]{2,120}?)[\|\t]\s*([^\|\t]+?)\s*[\|\t]\s*([^\|\t]+?)\s*[\|\t]\s*([^\|\t\n]+?)(?:[\|\t]|\n|$)",
            re.MULTILINE | re.IGNORECASE,
        )

        def _to_int(val: str) -> int:
            v = str(val).strip().lower()
            if v in ("-", "නැත", "nath", "naath", "none", "nil", "", "0", "nil.", "none."):
                return 0
            if any(unit in v for unit in ["kg", "ml", "mg", "lkr", " rs"]):
                return 0
            v = v.replace(",", "")
            try:
                return int(v)
            except ValueError:
                m = re.search(r'^(\d+)', v)
                return int(m.group(1)) if m else 0

        import difflib

        for m in row_re.finditer(full_text):
            raw_num_str = m.group(1)
            raw_name_str = m.group(2).strip()
            rep = _to_int(m.group(3))
            sol = _to_int(m.group(4))
            uns = _to_int(m.group(5))

            best_match_num = None
            highest_ratio = 0.0

            for cat_label in OFFICIAL_CASE_TABLE_CATEGORIES:
                parts = cat_label.split(".", 1)
                if len(parts) == 2:
                    official_num = parts[0].strip().zfill(2)
                    official_name = parts[1].strip()
                    ratio = difflib.SequenceMatcher(None, raw_name_str.lower(), official_name.lower()).ratio()
                    if ratio > highest_ratio:
                        highest_ratio = ratio
                        best_match_num = official_num

            if highest_ratio > 0.4:
                target_num = best_match_num
            else:
                target_num = str(int(raw_num_str)).zfill(2)
                if rep > 2000 or sol > 2000 or uns > 2000:
                    continue

            if target_num in table:
                if rep > 0 or table[target_num]["reported"] == 0:
                    table[target_num]["reported"] = rep
                if sol > 0 or table[target_num]["solved"] == 0:
                    table[target_num]["solved"] = sol
                if uns > 0 or table[target_num]["unsolved"] == 0:
                    table[target_num]["unsolved"] = uns

                logger.debug(
                    f"Table Match -> ['{raw_name_str}'] → Cat {target_num} | "
                    f"Rep:{rep} Sol:{sol} Uns:{uns}"
                )

    for cat_num, data in category_results.items():
        if cat_num in ("table_counts", "date_range"):
            continue
        padded = str(cat_num).zfill(2)
        if padded in table:
            count = data.get("count", 0) if isinstance(data, dict) else 0
            if table[padded]["reported"] == 0 and count > 0:
                table[padded]["reported"] = count
                table[padded]["unsolved"] = count

    return table


INCIDENT_JSON_SYSTEM_PROMPT = (
    "Convert the user's English police incident text into ONE JSON object only. "
    "No markdown fences, no explanation. "
    'Keys (strings): "station", "province", "district", "date", "time", '
    '"category_num", "category_name", "description". '
    'Optional keys: "summary", "division", "financial_loss", "status", "victim_suspect_names". '
    'Use English. Unknown station/province: use best guess from text or \"Unknown\" / \"WESTERN\".'
)


def _normalize_incident_dict(data):
    """Map common model aliases to keys desktop_pipeline expects."""
    if not isinstance(data, dict):
        return None
    desc = (
        data.get("description")
        or data.get("body")
        or data.get("narrative")
        or data.get("text")
        or data.get("english")
        or ""
    )
    st = data.get("station") or data.get("police_station") or "Unknown Station"
    div = data.get("division") or data.get("district") or "Unknown"
    prov = data.get("province") or "WESTERN"
    out = {
        "description": str(desc).strip() or "No description",
        "station": str(st).strip(),
        "province": str(prov).strip(),
        "date": str(data.get("date", "") or "").strip(),
        "time": str(data.get("time", "") or "").strip(),
        "summary": str(data.get("summary", "") or "").strip(),
        "division": str(div).strip(),
        "financial_loss": str(data.get("financial_loss", "") or "Nil").strip(),
        "status": str(data.get("status", "") or "Confirmed").strip(),
        "victim_suspect_names": str(data.get("victim_suspect_names", "") or "N/A").strip(),
        "category_num": str(data.get("category_num", "") or "").strip(),
        "category_name": str(data.get("category_name", "") or "").strip(),
    }
    if not out["summary"] and out["description"]:
        out["summary"] = out["description"][:150] + ("..." if len(out["description"]) > 150 else "")
    return out


def _parse_incident_ai_response(raw):
    """Parse Ollama/cloud text into a dict; handles markdown fences and minor JSON damage."""
    if not raw or (isinstance(raw, str) and raw.startswith("❌")):
        return {
            "description": raw or "",
            "station": "Unknown",
            "province": "WESTERN",
            "date": "",
        }
    s = raw.strip()
    candidates = [s]
    repaired = repair_json(s)
    if repaired and repaired != s:
        candidates.append(repaired)
    for cand in candidates:
        try:
            data = json.loads(cand)
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            normalized = _normalize_incident_dict(data)
            if normalized:
                return normalized
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    return {"description": s, "station": "Unknown", "province": "WESTERN", "date": ""}


_SINHALA_SCRIPT_RE = re.compile(r"[\u0D80-\u0DFF]")


def _text_contains_sinhala(s: str) -> bool:
    return bool(s and _SINHALA_SCRIPT_RE.search(s))


def _translate_block_for_pdf_english(text: str, max_chunk: int = 8000, retries: int = 2) -> str:
    """
    Translate Sinhala fragments to English for institutional PDF output.
    BUG FIX: Added retry logic with exponential backoff.
    """
    if not text or not _text_contains_sinhala(text):
        return text
    text = text.strip()
    if len(text) <= max_chunk:
        for attempt in range(retries + 1):
            try:
                out = (sanitize_police_translation_output(translate_sinhala_to_english(text)) or "").strip()
                if out and not out.startswith("❌") and "Translation unavailable" not in out:
                    out = _fix_date_format_in_text(out)
                    out = _fix_time_format_in_text(out)
                    out = _format_currency_suffix(out)
                    return out
            except Exception as e:
                logger.warning(f"[PDF-EN] translate attempt {attempt + 1} failed ({len(text)} chars): {e}")
                if attempt < retries:
                    import time
                    time.sleep(1.5 ** attempt)
        return text  # Fallback: return original if all retries fail
    parts: list[str] = []
    for i in range(0, len(text), max_chunk):
        seg = text[i: i + max_chunk]
        if _text_contains_sinhala(seg):
            parts.append(_translate_block_for_pdf_english(seg, max_chunk=max_chunk, retries=retries))
        else:
            parts.append(seg)
    return "\n".join(parts).strip()


def _ensure_pdf_english_incident(o: dict) -> None:
    """Mutate normalized incident so General/Security PDFs are English-only."""
    if (os.getenv("PDF_SKIP_SINHALA_BACKFILL") or "").strip().lower() in ("1", "true", "yes"):
        return
    body = str(o.get("body") or "").strip()
    if _text_contains_sinhala(body):
        o["body"] = _translate_block_for_pdf_english(body)
        o["description"] = o["body"]
        nb = o["body"]
        o["summary"] = (nb[:180] + "…") if len(nb) > 180 else nb
    else:
        summ = str(o.get("summary") or "").strip()
        if _text_contains_sinhala(summ):
            o["summary"] = _translate_block_for_pdf_english(summ)
        elif (not summ) and body:
            o["summary"] = (body[:180] + "…") if len(body) > 180 else body

    for field in ("station", "province"):
        val = str(o.get(field) or "").strip()
        if val and _text_contains_sinhala(val):
            try:
                translated = (sanitize_police_translation_output(translate_sinhala_to_english(val)) or "").strip()
                if translated and not translated.startswith("❌") and "Translation unavailable" not in translated:
                    o[field] = translated[:120]
            except Exception:
                pass

    hier = o.get("hierarchy")
    if hier is not None and hier != "":
        if isinstance(hier, list):
            o["hierarchy"] = [
                _translate_block_for_pdf_english(str(line).strip())
                if _text_contains_sinhala(str(line).strip()) else str(line).strip()
                for line in hier
            ]
        else:
            hs = str(hier).strip()
            if _text_contains_sinhala(hs):
                o["hierarchy"] = _translate_block_for_pdf_english(hs)

    # Final Sinhala strip pass
    o["station"] = strip_sinhala_forcefully(o.get("station", ""))
    o["province"] = strip_sinhala_forcefully(o.get("province", ""))

    hier = o.get("hierarchy")
    if isinstance(hier, list):
        o["hierarchy"] = [strip_sinhala_forcefully(h) for h in hier if strip_sinhala_forcefully(h)]
    elif isinstance(hier, str):
        o["hierarchy"] = strip_sinhala_forcefully(hier)


def _normalize_incident_for_pdf(inc):
    """
    Normalize incident dict for institutional HTML/PDF generators.
    BUG FIX: Handles edge cases where inc is None or malformed.
    """
    if not isinstance(inc, dict):
        return {
            "body": str(inc).strip() if inc else "",
            "station": "Unknown",
            "summary": "",
            "province": "WESTERN",
            "hierarchy": [],
        }
    o = dict(inc)
    body = (
        o.get("body")
        or o.get("description")
        or o.get("text")
        or o.get("narrative")
        or o.get("english")
        or ""
    )
    o["body"] = str(body).strip()

    st = o.get("station") or o.get("police_station") or "Unknown"
    o["station"] = strip_sinhala_forcefully(str(st).strip())

    # Auto-complete hierarchy via station mapping
    try:
        mapped_info = get_station_info(o["station"])
        o["province"] = mapped_info.get("province", o.get("province", "WESTERN"))
        o["hierarchy"] = [mapped_info.get("dig", ""), mapped_info.get("div", "")]
    except Exception as map_err:
        logger.debug(f"Station mapping failed for '{o['station']}': {map_err}")
        o.setdefault("province", "WESTERN")
        o.setdefault("hierarchy", [])

    o["station"] = strip_sinhala_forcefully(o["station"])
    o["province"] = strip_sinhala_forcefully(o.get("province", "WESTERN"))
    if isinstance(o.get("hierarchy"), list):
        o["hierarchy"] = [strip_sinhala_forcefully(h) for h in o["hierarchy"] if strip_sinhala_forcefully(h)]

    summ = o.get("summary")
    if (not summ) and o["body"]:
        b = o["body"]
        o["summary"] = (b[:180] + "…") if len(b) > 180 else b
    else:
        o["summary"] = str(summ or "").strip()

    # Institutional formatting
    for key in ("body", "summary"):
        if o.get(key):
            o[key] = _fix_date_format_in_text(o[key])
            o[key] = _fix_time_format_in_text(o[key])
            o[key] = _format_currency_suffix(o[key])

    _ensure_pdf_english_incident(o)
    return o


# ══════════════════════════════════════════════════════════════════════════════
# TEXT REPORT PROCESSING
# ══════════════════════════════════════════════════════════════════════════════

def process_text_report(text, output_folder="outputs", progress_callback=None):
    """Process a raw text report with 100% local deterministic logic."""
    os.makedirs(output_folder, exist_ok=True)
    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Paste / පෙළ — නිස්සාරණය (regex)…"})

    extractor = SinhalaPoliceReportExtractor()
    data = extractor.extract_all_from_text(text)

    if "error" in data:
        return {"success": False, "error": data["error"]}

    report_date_range = data.get("header", {}).get(
        "report_period", f"Generated on {datetime.now().strftime('%d %B %Y')}"
    )
    report_date_range = _fix_date_format_in_text(report_date_range)

    extracted_cats = data.get("categories", {})
    category_summary = {str(i).zfill(2): {"count": 0, "incidents": [], "raw_incidents": []} for i in range(1, 30)}
    table_counts = {}

    def translate_batch_local(cat_num, cat_data):
        incidents = cat_data.get("incidents", [])
        if not incidents:
            return cat_num, (0, [], [])

        translated_items = []
        raw_texts = []

        for inc in incidents:
            sinhala_text = inc.get('description', '')
            if not sinhala_text:
                continue
            try:
                translation = translate_sinhala_to_english(sinhala_text)
                ts = (translation or "").strip()
                if not ts or ts.startswith("❌"):
                    raise RuntimeError("bad translation")
                translation = _fix_date_format_in_text(ts)
                formatted_inc = _normalize_incident_for_pdf({
                    "body": translation,
                    "summary": translation[:100] + "...",
                    "station": inc.get("police_station", "Unknown"),
                    "date": _fix_date_format_in_text(inc.get("date", "")),
                    "time": inc.get("time", ""),
                    "ctm": inc.get("time", ""),
                    "origin_block": inc.get("origin_block", "General"),
                })
                translated_items.append(f"STATION: {formatted_inc['station']}\n{translation}")
                raw_texts.append(formatted_inc)
            except Exception:
                fb = (sinhala_text or "").strip()[:8000]
                if len(fb) < 3:
                    continue
                formatted_inc = _normalize_incident_for_pdf({
                    "body": "[Sinhala — translation pending]\n" + fb,
                    "summary": fb[:100] + "...",
                    "station": inc.get("police_station", "Unknown"),
                    "date": _fix_date_format_in_text(inc.get("date", "")),
                    "time": inc.get("time", ""),
                    "ctm": inc.get("time", ""),
                    "origin_block": inc.get("origin_block", "General"),
                })
                translated_items.append(f"STATION: {formatted_inc['station']}\n{formatted_inc['body']}")
                raw_texts.append(formatted_inc)

        return cat_num, (len(translated_items), translated_items, raw_texts)

    with ThreadPoolExecutor(max_workers=_translate_pool_workers(8)) as executor:
        futures = {
            executor.submit(translate_batch_local, cat, cdata): cat
            for cat, cdata in extracted_cats.items()
        }
        for future in as_completed(futures):
            cat_num, (count, translated, raw) = future.result()
            padded_cat = str(cat_num).zfill(2)
            if padded_cat in category_summary:
                category_summary[padded_cat] = {"count": count, "incidents": translated, "raw_incidents": raw}
                table_counts[padded_cat] = count

    category_summary["table_counts"] = table_counts
    category_summary["date_range"] = report_date_range

    generated_pdfs = generate_institutional_reports(category_summary, output_folder)

    return {
        "success": True,
        "full_translation": "Text Extraction and Translation complete using 100% Local Logic.",
        "category_results": category_summary,
        "generated_pdfs": generated_pdfs,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SINHALA CATEGORY TRANSLATION
# ══════════════════════════════════════════════════════════════════════════════

def _translate_sinhala_incidents_for_category(padded_cat, incidents):
    """Translate one category's Sinhala extractor incidents to English rows."""
    from police_patterns import OFFICIAL_CASE_TABLE_CATEGORIES

    category_context = "Unknown"
    for full_name in OFFICIAL_CASE_TABLE_CATEGORIES:
        if full_name.startswith(padded_cat + "."):
            category_context = full_name
            break

    mgr = get_engine()
    translated_items = []
    raw_texts = []

    for inc in incidents:
        sinhala_text = inc.get("description", "") or ""
        if not sinhala_text.strip():
            continue
        try:
            sub_prompt = (
                f"Expertly translate this Sri Lanka Police incident record into professional English. "
                f"Maintain institutional style and formatting.\n\nOriginal Sinhala:\n{sinhala_text}"
            )
            translation = mgr.call_ai(sub_prompt, category_context=category_context)
            ts = (translation or "").strip()
            if not ts or ts.startswith("❌") or "Translation unavailable" in ts:
                raise RuntimeError("empty or error translation")

            ts = _fix_date_format_in_text(ts)
            ts = _fix_time_format_in_text(ts)
            ts = _format_currency_suffix(ts)
            translation = ts

            formatted_inc = _normalize_incident_for_pdf({
                "body": translation,
                "summary": (translation[:100] + "...") if len(translation) > 100 else translation,
                "station": inc.get("police_station", "Unknown"),
                "date": _fix_date_format_in_text(inc.get("date", "")),
                "time": inc.get("time", ""),
                "ctm": inc.get("time", ""),
                "financial_loss": str(inc.get("financial_loss", "") or "Nil"),
                "status": str(inc.get("status", "") or "Confirmed"),
                "victim_suspect_names": str(inc.get("victim_suspect_names", "") or "N/A"),
                "origin_block": inc.get("origin_block", "General"),
            })
            translated_items.append(f"STATION: {formatted_inc['station']}\n{translation}")
            raw_texts.append(formatted_inc)

        except Exception as e:
            logger.warning(f"[Pipeline] Translation failed for Cat {padded_cat}: {e}")
            fallback = (sinhala_text or "").strip()
            if len(fallback) < 3:
                continue
            fb = _fix_date_format_in_text(fallback[:8000])
            formatted_inc = _normalize_incident_for_pdf({
                "body": "[Sinhala — translation pending]\n" + fb,
                "summary": fb[:140] + ("…" if len(fb) > 140 else ""),
                "station": inc.get("police_station", "Unknown"),
                "date": _fix_date_format_in_text(inc.get("date", "")),
                "time": inc.get("time", ""),
                "ctm": inc.get("time", ""),
                "financial_loss": str(inc.get("financial_loss", "") or "Nil"),
                "status": str(inc.get("status", "") or "Pending translation"),
                "victim_suspect_names": str(inc.get("victim_suspect_names", "") or "N/A"),
                "origin_block": inc.get("origin_block", "General"),
            })
            translated_items.append(f"STATION: {formatted_inc['station']}\n{formatted_inc['body']}")
            raw_texts.append(formatted_inc)

    return padded_cat, translated_items, raw_texts


# ══════════════════════════════════════════════════════════════════════════════
# SINHALA-FIRST PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def process_pdf_sinhala_split_then_translate(pdf_path, progress_callback=None, output_folder="outputs"):
    """
    Sinhala-first flow:
    1. PDF → Full Sinhala (OCR / Gemini File API)
    2. Split General / Security (Sinhala markers)
    3. Extract 01–29 per section (Sinhala), then translate to English
    4. Generate General + Security institutional PDFs
    """
    from sinhala_section_splitter import normalize_sinhala
    from translator_pipeline import split_sinhala_document

    os.makedirs(output_folder, exist_ok=True)
    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Step 1: PDF → Full Sinhala text..."})

    raw_sinhala = extract_pdf_to_sinhala(pdf_path)
    if not raw_sinhala or len(raw_sinhala.strip()) < 80:
        raise RuntimeError("Sinhala text insufficient or OCR failed.")

    clean = normalize_sinhala(raw_sinhala)
    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Translating incidents to English..."})

    general_sinhala, security_sinhala = split_sinhala_document(clean)

    extractor = SinhalaPoliceReportExtractor()
    merged_by_cat = {str(i).zfill(2): [] for i in range(1, 30)}
    report_period = ""

    blocks = [("General", general_sinhala), ("Security", security_sinhala)]
    for label, block in blocks:
        if not block or len(block.strip()) < 20:
            continue
        _safe_callback(progress_callback, "OCR_UPDATE", {"msg": f"Step 3: {label} — splitting sections..."})
        data = extractor.extract_all_from_text(block)
        if isinstance(data, dict) and data.get("error"):
            continue
        if not report_period:
            report_period = (data.get("header") or {}).get("report_period", "") or ""
        for cid, cdata in (data.get("categories") or {}).items():
            pad = str(cid).zfill(2)
            if pad not in merged_by_cat:
                continue
            for inc in cdata.get("incidents") or []:
                inc["origin_block"] = label
                merged_by_cat[pad].append(inc)

    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Step 4: Translating categories..."})

    category_summary = {str(i).zfill(2): {"count": 0, "incidents": [], "raw_incidents": []} for i in range(1, 30)}
    table_counts = {}
    preview_chunks = []

    with ThreadPoolExecutor(max_workers=_translate_pool_workers(12)) as executor:
        futures = {}
        for pad, inc_list in merged_by_cat.items():
            if not inc_list:
                table_counts[pad] = 0
                continue
            futures[executor.submit(_translate_sinhala_incidents_for_category, pad, inc_list)] = pad
        for future in as_completed(futures):
            pad, translated_items, raw_texts = future.result()
            category_summary[pad] = {
                "count": len(raw_texts),
                "incidents": translated_items,
                "raw_incidents": raw_texts,
            }
            table_counts[pad] = len(raw_texts)
            if raw_texts:
                _safe_callback(progress_callback, pad, category_summary[pad])
            preview_chunks.extend(translated_items)

    for pad in [str(i).zfill(2) for i in range(1, 30)]:
        if pad not in table_counts:
            table_counts[pad] = category_summary[pad]["count"]

    dr = _fix_date_format_in_text(report_period or f"Generated on {datetime.now().strftime('%d %B %Y')}")
    category_summary["table_counts"] = table_counts
    category_summary["date_range"] = dr

    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Step 5: Generating General / Security PDFs..."})

    generated_pdfs = generate_institutional_reports(category_summary, output_folder)

    full_translation = (
        "════════ Sinhala Pipeline: General+Security split & translated ════════\n"
        + "\n\n".join(preview_chunks)
        if preview_chunks
        else "(No incidents found — check Sinhala sections or extraction.)"
    )

    generated_words = []
    try:
        word_engine = WordReportEngine(templates_dir="sample")
        generated_words = word_engine.generate_reports(category_summary, output_folder)
    except Exception as e:
        logger.error(f"Word Generation failed: {e}")

    for p in generated_pdfs:
        cat = "General" if "General" in os.path.basename(p) else "Security"
        log_generated_file(p, "PDF", cat)
    for p in generated_words:
        cat = "General" if "General" in os.path.basename(p) else "Security"
        log_generated_file(p, "Word", cat)

    return {
        "success": True,
        "full_translation": full_translation,
        "category_results": category_summary,
        "generated_pdfs": generated_pdfs,
        "generated_words": generated_words,
    }


# ══════════════════════════════════════════════════════════════════════════════
# PARALLEL PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def process_category_worker(cat_num, title, content, progress_callback=None):
    """Worker function for parallel processing of a single category."""
    if "Nil" in content or len(content.strip()) < 15:
        data = {"count": 0, "incidents": [], "raw_incidents": []}
        _safe_callback(progress_callback, cat_num, data)
        return cat_num, data

    from police_patterns import INCIDENT_START_PATTERN
    incident_texts = []

    raw_lines = content.strip().split('\n')
    current_inc = []
    for line in raw_lines:
        if re.search(INCIDENT_START_PATTERN, line, re.IGNORECASE):
            if current_inc:
                incident_texts.append('\n'.join(current_inc))
            current_inc = [line]
        else:
            current_inc.append(line)
    if current_inc:
        incident_texts.append('\n'.join(current_inc))

    if not incident_texts:
        incident_texts = [content]

    translated_incidents = []
    raw_incidents_data = []
    mgr = get_engine()

    for inc_text in incident_texts:
        if mgr.mode == "triple":
            logger.info(f"  [AI-Triple] Processing incident in Cat {cat_num}...")
            results_json = mgr.triple_refine_pipeline(inc_text)
        else:
            logger.info(f"  [AI-Fast] Processing incident in Cat {cat_num}...")
            user_blob = (
                f"Official table category number for this block: {str(cat_num).zfill(2)}.\n\n"
                f"Incident text:\n{inc_text}"
            )
            results_json = mgr.call_ai(user_blob, system_prompt=INCIDENT_JSON_SYSTEM_PROMPT)

        english_data = _parse_incident_ai_response(results_json)
        st = english_data.get("station", "Unknown Station")
        desc = english_data.get("description", "No description")

        translated_incidents.append(f"STATION: {st}\n{desc}")
        raw_incidents_data.append({
            "station": st,
            "summary": english_data.get("summary", desc[:150] + "..."),
            "body": desc,
            "hierarchy": [english_data.get("division", "Unknown")],
            "province": english_data.get("province", "WESTERN"),
            "date": english_data.get("date", ""),
            "time": english_data.get("time", ""),
            "financial_loss": english_data.get("financial_loss", "Nil"),
            "status": english_data.get("status", "Confirmed"),
            "victim_suspect_names": english_data.get("victim_suspect_names", "N/A"),
        })

        save_translated_incident(
            report_type="Unified",
            incident_date=english_data.get("date", ""),
            station=st,
            sinhala=inc_text,
            english=desc,
            engine=f"Dual-Pipeline-{mgr.mode}",
        )

    data = {"count": len(translated_incidents), "incidents": translated_incidents, "raw_incidents": raw_incidents_data}
    _safe_callback(progress_callback, cat_num, data)
    return cat_num, data


def split_by_sections_go(raw_text):
    """Bridge to the high-performance Go-based section partitioner."""
    try:
        os.makedirs("tmp", exist_ok=True)
        tmp_input = os.path.join("tmp", "raw_text_split.txt")
        tmp_output = os.path.join("tmp", "partitioned_split.json")

        with open(tmp_input, "w", encoding="utf-8") as f:
            f.write(raw_text)

        go_cmd = ["go", "run", "main.go", "-input", tmp_input, "-output", tmp_output]
        subprocess.run(go_cmd, check=True, capture_output=True, timeout=60)

        with open(tmp_output, encoding="utf-8") as f:
            go_data = json.load(f)
            return [(sec["title"], sec["content"]) for sec in go_data.get("sections", [])]

    except subprocess.TimeoutExpired:
        logger.error("Go Partitioner timed out. Falling back to Python splitter.")
    except Exception as e:
        logger.warning(f"Go Partitioner failed ({e}). Falling back to Python splitter.")
    return split_by_sections(raw_text)


def process_pdf_parallel(pdf_path, progress_callback=None, output_folder="outputs"):
    """Parallel version of the 28-Category Pipeline for maximum speed."""
    os.makedirs(output_folder, exist_ok=True)

    logger.info("[Institutional-OCR] Stage 1: Gemini High-Fidelity Extraction...")
    from machine_translator import extract_pdf_to_sinhala

    try:
        raw_text = extract_pdf_to_sinhala(pdf_path)
    except Exception as e:
        logger.warning(f"Gemini extraction failed: {e}. Falling back to Local OCR.")
        raw_text = ""

    if len(raw_text.strip()) < 150:
        try:
            engine = get_engine()
            raw_text = engine.call_vision_ai("Extract all Sinhala text from this page exactly.", pdf_path)
        except Exception as e:
            logger.error(f"Vision OCR fallback failed: {e}")

    if not raw_text or len(raw_text) < 10:
        return {"success": False, "error": "Could not extract text from PDF."}

    sections = split_by_sections_go(raw_text)
    category_summary = {str(i).zfill(2): {"count": 0, "incidents": [], "raw_incidents": []} for i in range(1, 30)}

    results = {}
    with ThreadPoolExecutor(max_workers=_translate_pool_workers(10)) as executor:
        future_to_cat = {
            executor.submit(
                process_category_worker,
                title.split(".")[0],
                title,
                content,
                progress_callback,
            ): title.split(".")[0]
            for title, content in sections
        }
        for future in as_completed(future_to_cat):
            cat_num, data = future.result()
            results[cat_num] = data
            category_summary[cat_num] = data

    full_translation_output = []
    for cat in sorted(results.keys()):
        for inc in results[cat]["incidents"]:
            full_translation_output.append(inc + "\n" + "-" * 40)

    full_translation = "\n".join(full_translation_output) or "No incidents found."
    generated_pdfs = generate_institutional_reports(category_summary, output_folder)

    return {
        "success": True,
        "full_translation": full_translation,
        "category_results": category_summary,
        "generated_pdfs": generated_pdfs,
        "warnings": [],
    }


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def match_province(name):
    """Fuzzy match province name to official canonical names."""
    from police_patterns import PROVINCE_LIST
    if not name:
        return "WESTERN"
    clean_name = str(name).strip().upper()
    if clean_name in PROVINCE_LIST:
        return clean_name
    variants = {
        "N. WESTERN": "NORTH WESTERN", "WAYAMBA": "NORTH WESTERN",
        "N. CENTRAL": "NORTH CENTRAL", "RAJARATA": "NORTH CENTRAL",
        "SABARA": "SABARAGAMUWA", "SOUTH": "SOUTHERN",
        "NORTH": "NORTHERN", "EAST": "EASTERN", "WEST": "WESTERN",
    }
    for v, canonical in variants.items():
        if v in clean_name:
            return canonical
    for p in PROVINCE_LIST:
        if p in clean_name or clean_name in p:
            return p
    return "WESTERN"


def _ordinal(day):
    """Convert a day number to ordinal string: 1 → '1st', 2 → '2nd', etc."""
    day = int(day)
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"


def _fix_date_format_in_text(text):
    """
    Convert numeric date formats → English ordinal format.
    2026.03.20 → 20th of March 2026
    20.03.2026 → 20th of March 2026
    """
    if not text:
        return text

    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    def replace_ymd(match):
        y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= m <= 12 and 1 <= d <= 31:
            return f"{_ordinal(d)} of {month_names[m]} {y}"
        return match.group(0)

    def replace_dmy(match):
        d, m, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= m <= 12 and 1 <= d <= 31:
            return f"{_ordinal(d)} of {month_names[m]} {y}"
        return match.group(0)

    text = re.sub(r'(\d{4})[./\-](\d{1,2})[./\-](\d{1,2})', replace_ymd, text)
    text = re.sub(r'(\d{1,2})[./\-](\d{1,2})[./\-](\d{4})', replace_dmy, text)
    return text


def _fix_time_format_in_text(text):
    """Ensure all time strings follow the official 'HHMM hrs' format."""
    if not text:
        return text
    text = re.sub(r'\b(\d{2}):(\d{2})\s+hrs\b', r'\1\2 hrs', text)
    text = re.sub(r'\b(\d{2}):(\d{2})\b', r'\1\2 hrs', text)
    text = re.sub(r'\b(\d{4})hrs\b', r'\1 hrs', text)
    return text


def _format_currency_suffix(text):
    """Ensure all Rs. values end with official '/=' suffix if missing."""
    if not text:
        return text

    def add_suffix(match):
        val = match.group(0).strip()
        if not val.endswith('/=') and not val.endswith('/-'):
            return f"{val}/="
        return val

    return re.sub(r'Rs\.?\s*[\d,]+(?:\.\d{1,2})?', add_suffix, text)


def _is_english_text(text: str) -> bool:
    """Check if text is predominantly English vs Sinhala."""
    sinhala_chars = sum(1 for c in text if '\u0D80' <= c <= '\u0DFF')
    return sinhala_chars < len(text) * 0.05


# ══════════════════════════════════════════════════════════════════════════════
# KAGGLE-CLOUD HYBRID PIPELINE (BUG FIXED)
# ══════════════════════════════════════════════════════════════════════════════

def process_pdf_kaggle_cloud_hybrid(pdf_path, progress_callback=None, output_folder="outputs"):
    """
    HIGH-FIDELITY HYBRID PIPELINE:
    1. Kaggle (Surya OCR) → Streams raw Sinhala/English text.
    2. Local Machine → Dispatches Cloud AI (GitHub/Groq/OpenRouter) per page.
    3. Cloud AI → Final Institutional Refinement & General/Security Categorization.

    BUG FIX: Translation logic was nested inside `if progress_callback:` block.
              Now runs unconditionally; callback is optional.
    """
    os.makedirs(output_folder, exist_ok=True)
    mgr = get_engine()

    category_summary = {str(i).zfill(2): {"count": 0, "incidents": [], "raw_incidents": []} for i in range(1, 30)}
    full_preview_text = []

    logger.info(f"[Kaggle-Cloud-Hybrid] Starting: {os.path.basename(pdf_path)}")
    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Connecting to Kaggle High-Speed GPU Server..."})

    from local_ocr_tool import extract_text_from_pdf

    try:
        pages_text = extract_text_from_pdf(
            pdf_path,
            progress_callback=lambda m: _safe_callback(progress_callback, "OCR_UPDATE", {"msg": m}),
        )
    except Exception as e:
        logger.error(f"OCR Error: {e}")
        return {"success": False, "error": str(e)}

    for page_idx, sinhala_text in enumerate(pages_text):
        if not sinhala_text or len(sinhala_text.strip()) < 10:
            continue

        msg = f"Refining Page {page_idx + 1}/{len(pages_text)} using Cloud AI (GitHub/Groq)..."
        logger.info(f"  ✨ {msg}")
        _safe_callback(progress_callback, "OCR_UPDATE", {"msg": msg})

        # ── BUG FIX: This block was inside `if progress_callback:` ───────────
        refiner_prompt = (
            f"SOURCE TEXT (POLICE INCIDENT REPORT):\n{sinhala_text}\n\n"
            "TASK:\n"
            "1. Translate/Refine this text into institutional Sri Lanka Police English.\n"
            "2. Categorize every incident found into one of the 29 official categories.\n"
            "3. IMPORTANT: For each incident, explicitly label it as [GENERAL] or [SECURITY].\n"
            "   - SECURITY: Recovery of Arms/Ammunition, Subversive activities, Terrorism.\n"
            "   - GENERAL: Serious crimes, accidents, narcotics (04-29).\n"
            "4. FORMAT: Return each incident starting with a category header like "
            "'## CATEGORY 04: HOMICIDE [GENERAL]'\n"
            "   Then: 'STATION: [Name]. [Description including date/time/loss/status]'.\n"
        )

        try:
            refined_text = mgr.call_ai(
                refiner_prompt,
                system_prompt="You are a Sri Lanka Police Senior Data Architect.",
                timeout=120,
            )
        except Exception as ai_err:
            logger.warning(f"Cloud AI call failed on page {page_idx + 1}: {ai_err}")
            refined_text = "❌"

        if not refined_text or refined_text.startswith("❌"):
            is_en = _is_english_text(sinhala_text)
            if is_en:
                logger.info(f"  Source text already English. Skipping refinement for page {page_idx + 1}.")
                refined_text = sinhala_text
            else:
                logger.warning(f"  Cloud refinement failed on page {page_idx + 1}. Using draft text.")
                refined_text = sinhala_text

        full_preview_text.append(refined_text)

        # Parse this page's results and merge into category_summary
        parsed_page = _extract_categories_from_english(refined_text)
        page_cats = parsed_page.get("categories", {})

        for cat_num, data in page_cats.items():
            padded = str(cat_num).zfill(2)
            incidents = data.get("incidents", [])

            for inc in incidents:
                body_lower = (inc.get("description") or inc.get("body") or "").lower()
                origin = "Security" if padded in ["01", "02", "03"] else "General"
                if "[security]" in body_lower:
                    origin = "Security"

                norm_inc = _normalize_incident_for_pdf({
                    "station": inc.get("police_station", "Unknown"),
                    "body": inc.get("description", ""),
                    "origin_block": origin,
                    "province": match_province(inc.get("police_station", "")),
                    "date": inc.get("date", ""),
                    "time": inc.get("time", ""),
                    "financial_loss": inc.get("financial_loss", "Nil"),
                    "status": inc.get("status", "Confirmed"),
                })

                category_summary[padded]["raw_incidents"].append(norm_inc)
                category_summary[padded]["incidents"].append(
                    f"STATION: {norm_inc['station']}\n{norm_inc['body']}"
                )
                category_summary[padded]["count"] += 1

        _safe_callback(progress_callback, "PAGE_DONE", {"page_index": page_idx})
        # ─────────────────────────────────────────────────────────────────────

    logger.info("  Processing complete. Generating Institutional Reports...")
    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Generating General & Security PDFs..."})

    generated_pdfs = generate_institutional_reports(category_summary, output_folder)

    return {
        "success": True,
        "full_translation": "\n\n".join(full_preview_text),
        "category_results": category_summary,
        "generated_pdfs": generated_pdfs,
    }


# ══════════════════════════════════════════════════════════════════════════════
# ENGLISH CATEGORY EXTRACTOR
# ══════════════════════════════════════════════════════════════════════════════

def _incidents_from_markdown_table_rows(body_text: str) -> list:
    """Split markdown-style pipe rows into separate incidents."""
    rows_out = []
    for raw_line in body_text.split("\n"):
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        core = line.strip()
        if core.replace("|", "").replace("-", "").replace(" ", "") == "":
            continue
        parts = [p.strip() for p in core.strip("|").split("|")]
        parts = [p for p in parts if p]
        if len(parts) < 3:
            continue
        first = parts[0]
        if re.match(r"^[\-:]+$", first):
            continue
        low = first.lower()
        if low in ("serial", "s/n", "no", "location", "date", "time", "incident", "reported"):
            continue
        desc = " | ".join(parts)
        if len(desc) < 12:
            continue
        station = parts[1] if len(parts) > 1 else "Unknown"
        if re.match(r"^\d{1,2}$", station) and len(parts) > 2:
            station = parts[2]
        date = ""
        t_m = re.search(r"(\d{4}[./-]\d{2}[./-]\d{2})", desc)
        if t_m:
            date = t_m.group(1)
        rows_out.append({
            "police_station": (station or "Unknown")[:120],
            "division": "",
            "date": date,
            "time": "",
            "description": desc,
            "financial_loss": "",
            "status": "",
            "victim": {},
            "suspect": {},
        })
    return rows_out


def _extract_categories_from_english(text: str) -> dict:
    """Parse Gemini English output by numbered category headers."""
    EN_CATS = {
        "01": "Terrorist Activities",
        "02": "Recovery of Arms & Ammunition",
        "03": "Protests & Strikes",
        "04": "Homicides",
        "05": "Robberies",
        "06": "Thefts of Vehicles",
        "07": "Property Thefts",
        "08": "House Breaking & Theft",
        "09": "Rape & sexual Abuse",
        "10": "Fatal accidents",
        "11": "Unidentified dead bodies & suspicious dead bodies",
        "12": "Police Accidents",
        "13": "Serious injuries of Police officers and Damages to Police Property",
        "14": "Misconducts of Police officers",
        "15": "Deaths of Police officers",
        "16": "Hospital admission of SGOO",
        "17": "Passing away of close Relatives of SGOO",
        "18": "Passing away of close relatives of retired SGOO",
        "19": "Detections of Narcotics & Illicit Liquor",
        "20": "Large quantities of drugs/alcohol seized",
        "21": "Arrests",
        "22": "Arresting of Tri-forces Members",
        "23": "Disappearances",
        "24": "Suicides",
        "25": "Incidents regarding Foreigners",
        "26": "Wild elephant attacks & Deaths of wild elephants",
        "27": "Deaths due to drowning",
        "28": "Incidents of Fire",
        "29": "Others",
    }

    # Save debug copy
    try:
        debug_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp", "gemini_debug.txt")
        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
        with open(debug_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(text)
        logger.debug(f"Gemini output ({len(text)} chars) saved to: {debug_path}")
    except Exception:
        pass

    cat_header_re = re.compile(
        r'(?:^|\n)[ \t*#-]*(?:Category\s+|Serial\s*No\.?\s*)?(\d{1,2})[\.\s\)\]\-\:]+[ \t]*([^\n:\d]{3,}[^\n]*)',
        re.IGNORECASE,
    )

    matches = list(cat_header_re.finditer(text))
    logger.debug(f"Category headers found: {[m.group(1).zfill(2) for m in matches]}")

    blocks = {}
    official_counts = {}

    for i, m in enumerate(matches):
        cat_num = m.group(1).zfill(2)
        header_text = m.group(2)

        count_match = re.search(
            r'(?:[:-]\s*|Reported\s*:?\s*)(\d{1,3})(?:(?:\s*,.*)?|\s*\*+)?$',
            header_text, re.IGNORECASE,
        )
        if count_match:
            official_counts[cat_num] = int(count_match.group(1))
        elif re.search(r'(?:None|Nil|00)', header_text, re.IGNORECASE):
            official_counts[cat_num] = 0

        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block_text = text[start:end].strip()
        if cat_num not in blocks and 1 <= int(cat_num) <= 28:
            blocks[cat_num] = block_text

    categories_out = {}
    total_incidents = 0

    for cat_num in [str(i).zfill(2) for i in range(1, 30)]:
        block = blocks.get(cat_num, "")
        incidents = []

        if block:
            header_line = block.split('\n')[0]
            header_clean = re.sub(r'[\*#]', '', header_line).strip()
            is_nil = bool(re.search(
                r'\b(None|Nil|NIL)\b|:\s*(None|Nil|NIL)\s*\.?$',
                header_clean, re.IGNORECASE,
            ))

            if not is_nil:
                lines = block.split('\n')
                body_lines = []
                for line in lines[1:]:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if re.match(r'^[\|\-\s]+$', stripped):
                        continue
                    if stripped.startswith('|'):
                        cells = [c.strip() for c in stripped.split('|') if c.strip()]
                        meaningful = [c for c in cells if len(c) > 3 and not re.match(r'^\d+\.?$', c)]
                        if meaningful:
                            body_lines.append(' | '.join(meaningful))
                    else:
                        body_lines.append(stripped)

                body_text = '\n'.join(body_lines).strip()

                if len(body_text) >= 20:
                    table_rows = _incidents_from_markdown_table_rows(body_text)
                    if len(table_rows) >= 2:
                        incidents.extend(table_rows)
                    else:
                        date = ""
                        d_m = re.search(r'(\d{4}[./]\d{2}[./]\d{2})', body_text)
                        if d_m:
                            date = d_m.group(1)

                        station = "Unknown"
                        s_m = re.search(
                            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Police\s+)?Station)\b',
                            body_text,
                        )
                        if s_m:
                            station = s_m.group(1)

                        one = {
                            "police_station": station,
                            "division": "",
                            "date": date,
                            "time": "",
                            "description": body_text,
                            "financial_loss": "",
                            "status": "",
                            "victim": {},
                            "suspect": {},
                        }
                        incidents.append(table_rows[0] if len(table_rows) == 1 else one)

        categories_out[cat_num] = {
            "category_number": cat_num,
            "category_name": EN_CATS.get(cat_num, ""),
            "incidents": incidents,
            "summary": {
                "total_incidents": len(incidents),
                "status": "None" if not incidents else "",
            },
        }
        total_incidents += len(incidents)

    date_range = ""
    dr_m = re.search(
        r'(\d{4})\s*hrs?\s*on\s*(.{5,40}?)\s*to\s*(\d{4})\s*hrs?\s*on\s*(.{5,40}?)(?:\.|$|\n)',
        text, re.IGNORECASE,
    )
    if dr_m:
        date_range = (
            f"From {dr_m.group(1)} hrs on {dr_m.group(2).strip()} "
            f"to {dr_m.group(3)} hrs on {dr_m.group(4).strip()}"
        )

    logger.info(f"English extractor found {total_incidents} incidents across all categories.")

    return {
        "header": {"report_period": date_range, "report_title": "Daily Incident Report"},
        "categories": categories_out,
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "total_categories": 29,
            "total_incidents": total_incidents,
            "official_counts": official_counts,
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# HYPER HYBRID PIPELINE (PRIMARY ENTRY POINT)
# ══════════════════════════════════════════════════════════════════════════════

def _apply_fast_complete_env_defaults():
    """High-speed + full output environment defaults."""
    os.environ.setdefault("AI_DISPATCH_MODE", "race")
    os.environ.setdefault("TESSERACT_PAGE_WORKERS", "4")
    os.environ.setdefault("TESSERACT_DPI", "300")
    os.environ.setdefault("TRANSLATE_WORKERS", "12")
    os.environ.setdefault("GITHUB_TURBO_CHUNK_CHARS", "24000")


def _effective_sinhala_first(sinhala_first: bool) -> bool:
    """SINHALA_FIRST_PIPELINE=1 forces Sinhala split-first; =0 forces Turbo-first."""
    env = (os.getenv("SINHALA_FIRST_PIPELINE") or "").strip().lower()
    if env in ("1", "true", "yes", "on"):
        return True
    if env in ("0", "false", "no", "off"):
        return False
    return sinhala_first


def _save_split_json_files(data, output_folder, pdf_path):
    """Split and save one-shot extraction results into General and Security JSON files."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        security_ids = {"01", "02", "03"}

        header = data.get("header", {})
        categories = data.get("categories", {})

        gen_data = {"header": header, "categories": {}}
        sec_data = {"header": header, "categories": {}}

        for cat_id, cat_val in categories.items():
            padded = str(cat_id).zfill(2)
            target = sec_data if padded in security_ids else gen_data
            target["categories"][padded] = cat_val

        gen_path = os.path.join(output_folder, f"{base_name}_General_Data_{timestamp}.json")
        sec_path = os.path.join(output_folder, f"{base_name}_Security_Data_{timestamp}.json")

        with open(gen_path, "w", encoding="utf-8") as f:
            json.dump(gen_data, f, indent=4, ensure_ascii=False)
        with open(sec_path, "w", encoding="utf-8") as f:
            json.dump(sec_data, f, indent=4, ensure_ascii=False)

        logger.info(f"[PIPELINE] Saved split JSON: {os.path.basename(gen_path)}, {os.path.basename(sec_path)}")
        return [gen_path, sec_path]
    except Exception as e:
        logger.error(f"Failed to save split JSON files: {e}")
        return []


def process_pdf_hyper_hybrid(
    pdf_path,
    progress_callback=None,
    output_folder="outputs",
    force_local_ocr=True,
    sinhala_first=False,
    fast_complete=True,
):
    """
    Primary pipeline entry point.

    Fast+complete (default): Turbo JSON first (Gemini one-shot), fastest path.
    Sinhala-first (slower):  pass sinhala_first=True or set SINHALA_FIRST_PIPELINE=1.
    Fallback chain: Sinhala-first → Turbo → Full-document English → parse categories.
    """
    os.makedirs(output_folder, exist_ok=True)

    if fast_complete:
        _apply_fast_complete_env_defaults()
        logger.info("[Fast-Complete] Turbo-first, parallel API/OCR defaults.")

    sinhala_first = _effective_sinhala_first(sinhala_first)

    if sinhala_first:
        try:
            logger.info("[Sinhala-First] General/Security Sinhala split → extract → translate → PDF...")
            return process_pdf_sinhala_split_then_translate(pdf_path, progress_callback, output_folder)
        except Exception as sf_err:
            logger.warning(f"Sinhala-first pipeline failed ({sf_err}). Falling back to Turbo…")
            _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Sinhala-first failed — Turbo mode..."})

    # ── PRIMARY: Gemini Turbo Mode ─────────────────────────────────────────
    try:
        logger.info("[Turbo-Pipeline] Stage 1: Gemini One-Shot High-Speed Extraction...")
        _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Executing High-Speed Gemini Turbo extraction..."})

        from machine_translator import MachineTranslator
        translator = MachineTranslator()
        turbo_data = translator.extract_pdf_to_json_turbo(pdf_path)

        category_summary = {str(i).zfill(2): {"count": 0, "incidents": [], "raw_incidents": []} for i in range(1, 30)}
        raw_full_text = ""

        for cat_num, cat_info in turbo_data.get("categories", {}).items():
            inc_list = cat_info.get("incidents", [])
            padded_cat = str(cat_num).zfill(2)
            if padded_cat in category_summary:
                # Categories 01/02/03 = Security; everything else = General
                default_origin = "Security" if padded_cat in ("01", "02", "03") else "General"
                tagged_list = []
                for x in inc_list:
                    if isinstance(x, dict):
                        x.setdefault("origin_block", default_origin)
                    tagged_list.append(x)
                norm_list = [_normalize_incident_for_pdf(x) for x in tagged_list]
                # Ensure origin_block survives normalization
                for inc in norm_list:
                    inc.setdefault("origin_block", default_origin)
                category_summary[padded_cat]["count"] = len(norm_list)
                category_summary[padded_cat]["raw_incidents"] = norm_list

                formatted_incidents = []
                for inc in norm_list:
                    body = inc.get("body", "")
                    st = inc.get("station", "Unknown")
                    formatted_incidents.append(f"STATION: {st}\n{body}")
                    raw_full_text += f"STATION: {st}\n{body}\n" + "-" * 40 + "\n"

                category_summary[padded_cat]["incidents"] = formatted_incidents
                if norm_list:
                    _safe_callback(progress_callback, padded_cat, category_summary[padded_cat])

        report_date_range = turbo_data.get("header", {}).get(
            "date_range", f"Generated on {datetime.now().strftime('%d %B %Y')}"
        )
        category_summary["date_range"] = report_date_range
        category_summary["table_counts"] = {
            k: v["count"] for k, v in category_summary.items()
            if k not in ["date_range", "table_counts"]
        }

        logger.info("[Turbo-Pipeline] Stage 2: Generating Institutional Reports...")
        _save_split_json_files(turbo_data, output_folder, pdf_path)
        generated_pdfs = generate_institutional_reports(category_summary, output_folder)

        return {
            "success": True,
            "full_translation": raw_full_text or "No incidents found.",
            "category_results": category_summary,
            "generated_pdfs": generated_pdfs,
            "summary_table": _extract_summary_table(category_summary, raw_full_text),
        }

    except Exception as turbo_err:
        logger.warning(f"Turbo Mode failed ({turbo_err}). Falling back to Hybrid logic...")
        _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Turbo failed. Using one-shot translate fallback..."})

    # ── FALLBACK: Full-Document One-Shot Translation ────────────────────────
    logger.info("[Gemini-Fallback] Stage 1: Full-Document One-Shot Translation...")
    from machine_translator import MachineTranslator
    translator = MachineTranslator()

    full_text = ""
    try:
        logger.info("[Fallback] Page-by-page high-fidelity translation...")
        _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Starting Page-by-Page translation..."})
        full_text = translator.translate_full_sinhala_pdf_to_english(
            pdf_path, progress_callback=progress_callback
        )
        full_text = sanitize_police_translation_output(full_text)
        logger.info(f"[Fallback] OK: Translation complete ({len(full_text)} chars).")
    except Exception as e:
        logger.warning(f"[Fallback] translate_full_sinhala_pdf_to_english failed ({e}). Trying Sinhala OCR...")
        try:
            raw_sinhala = translator.extract_pdf_sinhala_with_gemini(pdf_path)
            if raw_sinhala and len(raw_sinhala.strip()) > 50:
                chunks = _split_large_text(raw_sinhala, 10000, overlap=1000)
                eng_parts = [
                    translator.translate_sinhala_document_to_english(chunk, idx + 1, len(chunks))
                    for idx, chunk in enumerate(chunks)
                ]
                full_text = sanitize_police_translation_output("\n\n".join(eng_parts))
            else:
                full_text = raw_sinhala or ""
        except Exception as e2:
            logger.error(f"[Fallback] All translation methods failed: {e2}")

    if not full_text or len(full_text.strip()) < 50:
        return {"success": False, "error": "Could not extract or translate text from PDF."}

    logger.info("[Fallback] Stage 2: Parsing English categories from full translation...")
    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Parsing 28 categories from translated text..."})

    parsed = _extract_categories_from_english(full_text)
    _save_split_json_files(parsed, output_folder, pdf_path)
    extracted_cats = parsed.get("categories", {})
    report_date_range = parsed.get("header", {}).get("report_period", "") or \
        f"Generated on {datetime.now().strftime('%d %B %Y')}"
    report_date_range = _fix_date_format_in_text(report_date_range)

    category_summary = {str(i).zfill(2): {"count": 0, "incidents": [], "raw_incidents": []} for i in range(1, 30)}
    official_counts = parsed.get("metadata", {}).get("official_counts", {})

    for cat_num, cat_data in extracted_cats.items():
        padded = str(cat_num).zfill(2)
        incidents_raw = cat_data.get("incidents", [])
        if padded not in category_summary:
            continue

        formatted_incidents = []
        raw_incidents_out = []

        for inc in incidents_raw:
            desc = (
                inc.get("description") or inc.get("body")
                or inc.get("text") or inc.get("narrative") or ""
            )
            if not desc or len(str(desc).strip()) < 5:
                continue
            desc = _fix_date_format_in_text(str(desc).strip())
            station = inc.get("police_station", "Unknown")
            province = match_province(inc.get("division", "WESTERN"))
            date_val = _fix_date_format_in_text(inc.get("date", ""))
            origin_val = "Security" if padded in ["01", "02", "03"] else "General"
            if "[security]" in str(desc).lower():
                origin_val = "Security"

            formatted_incidents.append(f"STATION: {station}\n{desc}")
            raw_incidents_out.append({
                "station": station,
                "body": desc,
                "summary": desc[:120] + "...",
                "province": province,
                "date": date_val,
                "time": inc.get("time", ""),
                "ctm": inc.get("time", ""),
                "hierarchy": inc.get("division", ""),
                "financial_loss": inc.get("financial_loss", "Nil"),
                "status": inc.get("status", "Confirmed"),
                "victim_suspect_names": inc.get("victim_suspect_names", "N/A"),
                "origin_block": origin_val,
            })

        count = len(raw_incidents_out) or official_counts.get(padded, 0)
        category_summary[padded] = {
            "count": count,
            "incidents": formatted_incidents,
            "raw_incidents": raw_incidents_out,
        }
        if count > 0:
            _safe_callback(progress_callback, padded, category_summary[padded])

    category_summary["table_counts"] = official_counts
    category_summary["date_range"] = report_date_range

    logger.info("[Fallback] Stage 3: Generating Institutional Reports...")
    _safe_callback(progress_callback, "OCR_UPDATE", {"msg": "Generating General & Security PDFs..."})

    try:
        generated_pdfs = generate_institutional_reports(category_summary, output_folder)
        logger.info(f"Institutional Reports Generated: {generated_pdfs}")
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        generated_pdfs = []

    full_translation_output = [
        inc + "\n" + "-" * 40
        for cat in sorted(k for k in category_summary if k not in ["table_counts", "date_range"])
        for inc in category_summary[cat].get("incidents", [])
    ]
    structured_block = (
        "\n".join(full_translation_output)
        if full_translation_output
        else "(No incidents passed structured filters.)"
    )

    try:
        preview_cap = int(os.getenv("TRANSLATION_PREVIEW_MAX_CHARS", "400000"))
    except ValueError:
        preview_cap = 400000

    raw_preview = (full_text or "").strip()
    if len(raw_preview) > preview_cap:
        raw_preview = raw_preview[:preview_cap] + "\n\n[… preview truncated …]"

    full_text_out = (
        "════════ FULL ENGLISH TRANSLATION (OCR + AI) ════════\n"
        + raw_preview
        + "\n\n════════ PARSED INCIDENTS (dashboard / PDFs) ════════\n"
        + structured_block
    )

    return {
        "success": True,
        "full_translation": full_text_out,
        "category_results": category_summary,
        "generated_pdfs": generated_pdfs,
        "summary_table": _extract_summary_table(category_summary, full_text or ""),
    }


# ══════════════════════════════════════════════════════════════════════════════
# INSTITUTIONAL REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_institutional_reports(category_summary, output_folder):
    """Enriched report mapping to fill both General and Security PDFs."""
    from general_report_engine import generate_general_report
    from general_report_engine import html_to_pdf as gen_to_pdf
    from police_incident_routing import apply_institutional_incident_routing
    from police_patterns import GENERAL_SECTIONS, PROVINCE_LIST, SECURITY_SECTIONS
    from web_report_engine_v2 import generate_security_report
    from web_report_engine_v2 import html_to_pdf as sec_to_pdf
    from word_report_engine import WordReportEngine

    category_summary = apply_institutional_incident_routing(category_summary)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gen_html = os.path.join(output_folder, f"General_Report_{timestamp}.html")
    gen_pdf  = os.path.join(output_folder, f"General_Report_{timestamp}.pdf")
    sec_html = os.path.join(output_folder, f"Security_Report_{timestamp}.html")
    sec_pdf  = os.path.join(output_folder, f"Security_Report_{timestamp}.pdf")

    default_dr = f"Generated {datetime.now().strftime('%d %B %Y')}"
    dr_raw = (category_summary.get("date_range") or "").strip()
    if dr_raw and _text_contains_sinhala(dr_raw):
        if (os.getenv("PDF_SKIP_SINHALA_BACKFILL") or "").strip().lower() not in ("1", "true", "yes"):
            logger.info("[PDF-EN] date_range contained Sinhala — translating for report header…")
            try:
                dr_en = sanitize_police_translation_output(translate_sinhala_to_english(dr_raw))
                if dr_en and not dr_en.startswith("❌") and "Translation unavailable" not in dr_en:
                    dr_raw = _fix_date_format_in_text(dr_en.strip())
            except Exception as e:
                logger.warning(f"[PDF-EN] date_range translation failed: {e}")

    date_range_final = dr_raw or default_dr

    general_data = {
        "date_range": date_range_final,
        "sections": [],
        "table_counts": category_summary.get("table_counts", {}),
    }
    security_data = {
        "date_range": date_range_final,
        "sections": [],
    }

    def get_provinces_structure():
        return [{"name": p, "incidents": [], "nil": True} for p in PROVINCE_LIST]

    gen_sections_map = {t: {"title": t, "provinces": get_provinces_structure()} for t in GENERAL_SECTIONS}
    sec_sections_map = {t: {"title": t, "provinces": get_provinces_structure()} for t in SECURITY_SECTIONS}

    for cat_num, data in category_summary.items():
        if cat_num in ["table_counts", "date_range"]:
            continue
        incidents = data.get("raw_incidents", [])
        if not incidents:
            continue

        logger.debug(f"Mapping Category {cat_num}: {len(incidents)} incidents")
        num = int(cat_num)

        for raw in incidents:
            inc = _normalize_incident_for_pdf(raw)
            origin = inc.get("origin_block", "General")

            # Safety net: categories 01/02/03 ALWAYS go to Security report
            # (origin_block may not be set correctly in all pipelines)
            if num in [1, 2, 3]:
                origin = "Security"

            target_map, target_sec = None, None

            if origin == "Security":
                if num == 1:
                    target_map, target_sec = sec_sections_map, SECURITY_SECTIONS[0]
                elif num == 3:
                    target_map, target_sec = sec_sections_map, SECURITY_SECTIONS[1]
                elif num == 2:
                    target_map, target_sec = sec_sections_map, SECURITY_SECTIONS[2]
                else:
                    target_map, target_sec = sec_sections_map, SECURITY_SECTIONS[3]
            else:
                if num in [4, 5, 6, 7, 8]:
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[0]
                elif num == 9:
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[1]
                elif num == 10:
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[2]
                elif num == 12:
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[3]
                elif num == 11:
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[4]
                elif num == 14:
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[5]
                elif num in [15, 16, 17, 18, 19]:
                    # 15=Deaths, 16=Hospital, 17=Relatives death, 18=Retired relatives, 19=Officers on Leave
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[6]
                elif num == 20:
                    # 20 = Narcotics/Illicit Liquor (NOT 19 — that is Officers on Leave)
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[7]
                elif num == 22:
                    # 22 = Tri-Forces (NOT 21 — that is Arrests → goes to OTHER)
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[8]
                elif num == 13:
                    desc = (inc.get("body") or "").lower()
                    if any(kw in desc for kw in ("property", "vehicle", "damage")):
                        target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[3]
                    else:
                        target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[6]
                else:
                    target_map, target_sec = gen_sections_map, GENERAL_SECTIONS[9]

            if target_map and target_sec:
                p_name = match_province(inc.get("province") or inc.get("division", "WESTERN"))
                placed = False
                for p_struct in target_map[target_sec]["provinces"]:
                    if p_struct["name"] == p_name:
                        p_struct["incidents"].append(inc)
                        p_struct["nil"] = False
                        placed = True
                        break
                if not placed:
                    for p_struct in target_map[target_sec]["provinces"]:
                        if p_struct["name"] == "WESTERN":
                            p_struct["incidents"].append(inc)
                            p_struct["nil"] = False
                            break

    general_data["sections"] = [gen_sections_map[t] for t in GENERAL_SECTIONS]
    security_data["sections"] = [sec_sections_map[t] for t in SECURITY_SECTIONS]

    paths = []

    try:
        generate_general_report(general_data, gen_html)
        gen_to_pdf(gen_html, gen_pdf)
        paths.append(gen_pdf)
        logger.info(f"General Report: {gen_pdf}")
    except Exception as e:
        logger.error(f"General Report Failed: {e}")

    try:
        generate_security_report(security_data, sec_html)
        sec_to_pdf(sec_html, sec_pdf)
        paths.append(sec_pdf)
        logger.info(f"Security Report: {sec_pdf}")
    except Exception as e:
        logger.error(f"Security Report Failed: {e}")

    try:
        word_engine = WordReportEngine(templates_dir="sample")
        word_paths = word_engine.generate_reports(category_summary, output_folder)
        paths.extend(word_paths)
        logger.info(f"Word Reports: {word_paths}")
    except Exception as e:
        logger.error(f"Word Report Generation Failed: {e}")

    return paths
