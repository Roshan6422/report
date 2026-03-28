import fitz  # PyMuPDF
import re
import datetime
import json
import os
import time
import deepseek_client
from deepseek_client import DeepSeekClient
import claude_client
from claude_client import ClaudeClient
import sinhala_section_splitter
import pipeline_utils
import regex_engine
import analytics_engine
import markdown_parser
from patterns import SECTION_HEADER_PATTERN
from sinhala_repair import pre_process_expert_layout

# Progress Reporting Hook
update_progress_fn = None

def report_progress(step, details):
    if update_progress_fn:
        update_progress_fn(step, details)
    else:
        print(f"  [Progress] {step}: {details}")

# --- OFFLINE CONSTANTS ---
MODEL_MAP = {
    "Offline Regex Engine": None
}

# --- PREPROCESSING ---
def reinforce_dataset_on_english(english_text):
    """Force-injects the professional dataset terms into English text to correct and standardize terminology."""
    from translation_vocabulary import INCIDENT_TEMPLATES, COMMON_PHRASES, SECTION_NAMES_SINHALA, PROVINCES_SINHALA
    from station_mapping import SINHALA_TO_ENGLISH
    
    refined = english_text

    # ✅ FIX: avoid None crash
    if not refined:
        return ""

    # Ensure Station Names are matched
    for sin_name, eng_name in SINHALA_TO_ENGLISH.items():
        refined = re.sub(re.escape(eng_name), eng_name.upper(), refined, flags=re.IGNORECASE)
    
    all_vocab = {**PROVINCES_SINHALA, **SECTION_NAMES_SINHALA, **COMMON_PHRASES}
    for sin_term, eng_term in sorted(all_vocab.items(), key=lambda x: len(x[0]), reverse=True):
        refined = re.sub(re.escape(sin_term), eng_term, refined, flags=re.IGNORECASE)
    
    return refined


def extract_text_with_layout(pdf_path):
    """Layout-aware extraction that prevents two-column text merging."""
    try:
        pdf_document = fitz.open(pdf_path)
        full_text = ""

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            blocks = page.get_text("blocks")

            # ✅ FIX: safe indexing
            text_blocks = [b for b in blocks if len(b) > 6 and b[6] == 0]

            text_blocks.sort(key=lambda b: (round(b[1] / 15), b[0]))

            for b in text_blocks:
                # ✅ FIX: safe access
                if len(b) > 4:
                    full_text += b[4] + "\n"

        pdf_document.close()
        return full_text

    except Exception as e:
        print(f"Extraction Error: {e}")
        return ""


def split_sinhala_document(full_text):
    """Slices the raw document text into General and Security sections."""
    sec_en = re.search(r'SECURITY\s*SITUATION', full_text, re.IGNORECASE)
    gen_en = re.search(r'GENERAL\s*SITUATION', full_text, re.IGNORECASE)

    if sec_en and gen_en:
        sec_idx, gen_idx = sec_en.start(), gen_en.start()

        if sec_idx < gen_idx:
            return full_text[gen_idx:].strip(), full_text[sec_idx:gen_idx].strip()

        return full_text[gen_idx:sec_idx].strip(), full_text[sec_idx:].strip()

    # fallback
    return full_text.strip(), full_text.strip()


def split_sinhala_document_to_raw(text, report_type):
    """Splits into functional blocks for parallel AI processing."""
    # ✅ FIX: safe call
    try:
        return sinhala_section_splitter.split_by_sections(text, report_type)
    except Exception:
        return []


# --- CORE ORCHESTRATOR ---

def extract_and_translate_structured(
    sinhala_text=None,
    api_key=None,
    report_type="General",
    engine="deepseek",
    pre_translated_text=None,
    pr=None,
    use_ai=False
):

    if not pre_translated_text and sinhala_text:
        pre_translated_text = sinhala_text
    
    if not pre_translated_text:
        return None, "❌ ERR: No text provided."
    
    start_time = time.time()
    proc_log = pipeline_utils.create_processing_log(pre_translated_text, report_type, use_ai)
    # Include report_type in hash so General/Security don't share cache
    input_hash = pipeline_utils.generate_hash(pre_translated_text + report_type)
    
    cached = pipeline_utils.cache_get(input_hash)
    if cached and not use_ai:
        # Validate cached data has meaningful content before serving it
        cached_total = sum(
            len(p.get("incidents", []))
            for s in cached.get("sections", [])
            for p in s.get("provinces", [])
        )
        if cached_total > 0:
            print(f"  [Cache] HIT for input hash {input_hash} ({cached_total} incidents)")
            proc_log["cache_hit"] = True
            return cached, None
        else:
            print(f"  [Cache] HIT but empty — ignoring poisoned cache, reprocessing.")

    # Select the requested AI Engine
    if engine.lower() in ["fastapi", "github", "groq"]:
        from fast_api_client import FastApiClient
        provider = "groq" if engine.lower() == "groq" else "github"
        assistant = FastApiClient(api_key=api_key, provider=provider)
        model_display_name = f"FastAPI ({assistant.provider.capitalize()} - {assistant.model})"
    elif engine.lower() == "claude":
        assistant = ClaudeClient(api_key=api_key)
        model_display_name = f"Claude ({assistant.model})"
    else:
        assistant = DeepSeekClient()
        model_display_name = f"{'Ollama' if hasattr(assistant, 'assistant') and assistant.assistant.fallback_active else 'OpenRouter'} ({getattr(assistant, 'model', 'default')})"

    result_data = None

    # 1. Expert Layout Repair
    print(f"  [Pipeline] Running Expert Layout Repair (v2.2)...")
    pre_translated_text = pre_process_expert_layout(pre_translated_text)
    
    if use_ai:
        report_progress("Parallel AI Generation", f"Starting {report_type} matrix structuring with {model_display_name}...")

        # ✅ FIX: ensure sections always defined
        sections = []
        try:
            sections = sinhala_section_splitter.split_by_sections(pre_translated_text, report_type)
        except Exception:
            sections = []

        final_markdown = ""

        # Process sections SEQUENTIALLY to avoid Ollama 429 rate limits
        # Ollama is a local single-instance server — concurrent requests cause 429
        for title, body in sections:
            print(f"  [AI] Processing section: {title}")
            result = assistant.structure_section(title, body, report_type)
            if result and result.startswith("❌"):
                print(f"  [AI RETRY] {title} failed ({result}), retrying in 5s...")
                import time as _time; _time.sleep(5)
                result = assistant.structure_section(title, body, report_type)
            if result and not result.startswith("❌"):
                final_markdown += result + "\n\n"
            else:
                print(f"  [AI SKIP] {title}: {result}")
            report_progress("Section Structured", f"Completed: {title}")
        
        result_data = markdown_parser.parse_high_fidelity_markdown(final_markdown)

        # Fallback: if AI produced no incidents at all, use regex engine instead
        ai_total = sum(
            len(p.get("incidents", []))
            for s in (result_data.get("sections", []) if result_data else [])
            for p in s.get("provinces", [])
        )
        if ai_total == 0:
            print(f"  [Pipeline] AI produced 0 incidents — falling back to Regex Engine.")
            result_data = regex_engine.structure_with_regex(pre_translated_text, report_type)

        # polish pass disabled
        pass

    else:
        result_data = regex_engine.structure_with_regex(pre_translated_text, report_type)
        sections = result_data.get("sections", []) if result_data else []

    if result_data:
        proc_log["sections_processed"] = len(sections)

        # ✅ FIX: prevent crash if AI disabled
        if use_ai:
            os.makedirs("tmp", exist_ok=True)
            with open(os.path.join("tmp", f"ai_debug_{report_type}.md"), "w", encoding="utf-8") as f:
                f.write(final_markdown)

        result_data = pipeline_utils.enhance_pipeline_output(result_data, pre_translated_text)

        total_incs = sum(
            len(p.get("incidents", []))
            for s in result_data.get("sections", [])
            for p in s.get("provinces", [])
        )

        proc_log["total_incidents"] = total_incs
        # Only cache if we have meaningful data (avoid poisoning cache with empty AI results)
        if total_incs > 0:
            pipeline_utils.cache_set(input_hash, result_data)
        else:
            print(f"  [Cache] Skipping cache write — 0 incidents extracted.")
        proc_log["status"] = "success"
    else:
        proc_log["status"] = "failed"
        proc_log["errors"].append("No data extracted")
    
    proc_log["processing_time_ms"] = round((time.time() - start_time) * 1000, 1)
    pipeline_utils.save_processing_log(proc_log)

    return result_data, None


def verify_and_fix_report(data, engine="", api_key="", log_fn=None):
    """Enhanced offline validation with confidence scoring."""
    if not data:
        return data, ["❌ No data to validate"]

    # Only run enhancement if not already done
    if "_enhancement" not in data:
        data = pipeline_utils.enhance_pipeline_output(data)
    
    enhancement = data.get("_enhancement", {})
    messages = [
        f"✅ Validation: Complete.",
        f"📊 Confidence Score: {enhancement.get('confidence', 0.0):.1%}",
        f"🔍 Validation Issues: {enhancement.get('validation_issues', 0)}",
        f"🚧 {enhancement.get('quality_gate', '')}"
    ]
    return data, messages