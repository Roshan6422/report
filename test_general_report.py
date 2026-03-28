"""
Test script for General Situation Report Generator
Tests the pixel-perfect formatting with sample data
"""

from general_report_engine import generate_general_report, html_to_pdf

# Sample data matching the official General Report format
sample_data = {
    "date_range": "From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026",
    "sections": [
        {
            "title": "01. SERIOUS CRIMES COMMITTED:",
            "provinces": [
                {
                    "name": "WESTERN",
                    "incidents": [
                        {
                            "station": "KALUTARA SOUTH",
                            "summary": "A case of a theft",
                            "body": "A case of a theft of Rs. 40,000/= and gold jewellery (6 ½ sovereigns) valued Rs. 3,440,000/= was reported to the police station. The offence took place between 1800 hrs on 15th of March 2026 and 1500 hrs on 16th of March 2026 at #08, Central Garden, Pragathi Mawatha, Kalutara south. Complainant named S. S. Malar, (TP 076-9386812). Suspect identified as P. Madushanka and yet to be arrested. The stolen property not recovered and investigations in process. Motive: For illegal gain.",
                            "hierarchy": ["DIG Kalutara District", "Kalutara Div."],
                            "ctm": "CTM.521"
                        }
                    ]
                },
                {
                    "name": "SABARAGAMUWA",
                    "incidents": []
                },
                {
                    "name": "SOUTHERN",
                    "incidents": [
                        {
                            "station": "SOORIYAWEWA",
                            "summary": "A case of a homicide by assaulting with a club",
                            "body": "A case of a homicide by assaulting with a club was reported to the police station. The offence took place on the 16th of March 2026 around 2100 hrs at #10, Usgala, Andarawewa, Sooriyawewa. Deceased: E. R. Kumara, aged 40, (male). Suspect identified as K. S. Alwis and yet to be arrested. Investigations are being conducted.",
                            "hierarchy": ["DIG Hambantota District", "Tangalle Div."],
                            "otm": "OTM.1400"
                        }
                    ]
                }
            ]
        },
        {
            "title": "02. RAPE, SEXUAL ASSAULT & CHILD ABUSE:",
            "provinces": []
        },
        {
            "title": "03. FATAL ACCIDENTS:",
            "provinces": []
        },
        {
            "title": "04. POLICE OFFICERS/VEHICLES INVOLVED IN ROAD ACCIDENTS AND DAMAGES TO SRI LANKA POLICE PROPERTY:",
            "provinces": []
        },
        {
            "title": "05. FINDING OF DEAD BODIES UNDER SUSPICIOUS CIRCUMSTANCES:",
            "provinces": []
        },
        {
            "title": "06. SERIOUS INJURY/ ILLNESSES/ DEATHS OF POLICE OFFICERS:",
            "provinces": []
        },
        {
            "title": "07. DETECT OF NARCOTIC AND ILLEGAL LIQUOR:",
            "provinces": []
        },
        {
            "title": "08. ARREST OF TRI-FORCES MEMBERS:",
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
        },
        {
            "title": "09. OTHER MATTERS:",
            "provinces": []
        },
        {
            "title": "10. [RESERVED]:",
            "provinces": []
        }
    ]
}

if __name__ == "__main__":
    print("=" * 70)
    print("Testing General Situation Report Generator")
    print("=" * 70)
    
    html_path = "Test_General_Report.html"
    pdf_path = "Test_General_Report.pdf"
    
    print("\n1. Generating HTML report...")
    generate_general_report(sample_data, html_path)
    
    print("\n2. Converting to PDF...")
    html_to_pdf(html_path, pdf_path)
    
    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)
    print(f"\nGenerated files:")
    print(f"  - {html_path}")
    print(f"  - {pdf_path}")
    print("\nOpen the HTML file in a browser to verify formatting.")
    print("Compare with the official sample to ensure 100% match.")
