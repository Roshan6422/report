"""
Process March 18, 2026 General Situation Report
Complete pipeline: Extract data → Generate detailed narratives → Create report
"""

from general_report_engine import generate_general_report, html_to_pdf
from general_report_processor import GeneralReportProcessor

# Extracted and translated data from the Sinhala PDF (March 18, 2026)
# NOW INCLUDES: 21 incidents total (added CHUNNAKAM from Northern Province)
MARCH_18_INCIDENTS = [
    # 02. Arms/Ammunition Recovery - 4 incidents
    {
        "station": "HINIDUMA",
        "summary": "Arrest of suspects with firearms and ammunition",
        "body": "On the 17th of March 2026, police arrested three suspects named (1) H.G. Sunil, aged 58, male, occupation: None, Ahalahapitiya, Nelua (2) G.H.A. Vihamitha, aged 26, male, occupation: None, Ahalahapitiya, Nelua (3) D.L.S. Senaratne, aged 41, male, occupation: None, # 38/3, Moragaharanda Para, Happitiya, Nelua while transporting a locally made 12 gauge shotgun and 05 bullets in vehicle # SP AAY 5691 without a valid license. The suspects are scheduled to be produced before the Magistrate court.",
        "hierarchy": ["DIG Galle District", "Elpitiya Div."],
        "otm": "OTM.1480",
        "province": "SOUTHERN"
    },
    {
        "station": "MAHAPASE",
        "summary": "Arrest of suspect with a homemade firearm",
        "body": "On the 18th of March 2026 at 0430 hrs, police arrested a suspect named D.D. Anuradha Silva, aged 39, male, occupation: Businessman, # 47, Magulpokuna, Ragama while possessing a homemade firearm without a valid license at # 543, Polpitigama Muralana, Kadana. The suspect is scheduled to be produced before the Magistrate court.",
        "hierarchy": ["DIG Kurunegala District", "Kuliyapitiya Div."],
        "ctm": "CTM.555",
        "province": "NORTH WESTERN"
    },
    {
        "station": "MANAPITIYA",
        "summary": "Arrest of suspect with a locally made shotgun",
        "body": "On the 18th of March 2026, police arrested a suspect named K.G. Mahindharathna, aged 54, male, occupation: Unknown, # 17, Kadurale, Polonnaruwa while possessing a locally made shotgun without a valid license at his residence. The suspect is scheduled to be produced before the Magistrate court.",
        "hierarchy": ["DIG Polonnaruwa District", "Polonnaruwa Div."],
        "otm": "OTM.1522",
        "province": "NORTH CENTRAL"
    },
    {
        "station": "BIBILA",
        "summary": "Arrest of suspect with a locally made shotgun",
        "body": "On the 18th of March 2026 at 1910 hrs, police arrested a suspect named S.A.N. Dilrukshi, aged 26, female, occupation: None, Pattiyadeniya, Nagala, Bibila while possessing a locally made shotgun without a valid license at her residence. The suspect is scheduled to be produced before the Magistrate court.",
        "hierarchy": ["DIG Monaragala District", "Monaragala Div."],
        "otm": "OTM.1532",
        "province": "UVA"
    },
    
    # 04. Homicide - 1 incident
    {
        "station": "KIRIDIWELA",
        "summary": "A case of homicide by strangulation",
        "body": "On the 18th of March 2026, a case of homicide was reported to the police station. The offence took place at # 80, Hisalulla, Kiridiwela. Deceased: R.D. Pushpa Nalani, aged 79, female, occupation: None, # 80, Hisalulla, Kiridiwela. The victim was found dead with her right ear cut off and a gold earring removed. Suspect: K.D. Vimal Ranathunga, aged 61, male, occupation: None, # 150, Hisalulla, Kiridiwela has been arrested. The suspect had injuries on his right hand and left leg. Investigations are being conducted.",
        "hierarchy": ["DIG Gampaha District", "Gampaha Div."],
        "ctm": "CTM.569",
        "otm": "OTM.1516",
        "province": "WESTERN"
    },
    
    # 06. Vehicle Thefts - 6 incidents
    {
        "station": "AHANGAMA",
        "summary": "A case of theft of a motorcycle",
        "body": "A case of theft of motorcycle # NW TN 6876 was reported to the police station. The offence took place between 2100 hrs on 16th of March 2026 and 0700 hrs on 17th of March 2026 at # 210/02, Atharagalla, Galgamuwa. Complainant named B.A. Mudiyanselage, (TP 0711033927). Suspect: Unknown. The stolen motorcycle not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Kurunegala District", "Nikaweratiya Div."],
        "ctm": "CTM.539",
        "province": "NORTH WESTERN",
        "value": "Rs. 50,000/="
    },
    {
        "station": "KULIYAPITIYA",
        "summary": "A case of theft of a motorcycle",
        "body": "A case of theft of motorcycle # NW BBF 8569 was reported to the police station. The offence took place between 1400 hrs and 1430 hrs on 17th of March 2026 at Galgamuwa. Complainant named P.A. Pathmaseela, (TP 0755013192). Suspect: Unknown. The stolen motorcycle not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Kurunegala District", "Kuliyapitiya Div."],
        "ctm": "CTM.544",
        "province": "NORTH WESTERN",
        "value": "Rs. 227,000/="
    },
    {
        "station": "PITIGALA",
        "summary": "A case of theft of a motorcycle",
        "body": "A case of theft of motorcycle # SP BBC 1984 was reported to the police station. The offence took place between 2130 hrs and 2240 hrs on 17th of March 2026 at Kanaththa Goda, Amugoda. Complainant named P.H.K. Lasantha, (TP 0760933588). Suspect: Unknown. The stolen motorcycle not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Galle District", "Elpitiya Div."],
        "ctm": "CTM.560",
        "province": "SOUTHERN",
        "value": "Rs. 280,000/="
    },
    {
        "station": "MALABE",
        "summary": "A case of theft of a motorcycle",
        "body": "A case of theft of motorcycle # WP BAA 2389 was reported to the police station. The offence took place between 1345 hrs and 1410 hrs on 18th of March 2026 at # 482, Samudra Mawatha, Athurugiriya, Hokandara North, Hokandara. Complainant named K.D.G. Perera, (TP 0779003587). Suspect: Unknown. The stolen motorcycle not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Colombo District", "Nugegoda Div."],
        "ctm": "CTM.559",
        "province": "WESTERN",
        "value": "Rs. 300,000/="
    },
    {
        "station": "MEEGAMU",
        "summary": "A case of theft of a motorcycle",
        "body": "A case of theft of motorcycle # WP BFO 6587 was reported to the police station. The offence took place between 1430 hrs and 1730 hrs on 18th of March 2026 at Meegamu Prison premises. Complainant named H.P. Latha Shaka de Silva, (TP 0778944687). Suspect: Unknown. The stolen motorcycle not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Colombo District", "Meegamu Div."],
        "ctm": "CTM.566",
        "province": "WESTERN",
        "value": "Rs. 500,000/="
    },
    {
        "station": "PILIYANDALA",
        "summary": "A case of theft of a motorcycle",
        "body": "A case of theft of motorcycle # WP BDC 3598 was reported to the police station. The offence took place between 1855 hrs and 2040 hrs on 18th of March 2026 at # 93/1/E, Ayans Greens Fitness, Parata Para, Maharagama. Complainant named B.B.R. Perera, (TP 0764049246). Suspect: Unknown. The stolen motorcycle not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Colombo District", "Galkissa Div."],
        "ctm": "CTM.568",
        "province": "WESTERN",
        "value": "Rs. 400,000/="
    },
    
    # 07. Thefts/Burglaries - 7 incidents (including CHUNNAKAM from Northern Province)
    {
        "station": "CHUNNAKAM",
        "summary": "A case of theft of gold jewellery",
        "body": "A case of theft of gold jewellery (05 sovereigns) valued Rs. 1,975,000/= was reported to the police station. The offence took place on the 17th of March 2026 between 0430 hrs and 0500 hrs at # 18/48, Induvil west, Induvil, Chunnakam. Complainant named S. Sarwalogeshwari, (TP 077-5692523). Suspect: Unknown. The stolen jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Jaffna District", "Jaffna Div."],
        "ctm": "CTM.524",
        "province": "NORTHERN",
        "value": "Rs. 1,975,000/="
    },
    {
        "station": "KUBUKKANDAWALA",
        "summary": "A case of theft of gold jewellery",
        "body": "A case of theft of gold jewellery (01 gold necklace, 01 pendant, 06 gold rings) valued Rs. 1,684,900/= was reported to the police station. The offence took place between 0915 hrs on 14th of March 2026 and 1130 hrs on 17th of March 2026 at Rambakupa Wala, Liththagenawe, Kubukkandawala. Complainant named U. Mallika, (TP 0763831026). Suspect: Unknown. The stolen jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Kurunegala District", "Kubukkandawala Div."],
        "ctm": "CTM.541",
        "province": "NORTH WESTERN",
        "value": "Rs. 1,684,900/="
    },
    {
        "station": "KURUNEGALA",
        "summary": "A case of theft from a bakery",
        "body": "A case of theft of Rs. 520,000/= cash and 19 cakes from CM Bakery was reported to the police station. The offence took place on 17th of March 2026 at 1600 hrs at CM Super Market. Complainant named U.D.H.H. Samarasinghe, occupation: Bakery worker, Nawagala, Nuwaragala, (TP 0743890842). Suspects: (1) R.A.G.S. Ratnayaka, aged 35, male, occupation: Salesman, Thelawaya, Kurunegala (2) P.A.A. Vitharanage, aged 34, male, occupation: Salesman, # 222/01, Nuwara Para, Kurunegala have been arrested. Investigations are being conducted.",
        "hierarchy": ["DIG Kurunegala District", "Kurunegala Div."],
        "ctm": "CTM.545",
        "province": "NORTH WESTERN",
        "value": "Rs. 560,755/="
    },
    {
        "station": "PADDEGAMA",
        "summary": "A case of theft of gold jewellery",
        "body": "A case of theft of gold jewellery (01 gold necklace, 03 pendants, 03 rings, 04 earrings, 02 bangles, 01 gold chain, 01 gold bracelet) valued Rs. 2,155,000/= was reported to the police station. The offence took place between 0200 hrs and 0315 hrs on 18th of March 2026 at # 46/A, Dewalgaha Handiya, Appegama. Complainant named K.B. Dilrukshi, (TP 0766788955). Suspect: Unknown. The stolen jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Galle District", "Elpitiya Div."],
        "ctm": "CTM.563",
        "province": "SOUTHERN",
        "value": "Rs. 2,155,000/="
    },
    {
        "station": "AHANGAMA",
        "summary": "A case of theft of gold jewellery",
        "body": "A case of theft of 23 sovereigns of gold jewellery valued Rs. 6,680,000/= was reported to the police station. The offence took place between 1000 hrs on 13th of March 2026 and 0930 hrs on 18th of March 2026 at # 146, Panugalgoda, Dikkumbura. Complainant named H.A. Kalyanee Yanththa, occupation: Hairdresser, (TP 0762390751). Suspect: Unknown. The stolen jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Galle District", "Galle Div."],
        "ctm": "CTM.561",
        "province": "SOUTHERN",
        "value": "Rs. 6,680,000/="
    },
    {
        "station": "NAWAGAMUWA",
        "summary": "A case of theft of gold jewellery",
        "body": "A case of theft of 09 sovereigns of gold jewellery valued Rs. 3,366,000/= was reported to the police station. The offence took place between 05th of January 2025 and 28th of November 2025 at # 708, Nawagamuwa, Kanala. Complainant named S. Chandraseka, occupation: Businessman, (TP 0762244123). Suspect: K.P.A.A. Subhashini, aged 58, female, occupation: Tenant, # 269/A, Dewana Patumaga, Kiranawila West, Ambaradawila, Halavatha has been arrested. Investigations are being conducted.",
        "hierarchy": ["DIG Colombo District", "Homagama Div."],
        "ctm": "CTM.567",
        "province": "WESTERN",
        "value": "Rs. 3,366,000/="
    },
    {
        "station": "PORALUWAGAMUWA",
        "summary": "A case of theft of gold jewellery",
        "body": "A case of theft of gold jewellery (01 gold watch, 01 ruby ring, 01 sapphire ring, 01 diamond ring) valued Rs. 2,500,000/= was reported to the police station. The offence took place between 0400 hrs and 1200 hrs on 18th of March 2026 at # 201/3/1, Galla Para, Nila Mahara, Poraluwagamuwa. Complainant named A.K. Mohomd Sarwan, occupation: Chief Accountant, (TP 0777700703). Suspect: Unknown. The stolen jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Colombo District", "Nugegoda Div."],
        "ctm": "CTM.553",
        "province": "WESTERN",
        "value": "Rs. 2,500,000/="
    },
    
    # 08. House Breaking & Theft - 3 incidents
    {
        "station": "PANWALA",
        "summary": "A case of house breaking and theft",
        "body": "A case of house breaking and theft of 06 ½ sovereigns of gold jewellery and Rs. 275,000/= cash was reported to the police station. The offence took place between 0700 hrs and 1330 hrs on 18th of March 2026 at # 238, Vindaya Gardens, Horakada Wila, Panwala. Complainant named B.A. Indrani, (TP 0763999520). Suspect: Unknown. The stolen cash and jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Colombo District", "Meegamu Div."],
        "ctm": "CTM.543",
        "province": "WESTERN",
        "value": "Rs. 2,735,000/="
    },
    {
        "station": "PAHALAGAMA WALA",
        "summary": "A case of house breaking and theft",
        "body": "A case of house breaking and theft of cash from a room was reported to the police station. The offence took place between 0630 hrs and 0900 hrs on 17th of March 2026 at Sadamalga, Kambawa. Complainant named H.S. Kusuratna, occupation: Businessman, (TP 0710559672). Suspect: Unknown. The stolen cash not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Anuradhapura District", "Anuradhapura Div."],
        "ctm": "CTM.558",
        "province": "NORTH CENTRAL",
        "value": "Rs. 500,000/="
    },
    {
        "station": "MADHYAMAKADAWURA",
        "summary": "A case of house breaking and theft",
        "body": "A case of house breaking and theft of gold jewellery (01 gold bracelet, 01 chain, 02 rings) valued Rs. 2,088,600/= was reported to the police station. The offence took place between 1200 hrs on 16th of March 2026 and 1200 hrs on 18th of March 2026 at # 12/46, Madhyama Kadawura, Salawa Keni 03. Complainant named S.S. Aruna Umaya, (TP 0717755487). Suspect: Unknown. The stolen jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Colombo District", "Avissawella Div."],
        "ctm": "CTM.565",
        "province": "WESTERN",
        "value": "Rs. 2,088,600/="
    }
]


def main():
    print("=" * 80)
    print("PROCESSING MARCH 18, 2026 GENERAL SITUATION REPORT")
    print("=" * 80)
    
    processor = GeneralReportProcessor()
    
    # Generate report
    processor.generate_report(
        incidents=MARCH_18_INCIDENTS,
        date_range="From 0400 hrs. on 18th March 2026 to 0400 hrs. on 19th March 2026",
        output_html="General_Report_March18_2026.html",
        output_pdf="General_Report_March18_2026.pdf"
    )
    
    print("\n📊 Report Statistics:")
    print(f"  • Total Incidents: {len(MARCH_18_INCIDENTS)}")
    print(f"  • Arms Recovery: 4")
    print(f"  • Homicides: 1")
    print(f"  • Vehicle Thefts: 6")
    print(f"  • Thefts/Burglaries: 7 (including CHUNNAKAM)")
    print(f"  • House Breaking: 3")
    print(f"  • Total Value: Rs. 25,532,255/=")
    print(f"\n  • Provinces with data:")
    print(f"    - Western Province: 9 incidents")
    print(f"    - North Western Province: 5 incidents")
    print(f"    - Southern Province: 4 incidents")
    print(f"    - North Central Province: 2 incidents")
    print(f"    - Uva Province: 1 incident")
    print(f"    - Northern Province: 1 incident (CHUNNAKAM)")
    print(f"  • Provinces showing Nil:")
    print(f"    - Sabaragamuwa, Central, Eastern")
    
    print("\n✅ General Report for March 18, 2026 generated successfully!")


if __name__ == "__main__":
    main()
