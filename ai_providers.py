import os
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------------------------
# Shared session with retry logic for all providers
# ---------------------------------------------------------------------------

_ai_session = requests.Session()
_ai_retry   = Retry(total=2, backoff_factor=1, status_forcelist=[502, 503, 504])
_ai_adapter = HTTPAdapter(max_retries=_ai_retry)
_ai_session.mount("https://", _ai_adapter)
_ai_session.mount("http://",  _ai_adapter)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class BaseProvider:
    def call(self, prompt: str, system_prompt: str, timeout: int,
             model_override: str | None = None) -> str:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# GitHub Models Provider  (OpenAI-compatible, Azure endpoint)
# ---------------------------------------------------------------------------

class GitHubProvider(BaseProvider):
    def __init__(self, api_url: str, model_name: str, api_keys: list):
        self.api_url    = api_url.rstrip("/")
        self.model_name = model_name
        self.api_keys   = api_keys   # list of (name, key) tuples
        self.key_index  = 0

    def get_next_key(self) -> str | None:
        if not self.api_keys:
            return None
        item = self.api_keys[self.key_index % len(self.api_keys)]
        self.key_index += 1
        # Support both plain strings and (name, key) tuples
        return item[1] if isinstance(item, (list, tuple)) else item

    def call(self, prompt: str, system_prompt: str, timeout: int,
             model_override: str | None = None) -> str:
        key = self.get_next_key()
        if not key:
            return "❌ GitHub Error: No API Key configured."

        model = model_override or self.model_name
        try:
            max_out = max(256, min(int(os.getenv("GITHUB_MAX_OUTPUT_TOKENS", "8192")), 16384))
        except ValueError:
            max_out = 8192

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "model":       model,
            "messages":    [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": prompt},
            ],
            "max_tokens":  max_out,
            "temperature": 0.3,
        }
        try:
            res = _ai_session.post(
                f"{self.api_url}/chat/completions",
                headers=headers, json=payload, timeout=timeout,
            )
            if res.status_code == 200:
                data = res.json()
                if data.get("choices"):
                    ch = data["choices"][0]
                    if ch.get("finish_reason") == "length":
                        print(f"  [GitHub] ⚠️ Output truncated for {model}. Raise GITHUB_MAX_OUTPUT_TOKENS.")
                    return ch["message"]["content"]
                return "❌ GitHub Error: Empty choices in response."
            if res.status_code == 401:
                return "❌ GitHub Error: 401 Unauthorized — check API key."
            if res.status_code == 429:
                return "❌ GitHub Error: 429 Rate Limit exceeded."
            return f"❌ GitHub Error: {res.status_code} — {res.text[:120]}"
        except requests.exceptions.Timeout:
            return f"❌ GitHub Timeout after {timeout}s"
        except Exception as e:
            return f"❌ GitHub Exception: {str(e)[:200]}"


# ---------------------------------------------------------------------------
# Gemini Provider  (Google Generative Language REST API)
# ---------------------------------------------------------------------------

# Ordered list of Gemini models to try (newest/fastest first)
_GEMINI_MODEL_PRIORITY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",          # legacy fallback
]

class GeminiProvider(BaseProvider):
    def __init__(self, api_keys: list):
        self.api_keys  = api_keys
        self.key_index = 0

    def _get_next_key(self) -> str | None:
        if not self.api_keys:
            return None
        key = self.api_keys[self.key_index % len(self.api_keys)]
        self.key_index += 1
        return key

    def call(self, prompt: str, system_prompt: str, timeout: int,
             model_override: str | None = None) -> str:
        if not self.api_keys:
            return "❌ Gemini Error: No API key configured."

        key = self._get_next_key()

        models_to_try = [model_override] if model_override else _GEMINI_MODEL_PRIORITY

        for model in models_to_try:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={key}"
            )
            # Gemini v1beta supports systemInstruction for better separation
            payload = {
                "systemInstruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 8192,
                },
            }
            try:
                res = _ai_session.post(url, headers={"Content-Type": "application/json"},
                                       json=payload, timeout=timeout)
                if res.status_code == 200:
                    data = res.json()
                    try:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError):
                        return "❌ Gemini Error: Unexpected response structure."

                if res.status_code == 404:
                    # Model not available — try next in list
                    print(f"  [Gemini] Model '{model}' not found (404). Trying next…")
                    continue
                if res.status_code == 401:
                    return "❌ Gemini Error: 401 Unauthorized — check API key."
                if res.status_code == 429:
                    return "❌ Gemini Error: 429 Rate Limit — quota exceeded."
                return f"❌ Gemini Error: {res.status_code} — {res.text[:120]}"

            except requests.exceptions.Timeout:
                return f"❌ Gemini Timeout after {timeout}s"
            except Exception as e:
                return f"❌ Gemini Exception: {str(e)[:200]}"

        return "❌ Gemini Error: All model variants failed."


# ---------------------------------------------------------------------------
# Ollama Provider  (local or Kaggle ngrok tunnel)
# ---------------------------------------------------------------------------

class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str, model_name: str):
        self.base_url   = base_url
        self.model_name = model_name

    @property
    def _is_cloud(self) -> bool:
        return "ngrok" in self.base_url or "kaggle" in self.base_url

    def call(self, prompt: str, system_prompt: str, timeout: int,
             model_override: str | None = None) -> str:
        model            = model_override or self.model_name
        effective_timeout = max(timeout, 300) if self._is_cloud else timeout
        max_attempts      = 2 if self._is_cloud else 1

        payload = {
            "model":   model,
            "prompt":  prompt,
            "system":  system_prompt,
            "stream":  False,
            "options": {
                "temperature": 0.4,
                "repeat_penalty": 1.5,
                "repeat_last_n": 64
            },
        }
        headers = {
            "ngrok-skip-browser-warning": "true",
            "Content-Type": "application/json",
        }

        last_err = None
        for attempt in range(max_attempts):
            try:
                res = _ai_session.post(
                    self.base_url, json=payload, headers=headers, timeout=effective_timeout,
                )
                if res.status_code == 200:
                    return res.json().get("response", "")
                if res.status_code == 401:
                    return "❌ Ollama Error: 401 Unauthorized."
                if res.status_code == 500:
                    return "❌ Ollama Error: 500 Internal Server Error (server overloaded / bad model)."
                return f"❌ Ollama Error: {res.status_code} — {res.text[:100]}"

            except requests.exceptions.Timeout:
                last_err = f"Timeout after {effective_timeout}s"
                if attempt < max_attempts - 1:
                    print(f"  [Ollama] Timeout on attempt {attempt + 1}. Retrying…")
                    time.sleep(2)
                    continue
                return f"❌ Ollama Timeout: {last_err}"
            except requests.exceptions.ConnectionError as e:
                last_err = str(e)[:150]
                if attempt < max_attempts - 1:
                    time.sleep(2)
                    continue
                return f"❌ Ollama Connection Error: {last_err}"
            except Exception as e:
                last_err = str(e)[:200]
                return f"❌ Ollama Exception: {last_err}"

        return f"❌ Ollama: Max retries exceeded. Last error: {last_err}"
