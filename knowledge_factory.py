import json
import os
import re

from ai_engine_manager import get_engine

# Configuration
SAMPLE_DIR = "sample"
DATASET_PATH = "dataset/police_training_data.jsonl"
TEACHERS = ["gemini", "openrouter", "github"]

def knowledge_factory():
    print("🚀 [Knowledge-Factory] Starting Production...")
    engine = get_engine()

    # 1. Identify source PDFs
    pdfs = [f for f in os.listdir(SAMPLE_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        print("❌ [Factory] No PDFs found in sample directory.")
        return

    print(f"  [Factory] Found {len(pdfs)} source reports.")
    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)

    new_samples = 0

    for pdf in pdfs:
        pdf_path = os.path.join(SAMPLE_DIR, pdf)
        print(f"\n📄 [Process] Extracting knowledge from: {pdf}")

        try:
            from local_ocr_tool import extract_text_from_pdf
            ocr_res = extract_text_from_pdf(pdf_path)
            sinhala_text = "\n".join(str(p) for p in ocr_res if p)
            if not sinhala_text or len(sinhala_text) < 100: continue
        except Exception as e:
            print(f"  [Error] OCR failed: {e}")
            continue

        # Distillation Chunks
        chunk_size = 4000
        chunks = [sinhala_text[i:i + chunk_size] for i in range(0, len(sinhala_text), chunk_size - 400)]

        for idx, chunk in enumerate(chunks):
            print(f"  🧠 [Distill] Chunk {idx+1}/{len(chunks)}...")

            teacher_prompt = (
                "You are the Master Sri Lanka Police Data Architect. Study this Sinhala report snippet.\n\n"
                "TASK:\n"
                "1. Identify every individual criminal/security incident mentioned.\n"
                "2. Extract exactly 8-field English JSON: station, division, date, time, description, financial_loss, status, victim_suspect_names.\n"
                "3. In the final list, add 'sinhala_raw' field with the source Sinhala text for each incident.\n"
                "OUTPUT: Respond ONLY with a JSON list [ { 'sinhala_raw': '...', 'english_json': {...} }, ... ]\n\n"
                f"SNIPPET:\n{chunk}"
            )

            # Try Teachers in order of intelligence/availability
            result = None
            used_teacher = None
            for t in TEACHERS:
                print(f"    [Trying Teacher: {t}]...")
                res = engine.call_ai(teacher_prompt, system_prompt="Expert Distiller", restricted_list=[t])
                if not res.startswith("❌"):
                    result = res
                    used_teacher = t
                    break
                print(f"    [Teacher {t} Failed: {res[:60]}]")

            if not result:
                print("    ❌ All Teachers failed for this chunk.")
                continue

            try:
                # Optimized cleaning for multiple potential teachers
                match = re.search(r'\[.*\]', result, re.DOTALL)
                if not match:
                    cleaned = result.replace("```json", "").replace("```", "").strip()
                    match = re.search(r'\[.*\]', cleaned, re.DOTALL)

                if match:
                    data_list = json.loads(match.group(0))
                    with open(DATASET_PATH, "a", encoding="utf-8") as f:
                        for entry in data_list:
                            raw_s = entry.get("sinhala_raw", "").strip()
                            gold_j = entry.get("english_json", {})
                            if not raw_s or len(gold_j) < 5: continue

                            sample = {
                                "messages": [
                                    {"role": "system", "content": "You are a professional Sri Lanka Police AI Architect."},
                                    {"role": "user", "content": raw_s},
                                    {"role": "assistant", "content": json.dumps(gold_j, ensure_ascii=False)}
                                ]
                            }
                            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                            new_samples += 1
                    print(f"    ✅ Added {len(data_list)} samples (Teacher: {used_teacher}).")
            except Exception as e:
                print(f"    ⚠️ Parsing error: {e}")

    print(f"\n🏆 [Factory] Done! Produced {new_samples} expert samples.")

if __name__ == "__main__":
    knowledge_factory()
