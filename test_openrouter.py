import requests

api_key = "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"

# Test 1: Check if we can list models
print("Testing OpenRouter API key...")
print("-" * 50)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ API key is VALID")
        data = response.json()
        print(f"✓ Found {len(data.get('data', []))} available models")
    elif response.status_code == 401:
        print("✗ API key is INVALID (Unauthorized)")
        print(f"Response: {response.text}")
    elif response.status_code == 403:
        print("✗ API key is valid but lacks permissions (Forbidden)")
        print(f"Response: {response.text}")
    else:
        print(f"✗ Unexpected response: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"✗ Error occurred: {str(e)}")
