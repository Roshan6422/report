import os
import json
import requests

class GeminiProClient:
    def __init__(self, api_key, model_name="gemini-1.5-flash"):
        # We use FLASH as it's more widely available and faster for high-volume sections
        self.api_key = api_key
        self.model_name = model_name
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    def structure_section(self, section_title, section_text, report_type="General"):
        prompt = f"""
### INSTITUTIONAL COMMAND: MASTER DATA ARCHITECT (v2.5)
Translate this police section to professional English ({report_type} Situation Report).
Match the "Official Intelligence Division" standard.

CRITICAL REQUIREMENTS:
1. HEADER STYLE: Use "Confidential - IG's Information Division" header style.
2. HIERARCHY: Format headers as [STATION]: S/DIG [Province], DIG [District], [Division].
3. INCIDENT COUNT: Zero omission. Count every single entry in the source.
4. MEDICAL/LEGAL: Use standard police terminology for injuries and forensic details.
5. NO SUMMARIES: Provide full narratives for every incident.

### SECTION: {section_title}
### SINHALA TEXT:
{section_text}

### OUTPUT FORMAT:
## {section_title}
### [STATION NAME]
- **Hierarchy**: S/DIG [Province], DIG [District], [Division]
- **Narrative**: [Full descriptive narrative]
- **Reference**: (CTM.XXX)MS
"""
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                res_json = response.json()
                return res_json['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"❌ Gemini API Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"❌ Gemini Connection Failed: {str(e)}"

if __name__ == "__main__":
    # Internal tester
    pass
