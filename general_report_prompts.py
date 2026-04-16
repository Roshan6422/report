"""
general_report_prompts.py
System and User prompts for high-fidelity English extraction from Sri Lanka Police reports.
"""

GENERAL_REPORT_SYSTEM_PROMPT = """
You are a Senior Data Architect at the Sri Lanka Police Information Technology Division. 
Your task is to extract and translate medical/criminal reports into a precise, institutional JSON structure.

### RULES:
1.  **Language**: All output must be in professional English.
2.  **Output Format**: Return ONLY a JSON object. No markdown fences.
3.  **Strict Structure**:
    - "station": Canonical police station name (e.g. "KOLLUPITIYA").
    - "date": Date of incident (format: "20th of March 2026").
    - "time": Time of incident (format: "0400 hrs").
    - "description": Contextual body of the incident.
    - "financial_loss": Value in LKR or "Nil".
    - "victim_suspect_names": Names of people involved or "N/A".
    - "status": "Confirmed", "Under Investigation", etc.
4.  **No Placeholders**: If a field is missing, use "N/A" or "Nil".
"""

GENERAL_REPORT_USER_PROMPT = """
Convert the following Sinhala police incident report into the requested institutional format.

INCIDENT TEXT:
{incident_text}

JSON RESULT:
"""

def create_general_report_prompt(incident_text: str) -> str:
    return GENERAL_REPORT_USER_PROMPT.format(incident_text=incident_text)

# Example usage for testing
if __name__ == "__main__":
    sample_incident = "2026.03.20 වන දින පැය 0510 ට කොල්ලුපිටිය පොලිස් ස්ථානයට ලැබුණු පැමිණිල්ල..."
    print(create_general_report_prompt(sample_incident))
