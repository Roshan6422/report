
import os
import re
from datetime import datetime


def parse_sinhala_date(filename):
    # Format: 2026.03.14 ??? ???????? ???????.pdf
    match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None

def parse_english_date(filename):
    # Format: 14 March 2026 General.pdf
    # Format: 14 March 2026 Security.pdf
    match = re.search(r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', filename, re.IGNORECASE)
    if match:
        day = match.group(1).zfill(2)
        month_str = match.group(2)
        year = match.group(3)
        try:
            dt = datetime.strptime(f"{day} {month_str} {year}", "%d %B %Y")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None
    return None

def main():
    sin_dir = r"D:\PROJECTS\ha\english\New folder"
    eng_dir = r"D:\PROJECTS\ha\english\New folder\New folder"

    sin_files = [f for f in os.listdir(sin_dir) if f.lower().endswith(".pdf")]
    eng_files = [f for f in os.listdir(eng_dir) if f.lower().endswith(".pdf")]

    with open(os.path.join("scratch", "mapping_results.txt"), "w", encoding="utf-8") as out_f:
        out_f.write(f"Found {len(sin_files)} Sinhala files and {len(eng_files)} English files.\n\n")

        mapping = {}

        for sf in sin_files:
            date = parse_sinhala_date(sf)
            if date:
                if date not in mapping: mapping[date] = {"sin": [], "eng": []}
                mapping[date]["sin"].append(sf)

        for ef in eng_files:
            date = parse_english_date(ef)
            if date:
                if date not in mapping: mapping[date] = {"sin": [], "eng": []}
                mapping[date]["eng"].append(ef)

        out_f.write("Alignment Mapping:\n")
        for date, data in sorted(mapping.items()):
            sin = ", ".join(data["sin"]) if data["sin"] else "MISSING"
            eng = ", ".join(data["eng"]) if data["eng"] else "MISSING"
            out_f.write(f"[{date}]\n")
            out_f.write(f"  SIN: {sin}\n")
            out_f.write(f"  ENG: {eng}\n")
            out_f.write("-" * 40 + "\n")

    print("Mapping complete. See scratch/mapping_results.txt")

if __name__ == "__main__":
    main()
