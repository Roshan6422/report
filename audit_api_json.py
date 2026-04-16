import os
import json
import requests
import concurrent.futures
from google import genai
from quota_manager import get_quota_mgr

def test_gemini(name, key):
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite", 
            contents=["hi"], 
            config={"max_output_tokens": 5}
        )
        return name, "Active"
    except Exception as e:
        s = str(e).lower()
        if "429" in s: return name, "Rate Limited"
        if "401" in s or "invalid" in s: return name, "Invalid"
        return name, f"Error: {str(e)[:40]}"

def test_github(name, key):
    try:
        url = "https://models.inference.ai.azure.com/chat/completions"
        headers = {"Authorization": f"Bearer {key}"}
        payload = {"messages": [{"role": "user", "content": "hi"}], "model": "gpt-4o-mini", "max_tokens": 5}
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        if r.status_code == 200: return name, "Active"
        if r.status_code == 429: return name, "Rate Limited"
        return name, f"Error {r.status_code}"
    except: return name, "Error"

def run_audit():
    gemini_keys = {}
    github_keys = {}
    with open("gemini_keys.json", "r") as f:
        gk = json.load(f)
        gemini_keys = {k: v for k, v in gk.items() if k.startswith("Gemini") and v.strip()}
    with open("github_keys.json", "r") as f:
        github_keys = json.load(f)

    results = {"Gemini": {}, "GitHub": {}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        g_futs = {executor.submit(test_gemini, k, v): k for k, v in gemini_keys.items()}
        gh_futs = {executor.submit(test_github, k, v): k for k, v in github_keys.items()}
        for f in concurrent.futures.as_completed(list(g_futs.keys()) + list(gh_futs.keys())):
            name, status = f.result()
            if name in gemini_keys: results["Gemini"][name] = status
            else: results["GitHub"][name] = status

    with open("audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("DONE_AUDIT")

if __name__ == "__main__":
    run_audit()
