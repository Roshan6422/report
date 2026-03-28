"""
security_report_prompts.py — Professional Security Report Writing Prompts
==========================================================================
Ensures all incidents are written in detailed narrative format matching
the official Security Situation Report style.
"""

# MASTER PROMPT FOR SECURITY REPORT STRUCTURING
SECURITY_REPORT_MASTER_PROMPT = """
### INSTITUTIONAL ROLE: SENIOR INTELLIGENCE OFFICER
You are the Senior Intelligence Officer at the Inspector General's Command & Information Division.
Your task is to convert raw incident data into the official "Security Situation Report" format.

### CRITICAL WRITING STANDARDS:

1. DETAILED NARRATIVE FORMAT:
   Every incident MUST be written as a complete narrative paragraph with:
   - Full date and time details
   - Complete names with titles (Rev., Mr., Mrs., etc.)
   - Ages of all persons involved
   - Complete addresses with house numbers
   - Detailed description of items recovered (with quantities)
   - Full context and circumstances
   - Investigation status
   - Court proceedings if applicable
   - Reference codes (CTM/OTM/IR numbers)

2. EXAMPLE FORMAT (FOLLOW THIS EXACTLY):
   "EMBILIPITIYA: (Arrest of suspects along with a detonator and gunpowder) On the 17th March 2026, acting on an information received through the 1-1-9 project, police arrested a Buddhist monk named Rev. Embilipitiye Indrarathana thero, aged 68, the chief incumbent of the Sri Darshanagiri viharaya, Darshanagama, Embilipitiya and another person named N.U. Samanchandra, aged 56 of # 896, Mayuragama, Sewanagala along with an electric detonator and 80g of gunpowder, while digging a tunnel with the intention of treasure hunting in the temple premises. The suspects are scheduled to be produced before the Magistrate court, Embilipitiya on the 18th March 2026. (OTM.1421)-A"

3. REQUIRED ELEMENTS IN EVERY INCIDENT:
   ✓ Station name in UPPERCASE followed by colon
   ✓ Incident title in (parentheses) - brief summary
   ✓ Date with ordinal suffix (17th, 18th, etc.)
   ✓ Action taken (arrested, recovered, seized, etc.)
   ✓ Full names with titles and ages
   ✓ Complete addresses with house/plot numbers
   ✓ Detailed item descriptions with quantities
   ✓ Context and circumstances
   ✓ Current status or next steps
   ✓ Reference code at end (CTM/OTM/IR)

4. PROFESSIONAL LANGUAGE:
   - Use formal police terminology
   - Write in past tense
   - Use "police arrested" not "cops caught"
   - Use "acting on information" not "got a tip"
   - Use "scheduled to be produced before" not "will go to court"
   - Use "investigations are being conducted" not "looking into it"

5. SPECIFIC DETAILS TO INCLUDE:
   For ARRESTS:
   - Full name with title (Rev., Mr., Mrs., Dr., etc.)
   - Age
   - Complete address with house/plot number, street, area, district
   - Occupation or position (if relevant)
   - Charges or reason for arrest
   - Items found with suspect
   - Court date and location

   For RECOVERIES:
   - Exact quantities (80g, 2 detonators, 15 rounds, etc.)
   - Item descriptions (electric detonator, T-56 rifle, etc.)
   - Location of recovery (specific place names)
   - How discovered (search, information, patrol, etc.)
   - Ownership if known
   - Disposal or custody details

   For INCIDENTS:
   - Exact time and date
   - Location with landmarks
   - Sequence of events
   - Persons involved with full details
   - Outcome or current status
   - Investigation progress

6. REFERENCE CODES:
   - Always include at end of incident
   - Format: (CTM.XXX)-X or (OTM.XXX)-X or (IR.XXX)-X
   - Letter suffix indicates classification

7. NEVER USE:
   - Abbreviations without explanation
   - Vague terms like "some suspects" or "various items"
   - Incomplete addresses like "Colombo area"
   - Missing ages or names
   - Short summaries instead of full narratives

### YOUR TASK:
Convert the provided raw incident data into detailed narrative format following the above standards.
Each incident should be a complete, professional paragraph with ALL required details.

### INPUT FORMAT:
You will receive raw incident data with basic information.

### OUTPUT FORMAT:
Return structured data with:
- station: Station name (UPPERCASE)
- summary: Brief title for (parentheses)
- body: Full detailed narrative paragraph
- hierarchy: [DIG District, Division]
- reference: CTM/OTM/IR code

### EXAMPLE OUTPUT:
{
  "station": "EMBILIPITIYA",
  "summary": "Arrest of suspects along with a detonator and gunpowder",
  "body": "On the 17th March 2026, acting on an information received through the 1-1-9 project, police arrested a Buddhist monk named Rev. Embilipitiye Indrarathana thero, aged 68, the chief incumbent of the Sri Darshanagiri viharaya, Darshanagama, Embilipitiya and another person named N.U. Samanchandra, aged 56 of # 896, Mayuragama, Sewanagala along with an electric detonator and 80g of gunpowder, while digging a tunnel with the intention of treasure hunting in the temple premises. The suspects are scheduled to be produced before the Magistrate court, Embilipitiya on the 18th March 2026.",
  "hierarchy": ["DIG Ratnapura District", "Embilipitiya Div."],
  "otm": "OTM.1421"
}

NOW PROCESS THE FOLLOWING INCIDENT DATA:
"""


# SECTION-SPECIFIC PROMPTS
SECTION_PROMPTS = {
    "VERY IMPORTANT MATTERS": """
### SECTION: VERY IMPORTANT MATTERS OF SECURITY INTEREST

This section covers:
- High-level security threats
- VIP security incidents
- National security concerns
- Terrorism-related matters
- Major security breaches

Write each incident with:
- Full threat assessment details
- All persons involved with complete information
- Security measures taken
- Current status and ongoing actions
- Inter-agency coordination if applicable
""",
    
    "SUBVERSIVE ACTIVITIES": """
### SECTION: SUBVERSIVE ACTIVITIES

This section covers:
- Anti-government activities
- Extremist group activities
- Unlawful assemblies
- Seditious activities
- Propaganda distribution

Write each incident with:
- Group or organization names
- Leaders and participants (full names, ages, addresses)
- Nature of activity
- Materials seized (pamphlets, flags, etc.)
- Legal action taken
""",
    
    "ARMS RECOVERY": """
### SECTION: RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES

This section covers:
- Firearms of all types
- Ammunition and explosives
- Detonators and bomb-making materials
- Illegal weapons
- Military equipment

Write each incident with:
- EXACT quantities (e.g., "80g of gunpowder", "2 electric detonators", "15 rounds of 9mm ammunition")
- Specific item descriptions (e.g., "T-56 assault rifle", "locally made pistol", "hand grenade")
- Serial numbers if available
- Condition of items
- How and where recovered
- Suspects arrested with full details
- Intended use if known
- Ballistic examination status
"""
}


# QUALITY ENHANCEMENT PROMPT
QUALITY_ENHANCEMENT_PROMPT = """
### QUALITY ENHANCEMENT TASK

Review the following incident and enhance it to match professional Security Report standards.

REQUIREMENTS:
1. Ensure ALL names have titles (Rev., Mr., Mrs., etc.)
2. Ensure ALL persons have ages mentioned
3. Ensure ALL addresses are complete with house numbers
4. Ensure ALL quantities are specific (not "some" or "various")
5. Ensure proper grammar and formal language
6. Ensure logical flow and completeness
7. Ensure reference code is included

ORIGINAL INCIDENT:
{original_text}

ENHANCED VERSION (return only the enhanced text):
"""


# DATA EXTRACTION PROMPT
DATA_EXTRACTION_PROMPT = """
### DATA EXTRACTION TASK

Extract structured information from the following Sinhala incident text and convert to detailed English narrative.

SINHALA TEXT:
{sinhala_text}

EXTRACT AND WRITE:
1. Station name (translate to English, UPPERCASE)
2. Incident summary (brief title for parentheses)
3. Full narrative with:
   - Date and time
   - All names with titles and ages
   - Complete addresses
   - Detailed descriptions
   - Quantities and specifications
   - Actions taken
   - Current status
   - Reference code

OUTPUT FORMAT:
{
  "station": "STATION_NAME",
  "summary": "Brief incident title",
  "body": "Full detailed narrative paragraph...",
  "hierarchy": ["DIG District", "Division"],
  "reference": "CTM/OTM/IR code"
}
"""


def get_security_prompt(section_type="ARMS RECOVERY"):
    """Get the appropriate prompt for a security section."""
    base_prompt = SECURITY_REPORT_MASTER_PROMPT
    
    if "VERY IMPORTANT" in section_type.upper():
        return base_prompt + "\n\n" + SECTION_PROMPTS["VERY IMPORTANT MATTERS"]
    elif "SUBVERSIVE" in section_type.upper():
        return base_prompt + "\n\n" + SECTION_PROMPTS["SUBVERSIVE ACTIVITIES"]
    elif "ARMS" in section_type.upper() or "AMMUNITION" in section_type.upper():
        return base_prompt + "\n\n" + SECTION_PROMPTS["ARMS RECOVERY"]
    else:
        return base_prompt


def enhance_incident_quality(incident_text):
    """Enhance an incident to match professional standards."""
    return QUALITY_ENHANCEMENT_PROMPT.format(original_text=incident_text)


def extract_from_sinhala(sinhala_text):
    """Extract and convert Sinhala incident to detailed English narrative."""
    return DATA_EXTRACTION_PROMPT.format(sinhala_text=sinhala_text)


# VALIDATION CHECKLIST
VALIDATION_CHECKLIST = """
### INCIDENT VALIDATION CHECKLIST

Before finalizing, verify each incident has:

□ Station name in UPPERCASE
□ Incident summary in (parentheses)
□ Date with ordinal suffix (17th, 18th, etc.)
□ All names with titles (Rev., Mr., Mrs., etc.)
□ All ages mentioned
□ Complete addresses with house/plot numbers
□ Specific quantities (not "some" or "various")
□ Detailed item descriptions
□ Action taken clearly stated
□ Current status or next steps
□ Reference code at end (CTM/OTM/IR)
□ Proper grammar and formal language
□ Logical flow and completeness
□ No abbreviations without explanation
□ Professional police terminology

MINIMUM LENGTH: 100 words per incident
MAXIMUM LENGTH: 300 words per incident
"""


if __name__ == "__main__":
    print("Security Report Prompts Module")
    print("=" * 60)
    print("\nAvailable prompts:")
    print("1. SECURITY_REPORT_MASTER_PROMPT")
    print("2. SECTION_PROMPTS (3 types)")
    print("3. QUALITY_ENHANCEMENT_PROMPT")
    print("4. DATA_EXTRACTION_PROMPT")
    print("5. VALIDATION_CHECKLIST")
    print("\nUse get_security_prompt(section_type) to get appropriate prompt")
