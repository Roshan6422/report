"""
patterns.py — Centralized Regex Patterns and Institutional Constants
===================================================================
Contains all standard Sri Lanka Police report markers, section titles,
and province mappings used by both AI and Regex engines.

System Version: v2.2.0
"""


# =============================================================================
# 1. SECTION DEFINITIONS
# =============================================================================

GENERAL_SECTIONS = [
    "01.SERIOUS CRIMES COMMITTED:",
    "02.RAPE, SEXUAL ASSAULT & CHILD ABUSE:",
    "03. FATAL ACCIDENTS:",
    "04. POLICE OFFICERS/VEHICLES INVOLVED IN ROAD ACCIDENTS AND DAMAGES TO SRI LANKA POLICE PROPERTY:",
    "05.FINDING OF DEAD BODIES UNDER SUSPICIOUS CIRCUMSTANCES:",
    "06.POLICE OFFICERS CHARGED IN COURTS / COMPLAINTS AGAINST POLICE / ALLEGED ACTS OF INDISCIPLINE BY POLICE OFFICERS:",
    "07.SERIOUS INJURY/ ILLNESSES/ DEATHS OF POLICE OFFICERS:",
    "08.DETECTION OF NARCOTIC AND ILLICIT LIQUOR:",
    "09.ARREST OF TRI-FORCES MEMBERS:",
    "10.OTHER MATTERS:"
]

SECURITY_SECTIONS = [
    "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST / TERRORIST ACTIVITIES:",
    "02. RECOVERY OF ARMS / AMMUNITION / EXPLOSIVES & BOMBS:",
    "03. PROTESTS, STRIKES & PUBLIC DEMONSTRATIONS:",
    "04. PNB / NAVY RECOVERIES & SPECIAL SECURITY OPERATIONS:",
    "05. OTHER MATTERS OF INTEREST AND IMPORTANCE:"
]

# --- Official 28 Institutional Categories ---
OFFICIAL_CASE_TABLE_CATEGORIES = [
    "01. Terrorist Activities",
    "02. Recovery of Arms & Ammunition",
    "03. Protests & Strikes",
    "04. Homicides",
    "05. Robberies",
    "06. Thefts of Vehicles",
    "07. Thefts of Properties",
    "08. House Breaking & Theft",
    "09. Rape & sexual Abuse",
    "10. Fatal accidents",
    "11. Unidentified dead bodies & suspicious dead bodies",
    "12. Police Accidents",
    "13. Serious injuries of Police officers and Damages to Police Property",
    "14. Misconducts of Police officers",
    "15. Deaths of Police officers",
    "16. Hospital admission of SGOO",
    "17. Passing away of close Relatives of SGOO",
    "18. Passing away of close relatives of retired SGOO",
    "19. Detections of Narcotics & Illicit Liquor",
    "20. Arrests",
    "21. Arresting of Tri-forces Members",
    "22. Disappearances",
    "23. Suicides",
    "24. Incidents regarding Foreigners",
    "25. Wild elephant attacks & Deaths of wild elephants",
    "26. Deaths due to drowning",
    "27. Incidents of Fire",
    "28. Cyber Crimes & Digital Offences",
    "29. Others",
]

# =============================================================================
# 2. PROVINCE & UNIT LISTS
# =============================================================================

PROVINCE_LIST = [
    "WESTERN", "SABARAGAMUWA", "SOUTHERN", "UVA", "CENTRAL",
    "NORTH WESTERN", "NORTH CENTRAL", "EASTERN", "NORTHERN"
]

SPECIAL_UNITS = [
    "CRIME", "TRAFFIC", "NARCOTICS", "SUPPORT SERVICES", "CID", "PNB", "STF"
]

# =============================================================================
# 3. QUALITY & CONFIDENCE CONSTANTS
# =============================================================================

REQUIRED_FIELDS = ["station", "body"]
QUALITY_FIELDS = ["hierarchy"]

QUALITY_KEYWORDS = [
    "reported", "arrested", "suspect", "victim", "complainant",
    "investigations", "motive", "aged", "rs.", "valued",
    "police station", "incident", "offence"
]

# =============================================================================
# 4. REGEX PATTERNS
# =============================================================================

# Matches section headers like "01. SERIOUS CRIMES" or "# 01."
SECTION_HEADER_PATTERN = r'\n\s*(?:#+\s*|\*\*|)?[\[\(]?((?:[IVX]{1,4}\.|[0-9]{1,2}\.)[\s\S]{5,120}?)[\)\]]?(?:\*\*|:|\n|$)'

# Matches incident starts (Station: Body) — supports bold markdown, CTM/OTM codes, and plain formats
INCIDENT_START_PATTERN = r'^(?:\d+\.?\s*)?(?:\*+\s*)?(?:\*\*)?([^:*–\-(\n]{2,60}?)(?:\*\*)?(?:\s*,\s*(?:CTM|OTM)\s*[\d/]+)?\s*(?:\([^)]*\))?\s*(?:\*\*)?[:\-–]\s*(?:\*\*)?(.*)$'

# Matches institutional hierarchy markers
HIERARCHY_MARKER_PATTERN = r'DIG |DIG|DIR\.|DIV\.|DISTRICT'
