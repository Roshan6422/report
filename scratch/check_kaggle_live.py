import json
import time

import requests

BASE = "https://nestable-mireya-uncarbonized.ngrok-free.dev"

print("=" * 55)
print(" KAGGLE POLICE AI — LIVE STATUS CHECK")
print("=" * 55)

# Test 1: Health endpoint
print("\n[1] Testing /health ...")
alive = False
try:
    r = requests.get(f"{BASE}/health", timeout=10)
    print(f"    HTTP {r.status_code}")
    print(f"    {json.dumps(r.json(), indent=4)}")
    alive = r.status_code == 200
except Exception as e:
    print(f"    FAILED: {e}")
    alive = False

if not alive:
    print("\n" + "=" * 55)
    print("  SERVER IS OFFLINE")
    print("  Kaggle session expired or notebook not running.")
    print("  Solution: Run Kaggle_Police_AI_v3.ipynb on Kaggle")
    print("=" * 55)
else:
    # Test 2: Quick AI generate test
    print("\n[2] Testing /api/generate ...")
    t0 = time.time()
    try:
        payload = {
            "model": "police-ai-master:latest",
            "prompt": 'Reply ONLY with this exact JSON: {"status":"ok"}',
            "stream": False
        }
        r2 = requests.post(f"{BASE}/api/generate", json=payload, timeout=30)
        elapsed = round(time.time() - t0, 2)
        data = r2.json()
        reply = data.get("response", "")[:200]
        print(f"    HTTP {r2.status_code} | {elapsed}s")
        print(f"    Response: {reply}")
    except Exception as e:
        print(f"    FAILED: {e}")

    # Test 3: Check /api/tags (list models)
    print("\n[3] Testing /api/tags (loaded models) ...")
    try:
        r3 = requests.get(f"{BASE}/api/tags", timeout=10)
        models = r3.json().get("models", [])
        for m in models:
            print(f"    - {m.get('name', m)}")
        if not models:
            print("    (no models loaded yet)")
    except Exception as e:
        print(f"    FAILED: {e}")

    print("\n" + "=" * 55)
    print("  KAGGLE AI IS ALIVE!")
    print(f"  URL: {BASE}")
    print("=" * 55)
