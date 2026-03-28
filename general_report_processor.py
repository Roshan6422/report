"""
General Report Processor
Automated processing of incidents for General Situation Reports with detailed narratives
"""

from ai_engine_manager import AIEngineManager
from general_report_prompts import GENERAL_REPORT_SYSTEM_PROMPT, create_general_report_prompt
from general_report_engine import generate_general_report, html_to_pdf
import json
import re


class GeneralReportProcessor:
    """Process incidents and generate General Situation Reports."""
    
    def __init__(self):
        self.ai_manager = AIEngineManager()
    
    def generate_detailed_narrative(self, incident_data):
        """Generate detailed narrative for a single incident using AI."""
        
        # Create prompt
        user_prompt = create_general_report_prompt(incident_data)
        
        # Get AI response
        response = self.ai_manager.generate_text(
            prompt=user_prompt,
            system_prompt=GENERAL_REPORT_SYSTEM_PROMPT,
            max_tokens=500,
            temperature=0.3
        )
        
        if response["success"]:
            narrative = response["text"].strip()
            
            # Extract components
            station, summary, body, ref = self._parse_narrative(narrative)
            
            return {
                "station": station,
                "summary": summary,
                "body": body,
                "reference": ref,
                "narrative": narrative,
                "word_count": len(narrative.split())
            }
        else:
            return {
                "error": response.get("error", "Unknown error"),
                "narrative": None
            }
    
    def _parse_narrative(self, narrative):
        """Parse narrative into components."""
        
        # Extract station name (before first colon)
        station_match = re.match(r'^([A-Z\s]+):', narrative)
        station = station_match.group(1).strip() if station_match else ""
        
        # Extract summary (text in first parentheses)
        summary_match = re.search(r'\(([^)]+)\)', narrative)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        # Extract reference code (last parentheses)
        ref_match = re.search(r'\(([CO]TM\.\d+)\)\s*$', narrative)
        ref = ref_match.group(1) if ref_match else ""
        
        # Body is everything between station and reference
        body = narrative
        if station:
            body = body.split(':', 1)[1].strip()
        if ref:
            body = body.rsplit('(', 1)[0].strip()
        
        return station, summary, body, ref
    
    def process_batch(self, incidents):
        """Process multiple incidents and generate narratives."""
        
        results = []
        
        print(f"\nProcessing {len(incidents)} incidents...")
        print("=" * 80)
        
        for i, inc in enumerate(incidents, 1):
            print(f"\n[{i}/{len(incidents)}] Processing: {inc.get('station', 'Unknown')}")
            
            result = self.generate_detailed_narrative(inc)
            
            if result.get("narrative"):
                print(f"  ✓ Generated: {result['word_count']} words")
                results.append(result)
            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print(f"✅ Completed: {len(results)}/{len(incidents)} successful")
        
        return results
    
    def categorize_for_general_report(self, incidents):
        """Categorize incidents into 10 General Report sections."""
        
        sections = {
            "01. SERIOUS CRIMES COMMITTED:": [],
            "02. RAPE, SEXUAL ASSAULT & CHILD ABUSE:": [],
            "03. FATAL ACCIDENTS:": [],
            "04. POLICE OFFICERS/VEHICLES INVOLVED IN ROAD ACCIDENTS AND DAMAGES TO SRI LANKA POLICE PROPERTY:": [],
            "05. FINDING OF DEAD BODIES UNDER SUSPICIOUS CIRCUMSTANCES:": [],
            "06. SERIOUS INJURY/ ILLNESSES/ DEATHS OF POLICE OFFICERS:": [],
            "07. DETECT OF NARCOTIC AND ILLEGAL LIQUOR:": [],
            "08. ARREST OF TRI-FORCES MEMBERS:": [],
            "09. OTHER MATTERS:": [],
            "10. [RESERVED]:": []
        }
        
        for inc in incidents:
            body_lower = inc.get("body", "").lower()
            summary_lower = inc.get("summary", "").lower()
            
            # Check if it's an arrest with firearms/ammunition (goes to OTHER MATTERS)
            is_arms_arrest = any(kw in body_lower or kw in summary_lower for kw in 
                                ["arrest", "arrested"]) and any(kw in body_lower or kw in summary_lower for kw in 
                                ["firearm", "shotgun", "weapon", "ammunition", "bullet"])
            
            # 09. OTHER MATTERS - Arms/ammunition arrests
            if is_arms_arrest:
                sections["09. OTHER MATTERS:"].append(inc)
            
            # 02. Rape, Sexual Assault & Child Abuse
            elif any(kw in body_lower or kw in summary_lower for kw in 
                   ["rape", "sexual assault", "sexual abuse", "child abuse", "molestation", "indecent"]):
                sections["02. RAPE, SEXUAL ASSAULT & CHILD ABUSE:"].append(inc)
            
            # 03. Fatal Accidents
            elif "accident" in body_lower and "fatal" in body_lower:
                sections["03. FATAL ACCIDENTS:"].append(inc)
            
            # 04. Police Officers/Vehicles in Road Accidents & Damages
            elif any(kw in body_lower for kw in ["police officer", "police vehicle", "police accident", "damage to police"]):
                sections["04. POLICE OFFICERS/VEHICLES INVOLVED IN ROAD ACCIDENTS AND DAMAGES TO SRI LANKA POLICE PROPERTY:"].append(inc)
            
            # 05. Finding of Dead Bodies under Suspicious Circumstances
            elif any(kw in body_lower for kw in ["dead body", "suspicious death", "unidentified body", "suspicious circumstances"]):
                sections["05. FINDING OF DEAD BODIES UNDER SUSPICIOUS CIRCUMSTANCES:"].append(inc)
            
            # 06. Serious Injury/Illnesses/Deaths of Police Officers
            elif any(kw in body_lower for kw in ["police officer injured", "police officer death", "police officer illness", "sgoo"]):
                sections["06. SERIOUS INJURY/ ILLNESSES/ DEATHS OF POLICE OFFICERS:"].append(inc)
            
            # 07. Detect of Narcotic and Illegal Liquor
            elif any(kw in body_lower for kw in ["narcotic", "drug", "heroin", "cocaine", "cannabis", "illegal liquor", "illicit liquor", "kasippu"]):
                sections["07. DETECT OF NARCOTIC AND ILLEGAL LIQUOR:"].append(inc)
            
            # 08. Arrest of Tri-forces Members
            elif any(kw in body_lower for kw in ["tri-force", "army", "navy", "air force", "soldier", "military"]):
                sections["08. ARREST OF TRI-FORCES MEMBERS:"].append(inc)
            
            # 01. Serious Crimes (homicide, theft, burglary, robbery - but NOT arms arrests)
            elif any(kw in body_lower for kw in 
                     ["homicide", "murder", "robbery", "theft", "burglary", "house breaking"]):
                sections["01. SERIOUS CRIMES COMMITTED:"].append(inc)
            
            # 09. Other Matters (default for anything else)
            else:
                sections["09. OTHER MATTERS:"].append(inc)
        
        return sections
    
    def organize_by_province(self, categorized_sections, show_all_provinces=True):
        """Organize incidents by province within each section in official order.
        
        Args:
            categorized_sections: Dict of section titles to incidents
            show_all_provinces: If True, show ALL 9 provinces with "Nil" for empty ones
        """
        
        # Official province order (MUST be in this exact order)
        OFFICIAL_PROVINCE_ORDER = [
            "WESTERN",
            "SABARAGAMUWA", 
            "SOUTHERN",
            "UVA",
            "CENTRAL",
            "NORTH WESTERN",
            "NORTH CENTRAL",
            "EASTERN",
            "NORTHERN"
        ]
        
        result = []
        
        for section_title, incidents in categorized_sections.items():
            # Group incidents by province
            provinces_dict = {}
            
            for inc in incidents:
                prov = inc.get("province", "UNKNOWN").upper()
                # Normalize province names
                if prov == "NORTH-WESTERN" or prov == "NORTHWESTERN":
                    prov = "NORTH WESTERN"
                elif prov == "NORTH-CENTRAL" or prov == "NORTHCENTRAL":
                    prov = "NORTH CENTRAL"
                
                if prov not in provinces_dict:
                    provinces_dict[prov] = []
                provinces_dict[prov].append(inc)
            
            # Convert to list format in official order
            provinces_list = []
            
            if show_all_provinces:
                # Show ALL 9 provinces, with "Nil" for empty ones
                for prov_name in OFFICIAL_PROVINCE_ORDER:
                    if prov_name in provinces_dict:
                        # Province has data
                        provinces_list.append({
                            "name": prov_name,
                            "incidents": provinces_dict[prov_name]
                        })
                    else:
                        # Province has no data - add "Nil" entry
                        provinces_list.append({
                            "name": prov_name,
                            "incidents": [],
                            "nil": True  # Flag to indicate this should show "Nil"
                        })
            else:
                # Only show provinces that have data
                for prov_name in OFFICIAL_PROVINCE_ORDER:
                    if prov_name in provinces_dict:
                        provinces_list.append({
                            "name": prov_name,
                            "incidents": provinces_dict[prov_name]
                        })
            
            # Add any provinces not in official order (shouldn't happen)
            for prov_name, incs in provinces_dict.items():
                if prov_name not in OFFICIAL_PROVINCE_ORDER:
                    provinces_list.append({
                        "name": prov_name,
                        "incidents": incs
                    })
            
            result.append({
                "title": section_title,
                "provinces": provinces_list
            })
        
        return result
    
    def generate_report(self, incidents, date_range, output_html, output_pdf=None):
        """Complete pipeline: categorize, organize, and generate report."""
        
        print("\n" + "=" * 80)
        print("GENERAL SITUATION REPORT - Complete Pipeline")
        print("=" * 80)
        
        # Categorize
        print("\n1. Categorizing incidents...")
        categorized = self.categorize_for_general_report(incidents)
        
        for section, incs in categorized.items():
            if incs:
                print(f"   {section} → {len(incs)} incidents")
        
        # Organize by province
        print("\n2. Organizing by province...")
        sections = self.organize_by_province(categorized)
        
        # Build report data
        print("\n3. Building report data structure...")
        report_data = {
            "date_range": date_range,
            "sections": sections
        }
        
        # Generate HTML
        print("\n4. Generating HTML report...")
        generate_general_report(report_data, output_html)
        
        # Generate PDF if requested
        if output_pdf:
            print("\n5. Converting to PDF...")
            html_to_pdf(output_html, output_pdf)
        
        print("\n" + "=" * 80)
        print("✅ REPORT GENERATION COMPLETE!")
        print("=" * 80)
        
        return report_data


# Example usage
if __name__ == "__main__":
    processor = GeneralReportProcessor()
    
    # Sample incident data
    sample_incident = {
        "station": "Pussellawa",
        "type": "Burglary",
        "details": "Rs. 150,000 cash and gold jewellery (1.75 sovereigns) worth Rs. 600,000",
        "method": "Breaking and entering through window",
        "time": "Between 0900 hrs on 14 March 2026 and 1400 hrs on 16 March 2026",
        "location": "Mawelakanda, Maswela",
        "complainant": "H. S. Kandegedara",
        "phone": "072-5340753",
        "suspect": "Unknown",
        "recovery": "Not recovered",
        "reference": "CTM.522",
        "province": "CENTRAL"
    }
    
    print("Testing General Report Processor")
    print("=" * 80)
    
    # Generate narrative
    result = processor.generate_detailed_narrative(sample_incident)
    
    if result.get("narrative"):
        print("\n✅ Generated Narrative:")
        print("-" * 80)
        print(result["narrative"])
        print("-" * 80)
        print(f"\nWord Count: {result['word_count']}")
        print(f"Station: {result['station']}")
        print(f"Summary: {result['summary']}")
        print(f"Reference: {result['reference']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")
