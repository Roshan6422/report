import re

def normalize_sinhala(text):
    """
    Cleans PDF extraction artifacts specific to Sri Lanka Police reports.
    """
    if not text: return ""
    
    repairs = {
        "වහ": "ස", "ෆී": "රු", "ළ": "ල", "඿": "ෂ", "඼": "ල", "තී": "ත්‍ර",
        "මිනීමෆ": "මිනීමැ", "වවො": "සො", "සලො": "සො", "සවො": "සො", "සරො": "කො",
        "සර්": "ක්", " උ්ඩ": " උණ්ඩ", "වෆර": "සැක", "ඳෆය": "පැය", "වහථ": "ස්ථා",
        "ලටිනළ": "වටිනා"
    }
    for old, new in repairs.items():
        text = text.replace(old, new)
    return text

def split_by_sections(raw_text, report_type="General"):
    """
    Full 29-Category Splitter based on the Official Sri Lanka Police Table.
    """
    clean_text = normalize_sinhala(raw_text)

    # 29 OFFICIAL CATEGORIES
    CATEGORIES = [
        {"id": "01", "name": "ත්‍රස්තවාදී ක්‍රියාකාරකම්", "fingers": ["ත්‍රස්තවාදී", "ත්‍රවහතලළදී", "Terrorist"]},
        {"id": "02", "name": "අවි ආයුධ සොයාගැනීම", "fingers": ["අවි", "ආයුධ", "උණ්ඩ", "පුපුරණ", "Arms"]},
        {"id": "03", "name": "උද්ඝෝෂණ", "fingers": ["උද්ඝෝෂණ", "විරෝධතා", "පැවැත්වීම", "Protest"]},
        {"id": "04", "name": "මනුෂ්‍ය ඝාතන", "fingers": ["මනුෂ්‍ය", "ඝාතන", "මිනීමැරී", "Homicide"]},
        {"id": "05", "name": "කොල්ලකෑම්", "fingers": ["කොල්ලකෑම්", "ආයුධ මගින්", "Robbery"]},
        {"id": "06", "name": "වාහන සොරකම්", "fingers": ["වාහන", "සොරකම්", "Vehicle"]},
        {"id": "07", "name": "දේපල සොරකම්", "fingers": ["දේපල", "සොරකම්", "Theft"]},
        {"id": "08", "name": "ගෙවල් බිඳුම්", "fingers": ["ගෙවල්", "බිඳුම්", "Burglary"]},
        {"id": "09", "name": "ස්ත්‍රී දූෂණ", "fingers": ["ස්ත්‍රී", "දූෂණ", "ලිංගික", "Rape"]},
        {"id": "10", "name": "මාරක රිය අනතුරු", "fingers": ["මාරක", "රිය", "අනතුරු", "Fatal"]},
        {"id": "11", "name": "නාඳුනන මළ සිරුරු", "fingers": ["නාඳුනන", "මළ", "සිරුරු", "මරණ", "Dead bodies"]},
        {"id": "12", "name": "පොලිස් රිය අනතුරු", "fingers": ["පොලිස්", "රිය", "අනතුරු", "Accidents"]},
        {"id": "13", "name": "තුවාල සිදුවීම", "fingers": ["නිලධාරීන්ට", "තුවාල", "පොලිසිය සම්බන්ධ", "Injuries"]},
        {"id": "14", "name": "විෂමාචාර ක්‍රියා", "fingers": ["විෂමාචාර", "ක්‍රියා", "Misconduct"]},
        {"id": "15", "name": "පොලිස් නිලධාරීන් මියයාම", "fingers": ["නිලධාරීන්", "මියයාම", "Deaths"]},
        {"id": "16", "name": "හඳුනාගත් නිලධාරීන්", "fingers": ["රාජ්‍ය නිවේදිත", "රෝහල්", "ගතවීම", "Hospital"]},
        {"id": "17", "name": "ඥාතීන් මියයාම", "fingers": ["රාජ්‍ය නිවේදිත", "ඥාතීන්", "මියයාම"]},
        {"id": "18", "name": "විශ්‍රාමික ඥාතීන්", "fingers": ["විශ්‍රාමික", "ඥාතීන්"]},
        {"id": "19", "name": "නිවාඩු ලබා සිටින", "fingers": ["නිවාඩු", "ජ්‍යෙ.නි.පො"]},
        {"id": "20", "name": "මත් ද්‍රව්‍ය / මත්පැන්", "fingers": ["මත් ද්‍රව්‍ය", "මත්පැන්", "අත්අඩංගුවට", "Narcotics"]},
        {"id": "21", "name": "අත්අඩංගුවට ගැනීම්", "fingers": ["අත්අඩංගුවට", "ගැනීම්", "Arrests"]},
        {"id": "22", "name": "ත්‍රිවිධ හමුදා", "fingers": ["ත්‍රිවිධ හමුදා", "අපරාධ"]},
        {"id": "23", "name": "අතුරුදහන්වීම්", "fingers": ["අතුරුදහන්වීම්", "Missing"]},
        {"id": "24", "name": "සියදිවි හානිකර ගැනීම්", "fingers": ["සියදිවි", "හානිකර", "Suicide"]},
        {"id": "25", "name": "විදේශ ජාතිකයින්", "fingers": ["විදේශ", "ජාතිකයින්", "Foreigners"]},
        {"id": "26", "name": "වන අලි පහරදීම්", "fingers": ["වන අලි", "පහරදීම්", "Elephants"]},
        {"id": "27", "name": "දියේ ගිලී මියයාම්", "fingers": ["දියේ ගිලී", "මියයාම්", "Drowning"]},
        {"id": "28", "name": "ගිනි ගැනීම්", "fingers": ["ගිනි ගැනීම්", "Fire"]},
        {"id": "29", "name": "වෙනත් විශේෂ සිද්ධීන්", "fingers": ["වෙනත්", "විශේෂ", "සිද්ධීන්", "Other"]}
    ]

    official_titles = [f"{c['id']}. {c['name']}" for c in CATEGORIES]
    found_content = {title: [] for title in official_titles}
    current_title = None

    lines = clean_text.split('\n')
    # More robust pattern: starts with number, then dot/space
    header_num_pat = r"^\s*(?:[0-9]{1,2}|[IVX]{1,3})[\.\s\)\]\-\:]+"

    for line in lines:
        l_strip = line.strip()
        if not l_strip:
            if current_title: found_content[current_title].append(line)
            continue

        matched_title = None
        # Check for numeric header OR direct category name mention
        for cat in CATEGORIES:
            # Match if line starts with ID or contains enough keywords (fingers)
            starts_with_id = re.match(r"^\s*" + cat["id"] + r"[\.\s]", l_strip)
            has_keywords = any(f in l_strip for f in cat["fingers"])
            
            if (starts_with_id or has_keywords) and len(l_strip) < 180:
                matched_title = f"{cat['id']}. {cat['name']}"
                break
        
        if matched_title:
            current_title = matched_title
            found_content[current_title].append(line)
        elif current_title:
            found_content[current_title].append(line)
        else:
            # Add to 'Other' or first category if no header found yet
            found_content[official_titles[-1]].append(line)

    return [(t, "\n".join(found_content[t]).strip()) for t in official_titles]
