import sys
import os
import argparse
import fitz  # PyMuPDF
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sinhala_section_splitter import split_by_sections

def extract_raw_text(file_path):
    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

def main():
    parser = argparse.ArgumentParser(description="Sinhala Section Splitting Tool")
    parser.add_argument("input", help="Path to PDF or TXT file")
    parser.add_argument("--mode", choices=["General", "Security"], default="General", help="Reporting mode")
    parser.add_argument("--output", help="Optional output JSON path")
    
    args = parser.parse_args()
    
    print(f"--- Process Starting: {os.path.basename(args.input)} [{args.mode}] ---")
    
    try:
        raw_text = extract_raw_text(args.input)
        sections = split_by_sections(raw_text, args.mode)
        
        # Display Results
        print("\n=== STRUCTURED SINHALA CONTENT ===\n")
        non_nil_count = 0
        for title, body in sections:
            if body != "Nil":
                print(f"[{title}]")
                # Print first 200 chars for preview
                preview = body[:200].replace("\n", " ").strip()
                print(f"Content: {preview}...")
                print("-" * 40)
                non_nil_count += 1
        
        print(f"\nSummary: Identified {non_nil_count} non-empty sections.")
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump({"file": args.input, "mode": args.mode, "sections": [{"title": t, "body": b} for t, b in sections]}, f, indent=4, ensure_ascii=False)
            print(f"Full results saved to: {args.output}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
