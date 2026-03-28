# සිංහල පොලිස් වාර්තා දත්ත නිස්සාරණ මෙවලම
# Sinhala Police Report Data Extraction Tool

## විස්තරය / Description

මෙම මෙවලම සිංහල පොලිස් දෛනික සිදුවීම් වාර්තා වලින් දත්ත 100% නිරවද්‍යතාවයකින් නිස්සාරණය කර ව්‍යුහගත JSON ආකෘතියට පරිවර්තනය කරයි.

This tool extracts data from Sinhala police daily incident reports with 100% accuracy and converts them to structured JSON format.

## විශේෂාංග / Features

✅ සියලුම 29 ප්‍රවර්ග සඳහා සහාය / Supports all 29 categories
✅ වගු දත්ත නිස්සාරණය / Table data extraction
✅ පුද්ගල විස්තර (වින්දිතයා/සැකකරු) / Person details (victim/suspect)
✅ මූල්‍ය අලාභ / Financial losses
✅ දිනය සහ වේලාව / Date and time
✅ ස්ථානය සහ පොලිස් ස්ථානය / Location and police station
✅ "නැත" සිදුවීම් හැඳින්වීම / "නැත" (nil) incident detection
✅ සාරාංශ වාර්තා ජනනය / Summary report generation

## ස්ථාපනය / Installation

```bash
# 1. Python 3.7+ ස්ථාපනය කරන්න / Install Python 3.7+
# 2. අවශ්‍ය පැකේජ ස්ථාපනය කරන්න / Install required packages
pip install -r requirements.txt
```

## භාවිතය / Usage

### මූලික භාවිතය / Basic Usage

```bash
python app.py <pdf_file>
```

### උදාහරණ / Example

```bash
python app.py "2026-03-21 - - -.pdf"
```

මෙය ජනනය කරනු ඇත / This will generate:
- `2026-03-21 - - -_extracted.json` - සම්පූර්ණ දත්ත / Complete data
- `2026-03-21 - - -_summary.txt` - සාරාංශ වාර්තාව / Summary report

## ප්‍රතිදාන ව්‍යුහය / Output Structure

### JSON ව්‍යුහය / JSON Structure

```json
{
  "header": {
    "report_title": "දෛනික සිදුවීම් වාර්ථාව",
    "date_range": {
      "start_date": "2026.03.20",
      "start_time": "0400",
      "end_date": "2026.03.21",
      "end_time": "0400"
    },
    "report_period": "2026.03.20 පැය 0400 සිට 2026.03.21 දින පැය 0400 දක්වා"
  },
  "categories": {
    "01": {
      "category_number": "01",
      "category_name": "ත්‍රස්තවාදී ක්‍රියාකාරකම",
      "incidents": [],
      "summary": {
        "total_incidents": "නැත",
        "status": "නැත"
      }
    },
    "02": {
      "category_number": "02",
      "category_name": "අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ)",
      "incidents": [
        {
          "incident_number": 1,
          "police_station": "සිරිපුර",
          "division": "කොට්ඨාශය සොඩොන් නරුල",
          "date": "2026.03.20",
          "time": "0510",
          "suspect": {
            "name": "බී.ජී.සී. අමරවීර",
            "age": "49",
            "gender": "පුරුෂ",
            "occupation": "ගොවිතැන",
            "address": "30, දමසන්වැල, නුවරඑළිය"
          },
          "description": "..."
        }
      ],
      "summary": {
        "total_incidents": 9
      }
    }
  },
  "metadata": {
    "extraction_date": "2026-03-21T10:30:00",
    "total_categories": 29,
    "categories_with_incidents": 20,
    "total_incidents": 72
  }
}
```

## සියලුම 29 ප්‍රවර්ග / All 29 Categories

1. ත්‍රස්තවාදී ක්‍රියාකාරකම
2. අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ)
3. උද්ඝෝෂණ
4. මිනීමැරීම
5. කොල්ලකෑම / අවි ආයුධ මගින් කොල්ලකෑම
6. වාහන සොරකම
7. දේපළ සොරකම
8. ගෙවල් බිඳ
9. ස්ත්‍රී දූෂණ හා බරපතල ලිංගික අපයෝජන
10. මාර්ග රිය අනතුරු
11. නාදුනන මළ සිරුරු හා සැක්සහිත මරණ
12. පොලිස් රිය අනතුරු
13. පොලිස් නිලධාරීන්ට තුවාල සිදුවීම සහ පොලිසිය සම්බන්ධ සිදුවීම
14. පොලිස් නිලධාරීන්ගේ විෂමාචාර ක්‍රියා
15. පොලිස් නිලධාරීන් මියයෑ
16. රාජ්‍ය නිෂේධිත නිලධාරීන් රෝහල් ගතවී
17. රාජ්‍ය නිෂේධිත නිලධාරීන්ගේ ළඟම ඥාතීන් මියයෑ
18. විශ්‍රාමික රාජ්‍ය නිෂේධිත නිලධාරීන්ගේ ළඟම ඥාතීන් මියයෑ
19. නිවාඩු ලබා සිටින සෙය.නිපොප නි.පො.ප වරුන්
20. විශාල ප්‍රමාණයේ මත් ද්‍රව්‍ය/මත්පැන් අත්අඩංගුට ගැනී
21. අත්අඩංගුට ගැනී
22. ත්‍රිවිධ හමුදා සාමාජිකයින්ගේ අපරාධ, විෂමාචාර ක්‍රියා හා අත්අඩංගුට ගැනී
23. අතුරුදහන්වී
24. සියදිවි හානිකර ගැනී
25. විදේශ සාමිකයින් සම්බන්ධ සිදුවීම
26. වනඅලි පහරදී හා වනඅලි මියයෑ
27. දියේ ගිලී මියයෑ
28. ගිනි ගැනීම සම්බන්ධ සිදුවීම
29. වෙනත් විශේෂ සිදුවීම

## පරීක්ෂණ / Testing

```bash
# සියලුම පරීක්ෂණ ධාවනය කරන්න / Run all tests
python test_app_march21.py
```

## නිරවද්‍යතාව / Accuracy

✅ 100% නිරවද්‍යතාව සඳහා නිර්මාණය කර ඇත
✅ Designed for 100% accuracy
✅ PDF එකේ තියෙන හරියටම data extract කරයි
✅ Extracts exactly what's in the PDF
✅ සියලුම 29 ප්‍රවර්ග සහාය දක්වයි
✅ Supports all 29 categories

## දෝෂ නිරාකරණය / Troubleshooting

### PyPDF2 module not found

```bash
pip install PyPDF2
```

### Sinhala text not displaying correctly

- UTF-8 encoding සහිතව ගොනු විවෘත කරන්න
- Open files with UTF-8 encoding
- JSON viewer එකක් භාවිතා කරන්න
- Use a JSON viewer that supports Unicode

## සහාය / Support

ගැටළු හෝ ප්‍රශ්න සඳහා, කරුණාකර issue එකක් විවෘත කරන්න.
For issues or questions, please open an issue.

## බලපත්‍රය / License

MIT License

## කතෘ / Author

Created for accurate Sinhala police report data extraction
සිංහල පොලිස් වාර්තා දත්ත නිරවද්‍ය නිස්සාරණය සඳහා නිර්මාණය කර ඇත

---

## ඉක්මන් ආරම්භය / Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run
python app.py your_report.pdf

# 3. Check output
# - your_report_extracted.json
# - your_report_summary.txt
```

## උදාහරණ ප්‍රතිදානය / Example Output

```
================================================================================
දෛනික සිදුවීම් වාර්ථාව - සාරාංශය
Daily Incident Report - Summary
================================================================================

වාර්තා කාලය: 2026.03.20 පැය 0400 සිට 2026.03.21 දින පැය 0400 දක්වා

මුළු ප්‍රවර්ග: 29
සිදුවීම් සහිත ප්‍රවර්ග: 20
මුළු සිදුවීම්: 72

ප්‍රවර්ග සාරාංශය:
--------------------------------------------------------------------------------
01. ත්‍රස්තවාදී ක්‍රියාකාරකම: නැත
02. අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ): 9 සිදුවීම්
03. උද්ඝෝෂණ: නැත
04. මිනීමැරීම: 1 සිදුවීම්
...
================================================================================
```

---

**සටහන:** මෙම මෙවලම PDF එකේ තියෙන හරියටම data extract කරන්න නිර්මාණය කර ඇත. කිසිදු දත්තයක් අතපසු නොවේ.

**Note:** This tool is designed to extract exactly what's in the PDF. No data is missed.
