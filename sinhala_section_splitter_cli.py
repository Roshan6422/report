import sys
import os
import json
import re
from pypdf import PdfReader

# Add current directory to path
sys.path.append(os.getcwd())
import sinhala_section_splitter

def extract_text_from_pdf(pdf_path):
    """Simple pypdf extraction for splitting."""
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        return full_text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python sinhala_section_splitter_cli.py <input_pdf> <output_json>")
        return

    pdf_path = sys.argv[1]
    output_json = sys.argv[2]

    print(f"Extracting text from: {pdf_path}...")
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text:
        return

    print("Splitting into 29 categories...")
    sections = sinhala_section_splitter.split_by_sections(raw_text)
    
    # Format for JSON
    data = {
        "filename": os.path.basename(pdf_path),
        "sections": [{"title": t, "body": b} for t, b in sections]
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Done! Saved to {output_json}")

if __name__ == "__main__":
    main()
