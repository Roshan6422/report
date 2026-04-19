"""
machine_translator.py
=====================
Sinhala-to-English Machine Translation Engine for Sri Lanka Police Reports.
Priority: OpenAI GPT-4o-mini → GitHub Models → Local OCR Fallback.

Usage:
    from machine_translator import MachineTranslator
    translator = MachineTranslator()
    result = translator.translate("සිංහල පෙළ")
"""

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS & CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

import json
import os
import re
import time
import logging
import tempfile
import shutil
import concurrent.futures
from typing import Any, Dict, List, Optional, Tuple, Union

# Local project imports
from quota_manager import get_quota_mgr
from station_mapping import enforce_terminology, get_institutional_prompt_snippet
from json_repair_tool import repair_json



try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    openai = None

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("machine_translator.log", encoding="utf-8", mode="a")
    ]
)
log = logging.getLogger("machine-translator")

# ── Constants ───────────────────────────────────────────────────────────────
POLICE_SUMMARY_TABLE_INSTRUCTIONS = """
OFFICIAL SUMMARY STATISTICS TABLE (29 rows × 5 columns):
- This is an official government data extraction task. 
- Keep exactly 29 rows (01–29); do not merge, skip, or omit any rows.
- Each numeric digit must stay in its exact column (reported | solved | unsolved).
- Translate Sinhala incident types into formal English legal/police terminology.
- Preserve the table as RAW text with " | " or TAB separators.
- Ensure 100% data fidelity for institutional reporting.
"""


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def _env_truthy(name: str, default: bool = False) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)).strip())
    except (ValueError, TypeError):
        return default



def _ocr_pages_to_text(pages) -> str:
    if isinstance(pages, list):
        return "\n".join("" if p is None else str(p) for p in pages)
    return pages if pages is not None else ""


def _extract_pdf_text_pypdf2(pdf_path: str) -> str:
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
    except ImportError:
        log.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
        return ""
    except Exception as e:
        log.warning(f"    [PDF/Text] PyPDF2 extraction failed: {e}")
        return ""


def _pdf_raw_text_for_ai_pipeline(pdf_path: str) -> str:
    raw = _extract_pdf_text_pypdf2(pdf_path)
    if len(raw.strip()) >= 80:
        log.info(f"    [PDF/AI] PyPDF2 extracted {len(raw)} chars.")
        return raw
    
    if _env_truthy("PDF_EXTRACT_NO_TESSERACT"):
        log.info(f"    [PDF/AI] PyPDF2 only: {len(raw)} chars (PDF_EXTRACT_NO_TESSERACT=1).")
        return raw.strip()
    
    if _env_truthy("MT_STRICT_PDF_ONLY") and not _env_truthy("PDF_EXTRACT_ALLOW_LOCAL_OCR"):
        log.info(
            "    [PDF/AI] PyPDF2 text thin; MT_STRICT_PDF_ONLY blocks local OCR. "
            "Use a text-based PDF or set PDF_EXTRACT_ALLOW_LOCAL_OCR=1 for scans."
        )
        return raw.strip()
    
    log.info("    [PDF/AI] PyPDF2 text thin; trying Tesseract for scanned PDF…")
    try:
        from local_ocr_tool import extract_text_from_pdf
        ocr_res = extract_text_from_pdf(pdf_path)
        ocr_text = _ocr_pages_to_text(ocr_res)
        if ocr_text and len(ocr_text.strip()) > len(raw.strip()):
            log.info(f"    [PDF/AI] Tesseract extracted {len(ocr_text)} chars.")
            return ocr_text.strip()
    except ImportError:
        log.warning("local_ocr_tool not available. Install Surya OCR or set PDF_EXTRACT_NO_TESSERACT=1")
    except Exception as e:
        log.warning(f"    [PDF/AI] Tesseract failed: {e}")
    
    return raw.strip()


def _pdf_extract_ai_engine() -> str:
    e = (os.getenv("PDF_EXTRACT_AI_ENGINE") or "").strip().lower()
    if e in ("groq", "github", "aimlapi"):
        return e
    return ""


def _normalize_turbo_cat_key(key) -> str:
    s = str(key).strip()
    if s.isdigit():
        return s.zfill(2)
    return s


def _merge_partial_turbo_json(merged: Dict, part: Dict) -> None:
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




def _load_openai_keys() -> List[str]:
    """Load all available OpenAI API keys from gemini_keys.json or env."""
    keys = []
    try:
        keys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_keys.json")
        if os.path.exists(keys_path):
            with open(keys_path, encoding="utf-8") as f:
                keys_dict = json.load(f)
            for k, v in keys_dict.items():
                if k.startswith("OpenAI") and v and isinstance(v, str) and v.strip():
                    keys.append(v.strip())
    except Exception:
        pass
    
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        keys.append(env_key)
    
    return keys


def _cleanup_pdf_parts(parts: List[Tuple]) -> None:
    for path, is_temp, *_ in parts:
        if is_temp and path and os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass




def sanitize_police_translation_output(text: str) -> str:
    if not text or not isinstance(text, str):
        return text
    t = text.rstrip()
    low = t.lower()
    
    refusal_needles = (
        "i'm sorry, but i can't assist",
        "i'm sorry, but i cannot assist",
        "i am sorry, but i can't assist",
        "i am sorry, but i cannot assist",
        "i can't assist with that",
        "i can't assist with this request",
        "as an ai language model, i cannot",
        "i cannot provide",
        "i'm unable to",
    )
    
    for needle in refusal_needles:
        j = low.find(needle)
        if j >= 800:
            t = t[:j].rstrip()
            low = t.lower()
            break
    
    return t


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CLASS: MachineTranslator
# ══════════════════════════════════════════════════════════════════════════════

class MachineTranslator:
    """
    Dedicated Sinhala-to-English Machine Translation (MT) Engine.
    
    Priority order:
    1. OpenAI GPT-4o-mini      - Primary fallback.
    3. GitHub Models           - Fallback via Azure/GitHub Models.
    4. Local OCR + AI          - Final fallback using Tesseract + cloud AI.
    """
    
    def __init__(self):
        pass
    def translate_with_openai(self, text) -> str:
        """Fallback: Translate using OpenAI GPT-4o-mini."""
        try:
            import openai
        except ImportError:
            raise RuntimeError("openai package not installed")
            
        openai_keys = _load_openai_keys()
        if not openai_keys:
            raise RuntimeError("No OpenAI API keys found.")
            
        client = openai.OpenAI(api_key=openai_keys[0])
        
        prompt = f"Translate this Sinhala police report text to professional English:\n\n{text}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Sri Lanka Police translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4096
        )
        return response.choices[0].message.content.strip()
    @staticmethod
    def get_api_health() -> Dict[str, Dict[str, str]]:
        if not HAS_REQUESTS:
            return {"GitHub": {}}
        
        results = {"GitHub": {}}
        github_keys = {}
        
        try:
            github_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_keys.json")
            if os.path.exists(github_path):
                with open(github_path, encoding="utf-8") as f:
                    github_keys = json.load(f)
        except Exception:
            pass
        
        def _test_github(name: str, key: str) -> Tuple[str, str]:
            if not HAS_REQUESTS:
                return name, "❌ requests Missing"
            try:
                url = "https://models.inference.ai.azure.com/chat/completions"
                headers = {"Authorization": f"Bearer {key}"}
                payload = {
                    "messages": [{"role": "user", "content": "hi"}],
                    "model": "gpt-4o-mini",
                    "max_tokens": 5
                }
                r = requests.post(url, headers=headers, json=payload, timeout=5)
                
                rem = r.headers.get("x-ratelimit-remaining-requests")
                if rem:
                    try:
                        get_quota_mgr().update_from_headers(name, int(rem))
                    except Exception:
                        pass
                
                if r.status_code == 200:
                    return name, "✅ Active"
                if r.status_code == 429:
                    return name, "🔴 Rate Limited"
                return name, f"❌ Failed ({r.status_code})"
            except Exception:
                return name, "⚠️ Error"
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            gh_futs = [executor.submit(_test_github, k, v) for k, v in github_keys.items()]
            
            for f in concurrent.futures.as_completed(gh_futs):
                name, status = f.result()
                usage = get_quota_mgr().get_status(name, "GitHub")
                results["GitHub"][name] = f"{status} ({usage})"
        
        return results
    
    def _extract_pdf_to_json_turbo_text_ai(self, pdf_path: str, engine: str) -> Dict:
        from ai_engine_manager import _split_large_text, get_engine
        
        log.info(f"    [TURBO/{engine}] PDF → local text → {engine} JSON (set PDF_EXTRACT_AI_ENGINE)…")
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
        except (ValueError, TypeError):
            gh_pause = 0.0
        gh_pause = max(0.0, min(gh_pause, 120.0))
        
        try:
            gh_turbo_timeout = int(os.getenv("GITHUB_TURBO_TIMEOUT_SEC", "360"))
        except (ValueError, TypeError):
            gh_turbo_timeout = 360
        gh_turbo_timeout = max(120, min(gh_turbo_timeout, 900))
        
        for idx, chunk in enumerate(chunks):
            if idx > 0 and gh_pause > 0:
                time.sleep(gh_pause)
            
            seg_prompt = turbo_rules + f"SEGMENT {idx + 1} of {len(chunks)}:\n{chunk}"
            result = mgr._dispatch_engine(engine, seg_prompt, turbo_sys, gh_turbo_timeout)
            
            if not result or str(result).startswith("❌"):
                log.warning(f"    [TURBO/{engine}] segment {idx + 1} primary failed: {str(result)[:180]}")
                result = mgr.translation_fallback_after_exhausted(
                    seg_prompt, turbo_sys, timeout=gh_turbo_timeout, skip_github=(engine == "github")
                )
            
            if not result or str(result).startswith("❌"):
                raise RuntimeError(f"TURBO/{engine} segment {idx + 1} failed: {str(result)[:200]}")
            
            clean_res = re.sub(r"```json\s*", "", str(result))
            clean_res = re.sub(r"```\s*", "", clean_res).strip()
            
            try:
                data = json.loads(clean_res)
            except json.JSONDecodeError:
                data = json.loads(repair_json(clean_res))
            
            _merge_partial_turbo_json(merged, data)
        
        if merged.get("categories"):
            log.info(f"    [TURBO/{engine}] ✅ JSON merge complete.")
            return merged
        
        raise RuntimeError(f"TURBO/{engine}: no categories in merged JSON.")
    
    def _extract_sinhala_text_via_ai(self, pdf_path: str, engine: str) -> str:
        from ai_engine_manager import _split_large_text, get_engine
        
        log.info(f"    [OCR/{engine}] PDF → local text → {engine} (Sinhala cleanup, PDF_EXTRACT_AI_ENGINE)…")
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
                res = mgr.translation_fallback_after_exhausted(up, sys_p, timeout=300, skip_github=False)
            
            if not res or str(res).startswith("❌"):
                raise RuntimeError(f"Sinhala extract via {engine} failed part {i + 1}: {res}")
            
            out_parts.append(str(res).strip())
        
        merged = "\n\n".join(out_parts)
        log.info(f"    [OCR/{engine}] ✅ Combined Sinhala text: {len(merged)} chars.")
        return merged
    
    def _translate_pdf_via_text_ai(self, pdf_path: str, engine: str) -> str:
        from ai_engine_manager import _split_large_text, get_engine
        
        log.info(f"    [MT/{engine}] PDF → local text → {engine} English translation (PDF_EXTRACT_AI_ENGINE)…")
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
                res = mgr.translation_fallback_after_exhausted(
                    base + extra + "\n\nSOURCE:\n" + ch, sys_p, timeout=420, skip_github=False
                )
            
            if not res or str(res).startswith("❌"):
                raise RuntimeError(f"translate_pdf via {engine} failed part {i + 1}: {res}")
            
            outs.append(sanitize_police_translation_output(str(res)))
        
        merged = sanitize_police_translation_output("\n\n".join(outs))
        log.info(f"    [MT/{engine}] ✅ Combined translation: {len(merged)} chars.")
        return self.post_process_translation_terminology(merged)
    
    def post_process_translation_terminology(self, text: str) -> str:
        return enforce_terminology(text)
    
    # ────────────────────────────────────────────────────────────────────────
    # GEMINI FILE API METHODS (Primary)
    # ────────────────────────────────────────────────────────────────────────
    
    def extract_pdf_to_json_turbo(self, pdf_path: str) -> Dict:
        """
        TURBO MODE: One-shot extraction of all 28 categories into English JSON.
        """
        alt = _pdf_extract_ai_engine()
        if alt:
            return self._extract_pdf_to_json_turbo_text_ai(pdf_path, alt)
        
        # Fallback to GitHub + local OCR
        log.info("    [TURBO/GitHub] 🔄 Trying GitHub models via local OCR…")
        
        if not _env_truthy("PDF_EXTRACT_ALLOW_LOCAL_OCR"):
            log.info(
                "    [TURBO/OCR] ⏭️ local OCR fallback disabled."
            )
            raise RuntimeError(
                f"Turbo: local OCR fallback disabled."
            )
        
        try:
            from ai_engine_manager import _split_large_text, get_engine
            from local_ocr_tool import extract_text_from_pdf
            
            ocr_res = extract_text_from_pdf(pdf_path)
            ocr_text = _ocr_pages_to_text(ocr_res)
            
            if ocr_text and len(ocr_text.strip()) > 50:
                log.info(f"    [TURBO/GitHub] Local OCR returned {len(ocr_text)} chars. Sending to GitHub...")
                mgr = get_engine()
                
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
                except (ValueError, TypeError):
                    gh_pause = 0.0
                gh_pause = max(0.0, min(gh_pause, 120.0))
                
                for idx, chunk in enumerate(chunks):
                    if idx > 0 and gh_pause > 0:
                        time.sleep(gh_pause)
                    
                    github_prompt = turbo_rules + f"SEGMENT {idx + 1} of {len(chunks)}:\n{chunk}"
                    
                    try:
                        gh_turbo_timeout = int(os.getenv("GITHUB_TURBO_TIMEOUT_SEC", "360"))
                    except (ValueError, TypeError):
                        gh_turbo_timeout = 360
                    gh_turbo_timeout = max(120, min(gh_turbo_timeout, 900))
                    
                    result = mgr._call_github(
                        github_prompt,
                        "You are a professional Sri Lanka Police Data Architect. "
                        "Output complete JSON with full-length English descriptions — no omissions.",
                        gh_turbo_timeout,
                    )
                    
                    if not result or result.startswith("❌"):
                        log.warning(f"    [TURBO/GitHub] GitHub fallbacks failed: {result}")
                        chunk_failed = True
                        break
                    
                    clean_res = re.sub(r"```json\s*", "", result)
                    clean_res = re.sub(r"```\s*", "", clean_res).strip()
                    
                    try:
                        data = json.loads(clean_res)
                    except json.JSONDecodeError:
                        data = json.loads(repair_json(clean_res))
                    
                    _merge_partial_turbo_json(merged, data)
                
                if not chunk_failed and merged.get("categories"):
                    return merged
                
                if not chunk_failed:
                    log.warning("    [TURBO/GitHub] GitHub returned no category data after chunked merge.")
                
        except Exception as e:
            log.warning(f"    [TURBO/GitHub] GitHub turbo fallback exception: {e}")
        
        raise RuntimeError("Turbo extraction failed (GitHub).")

    # [Additional methods would continue here - translate_pdf, 
    #  extract_pdf_sinhala, translate_text_with_gemini, etc.]
    #  For brevity, showing the structure and key methods.
    
    def translate(self, text) -> str:
        """
        Main translate method - orchestrates priority order.
        """
        if not text or (isinstance(text, str) and len(text.strip()) < 2):
            return text
        
        # 1. OpenAI GPT-4o-mini (Primary)
        if HAS_OPENAI:
            try:
                return self.translate_with_openai(text)
            except Exception as e:
                log.warning(f"    [MT] OpenAI failed: {e}. Trying GitHub Models...")
        
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
                restricted_list=["github", "aimlapi", "groq", "ollama"],
            )
            if res and not res.startswith("❌"):
                log.info("    [MT/GitHub] ✅ GitHub Models fallback success.")
                return res
        except Exception as e:
            log.warning(f"    [MT] GitHub Models failed: {e}.")
        
        return "Translation unavailable"


# ══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

_translator: Optional[MachineTranslator] = None


def translate_sinhala_to_english(text) -> str:
    """Convenience function: translate Sinhala text to English."""
    global _translator
    if _translator is None:
        _translator = MachineTranslator()
    return _translator.translate(text)


def extract_pdf_to_sinhala(pdf_path: str) -> str:
    """Convenience function: extract Sinhala text from PDF via Gemini."""
    global _translator
    if _translator is None:
        _translator = MachineTranslator()
    return _translator.extract_pdf_sinhala(pdf_path)


def translate_pdf_to_english(pdf_path: str) -> str:
    """Convenience function: translate full PDF to English via Gemini."""
    global _translator
    if _translator is None:
        _translator = MachineTranslator()
    return _translator.translate_pdf(pdf_path)


def full_pdf_sinhala_only_then_english(
    pdf_path: str,
    english_txt: Optional[str] = None,
    sinhala_txt: Optional[str] = None,
) -> str:
    """
    Full PDF pipeline: extract all Sinhala first, then translate that text to English only.
    """
    global _translator
    if _translator is None:
        _translator = MachineTranslator()
    return _translator.translate_full_sinhala_pdf_to_english(
        pdf_path, output_txt=english_txt, save_sinhala_txt=sinhala_txt
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN (for testing)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 MachineTranslator — Quick Test")
    print("=" * 60)
    
    # Test basic translation
    translator = MachineTranslator()
    
    test_text = "කොළඹ පොලිසිය, සොරකමක්."
    print(f"\nInput:  {test_text}")
    
    try:
        result = translator.translate(test_text)
        print(f"Output: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ Test complete.")