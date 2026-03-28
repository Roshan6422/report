"""
Script to extract data from the March 22, 2026 police report
"""

from complete_data_extraction_tool import SinhalaPoliceReportExtractor
import json

def main():
    """Extract data from March 22 report"""
    
    print("=" * 80)
    print("Extracting Data from March 22, 2026 Police Report")
    print("=" * 80)
    print()
    
    # The PDF text you provided
    pdf_text = """
දෛනික සිදුවීම් වාර්ථාව
2026.03.22 වන දින පැය 0400 සිට 2026.03.23 දින පැය 0400 දක්වා

01. ත්‍රස්තවාදී ක්‍රියාකාරකම : නැත.

02. අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ) :- 02

[Full PDF text would go here...]
"""
    
    # Create extractor
    extractor = SinhalaPoliceReportExtractor()
    
    # Extract all data
    print("Step 1: Extracting header information...")
    header = extractor.extract_header(pdf_text)
    print(f"✓ Report period: {header['report_period']}")
    print()
    
    print("Step 2: Extracting all 29 categories...")
    data = extractor.extract_all(pdf_text)
    print(f"✓ Total categories: {data['metadata']['total_categories']}")
    print(f"✓ Categories with incidents: {data['metadata']['categories_with_incidents']}")
    print()
    
    # Save JSON
    print("Step 3: Saving to JSON...")
    output_json = "march22_2026_extracted.json"
    extractor.save_to_json(data, output_json)
    print(f"✓ Saved to {output_json}")
    print()
    
    # Generate summary
    print("Step 4: Generating summary...")
    summary = extractor.generate_summary(data)
    output_summary = "march22_2026_summary.txt"
    with open(output_summary, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"✓ Saved to {output_summary}")
    print()
    
    # Print category breakdown
    print("Step 5: Category Breakdown:")
    print("-" * 80)
    
    for cat_num, cat_data in data['categories'].items():
        cat_name = cat_data['category_name']
        total = cat_data['summary']['total_incidents']
        status = cat_data.get('status', '')
        
        if status == 'නැත':
            print(f"{cat_num}. {cat_name}: නැත")
        elif total > 0:
            print(f"{cat_num}. {cat_name}: {total} සිදුවීම්")
            
            # Show first incident details if available
            if cat_data['incidents']:
                first_incident = cat_data['incidents'][0]
                if first_incident.get('police_station'):
                    print(f"    └─ Station: {first_incident['police_station']}")
                if first_incident.get('location'):
                    print(f"    └─ Location: {first_incident['location']}")
    
    print()
    print("=" * 80)
    print("Extraction Complete!")
    print("=" * 80)
    print()
    print("Output files:")
    print(f"  1. {output_json} - Full structured data")
    print(f"  2. {output_summary} - Human-readable summary")
    print()
    
    # Show statistics
    print("Statistics:")
    print(f"  - Total incidents: {sum(cat['summary']['total_incidents'] for cat in data['categories'].values())}")
    print(f"  - Categories with data: {data['metadata']['categories_with_incidents']}")
    print(f"  - Categories marked 'නැත': {sum(1 for cat in data['categories'].values() if cat.get('status') == 'නැත')}")
    print()

if __name__ == "__main__":
    main()
