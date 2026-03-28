# Provincial Mappings (Sinhala -> English)
PROVINCES_SINHALA = {
    "බස්නාහිර": "Western",
    "දකුණ": "Southern",
    "මධ්‍යම": "Central",
    "වයඹ": "North Western",
    "උතුරු මැද": "North Central",   # ✅ FIX: spacing variant
    "උතුරුමැද": "North Central",
    "ඌව": "Uva",
    "සබරගමුව": "Sabaragamuwa",
    "නැගෙනහිර": "Eastern",
    "උතුර": "Northern",
    "විශේෂ": "Special"
}


# Reinforcement Data (Optional but used for better matching)
INCIDENT_TEMPLATES = {
    "Homicide": "A case of murder was reported. Deceased: {name}. Investigations in process.",
    "Robbery": "A robbery was reported at {location}. Property stolen. Investigations in process.",
    "Theft": "A theft of property was reported. Investigations in process.",
    "Fatal Accident": "A fatal road accident was reported at {location}. Deceased: {name}."
}


COMMON_PHRASES = {
    "අත්අඩංගුලට": "arrested",
    "අත්අඩංගුවට": "arrested",  # ✅ FIX: correct Sinhala spelling
    "මරණය": "death",
    "තුවාල": "injured",
    "තුවාලයි": "injured",      # ✅ FIX: variation
    "සැකකරු": "suspect",
    "සැකකරුවන්": "suspects"   # ✅ FIX: plural support
}


SECTION_NAMES_SINHALA = {
    "මිනීමැරීම්": "Serious Crimes Committed",
    "මත්ද්‍රව්‍ය": "Detection of Narcotic",
    "අනතුරු": "Fatal Accidents"
}


# Keyword mappings for Matrix/Case calculation (Sinhala keywords)
KEYWORDS_SINHALA = {
    "Homicide": [
        "HOMICIDE", "MURDER", "FATAL ASSAULT",
        "මිනීමැරීම්", "ඝාතන", "ඝාතනය"
    ],

    "Robberies and Armed Robberies": [
        "ROBBERY", "ROBBED", "SNATCHING", "ARMED",
        "කොල්ලකෑම්", "කොල්ලය"
    ],

    "Theft": [
        "THEFT", "STOLEN", "CABLE", "MOTORCYCLE", "VEHICLE",
        "සොරකම්", "සොරකම"
    ],

    "HB & Theft": [
        "BURGLARY", "HOUSE BREAKING", "HOUSE BREAK-IN",
        "ENTERED THROUGH WINDOW",
        "ගෙවල් බිදුම්", "ගෙබිදුම්"  # ✅ FIX: Sinhala variation
    ],

    "Rape & Sexual Abuse": [
        "RAPE", "SEXUAL ABUSE", "CHILD ABUSE", "ABDUCTION",
        "SEXUALLY ABUSED",
        "දූෂණ", "අපයෝජන"
    ],

    "Police Accidents": [
        "POLICE ACCIDENT", "POLICE JEEP", "POLICE MOTORCYCLE DIED"
    ],

    "Fatal Accidents": [
        "FATAL ACCIDENT", "PEDESTRIAN RESULTED IN ONE DEATH",
        "FATAL",
        "මාරක", "අනතුරු", "අනතුර"
    ],

    "Others": [
        "ARREST", "NARCOTICS", "ILLICIT", "DISAPPEARANCE",
        "SUICIDE", "DROWNING",
        "මත්ද්‍රව්‍ය", "ගිනි අවි", "හදිසි මරණ"
    ]
}