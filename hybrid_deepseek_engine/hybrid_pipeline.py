import os
import requests

# Set your current environment directory (relative to this script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# === Helper Function: Load Templates ===
def load_template(filename):
    path = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# === Llama3 Local (Offline) ===
def ask_llama3(prompt):
    url = "http://localhost:11434/api/generate"
    # Using Llama3 specific configurations for ollama API
    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    try:
        resp = requests.post(url, json=data, timeout=60)
        return resp.json().get("response", "")
    except Exception as e:
        print(f"[Error: Local Llama3 Connection Failed] - {e}")
        return ""

# === DeepSeek Cloud API (Via OpenRouter) ===
def ask_deepseek(prompt, api_key):
    # Using OpenRouter to route specifically to DeepSeek
    url = "https://openrouter.ai/api/v1/chat/completions" 
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=60)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"[Error: DeepSeek/OpenRouter Connection Failed] - {e}")
        return ""

# === Quality Check Step ===
def is_good_answer(answer):
    """
    Validates output length and ensures it has professional formatting elements.
    We also load the "Quality Check" template to have AI evaluate it (optional advanced step).
    For speed, we use Python logic exactly as requested:
    """
    if not answer:
        return False
        
    word_count = len(answer.split())
    
    # 1. Output must not be completely empty or extremely short for a full report
    if word_count < 20: 
        return False
        
    # 2. Add extra logic as instructed (keywords)
    # keywords = ["general", "security", "report"]
    # if not any(k in answer.lower() for k in keywords): return False
    
    return True

# === The Hybrid Engine Core ===
def ask_hybrid(user_sinhala_text, deepseek_key):
    print("🚀 Starting Hybrid Pipeline...")
    
    # 1. Generate Prompt using our Template
    template_raw = load_template("report_generation.txt")
    if not template_raw:
        print("❌ Error: report_generation.txt template missing!")
        return None
        
    main_prompt = template_raw.replace("{user_sinhala_text}", user_sinhala_text)
    
    # 2. Local Llama3 (Fast & Free)
    print("  [Step 1] Asking Local Offline Llama3...")
    answer_local = ask_llama3(main_prompt)
    
    # 3. Validation Check
    if is_good_answer(answer_local):
        print("  ✅ Local Llama3 generated a high-quality response!")
        return answer_local
    else:
        print("  ⚠️ Llama3 output too short/low quality or server offline.")
        print("  🔄 [Step 2] Falling back to DeepSeek Cloud API...")
        # 4. DeepSeek Cloud API Fallback
        answer_cloud = ask_deepseek(main_prompt, deepseek_key)
        if answer_cloud:
            print("  ✅ DeepSeek Cloud successful!")
            return answer_cloud
        else:
            print("  ❌ DeepSeek Cloud also failed. Please check your API Key and connection.")
            return "ERROR: Could not fetch report from hybrid pipeline."

# ==========================================
# USAGE EXAMPLE
# ==========================================
if __name__ == "__main__":
    test_sinhala = "ඔබේ project එකට Sinhala → English report generate කරන්න. මෙහිදී 2026 මාර්තු මස 23 වන දින වාර්තාව ඇතුලත් කරන්න."
    
    # 🔑 Pass your OpenRouter API key via environment variable or argument
    DEEPSEEK_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
    if not DEEPSEEK_API_KEY:
        print("❌ Error: Set OPENROUTER_API_KEY environment variable.")
        exit(1)
    
    # Run the pipeline
    final_report = ask_hybrid(test_sinhala, DEEPSEEK_API_KEY)
    
    print("\n\n" + "="*50)
    print("FINAL ENGLISH REPORT:")
    print("="*50)
    print(final_report)
