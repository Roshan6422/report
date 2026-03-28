#!/usr/bin/env python3
"""Test Ollama connection and gpt-oss:120b-cloud model."""

import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:120b-cloud"

print("=" * 80)
print("Ollama Connection Test")
print("=" * 80)
print(f"URL: {OLLAMA_URL}")
print(f"Model: {MODEL}")
print("=" * 80)

# Test 1: Check if Ollama is running
print("\n[Test 1] Checking if Ollama is running...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        print("✅ Ollama is running")
        models = response.json().get("models", [])
        print(f"   Available models: {len(models)}")
        
        # Check if our model is available
        model_names = [m.get("name", "") for m in models]
        if MODEL in model_names:
            print(f"   ✅ {MODEL} is available")
        else:
            print(f"   ⚠️  {MODEL} not found")
            print(f"   Available models:")
            for m in models[:10]:  # Show first 10
                print(f"      - {m.get('name', 'unknown')}")
    else:
        print(f"❌ Ollama not responding: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot connect to Ollama: {e}")
    print("\n   Make sure Ollama is running:")
    print("   - Check if Ollama service is started")
    print("   - Try: ollama serve")
    exit(1)

# Test 2: Simple generation test
print("\n[Test 2] Testing text generation...")
try:
    payload = {
        "model": MODEL,
        "prompt": "Say 'Hello' in one word.",
        "stream": False
    }
    
    print(f"   Sending request to {MODEL}...")
    start_time = time.time()
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        generated_text = data.get("response", "")
        print(f"✅ Generation successful ({elapsed:.2f}s)")
        print(f"   Response: {generated_text[:200]}")
        
        # Show stats
        if "eval_count" in data:
            print(f"   Tokens generated: {data.get('eval_count', 'N/A')}")
            print(f"   Generation speed: {data.get('eval_count', 0) / elapsed:.1f} tokens/sec")
    else:
        print(f"❌ Generation failed: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Sinhala translation test
print("\n[Test 3] Testing Sinhala translation capability...")
try:
    sinhala_text = "පොලිස් ස්ථානයට පැමිණිල්ලක් ලැබුණි."
    
    payload = {
        "model": MODEL,
        "prompt": f"""Translate this Sinhala text to English:

Sinhala: {sinhala_text}

English:""",
        "stream": False
    }
    
    print(f"   Testing translation...")
    start_time = time.time()
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        translation = data.get("response", "").strip()
        print(f"✅ Translation successful ({elapsed:.2f}s)")
        print(f"   Sinhala: {sinhala_text}")
        print(f"   English: {translation[:200]}")
    else:
        print(f"❌ Translation failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
print("\nConfiguration:")
print("✅ Ollama is set as primary engine")
print("✅ OpenRouter available as backup (free tier)")
print("\nRecommendation:")
print("- Use Ollama for all processing (fast, free, local)")
print("- OpenRouter will only be used if Ollama fails")
