"""
security_categorizer.py — Intelligent Security Data Categorization
===================================================================
Automatically categorizes ALL security data into the 3 official sections.
"""

import re
from typing import List, Dict, Tuple

# CATEGORY DEFINITIONS WITH KEYWORDS
SECURITY_CATEGORIES = {
    "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST": {
        "keywords": [
            # High-level threats
            "terrorism", "terrorist", "national security", "vip security",
            "assassination", "bomb threat", "security breach", "intelligence",
            "espionage", "sabotage", "coup", "insurgency",
            # VIP related
            "president", "prime minister", "minister", "diplomat", "embassy",
            "high commissioner", "vip", "dignitary",
            # Major incidents
            "major incident", "critical", "emergency", "alert",
            "threat level", "security alert", "imminent threat",
            # Organized crime
            "organized crime", "mafia", "cartel", "syndicate",
            "human trafficking", "drug trafficking", "smuggling ring"
        ],
        "priority": 1
    },
    
    "02. SUBVERSIVE ACTIVITIES": {
        "keywords": [
            # Anti-government
            "subversive", "anti-government", "sedition", "treason",
            "rebellion", "revolt", "uprising", "insurrection",
            # Extremism
            "extremist", "radical", "militant", "separatist",
            "fundamentalist", "jihadist", "insurgent",
            # Unlawful assembly
            "unlawful assembly", "illegal gathering", "protest", "demonstration",
            "riot", "mob", "unrest", "disturbance",
            # Propaganda
            "propaganda", "inflammatory", "incitement", "hate speech",
            "seditious material", "banned literature", "extremist literature",
            # Organizations
            "banned organization", "proscribed group", "terrorist organization",
            "separatist group", "militant group"
        ],
        "priority": 2
    },
    
    "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES": {
        "keywords": [
            # Firearms
            "firearm", "gun", "pistol", "revolver", "rifle", "shotgun",
            "weapon", "t-56", "ak-47", "assault rifle", "automatic weapon",
            "semi-automatic", "handgun", "carbine", "sniper rifle",
            # Ammunition
            "ammunition", "bullet", "round", "cartridge", "shell",
            "magazine", "clip", "9mm", "7.62mm", ".38", ".45",
            # Explosives
            "explosive", "bomb", "grenade", "mine", "ied",
            "detonator", "fuse", "blasting cap", "c-4", "tnt",
            "dynamite", "gelignite", "gunpowder", "explosive device",
            # Components
            "bomb-making", "explosive material", "chemical", "fertilizer bomb",
            "timer", "trigger mechanism", "remote detonator",
            # Military equipment
            "military equipment", "army equipment", "ordnance",
            "mortar", "rocket", "missile", "launcher"
        ],
        "priority": 3
    }
}


class SecurityCategorizer:
    """Intelligent categorization of security incidents."""
    
    def __init__(self):
        self.categories = SECURITY_CATEGORIES
        self.stats = {
            "total_incidents": 0,
            "category_1": 0,
            "category_2": 0,
            "category_3": 0,
            "uncategorized": 0
        }
    
    def categorize_incident(self, incident_text: str) -> Tuple[str, float]:
        """
        Categorize a single incident into one of the 3 security categories.
        
        Args:
            incident_text: The incident text to categorize
        
        Returns:
            Tuple of (category_name, confidence_score)
        """
        incident_lower = incident_text.lower()
        scores = {}
        
        # Score each category based on keyword matches
        for category, data in self.categories.items():
            score = 0
            matched_keywords = []
            
            for keyword in data["keywords"]:
                if keyword.lower() in incident_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Boost score based on priority
            if score > 0:
                score = score * (4 - data["priority"])  # Higher priority = higher boost
            
            scores[category] = {
                "score": score,
                "keywords": matched_keywords
            }
        
        # Find best match
        if not any(s["score"] > 0 for s in scores.values()):
            # Default to category 3 (Arms Recovery) if no clear match
            return "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES", 0.5
        
        best_category = max(scores.items(), key=lambda x: x[1]["score"])
        category_name = best_category[0]
        confidence = min(best_category[1]["score"] / 5.0, 1.0)  # Normalize to 0-1
        
        return category_name, confidence
    
    def categorize_batch(self, incidents: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize multiple incidents into the 3 security categories.
        
        Args:
            incidents: List of incident dictionaries with 'body' or 'text' field
        
        Returns:
            Dictionary with category names as keys and lists of incidents as values
        """
        categorized = {
            "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST": [],
            "02. SUBVERSIVE ACTIVITIES": [],
            "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES": []
        }
        
        for incident in incidents:
            # Get incident text
            text = incident.get("body", incident.get("text", ""))
            
            # Categorize
            category, confidence = self.categorize_incident(text)
            
            # Add category info to incident
            incident["category"] = category
            incident["category_confidence"] = confidence
            
            # Add to appropriate category
            categorized[category].append(incident)
            
            # Update stats
            self.stats["total_incidents"] += 1
            if "01." in category:
                self.stats["category_1"] += 1
            elif "02." in category:
                self.stats["category_2"] += 1
            elif "03." in category:
                self.stats["category_3"] += 1
        
        return categorized
    
    def organize_by_province(self, categorized_incidents: Dict[str, List[Dict]]) -> Dict:
        """
        Organize categorized incidents by province for report generation.
        
        Args:
            categorized_incidents: Output from categorize_batch()
        
        Returns:
            Report data structure ready for web_report_engine_v2
        """
        sections = []
        
        for category_name, incidents in categorized_incidents.items():
            # Group incidents by province
            provinces = {}
            
            for incident in incidents:
                province = incident.get("province", "UNKNOWN PROVINCE")
                if province not in provinces:
                    provinces[province] = []
                provinces[province].append(incident)
            
            # Build section structure
            section = {
                "title": category_name + ":",
                "provinces": []
            }
            
            # Add provinces
            for province_name, province_incidents in provinces.items():
                section["provinces"].append({
                    "name": province_name,
                    "incidents": province_incidents
                })
            
            sections.append(section)
        
        return {"sections": sections}
    
    def print_stats(self):
        """Print categorization statistics."""
        print("\n" + "="*60)
        print("SECURITY CATEGORIZATION STATISTICS")
        print("="*60)
        print(f"Total Incidents:              {self.stats['total_incidents']}")
        print(f"Category 1 (Important):       {self.stats['category_1']}")
        print(f"Category 2 (Subversive):      {self.stats['category_2']}")
        print(f"Category 3 (Arms Recovery):   {self.stats['category_3']}")
        print(f"Uncategorized:                {self.stats['uncategorized']}")
        print("="*60)


def auto_categorize_security_data(raw_incidents: List[str]) -> Dict:
    """
    Automatically categorize raw security incident data.
    
    Args:
        raw_incidents: List of raw incident texts
    
    Returns:
        Structured data ready for report generation
    """
    categorizer = SecurityCategorizer()
    
    # Convert raw texts to incident dictionaries
    incidents = []
    for text in raw_incidents:
        incidents.append({
            "body": text,
            "station": extract_station_name(text),
            "province": extract_province(text)
        })
    
    # Categorize
    categorized = categorizer.categorize_batch(incidents)
    
    # Organize by province
    report_data = categorizer.organize_by_province(categorized)
    
    # Print stats
    categorizer.print_stats()
    
    return report_data


def extract_station_name(text: str) -> str:
    """Extract station name from incident text."""
    # Look for pattern: STATION_NAME: or STATION_NAME Police
    match = re.search(r'^([A-Z\s]+)(?:POLICE STATION|:)', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "UNKNOWN"


def extract_province(text: str) -> str:
    """Extract province from incident text."""
    provinces = [
        "WESTERN", "CENTRAL", "SOUTHERN", "NORTHERN", "EASTERN",
        "NORTH WESTERN", "NORTH CENTRAL", "UVA", "SABARAGAMUWA"
    ]
    
    text_upper = text.upper()
    for province in provinces:
        if province in text_upper:
            return province
    
    return "UNKNOWN"


# EXAMPLE USAGE
if __name__ == "__main__":
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  SECURITY DATA CATEGORIZER".center(58) + "█")
    print("█" + "  Automatic 3-Category Classification".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60 + "\n")
    
    # Sample incidents
    sample_incidents = [
        """
        EMBILIPITIYA: Police arrested suspects with electric detonator and 
        80g of gunpowder. Rev. Indrarathana thero, aged 68, and N.U. 
        Samanchandra, aged 56, arrested while digging tunnel for treasure 
        hunting. Court date: 18th March 2026. (OTM.1421)
        """,
        """
        COLOMBO: Unlawful assembly dispersed. Group of 50 persons gathered 
        distributing anti-government pamphlets. Three organizers arrested. 
        Seditious material seized. (CTM.234)
        """,
        """
        JAFFNA: Intelligence reports indicate potential VIP security threat. 
        Enhanced security measures implemented for ministerial visit. 
        Surveillance increased. (IR.567)
        """,
        """
        GALLE: T-56 assault rifle with 30 rounds of ammunition recovered 
        from abandoned vehicle. Serial number traced. Investigations ongoing. 
        (OTM.890)
        """,
        """
        KANDY: Extremist group meeting disrupted. Five members of banned 
        organization arrested. Propaganda materials confiscated. (CTM.456)
        """
    ]
    
    # Categorize
    categorizer = SecurityCategorizer()
    
    print("Categorizing incidents...\n")
    for i, incident in enumerate(sample_incidents, 1):
        category, confidence = categorizer.categorize_incident(incident)
        print(f"Incident {i}:")
        print(f"  Category: {category}")
        print(f"  Confidence: {confidence:.2f}")
        print()
    
    # Batch categorization
    incidents_dict = [{"body": text, "station": "TEST", "province": "WESTERN"} 
                      for text in sample_incidents]
    
    categorized = categorizer.categorize_batch(incidents_dict)
    
    print("\nCategorization Results:")
    print("-" * 60)
    for category, incidents in categorized.items():
        print(f"\n{category}")
        print(f"  Count: {len(incidents)}")
    
    categorizer.print_stats()
