import os
import sys
import requests
import json
import time
import threading
import re
from datetime import datetime
from json_repair_tool import repair_json, validate_incident_schema
from station_mapping import get_station_info
from quota_manager import get_quota_mgr

from api_keys import load_env, get_gemini_keys, get_github_keys, get_openrouter_key, get_aimlapi_keys, get_groq_keys
from machine_translator import _gemini_generate_models, sanitize_police_translation_output
from models import IncidentRecord, CategorizationOutput
from ai_providers import GitHubProvider, GeminiProvider, OllamaProvider
from config_loader import get_config
from knowledge_loader import ExpertKnowledgeLoader

# Ensure UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for Python versions < 3.7
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables from project .env
load_env()


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _is_network_dns_failure(msg) -> bool:
    """True if failure is DNS / no route (all remote APIs will fail the same way)."""
    if not msg:
        return False
    s = str(msg).lower()
    return any(
        x in s
        for x in (
            "getaddrinfo failed",
            "nameresolutionerror",
            "failed to resolve",
            "name or service not known",
            "temporary failure in name resolution",
            "network is unreachable",
            "no route to host",
        )
    )


def _is_ai_refusal(text: str) -> bool:
    """Detects if the AI returned a refusal (e.g. safety filters)."""
    if not text:
        return False
    refusal_keywords = [
        "i am sorry",
        "i cannot",
        "i'm sorry",
        "as an ai",
        "policy",
        "unable to",
        "don't have the ability",
        "does not permit",
        "restricted",
        "sensitive content",
        "violence",
        "graphic",
    ]
    low = (text.decode("utf-8") if isinstance(text, bytes) else str(text)).lower()
    return any(kw in low for kw in refusal_keywords)


def _post_process_police_data_text(text: str) -> str:
    """Cleans up the AI response, removing markdown code fences around JSON."""
    if not text:
        return text
    if "```json" in text:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
    if "```" in text:
        match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
    return text.strip()


def _split_large_text(text, max_chars, overlap=400):
    """Split text into chunks at paragraph boundaries; hard-split long paragraphs."""
    if not text:
        return [""]
    text = text.strip()
    if max_chars < 500:
        max_chars = 500
    if len(text) <= max_chars:
        return [text]
    chunks = []
    paras = text.split("\n\n")
    buf, cur_len = [], 0

    def flush_buf():
        nonlocal buf, cur_len
        if buf:
            chunks.append("\n\n".join(buf))
            buf, cur_len = [], 0

    for p in paras:
        plen = len(p)
        if plen > max_chars:
            flush_buf()
            start = 0
            while start < plen:
                end = min(start + max_chars, plen)
                chunks.append(p[start:end])
                start = end - overlap if end < plen else plen
            continue
        added = plen + (2 if buf else 0)
        if cur_len + added <= max_chars:
            buf.append(p)
            cur_len += added
        else:
            flush_buf()
            buf, cur_len = [p], plen
    flush_buf()
    return chunks


# ---------------------------------------------------------------------------
# Main Engine Manager
# ---------------------------------------------------------------------------

class AIEngineManager:
    """Unified engine manager for GitHub, AIML API, Groq, OpenRouter, Gemini, and Ollama."""

    # Class-level set — persists across hot-reloads in dev servers
    offline_engines: set = set()

    def __init__(self, mode="fast"):
        # Mode: "fast" (Direct Ollama), "triple" (Gemini -> Ollama), "consensus" (Ollama + Validator)
        self.mode = os.getenv("DEFAULT_ENGINE", mode).lower()
        if self.mode not in ["fast", "triple", "consensus"]:
            self.mode = "fast"

        # ── API Keys & Configuration ──────────────────────────────────────
        self.openrouter_key   = get_openrouter_key()
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free")

        self.aimlapi_keys  = get_aimlapi_keys()
        self.aimlapi_key   = self.aimlapi_keys[0] if self.aimlapi_keys else None
        _aiml_base         = os.getenv("AIMLAPI_BASE_URL", "https://api.aimlapi.com/v1").strip().rstrip("/")
        self.aimlapi_base  = _aiml_base or "https://api.aimlapi.com/v1"
        self.aimlapi_model = os.getenv("AIMLAPI_MODEL", "google/gemini-2-flash-lite")

        self.groq_keys  = get_groq_keys()
        self.groq_key   = self.groq_keys[0] if self.groq_keys else None
        _groq_base      = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip().rstrip("/")
        self.groq_base  = _groq_base or "https://api.groq.com/openai/v1"
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        self.gemini_keys = get_gemini_keys()
        self.gemini_key  = self.gemini_keys[0] if self.gemini_keys else None

        self.github_url   = os.getenv("GITHUB_API_URL", "https://models.inference.ai.azure.com")
        self.github_model = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
        _gh_models_env    = os.getenv("GITHUB_MODELS", "").strip()
        self.github_models = (
            [m.strip() for m in _gh_models_env.split(",") if m.strip()]
            if _gh_models_env
            else ["gpt-4o-mini", "gpt-4o"]
        )

        self.github_keys      = get_github_keys()
        self.github_key_index = 0
        self.github_lock      = threading.Lock()
        self.github_key       = self.github_keys[0][1] if self.github_keys else None  # FIX: was [0] not [0][1]

        # ── Ollama / Kaggle Configuration ─────────────────────────────────
        _ollama_url_default    = "http://localhost:11434/api/generate"
        _ollama_model_default  = "sri-lanka-police-ai"
        _kaggle_url_default    = "https://YOUR-NGROK-URL.ngrok-free.app/api/generate"
        _kaggle_model_default  = "police-ai-master:latest"
        _prefer_kaggle_default = False

        cfg = get_config()
        if cfg:
            oll_cfg = cfg.get("ai_engines", {}).get("ollama", {})
            if oll_cfg.get("base_url"):
                _ollama_url_default = oll_cfg["base_url"]
            if oll_cfg.get("local_model"):
                _ollama_model_default = oll_cfg["local_model"]
            if oll_cfg.get("kaggle_url"):
                _kaggle_url_default = oll_cfg["kaggle_url"]
            if oll_cfg.get("kaggle_model"):
                _kaggle_model_default = oll_cfg["kaggle_model"]
            if oll_cfg.get("prefer_kaggle") is not None:
                _prefer_kaggle_default = oll_cfg["prefer_kaggle"]
            print("  [AI Config] Loaded Ollama settings from centralized config")

        self.local_ollama_url    = os.getenv("OLLAMA_BASE_URL", _ollama_url_default)
        self.local_ollama_model  = _ollama_model_default
        self.kaggle_ollama_url   = os.getenv("KAGGLE_OLLAMA_URL", _kaggle_url_default)
        self.kaggle_ollama_model = os.getenv("KAGGLE_OLLAMA_MODEL", _kaggle_model_default)
        self.prefer_kaggle_ollama = _prefer_kaggle_default

        # Derived / unified fields
        self.ollama_url          = self.kaggle_ollama_url  if self.prefer_kaggle_ollama else self.local_ollama_url
        self.ollama_model        = self.kaggle_ollama_model if self.prefer_kaggle_ollama else self.local_ollama_model
        self.ollama_tuned_model  = self.ollama_model

        # ── State & Stats ─────────────────────────────────────────────────
        self.last_engine_used = None
        self.stats = {
            "ollama_calls": 0, "failures": 0, "github_calls": 0,
            "openrouter_calls": 0, "aimlapi_calls": 0, "groq_calls": 0,
        }
        self.stats_lock    = threading.Lock()
        self.failure_counts: dict = {}
        self._net_unreachable = False

        if not hasattr(AIEngineManager, "offline_engines"):
            AIEngineManager.offline_engines = set()

        # ── Auto-skip engines with no keys ────────────────────────────────
        if not self.github_keys:
            print("  [AI] [SEC] GitHub Keys missing. Auto-skipping.")
            self.offline_engines.add("github")
        if not self.gemini_keys:
            print("  [AI] [SEC] Gemini Keys missing. Auto-skipping.")
            self.offline_engines.add("gemini")
        if not self.openrouter_key:
            self.offline_engines.add("openrouter")
        if not self.groq_keys:
            self.offline_engines.add("groq")
        if not self.aimlapi_keys:
            self.offline_engines.add("aimlapi")

        # ── Modular Providers ─────────────────────────────────────────────
        self.gh_provider     = GitHubProvider(self.github_url, self.github_model, self.github_keys)
        self.gemini_provider = GeminiProvider(self.gemini_keys)
        self.ollama_provider = OllamaProvider(self.ollama_url, self.ollama_model)

        # ── Ollama round-robin ────────────────────────────────────────────
        self.ollama_round_robin_index = 0
        self._round_robin_lock        = threading.Lock()
        self.ollama_models_cache      = None
        self.ollama_cache_time        = 0.0

        # ── Expert Knowledge Base ─────────────────────────────────────────
        self.knowledge_loader = ExpertKnowledgeLoader()

    # -----------------------------------------------------------------------
    # Ollama helpers
    # -----------------------------------------------------------------------

    def set_ollama_preference(self, prefer_kaggle: bool, url: str = None, model: str = None):
        """Update Ollama/Kaggle preferences at runtime."""
        if prefer_kaggle is not None:
            self.prefer_kaggle_ollama = prefer_kaggle
        if url:
            self.kaggle_ollama_url = url
        if model:
            self.kaggle_ollama_model = model

        # FIX: was using self.local_ollama_url on both branches
        self.ollama_url   = self.kaggle_ollama_url   if self.prefer_kaggle_ollama else self.local_ollama_url
        self.ollama_model = self.kaggle_ollama_model if self.prefer_kaggle_ollama else self.local_ollama_model

        # Sync provider
        self.ollama_provider = OllamaProvider(self.ollama_url, self.ollama_model)
        print(f"  [AI Config] Updated preference: {'Kaggle' if self.prefer_kaggle_ollama else 'Local'} (URL: {self.ollama_url})")

    def set_ollama_model(self, model_name: str):
        """Update the active Ollama model and sync provider."""
        self.ollama_model = model_name
        self.ollama_tuned_model = model_name
        self.ollama_provider = OllamaProvider(self.ollama_url, model_name)
        print(f"  [Ollama] Switched to model: {model_name}")

    def get_installed_ollama_models(self, force_refresh=False) -> list[str]:
        """Query Ollama for all installed models with 60-second caching."""
        current_time = time.time()
        if not force_refresh and self.ollama_models_cache and (current_time - self.ollama_cache_time) < 60:
            return self.ollama_models_cache

        try:
            import subprocess
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return ["llama3"]

            lines  = result.stdout.strip().split("\n")[1:]  # skip header
            models = [line.split()[0] for line in lines if line.strip()]
            if not models:
                self.ollama_models_cache = ["llama3"]
                self.ollama_cache_time   = current_time
                return self.ollama_models_cache

            ordered: list[str] = []
            seen:    set[str]   = set()

            def _add(name: str):
                if name not in seen:
                    seen.add(name)
                    ordered.append(name)

            # Custom police model first
            for m in models:
                if "sri-lanka-police-ai" in m.lower():
                    _add(m)

            preferred_tags = (
                "police-ai", "llama3", "llama4", "gemma", "qwen", "mistral",
                "mixtral", "phi", "gpt-oss", "deepseek", "command-r",
                "aya", "dolphin", "wizardlm", "vicuna", "codellama",
            )
            for tag in preferred_tags:
                for m in models:
                    if tag in m.lower():
                        _add(m)
            for m in models:
                _add(m)

            self.ollama_models_cache = ordered
            self.ollama_cache_time   = current_time
            return ordered

        except Exception as e:
            print(f"  [Ollama] Failed to list models: {e}")
            return ["llama3"]

    def get_next_ollama_model(self) -> str:
        """Thread-safe round-robin model selector from installed Ollama models."""
        models = self.get_installed_ollama_models()
        if not models:
            return self.ollama_model
        with self._round_robin_lock:
            model = models[self.ollama_round_robin_index % len(models)]
            self.ollama_round_robin_index += 1
        return model

    # -----------------------------------------------------------------------
    # Properties / flags
    # -----------------------------------------------------------------------

    @property
    def fallback_active(self) -> bool:
        """True when the last successful AI call used Ollama."""
        lu = getattr(self, "last_engine_used", None)
        return bool(lu and str(lu).lower().startswith("ollama"))

    def _ollama_consensus_enabled(self) -> bool:
        try:
            return bool(get_config().get("ollama_consensus", False))
        except Exception:
            return os.getenv("OLLAMA_CONSENSUS", "").strip().lower() in ("1", "true", "yes", "on")

    def set_dispatch_mode(self, mode: str):
        """Dynamically switch between 'sequential' and 'race' (parallel) mode."""
        os.environ["AI_DISPATCH_MODE"] = mode
        print(f"  [AI] Dispatch mode changed to: {mode}")

    # -----------------------------------------------------------------------
    # Core dispatch helpers
    # -----------------------------------------------------------------------

    def _dispatch_engine(self, engine: str, prompt: str, system_prompt: str, timeout: int,
                         model_override: str = None) -> str:
        """Route to the correct modular provider."""
        if engine == "ollama":
            if not self.ollama_url:
                return "❌ Ollama not configured (OLLAMA_BASE_URL missing)"
            # FIX: pass model_override so "ollama:custom-model" entries work
            return self.ollama_provider.call(prompt, system_prompt, timeout, model_override=model_override)

        if engine == "github":
            if not self.github_keys:
                return "❌ GitHub Models not configured (no github_keys.json)"
            return self.gh_provider.call(prompt, system_prompt, timeout, model_override=model_override)

        if engine == "gemini":
            if not self.gemini_keys:
                return "❌ Gemini not configured (GEMINI_API_KEY missing)"
            return self.gemini_provider.call(prompt, system_prompt, timeout)

        if engine == "openrouter":
            if not self.openrouter_key:
                return "❌ OpenRouter not configured (OPENROUTER_API_KEY missing)"
            return self._call_openrouter(prompt, system_prompt, timeout)

        if engine == "aimlapi":
            if not self.aimlapi_keys:
                return "❌ AI/ML API not configured (AIMLAPI_API_KEY missing)"
            return self._call_aimlapi(prompt, system_prompt, timeout)

        if engine == "groq":
            if not self.groq_keys:
                return "❌ Groq not configured (GROQ_API_KEY missing)"
            return self._call_groq(prompt, system_prompt, timeout)

        return f"❌ Unknown Engine: {engine}"

    def _dispatch_one_engine_raw(self, eng: str, prompt: str, system_prompt: str,
                                  timeout: int, model_override: str):
        """Run one engine entry (e.g. 'ollama:custom-model' or 'github'). Returns (base_eng, response)."""
        base_eng       = eng.split(":")[0] if ":" in eng else eng
        target_override = eng.split(":", 1)[1] if ":" in eng else model_override

        if base_eng == "ollama" and self._ollama_consensus_enabled():
            res = self.call_ollama_consensus(prompt, system_prompt, timeout, fast_mode=True)
        else:
            res = self._dispatch_engine(base_eng, prompt, system_prompt, timeout, target_override)

        if res and not str(res).startswith("❌") and _is_ai_refusal(res):
            print(f"  [AI] ⚠️ Refusal detected from {base_eng}. Triggering fallback.")
            res = f"❌ Refusal: {str(res)[:100]}…"

        return base_eng, res

    def _apply_successful_ai_result(self, res: str, eng: str, base_eng: str) -> str:
        self.last_engine_used = eng
        self.failure_counts[base_eng] = 0
        if "{" in res and "}" in res:
            return self._post_process_police_data(res)
        return res

    # -----------------------------------------------------------------------
    # Parallel (race) dispatch
    # -----------------------------------------------------------------------

    def _call_ai_parallel_race(self, engines_to_try: list, prompt: str, system_prompt: str,
                                timeout: int, model_override: str) -> str:
        """Invoke all engines at once; return the first successful response."""
        import concurrent.futures

        max_w = min(len(engines_to_try), max(1, int(os.getenv("AI_RACE_MAX_WORKERS", "8"))))
        print(f"  [AI-Race] Parallel dispatch: {len(engines_to_try)} engine(s), max_workers={max_w}")

        def _job(eng):
            try:
                base_eng, res = self._dispatch_one_engine_raw(eng, prompt, system_prompt, timeout, model_override)
                return eng, base_eng, res
            except Exception as e:
                b = eng.split(":")[0] if ":" in eng else eng
                return eng, b, f"❌ {str(e)[:120]}"

        last_error = None
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_w) as ex:
            futures = [ex.submit(_job, eng) for eng in engines_to_try]
            for fut in concurrent.futures.as_completed(futures):
                try:
                    eng, base_eng, res = fut.result()
                except Exception as e:
                    last_error = f"❌ race worker: {str(e)[:100]}"
                    continue
                if res and not str(res).startswith("❌"):
                    return self._apply_successful_ai_result(res, eng, base_eng)
                last_error = res

        error_msg = f"❌ All {len(engines_to_try)} engines failed (parallel race)."
        if last_error:
            error_msg += f"\nLast error: {str(last_error)[:150]}"
        return error_msg

    # -----------------------------------------------------------------------
    # Public call_ai entry point
    # -----------------------------------------------------------------------

    def call_ai(self, prompt: str,
                system_prompt: str = "You are a professional police report assistant.",
                timeout: int = 120,
                restricted_list: list = None,
                model_override: str = None,
                category_context: str = None) -> str:
        """
        Main AI dispatch with optional engine restrictions and model overrides.
        Fallback chain: Ollama → GitHub → AIMLAPI → Groq → OpenRouter → Gemini
        """
        if category_context:
            system_prompt += (
                f"\n\n[INSTITUTIONAL CONTEXT]\n"
                f"This incident belongs to: '{category_context}'.\n"
                "Use formal Sri Lanka Police terminology (e.g. 'Homicide', 'Fatal Accident', 'Robbery')."
            )

        # Inject Expert Knowledge (Few-Shot Examples)
        expert_context = self.knowledge_loader.get_few_shot_context(limit=6)
        if expert_context:
            system_prompt += (
                "\n\n[EXPERT REFERENCE DATA - FOR INTERNAL USE ONLY]\n"
                "The following are examples of the institutional standard YOU MUST EMULATE. "
                "DO NOT copy these specific examples into your response. Simply use them as a "
                "stylistic and technical guide.\n"
            )
            system_prompt += expert_context
            system_prompt += "\n[END OF EXPERT REFERENCE DATA]\n"

        if self.mode == "consensus":
            return self.call_with_validation(prompt, system_prompt, timeout)

        # Build engine list
        if restricted_list:
            engines_to_try = [e for e in restricted_list
                              if e in ("ollama", "github", "openrouter", "gemini", "aimlapi", "groq")]
        else:
            engines_to_try = []
            if self.openrouter_key and "openrouter" not in self.offline_engines:
                engines_to_try.append("openrouter")
            if self.github_keys and "github" not in self.offline_engines:
                engines_to_try.append("github")
            if self.groq_keys and "groq" not in self.offline_engines:
                engines_to_try.append("groq")
            if self.aimlapi_keys and "aimlapi" not in self.offline_engines:
                engines_to_try.append("aimlapi")
            if self.ollama_url and "ollama" not in self.offline_engines:
                engines_to_try.append(f"ollama:{self.ollama_tuned_model}")
            if self.gemini_keys and "gemini" not in self.offline_engines:
                engines_to_try.append("gemini")

        if not engines_to_try:
            return "❌ No AI engines available or all are currently marked OFFLINE."

        dispatch = os.getenv("AI_DISPATCH_MODE", "sequential").strip().lower()
        if dispatch in ("race", "parallel", "fast") and len(engines_to_try) > 1:
            return self._call_ai_parallel_race(engines_to_try, prompt, system_prompt, timeout, model_override)

        last_error = None
        for eng in engines_to_try:
            base_eng = eng.split(":")[0] if ":" in eng else eng
            if base_eng in self.offline_engines:
                continue
            try:
                base_eng, res = self._dispatch_one_engine_raw(eng, prompt, system_prompt, timeout, model_override)
                if res and not res.startswith("❌"):
                    return self._apply_successful_ai_result(res, eng, base_eng)

                last_error = res

                if "401" in str(res):
                    print(f"  [AI] 🛡️ {base_eng} → UNAUTHORIZED (401). Marking OFFLINE.")
                    self.offline_engines.add(base_eng)
                elif "500" in str(res) and base_eng == "ollama":
                    print(f"  [AI] 🛡️ Ollama → 500 OVERLOAD. Marking OFFLINE until restart.")
                    self.offline_engines.add(base_eng)
                else:
                    self.failure_counts[base_eng] = self.failure_counts.get(base_eng, 0) + 1
                    if self.failure_counts[base_eng] >= 3:
                        print(f"  [AI] ⚠️ {base_eng} failing repeatedly. Marking OFFLINE.")
                        self.offline_engines.add(base_eng)

            except Exception as e:
                last_error = f"❌ {eng.capitalize()} exception: {str(e)[:100]}"
                self.failure_counts[base_eng] = self.failure_counts.get(base_eng, 0) + 1
                if self.failure_counts[base_eng] >= 3:
                    self.offline_engines.add(base_eng)

        error_msg = f"❌ All {len(engines_to_try)} engines failed."
        if last_error:
            error_msg += f"\nLast error: {last_error[:150]}"
        return error_msg

    def fast_refine(self, text: str, system_prompt: str = "Refine this police incident.") -> str:
        """High-speed single-call refinement using GitHub Models (gpt-4o-mini)."""
        print("  [AI-Turbo] Fast-refining with gpt-4o-mini…")
        return self.call_ai(text, system_prompt=system_prompt,
                            restricted_list=["github"], model_override="gpt-4o-mini")

    # -----------------------------------------------------------------------
    # Post-processing
    # -----------------------------------------------------------------------

    def _post_process_police_data(self, json_str: str) -> str:
        """Deep post-processing with Pydantic validation and station ground-truth override."""
        if not json_str or "{" not in json_str:
            return json_str
        try:
            repaired  = repair_json(json_str)
            raw_data  = json.loads(repaired)
            incident  = IncidentRecord(**raw_data)

            # Station ground-truth override
            info = get_station_info(incident.station)
            if info:
                incident.province = info.get("province", incident.province)
                if "div" in info:
                    incident.division = info["div"]

            return incident.json(indent=2)
        except Exception as e:
            print(f"  [Post-Process] ⚠️ Pydantic Validation Failed: {e}")
            # Still try to clean markdown fences
            return _post_process_police_data_text(json_str)

    # -----------------------------------------------------------------------
    # Triple/Dual Refinement Pipeline
    # -----------------------------------------------------------------------

    def triple_refine_pipeline(self, sinhala_text: str, timeout: int = 120) -> str:
        """
        DUAL-STAGE PIPELINE:
          Stage 1 – Gemini (linguistic correction / translation)
          Stage 2 – Ollama (institutional 8-field JSON formatting)
        """
        print("🚀 [Dual-AI] Stage 1: Gemini Refinement…")
        gemini_prompt = (
            f"Original Sinhala Police Record:\n{sinhala_text}\n\n"
            "Task: Translate this record into clinical, institutional English. "
            "Fix technical police terminology, ensure station/province names are correct, "
            "and improve narrative flow. Output ONLY the refined English narrative."
        )
        refined_text = self._dispatch_engine("gemini", gemini_prompt,
                                             "You are an expert Sri Lanka Police legal translator.", timeout)

        if refined_text.startswith("❌"):
            print(f"  ⚠️ Stage 1 Failed ({refined_text}). Using raw text for Stage 2.")
            refined_text = sinhala_text

        print("🚀 [Dual-AI] Stage 2: Ollama Formatting (8-Field Schema)…")
        ollama_prompt = (
            f"Refined Incident Narrative:\n{refined_text}\n\n"
            "Task: Convert this narrative into the Official Sri Lanka Police 8-field institutional format. "
            "Fields: station, division, date, time, description, financial_loss, status, victim_suspect_names. "
            "Return valid JSON only."
        )
        final_json = self.ollama_provider.call(ollama_prompt,
                                               "You are the Sri Lanka Police Data Architect.", timeout)

        if final_json.startswith("❌"):
            print(f"  ⚠️ Stage 2 Failed. Wrapping refined text as fallback JSON.")
            return json.dumps({
                "station": "Unknown", "division": "Unknown", "date": "", "time": "",
                "description": refined_text, "financial_loss": "Nil",
                "status": "Ongoing", "victim_suspect_names": "N/A",
            }, ensure_ascii=False)

        return self._post_process_police_data(final_json)

    # -----------------------------------------------------------------------
    # Consensus / Validation mode
    # -----------------------------------------------------------------------

    def call_with_validation(self, prompt: str,
                              system_prompt: str = "Maximum Fidelity Mode",
                              timeout: int = 120) -> str:
        """
        Consensus: Ollama primary + cloud validator cross-check.
        Falls back sequentially if either side fails.
        """
        print("  [AI] Running in Consensus Mode…")
        primary_res = self._dispatch_engine("ollama", prompt, system_prompt, timeout)

        if primary_res.startswith("❌"):
            print("  [AI] Primary (Ollama) failed. Falling back sequentially.")
            for eng in ("openrouter", "aimlapi", "groq", "gemini", "github"):
                if eng not in self.offline_engines:
                    res = self._dispatch_engine(eng, prompt, system_prompt, timeout)
                    if not res.startswith("❌"):
                        return res
            return primary_res

        # Pick a cloud validator
        validator = next(
            (e for e in ("openrouter", "aimlapi", "groq", "github", "gemini")
             if e not in self.offline_engines),
            None,
        )
        if not validator:
            return primary_res

        val_res = self._dispatch_engine(validator, prompt, system_prompt, timeout)
        if val_res.startswith("❌"):
            print(f"  [AI] Validator ({validator}) failed. Returning primary.")
            return primary_res

        # Sanity checks
        if len(primary_res) < 50 and len(val_res) > 200:
            print("  [AI] Consensus: Primary too short → using validator.")
            return val_res
        if "KOTTHALA" in primary_res.upper() and "KOTTHALA" not in val_res.upper():
            print("  [AI] Consensus ALERT: Possible hallucination in primary → using validator.")
            return val_res

        return primary_res

    def call_parallel(self, prompt: str,
                      system_prompt: str = "Maximum Accuracy Mode",
                      timeout: int = 120) -> dict:
        """Call all configured engines in parallel; returns per-engine results dict."""
        import concurrent.futures

        engines = [
            e for e in ("ollama", "github", "aimlapi", "groq", "openrouter", "gemini")
            if e not in self.offline_engines and (
                (e == "ollama"      and self.ollama_url)   or
                (e == "github"      and self.github_keys)  or
                (e == "aimlapi"     and self.aimlapi_keys) or
                (e == "groq"        and self.groq_keys)    or
                (e == "openrouter"  and self.openrouter_key) or
                (e == "gemini"      and self.gemini_keys)
            )
        ]
        if not engines:
            return {}

        max_w   = min(len(engines), max(1, int(os.getenv("AI_RACE_MAX_WORKERS", "8"))))
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_w) as executor:
            future_to_engine = {
                executor.submit(self._dispatch_engine, e, prompt, system_prompt, timeout): e
                for e in engines
            }
            for future in concurrent.futures.as_completed(future_to_engine):
                eng = future_to_engine[future]
                try:
                    results[eng] = future.result()
                except Exception as e:
                    results[eng] = f"❌ Exception: {e}"
        return results

    # -----------------------------------------------------------------------
    # Ollama multi-model helpers
    # -----------------------------------------------------------------------

    def call_ollama_consensus(self, prompt: str,
                               system_prompt: str = "You are a professional police report assistant.",
                               timeout: int = 240,
                               fast_mode: bool = False) -> str:
        """
        Round-robin / consensus across installed Ollama models.
        fast_mode=True → pick next model via round-robin (speed).
        fast_mode=False → try all, return first success (accuracy).
        """
        models = self.get_installed_ollama_models()
        if not models:
            return self._dispatch_engine("ollama", prompt, system_prompt, timeout)

        if fast_mode or len(models) == 1:
            model = self.get_next_ollama_model()
            print(f"  [Turbo] Speed Mode: '{model}' (Round-Robin)")
            return self._dispatch_engine("ollama", prompt, system_prompt, timeout, model_override=model)

        print(f"  [Consensus] Accuracy Mode: {len(models)} model(s): {models}")
        for model in models:
            res = self._dispatch_engine("ollama", prompt, system_prompt, timeout, model_override=model)
            if res and not res.startswith("❌"):
                print(f"  [Consensus] ✓ '{model}' succeeded ({len(res)} chars)")
                return res
            print(f"  [Consensus] ✗ '{model}' failed.")

        return f"❌ All {len(models)} consensus Ollama models failed."

    def _ollama_try_all_models(self, prompt: str, system_prompt: str, timeout: int) -> str:
        """Try every installed Ollama model in priority order until one succeeds."""
        if not self.ollama_url:
            return "❌ Ollama not configured (OLLAMA_BASE_URL missing)"

        try_all = os.getenv("OLLAMA_TRY_ALL_MODELS", "1").strip().lower() not in ("0", "false", "no", "off")
        if not try_all:
            return self._dispatch_engine("ollama", prompt, system_prompt, timeout)

        models = self.get_installed_ollama_models(force_refresh=True)
        if not models:
            return self._dispatch_engine("ollama", prompt, system_prompt, timeout)

        skip_cloud = (
            os.getenv("OLLAMA_SKIP_CLOUD_MODELS", "").strip().lower() in ("1", "true", "yes", "on")
            or self._net_unreachable
        )
        if skip_cloud:
            before  = len(models)
            models  = [m for m in models if ":cloud" not in m.lower() and not m.lower().endswith("-cloud")]
            dropped = before - len(models)
            if dropped:
                print(f"  [Ollama] ⏭️ Skipped {dropped} cloud model(s).")

        if not models:
            return self._dispatch_engine("ollama", prompt, system_prompt, timeout)

        preview = ", ".join(models[:12]) + (", …" if len(models) > 12 else "")
        print(f"  [Ollama] Trying {len(models)} local model(s): {preview}")

        last = None
        for m in models:
            res  = self._dispatch_engine("ollama", prompt, system_prompt, timeout, model_override=m)
            last = res
            if res and not str(res).startswith("❌"):
                print(f"  [Ollama] ✅ '{m}' succeeded ({len(res)} chars)")
                return res
            print(f"  [Ollama] ✗ '{m}' failed — next model…")
        return last or "❌ Ollama: all local models failed."

    # -----------------------------------------------------------------------
    # GitHub multi-key parallel dispatch
    # -----------------------------------------------------------------------

    def _call_github_unchunked(self, prompt: str, system_prompt: str, timeout: int) -> str:
        """Try each GitHub model, racing all keys in parallel batches."""
        if not self.github_keys:
            return "❌ GitHub Models Error: No API keys available."

        import concurrent.futures
        last_error = None

        def _run(model_name: str, api_key: str, key_id: str) -> str:
            get_quota_mgr().record_usage(key_id, "GitHub")
            try:
                max_out = max(256, min(int(os.getenv("GITHUB_MAX_OUTPUT_TOKENS", "8192")), 16384))
            except ValueError:
                max_out = 8192

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": prompt},
                ],
                "max_tokens": max_out,
                "temperature": 0.3,
            }
            res = requests.post(f"{self.github_url}/chat/completions",
                                headers=headers, json=payload, timeout=timeout)

            rem = res.headers.get("x-ratelimit-remaining-requests")
            if rem:
                try:
                    get_quota_mgr().update_from_headers(key_id, int(rem))
                except Exception:
                    pass

            if res.status_code == 200:
                data = res.json()
                if "choices" in data and data["choices"]:
                    ch = data["choices"][0]
                    if ch.get("finish_reason") == "length":
                        print(f"  [GitHub] ⚠️ Truncated output for {model_name}. "
                              "Consider raising GITHUB_MAX_OUTPUT_TOKENS.")
                    return ch["message"]["content"]
                raise RuntimeError("Empty choices")
            if res.status_code == 429:
                raise RuntimeError(f"Rate Limit (429) on {model_name}")
            if res.status_code == 401:
                raise RuntimeError(f"Invalid key (401) for {model_name}")
            raise RuntimeError(f"{res.status_code}: {res.text[:100]}")

        for model in self.github_models:
            print(f"  [GitHub] Attempting {model} with {len(self.github_keys)} key(s) in parallel…")
            batch_size = 5
            for batch_start in range(0, len(self.github_keys), batch_size):
                batch = self.github_keys[batch_start:batch_start + batch_size]
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as ex:
                    futures = {}
                    for key_id, key_val in batch:
                        if get_quota_mgr().is_key_exhausted(key_id, "GitHub"):
                            print(f"  [GitHub] ⏭️ Skipping exhausted key: {key_id}")
                            continue
                        futures[ex.submit(_run, model, key_val, key_id)] = f"{model} ({key_id})"

                    for fut in concurrent.futures.as_completed(futures):
                        label = futures[fut]
                        try:
                            result = fut.result()
                            print(f"  [GitHub] 🏆 {label} WON!")
                            with self.stats_lock:
                                self.stats["github_calls"] += 1
                            return result
                        except Exception as e:
                            last_error = str(e)

            print(f"  [GitHub] All keys exhausted for {model}. Trying next model…")
            if last_error and _is_network_dns_failure(last_error):
                print("  [GitHub] DNS/Network failure — skipping remaining GitHub models.")
                self._net_unreachable = True
                self.offline_engines.update(("github", "aimlapi", "groq", "openrouter"))
                break

        return f"❌ GitHub Models Error: All models/keys failed. Last: {last_error}"

    # -----------------------------------------------------------------------
    # Translation fallback chain
    # -----------------------------------------------------------------------

    def _mt_fallback_engines_ordered(self, skip_github: bool) -> list[str]:
        """
        Ordered fallback engines for machine translation (after Gemini exhausted).
        Override with env MT_FALLBACK_CHAIN (comma-separated).
        """
        available = []
        if self.openrouter_key:
            available.append("openrouter")
        if not skip_github and self.github_keys:
            available.append("github")
        if self.groq_keys:
            available.append("groq")
        if self.aimlapi_keys:
            available.append("aimlapi")
        if self.ollama_url:
            available.append("ollama")

        raw = (os.getenv("MT_FALLBACK_CHAIN") or "").strip()
        if not raw:
            return available

        preferred = [x.strip().lower() for x in raw.split(",") if x.strip()]
        seen, out = set(), []
        for e in preferred:
            if e in available and e not in seen:
                out.append(e); seen.add(e)
        for e in available:
            if e not in seen:
                out.append(e)
        return out

    def translation_fallback_after_gemini_exhausted(
        self,
        prompt:        str,
        system_prompt: str  = "Expert Sri Lanka Police Sinhala-to-English translator. Full literal translation, no omissions.",
        timeout:       int  = 300,
        skip_github:   bool = True,
    ) -> str:
        """Fallback translation chain invoked after Gemini is exhausted."""
        engines = self._mt_fallback_engines_ordered(skip_github)
        if not engines:
            return "❌ No fallback engines configured."

        last = None
        for eng in engines:
            if eng in self.offline_engines:
                print(f"  [MT-Chain] ⏭️ Skipping {eng} (offline).")
                continue
            if self._net_unreachable and eng in ("github", "aimlapi", "groq", "openrouter"):
                print(f"  [MT-Chain] ⏭️ Skipping {eng} (network unreachable).")
                continue
            print(f"  [MT-Chain] Trying {eng}…")
            try:
                res  = self._ollama_try_all_models(prompt, system_prompt, timeout) if eng == "ollama" \
                       else self._dispatch_engine(eng, prompt, system_prompt, timeout)
                last = res
                if res and not str(res).startswith("❌"):
                    print(f"  [MT-Chain] ✅ {eng} succeeded ({len(res)} chars)")
                    return res
                if _is_network_dns_failure(str(res)):
                    self._net_unreachable = True
                    self.offline_engines.update(("github", "aimlapi", "groq", "openrouter"))
                print(f"  [MT-Chain] ✗ {eng}: {str(res)[:180]}")
            except Exception as e:
                last = f"❌ {eng}: {e}"
                if _is_network_dns_failure(str(e)):
                    self._net_unreachable = True
                    self.offline_engines.update(("github", "aimlapi", "groq", "openrouter"))
                print(f"  [MT-Chain] ✗ {eng} exception: {e}")

        return last or "❌ All translation fallback engines failed."

    # -----------------------------------------------------------------------
    # Legacy wrappers (kept for backward compatibility)
    # -----------------------------------------------------------------------

    def _call_gemini(self, prompt: str, system_prompt: str, timeout: int) -> str:
        return self._dispatch_engine("gemini", prompt, system_prompt, timeout)

    def _call_github(self, prompt: str, system_prompt: str, timeout: int) -> str:
        return self._dispatch_engine("github", prompt, system_prompt, timeout)

    def _call_ollama(self, prompt: str, system_prompt: str, timeout: int,
                     model_override: str = None) -> str:
        return self._dispatch_engine("ollama", prompt, system_prompt, timeout, model_override)

    # -----------------------------------------------------------------------
    # Cloud provider implementations
    # -----------------------------------------------------------------------

    def _call_openrouter(self, prompt: str, system_prompt: str, timeout: int) -> str:
        try:
            with self.stats_lock:
                self.stats["openrouter_calls"] += 1
            try:
                or_max = max(512, min(int(os.getenv("OPENROUTER_MAX_TOKENS", "16384")), 128000))
            except ValueError:
                or_max = 16384

            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mirihana.police.lk",
                "X-Title": "Police Report Engine",
            }
            payload = {
                "model": self.openrouter_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": prompt},
                ],
                "max_tokens": or_max,
                "temperature": 0.7,
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                headers=headers, json=payload, timeout=timeout)
            if res.status_code == 200:
                data = res.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
                return "❌ OpenRouter returned no choices"
            if res.status_code == 401:
                return "❌ OpenRouter Error: Invalid API key (401)"
            if res.status_code == 402:
                return "❌ OpenRouter Error: Insufficient credits (402)"
            if res.status_code == 429:
                return "❌ OpenRouter Error: Rate limit exceeded (429)"
            return f"❌ OpenRouter Error: {res.status_code} - {res.text[:200]}"
        except requests.exceptions.ConnectionError as e:
            return f"❌ OpenRouter Connection Failed: {str(e)[:100]}"
        except requests.exceptions.Timeout:
            return f"❌ OpenRouter Timeout after {timeout}s"
        except Exception as e:
            with self.stats_lock:
                self.stats["failures"] += 1
            return f"❌ OpenRouter Exception: {str(e)[:200]}"

    def _call_aimlapi(self, prompt: str, system_prompt: str, timeout: int) -> str:
        if not self.aimlapi_keys:
            return "❌ AI/ML API Error: No API keys available."
        try:
            aiml_max  = max(512, min(int(os.getenv("AIMLAPI_MAX_TOKENS",  "16384")), 128000))
            aiml_temp = float(os.getenv("AIMLAPI_TEMPERATURE", "0.7"))
        except ValueError:
            aiml_max, aiml_temp = 16384, 0.7

        url      = f"{self.aimlapi_base}/chat/completions"
        last_err = None
        for attempt, api_key in enumerate(self.aimlapi_keys, 1):
            try:
                with self.stats_lock:
                    self.stats["aimlapi_calls"] += 1
                res = requests.post(
                    url,
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": self.aimlapi_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user",   "content": prompt},
                        ],
                        "max_tokens": aiml_max,
                        "temperature": aiml_temp,
                    },
                    timeout=timeout,
                )
                if res.status_code == 200:
                    data    = res.json()
                    content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
                    return content if content else "❌ AI/ML API returned no content."
                if res.status_code == 401:
                    return "❌ AI/ML API Error: Invalid API key (401)."
                last_err = f"{res.status_code}: {res.text[:200]}"
                print(f"  [AIMLAPI] Key {attempt} failed ({res.status_code}). Trying next…")
            except requests.exceptions.Timeout:
                return f"❌ AI/ML API Timeout after {timeout}s"
            except Exception as e:
                last_err = str(e)[:200]
                with self.stats_lock:
                    self.stats["failures"] += 1
        return f"❌ AI/ML API failed for all keys. Last: {last_err}"

    def _call_groq(self, prompt: str, system_prompt: str, timeout: int) -> str:
        if not self.groq_keys:
            return "❌ Groq Error: No API keys available."
        try:
            gq_max  = max(256, min(int(os.getenv("GROQ_MAX_TOKENS",  "8192")), 32768))
            gq_temp = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
        except ValueError:
            gq_max, gq_temp = 8192, 0.7

        url      = f"{self.groq_base}/chat/completions"
        msgs     = [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user",   "content": prompt},
        ]
        last_err = None
        for attempt, api_key in enumerate(self.groq_keys, 1):
            try:
                with self.stats_lock:
                    self.stats["groq_calls"] += 1
                res = requests.post(
                    url,
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": self.groq_model,
                        "messages": msgs,
                        "max_tokens": gq_max,
                        "temperature": gq_temp,
                    },
                    timeout=timeout,
                )
                if res.status_code == 200:
                    data    = res.json()
                    content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
                    return content if content else "❌ Groq returned no content."
                if res.status_code == 401:
                    return "❌ Groq Error: Invalid API key (401)."
                last_err = f"{res.status_code}: {res.text[:200]}"
                print(f"  [Groq] Key {attempt} failed ({res.status_code}). Trying next…")
            except requests.exceptions.Timeout:
                return f"❌ Groq Timeout after {timeout}s"
            except Exception as e:
                last_err = str(e)[:200]
                with self.stats_lock:
                    self.stats["failures"] += 1
        return f"❌ Groq failed for all keys. Last: {last_err}"

    # -----------------------------------------------------------------------
    # Kaggle streaming
    # -----------------------------------------------------------------------

    def call_kaggle_process_stream(self, file_path: str, fast_mode: bool = False):
        """Connect to Kaggle Surya OCR server and stream NDJSON results."""
        active_url = self.kaggle_ollama_url.replace("/api/generate", "/api/process_document")
        print(f"  [Kaggle-Stream] Connecting to: {active_url}")
        try:
            with open(file_path, "rb") as f:
                res = requests.post(
                    active_url,
                    files={"file": (os.path.basename(file_path), f, "application/pdf")},
                    data={"fast_mode": str(fast_mode).lower()},
                    headers={"ngrok-skip-browser-warning": "true", "User-Agent": "PoliceAI-Client/2.0"},
                    stream=True,
                    timeout=(15, 600),
                )
                if res.status_code != 200:
                    yield {"type": "error", "error": f"HTTP {res.status_code}: {res.text[:200]}"}
                    return
                for line in res.iter_lines():
                    if line:
                        try:
                            yield json.loads(line.decode("utf-8").strip())
                        except (json.JSONDecodeError, Exception):
                            continue
        except Exception as e:
            yield {"type": "error", "error": f"Connection failed: {e}"}


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_manager: AIEngineManager | None = None

def get_engine(mode: str = "auto") -> AIEngineManager:
    global _manager
    if _manager is None:
        _manager = AIEngineManager(mode=mode)
    return _manager


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("---[ AI Engine Manager Test ]---")
    mgr      = get_engine(mode="auto")
    test_res = mgr.call_ai("Hello, test engine connection. Respond with 'ACK'.")
    print(f"Engine Used : {mgr.last_engine_used}")
    print(f"Response    : {test_res}")