import re
import logging

logger = logging.getLogger(__name__)

class SinhalaSummaryParser:
    """
    Parses the OCR text of the Sinhala Summary Table found at the end of Police Reports.
    Table Format:
    අනු අංකය | සිද්ධිය | වාර්තා වූ ගණන | විසඳූ ගණන | නොවිසඳුණු ගණන
    (No) | (Category) | (Reported) | (Solved) | (Unsolved)
    """

    def __init__(self, categories_dict):
        self.categories = categories_dict

    def parse_summary_table(self, ocr_text: str) -> dict:
        """
        Extract numerical counts for all categories from OCR text.
        """
        summary = {}
        # Pre-fill structure
        for key, name in self.categories.items():
            summary[key] = {
                "category_name": name,
                "total_incidents": 0,
                "resolved": "-",
                "unresolved": "-"
            }

        lines = ocr_text.splitlines()

        for i, line in enumerate(lines):
            line = line.strip()
            # Match start of row e.g., "01 ත්‍රස්තවාදී..."
            match = re.match(r'^(\d{2})\s+(.+)$', line)
            if match:
                cat_num = match.group(1)
                remainder = match.group(2)
                
                if cat_num in self.categories:
                    tokens = [t.strip() for t in remainder.split() if t.strip()]
                    
                    counts = []
                    # Read from right to left (expecting numbers, 'නැත', or '-')
                    for token in reversed(tokens):
                        if re.match(r'^(\d+|නැත|-|--|None|none|Nil|nil)$', token, re.IGNORECASE):
                            counts.append(token)
                        else:
                            break
                    
                    # If the OCR pushed digits to the next line, grab them
                    if len(counts) < 3 and i + 1 < len(lines):
                        next_tokens = [t.strip() for t in lines[i+1].split() if t.strip()]
                        for token in next_tokens:
                            if re.match(r'^(\d+|නැත|-|--|None|none|Nil|nil)$', token, re.IGNORECASE):
                                counts.insert(0, token)
                    
                    # Normalize extracted counts
                    if len(counts) >= 3:
                        counts_ordered = counts[::-1][-3:]
                    elif len(counts) == 2:
                        counts_ordered = [counts[1], "-", "-"] if counts[1].isdigit() else [counts[-1], "-", "-"] 
                    elif len(counts) == 1:
                        counts_ordered = [counts[0], "-", "-"]
                    else:
                        counts_ordered = ["0", "-", "-"]

                    def parse_total(v):
                        if 'නැත' in v or '-' in v or 'nil' in v.lower() or 'none' in v.lower(): return 0
                        try: return int(v)
                        except: return 0

                    def parse_str_val(v):
                        if 'නැත' in v or 'nil' in v.lower() or 'none' in v.lower(): return "0"
                        if '-' in v: return "-"
                        try: return str(int(v))
                        except: return "-"

                    summary[cat_num]["total_incidents"] = parse_total(counts_ordered[0])
                    summary[cat_num]["resolved"] = parse_str_val(counts_ordered[1])
                    summary[cat_num]["unresolved"] = parse_str_val(counts_ordered[2])
                    
                    logger.info(f"Summary Table Extracted [{cat_num}]: Reported={summary[cat_num]['total_incidents']}, Solved={summary[cat_num]['resolved']}, Unsolved={summary[cat_num]['unresolved']}")
                    
        return summary
