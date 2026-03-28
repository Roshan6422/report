import json
import os
import re
import logging
import time
from ollama_translator import OllamaTranslator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityReportGenerator:
    """
    Orchestrates the filtering, chunking, and translation of 3-section institutional security reports.
    """
    
    def __init__(self, input_json, output_dir="d:/PROJECTS/ha"):
        self.input_json = input_json
        self.output_dir = output_dir
        self.translator = OllamaTranslator()
        
        # Mapping User's 3 sections to 29-category IDs
        self.TARGET_MAPPING = {
            "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST": ["01. ත්‍රස්තවාදී ක්‍රියාකාරකම්"],
            "02. SUBVERSIVE ACTIVITIES": ["03. උද්ඝෝෂණ", "29. වෙනත් විශේෂ සිදුවීම්"],
            "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES": ["02. අවි ආයුධ සොයාගැනීම"]
        }

    def split_into_incidents(self, text):
        """
        Splits a section body into individual incidents based on numbering (1., 2., 3., etc.)
        """
        if not text or text.strip().lower() == "nil":
            return []
            
        # Regex to match "1. ", "2. ", etc. at the start of segments
        # Using a lookahead to keep the number with the incident
        incidents = re.split(r'\n\s*(?=\d+\.\s+)', text)
        
        # Filter out empty or header-only strings
        valid_incidents = [inc.strip() for inc in incidents if len(inc.strip()) > 10]
        return valid_incidents

    def generate(self, report_date="2026-03-21"):
        if not os.path.exists(self.input_json):
            logger.error(f"Input file not found: {self.input_json}")
            return
            
        with open(self.input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        sections = data.get('sections', [])
        final_report = []
        
        # Institutional Header
        header = f"""# S/DIG SABARAGAMUWA PROVINCE
## Institutional Security Summary - {report_date}

---
"""
        final_report.append(header)
        
        for english_title, sinhala_titles in self.TARGET_MAPPING.items():
            combined_sinhala = ""
            for s in sections:
                if any(st in s['title'] for st in sinhala_titles):
                    if s['body'] and s['body'].strip().lower() != "nil":
                        combined_sinhala += s['body'] + "\n\n"
            
            final_report.append(f"## {english_title}\n")
            
            if not combined_sinhala.strip() or combined_sinhala.strip().lower() == "nil":
                final_report.append("Nil\n\n---\n")
                continue
            
            # SPLIT INTO CHUNKS FOR OLLAMA STABILITY
            chunks = self.split_into_incidents(combined_sinhala)
            
            if not chunks:
                # If no numbering found, treat entire section as one chunk (risky but fallback)
                chunks = [combined_sinhala]
                
            logger.info(f"Section '{english_title}' split into {len(chunks)} incidents.")
            
            for idx, chunk in enumerate(chunks, 1):
                logger.info(f"Translating item {idx}/{len(chunks)} of {english_title}...")
                
                # Single incident translation
                translated_item = self.translator.translate_section(english_title, chunk)
                
                final_report.append(f"{translated_item}\n\n")
            
            final_report.append("---\n")
            
        output_name = f"Security_Report_{report_date.replace('.', '_')}.md"
        output_path = os.path.join(self.output_dir, output_name)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(final_report)
            
        logger.info(f"Security report generated: {output_path}")
        return output_path

if __name__ == "__main__":
    # Process March 21st
    gen = SecurityReportGenerator("d:/PROJECTS/ha/21_mar_29cat_split.json")
    gen.generate("21.03.2026")
