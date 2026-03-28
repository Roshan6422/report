from pypdf import PdfReader
import sys

def test_pdf(path):
    try:
        reader = PdfReader(path)
        print(f"Pages: {len(reader.pages)}")
        first_page = reader.pages[0].extract_text()
        print("First 200 chars:")
        print(first_page[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pdf(sys.argv[1])
