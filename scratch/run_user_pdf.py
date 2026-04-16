import os
import sys
import json
import traceback
import time

# Add project root to path
sys.path.append(os.getcwd())

from desktop_pipeline import process_pdf_hyper_hybrid

def run_sample_process():
    # Use the renamed ASCII path
    pdf_path = "d:\\PROJECTS\\report_2026_03_14.pdf"
    output_dir = r"d:\PROJECTS\pdf convert tool\outputs"
    
    # Use a unique log for this run
    log_file = f"scratch/run_log_{int(time.time())}.txt"
    
    with open(log_file, "w", encoding="utf-8") as L:
        def log_msg(msg):
            L.write(msg + "\n")
            L.flush()
            print(msg, flush=True)

        log_msg(f"Starting background processing for: {pdf_path}")
        
        def progress_cb(cat, data):
            if cat == "OCR_UPDATE":
                msg = data.get('msg', '')
                log_msg(f"  [STATUS] {msg}")
            else:
                log_msg(f"  [DONE] Category {cat}: {data.get('count')} incidents")

        try:
            # Use our updated hybrid pipeline which now uses page-by-page translation
            results = process_pdf_hyper_hybrid(
                pdf_path, 
                progress_callback=progress_cb,
                output_folder=output_dir,
                fast_complete=False # Use the high-fidelity page-by-page path
            )
            
            if results.get("success"):
                log_msg("Processing Complete!")
                summary = {
                    "pdf_path": pdf_path,
                    "translation_len": len(results.get("full_translation", "")),
                    "generated_pdfs": results.get("generated_pdfs", []),
                    "preview_head": results.get("full_translation", "")[:2000]
                }
                with open("scratch/last_run_summary.json", "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2)
            else:
                log_msg(f"Failed: {results.get('error')}")

        except Exception as e:
            log_msg(f"Exception: {e}")
            log_msg(traceback.format_exc())

if __name__ == "__main__":
    run_sample_process()
