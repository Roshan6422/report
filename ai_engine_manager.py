import os
import requests
import json
import time
from datetime import datetime

# Load environment variables (Basic loader for environments without python-dotenv)
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

load_env()

class AIEngineManager:
    """Unified engine manager for OpenRouter (Cloud) and Ollama (Local)."""
    
    def __init__(self, mode="auto"):
        self.mode = os.getenv("DEFAULT_ENGINE", mode)
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
        self.ollama_model = "gpt-oss:120b-cloud" # Standard institutional model
        
        self.last_engine_used = None
        self.fallback_active = False
        self.stats = {"openrouter_calls": 0, "ollama_calls": 0, "failures": 0}

    def call_ai(self, prompt, system_prompt="You are a professional police report structuring assistant.", timeout=120):
        """Dispatches call based on mode with automatic fallback."""
        
        if self.mode == "openrouter":
            return self._call_openrouter(prompt, system_prompt, timeout)
        elif self.mode == "ollama":
            return self._call_ollama(prompt, timeout)
        else: # Auto mode
            if self.openrouter_key:
                print(f"  [AI Engine] Attempting OpenRouter ({self.openrouter_model})...")
                result = self._call_openrouter(prompt, system_prompt, timeout)
                if result and not result.startswith("❌"):
                    self.last_engine_used = "OpenRouter"
                    return result
                print(f"  [AI Engine] OpenRouter Failed/Unavailable. Falling back to Ollama...")
            
            self.fallback_active = True
            self.last_engine_used = "Ollama"
            return self._call_ollama(prompt, timeout)

    def _call_openrouter(self, prompt, system_prompt, timeout):
        try:
            self.stats["openrouter_calls"] += 1
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mirihana.police.lk", # Mandatory for some OpenRouter models
                "X-Title": "Police Report Engine"
            }
            payload = {
                "model": self.openrouter_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=timeout)
            if res.status_code == 200:
                data = res.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
            self.stats["failures"] += 1
            return f"❌ OpenRouter Error: {res.status_code} - {res.text}"
        except Exception as e:
            self.stats["failures"] += 1
            return f"❌ OpenRouter Exception: {str(e)}"

    def _call_ollama(self, prompt, timeout):
        try:
            self.stats["ollama_calls"] += 1
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
            res = requests.post(self.ollama_url, json=payload, timeout=240) # Local models need more time
            if res.status_code == 200:
                return res.json().get("response", "")
            return f"❌ Ollama Error: {res.status_code}"
        except Exception as e:
            return f"❌ Ollama Connection Failed: {str(e)}"

# Singleton Instance
_manager = None
def get_engine(mode="auto"):
    global _manager
    if _manager is None:
        _manager = AIEngineManager(mode=mode)
    return _manager

if __name__ == "__main__":
    print("---[ AI Engine Manager Test ]---")
    mgr = get_engine(mode="auto")
    test_res = mgr.call_ai("Hello, test engine connection. Respond with 'ACK'.")
    print(f"Engine Used: {mgr.last_engine_used}")
    print(f"Response: {test_res}")
