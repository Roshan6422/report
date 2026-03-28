"""
Test extraction for March 22, 2026 report
"""

# Sample text from the PDF (first few categories)
pdf_text = """
දෛනික සිදුවීම් වාර්ථාව
2026.03.21 වන දින පැය 0400 සිට 2026.03.22 වන දින පැය 0400 දක්වා

01. ත්‍රස්තවාදී ක්‍රියාකාරකම : නැත.

02. අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උ ඩ :- 08

1. තන්තිරිමඩුව OTM 1729 කොට්ඨාශය අනුරාධපුර 2026.03.21 දින IR 2026.03.21 පැය 1729
නැත සබෝ බ නිෂ්කාශිත ආයතනය ස වන MAG ආයතනයේ සේවකයින් විසින් තන්තිරිමඩුව ශදපාන්ස්කොඩ වාසේ සේඩවර විදුලි වාට ආවන්නයේ තිබි පුද්ගඩ නාඩඩ බි සබෝ බය ව (සොනි බට්ටා සොයා සඟන ඇත.

2. නාන්සන්රිය OTM 1746 කොට්ඨාශය නිඩවාරටිය 2026.03.21 දින IR 2026.03.21 පැය 2032
ආර්.එ .නවරත්න බංඩාර රත්නායඩ, අවුරුදු 52 යි, පුරුෂ, රැකියාව, සඟොවිතාන, ඉශඩ නාන්සන්රිය, මශ නාන්සන්රිය
ඉශඩ නාන්සන්රිය ප්‍රදේශයේදි සමරට නිෂ්හපාදිත සබසශත් සඟොටන තුව වකුව ව වම඙ වාඩඩරුසවකු අත්අඩංගුවට සඟන ඇත.

3. දඹඩල්ඩ OTM 1740 කොට්ඨාශය සමොණරාඩඩ 2026.03.21 පැය 1130 IR 2026.03.21 පැය 1937
නැත තඹාන සඟොහිඩ ආර ඩන්ද ර වෂිත ප්‍රදේශයේ තිී වාඩඩරුසවකු සනොමැති සමරට නිෂ්හපාදිත බඳින තුව වකු 02 ව ශා සබසශත් සඟොටන තුව වකුව ව අත්අඩංගුවට සඟන ඇත.

03. උද්සකෝෂණ :- 01

04. මිනීමැරීම :- 01

1. යාපනය CTM 638 OTM 1702 කොට්ඨාශය යාපනය 2026.03.17 රාත්‍රි කඩවේදි ST 2026.03.19 පැය 0730 IR 2026.03.21 පැය 0952
අංඩ 27 28, පුන්඙ කුඩ පාර, චුන්ඩු වකුවි, යාපනය
තිවිපන් දයාවිනි, අවුරුදු 53 යි, වහත්‍රි, විෂඩව විදයාඩ සද්ශඩක, අංඩ 27 28, පුන්඙ කුඩ පාර, චුන්ඩු වකුවි, යාපනය

1.තිනකර් තිවාකර්, අවුරුදු 20 යි, පුරුෂ, අංඩ 17, රාසේශවරි විදිය, නයන්මාර්ඩට්ටු, යාපනය
2.තිවිපන් සුවිතියා, අවුරුදු 19 යි, වහත්‍රි, අංඩ 27 28, පුන්඙ කුඩ පාර, චුන්ඩු වකුවි, යාපනය, අත්අඩංගුවට සඟන ඇත.

සකොල්ඩඩකන ඩද රන් භාණ්ඩඩ සවොයා සඟන ඇත.
"""

from complete_data_extraction_tool import SinhalaPoliceReportExtractor
import json

# Create extractor
extractor = SinhalaPoliceReportExtractor()

# Extract header
print("=" * 80)
print("HEADER EXTRACTION TEST")
print("=" * 80)
header = extractor.extract_header(pdf_text)
print(json.dumps(header, ensure_ascii=False, indent=2))

# Test category 01 (nil)
print("\n" + "=" * 80)
print("CATEGORY 01 TEST (NIL)")
print("=" * 80)
cat01 = extractor.extract_category_data(pdf_text, "01")
print(json.dumps(cat01, ensure_ascii=False, indent=2))

# Test category 02 (weapons)
print("\n" + "=" * 80)
print("CATEGORY 02 TEST (WEAPONS - 8 incidents)")
print("=" * 80)
cat02 = extractor.extract_category_data(pdf_text, "02")
print(json.dumps(cat02, ensure_ascii=False, indent=2))

# Test category 04 (murder)
print("\n" + "=" * 80)
print("CATEGORY 04 TEST (MURDER - 1 incident)")
print("=" * 80)
cat04 = extractor.extract_category_data(pdf_text, "04")
print(json.dumps(cat04, ensure_ascii=False, indent=2))

print("\n" + "=" * 80)
print("EXTRACTION TEST COMPLETE")
print("=" * 80)
