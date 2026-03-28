import PyPDF2
import os

pdf_path = r"D:\PROJECTS\ha\2026.03.21 දින සිදුවීම් වාර්තාව.pdf"
output_path = r"D:\PROJECTS\pdf convert tool\mar21_text_full.txt"

print(f"Starting robust extraction of {pdf_path}...")

try:
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        full_text = []
        for i, page in enumerate(reader.pages):
            try:
                print(f"  Extracting page {i+1}/{len(reader.pages)}...")
                text = page.extract_text()
                if text:
                    full_text.append(text)
            except Exception as e:
                print(f"  [Error] Skipping page {i+1}: {e}")
        
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write("\n\n--- PAGE BREAK ---\n\n".join(full_text))
            
    print(f"✅ Success! Full text saved to {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
except Exception as e:
    print(f"❌ Critical Error: {e}")
