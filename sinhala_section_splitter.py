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
        {"id": "01", "name": "ත්‍රස්තවාදී ක්‍රියාකාරකම්", "fingers": ["ත්‍රස්තවාදී", "ත්‍රවහතලළදී"]},
        {"id": "02", "name": "අවි ආයුධ සොයාගැනීම", "fingers": ["අවි", "ආයුධ", "උණ්ඩ", "පුපුරණ"]},
        {"id": "03", "name": "උද්ඝෝෂණ", "fingers": ["උද්ඝෝෂණ", "විරෝධතා", "පැවැත්වීම"]},
        {"id": "04", "name": "මනුෂ්‍ය ඝාතන", "fingers": ["මනුෂ්‍ය", "ඝාතන", "මිනීමැරී"]},
        {"id": "05", "name": "කොල්ලකෑම් / අවි ආයුධ මගින් කොල්ලකෑම්", "fingers": ["කොල්ලකෑම්", "ආයුධ මගින්"]},
        {"id": "06", "name": "වාහන සොරකම්", "fingers": ["වාහන", "සොරකම්", "වවොොරරම"]},
        {"id": "07", "name": "දේපල සොරකම්", "fingers": ["දේපල", "සොරකම්"]},
        {"id": "08", "name": "ගෙවල් බිඳුම්", "fingers": ["ගෙවල්", "බිඳුම්"]},
        {"id": "09", "name": "ස්ත්‍රී දූෂණ හා බරපතල ලිංගික අපයෝජන", "fingers": ["ස්ත්‍රී", "දූෂණ", "ලිංගික", "අපයෝජන"]},
        {"id": "10", "name": "මාරක රිය අනතුරු", "fingers": ["මාරක", "රිය", "අනතුරු"]},
        {"id": "11", "name": "නාඳුනන මළ සිරුරු හා සැක සහිත මරණ", "fingers": ["නාඳුනන", "මළ", "සිරුරු", "සැක සහිත", "මරණ"]},
        {"id": "12", "name": "පොලිස් රිය අනතුරු", "fingers": ["පොලිස්", "රිය", "අනතුරු"]},
        {"id": "13", "name": "පොලිස් නිලධාරීන්ට තුවාල සිදුවීම සහ පොලිසිය සම්බන්ධ සිද්ධි", "fingers": ["නිලධාරීන්ට", "තුවාල", "පොලිසිය සම්බන්ධ"]},
        {"id": "14", "name": "පොලිස් නිලධාරීන්ගේ විෂමාචාර ක්‍රියා", "fingers": ["විෂමාචාර", "ක්‍රියා"]},
        {"id": "15", "name": "පොලිස් නිලධාරීන් මියයාම", "fingers": ["නිලධාරීන්", "මියයාම"]},
        {"id": "16", "name": "රාජ්‍ය නිවේදිත නිලධාරීන් රෝහල් ගතවීම", "fingers": ["රාජ්‍ය නිවේදිත", "රෝහල්", "ගතවීම"]},
        {"id": "17", "name": "රාජ්‍ය නිවේදිත නිලධාරීන්ගේ ළඟම ඥාතීන් මියයාම", "fingers": ["රාජ්‍ය නිවේදිත", "ඥාතීන්", "මියයාම"]},
        {"id": "18", "name": "විශ්‍රාමික රාජ්‍ය නිවේදිත නිලධාරීන්ගේ ළඟම ඥාතීන් මියයාම", "fingers": ["විශ්‍රාමික", "රාජ්‍ය නිවේදිත", "ඥාතීන්", "මියයාම"]},
        {"id": "19", "name": "නිවාඩු ලබා සිටින ජ්‍යෙ.නි.පො/නි.පො.ප වරුන්", "fingers": ["නිවාඩු", "ජ්‍යෙ.නි.පො", "නි.පො.ප"]},
        {"id": "20", "name": "විශාල ප්‍රමාණයේ මත් ද්‍රව්‍ය/මත්පැන් අත්අඩංගුවට ගැනීම්", "fingers": ["විශාල ප්‍රමාණයේ", "මත් ද්‍රව්‍ය", "මත්පැන්", "අත්අඩංගුවට"]},
        {"id": "21", "name": "අත්අඩංගුවට ගැනීම්", "fingers": ["අත්අඩංගුවට", "ගැනීම්"]},
        {"id": "22", "name": "ත්‍රිවිධ හමුදා සමාජිකයින්ගේ අපරාධ, විෂමාචාර ක්‍රියා හා අත්අඩංගුවට ගැනීම්", "fingers": ["ත්‍රිවිධ හමුදා", "අපරාධ", "විෂමාචාර"]},
        {"id": "23", "name": "අතුරුදහන්වීම්", "fingers": ["අතුරුදහන්වීම්"]},
        {"id": "24", "name": "සියදිවි හානිකර ගැනීම්", "fingers": ["සියදිවි", "හානිකර"]},
        {"id": "25", "name": "විදේශ ජාතිකයින් සම්බන්ධ සිදුවීම්", "fingers": ["විදේශ", "ජාතිකයින්"]},
        {"id": "26", "name": "වන අලි පහරදීම් හා වන අලි මියයාම", "fingers": ["වන අලි", "පහරදීම්", "මියයාම"]},
        {"id": "27", "name": "දියේ ගිලී මියයාම් හා අතුරුදහන් වීම්", "fingers": ["දියේ ගිලී", "මියයාම්", "අතුරුදහන්"]},
        {"id": "28", "name": "ගිනි ගැනීම් සම්බන්ධ සිදුවීම්", "fingers": ["ගිනි ගැනීම්"]},
        {"id": "29", "name": "වෙනත් විශේෂ සිදුවීම්", "fingers": ["වෙනත් විශේෂ"]}
    ]

    official_titles = [f"{c['id']}. {c['name']}" for c in CATEGORIES]
    found_content = {title: [] for title in official_titles}
    current_title = None

    lines = clean_text.split('\n')
    header_num_pat = r"^\s*(?:[0-9]{1,2}|[IVX]{1,3})[\.\s\)\]\-\:]+"

    for line in lines:
        l_strip = line.strip()
        if not l_strip:
            if current_title: found_content[current_title].append(line)
            continue

        matched_title = None
        if re.match(header_num_pat, l_strip):
            # Check for ID and Name match
            for cat in CATEGORIES:
                if (cat["id"] in l_strip[:10] or any(f in l_strip for f in cat["fingers"])) and len(l_strip) < 150:
                    matched_title = f"{cat['id']}. {cat['name']}"
                    break
        
        if matched_title:
            current_title = matched_title
            found_content[current_title].append(line)
        elif current_title:
            found_content[current_title].append(line)
        else:
            found_content[official_titles[-1]].append(line)

    return [(t, "\n".join(found_content[t]).strip() or "Nil") for t in official_titles]
