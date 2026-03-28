# Complete Data Extraction Tool - User Guide

## Overview

The **Complete Data Extraction Tool** (`complete_data_extraction_tool.py`) is a comprehensive Python tool that extracts ALL data from Sinhala police daily incident reports (දෛනික සිදුවීම් වාර්ථාව) and structures it into JSON format.

## Features

✅ **Complete Data Extraction**
- Extracts header information (date range, report period)
- Processes all 29 incident categories
- Handles tables with multiple columns
- Extracts suspect/victim details
- Captures financial losses
- Preserves Sinhala text accurately

✅ **Smart Processing**
- Handles "නැත" (nil/none) entries
- Extracts location and time information
- Parses person details (name, age, gender, occupation, address, phone)
- Cleans and normalizes text

✅ **Multiple Output Formats**
- JSON (structured data)
- Text summary (human-readable)

## Installation

```bash
# No additional dependencies required
# Uses only Python standard library
python --version  # Requires Python 3.7+
```

## Usage

### Method 1: Command Line

```bash
# Extract from a text file
python complete_data_extraction_tool.py report.txt

# This will create:
# - report_extracted.json (full data)
# - report_summary.txt (summary)
```

### Method 2: Python Script

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor

# Read your PDF text
with open('report.txt', 'r', encoding='utf-8') as f:
    pdf_text = f.read()

# Create extractor
extractor = SinhalaPoliceReportExtractor()

# Extract all data
data = extractor.extract_all(pdf_text)

# Save to JSON
extractor.save_to_json(data, 'output.json')

# Generate summary
summary = extractor.generate_summary(data)
print(summary)
```

### Method 3: Extract Specific Categories

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor

extractor = SinhalaPoliceReportExtractor()

# Extract only header
header = extractor.extract_header(pdf_text)

# Extract specific category
category_02 = extractor.extract_category_data(pdf_text, "02")

# Extract person details
victim = extractor.extract_person_details(text_section, "පැමිණිලිකරු")
suspect = extractor.extract_person_details(text_section, "සැකකරු")
```

## Output Format

### JSON Structure

```json
{
  "header": {
    "report_title": "දෛනික සිදුවීම් වාර්ථාව",
    "date_range": {
      "start_date": "2026.03.22",
      "start_time": "0400",
      "end_date": "2026.03.23",
      "end_time": "0400"
    },
    "report_period": "2026.03.22 පැය 0400 සිට 2026.03.23 දින පැය 0400 දක්වා"
  },
  "categories": {
    "01": {
      "category_number": "01",
      "category_name": "ත්‍රස්තවාදී ක්‍රියාකාරකම",
      "status": "නැත",
      "incidents": [],
      "summary": {
        "total_incidents": 0,
        "resolved": 0,
        "unresolved": 0
      }
    },
    "02": {
      "category_number": "02",
      "category_name": "අවි ආයුධ සොයා ගැනීම",
      "incidents": [
        {
          "police_station": "ඉගිණියාගල",
          "date": "2026.03.22",
          "time": "1440",
          "location": "හිමිදුරාල ලැල රක්ෂිතය",
          "victim": {
            "name": "",
            "age": "",
            "gender": "",
            "occupation": "",
            "address": "",
            "phone": ""
          },
          "suspect": {
            "name": "රාජ්කුමාර් ඉන්ද දර්ශන",
            "age": "32",
            "gender": "පුරුෂ",
            "occupation": "නැත",
            "address": "වට්ටුපිත්තාන්මඩු, උයිරංකුලම",
            "phone": ""
          },
          "description": "...",
          "financial_loss": "",
          "status": "අත් අඩංගුවට ගෙන ඇත"
        }
      ],
      "summary": {
        "total_incidents": 2,
        "resolved": 2,
        "unresolved": 0
      }
    }
  },
  "metadata": {
    "extraction_date": "2024-01-15T10:30:00",
    "total_categories": 29,
    "categories_with_incidents": 15
  }
}
```

## All 29 Categories

The tool handles all these categories:

1. ත්‍රස්තවාදී ක්‍රියාකාරකම (Terrorism)
2. අවි ආයුධ සොයා ගැනීම (Weapons/Explosives)
3. උද්ඝෝෂණ (Protests)
4. මිනීමැරීම (Murder)
5. කොල්ලකෑම (Robbery)
6. වාහන සොරකම (Vehicle Theft)
7. දේපළ සොරකම (Property Theft)
8. ගෙවල් බිඳ (Burglary)
9. ස්ත්‍රී දූෂණ (Sexual Assault)
10. මාර්ග රිය අනතුරු (Traffic Accidents)
11. නාදුනන මළ සිරුරු (Unidentified Bodies)
12. පොලිස් රිය අනතුරු (Police Vehicle Accidents)
13. පොලිස් නිලධාරීන්ට තුවාල (Police Injuries)
14. පොලිස් නිලධාරීන්ගේ විෂමාචාර (Police Misconduct)
15. පොලිස් නිලධාරීන් මියයෑ (Police Deaths)
16. රාජ්‍ය නිෂේධිත නිලධාරීන් රෝහල් ගතවී (Officers Hospitalized)
17. රාජ්‍ය නිෂේධිත නිලධාරීන්ගේ ළඟම ඥාතීන් මියයෑ (Officers' Relatives Deaths)
18. විශ්‍රාමික නිලධාරීන්ගේ ඥාතීන් මියයෑ (Retired Officers' Relatives Deaths)
19. නිවාඩු ලබා සිටින නිලධාරීන් (Officers on Leave)
20. මත් ද්‍රව්‍ය අත්අඩංගුට ගැනී (Drug Seizures)
21. අත්අඩංගුට ගැනී (Arrests)
22. ත්‍රිවිධ හමුදා සාමාජිකයින් (Military Personnel)
23. අතුරුදහන්වී (Missing Persons)
24. සියදිවි හානිකර ගැනී (Suicides)
25. විදේශ සාමිකයින් (Foreign Nationals)
26. වනඅලි පහරදී (Elephant Attacks)
27. දියේ ගිලී මියයෑ (Drowning)
28. ගිනි ගැනීම (Fire Incidents)
29. වෙනත් විශේෂ සිදුවීම (Other Special Incidents)

## Key Functions

### `extract_header(text)`
Extracts report header with date range and period.

### `extract_category_data(text, category_num)`
Extracts all data for a specific category.

### `is_nil_category(text, category_num)`
Checks if a category has no incidents (නැත).

### `extract_table_incidents(text, category_num)`
Extracts incidents from table format.

### `extract_person_details(text, person_type)`
Extracts person details (name, age, gender, occupation, address, phone).

### `extract_all(pdf_text)`
Extracts complete data from the entire report.

### `save_to_json(data, output_file)`
Saves extracted data to JSON file.

### `generate_summary(data)`
Generates human-readable text summary.

## Examples

### Example 1: Basic Extraction

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor

# Read report
with open('march22_report.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract
extractor = SinhalaPoliceReportExtractor()
data = extractor.extract_all(text)

# Save
extractor.save_to_json(data, 'march22_data.json')

print(f"Extracted {data['metadata']['categories_with_incidents']} categories with incidents")
```

### Example 2: Filter Specific Categories

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor

extractor = SinhalaPoliceReportExtractor()
data = extractor.extract_all(text)

# Get only categories with incidents
active_categories = {
    cat_num: cat_data 
    for cat_num, cat_data in data['categories'].items()
    if cat_data.get('status') != 'නැත' and cat_data['summary']['total_incidents'] > 0
}

print(f"Active categories: {len(active_categories)}")
for cat_num, cat_data in active_categories.items():
    print(f"{cat_num}. {cat_data['category_name']}: {cat_data['summary']['total_incidents']} incidents")
```

### Example 3: Extract Financial Losses

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor

extractor = SinhalaPoliceReportExtractor()
data = extractor.extract_all(text)

total_loss = 0
for cat_data in data['categories'].values():
    for incident in cat_data['incidents']:
        if incident.get('financial_loss'):
            # Remove commas and convert to int
            loss = int(incident['financial_loss'].replace(',', ''))
            total_loss += loss

print(f"Total financial loss: Rs. {total_loss:,}")
```

## Testing

Run the test script:

```bash
python test_extraction_tool.py
```

This will:
1. Test header extraction
2. Test category extraction
3. Test full extraction
4. Generate sample output files

## Troubleshooting

### Issue: Missing data in extraction

**Solution**: Check if the PDF text format matches expected patterns. The tool uses regex patterns that may need adjustment for different report formats.

### Issue: Sinhala text not displaying correctly

**Solution**: Ensure your terminal/editor supports UTF-8 encoding:
```python
# When opening files
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
```

### Issue: Empty incidents list

**Solution**: The category might be marked as "නැත" or the text pattern might not match. Check the raw text and adjust regex patterns if needed.

## Extending the Tool

### Add New Category Handler

```python
def extract_custom_category(self, text: str) -> List[Dict[str, Any]]:
    """Extract custom category data"""
    incidents = []
    
    # Your extraction logic here
    pattern = r'your_pattern'
    matches = re.finditer(pattern, text)
    
    for match in matches:
        incident = {
            "field1": match.group(1),
            "field2": match.group(2)
        }
        incidents.append(incident)
    
    return incidents
```

### Customize Output Format

```python
def export_to_csv(self, data: Dict[str, Any], output_file: str):
    """Export data to CSV format"""
    import csv
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write your CSV logic here
```

## Best Practices

1. **Always use UTF-8 encoding** when reading/writing files
2. **Validate extracted data** before using in production
3. **Keep backup** of original PDF text
4. **Test with multiple reports** to ensure consistency
5. **Log extraction errors** for debugging

## Support

For issues or questions:
1. Check the test script for examples
2. Review the regex patterns in the code
3. Ensure PDF text is properly extracted
4. Verify Sinhala Unicode characters are preserved

## License

This tool is provided as-is for processing Sinhala police reports.
