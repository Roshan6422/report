import os
import requests
import json
import time

class FastApiClient:
    """Unified client for Fast APIs like GitHub Models and Groq."""
    
    def __init__(self, api_key=None, provider="github"):
        self.api_key = api_key or os.getenv("FAST_API_KEY")
        self.provider = provider
        
        if self.provider == "github":
            self.base_url = "https://models.inference.ai.azure.com/chat/completions"
            self.model = "gpt-4o-mini" # Best for Sinhala and extremely fast
        elif self.provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.1-70b-versatile" # Fastest
        else:
            self.base_url = "https://models.inference.ai.azure.com/chat/completions"
            self.model = "gpt-4o-mini"
            
    def structure_section(self, section_title, section_text, report_type="General"):
        prompt = f"""
        ### INSTITUTIONAL ROLE:
        You are the "Antigravity Data Processor & Translator," a high-precision Data Architect specialized for the Inspector General of Sri Lanka Police.
        Your mission is to achieve 100% data fidelity by translating and structuring the following incident report.

        ### OUTPUT STRUCTURE (MANDATORY):
        Start with: `## {section_title}`
        For every incident:
        ### [STATION]
        - **Hierarchy**: S/DIG [Province], DIG [District], [Division]
        - **Narrative**: [Professional Police Narration translated to Formal English].
        - **Reference**: (CTM.553)MS

        ### INPUT TEXT (PROCESS THIS NOW):
        {section_text}
        """
        return self._call_api(prompt)

    def _call_api(self, prompt):
        if not self.api_key:
            return "❌ API Key Missing: Please provide a valid FAST_API_KEY (GitHub PAT or Groq API Key)"
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            if self.provider == "github":
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a professional Sinhala to English translator for Police documents."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3, # low temp for better translation precision
                    "max_tokens": 4096
                }
            else:
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a professional Sinhala to English translator for Police documents."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 8192
                }
                
            res = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            return f"❌ {self.provider.upper()} API Error: {res.status_code} - {res.text}"
        except Exception as e:
            return f"❌ {self.provider.upper()} Connection Failed: {str(e)}"
