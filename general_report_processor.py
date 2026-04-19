"""
General Report Processor
========================
Automated processing of incidents for General Situation Reports with detailed narratives.
Features: AI-powered narrative generation, 10-section categorization, 
          province organization with official order, HTML/PDF report generation.

Usage:
    from general_report_processor import GeneralReportProcessor
    processor = GeneralReportProcessor()
    result = processor.generate_report(incidents, date_range, "output.html")
"""

import re
import time
import logging
from typing import Any, Dict, List, Optional

# ── Project Imports (with graceful fallback) ─────────────────────────────────
try:
    from ai_engine_manager import AIEngineManager
except ImportError:
    class AIEngineManager:
        def call_ai(self, *a, **k): return "❌ AIEngineManager not available"

try:
    from general_report_engine import generate_general_report, html_to_pdf
except ImportError:
    def generate_general_report(*a, **k): return None
    def html_to_pdf(*a, **k): pass

try:
    from general_report_prompts import (
        GENERAL_REPORT_SYSTEM_PROMPT,
        create_general_report_prompt,
    )
except ImportError:
    GENERAL_REPORT_SYSTEM_PROMPT = "You are a professional Sri Lanka Police report writer."
    def create_general_report_prompt(d): return f"Generate report for: {d}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("report_processor.log", encoding="utf-8", mode="a")
    ]
)
logger = logging.getLogger(__name__)


class GeneralReportProcessor:
    """Process incidents and generate General Situation Reports."""

    # Official province order (MUST be in this exact order for reports)
    OFFICIAL_PROVINCE_ORDER = [
        "WESTERN", "SABARAGAMUWA", "SOUTHERN", "UVA", "CENTRAL",
        "NORTH WESTERN", "NORTH CENTRAL", "EASTERN", "NORTHERN"
    ]

    # Category keyword mappings for intelligent classification
    CATEGORY_KEYWORDS = {
        "01. SERIOUS CRIMES COMMITTED:": [
            "homicide", "murder", "robbery", "house breaking", "vehicle theft",
            "property theft", "theft", "burglary", "stolen", "snatching"
        ],
        "02. RAPE, SEXUAL ASSAULT & CHILD ABUSE:": [
            "rape", "sexual assault", "sexual abuse", "child abuse",
            "molestation", "indecent", "statutory"
        ],
        "03. FATAL ACCIDENTS:": [
            "fatal accident", "deadly crash", "death in accident",
            "killed in accident", "fatality"
        ],
        "04. POLICE OFFICERS/VEHICLES INVOLVED IN ROAD ACCIDENTS AND DAMAGES TO SRI LANKA POLICE PROPERTY: ": [
            "police accident", "police vehicle", "police property",
            "damage to police", "police officer injured", "police vehicle accident"
        ],
        "05. FINDING OF DEAD BODIES UNDER SUSPICIOUS CIRCUMSTANCES:": [
            "dead body", "unidentified body", "suspicious death",
            "corpse", "unidentified dead", "found dead"
        ],
        "06. POLICE OFFICERS CHARGED IN COURTS / COMPLAINTS AGAINST POLICE / ALLEGED ACTS OF INDISCIPLINE BY POLICE OFFICERS": [
            "police misconduct", "complaint against police", "officer charged",
            "police charged", "indiscipline", "police complaint"
        ],
        "07. SERIOUS INJURY/ ILLNESSES/ DEATHS OF POLICE OFFICERS:": [
            "police officer injured", "police officer death", "police illness",
            "hospital admission police", "hospitalized police", "police death"
        ],
        "08. DETECT OF NARCOTIC AND ILLEGAL LIQUOR:": [
            "narcotic", "drug", "heroin", "cocaine", "cannabis", "illegal liquor",
            "illicit liquor", "kasippu", "methamphetamine", "ganja", "detection"
        ],
        "09. ARREST OF TRI-FORCES MEMBERS:": [
            "tri-force", "army", "navy", "air force", "soldier", "military",
            "tri-forces", "armed forces"
        ],
    }

    def __init__(self, ai_timeout: int = 120, max_retries: int = 2):
        """
        Initialize the processor.
        
        Args:
            ai_timeout: Timeout in seconds for AI calls (default: 120)
            max_retries: Number of retry attempts for failed AI calls (default: 2)
        """
        self.ai_manager = AIEngineManager()
        self.ai_timeout = ai_timeout
        self.max_retries = max_retries

    def _normalize_province(self, prov: Optional[str]) -> str:
        """
        Normalize province name to official canonical form.
        
        Args:
            prov: Province name (may be abbreviated or misspelled)
            
        Returns:
            Normalized province name in uppercase
        """
        if not prov:
            return "UNKNOWN"
        
        prov = str(prov).strip().upper()
        
        # Handle common variations and abbreviations
        variants = {
            "N. WESTERN": "NORTH WESTERN", "WAYAMBA": "NORTH WESTERN",
            "N. CENTRAL": "NORTH CENTRAL", "RAJARATA": "NORTH CENTRAL",
            "SABARA": "SABARAGAMUWA", "SOUTH": "SOUTHERN",
            "NORTH": "NORTHERN", "EAST": "EASTERN", "WEST": "WESTERN",
            "NORTH-WESTERN": "NORTH WESTERN", "NORTHWESTERN": "NORTH WESTERN",
            "NORTH-CENTRAL": "NORTH CENTRAL", "NORTHCENTRAL": "NORTH CENTRAL",
            "UVA PROVINCE": "UVA", "CENTRAL PROVINCE": "CENTRAL",
        }
        
        return variants.get(prov, prov)

    def _parse_narrative(self, narrative: str) -> tuple:
        """
        Parse AI-generated narrative into structured components.
        
        Args:
            narrative: Full narrative string from AI
            
        Returns:
            Tuple of (station, summary, body, reference)
        """
        if not narrative:
            return "", "", "", ""
        
        # Extract station name (before first colon, case-insensitive)
        station_match = re.match(r'^([A-Za-z\s]+?):', narrative)
        station = station_match.group(1).strip().upper() if station_match else ""
        
        # Extract summary — look for crime keywords in parentheses
        summary_match = re.search(
            r'\((?:A\s+case\s+of\s+)?([^)]*?(?:theft|robbery|homicide|rape|accident|assault)[^)]*?)\)',
            narrative, re.IGNORECASE
        )
        summary = summary_match.group(1).strip() if summary_match else ""
        
        # Extract reference code — support CTM, OTM, IR formats with optional suffix
        ref_match = re.search(r'\((?:CTM|OTM|IR)\.\d+(?:/\d+)?\)\s*$', narrative)
        ref = ref_match.group(1) if ref_match else ""
        
        # Extract body: everything between station and reference
        body = narrative
        if station and ':' in body:
            body = body.split(':', 1)[1].strip()
        if ref and '(' in body:
            # Remove reference from end
            body = re.sub(r'\s*\([^)]+\)\s*$', '', body).strip()
        
        return station, summary, body, ref

    def generate_detailed_narrative(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed narrative for a single incident using AI with retry logic.
        
        Args:
            incident_data: Dictionary containing incident details
            
        Returns:
            Dictionary with narrative components or error information
        """
        user_prompt = create_general_report_prompt(incident_data)
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.ai_manager.call_ai(
                    prompt=user_prompt,
                    system_prompt=GENERAL_REPORT_SYSTEM_PROMPT,
                    timeout=self.ai_timeout
                )
                
                if response and not str(response).startswith("❌"):
                    narrative = str(response).strip()
                    station, summary, body, ref = self._parse_narrative(narrative)
                    
                    return {
                        "station": station,
                        "summary": summary,
                        "body": body,
                        "reference": ref,
                        "narrative": narrative,
                        "word_count": len(narrative.split()),
                        "success": True
                    }
                    
                last_error = str(response) if response else "Empty response"
                logger.warning(f"AI call attempt {attempt + 1} failed: {last_error[:100]}")
                
            except Exception as e:
                last_error = f"Exception: {type(e).__name__}: {str(e)[:100]}"
                logger.warning(f"AI call attempt {attempt + 1} exception: {last_error}")
            
            # Exponential backoff before retry
            if attempt < self.max_retries:
                wait_time = 1.5 ** attempt
                logger.info(f"Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        # All retries failed
        logger.error(f"All {self.max_retries + 1} attempts failed. Last error: {last_error}")
        return {
            "error": last_error,
            "narrative": None,
            "success": False
        }

    def process_batch(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple incidents and generate narratives.
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            List of results with narratives or errors
        """
        results = []
        logger.info(f"Processing {len(incidents)} incidents...")
        
        for i, inc in enumerate(incidents, 1):
            station = inc.get("station", "Unknown")
            logger.info(f"[{i}/{len(incidents)}] Processing: {station}")
            
            result = self.generate_detailed_narrative(inc)
            
            if result.get("success"):
                logger.info(f"  ✓ Generated: {result.get('word_count', 0)} words")
                results.append(result)
            else:
                logger.warning(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
                results.append(result)
        
        successful = sum(1 for r in results if r.get("success"))
        logger.info(f"✅ Completed: {successful}/{len(incidents)} successful")
        
        return results

    def categorize_for_general_report(self, incidents: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Categorize incidents into 10 General Report sections using keyword matching.
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            Dictionary mapping section titles to lists of incidents
        """
        sections = {title: [] for title in self.CATEGORY_KEYWORDS}
        sections["10. OTHER MATTERS:"] = []  # Catch-all category
        
        for inc in incidents:
            # Combine all text fields for comprehensive keyword search
            body = str(inc.get("body", "")).lower()
            summary = str(inc.get("summary", "")).lower()
            narrative = str(inc.get("narrative", "")).lower()
            text_to_search = f"{body} {summary} {narrative}"
            
            categorized = False
            
            # Try each category in order
            for section_title, keywords in self.CATEGORY_KEYWORDS.items():
                if any(kw in text_to_search for kw in keywords):
                    # Special handling for Fatal Accidents vs Police Accidents
                    if section_title == "03. FATAL ACCIDENTS:":
                        if any(kw in text_to_search for kw in ["police accident", "police vehicle"]):
                            continue  # Don't categorize police accidents as general fatal accidents
                    sections[section_title].append(inc)
                    categorized = True
                    break
            
            # Default to "Other Matters" if no category matched
            if not categorized:
                sections["10. OTHER MATTERS:"].append(inc)
        
        return sections

    def organize_by_province(self, categorized_sections: Dict[str, List[Dict]], 
                          show_all_provinces: bool = True) -> List[Dict[str, Any]]:
        """
        Organize incidents by province within each section in official order.
        
        Args:
            categorized_sections: Dict of section titles to incident lists
            show_all_provinces: If True, include all 9 provinces with "Nil" for empty ones
            
        Returns:
            List of section dictionaries with province-organized incidents
        """
        result = []
        
        for section_title, incidents in categorized_sections.items():
            # Group incidents by normalized province name
            provinces_dict = {}
            
            for inc in incidents:
                prov = self._normalize_province(inc.get("province"))
                if prov not in provinces_dict:
                    provinces_dict[prov] = []
                provinces_dict[prov].append(inc)
            
            # Build province list in official order
            provinces_list = []
            
            if show_all_provinces:
                # Include ALL 9 official provinces, marking empty ones as "Nil"
                for prov_name in self.OFFICIAL_PROVINCE_ORDER:
                    if prov_name in provinces_dict:
                        provinces_list.append({
                            "name": prov_name,
                            "incidents": provinces_dict[prov_name]
                        })
                    else:
                        provinces_list.append({
                            "name": prov_name,
                            "incidents": [],
                            "nil": True  # Flag for "Nil" display in report
                        })
            else:
                # Only include provinces that have incidents
                for prov_name in self.OFFICIAL_PROVINCE_ORDER:
                    if prov_name in provinces_dict:
                        provinces_list.append({
                            "name": prov_name,
                            "incidents": provinces_dict[prov_name]
                        })
            
            # Add any non-standard provinces at the end (shouldn't happen with normalization)
            for prov_name, incs in provinces_dict.items():
                if prov_name not in self.OFFICIAL_PROVINCE_ORDER:
                    provinces_list.append({
                        "name": prov_name,
                        "incidents": incs
                    })
            
            result.append({
                "title": section_title,
                "provinces": provinces_list
            })
        
        return result

    def generate_report(self, incidents: List[Dict[str, Any]], 
                       date_range: str, 
                       output_html: str, 
                       output_pdf: Optional[str] = None,
                       table_counts: Optional[Dict] = None,
                       show_all_provinces: bool = True) -> Dict[str, Any]:
        """
        Complete pipeline: categorize, organize, and generate institutional report.
        
        Args:
            incidents: List of incident dictionaries to process
            date_range: Date range string for report header
            output_html: Path for output HTML file
            output_pdf: Optional path for output PDF file
            table_counts: Optional dict of category counts for summary table
            show_all_provinces: Whether to show all 9 provinces with "Nil" markers
            
        Returns:
            Dictionary containing the complete report data structure
        """
        logger.info("=" * 80)
        logger.info("GENERAL SITUATION REPORT - Complete Pipeline")
        logger.info("=" * 80)
        
        # Step 1: Categorize incidents into 10 official sections
        logger.info("\n1. Categorizing incidents...")
        categorized = self.categorize_for_general_report(incidents)
        
        for section, incs in categorized.items():
            if incs:
                logger.info(f"   {section} → {len(incs)} incidents")
        
        # Step 2: Organize by province in official order
        logger.info("\n2. Organizing by province...")
        sections = self.organize_by_province(categorized, show_all_provinces=show_all_provinces)
        
        # Step 3: Build report data structure
        logger.info("\n3. Building report data structure...")
        report_data = {
            "date_range": date_range,
            "sections": sections
        }
        
        if table_counts is not None:
            report_data["table_counts"] = table_counts
        
        # Step 4: Generate HTML report
        logger.info(f"\n4. Generating HTML report: {output_html}")
        try:
            generate_general_report(report_data, output_html)
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            return {"success": False, "error": f"HTML generation: {e}"}
        
        # Step 5: Convert to PDF if requested
        if output_pdf:
            logger.info(f"\n5. Converting to PDF: {output_pdf}")
            try:
                html_to_pdf(output_html, output_pdf)
            except Exception as e:
                logger.warning(f"PDF conversion failed: {e}")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ REPORT GENERATION COMPLETE!")
        logger.info("=" * 80)
        
        return {
            "success": True,
            "report_data": report_data,
            "output_html": output_html,
            "output_pdf": output_pdf
        }


# ══════════════════════════════════════════════════════════════════════════════
# Example usage & testing
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    processor = GeneralReportProcessor(ai_timeout=60, max_retries=1)
    
    # Sample incident data for testing
    sample_incident = {
        "station": "PUSSELLAWA",
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
        "province": "CENTRAL",
        "body": "A case of theft of Rs. 150,000 cash and gold jewellery valued Rs. 600,000/= was reported. The offence took place at Mawelakanda, Maswela.",
        "summary": "theft"
    }
    
    print("\n🧪 Testing General Report Processor")
    print("=" * 80)
    
    # Test 1: Single narrative generation
    print("\n1. Testing narrative generation...")
    result = processor.generate_detailed_narrative(sample_incident)
    
    if result.get("success"):
        print(f"✅ Generated: {result['word_count']} words")
        print(f"   Station: {result['station']}")
        print(f"   Summary: {result['summary']}")
        print(f"   Reference: {result['reference']}")
        print(f"\n   Narrative preview:\n   {result['narrative'][:200]}...")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 2: Categorization
    print("\n2. Testing categorization...")
    test_incidents = [sample_incident] * 3  # Duplicate for demo
    categorized = processor.categorize_for_general_report(test_incidents)
    
    for section, incs in categorized.items():
        if incs:
            print(f"   {section}: {len(incs)} incidents")
    
    # Test 3: Province organization
    print("\n3. Testing province organization...")
    organized = processor.organize_by_province(categorized)
    
    for section in organized:
        print(f"\n   {section['title']}")
        for prov in section['provinces'][:3]:  # Show first 3 provinces
            status = "Nil" if prov.get("nil") else f"{len(prov['incidents'])} incidents"
            print(f"     - {prov['name']}: {status}")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")