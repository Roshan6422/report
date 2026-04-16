import os
import sys
import re
import json
import time
from datetime import datetime

# Prevent Unicode Encode errors on Windows console with emojis
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from ai_engine_manager import get_engine
from local_ocr_tool import extract_text_from_pdf

# Configuration
SIN_DIR = r"D:\PROJECTS\ha\english\New folder"
ENG_DIR = r"D:\PROJECTS\ha\english\New folder\New folder"
OUTPUT_DB = "dataset/expert_gold_pairs.json"

def parse_sinhala_date(filename):
    match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}" if match else None

def parse_english_date(filename):
    match = re.search(r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', filename, re.IGNORECASE)
    if match:
        day, month_str, year = match.group(1).zfill(2), match.group(2), match.group(3)
        try:
            return datetime.strptime(f"{day} {month_str} {year}", "%d %B %Y").strftime("%Y-%m-%d")
        except: return None
    return None

def main():
    print("[Expert-Harvester] Starting Batch Alignment...")
    engine = get_engine()
    os.makedirs(os.path.dirname(OUTPUT_DB), exist_ok=True)
    
    sin_files = [f for f in os.listdir(SIN_DIR) if f.lower().endswith(".pdf")]
    eng_files = [f for f in os.listdir(ENG_DIR) if f.lower().endswith(".pdf")]
    
    mapping = {}
    for sf in sin_files:
        d = parse_sinhala_date(sf)
        if d:
            if d not in mapping: mapping[d] = {"sin": [], "eng": []}
            mapping[d]["sin"].append(os.path.join(SIN_DIR, sf))
    for ef in eng_files:
        d = parse_english_date(ef)
        if d:
            if d not in mapping: mapping[d] = {"sin": [], "eng": []}
            mapping[d]["eng"].append(os.path.join(ENG_DIR, ef))

    total_pairs = 0
    
    # Sort by date to process oldest to newest
    for date in sorted(mapping.keys()):
        data = mapping[date]
        if not data["sin"] or not data["eng"]:
            print(f"  [Skip] Date {date} is missing one language.")
            continue
            
        print(f"\n[Processing] Date: {date}")
        
        # 1. Extract Sinhala Text
        sin_text = ""
        for sf in data["sin"]:
            print(f"  [OCR] Sinhala: {os.path.basename(sf)}")
            try:
                pages = extract_text_from_pdf(sf)
                sin_text += "\n".join(pages)
            except Exception as e:
                print(f"  ❌ OCR Fail: {e}")
        
        # 2. Extract English Text
        eng_text = ""
        for ef in data["eng"]:
            print(f"  [OCR] English: {os.path.basename(ef)}")
            try:
                # English PDFs are usually digital, but we use the same robust tool
                pages = extract_text_from_pdf(ef)
                eng_text += "\n".join(pages)
            except Exception as e:
                print(f"  ❌ OCR Fail: {e}")

        if not sin_text or not eng_text:
            continue

        # 3. AI Alignment (Chunking if needed)
        print("  [Aligning] Using AI Aligner...")
        
        # We might need to chunk if the report is very long.
        # But for now, let's try a large context approach.
        
        alignment_prompt = (
            "You are a Master Police Data Aligner. I will provide you with a full Sinhala report and its corresponding English reports.\n\n"
            "TASK:\n"
            "1. Find every matching incident that exists in BOTH the Sinhala and English text.\n"
            "2. Extract the EXACT original Sinhala incident description.\n"
            "3. Extract the EXACT corresponding professional English translation from the English report.\n"
            "4. Assign the correct category code (01-29).\n"
            "5. Include metadata (station, date, category_name).\n\n"
            "OUTPUT: Respond ONLY with a JSON list: [ { 'sinhala': '...', 'english': '...', 'cat_num': '...', 'station': '...' }, ... ]\n\n"
            f"--- SINHALA REPORT ---\n{sin_text[:15000]}\n\n"
            f"--- ENGLISH REPORTS ---\n{eng_text[:15000]}"
        )
        
        # Use an intelligent teacher (Gemini or GitHub)
        res = engine.call_ai(alignment_prompt, system_prompt="Expert Alignment Architect", restricted_list=["gemini", "github"])
        
        try:
            # Clean JSON
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                batch_data = json.loads(match.group(0))
                with open(OUTPUT_DB, "a", encoding="utf-8") as f:
                    for entry in batch_data:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                        total_pairs += 1
                print(f"  [Done] Harvested {len(batch_data)} golden pairs for {date}.")
            else:
                print(f"  [Warning] No JSON alignment found for {date}.")
        except Exception as e:
            print(f"  [Error] Alignment Error: {e}")
            
    print(f"\n[Harvester] Done! Total expert pairs collected: {total_pairs}")

if __name__ == "__main__":
    main()
