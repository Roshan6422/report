import os
import json
import requests
import concurrent.futures
from google import genai
from quota_manager import get_quota_mgr
from api_keys import get_gemini_keys, get_github_keys

def test_gemini(name, key):
    try:
        client = genai.Client(api_key=key)
        # Minimal test: generate a single word
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite", 
            contents=["Status check. Respond with 'OK'."],
            config={"max_output_tokens": 5}
        )
        if response.text:
            return name, "✅ Active"
        return name, "⚠️ Empty Response"
    except Exception as e:
        s = str(e).lower()
        if "429" in s or "limit" in s:
            return name, "🔴 Rate Limited (Exhausted)"
        if "400" in s or "401" in s or "invalid" in s:
            return name, "❌ Invalid/Expired Key"
        return name, f"⚠️ Error: {str(e)[:50]}"

def test_github(name, key):
    try:
        url = "https://models.inference.ai.azure.com/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "messages": [{"role": "user", "content": "hi"}], 
            "model": "gpt-4o-mini", 
            "max_tokens": 5
        }
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # Update server quota
        rem = r.headers.get("x-ratelimit-remaining-requests")
        if rem:
            get_quota_mgr().update_from_headers(name, int(rem))
            
        if r.status_code == 200:
            return name, f"✅ Active ({rem if rem else 'Unknown'} remaining)"
        if r.status_code == 429:
            return name, "🔴 Rate Limited (Exhausted)"
        return name, f"❌ Failed ({r.status_code})"
    except Exception as e:
        return name, f"⚠️ Error: {str(e)[:50]}"

def run_audit():
    print("\n" + "="*50)
    print("      🚀 POLICE AI PIPELINE - API HEALTH AUDIT")
    print("="*50)
    
    # Load keys via central helper
    gemini_list = get_gemini_keys()
    gemini_keys = {f"Gemini_{i+1}": v for i, v in enumerate(gemini_list)}

    github_items = get_github_keys()
    github_keys = {k: v for k, v in github_items}

    print(f"\n🔍 Testing {len(gemini_keys)} Gemini keys and {len(github_keys)} GitHub keys...\n")

    results = {"Gemini": {}, "GitHub": {}}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        g_futs = [executor.submit(test_gemini, k, v) for k, v in gemini_keys.items()]
        gh_futs = [executor.submit(test_github, k, v) for k, v in github_keys.items()]
        
        for f in concurrent.futures.as_completed(g_futs + gh_futs):
            name, status = f.result()
            if name.startswith("Gemini"):
                results["Gemini"][name] = status
            else:
                results["GitHub"][name] = status

    # Print Results Table
    print(f"{'KEY NAME':<20} | {'STATUS':<30}")
    print("-" * 55)
    
    print("\n--- [ GEMINI MODELS ] ---")
    for name in sorted(results["Gemini"].keys()):
        print(f"{name:<20} | {results['Gemini'][name]}")

    print("\n--- [ GITHUB MODELS ] ---")
    for name in sorted(results["GitHub"].keys()):
        print(f"{name:<20} | {results['GitHub'][name]}")

    print("\n" + "="*50)
    print("Audit Complete.")

if __name__ == "__main__":
    run_audit()
