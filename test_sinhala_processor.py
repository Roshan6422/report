"""
Test the Sinhala Data Processor with a sample incident
"""

from sinhala_data_processor import SinhalaDataProcessor

# Create processor
processor = SinhalaDataProcessor()

# Test with the CHUNNAKAM incident from your PDF
test_incident = """
චුන්නාකම් පොලිස් ස්ථානයට රන් ආභරණ (ස්වර්ණ 05) රු. 1,975,000/= වටිනා 
සොරකම් සිද්ධියක් වාර්තා විය. මෙම වරද 2026 මාර්තු 17 වන දින 0430 සිට 
0500 පැය අතර #18/48, ඉඳුවිල් බටහිර, ඉඳුවිල්, චුන්නාකම් හිදී සිදුවී ඇත. 
පැමිණිලිකරු නම S. Sarwalogeshwari, (දු.අ. 077-5692523). සැකකරු: නොදනී. 
සොරකම් කළ ආභරණ සොයා ගෙන නොමැති අතර පරීක්ෂණ ක්‍රියාත්මක වේ. 
චේතනාව: නීති විරෝධී ලාභය සඳහා. (CTM.524)
"""

print("Testing Sinhala Data Processor...")
print("="*80)

# Process the incident
result = processor.add_incident(test_incident)

if result["success"]:
    print("\n✅ SUCCESS! Incident processed correctly")
    print("\nExtracted Data:")
    print(f"  Station: {result['data'].get('station')}")
    print(f"  Type: {result['data'].get('incident_type')}")
    print(f"  Category: {result['category'].upper()} REPORT")
    print(f"  Province: {result['data'].get('province')}")
    print(f"  Reference: {result['data'].get('reference')}")
    
    print("\n📝 Generated Narrative:")
    print("-"*80)
    print(result['data'].get('body', 'N/A'))
    print("-"*80)
    
    # Show summary
    processor.print_summary()
    
    print("\n✅ Tool is working correctly!")
    print("\nNow you can:")
    print("1. Run: python sinhala_data_processor.py interactive")
    print("2. Paste your Sinhala incidents one by one")
    print("3. Type 'done' when finished")
    print("4. Get both Security and General reports automatically!")
    
else:
    print(f"\n❌ Error: {result.get('error')}")
    print("\nPlease check your API configuration.")
