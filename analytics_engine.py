"""
analytics_engine.py — Police Report Statistics and Data Aggregation
==================================================================
Handles the automatic calculation of the 28-row Case Data Breakdown 
and the 9x10 Summary Matrix from extracted incident logs.

System Version: v2.1.0
"""

import re
from translation_vocabulary import KEYWORDS_SINHALA

def calculate_case_data(data):
    """Calculates the 28-row Case Breakdown Table automatically."""
    counts = [0] * 28
    solved_counts = [0] * 28
    
    for s in data.get("sections", []):
        for prov in s.get("provinces", []):
            for inc in prov.get("incidents", []):
                station_name = inc.get("station", "").upper()
                body_text = inc.get("body", "").upper()
                text_to_match = (body_text + " " + station_name).upper()
                section_title = s.get("title", "").upper()
                
                # Extract multi-case multiplier e.g. "(5 cases)"
                mult_match = re.search(r'\((\d+)\s*CASES?\)', text_to_match)
                weight = int(mult_match.group(1)) if mult_match else 1
                
                category_map = {
                    0: [r"\bSUBVERSIVE\b", r"\bTERRORIST\b"],
                    1: [r"\bRECOVER\b", r"\bWEAPON\b", r"\bPISTOL\b", r"\bGRENADE\b", r"\bAMMUNITION\b"],
                    2: [r"\bPROTEST\b", r"\bSTRIKE\b", r"\bDEMONSTRATION\b"],
                    3: [r"\bMURDER\b", r"\bHOMICIDE\b", r"\bFATAL ASSAULT\b", r"\bSTABBED TO DEATH\b"],
                    4: [r"\bROBBERY\b", r"\bROBBED\b", r"\bSNATCHING\b"],
                    5: [r"\bMOTORCYCLE\b.*\bSTOLEN\b", r"\bVEHICLE STOLEN\b", r"\bTHREE.WHEELER.*STOLEN\b"],
                    6: [r"\bTHEFT\b", r"\bSTOLEN\b"],
                    7: [r"\bHOUSE BREAK\b", r"\bBURGLARY\b", r"\bBREAKING.*DOOR\b", r"\bBREAKING.*WINDOW\b"],
                    8: [r"\bRAPE\b", r"\bSEXUAL ABUSE\b", r"\bCHILD ABUSE\b", r"\bSEXUALLY ABUSED\b"],
                    9: [r"\bFATAL ACCIDENT\b"],
                    10: [r"\bDEAD BODY\b", r"\bFOUND DEAD\b", r"\bDECOMPOSED BODY\b", r"\bSUSPICIOUS DEATH\b"],
                    11: [r"\bPOLICE MOTORCYCLE\b", r"\bPOLICE VEHICLE\b", r"\bPOLICE JEEP\b"],
                    12: [r"\bPOLICE OFFICER WAS INJURED\b", r"\bOFFICER.*ASSAULTED\b"],
                    13: [r"\bCHARGED IN COURT\b", r"\bMISCONDUCT\b", r"\bCOMPLAINT.*POLICE\b", r"\bIDENTITY CARD.*MISPLACED\b", r"\bABSENT FROM DUTY\b"],
                    14: [r"\bPOLICE.*DIED\b", r"\bDEATH OF POLICE\b", r"\bPASSED AWAY\b", r"\bDIED.*ILLNESS\b"],
                    15: [r"\bHOSPITALIZED\b", r"\bADMITTED TO HOSPITAL\b", r"\bHOSPITAL ADMISSION\b"],
                    16: [r"\bCLOSE RELATIVE.*DIED\b", r"\bPASSING AWAY.*RELATIVE\b"],
                    17: [r"\bRETIRED.*DIED\b", r"\bRETIRED.*PASSING\b"],
                    18: [r"\bCANNABIS\b", r"\bICE\b", r"\bHEROIN\b", r"\bLIQUOR\b", r"\bNARCOTIC\b"],
                    19: [r"\bARRESTED\b", r"\bAPPREHENDED\b"],
                    20: [r"\bSOLDIER\b", r"\bARMY\b", r"\bNAVY\b", r"\bTRI.FORCE\b"],
                    21: [r"\bMISSING\b", r"\bDISAPPEAR\b"],
                    22: [r"\bSUICIDE\b", r"\bHANGING\b"],
                    23: [r"\bFOREIGNER\b", r"\bTOURIST\b", r"\bFOREIGN NATIONAL\b"],
                    24: [r"\bELEPHANT\b"],
                    25: [r"\bDROWN\b"],
                    26: [r"\bFIRE\b"]
                }
                
                matched_any = False
                matched_idx = -1
                for idx, keywords in category_map.items():
                    if idx == 9 and ("ACCIDENT" in section_title and "FATAL" in section_title):
                        counts[idx] += weight; matched_any = True; matched_idx = idx; break
                    
                    if idx == 11:
                        if (any(re.search(x, text_to_match) for x in [r"\bPOLICE MOTORCYCLE\b", r"\bPOLICE VEHICLE\b"]) and 
                            re.search(r"\bACCIDENT\b", text_to_match)):
                            counts[idx] += weight; matched_any = True; matched_idx = idx; break
                        continue

                    if any(re.search(x, text_to_match) for x in keywords):
                        if idx == 6 and (re.search(r"\bMOTORCYCLE\b", text_to_match) or re.search(r"\bVEHICLE\b", text_to_match)):
                            continue
                        counts[idx] += weight; matched_any = True; matched_idx = idx; break
                
                if not matched_any:
                    matched_idx = 27
                    counts[27] += weight
                
                if any(x in body_text for x in ["ARREST", "APPREHEND", "REMAND", "RECOVER"]):
                    solved_counts[matched_idx] += weight
                    
    case_data = []
    for i in range(28):
        case_data.append({
            "reported": str(counts[i]),
            "solved": str(solved_counts[i]),
            "unsolved": str(max(0, counts[i] - solved_counts[i]))
        })
    return case_data

def calculate_summary_matrix(data):
    """Calculates the 9x10 matrix matching official Police dimensions."""
    crime_types = [
        "Theft", "HB & Theft", "Robberies and Armed Robberies", 
        "Rape & Sexual Abuse", "Homicide", "Police Accidents", 
        "Fatal Accidents", "Others"
    ]
    provinces = [
        "Western", "Sabaragamuwa", "Southern", "Uva", "Central",
        "North Western", "North Central", "Eastern", "Northern"
    ]
    matrix = {"headers": crime_types, "rows": [], "totals": [0]*len(crime_types)}
    
    for p_name in provinces:
        row = {"province": p_name + " Province", "values": [0]*len(crime_types)}
        for s in data.get("sections", []):
            s_title = s.get("title", "").upper()
            title_match = -1
            for i, ct in enumerate(crime_types):
                if any(kw in s_title for kw in KEYWORDS_SINHALA.get(ct, [])): 
                    title_match = i; break
            
            for p in s.get("provinces", []):
                if p_name.upper() in p.get("name", "").upper():
                    for inc in p.get("incidents", []):
                        body = inc.get("body", "").upper()
                        match_idx = title_match
                        if match_idx == -1:
                            for i, ct in enumerate(crime_types):
                                if any(kw in body for kw in KEYWORDS_SINHALA.get(ct, [])):
                                    match_idx = i; break
                                    
                        if match_idx == -1: match_idx = len(crime_types) - 1
                        if match_idx != -1:
                            row["values"][match_idx] += 1
                            matrix["totals"][match_idx] += 1
        
        row["grand_total"] = sum(row["values"])
        matrix.get("rows").append(row)
    
    matrix["grand_total_all"] = sum(matrix["totals"])
    return matrix
