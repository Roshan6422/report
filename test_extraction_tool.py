"""
Test script for the complete data extraction tool
"""

from complete_data_extraction_tool import SinhalaPoliceReportExtractor
import json

# Sample text from the PDF you provided
sample_text = """
දෛනික සිදුවීම් වාර්ථාව
2026.03.22 වන දින පැය 0400 සිට 2026.03.23 දින පැය 0400 දක්වා

01. ත්‍රස්තවාදී ක්‍රියාකාරකම : නැත.

02. අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ) :- 02

1. ඉගිණියාගල
   OTM 1840
   කොට්ඨාශය අපාර
   2026.03.22 පැය 1440
   IR 2026.03.22 පැය 2324
   
   සනොදනි ඉගිණියාගල පොලිස් ස්ථානයේ නිලධාරින් විසින් හිමිදුරාල ලැල රක්ෂිතයේ සිදු කරන මෙහෙයුම දී සැකකරුවකු නොමැති මෙරට නිෂ්පාදිත ජෙසේත් පොටන ගදින තුල්කුලක් සොයා ගෙන ඇත.

2. උයිරංකුලම
   OTM 1848
   කොට්ඨාශය මන්නාරම
   2026.03.22
   IR 2026.03.23 පැය 0022
   
   රාජ්කුමාර් ඉන්ද දර්ශන
   අවු :32
   පුරුෂ
   රැකියාව : නැත
   වට්ටුපිත්තාන්මඩු, උයිරංකුලම
   
   මන්නාරම පොලිස් විශේෂ පාර්ය ගදවුරේ නිලධාරින් විසින් මෙම සැකකරු ගදපත්‍රයක් නොමැතිව වෝටර් ජෙල් වර්ගයේ පුපුරණ ද්‍රවය කරල් 300 ක් සන්තකයේ තබා ගෙන සිටියදි උයිරංකුලම පොලිස් වසම දි අත් අඩංගුවට ගෙන ඇත.
"""

def test_extraction():
    """Test the extraction tool"""
    print("=" * 80)
    print("Testing Complete Data Extraction Tool")
    print("=" * 80)
    print()
    
    # Create extractor
    extractor = SinhalaPoliceReportExtractor()
    
    # Test header extraction
    print("1. Testing Header Extraction:")
    print("-" * 80)
    header = extractor.extract_header(sample_text)
    print(json.dumps(header, ensure_ascii=False, indent=2))
    print()
    
    # Test category extraction
    print("2. Testing Category 01 (Terrorism):")
    print("-" * 80)
    cat01 = extractor.extract_category_data(sample_text, "01")
    print(json.dumps(cat01, ensure_ascii=False, indent=2))
    print()
    
    print("3. Testing Category 02 (Weapons):")
    print("-" * 80)
    cat02 = extractor.extract_category_data(sample_text, "02")
    print(json.dumps(cat02, ensure_ascii=False, indent=2))
    print()
    
    # Test full extraction
    print("4. Testing Full Extraction:")
    print("-" * 80)
    full_data = extractor.extract_all(sample_text)
    
    # Save to file
    extractor.save_to_json(full_data, "test_output.json")
    print("✓ Saved to test_output.json")
    
    # Generate summary
    summary = extractor.generate_summary(full_data)
    with open("test_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    print("✓ Saved summary to test_summary.txt")
    print()
    
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_extraction()
