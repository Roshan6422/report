import os
import sys

# Force local OCR because Kaggle GPU is currently crashing
os.environ["KAGGLE_OCR_URL"] = "http://localhost:9999/gpu-ocr"
os.environ["OCR_FAST"] = "1"

if sys.stdout.encoding.lower() != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

from local_ocr_tool import extract_text_from_pdf


def main():
    print("[Full Context] Extracting text for Master Knowledge Base...")

    sin_pdf = r"D:\PROJECTS\ha\english\New folder\2026.03.21 දින සිදුවීම් වාර්තාව.pdf"
    gen_pdf = r"D:\PROJECTS\ha\english\New folder\New folder\21 March 2026 General Report.pdf"
    sec_pdf = r"D:\PROJECTS\ha\english\New folder\New folder\21 March  2026 Security Report.pdf"

    out_file = r"d:\PROJECTS\pdf convert tool\dataset\master_knowledge.txt"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    print("1. Extracting Sinhala Original...")
    try:
        sin_text = "\n".join(extract_text_from_pdf(sin_pdf))
    except Exception as e:
        print(f"Error extracting Sinhala: {e}")
        return

    print("2. Extracting English General...")
    try:
        gen_text = "\n".join(extract_text_from_pdf(gen_pdf))
    except Exception as e:
        print(f"Error extracting General: {e}")
        return

    print("3. Extracting English Security...")
    try:
        sec_text = "\n".join(extract_text_from_pdf(sec_pdf))
    except Exception as e:
        print(f"Error extracting Security: {e}")
        return

    print("Saving to master_knowledge.txt...")

    knowledge_blob = f"""This is the MASTER KNOWLEDGE BASE for Sri Lanka Police Incident Translations.

INSTRUCTIONS FOR AI:
When translating a new Sinhala log, you MUST match the format, professional tone, terminology, and exact category numbers demonstrated in the reference below. Observe how the single Sinhala input is cleanly split into a 'General Report' and a 'Security Report'.

--- BEGIN REFERENCE SINHALA INPUT ---
{sin_text.strip()}
--- END REFERENCE SINHALA INPUT ---

--- BEGIN REFERENCE ENGLISH GENERAL REPORT OPTIMAL OUTPUT ---
{gen_text.strip()}
--- END REFERENCE ENGLISH GENERAL REPORT OPTIMAL OUTPUT ---

--- BEGIN REFERENCE ENGLISH SECURITY REPORT OPTIMAL OUTPUT ---
{sec_text.strip()}
--- END REFERENCE ENGLISH SECURITY REPORT OPTIMAL OUTPUT ---

End of Knowledge Base.
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(knowledge_blob)

    print(f"[Done] Master Knowledge created successfully at: {out_file}")

if __name__ == "__main__":
    main()
