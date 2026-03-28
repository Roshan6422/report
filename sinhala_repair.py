"""
sinhala_repair.py — Layout Repair Utility for SL Police Reports
=============================================================
Identifies and merges vertically-split Sinhala labels (Police Station, Date, Time, etc.)
into single-line key-value pairs to ensure regex compatibility.

System Version: v2.2.0
"""

import re

# Common Sinhala labels seen in vertical layouts across March reports
REPAIR_MAP = {
    r'සඳොලිවහ\s*වහථළනය': 'සඳොලිවහ වහථළනය:',  # Police Station
    r'අනු\s*අංරය': 'අනු අංරය:',               # Serial Number
    r'දින\s*IR': 'දින IR:',                    # Date IR
    r'දිනය\s* IR': 'දිනය IR:',               # Date IR
    r'ඳෆය\s*\d{4}': 'ඳෆය:',                    # Time (hours)
    r' OT[MN]\s*\d+': 'OTM:',                # OTM Code
    r'සරොට්\s*ඨළවය': 'සරොට්ඨළවය:',              # Division/District
    r'සිදුවීම\s*ව෕\s*වහථළනය': 'සිදුවීම ව෕ වහථළනය:', # Place of Incident
    r'ඳෆමිණිලි\s*ලිරරු': 'ඳෆමිණිලිරරු:',       # Complainant
}

def repair_vertical_layout(text):
    """
    Scans the text for common vertical labels and joins them.
    Also removes excessive whitespace produced by poor OCR.
    """
    if not text: return ""
    
    # 1. Join split labels from REPAIR_MAP
    lines = text.split('\n')
    joined_text = "\n".join(lines)
    
    for pattern, replacement in REPAIR_MAP.items():
        joined_text = re.sub(pattern, replacement, joined_text, flags=re.IGNORECASE | re.MULTILINE)

    # 2. Heal specific labels that split across lines in a fixed way (e.g. 10+11)
    # We look for common pairs that appear sequentially
    raw_lines = joined_text.split('\n')
    repaired_lines = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i].strip()
        if not line:
            repaired_lines.append(line)
            i += 1; continue
        
        # Check if this line is "Police" and next is "Station"
        if line == "සඳොලිවහ" and i+1 < len(raw_lines) and raw_lines[i+1].strip() == "වහථළනය":
            repaired_lines.append("සඳොලිවහ වහථළනය:")
            i += 2; continue
            
        if line == "අනු" and i+1 < len(raw_lines) and raw_lines[i+1].strip() == "අංරය":
            repaired_lines.append("අනු අංරය:")
            i += 2; continue
            
        if line == "සිද්ධිය" and i+1 < len(raw_lines) and raw_lines[i+1].strip().upper() == "NIL":
            repaired_lines.append("සිද්ධිය: NIL")
            i += 2; continue

        repaired_lines.append(line)
        i += 1
        
    return "\n".join(repaired_lines)

def pre_process_expert_layout(text):
    """Entry point for full text recovery."""
    text = repair_vertical_layout(text)
    
    # Standardize "Nil" markers that confuse AI
    text = re.sub(r'නෆත\.?', 'නෆත (NIL)', text)
    
    return text
