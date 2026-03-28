"""
Verify the fix for station name format in Security Reports
"""
from web_report_engine import generate_html_report
import re

# Test data with the problematic station name format
test_data = {
    "report_type": "Security",
    "date_range": "From 0400 hrs. on 17<sup>th</sup> March 2026 to 0400 hrs. on 18<sup>th</sup> March 2026",
    "sections": [
        {
            "title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:",
            "provinces": [
                {
                    "name": "SABARAGAMUWA",
                    "incidents": [
                        {
                            # THIS IS THE PROBLEMATIC FORMAT - with extra text
                            "station": "Div, S/DIG SABARAGAMUWA PROVINCE, EMBILIPITIYA",
                            "summary": "Arrest of suspects along with a detonator and gunpowder",
                            "body": "On the 17th March 2026, acting on an information received through the 1-1-9 project, police arrested a Buddhist monk named Rev. Embilipitiye Indrarathana thero, aged 68, the chief incumbent of the Sri Darshanagiri viharaya, Darshanagama, Embilipitiya and another person named N.U. Samanchandra, aged 56 of # 896, Mayuragama, Sewanagala along with an electric detonator and 80g of gunpowder, while digging a tunnel with the intention of treasure hunting in the temple premises. The suspects are scheduled to be produced before the Magistrate court, Embilipitiya on the 18th March 2026.",
                            "hierarchy": ["DIG Ratnapura District", "Embilipitiya Div."],
                            "otm": "OTM.1421-A"
                        }
                    ]
                }
            ]
        }
    ]
}

print("=" * 80)
print("TESTING FIX FOR STATION NAME FORMAT")
print("=" * 80)
print("\nInput station name: 'Div, S/DIG SABARAGAMUWA PROVINCE, EMBILIPITIYA'")
print("Expected output:    'EMBILIPITIYA:'")
print("\nGenerating HTML report...")

html_path = "test_fix_verification.html"
generate_html_report(test_data, html_path, report_type="Security")

# Read and check the generated HTML
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Check if the problematic text exists
if "Div, S/DIG SABARAGAMUWA PROVINCE" in html_content:
    print("\n❌ FAILED: Extra text still present in HTML!")
    print("   Found: 'Div, S/DIG SABARAGAMUWA PROVINCE' in the output")
else:
    print("\n✅ SUCCESS: Extra text removed!")

# Extract the station name from HTML
match = re.search(r'<span class="station-name">([^<]+)</span>', html_content)
if match:
    station_in_html = match.group(1)
    print(f"\n   Station name in HTML: '{station_in_html}'")
    
    if station_in_html == "EMBILIPITIYA:":
        print("   ✅ Format is CORRECT!")
    else:
        print(f"   ❌ Format is WRONG! Expected 'EMBILIPITIYA:' but got '{station_in_html}'")
else:
    print("\n❌ Could not find station name in HTML")

print(f"\n📄 Check the generated file: {html_path}")
print("=" * 80)
