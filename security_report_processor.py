"""
security_report_processor.py — Enhanced Security Report Processor
==================================================================
Processes security incidents with detailed narrative format matching
official standards.
"""

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from openrouter_client import OpenRouterClient
from security_report_prompts import get_security_prompt, enhance_incident_quality
from web_report_engine_v2 import generate_security_report, html_to_pdf


class SecurityReportProcessor:
    """Process security incidents with detailed narrative format."""
    
    def __init__(self, api_key=None):
        """Initialize with OpenRouter API key."""
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY", "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")
        
        self.client = OpenRouterClient(api_key)
        self.stats = {
            "incidents_processed": 0,
            "words_generated": 0,
            "api_calls": 0
        }
    
    def process_raw_incident(self, raw_text, section_type="ARMS RECOVERY"):
        """
        Convert raw incident text to detailed narrative format.
        
        Args:
            raw_text: Raw incident text (Sinhala or English)
            section_type: Type of security section
        
        Returns:
            dict with station, summary, body, hierarchy, reference
        """
        # Get appropriate prompt
        prompt = get_security_prompt(section_type)
        prompt += f"\n\nRAW INCIDENT DATA:\n{raw_text}\n\nCONVERT TO DETAILED NARRATIVE:"
        
        # Call AI
        response = self.client.chat_completion(
            prompt,
            model="deepseek/deepseek-chat",
            max_tokens=1000,
            temperature=0.7
        )
        
        self.stats["api_calls"] += 1
        self.stats["incidents_processed"] += 1
        self.stats["words_generated"] += len(response.split())
        
        # Parse response (expecting JSON format)
        try:
            incident_data = json.loads(response)
            return incident_data
        except:
            # If not JSON, treat as narrative text
            return {
                "station": "UNKNOWN",
                "summary": "Incident reported",
                "body": response,
                "hierarchy": [],
                "reference": ""
            }
    
    def enhance_incident(self, incident_text):
        """
        Enhance an existing incident to match professional standards.
        
        Args:
            incident_text: Existing incident text
        
        Returns:
            Enhanced incident text
        """
        prompt = enhance_incident_quality(incident_text)
        
        response = self.client.chat_completion(
            prompt,
            model="deepseek/deepseek-chat",
            max_tokens=800,
            temperature=0.5
        )
        
        self.stats["api_calls"] += 1
        
        return response.strip()
    
    def process_security_section(self, section_data, section_type):
        """
        Process an entire security section with multiple incidents.
        
        Args:
            section_data: List of raw incident texts
            section_type: Type of section (VERY IMPORTANT, SUBVERSIVE, ARMS)
        
        Returns:
            Structured section data
        """
        processed_incidents = []
        
        for raw_incident in section_data:
            incident = self.process_raw_incident(raw_incident, section_type)
            processed_incidents.append(incident)
        
        return processed_incidents
    
    def generate_full_report(self, report_data, output_dir="outputs"):
        """
        Generate complete Security Situation Report.
        
        Args:
            report_data: dict with date_range and sections
            output_dir: Output directory for HTML/PDF
        
        Returns:
            Paths to generated HTML and PDF files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join(output_dir, f"Security_Report_{timestamp}.html")
        pdf_path = os.path.join(output_dir, f"Security_Report_{timestamp}.pdf")
        
        # Generate HTML
        generate_security_report(report_data, html_path)
        
        # Convert to PDF
        html_to_pdf(html_path, pdf_path)
        
        return html_path, pdf_path
    
    def print_stats(self):
        """Print processing statistics."""
        print("\n" + "="*60)
        print("SECURITY REPORT PROCESSING STATISTICS")
        print("="*60)
        print(f"Incidents Processed:  {self.stats['incidents_processed']}")
        print(f"Words Generated:      {self.stats['words_generated']}")
        print(f"API Calls Made:       {self.stats['api_calls']}")
        print(f"Avg Words/Incident:   {self.stats['words_generated'] // max(self.stats['incidents_processed'], 1)}")
        print("="*60)


def example_usage():
    """Example of how to use the SecurityReportProcessor."""
    
    # Initialize processor
    processor = SecurityReportProcessor()
    
    # Example raw incident data (could be from PDF extraction)
    raw_incidents = [
        """
        Embilipitiya police arrested monk with detonator and gunpowder.
        Rev. Indrarathana thero, 68 years, chief of Darshanagiri temple.
        Also arrested N.U. Samanchandra, 56, from Mayuragama.
        Found electric detonator and 80g gunpowder.
        Digging tunnel for treasure hunting.
        Court date: 18th March 2026.
        Reference: OTM.1421
        """,
        """
        Udawalawa police arrested person with illegal firearm.
        K.T. Ranathunga, 53, from Panahaduwa.
        Locally made muzzle loading firearm seized.
        Investigations ongoing.
        Reference: OTM.1445
        """
    ]
    
    # Process incidents
    print("Processing incidents...")
    processed = []
    for raw in raw_incidents:
        incident = processor.process_raw_incident(raw, "ARMS RECOVERY")
        processed.append(incident)
        print(f"\n✓ Processed: {incident.get('station', 'UNKNOWN')}")
    
    # Build report data structure
    report_data = {
        "date_range": "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026",
        "sections": [
            {
                "title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:",
                "provinces": []
            },
            {
                "title": "02. SUBVERSIVE ACTIVITIES:",
                "provinces": []
            },
            {
                "title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:",
                "provinces": [
                    {
                        "name": "SABARAGAMUWA",
                        "incidents": processed
                    }
                ]
            }
        ]
    }
    
    # Generate report
    print("\nGenerating Security Situation Report...")
    html_path, pdf_path = processor.generate_full_report(report_data)
    
    print(f"\n✅ HTML Report: {html_path}")
    print(f"✅ PDF Report:  {pdf_path}")
    
    # Print statistics
    processor.print_stats()


if __name__ == "__main__":
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  SECURITY REPORT PROCESSOR".center(58) + "█")
    print("█" + "  Detailed Narrative Format Generator".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60 + "\n")
    
    example_usage()
