"""
batch_processor.py — Batch PDF Processing Engine
=================================================
Process multiple PDFs in sequence with progress tracking and error recovery.

System Version: v2.1.0
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(__file__))
import run_cli
import pipeline_utils

class BatchProcessor:
    def __init__(self, input_dir="uploads", output_dir=None):
        self.input_dir = input_dir
        self.output_dir = output_dir or os.path.join(input_dir, "sinhala")
        self.results = []
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }
    
    def process_directory(self, use_ai=False, api_key=None, engine="deepseek"):
        """Process all PDFs in the input directory."""
        pdf_files = list(Path(self.input_dir).glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {self.input_dir}")
            return self.results
        
        self.stats["total"] = len(pdf_files)
        self.stats["start_time"] = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"BATCH PROCESSING: {len(pdf_files)} PDFs")
        print(f"{'='*60}\n")
        
        for idx, pdf_path in enumerate(pdf_files, 1):
            print(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
            print("-" * 60)
            
            result = {
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "status": "pending",
                "error": None,
                "outputs": [],
                "processing_time": 0
            }
            
            start = time.time()
            
            try:
                # Process the PDF
                run_cli.process_custom_pdf(
                    str(pdf_path),
                    use_ai=use_ai,
                    api_key=api_key,
                    engine=engine
                )
                
                # Check if outputs were created
                base_name = os.path.splitext(pdf_path.name)[0]
                expected_outputs = [
                    os.path.join(self.output_dir, f"{base_name}_General_Report.pdf"),
                    os.path.join(self.output_dir, f"{base_name}_Situation_Report.pdf")
                ]
                
                result["outputs"] = [f for f in expected_outputs if os.path.exists(f)]
                
                if result["outputs"]:
                    result["status"] = "success"
                    self.stats["success"] += 1
                    print(f"✓ Success: Generated {len(result['outputs'])} reports")
                else:
                    result["status"] = "failed"
                    result["error"] = "No output files generated"
                    self.stats["failed"] += 1
                    print(f"✗ Failed: No outputs generated")
                    
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                self.stats["failed"] += 1
                print(f"✗ Error: {e}")
            
            result["processing_time"] = time.time() - start
            self.results.append(result)
        
        self.stats["end_time"] = datetime.now()
        self._print_summary()
        self._save_batch_log()
        
        return self.results
    
    def _print_summary(self):
        """Print batch processing summary."""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        print(f"\n{'='*60}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total PDFs:     {self.stats['total']}")
        print(f"Successful:     {self.stats['success']} ✓")
        print(f"Failed:         {self.stats['failed']} ✗")
        print(f"Success Rate:   {(self.stats['success']/self.stats['total']*100):.1f}%")
        print(f"Total Time:     {duration:.1f}s")
        print(f"Avg Time/PDF:   {(duration/self.stats['total']):.1f}s")
        print(f"{'='*60}\n")
    
    def _save_batch_log(self):
        """Save batch processing log."""
        log_dir = "tmp/batch_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(log_dir, f"batch_{timestamp}.json")
        
        log_data = {
            "stats": {
                **self.stats,
                "start_time": self.stats["start_time"].isoformat(),
                "end_time": self.stats["end_time"].isoformat()
            },
            "results": self.results
        }
        
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"Batch log saved: {log_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process police report PDFs")
    parser.add_argument("--input", default="uploads", help="Input directory with PDFs")
    parser.add_argument("--output", default=None, help="Output directory (default: input/sinhala)")
    parser.add_argument("--ai", action="store_true", help="Use AI structuring (default: regex only)")
    parser.add_argument("--engine", default="deepseek", choices=["deepseek", "claude", "gemini", "openrouter", "fastapi", "github", "groq"], help="AI engine to use")
    parser.add_argument("--api-key", default=None, help="API key for AI engine")
    
    args = parser.parse_args()
    
    processor = BatchProcessor(input_dir=args.input, output_dir=args.output)
    processor.process_directory(use_ai=args.ai, api_key=args.api_key, engine=args.engine)
