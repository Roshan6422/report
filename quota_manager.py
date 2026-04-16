import os
import json
import time
from threading import Lock

class QuotaManager:
    _instance = None
    _lock = Lock()
    
    # Defaults for Free Tier
    LIMITS = {
        "Gemini": {"RPM": 15, "RPD": 1500},
        "GitHub": {"RPM": 15, "RPD": 150}
    }
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(QuotaManager, cls).__new__(cls)
                cls._instance._init()
            return cls._instance
            
    def _init(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usage_db.json")
        self.usage = {} # { "KeyId": {"daily_count": 0, "last_reset_day": "2024-04-03", "minute_count": 0, "last_reset_min": 171212...} }
        self._load_db()

    def _load_db(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    self.usage = json.load(f)
            except:
                self.usage = {}

    def _save_db(self):
        try:
            with open(self.db_path, "w") as f:
                json.dump(self.usage, f, indent=2)
        except:
            pass

    def _get_key_state(self, key_id, provider):
        now = time.time()
        today = time.strftime("%Y-%m-%d")
        
        if key_id not in self.usage:
            self.usage[key_id] = {
                "daily_count": 0,
                "last_reset_day": today,
                "minute_count": 0,
                "last_reset_min": now
            }
        
        state = self.usage[key_id]
        
        # Reset Daily if new day
        if state["last_reset_day"] != today:
            state["daily_count"] = 0
            state["last_reset_day"] = today
            
        # Reset Minute if > 60s passed
        if now - state.get("last_reset_min", 0) > 60:
            state["minute_count"] = 0
            state["last_reset_min"] = now
            
        return state

    def record_usage(self, key_id, provider="Gemini", tokens=0, exhausted=False):
        with self._lock:
            state = self._get_key_state(key_id, provider)
            state["daily_count"] += 1
            state["minute_count"] += 1
            if exhausted:
                state["exhausted_until"] = time.time() + 3600 # 1 hour cooldown
            self._save_db()

    def is_key_exhausted(self, key_id, provider="Gemini"):
        with self._lock:
            state = self._get_key_state(key_id, provider)
            # Check for hard limit
            limits = self.LIMITS.get(provider, {"RPM": 15, "RPD": 1500})
            if state["daily_count"] >= limits["RPD"]:
                return True
            # Check for cooldown
            if "exhausted_until" in state and time.time() < state["exhausted_until"]:
                return True
            # Check for server reported limit (GitHub)
            if provider == "GitHub" and state.get("server_remaining") == 0:
                # If updated recently
                if time.time() - state.get("last_update", 0) < 3600:
                    return True
            return False

    def update_from_headers(self, key_id, remaining_req=None):
        """Update actual remaining from GitHub/OpenAI headers."""
        if remaining_req is None: return
        with self._lock:
            state = self._get_key_state(key_id, "GitHub")
            # We skip local decrementing if we have actual server data
            # Adjust daily count based on what's left if we knew the limit, 
            # but usually we just want to pring the 'remaining' value.
            state["server_remaining"] = remaining_req
            state["last_update"] = time.time()

    def get_status(self, key_id, provider="Gemini"):
        with self._lock:
            state = self._get_key_state(key_id, provider)
            limits = self.LIMITS.get(provider, {"RPM": 15, "RPD": 1500})
            
            # For GitHub, if we have server remaining, use it
            if provider == "GitHub" and "server_remaining" in state:
                return f"{state['server_remaining']} left (Server)"
            
            rem_rpm = max(0, limits["RPM"] - state["minute_count"])
            rem_rpd = max(0, limits["RPD"] - state["daily_count"])
            
            return f"{rem_rpm}/{limits['RPM']} RPM | {rem_rpd} Daily"

def get_quota_mgr():
    return QuotaManager()
