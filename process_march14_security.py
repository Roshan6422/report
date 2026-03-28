import os
import sys
import json
import logging
from datetime import datetime

# Institutional Pipeline Imports
from translator_pipeline import extract_text_with_layout, pre_process_expert_layout
from sinhala_section_splitter import split_by_sections
from deepseek_client import DeepSeekClient
from markdown_parser import parse_high_fidelity_markdown
from web_report_engine import generate_html_report, html_to_pdf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class March14SecurityReportGenerator:
    """
    Processes the March 14, 2026 Sinhala PDF and generates English Security Report
    matching the exact institutional format (100% fidelity).
    """
    
    def __init__(self, output_dir="D:/PROJECTS/ha"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Instantiate with no key to force local Ollama as per institutional standard
        self.assistant = DeepSeekClient(api_key=None)
        
        # Security report sections mapping (Institutional Standard)
        self.SECURITY_SECTIONS_MAP = {
            "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST": ["01. ත්‍රස්තවාදී ක්‍රියාකාරකම්"],
            "02. SUBVERSIVE ACTIVITIES": ["03. උද්ඝෝෂණ", "29. වෙනත් විශේෂ සිදුවීම්"],
            "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES": ["02. අවි ආයුධ සොයාගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ)"]
        }

    def process_march14_pdf(self, pdf_path):
        """Main orchestrator for generating the March 14 Security Report."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
            
        logger.info(f"Step 1: Extracting text from {pdf_path}...")
        raw_text = extract_text_with_layout(pdf_path)
        if not raw_text:
            logger.error("Failed to extract text from PDF")
            return None
            
        logger.info("Step 2: Splitting into 29 Sinhala categories...")
        # Pre-process layout for cleaner splitting
        clean_text = pre_process_expert_layout(raw_text)
        all_sinhala_sections = split_by_sections(clean_text, "Situation")
        
        # Group Sinhala sections according to the Security Report mapping
        grouped_sections = {}
        for eng_title, sin_titles in self.SECURITY_SECTIONS_MAP.items():
            combined_body = ""
            for sin_title, sin_body in all_sinhala_sections:
                if any(st in sin_title for st in sin_titles):
                    if sin_body.strip().lower() not in ["nil", "නැත", ""]:
                        combined_body += sin_body + "\n\n"
            grouped_sections[eng_title] = combined_body.strip()
            
        logger.info("Step 3: Translating and structuring via Ollama (DeepSeek 120B)...")
        final_structured_sections = []
        
        for eng_title, sinhala_content in grouped_sections.items():
            if not sinhala_content:
                logger.info(f"Section {eng_title}: Nil")
                final_structured_sections.append({"title": eng_title, "provinces": []})
                continue
                
            logger.info(f"Processing section: {eng_title}")
            # Use the official structuring prompt from DeepSeekClient
            md_result = self.assistant.structure_section(eng_title, sinhala_content, "Security")
            
            # Parse the structured markdown back into the dictionary format expected by web_report_engine
            section_data = parse_high_fidelity_markdown(md_result)
            
            # Ensure the title matches our official numbering
            if section_data.get("sections"):
                processed_sec = section_data["sections"][0]
                processed_sec["title"] = eng_title
                final_structured_sections.append(processed_sec)
            else:
                # Fallback if parser fails
                final_structured_sections.append({"title": eng_title, "provinces": []})

        # Assemble the final data object for the HTML engine
        report_data = {
            "report_type": "Security",
            "date_range": "From 0400 hrs. on 13<sup>th</sup> March 2026 to 0400 hrs. on 14<sup>th</sup> March 2026",
            "sections": final_structured_sections
        }
        
        logger.info("Step 4: Generating Pixel-Perfect HTML and PDF...")
        base_name = "Security_Report_14_March_2026"
        html_path = os.path.join(self.output_dir, f"{base_name}.html")
        pdf_path = os.path.join(self.output_dir, f"{base_name}.pdf")
        
        # Generate the institutional HTML
        generate_html_report(report_data, html_path, report_type="Security")
        
        # Convert to high-fidelity PDF
        success = html_to_pdf(html_path, pdf_path)
        
        if success:
            logger.info(f"✓ SUCCESS: Security Report generated at {pdf_path}")
            return pdf_path
        else:
            logger.error("Failed to convert HTML to PDF")
            return None

def main():
    pdf_path = "uploads/2026.03.14 දින සිදුවිම් වාර්තාව.pdf"
    generator = March14SecurityReportGenerator(output_dir="D:/PROJECTS/ha")
    result = generator.process_march14_pdf(pdf_path)
    
    if result:
        print(f"\nFinal PDF Path: {result}")
    else:
        print("\nGeneration failed. Check logs.")

if __name__ == "__main__":
    main()

