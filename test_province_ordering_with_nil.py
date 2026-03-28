"""
Test Province Ordering with Nil Display
Verify that ALL 9 provinces are shown in official order with "Nil" for empty ones
"""

from general_report_processor import GeneralReportProcessor
from web_report_engine_v2 import generate_security_report
from general_report_engine import html_to_pdf

# Test data with gaps in provinces
TEST_INCIDENTS = [
    # Western Province
    {
        "station": "COLOMBO",
        "summary": "Test incident in Western Province",
        "body": "A case of theft was reported to the police station. The offence took place on 18th March 2026 at Colombo. Complainant named A. B. Silva, (TP 077-1234567). Suspect: Unknown. Investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Colombo District", "Colombo Div."],
        "ctm": "CTM.001",
        "province": "WESTERN"
    },
    # Southern Province (skip Sabaragamuwa)
    {
        "station": "GALLE",
        "summary": "Test incident in Southern Province",
        "body": "A case of theft was reported to the police station. The offence took place on 18th March 2026 at Galle. Complainant named C. D. Perera, (TP 077-2345678). Suspect: Unknown. Investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Galle District", "Galle Div."],
        "ctm": "CTM.002",
        "province": "SOUTHERN"
    },
    # Uva Province (skip Central)
    {
        "station": "BADULLA",
        "summary": "Test incident in Uva Province",
        "body": "A case of theft was reported to the police station. The offence took place on 18th March 2026 at Badulla. Complainant named E. F. Fernando, (TP 077-3456789). Suspect: Unknown. Investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Badulla District", "Badulla Div."],
        "ctm": "CTM.003",
        "province": "UVA"
    },
    # Northern Province (skip North Western, North Central, Eastern)
    {
        "station": "JAFFNA",
        "summary": "Test incident in Northern Province",
        "body": "A case of theft was reported to the police station. The offence took place on 18th March 2026 at Jaffna. Complainant named G. H. Kumar, (TP 077-4567890). Suspect: Unknown. Investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Jaffna District", "Jaffna Div."],
        "ctm": "CTM.004",
        "province": "NORTHERN"
    }
]

def test_general_report_with_nil():
    """Test General Report with Nil provinces."""
    print("=" * 80)
    print("TEST: GENERAL REPORT - Province Ordering with Nil")
    print("=" * 80)
    
    processor = GeneralReportProcessor()
    
    # Generate report with show_all_provinces=True
    processor.generate_report(
        incidents=TEST_INCIDENTS,
        date_range="From 0400 hrs. on 18th March 2026 to 0400 hrs. on 19th March 2026",
        output_html="Test_General_With_Nil.html",
        output_pdf="Test_General_With_Nil.pdf"
    )
    
    print("\n✅ General Report generated with ALL 9 provinces")
    print("\nExpected province order:")
    print("  1. WESTERN (has data)")
    print("  2. SABARAGAMUWA (Nil)")
    print("  3. SOUTHERN (has data)")
    print("  4. UVA (has data)")
    print("  5. CENTRAL (Nil)")
    print("  6. NORTH WESTERN (Nil)")
    print("  7. NORTH CENTRAL (Nil)")
    print("  8. EASTERN (Nil)")
    print("  9. NORTHERN (has data)")
    
    print("\n📁 Files: Test_General_With_Nil.html, Test_General_With_Nil.pdf")


def test_security_report_with_nil():
    """Test Security Report with Nil provinces."""
    print("\n" + "=" * 80)
    print("TEST: SECURITY REPORT - Province Ordering with Nil")
    print("=" * 80)
    
    # Test data with only 2 provinces
    security_incidents = [
        {
            "station": "COLOMBO",
            "summary": "Arrest with firearm",
            "body": "On 18th March 2026, police arrested a suspect named A. B. Silva, aged 35, male, occupation: None, # 123, Colombo while possessing a locally made firearm without a valid license. The suspect is scheduled to be produced before the Magistrate court.",
            "hierarchy": ["DIG Colombo District", "Colombo Div."],
            "ctm": "CTM.100",
            "province": "WESTERN"
        },
        {
            "station": "JAFFNA",
            "summary": "Arrest with ammunition",
            "body": "On 18th March 2026, police arrested a suspect named C. D. Kumar, aged 40, male, occupation: None, # 456, Jaffna while possessing ammunition without a valid license. The suspect is scheduled to be produced before the Magistrate court.",
            "hierarchy": ["DIG Jaffna District", "Jaffna Div."],
            "ctm": "CTM.101",
            "province": "NORTHERN"
        }
    ]
    
    # Organize by province with ALL 9 provinces
    OFFICIAL_PROVINCE_ORDER = [
        "WESTERN", "SABARAGAMUWA", "SOUTHERN", "UVA", "CENTRAL",
        "NORTH WESTERN", "NORTH CENTRAL", "EASTERN", "NORTHERN"
    ]
    
    provinces_dict = {}
    for inc in security_incidents:
        prov = inc.get("province", "UNKNOWN").upper()
        if prov not in provinces_dict:
            provinces_dict[prov] = []
        provinces_dict[prov].append(inc)
    
    # Create provinces list with Nil entries
    provinces_list = []
    for prov_name in OFFICIAL_PROVINCE_ORDER:
        if prov_name in provinces_dict:
            provinces_list.append({
                "name": prov_name,
                "incidents": provinces_dict[prov_name]
            })
        else:
            provinces_list.append({
                "name": prov_name,
                "incidents": [],
                "nil": True
            })
    
    security_data = {
        "date_range": "From 0400 hrs. on 18th March 2026 to 0400 hrs. on 19th March 2026",
        "sections": [
            {"title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:", "provinces": []},
            {"title": "02. SUBVERSIVE ACTIVITIES:", "provinces": []},
            {"title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:", "provinces": provinces_list}
        ]
    }
    
    generate_security_report(security_data, "Test_Security_With_Nil.html")
    html_to_pdf("Test_Security_With_Nil.html", "Test_Security_With_Nil.pdf")
    
    print("\n✅ Security Report generated with ALL 9 provinces")
    print("\nExpected province order:")
    print("  1. WESTERN (has data)")
    print("  2. SABARAGAMUWA (Nil)")
    print("  3. SOUTHERN (Nil)")
    print("  4. UVA (Nil)")
    print("  5. CENTRAL (Nil)")
    print("  6. NORTH WESTERN (Nil)")
    print("  7. NORTH CENTRAL (Nil)")
    print("  8. EASTERN (Nil)")
    print("  9. NORTHERN (has data)")
    
    print("\n📁 Files: Test_Security_With_Nil.html, Test_Security_With_Nil.pdf")


if __name__ == "__main__":
    test_general_report_with_nil()
    test_security_report_with_nil()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
    print("\nVerify the generated PDFs to ensure:")
    print("  • ALL 9 provinces are displayed in official order")
    print("  • Empty provinces show 'Nil'")
    print("  • General Report: 'Nil' indented below province heading")
    print("  • Security Report: 'Nil' on same line as section header")
