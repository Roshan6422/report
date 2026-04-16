import os
import json

# Centralized API key loader for the project
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if not key or not key.replace("_", "").isalnum():
                    continue
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                else:
                    comment_pos = value.find(" #")
                    if comment_pos > 0:
                        value = value[:comment_pos].strip()
                os.environ.setdefault(key, value)


def _load_json_keys(filename):
    try:
        path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def get_gemini_keys():
    data = _load_json_keys("gemini_keys.json")
    keys = [v for k, v in data.items() if k.startswith("Gemini") and isinstance(v, str) and v.strip()]
    if not keys:
        env_key = os.getenv("GEMINI_API_KEY")
        if env_key:
            keys = [env_key]
    return keys


def get_github_keys():
    data = _load_json_keys("github_keys.json")
    items = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str) and v.strip():
                items.append((k, v))
    if not items:
        env_key = os.getenv("GITHUB_API_KEY")
        if env_key:
            items = [("GitHub_Env", env_key)]
    return items


def get_openrouter_key():
    # OpenRouter typically stored in env
    return os.getenv("OPENROUTER_API_KEY")


def get_aimlapi_keys():
    """
    AI/ML API (https://aimlapi.com) — OpenAI-compatible base URL.
    Keys: AIMLAPI_API_KEY env and/or aimlapi_keys.json entries AIMLAPI_*.
    """
    keys = []
    data = _load_json_keys("aimlapi_keys.json")
    if isinstance(data, dict):
        for k, v in sorted(data.items()):
            if not k.upper().startswith("AIMLAPI"):
                continue
            if isinstance(v, str) and v.strip():
                keys.append(v.strip())
    env_key = (os.getenv("AIMLAPI_API_KEY") or "").strip()
    if env_key and env_key not in keys:
        keys.insert(0, env_key)
    return keys


def get_aimlapi_key():
    ks = get_aimlapi_keys()
    return ks[0] if ks else None


def get_groq_keys():
    """
    Groq Cloud API — OpenAI-compatible chat at api.groq.com.
    Keys: GROQ_API_KEY env and/or groq_keys.json entries GROQ_*.
    """
    keys = []
    data = _load_json_keys("groq_keys.json")
    if isinstance(data, dict):
        for k, v in sorted(data.items()):
            if not k.upper().startswith("GROQ"):
                continue
            if isinstance(v, str) and v.strip():
                keys.append(v.strip())
    env_key = (os.getenv("GROQ_API_KEY") or "").strip()
    if env_key and env_key not in keys:
        keys.insert(0, env_key)
    return keys


def get_groq_key():
    ks = get_groq_keys()
    return ks[0] if ks else None


def get_key(provider):
    p = (provider or "").lower()
    if p == "gemini":
        ks = get_gemini_keys()
        return ks[0] if ks else None
    if p == "github":
        ks = get_github_keys()
        return ks[0][1] if ks else None
    if p == "openrouter":
        return get_openrouter_key()
    if p in ("aimlapi", "aiml_api"):
        return get_aimlapi_key()
    if p == "groq":
        return get_groq_key()
    # fallback to env var lookup
    return os.getenv(provider.upper())


def _project_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def mask_api_key(key: str | None) -> str:
    if not key or not str(key).strip():
        return "—"
    s = str(key).strip()
    if len(s) <= 8:
        return "••••••••"
    return "••••" + s[-4:]


def get_gemini_key_display() -> tuple[bool, str]:
    """(configured, description for UI — never the raw key)."""
    data = _load_json_keys("gemini_keys.json")
    if isinstance(data, dict):
        for k, v in sorted(data.items()):
            if k.startswith("Gemini") and isinstance(v, str) and v.strip():
                return True, f"{mask_api_key(v)} (gemini_keys.json · {k})"
    env_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if env_key:
        return True, f"{mask_api_key(env_key)} (.env / GEMINI_API_KEY only)"
    return False, "No Gemini key — add one below or set GEMINI_API_KEY"


def save_gemini_api_key(api_key: str) -> tuple[bool, str]:
    key = (api_key or "").strip()
    if len(key) < 12:
        return False, "Key looks too short. Paste the full Google AI Studio key."

    path = os.path.join(_project_root(), "gemini_keys.json")
    data = _load_json_keys("gemini_keys.json")
    if not isinstance(data, dict):
        data = {}
    data["Gemini_1"] = key
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        return False, f"Could not write gemini_keys.json: {e}"

    os.environ["GEMINI_API_KEY"] = key
    _upsert_dotenv_var("GEMINI_API_KEY", key)
    return True, "Saved to gemini_keys.json and GEMINI_API_KEY in .env (restart not required)."


def delete_gemini_api_keys() -> tuple[bool, str]:
    path = os.path.join(_project_root(), "gemini_keys.json")
    data = _load_json_keys("gemini_keys.json")
    if isinstance(data, dict):
        for name in list(data.keys()):
            if name.startswith("Gemini"):
                del data[name]
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            return False, f"Could not update gemini_keys.json: {e}"

    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    _upsert_dotenv_var("GEMINI_API_KEY", None)
    return True, "Removed all Gemini_* entries from gemini_keys.json and GEMINI_API_KEY from .env."


def _upsert_dotenv_var(name: str, value: str | None) -> None:
    env_path = os.path.join(_project_root(), ".env")
    if not os.path.isfile(env_path) and value is None:
        return
    kept: list[str] = []
    if os.path.isfile(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    kept.append(line)
                    continue
                k = s.split("=", 1)[0].strip()
                if k == name:
                    continue
                kept.append(line)
    if value is not None and str(value).strip() != "":
        if kept and not kept[-1].endswith("\n"):
            kept[-1] = kept[-1] + "\n"
        kept.append(f"{name}={value.strip()}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(kept)
