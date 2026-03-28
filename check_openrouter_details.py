#!/usr/bin/env python3
"""Check OpenRouter API key details and available models."""

import requests
import json

API_KEY = "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"

print("=" * 80)
print("OpenRouter API Key Analysis")
print("=" * 80)

# 1. Check account/key info
print("\n[1] Checking API Key Information...")
try:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Get key limits/info
    response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers, timeout=10)
    if response.status_code == 200:
        key_info = response.json()
        print("✅ API Key Details:")
        print(json.dumps(key_info, indent=2))
    else:
        print(f"⚠️  Could not fetch key details: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 2. List all available models
print("\n[2] Fetching Available Models...")
try:
    response = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
    if response.status_code == 200:
        models_data = response.json()
        models = models_data.get("data", [])
        
        print(f"✅ Total Models Available: {len(models)}")
        
        # Filter free models
        free_models = [m for m in models if m.get("pricing", {}).get("prompt", "0") == "0"]
        print(f"   Free Models: {len(free_models)}")
        
        # Show some popular free models
        print("\n   Popular FREE Models:")
        free_model_names = [
            "meta-llama/llama-3.2-3b-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
            "google/gemini-flash-1.5:free",
            "mistralai/mistral-7b-instruct:free",
            "nousresearch/hermes-3-llama-3.1-405b:free"
        ]
        
        for model_name in free_model_names:
            model = next((m for m in models if m.get("id") == model_name), None)
            if model:
                print(f"   ✅ {model_name}")
                print(f"      Context: {model.get('context_length', 'N/A')} tokens")
            else:
                print(f"   ❌ {model_name} (Not available)")
        
        # Show some popular paid models (low cost)
        print("\n   Popular LOW-COST Models:")
        paid_model_names = [
            "deepseek/deepseek-chat",
            "google/gemini-flash-1.5",
            "anthropic/claude-3-haiku",
            "openai/gpt-3.5-turbo"
        ]
        
        for model_name in paid_model_names:
            model = next((m for m in models if m.get("id") == model_name), None)
            if model:
                pricing = model.get("pricing", {})
                prompt_price = float(pricing.get("prompt", 0)) * 1_000_000  # per 1M tokens
                completion_price = float(pricing.get("completion", 0)) * 1_000_000
                print(f"   ✅ {model_name}")
                print(f"      Cost: ${prompt_price:.2f} / ${completion_price:.2f} per 1M tokens")
            else:
                print(f"   ❌ {model_name} (Not available)")
                
    else:
        print(f"❌ Could not fetch models: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 3. Test a simple request with a working model
print("\n[3] Testing a Working Model...")
try:
    test_model = "deepseek/deepseek-chat"  # Known working model
    
    payload = {
        "model": test_model,
        "messages": [
            {"role": "user", "content": "Say 'Hello' in one word."}
        ],
        "max_tokens": 10
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
        print(f"✅ Test successful with {test_model}")
        print(f"   Response: {content}")
        
        # Show usage/cost
        usage = data.get("usage", {})
        print(f"   Tokens used: {usage.get('total_tokens', 'N/A')}")
    else:
        print(f"❌ Test failed: {response.status_code}")
        print(f"   {response.text[:300]}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("Analysis Complete")
print("=" * 80)
