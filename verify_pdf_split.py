import sinhala_section_splitter
import os

path = r"d:\PROJECTS\pdf convert tool\uploads\sinhala_extract_mar19.txt"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

res = sinhala_section_splitter.split_by_sections(text, "General")
print("\n--- RESULTS FOR SINHALA PDF EXTRACT ---")
found = 0
for t, c in res:
    if c != "Nil":
        found += 1
        print(f"✅ {t}: {len(c)} chars")
        # print(f"   {c[:50]}...")
print(f"\nTOTAL SECTIONS FOUND: {found}")
