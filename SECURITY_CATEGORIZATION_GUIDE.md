# Security Data Categorization Guide

## Overview

This system automatically categorizes ALL security-related data into the 3 official Security Situation Report categories:

1. **01. VERY IMPORTANT MATTERS OF SECURITY INTEREST**
2. **02. SUBVERSIVE ACTIVITIES**
3. **03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES**

---

## How It Works

### Intelligent Keyword Matching

The system uses comprehensive keyword lists to automatically categorize each incident:

#### Category 1: VERY IMPORTANT MATTERS OF SECURITY INTEREST
**Triggers on:**
- VIP-related: president, prime minister, minister, diplomat, embassy
- High-level threats: terrorism, national security, assassination, bomb threat
- Major incidents: critical, emergency, security alert, imminent threat
- Organized crime: human trafficking, drug trafficking, smuggling ring

#### Category 2: SUBVERSIVE ACTIVITIES
**Triggers on:**
- Anti-government: subversive, sedition, treason, rebellion, revolt
- Extremism: extremist, radical, militant, separatist, jihadist
- Unlawful assembly: illegal gathering, protest, riot, mob, unrest
- Propaganda: inflammatory, incitement, hate speech, banned literature
- Organizations: banned organization, terrorist organization, militant group

#### Category 3: RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES
**Triggers on:**
- Firearms: gun, pistol, rifle, shotgun, T-56, AK-47, assault rifle
- Ammunition: bullet, round, cartridge, magazine, 9mm, 7.62mm
- Explosives: bomb, grenade, mine, IED, detonator, C-4, TNT, gunpowder
- Components: bomb-making, explosive material, timer, trigger mechanism
- Military equipment: ordnance, mortar, rocket, missile, launcher

---

## Usage

### Basic Categorization

```python
from security_categorizer import SecurityCategorizer

# Initialize
categorizer = SecurityCategorizer()

# Categorize single incident
incident_text = "Police arrested suspects with detonator and gunpowder..."
category, confidence = categorizer.categorize_incident(incident_text)

print(f"Category: {category}")
print(f"Confidence: {confidence:.2f}")
```

### Batch Categorization

```python
# Prepare incidents
incidents = [
    {"body": "Incident text 1...", "station": "COLOMBO", "province": "WESTERN"},
    {"body": "Incident text 2...", "station": "JAFFNA", "province": "NORTHERN"},
    # ... more incidents
]

# Categorize all
categorized = categorizer.categorize_batch(incidents)

# Result: Dictionary with 3 categories, each containing relevant incidents
for category, incidents_list in categorized.items():
    print(f"{category}: {len(incidents_list)} incidents")
```

### Generate Report Structure

```python
# Organize for report generation
report_data = categorizer.organize_by_province(categorized)

# Add date range
report_data["date_range"] = "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026"

# Generate report
from web_report_engine_v2 import generate_security_report, html_to_pdf

html_path = generate_security_report(report_data, "security_report.html")
html_to_pdf(html_path, "security_report.pdf")
```

---

## Categorization Rules

### Priority System

1. **Category 1** (Highest Priority)
   - VIP security matters
   - National security threats
   - Critical incidents
   - If keywords match, always categorize here first

2. **Category 2** (Medium Priority)
   - Subversive activities
   - Anti-government actions
   - Extremist activities
   - Checked if Category 1 doesn't match

3. **Category 3** (Default)
   - Arms and ammunition
   - Explosives
   - Military equipment
   - Default category if no clear match

### Confidence Scoring

- **1.0 (100%)**: Strong keyword matches (5+ keywords)
- **0.8 (80%)**: Good matches (4 keywords)
- **0.6 (60%)**: Moderate matches (3 keywords)
- **0.5 (50%)**: Weak matches or default assignment
- **0.0 (0%)**: No matches (shouldn't happen)

---

## Examples

### Example 1: Arms Recovery (Category 3)

**Input:**
```
EMBILIPITIYA: Police arrested suspects with electric detonator and 
80g of gunpowder while digging tunnel for treasure hunting.
```

**Keywords Matched:** detonator, gunpowder  
**Category:** 03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES  
**Confidence:** 0.60

---

### Example 2: Subversive Activity (Category 2)

**Input:**
```
COLOMBO: Unlawful assembly dispersed. Group distributing anti-government 
pamphlets. Three organizers arrested. Seditious material seized.
```

**Keywords Matched:** unlawful assembly, anti-government, seditious  
**Category:** 02. SUBVERSIVE ACTIVITIES  
**Confidence:** 1.00

---

### Example 3: VIP Security (Category 1)

**Input:**
```
JAFFNA: Intelligence reports indicate potential VIP security threat. 
Enhanced security measures for ministerial visit.
```

**Keywords Matched:** intelligence, vip security, minister  
**Category:** 01. VERY IMPORTANT MATTERS OF SECURITY INTEREST  
**Confidence:** 1.00

---

## Integration with Existing System

### Step 1: Extract Incidents from PDF

```python
import translator_pipeline

# Extract text from PDF
text = translator_pipeline.extract_text_with_layout("security_report.pdf")

# Split into incidents (your existing logic)
incidents = split_into_incidents(text)
```

### Step 2: Categorize Automatically

```python
from security_categorizer import SecurityCategorizer

categorizer = SecurityCategorizer()

# Convert to incident dictionaries
incident_dicts = []
for text in incidents:
    incident_dicts.append({
        "body": text,
        "station": extract_station(text),
        "province": extract_province(text)
    })

# Categorize
categorized = categorizer.categorize_batch(incident_dicts)
```

### Step 3: Process with Detailed Narrative

```python
from security_report_processor import SecurityReportProcessor

processor = SecurityReportProcessor()

# Process each category
for category, incidents in categorized.items():
    for incident in incidents:
        # Enhance to detailed narrative format
        enhanced = processor.process_raw_incident(
            incident["body"],
            section_type=category
        )
        incident.update(enhanced)
```

### Step 4: Generate Report

```python
# Organize by province
report_data = categorizer.organize_by_province(categorized)
report_data["date_range"] = "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026"

# Generate HTML and PDF
from web_report_engine_v2 import generate_security_report, html_to_pdf

html_path = generate_security_report(report_data, "output.html")
html_to_pdf(html_path, "output.pdf")
```

---

## Customization

### Adding Keywords

Edit `security_categorizer.py` and add keywords to the appropriate category:

```python
SECURITY_CATEGORIES = {
    "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST": {
        "keywords": [
            # Add your keywords here
            "new_keyword_1",
            "new_keyword_2",
            # ...
        ],
        "priority": 1
    },
    # ...
}
```

### Adjusting Priority

Change the priority value (1-3) to adjust categorization preference:
- **1** = Highest priority (checked first)
- **2** = Medium priority
- **3** = Lowest priority (default)

### Custom Categorization Logic

Override the `categorize_incident()` method:

```python
class CustomCategorizer(SecurityCategorizer):
    def categorize_incident(self, incident_text):
        # Your custom logic here
        if "special_condition" in incident_text:
            return "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST", 1.0
        
        # Fall back to default logic
        return super().categorize_incident(incident_text)
```

---

## Statistics and Monitoring

### View Categorization Stats

```python
categorizer.print_stats()
```

**Output:**
```
============================================================
SECURITY CATEGORIZATION STATISTICS
============================================================
Total Incidents:              50
Category 1 (Important):       5
Category 2 (Subversive):      12
Category 3 (Arms Recovery):   33
Uncategorized:                0
============================================================
```

### Access Stats Programmatically

```python
stats = categorizer.stats

print(f"Total: {stats['total_incidents']}")
print(f"Category 1: {stats['category_1']}")
print(f"Category 2: {stats['category_2']}")
print(f"Category 3: {stats['category_3']}")
```

---

## Validation

### Check Categorization Quality

```python
# Review low-confidence categorizations
for category, incidents in categorized.items():
    for incident in incidents:
        if incident["category_confidence"] < 0.7:
            print(f"Low confidence: {incident['station']}")
            print(f"  Category: {category}")
            print(f"  Confidence: {incident['category_confidence']:.2f}")
            print(f"  Text: {incident['body'][:100]}...")
```

### Manual Override

```python
# If categorization is wrong, manually reassign
incident["category"] = "02. SUBVERSIVE ACTIVITIES"
incident["category_confidence"] = 1.0
```

---

## Best Practices

1. **Review Low Confidence**: Check incidents with confidence < 0.7
2. **Update Keywords**: Add new keywords as you encounter them
3. **Monitor Distribution**: Ensure reasonable distribution across categories
4. **Validate Output**: Spot-check categorized reports
5. **Keep Stats**: Track categorization accuracy over time

---

## Troubleshooting

### Issue: All incidents go to Category 3

**Cause:** No keywords matching Categories 1 or 2  
**Solution:** Add more relevant keywords or check incident text format

### Issue: Wrong categorization

**Cause:** Ambiguous keywords or insufficient context  
**Solution:** Add more specific keywords or adjust priority

### Issue: Low confidence scores

**Cause:** Few keyword matches  
**Solution:** Expand keyword lists or accept lower threshold

---

## Complete Example

```python
from security_categorizer import SecurityCategorizer
from security_report_processor import SecurityReportProcessor
from web_report_engine_v2 import generate_security_report, html_to_pdf

# Initialize
categorizer = SecurityCategorizer()
processor = SecurityReportProcessor()

# Raw incidents from PDF extraction
raw_incidents = [
    "EMBILIPITIYA: Detonator and gunpowder seized...",
    "COLOMBO: Anti-government protest dispersed...",
    "JAFFNA: VIP security threat reported...",
    # ... more incidents
]

# Step 1: Categorize
incidents = [{"body": text, "station": "TEST", "province": "WESTERN"} 
             for text in raw_incidents]
categorized = categorizer.categorize_batch(incidents)

# Step 2: Enhance to detailed narrative
for category, incidents_list in categorized.items():
    for incident in incidents_list:
        enhanced = processor.process_raw_incident(
            incident["body"],
            section_type=category
        )
        incident.update(enhanced)

# Step 3: Organize and generate report
report_data = categorizer.organize_by_province(categorized)
report_data["date_range"] = "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026"

html_path = generate_security_report(report_data, "security_report.html")
html_to_pdf(html_path, "security_report.pdf")

# Step 4: Review stats
categorizer.print_stats()
processor.print_stats()

print(f"\n✅ Report generated: security_report.pdf")
```

---

## Summary

The security categorization system:
- ✅ Automatically categorizes ALL security data
- ✅ Uses intelligent keyword matching
- ✅ Supports 3 official categories only
- ✅ Provides confidence scoring
- ✅ Integrates with existing pipeline
- ✅ Generates statistics
- ✅ Fully customizable

All security incidents will be properly categorized and formatted in detailed narrative style!

---

**Document Version:** 1.0  
**Last Updated:** March 28, 2026  
**Module:** security_categorizer.py
