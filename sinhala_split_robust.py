import os
import sys
import json
from pypdf import PdfReader
import sinhala_section_splitter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_robust(pdf_path, output_json):
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found: {pdf_path}")
            return False
            
        reader = PdfReader(pdf_path)
        full_text = ""
        total_pages = len(reader.pages)
        logger.info(f"Processing PDF: {pdf_path} ({total_pages} pages)")
        
        for i, page in enumerate(reader.pages):
            logger.info(f"Extracting page {i+1}/{total_pages}...")
            full_text += page.extract_text() + "\n"
            
        logger.info("Splitting text into 29 categories...")
        sections = sinhala_section_splitter.split_by_sections(full_text)
        
        data = {
            "filename": os.path.basename(pdf_path),
            "sections": [{"title": t, "body": b} for t, b in sections]
        }

        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Split complete: {output_json}")
        return True
    except Exception as e:
        logger.error(f"Error in robust split: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sinhala_split_robust.py <input_pdf> <output_json>")
    else:
        split_robust(sys.argv[1], sys.argv[2])
