import pdfplumber
from fpdf import FPDF
import os
import glob
import sys

# Force UTF-8 for console output to avoid Sinhala filename errors
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def convert_pdf_font(input_pdf_path, output_pdf_path, font_path):
    # Quiet mode to avoid console unicode errors with sinhala filenames
    pass
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Unicode font support
    pdf.add_font('NotoSans', '', font_path)
    pdf.set_font('NotoSans', size=11)

    try:
        with pdfplumber.open(input_pdf_path) as input_pdf:
            has_content = False
            for page in input_pdf.pages:
                text = page.extract_text()
                if text:
                    has_content = True
                    pdf.add_page()
                    pdf.multi_cell(0, 8, text)
            
            if has_content:
                pdf.output(output_pdf_path)
                print(f"Success: Saved to {output_pdf_path}")
            else:
                print(f"Warning: No text found in {input_pdf_path} (It might be a scan/image).")
        
    except Exception as e:
        print(f"Error processing {input_pdf_path}: {e}")

if __name__ == "__main__":
    # Settings
    FONT_FILE = os.path.abspath("NotoSansSinhala-Regular.ttf")
    INPUT_FOLDER = r"D:\PROJECTS\ha\english\New folder"
    OUTPUT_FOLDER = os.path.join(INPUT_FOLDER, "Converted_Fonts")

    if not os.path.exists(FONT_FILE):
        print(f"Font not found at: {FONT_FILE}")
    elif not os.path.exists(INPUT_FOLDER):
        print(f"Input folder not found: {INPUT_FOLDER}")
    else:
        # Create output folder if it doesn't exist
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
            print(f"Created output folder: {OUTPUT_FOLDER}")

        # Find all PDF files in the folder
        pdf_files = glob.glob(os.path.join(INPUT_FOLDER, "*.pdf"))
        
        if not pdf_files:
            print("No PDF files found in the folder.")
        else:
            print(f"Found {len(pdf_files)} PDF files. Starting batch conversion...")
            for input_path in pdf_files:
                filename = os.path.basename(input_path)
                # Use a safe display name for console
                safe_name = filename.encode('ascii', 'ignore').decode('ascii') or "Sinhala_Filename"
                output_path = os.path.join(OUTPUT_FOLDER, "fixed_" + filename)
                convert_pdf_font(input_path, output_path, FONT_FILE)
            
            print("\n==========================================")
            print(f"Batch Processing Complete!")
            print(f"Check the folder: {OUTPUT_FOLDER}")
            print("==========================================")
