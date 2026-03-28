import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaTranslator:
    """
    High-Fidelity Sinhala-to-English Translator for Sri Lanka Police Reports.
    Uses local Ollama gpt-oss:120b-cloud engine with Master Data Architect v2.8 prompt.
    """
    
    def __init__(self, model="gpt-oss:120b-cloud", url="http://localhost:11434/api/generate"):
        self.model = model
        self.url = url
        self.timeout = 600  # 10 minute timeout for 120B model
        
    def translate_section(self, section_name, sinhala_text):
        """
        Translates a single police report section into official English format.
        """
        if not sinhala_text or sinhala_text.strip().lower() == "nil":
            return "Nil"
            
        logger.info(f"Translating section: {section_name}...")
        
        prompt = f"""
### INSTRUCTION: MASTER DATA ARCHITECT (Institutional Reporting v3.0)
You are an expert translator for the Sri Lanka Police Department. 
Your task is to translate the following Sinhala incident data into official, high-fidelity English.

### STYLE REFERENCE (MANDATORY FORMAT):
Each incident MUST follow this exact structure:
[STATION NAME IN CAPS]: (Short Summary of Incident in Parentheses) Detailed Narrative in English ... (Reference Code)

#### EXAMPLE:
EMBILIPITIYA: (Arrest of suspects along with a detonator and gunpowder) On the 17th March 2026, acting on an information received through the 1-1-9 project, police arrested a Buddhist monk named Rev. Embilipitiye Indrarathana thero, aged 68, the chief incumbent of the Sri Darshanagiri viharaya... (OTM.1421)

### DATA FIDELITY RULES:
1. DATA PRESERVATION: Retain all names, ages, dates, and registration numbers (e.g., OTM/CTM numbers) exactly.
2. HIERARCHY: Prepend the Hierarchy (S/DIG Sabaragamuwa, District, Division) if clearly identifiable, but the CORE narrative must follow the Style Reference above.
3. LANGUAGE: Use professional, formal police terminology (e.g., "acting on information," "produced before the Magistrate," "seized," "remanded").
4. OMISSION: Do not omit any factual detail. If an incident has multiple suspects, list all.

### TARGET SECTION: {section_name}
### SINHALA RAW DATA:
{sinhala_text}

### OFFICIAL ENGLISH OUTPUT:
"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.1
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(self.url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            elapsed = time.time() - start_time
            logger.info(f"Translation completed in {elapsed:.2f}s")
            
            return response.json().get('response', '').strip()
            
        except Exception as e:
            logger.error(f"Translation failed for {section_name}: {str(e)}")
            return f"[ERROR: Translation failed - {str(sinhala_text[:100])}...]"

if __name__ == "__main__":
    # Quick test
    translator = OllamaTranslator()
    test_sinhala = "ඇඹිලිපිටිය: (පුපුරණ ද්‍රව්‍ය සමඟ සැකකරුවන් අත්අඩංගුවට ගැනීම) 2026 මාර්තු 17 වන දින..."
    print(translator.translate_section("Security Matters", test_sinhala))
