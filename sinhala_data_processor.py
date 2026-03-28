"""
Sinhala Data Processor - Efficient Tool for Processing Sinhala Police Reports
Automatically translates, categorizes, and generates both Security and General reports
"""

import os
import json
from ai_engine_manager import AIEngineManager
from web_report_engine_v2 import generate_security_report, html_to_pdf as security_pdf
from general_report_engine import generate_general_report, html_to_pdf as general_pdf


class SinhalaDataProcessor:
    """Process Sinhala incident data and generate reports."""
    
    def __init__(self):
        self.ai_manager = AIEngineManager()
        self.security_incidents = []
        self.general_incidents = []
    
    def validate_incident_data(self, incident_data):
        """
        Validate that all required data is present and correctly formatted.
        
        Returns:
            dict with validation results
        """
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["station", "body", "hierarchy", "province"]
        for field in required_fields:
            if not incident_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate station name
        station = incident_data.get("station", "")
        if station and station.isupper():
            # Good - station names should be uppercase
            pass
        elif station:
            warnings.append(f"Station name should be uppercase: {station}")
        
        # Validate province
        valid_provinces = [
            "WESTERN", "SABARAGAMUWA", "SOUTHERN", "UVA", "CENTRAL",
            "NORTH WESTERN", "NORTH CENTRAL", "EASTERN", "NORTHERN"
        ]
        province = incident_data.get("province", "").upper()
        if province not in valid_provinces:
            errors.append(f"Invalid province: {province}. Must be one of: {', '.join(valid_provinces)}")
        
        # Validate hierarchy
        hierarchy = incident_data.get("hierarchy", [])
        if len(hierarchy) != 2:
            errors.append(f"Hierarchy must have exactly 2 elements: ['DIG District', 'Division']. Got: {hierarchy}")
        else:
            if not hierarchy[0].startswith("DIG "):
                warnings.append(f"First hierarchy element should start with 'DIG ': {hierarchy[0]}")
            if not hierarchy[1].endswith(" Div."):
                warnings.append(f"Second hierarchy element should end with ' Div.': {hierarchy[1]}")
        
        # Validate reference code
        reference = incident_data.get("reference", "")
        if reference:
            if not (reference.startswith("CTM.") or reference.startswith("OTM.")):
                warnings.append(f"Reference code should start with CTM. or OTM.: {reference}")
        else:
            warnings.append("Missing reference code (CTM.XXX or OTM.XXX)")
        
        # Validate body length
        body = incident_data.get("body", "")
        word_count = len(body.split())
        if word_count < 50:
            warnings.append(f"Body text too short ({word_count} words). Should be 100-300 words.")
        elif word_count > 350:
            warnings.append(f"Body text too long ({word_count} words). Should be 100-300 words.")
        
        # Check for important details in body
        if body:
            if "aged" not in body.lower():
                warnings.append("Body text missing age information")
            if "#" not in body:
                warnings.append("Body text missing house number (# XX format)")
            if "TP " not in body and "phone" not in body.lower():
                warnings.append("Body text missing phone number")
            if "Rs." not in body and "cash" not in body.lower():
                # Only warning if it's a theft/robbery case
                incident_type = incident_data.get("incident_type", "").lower()
                if "theft" in incident_type or "robbery" in incident_type or "burglary" in incident_type:
                    warnings.append("Body text missing monetary value for theft case")
        
        # Validate persons array
        persons = incident_data.get("persons", [])
        if not persons:
            warnings.append("No persons extracted. Should have at least victim/complainant/suspect.")
        else:
            for i, person in enumerate(persons):
                if not person.get("name"):
                    warnings.append(f"Person {i+1} missing name")
                if not person.get("age"):
                    warnings.append(f"Person {i+1} missing age")
                if not person.get("role"):
                    warnings.append(f"Person {i+1} missing role (victim/suspect/complainant)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": 100 - (len(errors) * 20) - (len(warnings) * 5)
        }
    
    def process_sinhala_text(self, sinhala_text, incident_type_hint=None):
        """
        Process Sinhala text and extract incident data.
        
        Args:
            sinhala_text: Raw Sinhala incident text
            incident_type_hint: Optional hint (e.g., "arms", "theft", "rape", "accident")
        
        Returns:
            dict with incident data
        """
        
        prompt = f"""You are a Sinhala to English translator for Sri Lankan Police reports.

CRITICAL REQUIREMENTS - YOU MUST FOLLOW EXACTLY:
1. Extract EVERY name mentioned (victims, suspects, complainants, witnesses)
2. Extract EVERY age mentioned
3. Extract EVERY address with house numbers (# XX format)
4. Extract EVERY phone number (format: XXX-XXXXXXX)
5. Extract EVERY quantity (money, weights, counts)
6. Extract EVERY vehicle number
7. Identify the correct PROVINCE from the DIG District
8. Identify the correct POLICE STATION name
9. Identify the correct DIG DISTRICT and DIVISION

SINHALA TEXT TO TRANSLATE:
{sinhala_text}

PROVINCE MAPPING (USE THIS TO IDENTIFY PROVINCE):
- DIG Colombo/Gampaha/Kalutara District → WESTERN Province
- DIG Kegalle/Ratnapura District → SABARAGAMUWA Province
- DIG Galle/Matara/Hambantota District → SOUTHERN Province
- DIG Badulla/Monaragala District → UVA Province
- DIG Kandy/Matale/Nuwara-Eliya District → CENTRAL Province
- DIG Kurunegala/Puttalam District → NORTH WESTERN Province
- DIG Anuradhapura/Polonnaruwa District → NORTH CENTRAL Province
- DIG Ampara/Batticaloa/Trincomalee District → EASTERN Province
- DIG Jaffna/Kilinochchi/Mannar/Mullaitivu/Vavuniya/Wanni District → NORTHERN Province

OUTPUT FORMAT (JSON):
{{
    "station": "EXACT POLICE STATION NAME IN ENGLISH",
    "incident_type": "theft/homicide/rape/accident/arms/narcotics/etc",
    "summary": "Brief summary (10-15 words)",
    "body": "Full detailed narrative in English (100-300 words). MUST include: ALL names with titles (Rev./Mr./Mrs.), ALL ages, ALL complete addresses with house numbers (# XX), ALL phone numbers (XXX-XXXXXXX), ALL quantities with units (Rs. X/=, X sovereigns, Xg), ALL vehicle numbers, date and time, location, investigation status, motive.",
    "hierarchy": ["DIG [District Name] District", "[Division Name] Div."],
    "reference": "CTM.XXX or OTM.XXX (extract from text)",
    "province": "PROVINCE NAME (use mapping above)",
    "date_time": "exact date and time from text",
    "location": "complete location with house number if available",
    "persons": [
        {{
            "name": "Full Name with Title",
            "age": 00,
            "gender": "male/female",
            "role": "victim/suspect/complainant/witness",
            "address": "complete address with house number",
            "phone": "XXX-XXXXXXX if available",
            "occupation": "occupation if mentioned"
        }}
    ],
    "values": {{
        "cash": "Rs. X/= if mentioned",
        "items": "detailed description with quantities"
    }},
    "vehicles": ["vehicle numbers with # symbol"]
}}

TRANSLATION RULES:
1. Names: Translate phonetically (e.g., සිල්වා → Silva, පෙරේරා → Perera)
2. Titles: Rev. (හාමුදුරුවෝ), Mr./Mrs. (මහතා/මහත්මිය)
3. Ages: Extract exact numbers
4. Addresses: Keep house numbers as # XX format
5. Phone numbers: Keep as XXX-XXXXXXX format
6. Money: Keep as Rs. X/= format
7. Weights: Keep units (g, kg, sovereigns)
8. Vehicle numbers: Keep as shown (e.g., WP BAA 1234)

BODY TEXT FORMAT (100-300 words):
"A case of [incident type] was reported to the police station. The offence took place [date/time] at [complete address with house number]. [Victim details: name, age, gender, occupation, address, phone]. [Suspect details: name, age, gender, occupation, address OR "Suspect: Unknown"]. [Stolen/recovered items with quantities]. [Investigation status]. [Motive if applicable]. ([Reference code])"

EXAMPLE BODY:
"A case of a theft of gold jewellery (05 sovereigns) valued Rs. 1,975,000/= was reported to the police station. The offence took place on the 17th of March 2026 between 0430 hrs and 0500 hrs at # 18/48, Induvil west, Induvil, Chunnakam. Complainant named S. Sarwalogeshwari, (TP 077-5692523). Suspect: Unknown. The stolen jewellery not recovered and investigations in process. Motive: For illegal gain. (CTM.524)"

RESPOND WITH ONLY THE JSON, NO OTHER TEXT OR MARKDOWN.

        try:
            response = self.ai_manager.generate_text(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            if response["success"]:
                # Parse JSON response
                json_text = response["text"].strip()
                # Remove markdown code blocks if present
                if json_text.startswith("```"):
                    json_text = json_text.split("```")[1]
                    if json_text.startswith("json"):
                        json_text = json_text[4:]
                json_text = json_text.strip()
                
                incident_data = json.loads(json_text)
                return {"success": True, "data": incident_data}
            else:
                return {"success": False, "error": response.get("error", "Unknown error")}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def categorize_incident(self, incident_data):
        """
        Categorize incident into Security or General report.
        
        Returns:
            "security" or "general"
        """
        incident_type = incident_data.get("incident_type", "").lower()
        body = incident_data.get("body", "").lower()
        summary = incident_data.get("summary", "").lower()
        
        # Security Report keywords
        security_keywords = [
            "arms", "ammunition", "explosive", "detonator", "gunpowder",
            "firearm", "shotgun", "weapon", "gun", "bullet", "grenade",
            "subversive", "terrorist", "security threat"
        ]
        
        # Check if it's a security incident
        for keyword in security_keywords:
            if keyword in incident_type or keyword in body or keyword in summary:
                return "security"
        
        # Everything else goes to General Report
        return "general"
    
    def add_incident(self, sinhala_text, incident_type_hint=None):
        """
        Add a single incident from Sinhala text.
        
        Returns:
            dict with status and processed data
        """
        print(f"\n{'='*80}")
        print("Processing Sinhala incident...")
        print(f"{'='*80}")
        
        # Process the text
        result = self.process_sinhala_text(sinhala_text, incident_type_hint)
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            return result
        
        incident_data = result["data"]
        
        # Validate the extracted data
        validation = self.validate_incident_data(incident_data)
        
        print(f"\n📊 Data Quality Score: {validation['score']}/100")
        
        if validation["errors"]:
            print(f"\n❌ ERRORS ({len(validation['errors'])}):")
            for error in validation["errors"]:
                print(f"   • {error}")
        
        if validation["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(validation['warnings'])}):")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
        
        if not validation["valid"]:
            print("\n❌ Data validation failed. Please check the Sinhala text and try again.")
            return {"success": False, "error": "Validation failed", "validation": validation}
        
        # Categorize
        category = self.categorize_incident(incident_data)
        
        # Add to appropriate list
        if category == "security":
            self.security_incidents.append(incident_data)
            print(f"\n✅ Added to SECURITY REPORT")
        else:
            self.general_incidents.append(incident_data)
            print(f"\n✅ Added to GENERAL REPORT")
        
        print(f"\n📋 Extracted Details:")
        print(f"   Station: {incident_data.get('station', 'Unknown')}")
        print(f"   Type: {incident_data.get('incident_type', 'Unknown')}")
        print(f"   Province: {incident_data.get('province', 'Unknown')}")
        print(f"   Hierarchy: {' → '.join(incident_data.get('hierarchy', []))}")
        print(f"   Reference: {incident_data.get('reference', 'Unknown')}")
        
        # Show persons extracted
        persons = incident_data.get("persons", [])
        if persons:
            print(f"\n👥 Persons Extracted ({len(persons)}):")
            for person in persons:
                print(f"   • {person.get('name', 'Unknown')} (Age: {person.get('age', '?')}, Role: {person.get('role', '?')})")
        
        # Show values extracted
        values = incident_data.get("values", {})
        if values.get("cash") or values.get("items"):
            print(f"\n💰 Values Extracted:")
            if values.get("cash"):
                print(f"   • Cash: {values['cash']}")
            if values.get("items"):
                print(f"   • Items: {values['items']}")
        
        # Show vehicles extracted
        vehicles = incident_data.get("vehicles", [])
        if vehicles:
            print(f"\n🚗 Vehicles Extracted ({len(vehicles)}):")
            for vehicle in vehicles:
                print(f"   • {vehicle}")
        
        return {"success": True, "category": category, "data": incident_data, "validation": validation}
    
    def add_batch(self, sinhala_texts):
        """
        Add multiple incidents at once.
        
        Args:
            sinhala_texts: List of Sinhala text strings
        
        Returns:
            Summary of processed incidents
        """
        results = {
            "total": len(sinhala_texts),
            "security": 0,
            "general": 0,
            "errors": 0
        }
        
        for i, text in enumerate(sinhala_texts, 1):
            print(f"\n[{i}/{len(sinhala_texts)}] Processing...")
            result = self.add_incident(text)
            
            if result["success"]:
                if result["category"] == "security":
                    results["security"] += 1
                else:
                    results["general"] += 1
            else:
                results["errors"] += 1
        
        return results
    
    def generate_reports(self, date_range, output_prefix="Report"):
        """
        Generate both Security and General reports.
        
        Args:
            date_range: Date range string (e.g., "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026")
            output_prefix: Prefix for output files
        
        Returns:
            dict with file paths
        """
        print(f"\n{'='*80}")
        print("GENERATING REPORTS")
        print(f"{'='*80}")
        
        files = {}
        
        # Generate Security Report
        if self.security_incidents:
            print(f"\n📋 Security Report: {len(self.security_incidents)} incidents")
            
            # Categorize security incidents (all go to Category 03)
            provinces_dict = {}
            for inc in self.security_incidents:
                prov = inc.get("province", "UNKNOWN").upper()
                if prov not in provinces_dict:
                    provinces_dict[prov] = []
                provinces_dict[prov].append(inc)
            
            provinces_list = [{"name": p, "incidents": incs} for p, incs in provinces_dict.items()]
            
            security_data = {
                "date_range": date_range,
                "sections": [
                    {"title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:", "provinces": []},
                    {"title": "02. SUBVERSIVE ACTIVITIES:", "provinces": []},
                    {"title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:", "provinces": provinces_list}
                ]
            }
            
            security_html = f"{output_prefix}_Security.html"
            security_pdf_file = f"{output_prefix}_Security.pdf"
            
            generate_security_report(security_data, security_html)
            security_pdf(security_html, security_pdf_file)
            
            files["security_html"] = security_html
            files["security_pdf"] = security_pdf_file
            
            print(f"  ✅ {security_html}")
            print(f"  ✅ {security_pdf_file}")
        else:
            print("\n⚠️  No security incidents to report")
        
        # Generate General Report
        if self.general_incidents:
            print(f"\n📋 General Report: {len(self.general_incidents)} incidents")
            
            from general_report_processor import GeneralReportProcessor
            processor = GeneralReportProcessor()
            
            general_html = f"{output_prefix}_General.html"
            general_pdf_file = f"{output_prefix}_General.pdf"
            
            processor.generate_report(
                incidents=self.general_incidents,
                date_range=date_range,
                output_html=general_html,
                output_pdf=general_pdf_file
            )
            
            files["general_html"] = general_html
            files["general_pdf"] = general_pdf_file
            
            print(f"  ✅ {general_html}")
            print(f"  ✅ {general_pdf_file}")
        else:
            print("\n⚠️  No general incidents to report")
        
        print(f"\n{'='*80}")
        print("✅ REPORTS GENERATED SUCCESSFULLY!")
        print(f"{'='*80}")
        
        return files
    
    def save_data(self, filename="processed_data.json"):
        """Save processed data to JSON file."""
        data = {
            "security_incidents": self.security_incidents,
            "general_incidents": self.general_incidents
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Data saved to: {filename}")
    
    def load_data(self, filename="processed_data.json"):
        """Load processed data from JSON file."""
        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}")
            return False
        
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.security_incidents = data.get("security_incidents", [])
        self.general_incidents = data.get("general_incidents", [])
        
        print(f"\n💾 Data loaded from: {filename}")
        print(f"  • Security incidents: {len(self.security_incidents)}")
        print(f"  • General incidents: {len(self.general_incidents)}")
        
        return True
    
    def print_summary(self):
        """Print summary of processed data."""
        print(f"\n{'='*80}")
        print("PROCESSED DATA SUMMARY")
        print(f"{'='*80}")
        print(f"Security Incidents: {len(self.security_incidents)}")
        print(f"General Incidents: {len(self.general_incidents)}")
        print(f"Total: {len(self.security_incidents) + len(self.general_incidents)}")
        print(f"{'='*80}")


def interactive_mode():
    """Interactive mode for adding incidents one by one."""
    processor = SinhalaDataProcessor()
    
    print("""
================================================================================
                   SINHALA DATA PROCESSOR - INTERACTIVE MODE
================================================================================
  Paste Sinhala incident text and press Enter twice to process
  Commands:
    'done' - Finish and generate reports
    'summary' - Show current summary
    'save' - Save data to file
    'load' - Load data from file
    'quit' - Exit without generating reports
================================================================================
    """)
    
    while True:
        print("\n" + "-"*80)
        print("Paste Sinhala incident text (or command):")
        print("-"*80)
        
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        
        text = "\n".join(lines).strip()
        
        if not text:
            continue
        
        # Check for commands
        if text.lower() == "done":
            if len(processor.security_incidents) + len(processor.general_incidents) == 0:
                print("\n⚠️  No incidents to process!")
                continue
            
            date_range = input("\nEnter date range (e.g., From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026): ")
            output_prefix = input("Enter output file prefix (default: Report): ").strip() or "Report"
            
            processor.generate_reports(date_range, output_prefix)
            break
        
        elif text.lower() == "summary":
            processor.print_summary()
            continue
        
        elif text.lower() == "save":
            filename = input("Enter filename (default: processed_data.json): ").strip() or "processed_data.json"
            processor.save_data(filename)
            continue
        
        elif text.lower() == "load":
            filename = input("Enter filename (default: processed_data.json): ").strip() or "processed_data.json"
            processor.load_data(filename)
            continue
        
        elif text.lower() == "quit":
            print("\n👋 Exiting...")
            break
        
        # Process the incident
        processor.add_incident(text)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        print("""
================================================================================
                        SINHALA DATA PROCESSOR
================================================================================

USAGE:
  python sinhala_data_processor.py interactive    # Interactive mode
  
  Or use in your Python code:
  
  from sinhala_data_processor import SinhalaDataProcessor
  
  processor = SinhalaDataProcessor()
  
  # Add single incident
  processor.add_incident(sinhala_text)
  
  # Add multiple incidents
  processor.add_batch([text1, text2, text3])
  
  # Generate reports
  processor.generate_reports(
      date_range="From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026",
      output_prefix="March17_18"
  )
  
  # Save/load data
  processor.save_data("my_data.json")
  processor.load_data("my_data.json")

FEATURES:
  * Automatic Sinhala to English translation
  * Automatic categorization (Security vs General)
  * Extracts all details (names, ages, addresses, quantities)
  * Generates both Security and General reports
  * Save/load functionality for batch processing
  * Interactive mode for easy data entry

Run 'python sinhala_data_processor.py interactive' to start!
        """)

