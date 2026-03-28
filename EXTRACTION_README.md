# 🎯 Complete Data Extraction Tool

## මෙය කරන්නේ මොකක්ද? (What does this do?)

This tool extracts **ALL data** from Sinhala police daily incident reports (දෛනික සිදුවීම් වාර්ථාව) and converts it into structured JSON format.

## 🚀 Quick Start (3 Steps)

### 1️⃣ Prepare Your Report

Save your PDF text as `report.txt` (UTF-8 encoding)

### 2️⃣ Run the Tool

```bash
python complete_data_extraction_tool.py report.txt
```

### 3️⃣ Get Your Results

```
✅ report_extracted.json  (Complete structured data)
✅ report_summary.txt     (Human-readable summary)
```

## 📦 What You Get

### JSON Output (Structured Data)

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
          "time": "1440",
          "location": "හිමිදුරාල ලැල රක්ෂිතය",
          "suspect": {
            "name": "රාජ්කුමාර් ඉන්ද දර්ශන",
            "age": "32",
            "gender": "පුරුෂ",
            "occupation": "නැත",
            "address": "වට්ටුපිත්තාන්මඩු, උයිරංකුලම"
          },
          "description": "...",
          "financial_loss": "",
          "status": "අත් අඩංගුවට ගෙන ඇත"
        }
      ],
      "summary": {
        "total_incidents": 2
      }
    }
  }
}
```

### Text Summary (Human-Readable)

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
04. මිනීමැරීම: 1 සිදුවීම්
...
```

## 🎯 Features

### ✅ Complete Extraction
- All 29 incident categories
- Header information (dates, times)
- Incident details (location, time, description)
- Person details (victim/suspect)
- Financial losses
- Status information

### ✅ Smart Processing
- Handles "නැත" (nil) entries
- Preserves Sinhala Unicode
- Cleans and normalizes text
- Validates data structure

### ✅ Multiple Outputs
- JSON (for programs)
- Text summary (for humans)
- Customizable formats

## 📊 All 29 Categories

| # | Category (English) | Category (Sinhala) |
|---|-------------------|-------------------|
| 01 | Terrorism | ත්‍රස්තවාදී ක්‍රියාකාරකම |
| 02 | Weapons/Explosives | අවි ආයුධ සොයා ගැනීම |
| 03 | Protests | උද්ඝෝෂණ |
| 04 | Murder | මිනීමැරීම |
| 05 | Robbery | කොල්ලකෑම |
| 06 | Vehicle Theft | වාහන සොරකම |
| 07 | Property Theft | දේපළ සොරකම |
| 08 | Burglary | ගෙවල් බිඳ |
| 09 | Sexual Assault | ස්ත්‍රී දූෂණ |
| 10 | Traffic Accidents | මාර්ග රිය අනතුරු |
| 11 | Unidentified Bodies | නාදුනන මළ සිරුරු |
| 12 | Police Vehicle Accidents | පොලිස් රිය අනතුරු |
| 13 | Police Injuries | පොලිස් නිලධාරීන්ට තුවාල |
| 14 | Police Misconduct | පොලිස් නිලධාරීන්ගේ විෂමාචාර |
| 15 | Police Deaths | පොලිස් නිලධාරීන් මියයෑ |
| 16 | Officers Hospitalized | රාජ්‍ය නිෂේධිත නිලධාරීන් රෝහල් ගතවී |
| 17 | Officers' Relatives Deaths | රාජ්‍ය නිෂේධිත නිලධාරීන්ගේ ළඟම ඥාතීන් මියයෑ |
| 18 | Retired Officers' Relatives Deaths | විශ්‍රාමික නිලධාරීන්ගේ ඥාතීන් මියයෑ |
| 19 | Officers on Leave | නිවාඩු ලබා සිටින නිලධාරීන් |
| 20 | Drug Seizures | මත් ද්‍රව්‍ය අත්අඩංගුට ගැනී |
| 21 | Arrests | අත්අඩංගුට ගැනී |
| 22 | Military Personnel | ත්‍රිවිධ හමුදා සාමාජිකයින් |
| 23 | Missing Persons | අතුරුදහන්වී |
| 24 | Suicides | සියදිවි හානිකර ගැනී |
| 25 | Foreign Nationals | විදේශ සාමිකයින් |
| 26 | Elephant Attacks | වනඅලි පහරදී |
| 27 | Drowning | දියේ ගිලී මියයෑ |
| 28 | Fire Incidents | ගිනි ගැනීම |
| 29 | Other Special Incidents | වෙනත් විශේෂ සිදුවීම |

## 💻 Usage Examples

### Example 1: Basic Usage

```bash
python complete_data_extraction_tool.py march22_report.txt
```

### Example 2: Python API

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor

# Read report
with open('report.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract
extractor = SinhalaPoliceReportExtractor()
data = extractor.extract_all(text)

# Save
extractor.save_to_json(data, 'output.json')

# Print summary
print(extractor.generate_summary(data))
```

### Example 3: Get Statistics

```python
# Total incidents
total = sum(cat['summary']['total_incidents'] 
           for cat in data['categories'].values())
print(f"Total incidents: {total}")

# Active categories
active = sum(1 for cat in data['categories'].values()
            if cat.get('status') != 'නැත')
print(f"Active categories: {active}")

# Total financial loss
loss = 0
for cat in data['categories'].values():
    for incident in cat['incidents']:
        if incident.get('financial_loss'):
            loss += int(incident['financial_loss'].replace(',', ''))
print(f"Total loss: Rs. {loss:,}")
```

## 📚 Documentation

| File | Description |
|------|-------------|
| `TOOL_SUMMARY.md` | Complete overview |
| `QUICK_EXTRACTION_GUIDE.md` | Quick start guide |
| `EXTRACTION_TOOL_GUIDE.md` | Full API reference |
| `test_extraction_tool.py` | Test examples |

## 🧪 Testing

```bash
# Run test
python test_extraction_tool.py

# Check output
cat test_output.json
cat test_summary.txt
```

## 🔧 Requirements

- Python 3.7+
- No external dependencies (uses only standard library)
- UTF-8 text encoding

## 📁 Files

```
complete_data_extraction_tool.py  (Main tool - 500+ lines)
test_extraction_tool.py           (Test script)
extract_march22_report.py         (Example usage)
EXTRACTION_README.md              (This file)
TOOL_SUMMARY.md                   (Complete overview)
QUICK_EXTRACTION_GUIDE.md         (Quick reference)
EXTRACTION_TOOL_GUIDE.md          (Full documentation)
```

## ⚡ Quick Commands

```bash
# Extract data
python complete_data_extraction_tool.py report.txt

# Run tests
python test_extraction_tool.py

# Process March 22 report
python extract_march22_report.py

# View JSON output
cat report_extracted.json | python -m json.tool

# View summary
cat report_summary.txt
```

## 🎯 What Gets Extracted

For each incident:
- ✅ Police station name
- ✅ Date and time
- ✅ Location
- ✅ Victim details (name, age, gender, occupation, address, phone)
- ✅ Suspect details (name, age, gender, occupation, address, phone)
- ✅ Full description
- ✅ Financial loss amount
- ✅ Status (arrested, under investigation, etc.)

## 🚀 Next Steps

1. **Test it**: Run `python test_extraction_tool.py`
2. **Use it**: Process your March 22 report
3. **Customize it**: Modify for your specific needs
4. **Integrate it**: Connect to your database/system

## 📞 Need Help?

1. Read `QUICK_EXTRACTION_GUIDE.md` for quick start
2. Check `EXTRACTION_TOOL_GUIDE.md` for full documentation
3. Run `test_extraction_tool.py` to see examples
4. Review code comments in `complete_data_extraction_tool.py`

## ✅ Success Checklist

- [ ] Tool installed and working
- [ ] Test script runs successfully
- [ ] Sample output looks correct
- [ ] Sinhala text displays properly
- [ ] JSON structure is valid
- [ ] Ready to process real reports

## 🎉 You're Ready!

The tool is **complete and ready to use**. Just run:

```bash
python complete_data_extraction_tool.py your_report.txt
```

And you'll get structured JSON data + human-readable summary! 🎊

---

**Created**: March 28, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
