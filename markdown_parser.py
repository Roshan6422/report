import re
from datetime import datetime, timedelta


def parse_high_fidelity_markdown(markdown_text):
    """
    Expert-level Markdown parser designed for SL Police reports.
    Handles parallelized AI outputs with mixed list/header formatting.
    """
    data = {
        "date_range": "From 0400 hrs. on 18th March 2026 to 0400 hrs. on 19th March 2026",
        "sections": []
    }

    # 1. Date Range extraction (Heuristic)
    date_match = re.search(r'(\d{2}[-‑\.]\d{2}[-‑\.]\d{4})', markdown_text[:500])
    if date_match:
        dt_str = date_match.group(1).replace("‑", "-").replace(".", "-")
        try:
            d2 = datetime.strptime(dt_str, "%d-%m-%Y")
            d1 = d2 - timedelta(days=1)
            def ord_f(d):
                day = d.day
                sfx = 'th' if 11<=day<=13 else {1:'st', 2:'nd', 3:'rd'}.get(day%10, 'th')
                return d.strftime(f"{day}{sfx} %B %Y")
            data["date_range"] = f"From 0400 hrs. on {ord_f(d1)} to 0400 hrs. on {ord_f(d2)}"
        except (ValueError, IndexError):
            pass

    # 2. Partition Sections by Header (## 01. ...)
    # Look for headers like "## 01. SERIOUS CRIMES" or similar
    sections_raw = re.split(r'(?:\r?\n|^)##\s*(?=[0-9]{1,2}\.|[IVX]{1,4}\.)', markdown_text)

    for sec_chunk in sections_raw:
        if not sec_chunk.strip(): continue

        # Extract title from the first line
        lines = sec_chunk.strip().split('\n')
        title = lines[0].strip().rstrip(':').strip()
        body = "\n".join(lines[1:]).strip()

        if not title: continue

        section = {"title": title, "provinces": []}

        # 3. Flat extract all incidents from section content
        # We search for ### [Station Name] markers
        inc_blocks = re.split(r'(?:\r?\n|^)###\s*', body)

        all_section_incidents = []
        # AI filler phrases that indicate empty sections — skip entirely
        AI_FILLER = [
            "no incidents", "no records found", "end of report", "nil", "data summary",
            "source material contained", "no reported incidents", "count verified",
            "no further station", "audit note", "recommendation:", "next steps",
            "processing attempt", "data recovery", "heavily corrupted", "could not be achieved",
            "no verifiable incidents", "summary of processing", "phase 1", "phase 2",
            "phase 3", "phase 4", "not yet been arrested", "zero entries",
        ]

        for block in inc_blocks:
            block = block.strip()
            block_lower = block.lower()
            if not block or block.upper().startswith("STATION"): continue
            if any(filler in block_lower for filler in AI_FILLER): continue

            # Split Title/Station from content
            lines = block.split('\n')
            station_raw = lines[0].strip().replace("**", "").replace("_", "")
            station = re.sub(r'^\d+[\.\s]*', '', station_raw).strip()

            content = "\n".join(lines[1:]).strip()

            # Extract components using keys
            h_match = re.search(r'(?:\*\*Hierarchy\*\*|Hierarchy)[:\s]+([^\r\n]+)', content, re.IGNORECASE)
            s_match = re.search(r'(?:\*\*Summary\*\*|Summary)[:\s]+([\s\S]+?)(?:\r?\n|$)', content, re.IGNORECASE)
            n_match = re.search(r'(?:\*\*Narrative\*\*|Narrative)[:\s]+([\s\S]+?)(?:\s*\- \*\*Reference\*\*|\s*Reference:|\s*\(?[A-Z]{3}[\.\s]?\d+\)?MS|$)', content, re.IGNORECASE)
            r_match = re.search(r'(\(?[A-Z]{3,4}[\.\s]?\d+\)?MS)', content, re.IGNORECASE)

            def _clean_sl_chars(txt):
                if not txt: return ""
                # Strip Sinhala (U+0D80-0DFF) and Tamil (U+0B80-0BFF) script characters,
                # but only if the text is predominantly Latin (English).
                # If text is mostly non-Latin, return as-is to avoid data destruction.
                latin_chars = len(re.findall(r'[a-zA-Z]', txt))
                total_alpha = len(re.findall(r'\w', txt))
                if total_alpha > 0 and latin_chars / total_alpha < 0.3:
                    return txt.strip()  # Mostly non-Latin — don't strip
                return re.sub(r'[\u0D80-\u0DFF\u0B80-\u0BFF]+', '', txt).strip()

            hierarchy_str = _clean_sl_chars(h_match.group(1)) if h_match else ""
            summary = _clean_sl_chars(s_match.group(1)) if s_match else ""
            narrative = _clean_sl_chars(n_match.group(1)) if n_match else content
            ref = _clean_sl_chars(r_match.group(1)) if r_match else ""

            # If no explicit summary but narrative starts with a parenthesis, extract it!
            if not summary and narrative.strip().startswith('('):
                paren_match = re.match(r'^\(([^)]+)\)', narrative.strip())
                if paren_match:
                    summary = paren_match.group(1)
                    narrative = narrative.strip()[len(paren_match.group(0)):].strip()

            # Clean summary (ensure it's in parentheses if not already)
            if summary and not summary.startswith('('): summary = f"({summary})"

            # Clean narrative
            narrative = re.sub(r'(?:\*\*Hierarchy\*\*|Hierarchy)[:\s]+[^\r\n]+', '', narrative, flags=re.IGNORECASE)
            narrative = re.sub(r'(?:\*\*Summary\*\*|Summary)[:\s]+[^\r\n]+', '', narrative, flags=re.IGNORECASE)
            narrative = re.sub(r'(?:\*\*Narrative\*\*|Narrative)[:\s]+', '', narrative, flags=re.IGNORECASE)
            narrative = re.sub(r'[*_]{2,}', '', narrative).strip()
            narrative = narrative.lstrip(':').strip()
            narrative = _clean_sl_chars(narrative)

            # Parse Hierarchy
            h_parts = [p.strip() for p in hierarchy_str.split(',')]
            curr_s_dig = "NATIONAL"
            curr_dig = ""
            curr_div = ""

            for p in h_parts:
                p_up = p.upper()
                if "S/DIG" in p_up:
                    curr_s_dig = p.replace("S/DIG", "").replace("Province", "").replace("-", "").strip().upper()
                elif "DIG" in p_up: curr_dig = p
                elif any(x in p_up for x in ["DIV", "DISTRICT"]): curr_div = p

            # Skip short or AI-generated filler narratives
            narrative_lower = narrative.lower()
            if len(narrative) < 20: continue
            if any(filler in narrative_lower for filler in AI_FILLER): continue
            if re.search(r'\bnil\b', narrative_lower): continue

            # Clean Hierarchy: Remove S/DIG from the incident list, keep only DIG and Div
            clean_hierarchy = [p for p in [curr_dig, curr_div] if p]

            all_section_incidents.append({
                "province_target": curr_s_dig if "PROVINCE" in curr_s_dig else f"{curr_s_dig} PROVINCE",
                "station": _clean_sl_chars(station).upper(),
                "hierarchy": clean_hierarchy,
                "summary": summary,
                "body": f"{narrative} {ref}".strip()
            })

        # 4. Group into Province buckets for the engine
        prov_dict = {}
        for inc in all_section_incidents:
            p_name = inc.pop("province_target")
            if p_name not in prov_dict: prov_dict[p_name] = {"name": p_name, "incidents": []}
            prov_dict[p_name]["incidents"].append(inc)

        section["provinces"] = list(prov_dict.values())
        if section["provinces"]:
            total_count = sum(len(p["incidents"]) for p in section["provinces"])
            section["count"] = f"{total_count:02d}"
            data["sections"].append(section)

    # 5. Statistical Calculations
    data["summary_matrix"] = calculate_summary_matrix(data)
    data["case_data"] = _calculate_case_data(data["sections"])

    return data

def calculate_summary_matrix(data):
    # This function is used by web_report_engine.py
    # If passed data was result_data (the top-level dict), look into its 'sections'
    sections = data.get("sections", []) if isinstance(data, dict) else data

    categories = ["Theft", "HB & Theft", "Robberies and Armed Robberies", "Rape & Sexual Abuse", "Homicide", "Police Accidents", "Fatal Accidents", "Others"]
    provinces = ["WESTERN", "SABARAGAMUWA", "SOUTHERN", "UVA", "CENTRAL", "NORTH WESTERN", "NORTH CENTRAL", "EASTERN", "NORTHERN"]
    matrix = {"headers": categories, "rows": [], "totals": [0]*8, "grand_total_all": 0}

    for p_base in provinces:
        row = {"province": p_base.title() + " Province", "values": [0]*8, "grand_total": 0}
        for sec in sections:
            s_title = sec["title"].upper()
            for prov in sec["provinces"]:
                if p_base in prov["name"].upper():
                    for inc in prov["incidents"]:
                        txt = inc["body"].upper()
                        idx = 7
                        if "HB & THEFT" in txt or "HOUSE BREAK" in txt: idx = 1
                        elif "THEFT" in txt: idx = 0
                        elif "ROBBER" in txt: idx = 2
                        elif "RAPE" in txt or "SEXUAL" in txt: idx = 3
                        elif "HOMICIDE" in txt or "MURDER" in txt: idx = 4
                        elif "POLICE" in txt and "ACCIDENT" in txt: idx = 5
                        elif "FATAL" in txt and "ACCIDENT" in txt: idx = 6

                        if idx == 7: # Section title fallback
                            if "THEFT" in s_title and "HOUSE" not in s_title: idx = 0
                            elif "HOUSE" in s_title: idx = 1
                            elif "ROBBER" in s_title: idx = 2
                            elif "FATAL" in s_title: idx = 6

                        row["values"][idx] += 1
                        row["grand_total"] += 1
                        matrix["totals"][idx] += 1
                        matrix["grand_total_all"] += 1
        row["values"] = [f"{v:02d}" if v > 0 else "-" for v in row["values"]]
        matrix["rows"].append(row)
    matrix["totals"] = [f"{v:02d}" if v > 0 else "-" for v in matrix["totals"]]
    return matrix

def _calculate_case_data(sections):
    """Calculates the 28-row official case breakdown using incident-level mapping."""
    rows = [{"reported_int": 0, "solved_int": 0, "reported": "-", "solved": "-", "unsolved": "-"} for _ in range(28)]

    for sec in sections:
        for prov in sec["provinces"]:
            for inc in prov["incidents"]:
                txt = inc["body"].upper()

                # Heuristic mapping to the 28 standard rows
                idx = 27 # Default to "Others"
                if any(x in txt for x in ["TERROR", "SUBVERSIVE"]): idx = 0
                elif any(x in txt for x in ["ARMS", "WEAPON", "PISTOL", "GRENADE", "MAOSER", "GUN"]): idx = 1
                elif any(x in txt for x in ["PROTEST", "STRIKE", "DEMONSTRATION", "UNREST"]): idx = 2
                elif any(x in txt for x in ["HOMICIDE", "MURDER", "KILLING", "FATAL ASSAULT"]): idx = 3
                elif "ROBBER" in txt: idx = 4
                elif "VEHICLE" in txt and "THEFT" in txt: idx = 5
                elif "THEFT" in txt and "HOUSE" not in txt: idx = 6
                elif any(x in txt for x in ["HOUSE BREAK", "BURGLARY", "HB &"]): idx = 7
                elif any(x in txt for x in ["RAPE", "SEXUAL", "ABUSE"]): idx = 8
                elif "FATAL" in txt and "ACCIDENT" in txt: idx = 9
                elif any(x in txt for x in ["DEAD BODIES", "SUSPICIOUS DEAD", "FOUND DEAD"]): idx = 10
                elif "POLICE" in txt and "ACCIDENT" in txt: idx = 11
                elif any(x in txt for x in ["NARCOTIC", "LIQUOR", "HEROIN", "CANNABIS", "ICE"]): idx = 18

                rows[idx]["reported_int"] += 1

                # Check solved status from body text
                if any(x in txt for x in ["ARREST", "APPREHEND", "REMAND", "RECOVER"]):
                    rows[idx]["solved_int"] += 1

    # Format the integers back to strings for the engine
    for row in rows:
        if row["reported_int"] > 0:
            row["reported"] = f"{row['reported_int']:02d}"
        if row["solved_int"] > 0:
            row["solved"] = f"{row['solved_int']:02d}"
        unsolved = row["reported_int"] - row["solved_int"]
        if unsolved > 0:
            row["unsolved"] = f"{unsolved:02d}"
        del row["reported_int"]
        del row["solved_int"]

    return rows
