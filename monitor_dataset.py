import os
import sys
import time

# Force utf-8 stdout to avoid cp1252 errors on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def get_line_count(filepath):
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def get_last_line(filepath):
    if not os.path.exists(filepath):
        return ""
    try:
        with open(filepath, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode('utf-8')
            return last_line
    except Exception:
        return "No data yet..."

def main():
    # Detect if we are in migration or full production
    v2_path = r"dataset\police_training_data_v2.jsonl"
    v1_path = r"dataset\police_training_data.jsonl"

    dataset_path = v2_path if os.path.exists(v2_path) else v1_path

    print("="*60)
    print("🚀 SRI LANKA POLICE AI - DATASET HARVESTING MONITOR")
    print("="*60)
    print(f"Monitoring: {dataset_path}")
    print("Press Ctrl+C to stop.\n")

    last_count = -1

    while True:
        try:
            count = get_line_count(dataset_path)
            if count != last_count:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("="*60)
                print("🚀 SRI LANKA POLICE AI - DATASET HARVESTING MONITOR")
                print("="*60)
                print(f"📊 Total Records Collected: {count}")
                print(f"⏱️  Last Update: {time.strftime('%H:%M:%S')}")
                print("-" * 60)

                # Show progress bar (approximate based on 20 PDFs)
                # Let's assume each PDF might have ~30 incidents on average
                estimated_total = 20 * 15
                progress = min(100, int((count / estimated_total) * 100))
                bar = "█" * (progress // 2) + "-" * (50 - progress // 2)
                print(f"Progress: [{bar}] {progress}% (Estimated)")
                print("-" * 60)

                # Show last sample summary (briefly)
                last_sample = get_last_line(dataset_path)
                if last_sample:
                    print("🔍 LATEST HARVESTED SAMPLE:")
                    # Try to show a snippet from the sample
                    try:
                        import json
                        data = json.loads(last_sample)
                        # The harvester uses ChatML format
                        # System -> User (Sinhala) -> Assistant (English JSON)
                        messages = data.get("messages", [])
                        if len(messages) >= 3:
                            sinhala = messages[1].get("content", "")[:100]
                            print(f"  Sinhala: {sinhala}...")

                            try:
                                english_json = json.loads(messages[2].get("content", "{}"))
                                print(f"  Province: {english_json.get('province', 'N/A')}")
                                print(f"  District: {english_json.get('district', 'N/A')}")
                                print(f"  Category: {english_json.get('category_num', '??')} - {english_json.get('category_name', 'N/A')}")
                                print(f"  Description: {english_json.get('description', '')[:100]}...")
                            except Exception:
                                print(f"  English: {messages[2].get('content', '')[:100]}...")
                    except Exception:
                        print(f"  Raw: {last_sample[:100]}...")

                last_count = count

            time.sleep(5) # Update every 5 seconds
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
