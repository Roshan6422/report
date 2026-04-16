import json
import os
import re
import time

from quota_manager import get_quota_mgr
from station_mapping import (
    enforce_terminology,
    get_institutional_prompt_snippet,
)

# Prefer Gemini 3 preview per https://ai.google.dev/gemini-api/docs; fall back to 2.0 if unavailable.
_DEFAULT_GEMINI_MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

# 29-row summary (අනු අංකය / සිද්ධිය / වාර්තා / විසඳූ / නොවිසඳු) — keep rows & counts aligned in EN output
POLICE_SUMMARY_TABLE_INSTRUCTIONS = """
OFFICIAL SUMMARY STATISTICS TABLE (29 rows × 5 columns):
- This is an official government data extraction task. 
- Keep exactly 29 rows (01–29); do not merge, skip, or omit any rows.
- Each numeric digit must stay in its exact column (reported | solved | unsolved).
- Translate Sinhala incident types into formal English legal/police terminology.
- Preserve the table as RAW text with " | " or TAB separators.
- Ensure 100% data fidelity for institutional reporting.
"""


def sanitize_police_translation_output(text: str) -> str:
    """
    Cloud models sometimes append safety refusals after a partial translation, or invent
    huge fake tables. Trim known refusal tails so parsing and the UI see real content.
    """
    if not text or not isinstance(text, str):
        return text
    t = text.rstrip()
    low = t.lower()
    # Cut at first major refusal if enough real content precedes it
    refusal_needles = (
        "i'm sorry, but i can't assist",
        "i’m sorry, but i can’t assist",
        "i am sorry, but i can't assist",
        "i am sorry, but i cannot assist",
        "i'm sorry, but i cannot assist",
        "i can't assist with that",
        "i can’t assist with that",
        "i cannot assist with this request",
        "as an ai language model, i cannot",
    )
    for needle in refusal_needles:
        j = low.find(needle)
        if j >= 800:
            t = t[:j].rstrip()
            low = t.lower()
            break
    return t


def _env_truthy(name: str, default: bool = False) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


def _is_gemini_quota_or_rate_limit(msg) -> bool:
    """True when Gemini cannot run due to quota / rate limits / exhausted keys (OCR may still help)."""
    if msg is None:
        return False
    s = str(msg).lower()
    if "429" in s or "resource_exhausted" in s:
        return True
    if "exhausted" in s and ("gemini" in s or "key" in s):
        return True
    if "quota" in s and any(x in s for x in ("exceed", "limit", "exhausted", "free_tier")):
        return True
    if "rate" in s and "limit" in s:
        return True
    return False


def _mt_skip_local_ocr_fallback(last_error=None) -> bool:
    """
    If True, do not run local Tesseract after Gemini fails (PDF→Gemini-only path).

    Exception: when ``MT_SKIP_LOCAL_OCR_FALLBACK=1`` but the failure is quota/rate-limit,
    we still allow Tesseract so the job can complete. Set ``MT_STRICT_PDF_GEMINI_ONLY=1``
    to never use Tesseract even then.
    """
    if not _env_truthy("MT_SKIP_LOCAL_OCR_FALLBACK"):
        return False
    if _env_truthy("MT_STRICT_PDF_GEMINI_ONLY"):
        return True
    if last_error is not None and _is_gemini_quota_or_rate_limit(last_error):
        print(
            "    [MT/OCR] ⚠️ Gemini quota/rate limit — allowing local Tesseract fallback "
            "(MT_SKIP_LOCAL_OCR_FALLBACK relaxed for this run; set MT_STRICT_PDF_GEMINI_ONLY=1 to block)."
        )
        return False
    return True


def _gemini_output_config(**extra):
    """Avoid truncated translations — API may still cap by tier; tune GEMINI_MAX_OUTPUT_TOKENS."""
    try:
        cap = int(os.environ.get("GEMINI_MAX_OUTPUT_TOKENS", "65536"))
    except ValueError:
        cap = 65536
    cfg = {"max_output_tokens": max(1024, cap)}
    cfg.update(extra)
    return cfg


def _gemini_generate_models():
    raw = os.environ.get("GEMINI_MODEL_LIST", "").strip()
    if raw:
        return [m.strip() for m in raw.split(",") if m.strip()]
    return list(_DEFAULT_GEMINI_MODELS)


def _ocr_pages_to_text(pages):
    if isinstance(pages, list):
        return "\n".join("" if p is None else str(p) for p in pages)
    return pages if pages is not None else ""


def _extract_pdf_text_pypdf2(pdf_path: str) -> str:
    """Extract embedded text from PDF (digital reports). Empty for pure scan PDFs."""
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(pdf_path)
        parts = []
        for page in reader.pages:
            try:
                t = page.extract_text()
            except Exception:
                t = ""
            parts.append(t or "")
        return "\n\n".join(parts).strip()
    except Exception as e:
        print(f"    [PDF/Text] PyPDF2 extraction failed: {e}")
        return ""


def _pdf_raw_text_for_ai_pipeline(pdf_path: str) -> str:
    """
    Text for Groq/OpenRouter/etc.: PyPDF2 first, then Tesseract if thin (unless PDF_EXTRACT_NO_TESSERACT=1).
    If ``MT_STRICT_PDF_GEMINI_ONLY=1``, Tesseract is skipped unless ``PDF_EXTRACT_ALLOW_LOCAL_OCR=1``.
    """
    raw = _extract_pdf_text_pypdf2(pdf_path)
    if len(raw.strip()) >= 80:
        print(f"    [PDF/AI] PyPDF2 extracted {len(raw)} chars.")
        return raw
    if _env_truthy("PDF_EXTRACT_NO_TESSERACT"):
        print(f"    [PDF/AI] PyPDF2 only: {len(raw)} chars (PDF_EXTRACT_NO_TESSERACT=1).")
        return raw.strip()
    if _env_truthy("MT_STRICT_PDF_GEMINI_ONLY") and not _env_truthy("PDF_EXTRACT_ALLOW_LOCAL_OCR"):
        print(
            "    [PDF/AI] PyPDF2 text thin; MT_STRICT_PDF_GEMINI_ONLY blocks local OCR. "
            "Use a text-based PDF or set PDF_EXTRACT_ALLOW_LOCAL_OCR=1 for scans."
        )
        return raw.strip()
    print("    [PDF/AI] PyPDF2 text thin; trying Tesseract for scanned PDF…")
    try:
        from local_ocr_tool import extract_text_from_pdf
        ocr_res = extract_text_from_pdf(pdf_path)
        ocr_text = _ocr_pages_to_text(ocr_res)
        if ocr_text and len(ocr_text.strip()) > len(raw.strip()):
            print(f"    [PDF/AI] Tesseract extracted {len(ocr_text)} chars.")
            return ocr_text.strip()
    except Exception as e:
        print(f"    [PDF/AI] Tesseract failed: {e}")
    return raw.strip()


def _pdf_extract_ai_engine() -> str:
    """
    PDF_EXTRACT_AI_ENGINE=openrouter|groq|github|aimlapi → no Gemini PDF upload; local text + chosen API.
    Unset or ``gemini`` → default Gemini File API path.
    """
    e = (os.getenv("PDF_EXTRACT_AI_ENGINE") or "").strip().lower()
    if e in ("openrouter", "groq", "github", "aimlapi"):
        return e
    return ""


def refine_tesseract_pages_with_ai(
    pages: list[str],
    engine: str,
    progress_callback=None,
) -> list[str]:
    """
    After Tesseract: optional fast AI pass per page (fixes OCR noise; keeps Sinhala).
    Env: ``TESSERACT_POST_AI_WORKERS`` (default 4) — parallel API calls.

    Pair with ``TESSERACT_FAST=1`` for faster OCR + AI polish vs slow ``TESSERACT_FULL_OCR=1``.
    """
    import concurrent.futures

    from ai_engine_manager import get_engine

    mgr = get_engine()
    try:
        workers = max(1, int(os.getenv("TESSERACT_POST_AI_WORKERS", "4").strip()))
    except ValueError:
        workers = 4

    sys_p = (
        "You repair noisy OCR of Sri Lanka Police Sinhala text. Output ONLY corrected Sinhala for this page. "
        "Do not translate to English. Preserve category numbers (01. 02. …), tables, and digits."
    )

    def job(idx_txt: tuple[int, str]) -> tuple[int, str]:
        i, txt = idx_txt
        if not txt or len(txt.strip()) < 8:
            return i, txt or ""
        user = f"OCR page {i + 1}:\n\n{txt}"
        res = mgr._dispatch_engine(engine, user, sys_p, 120)
        if res and not str(res).startswith("❌"):
            return i, str(res).strip()
        return i, txt

    n = len(pages)
    if progress_callback:
        progress_callback(f"[OCR+AI] Polishing {n} page(s) with {engine} ({workers} workers)…")
    print(f"    [OCR+AI] Post-processing {n} Tesseract page(s) with {engine}…")

    if workers > 1 and n > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(workers, n)) as ex:
            ordered = sorted(ex.map(job, list(enumerate(pages))), key=lambda x: x[0])
        return [t for _, t in ordered]

    out: list[str] = []
    for i, p in enumerate(pages):
        out.append(job((i, p))[1])
    return out


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)).strip())
    except ValueError:
        return default


def pdf_parts_for_gemini_upload(pdf_path: str) -> list[tuple]:
    """
    Long PDFs → several smaller PDF temp files so Gemini OCR/translate is less likely to truncate.

    Returns: list of (path, is_temp, part_i_1based, part_total, page_range_str)

    Env:
      GEMINI_OCR_PAGE_SPLIT=0 — disable splitting (single upload)
      GEMINI_OCR_PAGES_PER_PART — pages per chunk (default 6)
      GEMINI_OCR_SPLIT_MIN_PAGES — split only if page count > this (default 8)
    """
    if (os.environ.get("GEMINI_OCR_PAGE_SPLIT") or "1").strip().lower() in ("0", "false", "no", "off"):
        return [(pdf_path, False, 1, 1, "all")]

    try:
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        return [(pdf_path, False, 1, 1, "all")]

    try:
        reader = PdfReader(pdf_path)
        n = len(reader.pages)
    except Exception:
        return [(pdf_path, False, 1, 1, "all")]

    per = max(1, _env_int("GEMINI_OCR_PAGES_PER_PART", 6))
    min_pages = max(2, _env_int("GEMINI_OCR_SPLIT_MIN_PAGES", 8))

    if n <= min_pages:
        return [(pdf_path, False, 1, 1, f"1-{n}" if n else "1")]

    import tempfile

    total_parts = (n + per - 1) // per
    out: list[tuple] = []
    part_i = 0
    for start in range(0, n, per):
        part_i += 1
        end = min(start + per, n)
        w = PdfWriter()
        for p in range(start, end):
            w.add_page(reader.pages[p])
        fd, tmp = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        with open(tmp, "wb") as f:
            w.write(f)
        out.append((tmp, True, part_i, total_parts, f"{start + 1}-{end}"))
    return out


def _cleanup_pdf_parts(parts: list[tuple]) -> None:
    for path, is_temp, *_ in parts:
        if is_temp and path and os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass


def _normalize_turbo_cat_key(key):
    s = str(key).strip()
    if s.isdigit():
        return s.zfill(2)
    return s


def _merge_partial_turbo_json(merged, part):
    if not isinstance(part, dict):
        return
    pcats = part.get("categories") or {}
    mcats = merged.setdefault("categories", {})
    for key, val in pcats.items():
        sk = _normalize_turbo_cat_key(key)
        if not isinstance(val, dict):
            continue
        if sk not in mcats:
            mcats[sk] = {
                "name": val.get("name") or "",
                "incidents": list(val.get("incidents") or []),
            }
        else:
            sub = mcats[sk]
            if val.get("name") and not sub.get("name"):
                sub["name"] = val["name"]
            oi = sub.get("incidents") or []
            ni = val.get("incidents") or []
            sub["incidents"] = oi + ni
    ph = part.get("header") or {}
    if isinstance(ph, dict) and ph.get("date_range"):
        mh = merged.setdefault("header", {})
        if not mh.get("date_range"):
            mh["date_range"] = ph["date_range"]


def _load_gemini_key():
    """Load first available Gemini API key from gemini_keys.json."""
    try:
        keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
        if os.path.exists(keys_path):
            with open(keys_path) as f:
                keys = json.load(f)
            for k, v in keys.items():
                if k.startswith("Gemini") and v.strip():
                    return v.strip()
    except Exception:
        pass
    # Fallback to ENV if file is missing or empty
    return os.environ.get("GEMINI_API_KEY", "")

def _load_openai_keys():
    """Load all available OpenAI API keys from gemini_keys.json."""
    try:
        keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
        with open(keys_path) as f:
            keys = json.load(f)
        found = [v.strip() for k, v in keys.items() if k.startswith("OpenAI") and v.strip()]
        if found:
            return found
    except Exception:
        pass
    env_key = os.environ.get("OPENAI_API_KEY", "")
    return [env_key] if env_key else []


class MachineTranslator:
    """
    Dedicated Sinhala-to-English Machine Translation (MT) Engine.
    Priority order:
    1. Gemini AI File API      - Ultra-fast, high-fidelity, handles full PDFs.
    2. OpenAI GPT-4o-mini      - Fallback when Gemini quota is exhausted.
    3. Google Translate API    - Fast, requires internet, line-by-line.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_api_health():
        """
        Check status of all Gemini and GitHub keys.
        Returns a dict: { 'Gemini': { 'Key1': '✅ Active', ... }, 'GitHub': { ... } }
        """
        import concurrent.futures

        import requests
        from google import genai

        results = {"Gemini": {}, "GitHub": {}}

        # 1. Load keys
        gemini_keys = {}
        github_keys = {}
        keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
        github_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_keys.json")

        try:
            with open(keys_path) as f:
                gk = json.load(f)
                gemini_keys = {k: v for k, v in gk.items() if k.startswith("Gemini") and v.strip()}
        except Exception: pass

        try:
            with open(github_path) as f:
                github_keys = json.load(f)
        except Exception: pass

        def _test_gemini(name, key):
            try:
                client = genai.Client(api_key=key)
                primary = (_gemini_generate_models() or ["gemini-3-flash-preview"])[0]
                client.models.generate_content(model=primary, contents=["hi"])
                return name, "✅ Active"
            except Exception as e:
                s = str(e)
                if "429" in s: return name, "🔴 Rate Limited"
                if "400" in s or "401" in s or "API_KEY_INVALID" in s: return name, "❌ Invalid"
                return name, "⚠️ Error"

        def _test_github(name, key):
            try:
                url = "https://models.inference.ai.azure.com/chat/completions"
                headers = {"Authorization": f"Bearer {key}"}
                payload = {"messages": [{"role": "user", "content": "hi"}], "model": "gpt-4o-mini", "max_tokens": 5}
                r = requests.post(url, headers=headers, json=payload, timeout=5)

                rem = r.headers.get("x-ratelimit-remaining-requests")
                if rem:
                    try: get_quota_mgr().update_from_headers(name, int(rem))
                    except Exception: pass

                if r.status_code == 200: return name, "✅ Active"
                if r.status_code == 429: return name, "🔴 Rate Limited"
                return name, f"❌ Failed ({r.status_code})"
            except Exception: return name, "⚠️ Error"

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            g_futs = [executor.submit(_test_gemini, k, v) for k, v in gemini_keys.items()]
            gh_futs = [executor.submit(_test_github, k, v) for k, v in github_keys.items()]
            for f in concurrent.futures.as_completed(g_futs + gh_futs):
                name, status = f.result()
                if name.startswith("Gemini"):
                    usage = get_quota_mgr().get_status(name, "Gemini")
                    results["Gemini"][name] = f"{status} ({usage})"
                else:
                    usage = get_quota_mgr().get_status(name, "GitHub")
                    results["GitHub"][name] = f"{status} ({usage})"

        return results

    def _extract_pdf_to_json_turbo_text_ai(self, pdf_path: str, engine: str) -> dict:
        """Turbo JSON via PyPDF2/Tesseract text + Groq/OpenRouter/GitHub/AIML (no Gemini PDF upload)."""
        import time as _time

        from ai_engine_manager import _split_large_text, get_engine

        print(f"    [TURBO/{engine}] PDF → local text → {engine} JSON (set PDF_EXTRACT_AI_ENGINE)…")
        ocr_text = _pdf_raw_text_for_ai_pipeline(pdf_path)
        if not ocr_text or len(ocr_text.strip()) < 50:
            raise RuntimeError(
                "PDF_EXTRACT_AI_ENGINE: not enough text from PDF (use a text-based PDF or allow Tesseract)."
            )

        mgr = get_engine()
        turbo_chunk = int(os.getenv("GITHUB_TURBO_CHUNK_CHARS", "24000"))
        turbo_rules = (
            "PERSONA: You are a Professional Institutional Data Analyst for the Sri Lanka Police. "
            "TASK: Extract all incident records from the provided Sinhala daily report segment into structured English JSON. "
            "CONTEXT: This data is for official government reporting and documentation purposes. "
            "Direct, clinical, and neutral language is required.\n\n"
            "Technical Requirements:\n"
            "1. Output valid JSON in the specified 8-field schema.\n"
            "2. Translate all Sinhala narratives into CLINICAL, NEUTRAL English police terminology. "
            "Use terms like 'offence', 'suspect', 'complainant', 'investigation', 'recovery', 'detection'.\n"
            "3. Include ALL details: dates, times, financial values (Rs.), names, and addresses. Do NOT summarize or omit anything.\n"
            "4. Use formal titles: 'Complainant', 'Suspect', 'Status of Investigation'.\n"
            "5. NO Sinhala characters allowed in JSON values.\n"
            "6. Top-level structure: {'categories': {'01': {...}, ...}, 'header': {'date_range': '...'}}\n"
            "\n" + get_institutional_prompt_snippet() + "\n"
        )
        turbo_sys = (
            "You are a professional Sri Lanka Police Data Architect. "
            "Extract data with high precision. Use institutional, neutral language. "
            "Output complete JSON with full-length English descriptions — no omissions."
        )
        chunks = _split_large_text(ocr_text, turbo_chunk)
        merged = {"categories": {}, "header": {}}
        try:
            gh_pause = float(os.environ.get("GITHUB_CHUNK_COOLDOWN_SEC", "0"))
        except ValueError:
            gh_pause = 0.0
        gh_pause = max(0.0, min(gh_pause, 120.0))
        try:
            gh_turbo_timeout = int(os.getenv("GITHUB_TURBO_TIMEOUT_SEC", "360"))
        except ValueError:
            gh_turbo_timeout = 360
        gh_turbo_timeout = max(120, min(gh_turbo_timeout, 900))

        for idx, chunk in enumerate(chunks):
            if idx > 0 and gh_pause > 0:
                _time.sleep(gh_pause)
            seg_prompt = turbo_rules + f"SEGMENT {idx + 1} of {len(chunks)}:\n{chunk}"
            result = mgr._dispatch_engine(engine, seg_prompt, turbo_sys, gh_turbo_timeout)
            if not result or str(result).startswith("❌"):
                print(f"    [TURBO/{engine}] segment {idx + 1} primary failed: {str(result)[:180]}")
                result = mgr.translation_fallback_after_gemini_exhausted(
                    seg_prompt, turbo_sys, timeout=gh_turbo_timeout, skip_github=(engine == "github")
                )
            if not result or str(result).startswith("❌"):
                raise RuntimeError(f"TURBO/{engine} segment {idx + 1} failed: {str(result)[:200]}")
            clean_res = re.sub(r"```json\s*", "", str(result))
            clean_res = re.sub(r"```\s*", "", clean_res).strip()
            try:
                data = json.loads(clean_res)
            except json.JSONDecodeError:
                from json_repair_tool import repair_json

                data = json.loads(repair_json(clean_res))
            _merge_partial_turbo_json(merged, data)

        if merged.get("categories"):
            print(f"    [TURBO/{engine}] ✅ JSON merge complete.")
            return merged
        raise RuntimeError(f"TURBO/{engine}: no categories in merged JSON.")

    def _extract_sinhala_text_via_ai(self, pdf_path: str, engine: str) -> str:
        """Raw Sinhala line via local text + chosen API (no Gemini upload)."""
        from ai_engine_manager import _split_large_text, get_engine

        print(f"    [OCR/{engine}] PDF → local text → {engine} (Sinhala cleanup, PDF_EXTRACT_AI_ENGINE)…")
        raw = _pdf_raw_text_for_ai_pipeline(pdf_path)
        if len(raw.strip()) < 30:
            raise RuntimeError("PDF_EXTRACT_AI_ENGINE: insufficient text from PDF.")

        sys_p = (
            "You are digitizing a Sri Lanka Police incident report. Input may be noisy PDF/OCR text.\n"
            "Output ONLY corrected Sinhala — no English translation. Preserve 01. 02. … headers and tables.\n"
            "Keep the 28-row summary table as row-aligned lines; do not merge into prose."
        )
        mgr = get_engine()
        chunk_sz = max(4000, int(os.getenv("PDF_EXTRACT_SINHALA_CHUNK", "28000")))
        chunks = _split_large_text(raw, chunk_sz)
        out_parts = []
        for i, ch in enumerate(chunks):
            up = f"PART {i + 1} of {len(chunks)} — output only Sinhala for this part:\n\n{ch}"
            res = mgr._dispatch_engine(engine, up, sys_p, 300)
            if not res or str(res).startswith("❌"):
                res = mgr.translation_fallback_after_gemini_exhausted(up, sys_p, timeout=300, skip_github=False)
            if not res or str(res).startswith("❌"):
                raise RuntimeError(f"Sinhala extract via {engine} failed part {i + 1}: {res}")
            out_parts.append(str(res).strip())
        merged = "\n\n".join(out_parts)
        print(f"    [OCR/{engine}] ✅ Combined Sinhala text: {len(merged)} chars.")
        return merged

    def _translate_pdf_via_text_ai(self, pdf_path: str, engine: str) -> str:
        """Full-document English translation via local text + chosen API."""
        from ai_engine_manager import _split_large_text, get_engine

        print(f"    [MT/{engine}] PDF → local text → {engine} English translation (PDF_EXTRACT_AI_ENGINE)…")
        raw = _pdf_raw_text_for_ai_pipeline(pdf_path)
        if len(raw.strip()) < 30:
            raise RuntimeError("PDF_EXTRACT_AI_ENGINE: insufficient text from PDF.")

        base = (
            "You are an expert translator. This is a Sri Lanka Police daily incident report in Sinhala. "
            "Translate the following PART fully and accurately into English. Preserve category numbers 01.–29.\n"
            + POLICE_SUMMARY_TABLE_INSTRUCTIONS
            + "- Translate 'නැත' as 'None' where appropriate.\n"
            + "\n" + get_institutional_prompt_snippet() + "\n"
        )
        mgr = get_engine()
        chunk_sz = max(4000, int(os.getenv("PDF_EXTRACT_MT_CHUNK", "24000")))
        chunks = _split_large_text(raw, chunk_sz)
        sys_p = "Expert Sri Lanka Police Sinhala-to-English translator. Literal full translation; no omissions."
        outs = []
        for i, ch in enumerate(chunks):
            extra = ""
            if len(chunks) > 1:
                extra = f"\n\nThis is PART {i + 1} of {len(chunks)} only — translate every line."
            res = mgr._dispatch_engine(engine, base + extra + "\n\nSOURCE:\n" + ch, sys_p, 420)
            if not res or str(res).startswith("❌"):
                res = mgr.translation_fallback_after_gemini_exhausted(
                    base + extra + "\n\nSOURCE:\n" + ch, sys_p, timeout=420, skip_github=False
                )
            if not res or str(res).startswith("❌"):
                raise RuntimeError(f"translate_pdf via {engine} failed part {i + 1}: {res}")
            outs.append(sanitize_police_translation_output(str(res)))
        merged = sanitize_police_translation_output("\n\n".join(outs))
        print(f"    [MT/{engine}] ✅ Combined translation: {len(merged)} chars.")
        return self.post_process_translation_terminology(merged)

    def post_process_translation_terminology(self, text: str) -> str:
        """Enforce standard English station names via shared utility."""
        return enforce_terminology(text)

    # ------------------------------------------------------------------ #
    #  1. GEMINI FILE API  (Primary: handles full PDF natively)
    # ------------------------------------------------------------------ #

    def extract_pdf_to_json_turbo(self, pdf_path: str) -> dict:
        """
        TURBO MODE: One-shot extraction of all 28 categories into English JSON.
        Rotation: each Gemini model gets ONE attempt (key rotates per model).

        Set ``PDF_EXTRACT_AI_ENGINE=openrouter`` (or ``groq``, ``github``, ``aimlapi``) to skip Gemini
        PDF upload: extract text with PyPDF2/Tesseract, then call that API for JSON.
        """
        alt = _pdf_extract_ai_engine()
        if alt:
            return self._extract_pdf_to_json_turbo_text_ai(pdf_path, alt)

        import time as _time

        gemini_keys = _load_openai_keys.__doc__ and []  # just init
        try:
            keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
            with open(keys_path) as f:
                keys_dict = json.load(f)
            gemini_keys = [(k, v.strip()) for k, v in keys_dict.items() if k.startswith("Gemini") and v.strip()]
        except Exception:
            pass
        if not gemini_keys:
            env_key = os.environ.get("GEMINI_API_KEY", "")
            gemini_keys = [("Gemini_Env", env_key)] if env_key else []
        if not gemini_keys:
            raise RuntimeError("No Gemini API keys found.")

        gemini_models = _gemini_generate_models()
        last_error = None

        import concurrent.futures

        def _run_turbo_model(model_id, api_key, key_id):
            if get_quota_mgr().is_key_exhausted(key_id, "Gemini"):
                raise RuntimeError(f"Key {key_id} is exhausted.")
            try:
                # Record usage immediately when attempting
                get_quota_mgr().record_usage(key_id, "Gemini")

                from google import genai
                client = genai.Client(api_key=api_key)

                upload_path = pdf_path
                temp_copy = None
                try:
                    pdf_path.encode('ascii')
                except UnicodeEncodeError:
                    temp_copy = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp", f"_turbo_{model_id.replace('.','_')}_{key_id}.pdf")
                    os.makedirs(os.path.dirname(temp_copy), exist_ok=True)
                    import shutil
                    shutil.copy2(pdf_path, temp_copy)
                    upload_path = temp_copy

                try:
                    print(f"    [TURBO/Gemini] Uploading PDF to {model_id}...")
                    pdf_file = client.files.upload(file=upload_path)

                    for _ in range(30):
                        if pdf_file.state.name != "PROCESSING":
                            break
                        _time.sleep(2)
                        pdf_file = client.files.get(name=pdf_file.name)

                    if pdf_file.state.name == "FAILED":
                        raise RuntimeError("File processing failed")

                    prompt = (
                        "PERSONA: Sri Lanka Police Data Architect.\n"
                        "TASK: Extract ALL incidents from this Sinhala daily report into one structured English JSON object.\n"
                        "Rules:\n"
                        "1. Include every category 01.–29. that appears; empty categories use {\"incidents\": []}.\n"
                        "2. Each `description` must be the COMPLETE English narrative: every line of the සිදුවීම block, "
                        "all numbered suspects, Rs amounts, phones, weapons, dates — NO summarizing, NO '...', "
                        "NO omitting paragraphs. Multiple numbered incidents → separate objects in `incidents`.\n"
                        "3. Use CLINICAL, INSTITUTIONAL English. Avoid emotional or non-neutral descriptions. "
                        "Translate accurately: 'reported', 'arrested', 'suspect', 'victim', 'complainant', 'motive'.\n"
                        "4. NO Sinhala script in JSON values — every station, description, header date_range, and category name must be English only.\n"
                        "5. JSON: {'categories': {'01': {'name': '...', 'incidents': [{'station': '...', "
                        "'description': '...', 'date': '...', 'time': '...', 'financial_loss': '...', "
                        "'status': '...', 'victim_suspect_names': '...', 'province': '...'}]}, ...}, "
                        "'header': {'date_range': '...'}}\n"
                        "6. Province MUST be one of: WESTERN, SOUTHERN, CENTRAL, NORTHERN, EASTERN, "
                        "NORTH WESTERN, NORTH CENTRAL, UVA, SABARAGAMUWA.\n"
                        "7. Respond ONLY with valid JSON — no markdown."
                    )

                    response = client.models.generate_content(
                        model=model_id,
                        contents=[pdf_file, prompt],
                        config=_gemini_output_config(response_mime_type="application/json"),
                    )

                    try:
                        client.files.delete(name=pdf_file.name)
                    except Exception:
                        pass

                    import json
                    return json.loads(response.text)

                finally:
                    if temp_copy and os.path.exists(temp_copy):
                        os.remove(temp_copy)

            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    get_quota_mgr().record_usage(key_id, "Gemini", exhausted=True)
                print(f"    [TURBO/Gemini] {model_id} failed: {e}")
                raise e

        # FULL PARALLEL execution across keys in batches — optional skip or early exit on dead free tier
        if _env_truthy("TURBO_SKIP_GEMINI"):
            print(
                "    [TURBO/Gemini] ⏭️ Skipped (TURBO_SKIP_GEMINI=1) — OCR + GitHub/OpenRouter/Ollama only.\n"
                "    [TURBO/Hint] Billing not needed for turbo if this path works for you."
            )
            last_error = RuntimeError("TURBO_SKIP_GEMINI")
        else:
            print(f"    [TURBO/Gemini] 🚀 Launching {len(gemini_keys)} keys (Batches of 5) in PARALLEL…")
            batch_size = 5
            for batch_start in range(0, len(gemini_keys), batch_size):
                batch_keys = gemini_keys[batch_start:batch_start + batch_size]
                batch_errors = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch_keys)) as executor:
                    future_to_model = {}
                    for i, (key_id, key_val) in enumerate(batch_keys):
                        assigned_model = gemini_models[(batch_start + i) % len(gemini_models)]
                        display_name = f"{assigned_model} ({key_id})"
                        future_to_model[
                            executor.submit(_run_turbo_model, assigned_model, key_val, key_id)
                        ] = display_name

                    for future in concurrent.futures.as_completed(future_to_model, timeout=120):
                        model_id = future_to_model[future]
                        try:
                            result = future.result()
                            print(f"    [TURBO/Gemini] 🏆 {model_id} WON the race!")
                            return result
                        except Exception as e:
                            last_error = e
                            batch_errors.append(str(e))

                all_quota_zero = batch_errors and all(
                    "limit: 0" in err and ("429" in err or "RESOURCE_EXHAUSTED" in err)
                    for err in batch_errors
                )
                if all_quota_zero:
                    print(
                        "    [TURBO/Gemini] ⏭️ Free-tier quota limit 0 on this batch — skipping remaining Gemini batches.\n"
                        "    [TURBO/Hint] Enable Gemini billing, or set TURBO_SKIP_GEMINI=1 to skip these uploads."
                    )
                    break

        print("    [TURBO/GitHub] 🔄 All Gemini models exhausted/failed. Trying GitHub models via local OCR…")
        if _mt_skip_local_ocr_fallback(last_error) and not _env_truthy("TURBO_SKIP_GEMINI"):
            print(
                "    [TURBO/OCR] ⏭️ MT_SKIP_LOCAL_OCR_FALLBACK=1 — skipping Tesseract + text-based turbo.\n"
                "    [TURBO/Hint] Normal path uses Gemini PDF only; unset env to allow local OCR fallback."
            )
            raise RuntimeError(
                f"Turbo: Gemini failed and local OCR fallback disabled. Last Gemini error: {last_error}"
            )
        try:
            from ai_engine_manager import _split_large_text, get_engine
            from local_ocr_tool import extract_text_from_pdf

            ocr_res = extract_text_from_pdf(pdf_path)
            ocr_text = _ocr_pages_to_text(ocr_res)
            if ocr_text and len(ocr_text.strip()) > 50:
                print(f"    [TURBO/GitHub] Local OCR returned {len(ocr_text)} chars. Sending to GitHub...")
                mgr = get_engine()
                # Smaller segments → less often truncated JSON (raise if you get too many chunks)
                turbo_chunk = int(os.getenv("GITHUB_TURBO_CHUNK_CHARS", "24000"))
                turbo_rules = (
                    "PERSONA: Sri Lanka Police Data Architect.\n"
                    "TASK: Extract incidents from this Sinhala daily report TEXT SEGMENT into structured English JSON.\n"
                    "Rules:\n"
                    "1. Only include category keys (01–29) that appear in THIS segment.\n"
                    "2. Translate EVERY incident into FULL clinical, institutional English. "
                    "Include: complainant lines, suspects, ages, addresses, phone numbers, Rs amounts, times, "
                    "weapon lists, and numbered lists (1)(2)(3)… must ALL appear in `description`. "
                    "Do NOT summarize, shorten, use '...', '[truncated]', or skip paragraphs. "
                    "NO Sinhala characters in any JSON string — output English only.\n"
                    "3. For a category with no incidents here, omit it or use {\"incidents\": []}.\n"
                    "4. Per category: {'name': '...', 'incidents': [{'station': '...', 'description': '...', "
                    "'date': '...', 'time': '...', 'financial_loss': '...', 'status': '...', "
                    "'victim_suspect_names': '...', 'province': '...'}]}\n"
                    "5. Top-level shape: {'categories': {'01': {...}, ...}, 'header': {'date_range': '...'}}\n"
                    "6. Province MUST be one of: WESTERN, SOUTHERN, CENTRAL, NORTHERN, EASTERN, "
                    "NORTH WESTERN, NORTH CENTRAL, UVA, SABARAGAMUWA.\n"
                    "7. If multiple separate incidents exist under one category (numbered 1. 2. 3.), "
                    "output separate objects in `incidents` — never merge into one vague sentence.\n"
                    "8. Respond ONLY with valid JSON — no markdown fences.\n\n"
                )
                chunks = _split_large_text(ocr_text, turbo_chunk)
                merged = {"categories": {}, "header": {}}
                chunk_failed = False
                try:
                    gh_pause = float(os.environ.get("GITHUB_CHUNK_COOLDOWN_SEC", "0"))
                except ValueError:
                    gh_pause = 0.0
                gh_pause = max(0.0, min(gh_pause, 120.0))
                for idx, chunk in enumerate(chunks):
                    if idx > 0 and gh_pause > 0:
                        time.sleep(gh_pause)
                    github_prompt = turbo_rules + f"SEGMENT {idx + 1} of {len(chunks)}:\n{chunk}"
                    try:
                        gh_turbo_timeout = int(os.getenv("GITHUB_TURBO_TIMEOUT_SEC", "360"))
                    except ValueError:
                        gh_turbo_timeout = 360
                    gh_turbo_timeout = max(120, min(gh_turbo_timeout, 900))
                    result = mgr._call_github(
                        github_prompt,
                        "You are a professional Sri Lanka Police Data Architect. "
                        "Output complete JSON with full-length English descriptions — no omissions.",
                        gh_turbo_timeout,
                    )
                    if not result or result.startswith("❌"):
                        print(f"    [TURBO/GitHub] GitHub fallbacks failed: {result}")
                        chunk_failed = True
                        break
                    clean_res = re.sub(r"```json\s*", "", result)
                    clean_res = re.sub(r"```\s*", "", clean_res).strip()
                    try:
                        data = json.loads(clean_res)
                    except json.JSONDecodeError:
                        from json_repair_tool import repair_json

                        data = json.loads(repair_json(clean_res))
                    _merge_partial_turbo_json(merged, data)
                if not chunk_failed and merged.get("categories"):
                    return merged
                if not chunk_failed:
                    print("    [TURBO/GitHub] GitHub returned no category data after chunked merge.")

                print("    [TURBO/Chain] 🔄 Trying OpenRouter → Ollama for JSON segments (same rules as GitHub)…")
                merged_chain = {"categories": {}, "header": {}}
                turbo_sys = (
                    "You are a professional Sri Lanka Police Data Architect. Output valid JSON only. "
                    "Every incident description must be FULL English text — no summaries or ellipses."
                )
                chain_ok = True
                for idx, chunk in enumerate(chunks):
                    seg_prompt = turbo_rules + f"SEGMENT {idx + 1} of {len(chunks)}:\n{chunk}"
                    result = mgr.translation_fallback_after_gemini_exhausted(
                        seg_prompt, turbo_sys, timeout=360, skip_github=True
                    )
                    if not result or result.startswith("❌"):
                        print(f"    [TURBO/Chain] segment {idx + 1} failed: {result}")
                        chain_ok = False
                        break
                    clean_res = re.sub(r"```json\s*", "", result)
                    clean_res = re.sub(r"```\s*", "", clean_res).strip()
                    try:
                        data = json.loads(clean_res)
                    except json.JSONDecodeError:
                        from json_repair_tool import repair_json

                        data = json.loads(repair_json(clean_res))
                    _merge_partial_turbo_json(merged_chain, data)
                if chain_ok and merged_chain.get("categories"):
                    return merged_chain
        except Exception as e:
            print(f"    [TURBO/GitHub] GitHub turbo fallback exception: {e}")

        raise RuntimeError(
            f"Turbo extraction failed (Gemini + GitHub + OpenRouter/Ollama). Last Gemini error: {last_error}"
        )

    def _gemini_mt_parallel_race(self, file_path: str, prompt: str, gemini_keys: list, gemini_models: list):
        """One PDF → Gemini translate-to-English race. Returns (text_or_None, last_error)."""
        import concurrent.futures
        import time as _time

        last_error = None
        if not gemini_keys:
            return None, last_error

        def _run_mt_model(model_id, api_key, key_id):
            if get_quota_mgr().is_key_exhausted(key_id, "Gemini"):
                raise RuntimeError(f"Key {key_id} is exhausted.")
            try:
                get_quota_mgr().record_usage(key_id, "Gemini")
                from google import genai
                client = genai.Client(api_key=api_key)

                upload_path = file_path
                temp_copy = None
                try:
                    file_path.encode("ascii")
                except UnicodeEncodeError:
                    temp_copy = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "tmp",
                        f"_mt_{model_id.replace('.', '_')}_{key_id}_{abs(hash(file_path))}.pdf",
                    )
                    os.makedirs(os.path.dirname(temp_copy), exist_ok=True)
                    import shutil

                    shutil.copy2(file_path, temp_copy)
                    upload_path = temp_copy

                try:
                    pdf_file = client.files.upload(file=upload_path)

                    for _ in range(30):
                        if pdf_file.state.name != "PROCESSING":
                            break
                        _time.sleep(2)
                        pdf_file = client.files.get(name=pdf_file.name)

                    if pdf_file.state.name == "FAILED":
                        raise RuntimeError(f"{model_id} file processing failed.")

                    response = client.models.generate_content(
                        model=model_id,
                        contents=[pdf_file, prompt],
                        config=_gemini_output_config(),
                    )

                    try:
                        client.files.delete(name=pdf_file.name)
                    except Exception:
                        pass

                    return (response.text or "").strip()

                finally:
                    if temp_copy and os.path.exists(temp_copy):
                        os.remove(temp_copy)

            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    get_quota_mgr().record_usage(key_id, "Gemini", exhausted=True)
                print(f"    [MT/Gemini] {model_id} failed: {e}")
                raise e

        print(f"    [MT/Gemini] 🚀 Launching {len(gemini_keys)} keys (batches of 5) in PARALLEL…")
        batch_size = 5
        for batch_start in range(0, len(gemini_keys), batch_size):
            batch_keys = gemini_keys[batch_start : batch_start + batch_size]
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch_keys)) as executor:
                future_to_model = {}
                for i, (key_id, key_val) in enumerate(batch_keys):
                    assigned_model = gemini_models[(batch_start + i) % len(gemini_models)]
                    display_name = f"{assigned_model} ({key_id})"
                    future_to_model[
                        executor.submit(_run_mt_model, assigned_model, key_val, key_id)
                    ] = display_name

                for future in concurrent.futures.as_completed(future_to_model, timeout=600):
                    model_id = future_to_model[future]
                    try:
                        result = future.result()
                        if result:
                            print(f"    [MT/Gemini] 🏆 {model_id} WON the race!")
                            return result, None
                    except Exception as e:
                        last_error = e

        return None, last_error

    def translate_pdf_with_gemini(self, pdf_path: str) -> str:
        """
        Upload PDF to Gemini → OCR + translate to English in one shot.
        Long PDFs are split into several uploads (same as OCR) so output is less likely to truncate.

        Set ``MT_SKIP_LOCAL_OCR_FALLBACK=1`` to never run local Tesseract after Gemini fails
        (faster; requires working Gemini or you accept failure).

        Set ``PDF_EXTRACT_AI_ENGINE=openrouter`` (or ``groq``, ``github``, ``aimlapi``) to skip Gemini:
        PyPDF2/Tesseract text → that API for English.
        """
        alt = _pdf_extract_ai_engine()
        if alt:
            return self._translate_pdf_via_text_ai(pdf_path, alt)

        gemini_keys = []
        try:
            keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
            with open(keys_path) as f:
                keys_dict = json.load(f)
            gemini_keys = [(k, v.strip()) for k, v in keys_dict.items() if k.startswith("Gemini") and v.strip()]
        except Exception:
            pass
        if not gemini_keys:
            env_key = os.environ.get("GEMINI_API_KEY", "")
            gemini_keys = [("Gemini_Env", env_key)] if env_key else []

        gemini_models = _gemini_generate_models()
        last_error = None
        base_prompt = (
            "PERSONA: Expert Institutional Translator for Sri Lanka Police.\n"
            "TASK: This is a daily incident report in Sinhala. Extract ALL text and translate it "
            "fully into clinical, neutral English. Preserve the numbered categories exactly:\n"
            "- Use institutional terminology: 'offence', 'complainant', 'suspect', 'reported', 'investigation'.\n"
            "- Keep all numbered category headers (e.g., 01. 02. 03. etc.) as they appear.\n"
            "- Narrative tables in the body: prefer plain text lines (not markdown) unless a grid is clearer.\n"
            + POLICE_SUMMARY_TABLE_INSTRUCTIONS
            + "- Translate 'නැත' as 'None' where appropriate.\n"
            "- Keep vehicle numbers and proper nouns as-is.\n"
            "- Do not use long runs of ---; use 'None' for empty narrative slots where needed."
        )

        parts = pdf_parts_for_gemini_upload(pdf_path)
        chunks_out: list[str] = []
        try:
            if len(parts) > 1:
                print(
                    f"    [MT/Gemini] 📎 Split PDF into {len(parts)} part(s) "
                    f"so each segment is fully translated."
                )
            for path, _is_temp, pi, pt, prange in parts:
                extra = ""
                if pt > 1:
                    extra = (
                        f"\n\nThis file is ONLY pages {prange} of the full report (part {pi} of {pt}). "
                        "Translate every line into English; do not omit tables or categories."
                    )
                res, err = self._gemini_mt_parallel_race(path, base_prompt + extra, gemini_keys, gemini_models)
                if res:
                    chunks_out.append(res)
                    last_error = None
                else:
                    last_error = err
                    break
        finally:
            _cleanup_pdf_parts(parts)

        if len(chunks_out) == len(parts) and chunks_out:
            merged = sanitize_police_translation_output("\n\n".join(chunks_out))
            print(f"    [MT/Gemini] ✅ Combined translation: {len(merged)} characters.")
            return merged

        # --- GITHUB FALLBACK: Local OCR text → GitHub text models ---
        print("    [MT/GitHub] 🔄 All Gemini models exhausted. Trying GitHub models via local OCR...")
        if _mt_skip_local_ocr_fallback(last_error):
            print(
                "    [MT/OCR] ⏭️ MT_SKIP_LOCAL_OCR_FALLBACK=1 — skipping Tesseract/GitHub/OCR fallback."
            )
            raise RuntimeError(
                f"PDF translation failed (Gemini only; local OCR disabled). Last error: {last_error}"
            )
        try:
            from local_ocr_tool import extract_text_from_pdf
            ocr_res = extract_text_from_pdf(pdf_path)
            ocr_text = _ocr_pages_to_text(ocr_res)

            if ocr_text and len(ocr_text.strip()) > 50:
                print(f"    [MT/Fallback] Local OCR extracted {len(ocr_text)} chars. Chunking and translating...")
                from ai_engine_manager import _split_large_text, get_engine
                mgr = get_engine()
                mt_sys = (
                    "Expert Institutional Translator. Clinical and neutral tone. "
                    "Literal full translation; never refuse; never summarize."
                )
                chunks = _split_large_text(ocr_text, 10000, overlap=1000)
                eng_parts_dict = {}

                def _process_and_verify_chunk(idx: int, chunk: str) -> tuple:
                    """Worker function: Translates a chunk, then feeds it to a Checker AI for verification."""
                    print(f"    [MT/Worker-{idx}] Starting translation (~{len(chunk)} chars)...")

                    # --- STEP 1: Preliminary Translation ---
                    # Only request the summary table if it's the LAST chunk, since the table is at the end of the PDF!
                    table_instruction = (
                        POLICE_SUMMARY_TABLE_INSTRUCTIONS
                        if idx == len(chunks) - 1
                        else ""
                    )

                    github_prompt = (
                        f"PERSONA: Expert Sri Lanka Police report translator.\n"
                        f"TASK: Translate the following Sinhala police report text into English.\n"
                        f"(Part {idx+1} of {len(chunks)})\n"
                        f"Rules:\n"
                        f"- Output ONLY the translation (no preface).\n"
                        f"- Use CLINICAL, INSTITUTIONAL language. Direct and neutral tone is mandatory.\n"
                        f"- Do NOT summarize, shorten, or replace with samples.\n"
                        f"- Preserve all numbered category headers (01., 02., … 29.) and row order.\n"
                        f"- Keep station names, dates, times, and vehicle numbers faithful to the source.\n"
                        f"{table_instruction}\n"
                        f"\n\nSINHALA / OCR SOURCE:\n"
                        f"{chunk}"
                    )

                    # We try Github first for the rough translation
                    translated_text = mgr._call_github(github_prompt, mt_sys, 180)
                    if not translated_text or translated_text.startswith("❌"):
                        print(f"    [MT/Worker-{idx}] 🔄 GitHub failed, trying Chain (Ollama/OpenRouter)...")
                        translated_text = mgr.translation_fallback_after_gemini_exhausted(
                            github_prompt, mt_sys, timeout=300, skip_github=True
                        )
                        if not translated_text or translated_text.startswith("❌"):
                            print(f"    [MT/Worker-{idx}] ❌ Translation failed entirely!")
                            return (idx, "[Translation Failed]")

                    # --- STEP 2: Checker AI Verification ---
                    print(f"    [MT/Worker-{idx}] 🕵️ Checking & Verifying translation via Checker AI...")
                    checker_prompt = (
                        f"PERSONA: Senior Sri Lanka Police Editor and Verification Agent.\n"
                        f"TASK: You are provided the original Sinhala text and a draft English translation.\n"
                        f"Your job is to CLEANSE the English translation. Completely REMOVE hallucinated elements.\n\n"
                        f"CRITICAL RULES:\n"
                        f"1. OUTPUT STRICTLY THE CORRECTED ENGLISH TEXT ONLY. Do not use conversational markdown.\n"
                        f"2. REMOVE any tables, categories, or lists that DO NOT exist in the Sinhala source.\n"
                        f"3. Ensure the tone is institutional and formal.\n"
                        f"4. Correct any glaring mistranslations.\n\n"
                        f"SINHALA SOURCE:\n{chunk}\n\n"
                        f"DRAFT TRANSLATION:\n{translated_text}\n\n"
                        f"CORRECTED ENGLISH OUTPUT ONLY:"
                    )
                    checker_sys = "You are an automated code validation agent. Output exactly the requested text. No markdown formatting."

                    # User requested: No Github for the Checker AI. Use Ollama/Groq.
                    verified_text = mgr.translation_fallback_after_gemini_exhausted(
                        checker_prompt, checker_sys, timeout=300, skip_github=True
                    )

                    if verified_text and not verified_text.startswith("❌"):
                        print(f"    [MT/Worker-{idx}] ✅ Verification complete.")
                        return (idx, verified_text)
                    else:
                        print(f"    [MT/Worker-{idx}] ⚠️ Checker failed. Using unverified draft.")
                        return (idx, translated_text)

                import concurrent.futures
                MAX_WORKERS = 3 # Limiting to 3 to prevent brutal rate-limits / locking

                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    future_to_idx = {
                        executor.submit(_process_and_verify_chunk, idx, chunk): idx
                        for idx, chunk in enumerate(chunks)
                    }
                    for future in concurrent.futures.as_completed(future_to_idx):
                        idx = future_to_idx[future]
                        try:
                            returned_idx, res_text = future.result()
                            eng_parts_dict[returned_idx] = res_text
                        except Exception as e:
                            print(f"    [MT/Fallback] Worker {idx} crashed: {e}")
                            eng_parts_dict[idx] = "[Worker Crashed]"

                # Reassemble correctly based on original chunk index order
                eng_parts = [eng_parts_dict[i] for i in range(len(chunks)) if i in eng_parts_dict]

                print("    [MT/Fallback] ✅ All chunks concurrently translated & verified.")
                return sanitize_police_translation_output("\n\n".join(eng_parts))
            else:
                print("    [MT/Fallback] Local OCR returned insufficient text.")
        except Exception as e:
            print(f"    [MT/GitHub] GitHub fallback failed: {e}")

        raise RuntimeError(f"PDF translation failed (Gemini + GitHub + OpenRouter/Ollama). Last error: {last_error}")

    def _gemini_ocr_parallel_race(self, file_path: str, prompt: str, gemini_keys: list, gemini_models: list):
        """Upload one PDF file to Gemini; parallel race across keys/models. Returns (text_or_None, last_error)."""
        import concurrent.futures
        import time as _time

        last_error = None
        if not gemini_keys:
            return None, last_error

        def _run_ocr_model(model_id, api_key, key_id):
            try:
                get_quota_mgr().record_usage(key_id, "Gemini")
                from google import genai
                client = genai.Client(api_key=api_key)

                upload_path = file_path
                temp_copy = None
                try:
                    file_path.encode("ascii")
                except UnicodeEncodeError:
                    temp_copy = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "tmp",
                        f"_ocr_{model_id.replace('.', '_')}_{key_id}_{abs(hash(file_path))}.pdf",
                    )
                    os.makedirs(os.path.dirname(temp_copy), exist_ok=True)
                    import shutil

                    shutil.copy2(file_path, temp_copy)
                    upload_path = temp_copy

                try:
                    pdf_file = client.files.upload(file=upload_path)

                    for _ in range(30):
                        if pdf_file.state.name != "PROCESSING":
                            break
                        _time.sleep(2)
                        pdf_file = client.files.get(name=pdf_file.name)

                    response = client.models.generate_content(
                        model=model_id,
                        contents=[pdf_file, prompt],
                        config=_gemini_output_config(),
                    )

                    try:
                        client.files.delete(name=pdf_file.name)
                    except Exception:
                        pass

                    return (response.text or "").strip()

                finally:
                    if temp_copy and os.path.exists(temp_copy):
                        os.remove(temp_copy)

            except Exception as e:
                print(f"    [OCR/Gemini] {model_id} failed: {e}")
                raise e

        print(f"    [OCR/Gemini] 🚀 Launching {len(gemini_keys)} keys (batches of 5) in PARALLEL…")
        batch_size = 5
        for batch_start in range(0, len(gemini_keys), batch_size):
            batch_keys = gemini_keys[batch_start : batch_start + batch_size]
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch_keys)) as executor:
                future_to_model = {}
                for i, (key_id, key_val) in enumerate(batch_keys):
                    assigned_model = gemini_models[(batch_start + i) % len(gemini_models)]
                    display_name = f"{assigned_model} ({key_id})"
                    future_to_model[
                        executor.submit(_run_ocr_model, assigned_model, key_val, key_id)
                    ] = display_name

                for future in concurrent.futures.as_completed(future_to_model, timeout=600):
                    model_id = future_to_model[future]
                    try:
                        result = future.result()
                        if result:
                            print(f"    [OCR/Gemini] 🏆 {model_id} WON the race!")
                            return result, None
                    except Exception as e:
                        last_error = e

        return None, last_error

    def extract_pdf_sinhala_with_gemini(self, pdf_path: str, return_chunks: bool = False, progress_callback: callable = None) -> str | list[str]:
        """
        Upload PDF to Gemini → extract RAW SINHALA TEXT (no translation).
        Long PDFs are split into smaller uploads (see GEMINI_OCR_PAGES_PER_PART) to reduce truncation.
        Fallback: local Tesseract OCR.

        Set ``PDF_EXTRACT_AI_ENGINE=openrouter`` (or ``groq``, ``github``, ``aimlapi``) for non-Gemini
        path: local PDF text → API returns cleaned Sinhala.
        """
        alt = _pdf_extract_ai_engine()
        if alt:
            return self._extract_sinhala_text_via_ai(pdf_path, alt)

        gemini_keys = []
        try:
            keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
            with open(keys_path) as f:
                keys_dict = json.load(f)
            gemini_keys = [(k, v.strip()) for k, v in keys_dict.items() if k.startswith("Gemini") and v.strip()]
        except Exception:
            pass
        if not gemini_keys:
            env_key = os.environ.get("GEMINI_API_KEY", "")
            gemini_keys = [("Gemini_Env", env_key)] if env_key else []

        gemini_models = _gemini_generate_models()
        last_error = None
        base_prompt = (
            "Extract ALL text from this Sri Lanka Police incident report EXACTLY as it is written in Sinhala.\n"
            "- DO NOT translate to English. Keep the output entirely in Sinhala.\n"
            "- Preserve all numbered category headers (e.g. 01. 02. 03.) exactly as written.\n"
            "- For the 29-row summary statistics table: keep one row per line; preserve columns using TABs or aligned spacing "
            "so serial numbers stay aligned with their counts (වාර්තා වූ / විසඳූ / නොවිසඳු).\n"
            "- Do not merge summary rows into prose; do not drop count columns.\n"
            "- Other layout tables: plain text rows is fine.\n"
            "- Keep numbers, vehicle plates, and names as they appear."
        )

        parts = pdf_parts_for_gemini_upload(pdf_path)
        chunks_out: list[str] = []
        try:
            if len(parts) > 1:
                print(
                    f"    [OCR/Gemini] - Split PDF into {len(parts)} part(s) "
                    f"(GEMINI_OCR_PAGES_PER_PART={_env_int('GEMINI_OCR_PAGES_PER_PART', 6)}) to limit truncation."
                )
            for path, _is_temp, pi, pt, prange in parts:
                extra = ""
                if pt > 1:
                    extra = (
                        f"\n\nThis PDF contains ONLY pages {prange} of the full report "
                        f"(part {pi} of {pt}). Extract every Sinhala line from these pages; "
                        "do not skip tables, footnotes, or numbered sections."
                    )
                full_prompt = base_prompt + extra
                print(f"    [OCR/Gemini] Part {pi}/{pt} (pages {prange}) …")
                res, err = self._gemini_ocr_parallel_race(path, full_prompt, gemini_keys, gemini_models)
                if res:
                    chunks_out.append(res)
                    last_error = None
                    if progress_callback:
                        progress_callback("OCR_UPDATE", {"msg": f"Page {prange} extracted (Sinhala)..."})
                else:
                    last_error = err
                    break
        finally:
            _cleanup_pdf_parts(parts)

        if len(chunks_out) == len(parts) and chunks_out:
            if return_chunks:
                return chunks_out
            merged = "\n\n".join(chunks_out)
            return merged

        # --- GITHUB FALLBACK: Local OCR ---
        print("    [OCR/GitHub] 🔄 All Gemini OCR models exhausted. Using local Tesseract OCR...")
        if _mt_skip_local_ocr_fallback(last_error):
            print("    [OCR/Local] ⏭️ MT_SKIP_LOCAL_OCR_FALLBACK=1 — skipping Tesseract.")
            raise RuntimeError(
                f"Sinhala extraction: Gemini failed and local OCR disabled. Last error: {last_error}"
            )
        try:
            from local_ocr_tool import extract_text_from_pdf
            ocr_res = extract_text_from_pdf(pdf_path)
            ocr_text = _ocr_pages_to_text(ocr_res)
            if ocr_text and len(ocr_text.strip()) > 30:
                print(f"    [OCR/Local] Tesseract extracted {len(ocr_text)} chars.")
                return [ocr_text] if return_chunks else ocr_text
        except Exception as e:
            print(f"    [OCR/Local] Tesseract failed: {e}")

        raise RuntimeError(f"Sinhala extraction failed on all Gemini models and local OCR. Last error: {last_error}")


    def translate_text_with_gemini(self, text) -> str:
        """
        Translate Sinhala text (string or list) using Gemini.
        Rotation: ONE attempt per Gemini model (key rotates per model).
        Fallback: GitHub models (gpt-4o-mini → llama → phi) via ai_engine_manager.
        """

        from google import genai

        gemini_keys = []
        try:
            keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
            with open(keys_path) as f:
                keys_dict = json.load(f)
            gemini_keys = [(k, v.strip()) for k, v in keys_dict.items() if k.startswith("Gemini") and v.strip()]
        except Exception:
            pass
        if not gemini_keys:
            env_key = os.environ.get("GEMINI_API_KEY", "")
            gemini_keys = [("Gemini_Env", env_key)] if env_key else []

        texts = text if isinstance(text, list) else [text]
        combined = "\n".join(texts)

        translate_prompt = (
            "Translate each of the following Sinhala lines into English. "
            "Return only the English translations, one per line, in the same order.\n\n"
            f"{combined}"
        )

        gemini_models = _gemini_generate_models()
        last_error = None
        result_lines = []

        # --- GEMINI: PARALLEL RACE ACROSS ALL MODELS ---
        if gemini_keys:
            import concurrent.futures

            def _run_text_model(model_id, api_key, key_id):
                try:
                    get_quota_mgr().record_usage(key_id, "Gemini")
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=model_id,
                        contents=[translate_prompt],
                        config=_gemini_output_config(),
                    )
                    return (response.text or "").strip().split("\n")
                except Exception as e:
                    print(f"    [MT/Gemini] {model_id} failed: {e}")
                    raise e

            print(f"    [MT/Gemini] 🚀 Launching {len(gemini_keys)} keys (Batches of 5) for text in PARALLEL...")
            batch_size = 5
            for batch_start in range(0, len(gemini_keys), batch_size):
                batch_keys = gemini_keys[batch_start:batch_start + batch_size]
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch_keys)) as executor:
                    future_to_model = {}
                    for i, (key_id, key_val) in enumerate(batch_keys):
                        assigned_model = gemini_models[(batch_start + i) % len(gemini_models)]
                        display_name = f"{assigned_model} ({key_id})"
                        future_to_model[executor.submit(_run_text_model, assigned_model, key_val, key_id)] = display_name

                    for future in concurrent.futures.as_completed(future_to_model):
                        model_id = future_to_model[future]
                        try:
                            result_lines = future.result()
                            print(f"    [MT/Gemini] 🏆 {model_id} WON the race!")
                            break
                        except Exception as e:
                            last_error = e
                if result_lines:
                    break

        if result_lines:
            if isinstance(text, list):
                while len(result_lines) < len(texts):
                    result_lines.append("")
                return result_lines[:len(texts)]
            return "\n".join(result_lines).strip()

        # --- GITHUB → OpenRouter → Ollama (after Gemini) ---
        print("    [MT/GitHub] 🔄 All Gemini models exhausted. Trying GitHub models...")
        si_en_system = "Expert Sri Lanka Police Sinhala-to-English translator."
        github_prompt = (
            "You are an expert Sri Lanka Police incident report translator. "
            "Translate the following Sinhala text into professional English. "
            "Preserve all numbered categories (01., 02., etc.), station names, "
            "vehicle numbers, and proper nouns exactly as-is.\n\n"
            f"{combined}"
        )
        try:
            from ai_engine_manager import get_engine
            mgr = get_engine()
            result = mgr._call_github(github_prompt, si_en_system, 180)
            if result and not result.startswith("❌"):
                print("    [MT/GitHub] ✅ GitHub model success!")
                if isinstance(text, list):
                    lines = result.split("\n")
                    while len(lines) < len(texts):
                        lines.append("")
                    return lines[:len(texts)]
                return result
            print(f"    [MT/GitHub] all GitHub models failed: {result}")
        except Exception as e:
            print(f"    [MT/GitHub] GitHub fallback exception: {e}")

        print("    [MT-Chain] 🔄 GitHub done. Trying OpenRouter → Ollama…")
        try:
            from ai_engine_manager import get_engine
            mgr = get_engine()
            result = mgr.translation_fallback_after_gemini_exhausted(
                github_prompt, si_en_system, timeout=300, skip_github=True
            )
            if result and not result.startswith("❌"):
                print("    [MT-Chain] ✅ Translation via OpenRouter/Ollama.")
                if isinstance(text, list):
                    lines = result.split("\n")
                    while len(lines) < len(texts):
                        lines.append("")
                    return lines[:len(texts)]
                return result
        except Exception as e:
            print(f"    [MT-Chain] OpenRouter/Ollama exception: {e}")

        raise RuntimeError(f"Text translation failed (Gemini + GitHub + OpenRouter/Ollama). Last error: {last_error}")

    def translate_sinhala_document_to_english(
        self, sinhala_text: str, part_index: int = 1, part_total: int = 1
    ) -> str:
        """
        Full-document Sinhala → English (not line-by-line). Keeps structure; no summarization.
        Used when the whole PDF body has already been extracted as Sinhala-only text.
        """
        from google import genai

        if not sinhala_text or len(sinhala_text.strip()) < 2:
            return sinhala_text or ""

        gemini_keys = []
        try:
            keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
            with open(keys_path) as f:
                keys_dict = json.load(f)
            gemini_keys = [(k, v.strip()) for k, v in keys_dict.items() if k.startswith("Gemini") and v.strip()]
        except Exception:
            pass
        if not gemini_keys:
            env_key = os.environ.get("GEMINI_API_KEY", "")
            gemini_keys = [("Gemini_Env", env_key)] if env_key else []

        scope = ""
        if part_total > 1:
            scope = (
                f"This is segment {part_index} of {part_total} of the SAME report. "
                "Translate only this segment; do not summarize or skip any line.\n\n"
            )

        translate_prompt = (
            scope
            + "You translate Sri Lanka Police daily incident reports from Sinhala into English.\n"
            "Rules:\n"
            "- Translate the ENTIRE Sinhala block below. Do not omit, summarize, or skip sentences.\n"
            "- Keep category numbers (01. through 29.), dates, names, vehicle numbers, and stations as in the source.\n"
            + POLICE_SUMMARY_TABLE_INSTRUCTIONS
            + "- Outside the summary grid, use the institutional narrative style: "
            '"A case of … was reported to the police station.", full time/place/complainant/suspect/property, '
            "closing with motive/investigations as in official English reports.\n"
            "- Preserve hierarchy lines in order when present in the source (e.g. DIG …, District, … Div.) "
            "each on its own line before the station line (e.g. STATION: A case of …).\n"
            "- End each distinct incident narrative with the reference exactly as in the source, "
            "typically like (CTM.370)  or (OTM.1136); put a blank line before the next incident when "
            "several appear in one segment (so downstream splitting stays reliable).\n"
            "- Use normal paragraphs where appropriate.\n\n"
            "SINHALA TEXT:\n"
            f"{sinhala_text}"
        )

        gemini_models = _gemini_generate_models()
        last_error = None
        result_text = ""

        if gemini_keys:
            import concurrent.futures

            def _run_doc_model(model_id, api_key, key_id):
                try:
                    get_quota_mgr().record_usage(key_id, "Gemini")
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=model_id,
                        contents=[translate_prompt],
                        config=_gemini_output_config(),
                    )
                    return (response.text or "").strip()
                except Exception as e:
                    print(f"    [MT-Doc/Gemini] {model_id} failed: {e}")
                    raise e

            print(
                f"    [MT-Doc/Gemini] 🚀 Translating document segment {part_index}/{part_total} "
                f"({len(sinhala_text)} Sinhala chars)..."
            )
            batch_size = 5
            for batch_start in range(0, len(gemini_keys), batch_size):
                batch_keys = gemini_keys[batch_start:batch_start + batch_size]
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch_keys)) as executor:
                    future_to_model = {}
                    for i, (key_id, key_val) in enumerate(batch_keys):
                        assigned_model = gemini_models[(batch_start + i) % len(gemini_models)]
                        display_name = f"{assigned_model} ({key_id})"
                        future_to_model[executor.submit(_run_doc_model, assigned_model, key_val, key_id)] = display_name

                    for future in concurrent.futures.as_completed(future_to_model):
                        model_id = future_to_model[future]
                        try:
                            result_text = future.result()
                            print(f"    [MT-Doc/Gemini] 🏆 {model_id} WON the race!")
                            break
                        except Exception as e:
                            last_error = e
                if result_text:
                    break

        if result_text:
            return result_text

        doc_sys = (
            "Expert Sri Lanka Police Sinhala-to-English translator. Full literal translation, no omissions. "
            "Preserve 29-row summary tables with aligned counts (pipe or tab columns)."
        )
        print("    [MT-Doc/GitHub] 🔄 Gemini failed for document chunk. Trying GitHub…")
        try:
            from ai_engine_manager import get_engine

            mgr = get_engine()
            result = mgr._call_github(translate_prompt, doc_sys, 240)
            if result and not result.startswith("❌"):
                print("    [MT-Doc/GitHub] ✅ Success.")
                return result.strip()
            print(f"    [MT-Doc/GitHub] failed: {result}")
        except Exception as e:
            print(f"    [MT-Doc/GitHub] exception: {e}")

        print("    [MT-Doc-Chain] Trying OpenRouter → Ollama…")
        try:
            from ai_engine_manager import get_engine

            mgr = get_engine()
            result = mgr.translation_fallback_after_gemini_exhausted(
                translate_prompt, doc_sys, timeout=300, skip_github=True
            )
            if result and not result.startswith("❌"):
                print("    [MT-Doc-Chain] ✅ Success.")
                return result.strip()
        except Exception as e:
            print(f"    [MT-Doc-Chain] exception: {e}")

        raise RuntimeError(
            f"Document translation failed (Gemini + GitHub + OpenRouter/Ollama). Last error: {last_error}"
        )

    def translate_full_sinhala_pdf_to_english(
        self,
        pdf_path: str,
        output_txt: str | None = None,
        save_sinhala_txt: str | None = None,
        progress_callback: callable = None
    ) -> str:
        """
        Pipeline: PDF -> Sinhala-only text (full document) -> English (full document).
        Processes page-by-page for maximum fidelity.
        """
        print("[Full PDF -> English] Translating Page-by-Page...")

        # Force 1-page splits for OCR
        os.environ["GEMINI_OCR_PAGES_PER_PART"] = "1"
        os.environ["GEMINI_OCR_SPLIT_MIN_PAGES"] = "1"

        chunks = self.extract_pdf_sinhala_with_gemini(pdf_path, return_chunks=True, progress_callback=progress_callback)

        if isinstance(chunks, str):
            chunks = [chunks]

        if not chunks:
             raise RuntimeError("OCR failed to return segments.")

        if save_sinhala_txt:
            os.makedirs(os.path.dirname(os.path.abspath(save_sinhala_txt)) or ".", exist_ok=True)
            with open(save_sinhala_txt, "w", encoding="utf-8", errors="replace") as f:
                f.write("\n\n".join(chunks))
            print(f"   Saved Sinhala text: {save_sinhala_txt}")

        eng_parts = []
        for i, seg in enumerate(chunks):
            pnum = i + 1
            marker = f"--- Page {pnum} ---"
            print(f"   [MT] Translating Page {pnum}/{len(chunks)}...")
            if progress_callback:
                progress_callback("OCR_UPDATE", {"msg": f"Translating Page {pnum}/{len(chunks)}..."})
            trans = self.translate_sinhala_document_to_english(seg, pnum, len(chunks))
            eng_parts.append(f"{marker}\n\n{trans}")

        english = "\n\n".join(eng_parts)

        if output_txt:
            d = os.path.dirname(os.path.abspath(output_txt))
            if d:
                os.makedirs(d, exist_ok=True)
            with open(output_txt, "w", encoding="utf-8", errors="replace") as f:
                f.write(english)
            print(f"   Saved English text: {output_txt}")

        return english

    # ------------------------------------------------------------------ #
    #  2. OPENAI GPT-4o-mini  (Fallback when Gemini quota exhausted)
    # ------------------------------------------------------------------ #

    def translate_with_openai(self, text) -> str:
        """
        Translate Sinhala text to English using OpenAI GPT-4o-mini.
        Used as fallback when all Gemini keys are quota-exhausted.
        """
        try:
            import openai
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

        openai_keys = _load_openai_keys()
        if not openai_keys:
            raise RuntimeError("No OpenAI API keys found in gemini_keys.json or OPENAI_API_KEY env.")

        texts = text if isinstance(text, list) else [text]
        combined = "\n".join(texts)

        prompt = (
            "You are an expert Sri Lanka Police incident report translator. "
            "Translate the following Sinhala text into professional English. "
            "Preserve all numbered categories (01., 02., etc.), station names, "
            "vehicle numbers, and proper nouns exactly as-is.\n\n"
            f"{combined}"
        )

        last_error = None
        for api_key in openai_keys:
            try:
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional Sri Lanka Police report translator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4096
                )
                result = response.choices[0].message.content.strip()
                print("    [MT/OpenAI] ✅ GPT-4o-mini translation success!")
                if isinstance(text, list):
                    lines = result.split("\n")
                    while len(lines) < len(texts):
                        lines.append("")
                    return lines[:len(texts)]
                return result
            except Exception as e:
                last_error = e
                print(f"    [MT/OpenAI] Key failed: {e}")
                continue

        raise RuntimeError(f"OpenAI translation failed after all keys: {last_error}")

    # ------------------------------------------------------------------ #
    #  3. GOOGLE TRANSLATE  (Fast internet-based fallback)
    # ------------------------------------------------------------------ #




    # ------------------------------------------------------------------ #
    #  Main entrypoint
    # ------------------------------------------------------------------ #

    def translate(self, text):
        """
        Translate Sinhala text → English.
        Priority (default):
        1. Gemini (High Fidelity Cloud — 5 keys × 4 models)
        2. OpenAI GPT-4o-mini (Quota-exhaustion fallback)
        3. GitHub Models (GPT-4o-mini / Llama via Azure)
        4. [DEPRECATED] (offline fallback)
        """
        if not text or (isinstance(text, str) and len(text.strip()) < 2):
            return text

        # 1. Gemini (Primary — 5 keys × 4 models = 20 attempts)
        try:
            return self.translate_text_with_gemini(text)
        except Exception as e:
            print(f"    [MT] Gemini failed: {e}. Trying OpenAI...")

        # 2. OpenAI GPT-4o-mini (Fallback when Gemini quota exhausted)
        try:
            return self.translate_with_openai(text)
        except Exception as e:
            print(f"    [MT] OpenAI failed: {e}. Trying GitHub Models...")

        # 3. GitHub Models (via AIEngineManager)
        try:
            from ai_engine_manager import get_engine
            ai_mgr = get_engine()
            prompt = (
                "You are an expert Sri Lanka Police translator. Translate the following Sinhala text "
                "into professional English. Keep names, vehicle numbers, and numbered categories as-is.\n\n"
                f"{text}"
            )
            res = ai_mgr.call_ai(
                prompt,
                system_prompt="Police Record Translator",
                restricted_list=["github", "aimlapi", "groq", "openrouter", "ollama"],
            )
            if res and not res.startswith("❌"):
                print("    [MT/GitHub] ✅ GitHub Models fallback success.")
                return res
        except Exception as e:
            print(f"    [MT] GitHub Models failed: {e}. Trying Google Translate…")

        # 5. [DEPRECATED] Google Translate removed.
        return "Translation unavailable"


# ------------------------------------------------------------------ #
#  Convenience helpers used by rest of pipeline
# ------------------------------------------------------------------ #

_translator = None

def translate_sinhala_to_english(text):
    global _translator
    if _translator is None:
        _translator = MachineTranslator()
    return _translator.translate(text)

def extract_pdf_to_sinhala(pdf_path: str) -> str:
    """
    High-fidelity, ultra-fast full-PDF Native Sinhala OCR via Gemini File API.
    """
    global _translator
    if _translator is None:
        _translator = MachineTranslator()
    return _translator.extract_pdf_sinhala_with_gemini(pdf_path)

def translate_pdf_to_english(pdf_path: str) -> str:
    """
    High-fidelity, ultra-fast full-PDF OCR + translation via Gemini.
    Returns the full English text.
    """
    global _translator
    if _translator is None:
        _translator = MachineTranslator()
    return _translator.translate_pdf_with_gemini(pdf_path)


def full_pdf_sinhala_only_then_english(
    pdf_path: str,
    english_txt: str | None = None,
    sinhala_txt: str | None = None,
) -> str:
    """
    මුළු PDF එක: පළමුව සම්පූර්ණ සිංහල පෙළ, පසුව ඉංග්‍රීසි පරිවර්තනය පමණී (JSON/කාණ්ඩ නොවේ).
    Full PDF: extract all Sinhala first, then translate that text to English only.
    """
    global _translator
    if _translator is None:
        _translator = MachineTranslator()
    return _translator.translate_full_sinhala_pdf_to_english(
        pdf_path, output_txt=english_txt, save_sinhala_txt=sinhala_txt
    )
