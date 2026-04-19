"""
station_mapping.py
==================
Mapping of Sinhala Station/Division names to English and Province mapping.
Used by pipeline_utils.py and desktop_pipeline.py for geo-enrichment.
"""

# Dictionary mapping Sinhala Station/Division names to English
# OCR errors from user input have been corrected here.
SINHALA_TO_ENGLISH = {
    # Western Province
    "කොළඹ": "COLOMBO",
    "කොළඹ මහ": "FORT",
    "පේට්ටා": "PETTAH",
    "මරදාන": "MARADANA",
    "බොරැල්ල": "BORELLA",
    "නාරාහේන්පිට": "NARAHENPITA",
    "කිරුළප්පොන": "KIRULAPONE",
    "වැල්ලවත්ත": "WELLAWATTE",
    "දෙහිවල": "DEHIWALA",
    "ගල්කිස්ස": "DEHIWALA",
    "මවුන්ට් ලැවිනියා": "MOUNT LAVINIA",
    "මොරටුව": "MORATUWA",
    "රත්මලාන": "RATMALANA",
    "කේස්බෑව": "KESBEWA",
    "පිළියන්දල": "PILIYANDALA",
    "හෝමාගම": "HOMAGAMA",
    "නුගේගොඩ": "NUGEGODA",
    "මහරගම": "MAHARAGAMA",
    "කොට්ටාව": "KOTTAWA",
    "පන්නිපිටිය": "PANNIPITIYA",
    "කඩුවෙල": "KADUWELA",
    "මාළඹේ": "MALABE",
    "කොලොන්නාව": "KOLONNAWA",
    "මුල්ලේරියාව": "MULLERIYAWA",
    "බියගම": "BIYAGAMA",
    "පේලියගොඩ": "PELIYAGODA",
    "වත්තල": "WATTALA",
    "හේදල": "HENDALA",
    "රාගම": "RAGAMA",
    "ජා-ඇල": "JA-ELA",
    "සීදුව": "SEEDUWA",
    "කටුනායක": "KATUNAYAKE",
    "ඒකල": "EKALA",
    "ගම්පහ": "GAMPAHA",
    "නිට්ටඹුව": "NITTAMBUWA",
    "මිරිගම": "MIRIGAMA",
    "මිනුවන්ගොඩ": "MINUWANGODA",
    "දිවුලපිටිය": "DIVULAPITIYA",
    "වේයන්ගොඩ": "VEYANGODA",
    "අත්තනගල්ල": "ATTANAGALLA",
    "ගණේමුල්ල": "GANEMULLA",
    "මීගමුව": "NEGOMBO",
    "කටාන": "KATANA",
    "කැලණිය": "KELANIYA",
    "කිරිබත්ගොඩ": "KIRIBATHGODA",
    "පානදුර": "PANADURA",
    "කළුතර": "KALUTARA",
    "බේරුවල": "BERUWALA",
    "අළුත්ගම": "ALUTHGAMA",
    "බණ්ඩාරගම": "BANDARAGAMA",
    "හොරණ": "HORANA",
    "ඉංගිරිය": "INGIRIYA",
    "මාතුගම": "MATHUGAMA",
    "අගලවත්ත": "AGALAWATTA",
    "බුලත්සිංහල": "BULATHSINHALA",
    "ශ්‍රී ජයවර්ධනපුර": "SRI JAYAWARDENEPURA",

    # Southern Province
    "ගාල්ල": "GALLE",
    "හික්කඩුව": "HIKKADUWA",
    "අම්බලන්ගොඩ": "AMBALANGODA",
    "ඇල්පිටිය": "ELPITIYA",
    "අහංගම": "AHANGAMA",
    "මාතර": "MATARA",
    "වැල්ලම": "WELIGAMA",
    "හම්බන්තොට": "HAMBANTOTA",
    "තංගල්ල": "TANGALLE",
    "තිස්සමහාරාම": "TISSAMAHARAMA",
    "හිනිඳුම": "HINIDUMA",

    # Central Province
    "කන්ද": "KANDY",
    "මහනුවර": "KANDY",
    "පේරාදෙණිය": "PERADENIYA",
    "කටුගස්තොට": "KATUGASTOTA",
    "මාතලේ": "MATALE",
    "දඹුල්ල": "DAMBULLA",
    "සීගිරිය": "SIGIRIYA",
    "නුවරඑළිය": "NUWARA ELIYA",
    "හැටන්": "HATTON",
    "තලවාකැලේ": "TALAWAKELLE",
    "මධ්ය මාර්ගය": "CENTRAL CAMP",

    # North Western Province
    "කුරුණෑගල": "KURUNEGALA",
    "කුළියාපිටිය": "KULIYAPITIYA",
    "නිකවෙරටිය": "NIKAWERATIYA",
    "අඹන්පොළ": "AMBANPOLA",
    "පුත්තලම": "PUTTALAM",
    "හලාවත": "CHILAW",
    "වෙන්නප්පුව": "WENNAPPUWA",

    # North Central Province
    "අනුරාධපුරය": "ANURADHAPURA",
    "කැකිරාව": "KEKIRAWA",
    "මේදවච්චිය": "MEDAWACHCHIYA",
    "පොළොන්නරුව": "POLONNARUWA",
    "මානම්පිටිය": "MANAMPITIYA",
    "හිංගුරක්ගොඩ": "HINGURAKGODA",

    # Uva Province
    "බදුල්ල": "BADULLA",
    "බණ්ඩාරවෙල": "BANDARAWELA",
    "වෙලිමඩ": "WELIMADA",
    "හාපුතලේ": "HAPUTALE",
    "මොනරාගල": "MONARAGALA",
    "වැල්ලවාය": "WELLAWAYA",
    "බිබිල": "BIBILE",
    "පද්දුල්ල": "PADDULLA",

    # Sabaragamuwa Province
    "රත්නපුරය": "RATNAPURA",
    "එඹිලිපිටිය": "EMBILIPITIYA",
    "බලංගොඩ": "BALANGODA",
    "කෑගල්ල": "KEGALLE",
    "මාවනැල්ල": "MAWANELLA",
    "රුවන්වැල්ල": "RUWANWELLA",

    # Northern Province
    "යාපනය": "JAFFNA",
    "චාවකච්චේරි": "CHAVAKACHCHERI",
    "වව්නියා": "VAVUNIYA",
    "මූලතිව්": "MULLAITIVU",
    "කිලිනොච්චි": "KILINOCHCHI",
    "මන්නාරම": "MANNAR",

    # Eastern Province
    "ත්‍රිකුණාමලය": "TRINCOMALEE",
    "කන්නිය": "KINNIYA",
    "මුතූර්": "MUTUR",
    "මඩකලපුව": "BATTICALOA",
    "කල්මුණේ": "KALMUNAI",
    "අම්පාර": "AMPARA",
    
    # Misc / Others (Corrected from OCR errors)
    "මහබාගේ": "MAHABAGE",
    "කිරිදිවෙල": "KIRIDIWELA",
    "පිටිගල": "PITIGALA",
    "නාවගමුව": "NAWAGAMUWA",
    "වඩමල්ලගම": "WADAMALAGAMA",
    "මාළඹේ": "MALABE", # Duplicate key check handled by dict
}

# Mapping of Districts/Divisions to Provinces
REGION_TO_PROVINCE = {
    "GALLE": "SOUTHERN PROVINCE",
    "HINIDUMA": "SOUTHERN PROVINCE",
    "AHANGAMA": "SOUTHERN PROVINCE",
    "TANGALLE": "SOUTHERN PROVINCE",
    "MATARA": "SOUTHERN PROVINCE",
    "FORT": "WESTERN PROVINCE",
    "PETTAH": "WESTERN PROVINCE",
    "MARADANA": "WESTERN PROVINCE",
    "BORELLA": "WESTERN PROVINCE",
    "NARAHENPITA": "WESTERN PROVINCE",
    "KIRULAPONE": "WESTERN PROVINCE",
    "WELLAWATTE": "WESTERN PROVINCE",
    "DEHIWALA": "WESTERN PROVINCE",
    "MOUNT LAVINIA": "WESTERN PROVINCE",
    "MORATUWA": "WESTERN PROVINCE",
    "RATMALANA": "WESTERN PROVINCE",
    "KESBEWA": "WESTERN PROVINCE",
    "PILIYANDALA": "WESTERN PROVINCE",
    "HOMAGAMA": "WESTERN PROVINCE",
    "NUGEGODA": "WESTERN PROVINCE",
    "MAHARAGAMA": "WESTERN PROVINCE",
    "KOTTAWA": "WESTERN PROVINCE",
    "PANNIPITIYA": "WESTERN PROVINCE",
    "KADUWELA": "WESTERN PROVINCE",
    "MALABE": "WESTERN PROVINCE",
    "KOLONNAWA": "WESTERN PROVINCE",
    "MULLERIYAWA": "WESTERN PROVINCE",
    "BIYAGAMA": "WESTERN PROVINCE",
    "PELIYAGODA": "WESTERN PROVINCE",
    "WATTALA": "WESTERN PROVINCE",
    "HENDALA": "WESTERN PROVINCE",
    "RAGAMA": "WESTERN PROVINCE",
    "JA-ELA": "WESTERN PROVINCE",
    "SEEDUWA": "WESTERN PROVINCE",
    "KATUNAYAKE": "WESTERN PROVINCE",
    "EKALA": "WESTERN PROVINCE",
    "GAMPAHA": "WESTERN PROVINCE",
    "NITTAMBUWA": "WESTERN PROVINCE",
    "MIRIGAMA": "WESTERN PROVINCE",
    "MINUWANGODA": "WESTERN PROVINCE",
    "DIVULAPITIYA": "WESTERN PROVINCE",
    "VEYANGODA": "WESTERN PROVINCE",
    "ATTANAGALLA": "WESTERN PROVINCE",
    "GANEMULLA": "WESTERN PROVINCE",
    "NEGOMBO": "WESTERN PROVINCE",
    "KATANA": "WESTERN PROVINCE",
    "KELANIYA": "WESTERN PROVINCE",
    "KIRIBATHGODA": "WESTERN PROVINCE",
    "PANADURA": "WESTERN PROVINCE",
    "KALUTARA": "WESTERN PROVINCE",
    "BERUWALA": "WESTERN PROVINCE",
    "ALUTHGAMA": "WESTERN PROVINCE",
    "BANDARAGAMA": "WESTERN PROVINCE",
    "HORANA": "WESTERN PROVINCE",
    "INGIRIYA": "WESTERN PROVINCE",
    "MATHUGAMA": "WESTERN PROVINCE",
    "AGALAWATTA": "WESTERN PROVINCE",
    "BULATHSINHALA": "WESTERN PROVINCE",
    "SRI JAYAWARDENEPURA": "WESTERN PROVINCE",
    "MAHABAGE": "WESTERN PROVINCE",
    "NAWAGAMUWA": "WESTERN PROVINCE",
    "KIRIDIWELA": "WESTERN PROVINCE",
    "PADDULLA": "UVA PROVINCE",
    "BIBILE": "UVA PROVINCE",
    "KANDY": "CENTRAL PROVINCE",
    "PERADENIYA": "CENTRAL PROVINCE",
    "KATUGASTOTA": "CENTRAL PROVINCE",
    "MATALE": "CENTRAL PROVINCE",
    "DAMBULLA": "CENTRAL PROVINCE",
    "SIGIRIYA": "CENTRAL PROVINCE",
    "NUWARA ELIYA": "CENTRAL PROVINCE",
    "HATTON": "CENTRAL PROVINCE",
    "TALAWAKELLE": "CENTRAL PROVINCE",
    "CENTRAL CAMP": "CENTRAL PROVINCE",
    "HIKKADUWA": "SOUTHERN PROVINCE",
    "AMBALANGODA": "SOUTHERN PROVINCE",
    "ELPITIYA": "SOUTHERN PROVINCE",
    "WELIGAMA": "SOUTHERN PROVINCE",
    "HAMBANTOTA": "SOUTHERN PROVINCE",
    "TISSAMAHARAMA": "SOUTHERN PROVINCE",
    "KURUNEGALA": "NORTH WESTERN PROVINCE",
    "KULIYAPITIYA": "NORTH WESTERN PROVINCE",
    "NIKAWERATIYA": "NORTH WESTERN PROVINCE",
    "AMBANPOLA": "NORTH WESTERN PROVINCE",
    "PUTTALAM": "NORTH WESTERN PROVINCE",
    "CHILAW": "NORTH WESTERN PROVINCE",
    "WENNAPPUWA": "NORTH WESTERN PROVINCE",
    "ANURADHAPURA": "NORTH CENTRAL PROVINCE",
    "KEKIRAWA": "NORTH CENTRAL PROVINCE",
    "MEDAWACHCHIYA": "NORTH CENTRAL PROVINCE",
    "POLONNARUWA": "NORTH CENTRAL PROVINCE",
    "MANAMPITIYA": "NORTH CENTRAL PROVINCE",
    "HINGURAKGODA": "NORTH CENTRAL PROVINCE",
    "BADULLA": "UVA PROVINCE",
    "BANDARAWELA": "UVA PROVINCE",
    "WELIMADA": "UVA PROVINCE",
    "HAPUTALE": "UVA PROVINCE",
    "MONARAGALA": "UVA PROVINCE",
    "WELLAWAYA": "UVA PROVINCE",
    "RATNAPURA": "SABARAGAMUWA PROVINCE",
    "EMBILIPITIYA": "SABARAGAMUWA PROVINCE",
    "BALANGODA": "SABARAGAMUWA PROVINCE",
    "KEGALLE": "SABARAGAMUWA PROVINCE",
    "MAWANELLA": "SABARAGAMUWA PROVINCE",
    "RUWANWELLA": "SABARAGAMUWA PROVINCE",
    "JAFFNA": "NORTHERN PROVINCE",
    "CHAVAKACHCHERI": "NORTHERN PROVINCE",
    "VAVUNIYA": "NORTHERN PROVINCE",
    "MULLAITIVU": "NORTHERN PROVINCE",
    "KILINOCHCHI": "NORTHERN PROVINCE",
    "MANNAR": "NORTHERN PROVINCE",
    "TRINCOMALEE": "EASTERN PROVINCE",
    "KINNIYA": "EASTERN PROVINCE",
    "MUTUR": "EASTERN PROVINCE",
    "BATTICALOA": "EASTERN PROVINCE",
    "KALMUNAI": "EASTERN PROVINCE",
    "AMPARA": "EASTERN PROVINCE",
    "PITIGALA": "SOUTHERN PROVINCE",
    "WADAMALAGAMA": "WESTERN PROVINCE",
}


def clean_sinhala(text: str) -> str:
    """Clean input text (strip whitespace)."""
    if not text:
        return ""
    return text.strip()


def get_geo_info(sinhala_text: str) -> dict:
    """
    Extract Station and Province from Sinhala text.
    Prioritizes longer matches (e.g., "Sri Jayawardenepura" over "Jayawardenepura").
    """
    if not sinhala_text:
        return {"station": "UNKNOWN", "province": "UNKNOWN"}
    
    cleaned = clean_sinhala(sinhala_text)
    found_station = "UNKNOWN"
    found_province = "UNKNOWN"
    
    # Sort keys by length (descending) to match specific stations before general ones
    # e.g., Match "කොළඹ මහ" before "කොළඹ"
    sorted_keys = sorted(SINHALA_TO_ENGLISH.keys(), key=len, reverse=True)
    
    for s_word in sorted_keys:
        if s_word in cleaned:
            found_station = SINHALA_TO_ENGLISH[s_word]
            break
            
    if found_station != "UNKNOWN" and found_station in REGION_TO_PROVINCE:
        found_province = REGION_TO_PROVINCE[found_station]
        
    return {"station": found_station, "province": found_province}


def get_station_info(station_name: str) -> dict:
    """
    Wrapper for get_geo_info to support pipeline_utils.py calls.
    If input is English, tries to map province directly.
    """
    if not station_name:
        return {"station": "UNKNOWN", "province": "UNKNOWN", "dig": "", "div": ""}
        
    # If input is likely English (no Sinhala chars), check province map directly
    if not any("\u0D80" <= char <= "\u0DFF" for char in station_name):
        eng_name = station_name.upper().strip()
        province = REGION_TO_PROVINCE.get(eng_name, "UNKNOWN")
        return {"station": eng_name, "province": province, "dig": "", "div": ""}
        
    # Otherwise run standard Sinhala extraction
    result = get_geo_info(station_name)
    result["dig"] = "" # Placeholder
    result["div"] = "" # Placeholder
    return result


if __name__ == "__main__":
    test_cases = [
        "හිනිඳුම OTM 1480 ගාල්ල",
        "කුරුණෑගල CTM 555 කැලණිය",
        "බිබිල OTM 1532 මොනරාගල",
        "කොළඹ මහ පේට්ටා", # Should match Fort/Pettah
        "ශ්‍රී ජයවර්ධනපුර කෝට්ටේ", # Should match Sri Jayawardenepura
    ]
    print("Running self-test...")
    for tc in test_cases:
        res = get_geo_info(tc)
        print(f"Input: {tc}")
        print(f"  -> Station: {res['station']}, Province: {res['province']}")
        print("-" * 40)