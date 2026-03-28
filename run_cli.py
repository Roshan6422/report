import os
import sys
import json
import time

# Add project root to path
os.chdir(r"d:\PROJECTS\pdf convert tool")
sys.path.append(r"d:\PROJECTS\pdf convert tool")

import translator_pipeline
import web_report_engine
import pipeline_utils

# =============================================================================
# SYSTEM VERSION
# =============================================================================
SYSTEM_VERSION = pipeline_utils.SYSTEM_VERSION

# Progress Reporting Hook (to be injected by the app)
update_progress_fn = None

def report_progress(step, details):
    if update_progress_fn:
        update_progress_fn(step, details)
    else:
        print(f"  [Progress] {step}: {details}")

def process_custom_pdf(pdf_path, use_ai=False, api_key=None, engine="deepseek"):
    print(f"\n--- ANTIGRAVITY ENGINE {SYSTEM_VERSION} ---")
    print(f"File: {pdf_path}")
    print("⚠️ [Note] Sinhala-to-English translation is DISABLED. This engine expects English text.")
    
    # 1. Extract layout-aware raw text
    full_text = translator_pipeline.extract_text_with_layout(pdf_path)
    if not full_text:
        print("Error extracting text.")
        return
        
    # 2. Split General and Security (Based on English keywords now)
    general_text, security_text = translator_pipeline.split_sinhala_document(full_text)
    
    # Base paths
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.join(os.path.dirname(pdf_path), "sinhala")
    os.makedirs(output_dir, exist_ok=True)
    
    html_gen = os.path.join(output_dir, f"{base_name}_General_Report.html")
    pdf_gen = os.path.join(output_dir, f"{base_name}_General_Report.pdf")
    html_sec = os.path.join(output_dir, f"{base_name}_Situation_Report.html")
    pdf_sec = os.path.join(output_dir, f"{base_name}_Situation_Report.pdf")

    # ==========================
    # GENERAL REPORT
    # ==========================
    print("\n[Step 2] Structuring General Report (Offline Regex)...")
    gen_data, err = translator_pipeline.extract_and_translate_structured(
        pre_translated_text=general_text,
        report_type="General",
        use_ai=use_ai,
        api_key=api_key
    )
    
    if gen_data:
        if not use_ai:
            gen_data, verify_msgs = translator_pipeline.verify_and_fix_report(gen_data)
            for msg in verify_msgs:
                print(f"  {msg}")
        
        # --- QUALITY GATE ---
        passed, qg_msg, conf = pipeline_utils.quality_gate_check(gen_data)
        print(f"  {qg_msg}")
        
        web_report_engine.generate_html_report(gen_data, html_gen, report_type="General")
        web_report_engine.html_to_pdf(html_gen, pdf_gen)
        print(f"  [OK] PDF: {pdf_gen}")
    else:
        print(f"  ❌ Failed: {err}")

    # ==========================
    # SECURITY REPORT
    # ==========================
    print("\n[Step 3] Structuring Security Report (Offline Regex)...")
    sec_data, err = translator_pipeline.extract_and_translate_structured(
        pre_translated_text=security_text,
        report_type="Security",
        use_ai=use_ai,
        api_key=api_key
    )

    if sec_data:
        sec_data, verify_msgs = translator_pipeline.verify_and_fix_report(sec_data)
        for msg in verify_msgs:
            print(f"  {msg}")
        
        # --- QUALITY GATE ---
        passed, qg_msg, conf = pipeline_utils.quality_gate_check(sec_data)
        print(f"  {qg_msg}")
        
        report_progress("Generating Security Report", "Creating HTML and PDF for Security Report...")
        
        web_report_engine.generate_html_report(sec_data, html_sec, report_type="Security")
        web_report_engine.html_to_pdf(html_sec, pdf_sec)
        print(f"  ✅ PDF: {pdf_sec}")
    else:
        print(f"  ❌ Failed: {err}")
        report_progress("Error", f"Failed to structure Security Report: {err}")

    print("\n✅ PROCESS COMPLETE!")
    report_progress("Complete", "PDF processing finished.")

def process_pretranslated_text(english_text, output_dir=None, base_name="Report", use_ai=False, api_key=None, engine="deepseek"):
    """
    100% OFFLINE MODE: Accepts already-translated English text.
    Splits into General/Security, structures with Regex, generates both PDFs instantly.
    Enhanced with: logging, caching, confidence scoring, quality gate.
    """
    report_progress("Starting Instant Process", "Processing pre-translated English text...")
    print(f"\n--- ANTIGRAVITY ENGINE {SYSTEM_VERSION} (INSTANT) ---")
    
    if not output_dir:
        output_dir = os.path.join("uploads", "sinhala")
    os.makedirs(output_dir, exist_ok=True)
    
    html_gen = os.path.join(output_dir, f"{base_name}_General_Report.html")
    pdf_gen = os.path.join(output_dir, f"{base_name}_General_Report.pdf")
    html_sec = os.path.join(output_dir, f"{base_name}_Situation_Report.html")
    pdf_sec = os.path.join(output_dir, f"{base_name}_Situation_Report.pdf")
    
    # 1. SPLIT: General vs Security
    print("\n[Step 1] Categorizing into General & Security...")
    general_text, security_text = translator_pipeline.split_sinhala_document(english_text)
    
    # 2. GENERAL REPORT
    print("\n[Step 2] Structuring General Report (Offline Regex)...")
    if not use_ai:
        general_text = translator_pipeline.reinforce_dataset_on_english(general_text)
    gen_data, err = translator_pipeline.extract_and_translate_structured(
        pre_translated_text=general_text,
        report_type="General",
        use_ai=use_ai,
        api_key=api_key
    )
    
    gen_confidence = 0.0
    if gen_data:
        if not use_ai:
            gen_data, verify_msgs = translator_pipeline.verify_and_fix_report(gen_data)
            for msg in verify_msgs:
                print(f"  {msg}")
        
        # --- QUALITY GATE ---
        passed, qg_msg, gen_confidence = pipeline_utils.quality_gate_check(gen_data)
        print(f"  {qg_msg}")
        
        web_report_engine.generate_html_report(gen_data, html_gen, report_type="General")
        web_report_engine.html_to_pdf(html_gen, pdf_gen)
        print(f"  ✅ PDF: {pdf_gen}")
    
    # 3. SECURITY REPORT
    print("\n[Step 3] Structuring Security Report (Offline Regex)...")
    if not use_ai:
        security_text = translator_pipeline.reinforce_dataset_on_english(security_text)
    sec_data, err = translator_pipeline.extract_and_translate_structured(
        pre_translated_text=security_text,
        report_type="Security",
        use_ai=use_ai,
        api_key=api_key
    )
    
    sec_confidence = 0.0
    if sec_data:
        sec_data, verify_msgs = translator_pipeline.verify_and_fix_report(sec_data)
        for msg in verify_msgs:
            print(f"  {msg}")
        
        # --- QUALITY GATE ---
        passed, qg_msg, sec_confidence = pipeline_utils.quality_gate_check(sec_data)
        print(f"  {qg_msg}")
        
        web_report_engine.generate_html_report(sec_data, html_sec, report_type="Security")
        web_report_engine.html_to_pdf(html_sec, pdf_sec)
        print(f"  ✅ PDF: {pdf_sec}")
    
    avg_confidence = (gen_confidence + sec_confidence) / 2 if (gen_confidence + sec_confidence) > 0 else 0
    print(f"\n✅ OFFLINE PROCESS COMPLETE! (Overall Confidence: {avg_confidence:.1%})")
    return pdf_gen, pdf_sec

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=f"Antigravity Engine {SYSTEM_VERSION}")
    parser.add_argument("file", help="Path to English report text file")
    parser.add_argument("--use_ai", action="store_true", help="Use AI for structuring")
    parser.add_argument("--api_key", default="", help="AI API Key")
    parser.add_argument("--engine", default="deepseek", choices=["deepseek", "claude", "fastapi", "github", "groq"], help="AI engine choice")
    args = parser.parse_args()
    
    if os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        base = os.path.splitext(os.path.basename(args.file))[0]
        output_dir = os.path.join("uploads", "sinhala")
        process_pretranslated_text(content, base_name=base, use_ai=args.use_ai, api_key=args.api_key, output_dir=output_dir, engine=args.engine)
    else:
        print(f"Error: File not found {args.file}")
