"""
Maps official 29 Sinhala table category IDs (app.SinhalaPoliceReportExtractor keys)
to English General / Security section groupings for regex_engine.structure_sinhala_with_regex.
"""

# Reserved for future Sinhala-label → category hints (optional enrichment).
SINHALA_CATEGORY_MAP = {}

# Keys must match police_patterns.GENERAL_SECTIONS strings exactly.
GENERAL_SECTION_ROUTING = {
    "01.SERIOUS CRIMES COMMITTED:": ["04", "05", "06", "07", "08"],
    "02.RAPE, SEXUAL ASSAULT & CHILD ABUSE:": ["09"],
    "03. FATAL ACCIDENTS:": ["10"],
    "04. POLICE OFFICERS/VEHICLES INVOLVED IN ROAD ACCIDENTS AND DAMAGES TO SRI LANKA POLICE PROPERTY:": ["12"],
    "05.FINDING OF DEAD BODIES UNDER SUSPICIOUS CIRCUMSTANCES:": ["11"],
    "06.POLICE OFFICERS CHARGED IN COURTS / COMPLAINTS AGAINST POLICE / ALLEGED ACTS OF INDISCIPLINE BY POLICE OFFICERS:": ["14"],
    "07.SERIOUS INJURY/ ILLNESSES/ DEATHS OF POLICE OFFICERS:": ["13", "15", "16", "17", "18", "19"],
    "08.DETECTION OF NARCOTIC AND ILLICIT LIQUOR:": ["20"],
    "09.ARREST OF TRI-FORCES MEMBERS:": ["22"],
    "10.OTHER MATTERS:": [
        "01", "02", "03", "21", "23", "24", "25", "26", "27", "28", "29",
    ],
}
