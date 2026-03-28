"""
regex_engine.py — Zero-AI Deterministic Extraction Engine
==========================================================
Implements the core regex logic for partitioning reports, extracting
incidents by province, and routing them to official institutional headers.

System Version: v2.1.0
"""

import re
import datetime
from patterns import SECTION_HEADER_PATTERN, INCIDENT_START_PATTERN, HIERARCHY_MARKER_PATTERN, GENERAL_SECTIONS, SECURITY_SECTIONS
import analytics_engine
from translation_vocabulary import PROVINCES_SINHALA
from station_mapping import SINHALA_TO_ENGLISH, get_station_info


def _strip_sinhala(text):
    """Remove Sinhala Unicode characters and stray markdown asterisks."""
    if not text:
        return ""
    text = re.sub(r'[\u0D80-\u0DFF]+', '', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def structure_with_regex(text, report_type="General"):
    """Main entry point for Zero-AI parsing."""
    print(f"  [Regex Engine] Structuring '{report_type}' report...")

    # Pre-clean: strip Sinhala and stray asterisks from input
    text = _strip_sinhala(text)

    # 1. Date Range & Prepared By
    date_range = _extract_date_range(text)
    prepared_by = _extract_value(text, r'Prepared\s*By\s*[:]\s*([^\n]+)', "PS 51258")
    prepared_name = _extract_value(text, r'Name\s*[:]\s*([^\n]+)', "U.G. Ajith Priyantha")

    search_text = "\n00. START\n" + text

    # 2. Extract Data Tables
    case_data_parsed = _extract_case_table(search_text)
    summary_matrix_parsed = _extract_summary_table(search_text)

    # Clean footer
    search_text = re.sub(
        r'(?:\n---*\n*)?(?:Prepared by:|Checked by:|Copies to:)[\s\S]*',
        '', search_text, flags=re.IGNORECASE
    )

    # 3. Partition Sections
    sections_found = []
    exclude_list = ["PREPARED BY", "CHECKED BY", "COPIES TO", "SUMMARY", "S/NOS", "CASE", "REPORTED"]

    for m in re.finditer(SECTION_HEADER_PATTERN, search_text):
        title = m.group(1).strip()
        if any(ex in title.upper() for ex in exclude_list) or len(title) > 120:
            continue
        title = re.sub(r'[:]\s*Nil\s*$', '', title, flags=re.IGNORECASE).rstrip(':').strip()
        sections_found.append({"title": title, "start": m.start(), "end": m.end()})

    parsed_sections = []
    for idx, s in enumerate(sections_found):
        body_start = s["end"]
        body_end = sections_found[idx + 1]["start"] if idx + 1 < len(sections_found) else len(search_text)
        body = search_text[body_start:body_end].strip()

        provinces = _parse_provinces_and_incidents(body)
        count = sum(len(p["incidents"]) for p in provinces)
        parsed_sections.append({
            "title": s["title"],
            "count": str(count) if count > 0 else "Nil",
            "provinces": provinces
        })

    # 4. Standardize & Route
    final_sections = standardize_and_map_headers(parsed_sections, report_type)

    result = {
        "date_range": date_range,
        "sections": final_sections,
        "case_data": case_data_parsed,
        "summary_matrix": summary_matrix_parsed,
        "prepared_by": prepared_by,
        "prepared_name": prepared_name,
        "checked_title": "Chief Inspector of Police",
        "date_stamp": datetime.datetime.now().strftime("%dth %B %Y")
    }

    if report_type == "General" and not result["summary_matrix"]:
        result["summary_matrix"] = analytics_engine.calculate_summary_matrix(result)
        result["case_data"] = analytics_engine.calculate_case_data(result)

    return result


def standardize_and_map_headers(parsed_sections, report_type):
    """Guarantees official structure by routing incidents into standard buckets,
    and assigns each incident to its correct province via station_mapping."""
    from station_mapping import STATION_MAP
    headers = SECURITY_SECTIONS if report_type == "Security" else GENERAL_SECTIONS
    mapped_data = {h: {} for h in headers}

    for sec in parsed_sections:
        for prov in sec.get("provinces", []):
            for inc in prov.get("incidents", []):
                # Skip incidents with empty or Nil-only bodies
                body = inc.get("body", "").strip()
                if not body or body.upper() in ("NIL", "NIL.", "NONE"):
                    continue
                # Skip if station is a known non-station label
                station = inc.get("station", "").upper()
                if station in ("SUBVERSIVE ACTIVITIES", "NIL", ""):
                    continue

                target = _route_incident(inc, prov["name"], sec["title"], report_type, headers)

                # Resolve province from station map; fall back to parsed province
                station = inc.get("station", "")
                station_info = STATION_MAP.get(station, {})
                resolved_prov = station_info.get("province", prov["name"]).upper()
                if not resolved_prov or resolved_prov == "NATIONAL":
                    resolved_prov = prov["name"]

                # Update hierarchy from station map if available
                if station_info:
                    inc["hierarchy"] = [
                        f"S/DIG {resolved_prov.replace(' PROVINCE', '')}",
                        station_info.get("dig", ""),
                        station_info.get("div", "")
                    ]

                if resolved_prov not in mapped_data[target]:
                    mapped_data[target][resolved_prov] = []
                mapped_data[target][resolved_prov].append(inc)

    final = []
    for h in headers:
        p_dict = mapped_data[h]
        p_arr = [{"name": n, "incidents": i} for n, i in p_dict.items()]
        total = sum(len(i) for i in p_dict.values())
        final.append({"title": h, "count": str(total).zfill(2), "provinces": p_arr})
    return final


def _route_incident(inc, prov_name, orig_title, report_type, headers):
    text = (inc.get("body", "") + " " + inc.get("station", "")).lower()
    orig = orig_title.lower()
    if report_type == "Security":
        if "subversive" in text or "subversive" in orig:
            return headers[1]
        if any(k in text for k in ["recover", "weapon", "pistol", "gun", "grenade", "explosive", "ammunition"]):
            return headers[2]
        return headers[0]
    else:
        # Route by original section title first (most reliable)
        if any(k in orig for k in ["rape", "sexual", "child abuse"]):
            return headers[1]
        if "fatal accident" in orig:
            return headers[2]
        if any(k in orig for k in ["road accident", "damage to sri lanka police", "vehicles involved"]):
            return headers[3]
        if any(k in orig for k in ["dead bod", "suspicious", "finding of dead"]):
            return headers[4]
        if any(k in orig for k in ["charged in court", "misconduct", "indiscipline", "complaints against police"]):
            return headers[5]
        if any(k in orig for k in ["serious injury", "illness", "death of police", "deaths of police"]):
            return headers[6]
        if any(k in orig for k in ["narcotic", "illegal liquor", "detection"]):
            return headers[7]
        if any(k in orig for k in ["tri-force", "tri force", "forces member", "arrest of tri"]):
            return headers[8]
        if any(k in orig for k in ["other matter", "09. other", "10. other"]):
            return headers[9]
        # Fallback: route by body text
        if any(k in text for k in ["sexual", "rape", "child abuse", "sexually abused"]):
            return headers[1]
        if "fatal accident" in text:
            return headers[2]
        if any(k in text for k in ["police vehicle", "police motorcycle", "police jeep"]) and "accident" in text:
            return headers[3]
        if any(k in text for k in ["found dead", "dead body", "decomposed body", "suspicious death"]):
            return headers[4]
        if any(k in text for k in ["charged in court", "misconduct", "absent from duty"]):
            return headers[5]
        if any(k in text for k in ["passed away", "death of police", "hospitalized", "retired.*died"]):
            return headers[6]
        if any(k in text for k in ["cannabis", "ice", "heroin", "liquor", "narcotic"]):
            return headers[7]
        if any(k in text for k in ["soldier", "army", "navy", "tri-force", "tri force"]):
            return headers[8]
        if any(k in text for k in ["murder", "homicide", "robbery", "theft", "break", "stabbed", "snatched"]):
            return headers[0]
        return headers[9]


def _parse_provinces_and_incidents(body):
    prov_word = "\u0db4\u0dc5\u0dcf\u0dad"
    prov_pattern = (
        r'(\n\s*(?:[#*\-]+\s*)?S/DIG\s+[^\n*]+(?:\*+)?(?:\n|$))'
        r'|(\n\s*(?:[#*\-]+\s*)?[^\n*]+PROVINCE(?:\*+)?(?:\n|$))'
        r'|(\n\s*(?:[#*\-]+\s*)?[^\n*]+' + prov_word + r'(?:\*+)?(?:\n|$))'
    )
    parts = re.split(prov_pattern, "\n" + body, flags=re.IGNORECASE)

    current_prov = "NATIONAL"
    province_groups = {"NATIONAL": []}

    for chunk in parts:
        if not chunk:
            continue
        chunk = chunk.strip()
        found_name = None
        # Only treat as province header if short (a header line, not an incident body)
        if len(chunk) < 100:
            for sk, ek in PROVINCES_SINHALA.items():
                if ek.upper() in chunk.upper() or sk in chunk:
                    found_name = ek.upper() + " PROVINCE"
                    break

        if found_name:
            current_prov = found_name
            if current_prov not in province_groups:
                province_groups[current_prov] = []
            continue

        incidents = _extract_incidents_from_chunk(chunk, current_prov)
        province_groups[current_prov] = province_groups.get(current_prov, []) + incidents

    provinces = []
    for name, incs in province_groups.items():
        if incs:
            provinces.append({"name": name, "incidents": incs})
    return provinces


def _extract_incidents_from_chunk(chunk, prov_name):
    incs = []
    hierarchy = []
    last_inc = None
    lines = chunk.split('\n')
    i = 0
    while i < len(lines):
        orig_line = lines[i].strip()
        # Strip leading markdown bullets/bold markers
        line = re.sub(r'^[*\-#]+\s*', '', orig_line).strip()
        line = re.sub(r'^\*\*', '', line).strip()
        # Strip Sinhala characters
        line = _strip_sinhala(line)

        if not line or line.upper() == "NIL":
            i += 1
            continue

        # Skip sub-headers like "Murders - 03" or "House-breaking and theft - 05"
        if re.match(r'^[A-Za-z\s\-&/,]+\s*[-\u2013]\s*\d+\s*$', line):
            last_inc = None
            i += 1
            continue
        if re.match(r'^[-\u2013]\s*\d+\s*$', line):
            i += 1
            continue

        # Bullet sub-items (no CTM/OTM, no colon) → append to last incident
        if (orig_line.startswith('*') and
                not re.search(r'(?:CTM|OTM)\s*[\d/]+', orig_line, re.IGNORECASE) and
                ':' not in orig_line and
                last_inc is not None):
            last_inc["body"] += " " + line
            i += 1
            continue

        if re.search(HIERARCHY_MARKER_PATTERN, line.upper()):
            hierarchy.append(line.replace('*', '').strip(':'))
            i += 1
            continue

        # Try "Station, [Sub Unit,] CTM/OTM XXXX[:**] body"
        ctm_match = re.match(
            r'^(.+?)\s*,\s*((?:CTM|OTM)\s*[\d/]+(?:\s*/\s*(?:CTM|OTM)\s*[\d/]+)*)\s*[:\-\u2013]\*?\*?\s*(.*)',
            line, re.IGNORECASE
        )
        if ctm_match:
            st_raw = ctm_match.group(1).strip()
            ctm_code = ctm_match.group(2).strip()
            bd = ctm_match.group(3).strip().rstrip('*')

            st_upper = st_raw.upper()
            if (re.search(r'\b(FROM|TO|ON|AT|HRS|MARCH|JANUARY|FEBRUARY|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\b', st_upper)
                    or re.search(r'\d{4}', st_raw)
                    or st_upper in ("GENERAL SITUATION", "SECURITY SITUATION", "SITUATION REPORT", "GENERAL", "SECURITY")
                    or len(st_raw) > 80):
                i += 1
                continue

            # Look-ahead for short body
            if len(bd) < 10 and i + 1 < len(lines):
                next_clean = _strip_sinhala(re.sub(r'^[*\-#]+\s*', '', lines[i + 1].strip()).strip())
                if (next_clean and
                        not re.match(r'^.+?,\s*(?:CTM|OTM)', next_clean, re.IGNORECASE) and
                        not re.search(HIERARCHY_MARKER_PATTERN, next_clean.upper())):
                    bd += " " + next_clean
                    i += 1

            st_en = SINHALA_TO_ENGLISH.get(st_raw, st_raw)
            info = get_station_info(st_en)
            inc = {
                "station": _strip_sinhala(st_en),
                "ctm": ctm_code,
                "hierarchy": [
                    f"S/DIG {prov_name.replace(' PROVINCE', '')}",
                    info["dig"],
                    info["div"]
                ],
                "body": _strip_sinhala(bd)
            }
            if hierarchy:
                inc["hierarchy"].extend(hierarchy)
            incs.append(inc)
            last_inc = inc
            hierarchy = []
            i += 1
            continue

        # Fallback: plain "Station: body"
        m = re.search(INCIDENT_START_PATTERN, line)
        if m:
            st_raw = m.group(1).strip()
            bd = (m.group(2) or "").strip().rstrip('*')

            st_upper = st_raw.upper()
            # Skip non-station words (drug names, generic labels)
            _NON_STATIONS = {"HEROIN", "ICE", "CANNABIS", "COCAINE", "LIQUOR",
                             "SUBVERSIVE ACTIVITIES", "DEMONSTRATIONS", "PROTESTS",
                             "MISSING PERSONS", "SUICIDE", "OTHER SPECIAL INCIDENTS",
                             "INCIDENTS INVOLVING FOREIGN NATIONALS"}
            if st_upper in _NON_STATIONS:
                if last_inc:
                    last_inc["body"] += " " + line
                i += 1
                continue

            if (re.search(r'\b(FROM|TO|ON|AT|HRS|MARCH|JANUARY|FEBRUARY|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\b', st_upper)
                    or re.search(r'\d{4}', st_raw)
                    or st_upper in ("GENERAL SITUATION", "SECURITY SITUATION", "SITUATION REPORT", "GENERAL", "SECURITY")
                    or len(st_raw) > 50):
                i += 1
                continue

            if len(bd) < 10 and i + 1 < len(lines):
                next_clean = _strip_sinhala(re.sub(r'^[*\-#]+\s*', '', lines[i + 1].strip()).strip())
                if (next_clean and
                        not re.search(INCIDENT_START_PATTERN, next_clean) and
                        not re.search(HIERARCHY_MARKER_PATTERN, next_clean.upper())):
                    bd += " " + next_clean
                    i += 1

            st_en = SINHALA_TO_ENGLISH.get(st_raw, st_raw)
            info = get_station_info(st_en)

            # Skip count-only headers or single-letter "stations"
            if re.search(r'[-\u2013]\s*\d+', st_raw) or (bd.replace(' ', '').isdigit() and len(bd) <= 2):
                i += 1
                continue
            if re.match(r'^[a-z\s\-&/,]+\s*[-\u2013]\s*\d+\s*$', bd.lower()):
                i += 1
                continue
            if len(st_raw) < 3:
                if last_inc:
                    last_inc["body"] += " " + line
                i += 1
                continue

            inc = {
                "station": _strip_sinhala(st_en),
                "hierarchy": [
                    f"S/DIG {prov_name.replace(' PROVINCE', '')}",
                    info["dig"],
                    info["div"]
                ],
                "body": _strip_sinhala(bd)
            }
            if hierarchy:
                inc["hierarchy"].extend(hierarchy)
            incs.append(inc)
            last_inc = inc
            hierarchy = []
        elif last_inc:
            clean = _strip_sinhala(re.sub(r'^[*\-#]+\s*', '', line).strip())
            if clean:
                last_inc["body"] += " " + clean

        i += 1
    return incs


def _extract_date_range(text):
    m = re.search(r'[Ff]rom\s+([^\n]{5,40})\s+to\s+([^\n]{5,40})', text[:2000])
    if m:
        return f"From {m.group(1).strip()} to {m.group(2).strip()}"
    return (
        f"From {datetime.date.today().strftime('%dth %B %Y')} "
        f"to {datetime.date.today().strftime('%dth %B %Y')}"
    )


def _extract_value(text, pattern, default):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else default


def _extract_case_table(search_text):
    case_data_parsed = []
    case_table_match = re.search(
        r'\|\s*S/Nos\.\s*\|\s*Case\s*\|\s*Reported[\s\S]*?(?=\n\s*\n|\Z)',
        search_text, re.IGNORECASE
    )
    if case_table_match:
        table_text = case_table_match.group(0)
        for line in table_text.strip().split('\n')[2:]:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                case_data_parsed.append({
                    "reported": parts[2],
                    "solved": parts[3],
                    "unsolved": parts[4]
                })
    return case_data_parsed


def _extract_summary_table(search_text):
    summary_matrix_parsed = {}
    summary_table_match = re.search(
        r'\|\s*\|\s*Theft\s*\|\s*HB[\s\S]*?(?=\n\s*\n|\Z)',
        search_text, re.IGNORECASE
    )
    if summary_table_match:
        table_text = summary_table_match.group(0)
        lines = table_text.strip().split('\n')
        if len(lines) > 2:
            headers = [p.strip() for p in lines[0].split('|') if p.strip()][-9:-1]
            rows = []
            totals = []
            grand_total_all = None
            for line in lines[2:]:
                parts = [p.strip().replace('**', '') for p in line.split('|') if p.strip()]
                if not parts:
                    continue
                if parts[0].upper() == "TOTAL":
                    totals = parts[1:-1]
                    if len(parts) > 1:
                        grand_total_all = parts[-1]
                else:
                    rows.append({
                        "province": parts[0],
                        "values": parts[1:-1],
                        "grand_total": parts[-1] if len(parts) > 1 else ""
                    })
            summary_matrix_parsed = {
                "headers": headers,
                "rows": rows,
                "totals": totals,
                "grand_total_all": grand_total_all
            }
    return summary_matrix_parsed
