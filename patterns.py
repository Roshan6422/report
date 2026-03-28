"""
patterns.py — Centralized Regex Patterns and Institutional Constants
===================================================================
Contains all standard Sri Lanka Police report markers, section titles,
and province mappings used by both AI and Regex engines.

System Version: v2.1.0
"""

import re

# =============================================================================
# 1. SECTION DEFINITIONS
# =============================================================================

GENERAL_SECTIONS = [
    "01. SERIOUS CRIMES COMMITTED",
    "02. RAPE, SEXUAL ASSAULT & CHILD ABUSE",
    "03. FATAL ACCIDENTS",
    "04. POLICE OFFICERS/VEHICLES INVOLVED IN ROAD ACCIDENTS AND DAMAGES TO SRI LANKA POLICE PROPERTY",
    "05. FINDING OF DEAD BODIES UNDER SUSPICIOUS CIRCUMSTANCES",
    "06. POLICE OFFICERS CHARGED IN COURTS / COMPLAINTS AGAINST POLICE / ALLEGED ACTS OF INDISCIPLINE BY POLICE OFFICERS",
    "07. SERIOUS INJURY/ ILLNESSES/ DEATHS OF POLICE OFFICERS",
    "08. DETECTION OF NARCOTIC AND ILLEGAL LIQUOR",
    "09. ARREST OF TRI-FORCES MEMBERS",
    "10. OTHER MATTERS"
]

SECURITY_SECTIONS = [
    "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST",
    "02. SUBVERSIVE ACTIVITIES",
    "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES"
]

# =============================================================================
# 2. PROVINCE & UNIT LISTS
# =============================================================================

PROVINCE_LIST = [
    "WESTERN", "SOUTHERN", "NORTHERN", "EASTERN", "NORTH WESTERN", 
    "NORTH CENTRAL", "UVA", "SABARAGAMUWA", "CENTRAL"
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
