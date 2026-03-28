import fitz
import os

path = r"d:\PROJECTS\pdf convert tool\uploads\mar26_output\General_Report_Mar26.pdf"
doc = fitz.open(path)
text = ""
for page in doc:
    text += page.get_text()

print("--- TEXT PREVIEW (Last 3000 chars) ---")
print(text[-3000:])

print("\n--- KEYWORD CHECK ---")
for kw in ["REPORTED", "SOLVED", "UNSOLVED", "SUMMARY MATRIX", "SUMMARY", "THEFT", "HOMICIDE"]:
    if kw in text.upper():
        print(f"  ✅ '{kw}' found")
    else:
        print(f"  ❌ '{kw}' NOT found")

doc.close()
