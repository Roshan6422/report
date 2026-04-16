import sys
import os

# Add path to find modules
sys.path.append(r"d:\PROJECTS\pdf convert tool")

from build_training_dataset import build_pairs

def test_pairing():
    print("--- [Dry Run] Testing PDF Pairing Logic ---")
    try:
        pairs = build_pairs()
        print(f"Total entries found: {len(pairs)}")
        
        paired = [p for p in pairs if p['status'] == 'PAIRED']
        missing_eng = [p for p in pairs if p['status'] == 'MISSING_ENG']
        missing_sin = [p for p in pairs if p['status'] == 'MISSING_SIN']
        
        print(f"✅ Fully Paired: {len(paired)}")
        for p in paired[:5]:
            print(f"  - {p['date']} [{p['type']}]: {os.path.basename(p['sinhala'])} <-> {os.path.basename(p['english'])}")
            
        print(f"\n⚠️ Missing English: {len(missing_eng)}")
        for p in missing_eng[:3]:
             print(f"  - {p['date']} [{p['type']}]: {os.path.basename(p['sinhala'])}")

        print(f"\n⚠️ Missing Sinhala: {len(missing_sin)}")
        for p in missing_sin[:3]:
             print(f"  - {p['date']} [{p['type']}]: {os.path.basename(p['english'])}")

    except Exception as e:
        print(f"Error during pairing: {e}")

if __name__ == "__main__":
    test_pairing()
