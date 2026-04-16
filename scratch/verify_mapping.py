import sys

# Add path to find modules
sys.path.append(r"d:\PROJECTS\pdf convert tool")

# Set encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

from machine_translator import MachineTranslator
from station_mapping import get_institutional_prompt_snippet


def test_mapping_injection():
    print("--- [Test 1] Mapping Injection Content ---")
    snippet = get_institutional_prompt_snippet()

    # Check for some key stations
    test_keys = ["මීගමුව", "කොළඹ", "ගාල්ල", "බුළත්සිංහල"]
    all_found = True
    for k in test_keys:
        if k in snippet:
            print(f"[OK] Found '{k}' in prompt snippet.")
        else:
            print(f"[FAIL] Missing '{k}' in prompt snippet.")
            all_found = False

    if all_found:
        print("PASS: Mapping injection looks complete.")
    else:
        print("FAIL: Some keys are missing from the snippet.")

def test_post_processing():
    print("\n--- [Test 2] Post-Processing Enforcement ---")
    tx = MachineTranslator()

    test_cases = [
        ("A robbery was reported in meegamuwa station.", "NEGOMBO"),
        ("The incident happened at galle police station.", "GALLE"),
        ("Suspect arrested in colombo fort.", "FORT"),
        ("Death reported in bulathsinhala.", "BULATHSINHALA")
    ]

    for input_text, expected_upper in test_cases:
        output = tx.post_process_translation_terminology(input_text)
        if expected_upper in output:
            print(f"[OK] Success: '{input_text}' -> '{output}' (Found {expected_upper})")
        else:
            print(f"[FAIL] Failure: '{input_text}' -> '{output}' (Missing {expected_upper})")

if __name__ == "__main__":
    test_mapping_injection()
    test_post_processing()
