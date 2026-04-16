import json
import os
import sys

# Force utf-8 stdout to avoid cp1252 errors on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

dataset_path = r"dataset\police_training_data.jsonl"

def main():
    if not os.path.exists(dataset_path):
        print("Dataset file not found yet.")
        return

    try:
        with open(dataset_path, encoding='utf-8') as f:
            lines = f.readlines()
            count = len(lines)
            last_line = lines[-1] if lines else None

            print("="*60)
            print("🚀 LIVE DATASET STATUS (Snapshot)")
            print("="*60)
            print(f"📊 Total Training Samples: {count}")
            print("-" * 60)

            if last_line:
                data = json.loads(last_line)
                messages = data.get("messages", [])
                if len(messages) >= 3:
                    sinhala = messages[1].get("content", "")
                    english = messages[2].get("content", "")
                    print("🔍 LATEST SAMPLE (Sinhala):")
                    print(f"  {sinhala[:200]}...")
                    print("-" * 60)
                    print("🎯 LATEST SAMPLE (English):")
                    print(f"  {english[:200]}...")
            print("="*60)
    except Exception as e:
        print(f"Error reading dataset: {e}")

if __name__ == "__main__":
    main()
