"""
Test Security Report Format - Verify exact format matching
"""
import json
from web_report_engine import generate_html_report

# Sample data matching your PDF structure
test_data = {
    "report_type": "Security",
    "date_range": "From 0400 hrs. on 17<sup>th</sup> March 2026 to 0400 hrs. on 18<sup>th</sup> March 2026",
    "sections": [
        {
            "title": "01. VERY IMPORTANT MATTERS OF SECURITY INTEREST:",
            "provinces": []
        },
        {
            "title": "02. SUBVERSIVE ACTIVITIES:",
            "provinces": []
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
                            "otm": "OTM.1421-A"
                        },
                        {
                            "station": "UDAWALAWA",
                            "summary": "Arrest of a person for possession of a firearm",
                            "body": "On the 17th of March 2026, police arrested a person named K.T. Ranathunga, aged 53 of # 472 Panahaduwa, Kolombage-Ara for possession of a locally made muzzle loading firearm at Panahaduwa in Udawalawa area. Investigations are being conducted.",
                            "hierarchy": ["DIG Ratnapura District", "Embilipitiya Div."],
                            "otm": "OTM.1445-E"
                        }
                    ]
                },
                {
                    "name": "NORTHERN",
                    "incidents": [
                        {
                            "station": "ADAMPAN",
                            "summary": "Arrest of suspects along with two detonators",
                            "body": "On the 17th of March 2026, officers of the Navy attached to the Wedithalathivu camp arrested the following persons while sailing in a boat in the sea of Wedithalathivu area with the possession of 2 non-electric detonators. (1) A.R.J. Patric, aged 27 (2) A.F. Perera, aged 44 (3) R. Jonindan, aged 44 and (4) A.S. Pihiravo, aged 32 of Pallimune-East, Mannar. Investigations are being conducted.",
                            "hierarchy": ["DIG Wanni District", "Mannar Div."],
                            "ctm": "CTM.530-M"
                        }
                    ]
                }
            ]
        }
    ]
}

# Generate HTML
print("Generating Security Report HTML...")
html_path = "test_security_format.html"
generate_html_report(test_data, html_path, report_type="Security")

print(f"\n✅ HTML generated: {html_path}")
print("\nOpen the HTML file to verify:")
print("1. Station names should be: EMBILIPITIYA:, UDAWALAWA:, ADAMPAN:")
print("2. NO extra text like 'Div, S/DIG PROVINCE' should appear")
print("3. Left column should show: DIG District, Division")
print("4. Right column should show: STATION: (Title) Body (REF)")
