"""
Complete Workflow Demo: PDF Text → JSON → PDF Report
=====================================================

This demonstrates the complete workflow:
1. Extract data from PDF text
2. Save to JSON
3. Generate formatted PDF report
"""

from complete_data_extraction_tool import SinhalaPoliceReportExtractor
from generate_pdf_from_extraction import PDFReportGenerator
import json

# Sample data from your March 22 report
SAMPLE_REPORT = """
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

03. උද්ඝෝෂණ :- 01

1. යාපනය
   OTM 1804
   කොට්ඨාශය යාපනය
   2026.02.22 පැය 1015 සිට 1105 දක්වා
   
   යාපනය අන්නචන්ද්‍ර දු රිය ශරවහ මාර්ගය ඉදිරිපිට දී
   
   යාපනය අන්නචන්ද්‍ර දු රිය ශරවහ මාර්ගය වසා දීමමට ගෙන ඇති තීන්දුවට විරෝධය පළ කරමින් ශා එම ස්ථානයේ ආරක්ෂිත සේට්ටුවක් සවි කර නැවත මාර්ගය විවෘත කරන සේවට ඉල්ලා ප්‍රදේශවාසීන් 70 කසේ සහභාගිත්වයෙන් උද්ඝෝෂණයක් පවත්වා ඇත.

04. මිනීමැරීම :- 01

1. කොක්ගඩි සචෝරය
   CTM 682
   කොට්ඨාශය මඩකල්පුව
   2026.02.28 පැය 1200-1600 අතර
   ST 2026.03.22
   IR 2026.03.23 පැය 0335
   
   කොක්ගඩි සචෝරය, නෙල්වි඗ාඩු ප්‍රදේශයේ දී
   
   ආර්. නරායිනී
   අවු : 46
   ස්ත්‍රී
   රැකියාව : නැත
   40 ග්‍රාමය, ව මියඩි උත්තු, තික්සේොඩය
   
   මෙම මරණකාරිය 2026.02.28 වන දින රෝගී තත්වයක් සදහා ප්‍රථිකාර ලැබා ගැනීමට පවුගාම ප්‍රදේශයේ පිහිටි රෝශලරකට ගොවහ ප්‍රදේශයේ ගෘංකුවකින් මුදල්ද ලැබාගෙන නිවස ගෙරා යාම සදහා මාර්ගය ආවන්නයේ සිටිය දී මෙහි පෂමු සැකකරුවන් දෙදෙනා ශා සැකකාරිය ත්‍රීරෝද රථයකින් එම ස්ථානයට පැමිණ ඔවුන් වෙල්රාවලි ප්‍රදේශයට යන ගවට මරණකාරියට දෆනු දී ඇත.
"""

def main():
    """Run complete workflow demo"""
    print("=" * 80)
    print("Complete Workflow Demo")
    print("PDF Text → JSON Extraction → PDF Report")
    print("=" * 80)
    print()
    
    # Step 1: Extract data from text
    print("Step 1: Extracting data from report text...")
    print("-" * 80)
    
    extractor = SinhalaPoliceReportExtractor()
    data = extractor.extract_all(SAMPLE_REPORT)
    
    print(f"✓ Extracted header information")
    print(f"✓ Processed {len(data['categories'])} categories")
    print(f"✓ Found {data['metadata']['categories_with_incidents']} categories with incidents")
    print()
    
    # Step 2: Save to JSON
    print("Step 2: Saving extracted data to JSON...")
    print("-" * 80)
    
    json_file = "demo_extracted_data.json"
    extractor.save_to_json(data, json_file)
    print(f"✓ Saved to {json_file}")
    print()
    
    # Step 3: Generate text summary
    print("Step 3: Generating text summary...")
    print("-" * 80)
    
    summary = extractor.generate_summary(data)
    summary_file = "demo_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"✓ Saved to {summary_file}")
    print()
    
    # Step 4: Generate PDF report
    print("Step 4: Generating PDF report...")
    print("-" * 80)
    
    pdf_file = "demo_report.pdf"
    generator = PDFReportGenerator()
    generator.generate_pdf(json_file, pdf_file)
    print()
    
    # Step 5: Show statistics
    print("Step 5: Statistics")
    print("-" * 80)
    
    total_incidents = sum(cat['summary']['total_incidents'] 
                         for cat in data['categories'].values())
    
    print(f"Total incidents: {total_incidents}")
    print(f"Categories with data: {data['metadata']['categories_with_incidents']}")
    print(f"Categories marked 'නැත': {sum(1 for cat in data['categories'].values() if cat.get('status') == 'නැත')}")
    print()
    
    # Show category breakdown
    print("Category Breakdown:")
    print("-" * 80)
    for cat_num, cat_data in sorted(data['categories'].items()):
        cat_name = cat_data['category_name']
        total = cat_data['summary']['total_incidents']
        status = cat_data.get('status', '')
        
        if status == 'නැත':
            print(f"{cat_num}. {cat_name}: නැත")
        elif total > 0:
            print(f"{cat_num}. {cat_name}: {total} සිදුවීම්")
    
    print()
    print("=" * 80)
    print("Workflow Complete!")
    print("=" * 80)
    print()
    print("Generated Files:")
    print(f"  1. {json_file} - Structured JSON data")
    print(f"  2. {summary_file} - Text summary")
    print(f"  3. {pdf_file} - Formatted PDF report")
    print()
    print("You can now:")
    print("  - View the JSON data in any text editor")
    print("  - Read the summary in demo_summary.txt")
    print("  - Open the PDF report in any PDF viewer")
    print()


if __name__ == "__main__":
    main()
