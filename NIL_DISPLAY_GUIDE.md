# Nil Display Guide for Security Reports

## Overview

When a security section has NO data/incidents, it automatically displays "Nil" exactly as shown in the official sample.

---

## How It Works

### Automatic Detection

The system automatically checks each section:
- **Has incidents?** → Display section with data
- **No incidents?** → Display "Nil" after section title

### Format

```
01. VERY IMPORTANT MATTERS OF SECURITY INTEREST: Nil
02. SUBVERSIVE ACTIVITIES: Nil
03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:
    [Data if available]
```

---

## Implementation

### In Code

```python
def build_section_html(sec):
    title = str(sec.get("title", ""))
    provinces = sec.get("provinces", [])
    
    # Check if section has any incidents
    has_incidents = any(p.get("incidents") for p in provinces)
    
    # Section header with "Nil" if empty
    if not has_incidents:
        return f'<div class="section-header">{title} Nil</div>'
    
    # Otherwise, show section with data
    html = f'<div class="section-header">{title}</div>'
    # ... add provinces and incidents
```

### Data Structure

**Empty Section (Shows Nil):**
```python
{
    "title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:",
    "provinces": []  # Empty list = Nil
}
```

**Section with Data:**
```python
{
    "title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:",
    "provinces": [
        {
            "name": "SABARAGAMUWA",
            "incidents": [
                {
                    "station": "EMBILIPITIYA",
                    "body": "...",
                    # ... incident details
                }
            ]
        }
    ]
}
```

---

## Examples

### Example 1: All Sections Empty

**Input:**
```python
report_data = {
    "sections": [
        {"title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:", "provinces": []},
        {"title": "02. SUBVERSIVE ACTIVITIES:", "provinces": []},
        {"title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:", "provinces": []}
    ]
}
```

**Output:**
```
01. VERY IMPORTANT MATTERS OF SECURITY INTEREST: Nil
02. SUBVERSIVE ACTIVITIES: Nil
03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES: Nil
```

---

### Example 2: Mixed (Some Empty, Some With Data)

**Input:**
```python
report_data = {
    "sections": [
        {"title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:", "provinces": []},
        {"title": "02. SUBVERSIVE ACTIVITIES:", "provinces": []},
        {
            "title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:",
            "provinces": [
                {
                    "name": "SABARAGAMUWA",
                    "incidents": [incident1, incident2]
                }
            ]
        }
    ]
}
```

**Output:**
```
01. VERY IMPORTANT MATTERS OF SECURITY INTEREST: Nil
02. SUBVERSIVE ACTIVITIES: Nil
03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:

S/DIG  SABARAGAMUWA PROVINCE

DIG Ratnapura          EMBILIPITIYA: (Arrest of suspects...) On the 17th...
District
Embilipitiya Div.
```

---

### Example 3: All Sections With Data

**Input:**
```python
report_data = {
    "sections": [
        {
            "title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:",
            "provinces": [{"name": "WESTERN", "incidents": [incident1]}]
        },
        {
            "title": "02. SUBVERSIVE ACTIVITIES:",
            "provinces": [{"name": "NORTHERN", "incidents": [incident2]}]
        },
        {
            "title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:",
            "provinces": [{"name": "SABARAGAMUWA", "incidents": [incident3]}]
        }
    ]
}
```

**Output:**
```
01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:

S/DIG  WESTERN PROVINCE
[Incident 1 details...]

02. SUBVERSIVE ACTIVITIES:

S/DIG  NORTHERN PROVINCE
[Incident 2 details...]

03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:

S/DIG  SABARAGAMUWA PROVINCE
[Incident 3 details...]
```

---

## With Categorization System

When using the automatic categorizer, empty categories automatically show "Nil":

```python
from security_categorizer import SecurityCategorizer
from web_report_engine_v2 import generate_security_report

categorizer = SecurityCategorizer()

# If no incidents match a category, it will be empty
incidents = [
    {"body": "Arms recovery incident...", "station": "X", "province": "Y"}
]

categorized = categorizer.categorize_batch(incidents)

# Result might be:
# Category 1: [] (empty) → Will show "Nil"
# Category 2: [] (empty) → Will show "Nil"
# Category 3: [1 incident] → Will show data

report_data = categorizer.organize_by_province(categorized)
report_data["date_range"] = "..."

generate_security_report(report_data, "output.html")
```

**Output will automatically show:**
```
01. VERY IMPORTANT MATTERS OF SECURITY INTEREST: Nil
02. SUBVERSIVE ACTIVITIES: Nil
03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:
    [Data for the one incident]
```

---

## Testing

### Test Empty Sections

```python
# Test data with empty sections
test_data = {
    "date_range": "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026",
    "sections": [
        {"title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:", "provinces": []},
        {"title": "02. SUBVERSIVE ACTIVITIES:", "provinces": []},
        {"title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:", "provinces": []}
    ]
}

from web_report_engine_v2 import generate_security_report

generate_security_report(test_data, "test_nil.html")
```

**Expected Result:**
All three sections show "Nil"

---

## Verification Checklist

When generating reports, verify:

- [ ] Empty sections show ": Nil" after title
- [ ] "Nil" is on the same line as section title
- [ ] No extra spacing or line breaks
- [ ] Font and formatting match section headers
- [ ] Sections with data do NOT show "Nil"
- [ ] Mixed reports show "Nil" only for empty sections

---

## Common Scenarios

### Scenario 1: Daily Report with No Security Incidents

If a day has no security incidents at all:
```
01. VERY IMPORTANT MATTERS OF SECURITY INTEREST: Nil
02. SUBVERSIVE ACTIVITIES: Nil
03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES: Nil
```

### Scenario 2: Only Arms Recoveries

If only arms were recovered that day:
```
01. VERY IMPORTANT MATTERS OF SECURITY INTEREST: Nil
02. SUBVERSIVE ACTIVITIES: Nil
03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:
    [Incidents listed here]
```

### Scenario 3: Multiple Categories Active

If incidents in multiple categories:
```
01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:
    [VIP security incidents]

02. SUBVERSIVE ACTIVITIES: Nil

03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:
    [Arms recovery incidents]
```

---

## Formatting Details

### CSS Styling

The "Nil" text uses the same styling as section headers:

```css
.section-header { 
    font-weight: bold; 
    font-size: 11pt; 
    margin-top: 3mm; 
    margin-bottom: 3mm; 
    text-align: left;
}
```

### HTML Output

**Empty section:**
```html
<div class="section-header">01. VERY IMPORTANT MATTERS OF SECURITY INTEREST: Nil</div>
```

**Section with data:**
```html
<div class="section-header">03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:</div>
<div class="province-heading">S/DIG  SABARAGAMUWA PROVINCE</div>
<!-- incidents here -->
```

---

## Integration

### With Existing Pipeline

```python
# Extract from PDF
text = extract_text_with_layout("report.pdf")

# Categorize
categorizer = SecurityCategorizer()
incidents = parse_incidents(text)
categorized = categorizer.categorize_batch(incidents)

# Some categories might be empty → Will show "Nil" automatically
report_data = categorizer.organize_by_province(categorized)

# Generate report
generate_security_report(report_data, "output.html")
```

### Manual Control

If you want to force a section to show "Nil":

```python
# Empty provinces list = Nil
section = {
    "title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:",
    "provinces": []  # Empty = Nil
}
```

If you want to force a section to show data:

```python
# Add at least one province with incidents
section = {
    "title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:",
    "provinces": [
        {
            "name": "WESTERN",
            "incidents": [incident_dict]
        }
    ]
}
```

---

## Summary

✅ **Automatic**: System detects empty sections  
✅ **Correct Format**: Shows "Nil" exactly as official sample  
✅ **No Manual Work**: Happens automatically  
✅ **Works with Categorizer**: Empty categories show "Nil"  
✅ **Tested**: Verified with test_nil_sections.py  

The "Nil" display is already implemented and working perfectly!

---

**Document Version:** 1.0  
**Last Updated:** March 28, 2026  
**Module:** web_report_engine_v2.py
