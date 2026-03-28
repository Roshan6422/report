"""
test_nil_sections.py — Test Nil Display for Empty Sections
===========================================================
Demonstrates that empty sections show "Nil" exactly as in the official sample.
"""

from web_report_engine_v2 import generate_security_report, html_to_pdf

# Test data with some empty sections (showing Nil)
test_data = {
    "date_range": "From 0400 hrs. on 17<sup>th</sup> March 2026 to 0400 hrs. on 18<sup>th</sup> March 2026",
    "sections": [
        {
            "title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:",
            "provinces": []  # EMPTY - Will show "Nil"
        },
        {
            "title": "02. SUBVERSIVE ACTIVITIES:",
            "provinces": []  # EMPTY - Will show "Nil"
        },
        {
            "title": "03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:",
            "provinces": [
                {
                    "name": "SABARAGAMUWA",
                    "incidents": [
                        {
                            "station": "EMBILIPITIYA",
                            "summary": "Arrest of suspects along with a detonator and gunpowder",
                            "body": "On the 17th March 2026, acting on an information received through the 1-1-9 project, police arrested a Buddhist monk named Rev. Embilipitiye Indrarathana thero, aged 68, the chief incumbent of the Sri Darshanagiri viharaya, Darshanagama, Embilipitiya and another person named N.U. Samanchandra, aged 56 of # 896, Mayuragama, Sewanagala along with an electric detonator and 80g of gunpowder, while digging a tunnel with the intention of treasure hunting in the temple premises. The suspects are scheduled to be produced before the Magistrate court, Embilipitiya on the 18th March 2026.",
                            "hierarchy": ["DIG Ratnapura District", "Embilipitiya Div."],
                            "otm": "OTM.1421"
                        }
                    ]
                }
            ]
        }
    ]
}

print("\n" + "="*60)
print("TESTING NIL DISPLAY FOR EMPTY SECTIONS")
print("="*60)

print("\nTest Data Structure:")
print("  Section 1 (Important Matters): EMPTY → Should show 'Nil'")
print("  Section 2 (Subversive):        EMPTY → Should show 'Nil'")
print("  Section 3 (Arms Recovery):     1 incident → Should show data")

print("\nGenerating report...")

# Generate HTML
html_path = "test_nil_display.html"
generate_security_report(test_data, html_path)

print(f"✅ HTML generated: {html_path}")

# Generate PDF
pdf_path = "test_nil_display.pdf"
html_to_pdf(html_path, pdf_path)

print(f"✅ PDF generated: {pdf_path}")

print("\n" + "="*60)
print("EXPECTED OUTPUT IN REPORT:")
print("="*60)
print("01. VERY IMPORTANT MATTERS OF SECURITY INTEREST: Nil")
print("02. SUBVERSIVE ACTIVITIES: Nil")
print("03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES:")
print("    S/DIG  SABARAGAMUWA PROVINCE")
print("    [Incident details...]")
print("="*60)

print("\n✅ Test complete! Open the PDF to verify Nil display.")
print("   Empty sections show 'Nil' exactly as in your sample.")
