import os

import requests


def check_health():
    print("=== POLICE AI - OCR HEALTH CHECK ===\n")

    # 1. Check Kaggle / Ngrok
    kaggle_url = os.getenv("KAGGLE_OCR_URL", "https://nestable-mireya-uncarbonized.ngrok-free.dev/gpu-ocr")
    print(f"1. Testing Kaggle Surya API: {kaggle_url}")
    try:
        # Just a heartbeat check
        res = requests.get(kaggle_url.split('/gpu-ocr')[0], timeout=5)
        print(f"   [OK] Kaggle tunnel is reachable (Status: {res.status_code})")
    except Exception as e:
        print("   [ERROR] Kaggle tunnel unreachable. Please start your Kaggle Notebook.")
        print(f"           Error type: {type(e).__name__}")

    # 2. Check Tesseract
    print("\n2. Testing Local Tesseract OCR:")
    from local_ocr_tool import _get_pytesseract
    pytesseract = _get_pytesseract()
    cmd = pytesseract.pytesseract.tesseract_cmd
    print(f"   Configured Path: {cmd}")

    if os.path.exists(cmd) or cmd == "tesseract":
        try:
            ver = pytesseract.get_tesseract_version()
            print(f"   [OK] Tesseract found! Version: {ver}")
        except Exception as e:
            print(f"   [ERROR] Tesseract found but not working: {e}")
    else:
        print("   [ERROR] Tesseract not found at this path.")
        print("           ACTION: Install Tesseract for Windows and add to PATH.")

    # 3. Check Folders
    print("\n3. Checking Data Folders:")
    folders = [
        r"D:\PROJECTS\ha\english\New folder",
        r"D:\PROJECTS\ha\english\New folder\New folder"
    ]
    for f in folders:
        if os.path.exists(f):
            count = len([x for x in os.listdir(f) if x.lower().endswith('.pdf')])
            print(f"   [OK] Folder exists: {f} ({count} PDFs found)")
        else:
            print(f"   [ERROR] Folder MISSING: {f}")

    print("\n" + "="*40)
    print("FINAL ADVICE:")
    print("If both Kaggle and Tesseract are [ERROR], the script cannot read your PDFs.")
    print("Please start Kaggle or install Tesseract to continue.")
    print("="*40)

if __name__ == "__main__":
    check_health()
