#!/usr/bin/env python3
"""Test OpenRouter connection and diagnose issues."""

import requests
import os
from datetime import datetime

def load_env():
    """Load .env file."""
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

load_env()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free")

print("=" * 70)
print("OpenRouter Connection Diagnostic")
print("=" * 70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Model: {MODEL}")
print(f"API Key: {API_KEY[:20]}..." if API_KEY else "API Key: NOT FOUND")
print("=" * 70)

# Test 1: Check API key validity
print("\n[Test 1] Checking API Key Validity...")
try:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
    if response.status_code == 200:
        print("✅ API Key is valid")
        models = response.json()
        print(f"   Available models: {len(models.get('data', []))} models found")
    else:
        print(f"❌ API Key validation failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Connection error: {e}")

# Test 2: Test specific model
print(f"\n[Test 2] Testing model: {MODEL}")
try:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mirihana.police.lk",
        "X-Title": "Police Report Engine"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "Reply with just 'OK' if you receive this."}
        ],
        "max_tokens": 50
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"✅ Model responded successfully")
        print(f"   Response: {content}")
    else:
        print(f"❌ Model request failed: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
        # Parse error details
        try:
            error_data = response.json()
            if "error" in error_data:
                print(f"   Error type: {error_data['error'].get('type', 'unknown')}")
                print(f"   Error message: {error_data['error'].get('message', 'unknown')}")
        except:
            pass
            
except Exception as e:
    print(f"❌ Request error: {e}")

# Test 3: Suggest alternatives
print("\n[Test 3] Checking alternative free models...")
alternative_models = [
    "deepseek/deepseek-chat",
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free"
]

print("   Recommended alternatives:")
for model in alternative_models:
    print(f"   - {model}")

print("\n" + "=" * 70)
print("Diagnostic Complete")
print("=" * 70)
print("\nRecommendations:")
print("1. If API key is invalid: Get a new key from https://openrouter.ai/keys")
print("2. If model is unavailable: Update OPENROUTER_MODEL in .env to an alternative")
print("3. If rate limited: Wait a few minutes or switch to Ollama (DEFAULT_ENGINE=ollama)")
print("4. If all fails: Use Ollama exclusively for local processing")
