# Provincial Mappings (Sinhala -> English)
PROVINCES_SINHALA = {
    "බස්නාහිර": "Western",
    "දකුණ": "Southern",
    "සබරගමුව": "Sabaragamuwa",
    "මධ්‍යම": "Central",
    "වයඹ": "North Western",
    "උතුරු මැද": "North Central",
    "ඌව": "Uva",
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

    "අත්අඩංගුවට": "arrested",
    "මරණය": "death",
    "තුවාලයි": "injured",
    "සැකකරු": "suspect",
    "සැකකරුවන්": "suspects"
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
        "ගෙවල් බිදුම්", "ගෙබිදුම්"
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
# =============================================================================
# SECURITY PATTERNS ADDITION (Add this below your existing dictionaries)
# =============================================================================

# Security-specific Section Mappings (Sinhala -> English)
SECURITY_SECTION_NAMES_SINHALA = {
    "ත්‍රස්තවාදී": "Terrorist Activities",
    "ගිනි අවි සහ උණ්ඩ": "Recovery of Arms & Ammunition",
    "උද්ඝෝෂණ": "Protests & Strikes",
    "PNB/නාවික": "PNB/Navy Recoveries",
    "පිපිරවීම්": "Explosives & Bombs",
    "විශේෂ ආරක්ෂක": "Special Security Operations"
}

# Merge into existing SECTION_NAMES_SINHALA
SECTION_NAMES_SINHALA.update(SECURITY_SECTION_NAMES_SINHALA)

# Security-specific Incident Templates
INCIDENT_TEMPLATES.update({
    "Arms Recovery": "A quantity of arms and ammunition was recovered at {location}. Items include {items}. Handed over to {unit}. Investigations in process.",
    "Terror/Explosive": "A suspicious explosive device/subversive material was detected at {location}. STF/Police specialists rendered it safe. No casualties reported.",
    "Protest/Strike": "A protest/demonstration was held at {location} by {group}. Traffic diverted. No untoward incidents reported.",
    "PNB/Navy Handover": "Suspects arrested with sealed packets of narcotics/weapons were handed over to the PNB/Navy at {location}. Case registered under {act}.",
    "Special Security": "Security alert raised at {location}. Increased patrols deployed. Situation normal."
})

# Security Keyword Mappings for Classification & Matrix Calculation
SECURITY_KEYWORDS = {
    "Terrorist Activities": [
        "TERROR", "SUBVERSIVE", "LTTE", "EXPLOSION", "BLAST", "BOMB", "SUICIDE ATTACK", "IED",
        "ත්‍රස්ත", "ප්‍රහාර", "බෝම්බ", "විනාශකාරී", "සබර්සිව්"
    ],
    "Recovery of Arms & Ammunition": [
        "ARMS", "AMMUNITION", "FIREARM", "PISTOL", "T-56", "M-16", "GRENADE", "MAGAZINE", "BULLETS", "RIFLE", "STEN GUN",
        "ගිනි අවි", "වෙඩි උණ්ඩ", "බෝම්බ", "පිස්තෝල", "T-56", "ස්ටෙන් ගන්", "උණ්ඩ", "රයිෆල්"
    ],
    "Protests & Strikes": [
        "PROTEST", "STRIKE", "DEMONSTRATION", "UNION", "MARCH", "DHARNA", "SATYAGRAHA", "BANDH", "HARTAL",
        "උද්ඝෝෂණ", "වැඩ වර්ජන", "සත්‍යග්‍රහ", "උපවාස", "උද්ෝෂණ", "හර්තාල්"
    ],
    "PNB/Navy Recoveries": [
        "PNB", "POLICE NARCOTICS BUREAU", "NAVY", "HARBOUR", "FISHING VESSEL", "HANDOVER",
        "SEALED PACKETS", "HEROIN BLOCKS", "CHARAS", "ICE", "METHAMPHETAMINE", "Ganja", "Kasippu",
        "මත්ද්‍රව්‍ය", "නාවික හමුදා", "වරාය", "ධාවනය", "හෙරොයින්", "අයිස්", "ගංජා", "කසිප්පු"
    ],
    "Explosives & Bombs": [
        "IED", "IMPROVISED EXPLOSIVE DEVICE", "DETONATOR", "FUSE", "DYNAMITE", "GELIGNITE", "TIMER", "CELL-PHONE TRIGGER",
        "පිපිරවීම්", "ඩයිනමයිට්", "ජෙලිග්නයිට්", "බෝම්බ", "විදුලි උණ්ඩ", "ටයිමර්"
    ]
}

# Merge into main KEYWORDS_SINHALA for unified routing/matrix logic
KEYWORDS_SINHALA.update(SECURITY_KEYWORDS)

# =============================================================================
# HELPER: Check if incident belongs to Security Report
# =============================================================================
def is_security_incident(body_text: str, station: str = "", category_num: str = "") -> bool:
    """
    Quick heuristic check to route incidents to Security vs General reports.
    Returns True if content matches security patterns or category is specialized.
    """
    # 1. Category-based routing (Institutional standard)
    # 01:Terrorism, 02:Weapons, 03:Demonstrations, 20:Narcotics, 22:Military
    if str(category_num).zfill(2) in ("01", "02", "03", "20", "22"):
        return True
    if not body_text:
        return False
    
    combined = (body_text + " " + station).upper()
    
    # High-confidence security triggers
    security_triggers = [
        "PNB", "POLICE NARCOTICS BUREAU", "NAVY", "HARBOUR", "FISHING VESSEL",
        "T-56", "M-16", "STEN GUN", "GRENADE", "MAGAZINE", "BULLETS",
        "IED", "DYNAMITE", "GELIGNITE", "DETONATOR", "BLAST", "EXPLOSION",
        "SUBVERSIVE", "LTTE", "TERROR", "SUICIDE ATTACK",
        "HEROIN", "ICE", "METHAMPHETAMINE", "NARCOTICS",
        "ගිනි අවි", "වෙඩි උණ්ඩ", "බෝම්බ", "ත්‍රස්ත", "ප්‍රහාර", "නාවික", "වරාය",
        "මත්ද්‍රව්‍ය", "මත්ද්රව්ය", "හෙරොයින්", "අයිස්"
    ]
    
    return any(trigger in combined for trigger in security_triggers)