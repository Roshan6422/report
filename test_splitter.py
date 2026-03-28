import sinhala_section_splitter
import os

def test_file(filename, report_type="General"):
    path = os.path.join(r"d:\PROJECTS\pdf convert tool\uploads", filename)
    if not os.path.exists(path):
        print(f"File {filename} not found!")
        return
        
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    
    print(f"\n--- TESTING: {filename} ({report_type}) ---")
    sections = sinhala_section_splitter.split_by_sections(text, report_type)
    
    found_count = 0
    for title, content in sections:
        if content != "Nil":
            found_count += 1
            print(f"✅ FOUND: {title} ({len(content)} chars)")
            # print(f"   Sample: {content[:100]}...")
        else:
            # print(f"❌ MISSING: {title}")
            pass
    print(f"SUMMARY: Captured {found_count} sections.")

if __name__ == "__main__":
    test_file("general_sinhala_1.txt", "General")
    test_file("report_mar18_raw.txt", "General")
    test_file("security_sinhala.txt", "Security")
