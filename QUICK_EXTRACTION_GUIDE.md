# Quick Extraction Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Prepare Your PDF Text

```bash
# If you have a PDF, extract text first
# (You can use any PDF to text tool)
# Save as: report.txt
```

### Step 2: Run Extraction

```bash
python complete_data_extraction_tool.py report.txt
```

### Step 3: Get Results

```
✓ report_extracted.json  (Full structured data)
✓ report_summary.txt     (Human-readable summary)
```

## 📊 What Gets Extracted

### Header Information
- Report title
- Date range (start/end)
- Time period

### For Each Category (1-29)
- Category number and name
- Status (නැත or incident count)
- List of incidents with:
  - Police station
  - Date and time
  - Location
  - Victim details (name, age, gender, occupation, address, phone)
  - Suspect details (name, age, gender, occupation, address, phone)
  - Description
  - Financial loss
  - Status

### Metadata
- Extraction timestamp
- Total categories
- Categories with incidents

## 🔧 Common Use Cases

### Use Case 1: Extract Everything

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor

with open('report.txt', 'r', encoding='utf-8') as f:
    text = f.read()

extractor = SinhalaPoliceReportExtractor()
data = extractor.extract_all(text)
extractor.save_to_json(data, 'output.json')
```

### Use Case 2: Get Only Active Categories

```python
active = {
    num: cat for num, cat in data['categories'].items()
    if cat.get('status') != 'නැත' and cat['summary']['total_incidents'] > 0
}
```

### Use Case 3: Calculate Total Financial Loss

```python
total = 0
for cat in data['categories'].values():
    for incident in cat['incidents']:
        if incident.get('financial_loss'):
            total += int(incident['financial_loss'].replace(',', ''))
print(f"Total loss: Rs. {total:,}")
```

### Use Case 4: Find All Arrests

```python
arrests = []
for cat in data['categories'].values():
    for incident in cat['incidents']:
        if 'අත් අඩංගුවට' in incident.get('status', ''):
            arrests.append(incident)
print(f"Total arrests: {len(arrests)}")
```

### Use Case 5: Export to CSV

```python
import csv

with open('incidents.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Category', 'Station', 'Date', 'Location', 'Description'])
    
    for cat_num, cat in data['categories'].items():
        for incident in cat['incidents']:
            writer.writerow([
                cat['category_name'],
                incident.get('police_station', ''),
                incident.get('date', ''),
                incident.get('location', ''),
                incident.get('description', '')[:100]  # First 100 chars
            ])
```

## 📋 Category Quick Reference

| # | Category | Sinhala |
|---|----------|---------|
| 01 | Terrorism | ත්‍රස්තවාදී ක්‍රියාකාරකම |
| 02 | Weapons | අවි ආයුධ සොයා ගැනීම |
| 03 | Protests | උද්ඝෝෂණ |
| 04 | Murder | මිනීමැරීම |
| 05 | Robbery | කොල්ලකෑම |
| 06 | Vehicle Theft | වාහන සොරකම |
| 07 | Property Theft | දේපළ සොරකම |
| 08 | Burglary | ගෙවල් බිඳ |
| 09 | Sexual Assault | ස්ත්‍රී දූෂණ |
| 10 | Traffic Accidents | මාර්ග රිය අනතුරු |
| 20 | Drug Seizures | මත් ද්‍රව්‍ය අත්අඩංගුට |
| 23 | Missing Persons | අතුරුදහන්වී |
| 24 | Suicides | සියදිවි හානිකර ගැනී |

## 🎯 Output Examples

### JSON Output Structure

```json
{
  "header": {
    "report_title": "දෛනික සිදුවීම් වාර්ථාව",
    "date_range": {
      "start_date": "2026.03.22",
      "start_time": "0400",
      "end_date": "2026.03.23",
      "end_time": "0400"
    }
  },
  "categories": {
    "01": {
      "category_name": "ත්‍රස්තවාදී ක්‍රියාකාරකම",
      "status": "නැත",
      "incidents": []
    },
    "02": {
      "category_name": "අවි ආයුධ සොයා ගැනීම",
      "incidents": [
        {
          "police_station": "ඉගිණියාගල",
          "date": "2026.03.22",
          "suspect": {
            "name": "රාජ්කුමාර් ඉන්ද දර්ශන",
            "age": "32",
            "gender": "පුරුෂ"
          }
        }
      ]
    }
  }
}
```

### Summary Output

```
================================================================================
දෛනික සිදුවීම් වාර්ථාව - සාරාංශය
================================================================================

වාර්තා කාලය: 2026.03.22 පැය 0400 සිට 2026.03.23 දින පැය 0400 දක්වා

ප්‍රවර්ග සාරාංශය:
--------------------------------------------------------------------------------
01. ත්‍රස්තවාදී ක්‍රියාකාරකම: නැත
02. අවි ආයුධ සොයා ගැනීම: 2 සිදුවීම්
03. උද්ඝෝෂණ: 1 සිදුවීම්
...
```

## ⚡ Performance Tips

1. **Large Files**: Process in chunks if file > 10MB
2. **Multiple Reports**: Use batch processing
3. **Memory**: Clear data after saving to JSON
4. **Speed**: Use multiprocessing for multiple files

## 🐛 Troubleshooting

### Problem: No data extracted

```python
# Check if text is properly loaded
print(len(pdf_text))  # Should be > 0
print(pdf_text[:100])  # Check first 100 chars
```

### Problem: Sinhala text garbled

```python
# Always use UTF-8 encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
```

### Problem: Missing incidents

```python
# Check if category is marked as නැත
if extractor.is_nil_category(text, "01"):
    print("Category 01 has no incidents")
```

## 📞 Need Help?

1. Check `EXTRACTION_TOOL_GUIDE.md` for detailed documentation
2. Run `python test_extraction_tool.py` to see examples
3. Review the code comments in `complete_data_extraction_tool.py`

## 🎓 Learning Path

1. **Beginner**: Use command line tool
   ```bash
   python complete_data_extraction_tool.py report.txt
   ```

2. **Intermediate**: Use Python API
   ```python
   extractor = SinhalaPoliceReportExtractor()
   data = extractor.extract_all(text)
   ```

3. **Advanced**: Customize extraction logic
   ```python
   # Add your own category handler
   def extract_custom_category(self, text):
       # Your logic here
       pass
   ```

## ✅ Checklist

Before running extraction:
- [ ] PDF text is properly extracted
- [ ] File encoding is UTF-8
- [ ] Sinhala characters are visible
- [ ] File size is reasonable (< 50MB)

After extraction:
- [ ] JSON file is created
- [ ] Summary file is created
- [ ] Data looks correct
- [ ] No encoding errors

## 🚀 Next Steps

1. Extract your first report
2. Review the JSON output
3. Customize for your needs
4. Integrate with your system

Happy extracting! 🎉
