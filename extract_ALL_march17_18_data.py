"""
Extract ALL incidents from March 17-18, 2026 Official PDFs
Security Report: 3 incidents
General Report: 71 incidents (from summary table)
"""

# ============================================================================
# SECURITY REPORT - March 17-18, 2026 (3 incidents)
# ============================================================================
SECURITY_MARCH17_18 = [
    # Category 03: RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES
    {
        "station": "EMBILIPITIYA",
        "summary": "Arrest of suspects along with a detonator and gunpowder",
        "body": "On the 17th March 2026, acting on an information received through the 1-1-9 project, police arrested a Buddhist monk named Rev. Embilipitiye Indrarathana thero, aged 68, the chief incumbent of the Sri Darshanagiri viharaya, Darshanagama, Embilipitiya and another person named N.U. Samanchandra, aged 56 of # 896, Mayuragama, Sewanagala along with an electric detonator and 80g of gunpowder, while digging a tunnel with the intention of treasure hunting in the temple premises. The suspects are scheduled to be produced before the Magistrate court, Embilipitiya on the 18th March 2026.",
        "hierarchy": ["DIG Ratnapura District", "Embilipitiya Div."],
        "otm": "OTM.1421",
        "province": "SABARAGAMUWA"
    },
    {
        "station": "UDAWALAWA",
        "summary": "Arrest of a person for possession of a firearm",
        "body": "On the 17th of March 2026, police arrested a person named K.T. Ranathunga, aged 53 of #14/2 Panahaduwa, Kolombage-Ara for possession of a locally made muzzle loading firearm at Panahaduwa in Udawalawa area. Investigations are being conducted.",
        "hierarchy": ["DIG Ratnapura District", "Embilipitiya Div."],
        "otm": "OTM.1445",
        "province": "SABARAGAMUWA"
    },
    {
        "station": "ADAMPAN",
        "summary": "Arrest of suspects along with two detonators",
        "body": "On the 17th of March 2026, officers of the Navy attached to the Wedithalathivu camp arrested the following persons while sailing in a boat in the sea of Wedithalathivu area with the possession of 2 non-electric detonators. (1) A.R.J. Patric, aged 27 (2) A.F. Perera, aged 44 (3) R. Jonindan, aged 44 and (4) A.S. Pihiravo, aged 32 of Pallimune-East, Mannar. Investigations are being conducted.",
        "hierarchy": ["DIG Wanni District", "Mannar Div."],
        "ctm": "CTM.530",
        "province": "NORTHERN"
    }
]

# ============================================================================
# GENERAL REPORT - March 17-18, 2026 (71 incidents total)
# ============================================================================

# 01. SERIOUS CRIMES COMMITTED (7 incidents from PDF)
GENERAL_01_SERIOUS_CRIMES = [
    {
        "station": "KALUTARA SOUTH",
        "summary": "A case of a theft of Rs. 40,000/= and gold jewellery",
        "body": "A case of a theft of Rs. 40,000/= and gold jewellery (6 ½ sovereigns) valued Rs. 3,440,000/= was reported to the police station. The offence took place between 1800 hrs on 1st of March 2026 and 1500 hrs on 16th of March 2026 at #08, Central Garden, Pragathi Mawatha, Kalutara south. Complainant named S. S. Malar, (TP 076-9386812). Suspect identified as P. Madushanka and yet to be arrested. The stolen property not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Kalutara District", "Kalutara Div."],
        "ctm": "CTM.521",
        "province": "WESTERN"
    },
    {
        "station": "SOORIYAWEWA",
        "summary": "A case of a homicide by assaulting with a club",
        "body": "A case of a homicide by assaulting with a club was reported to the police station. The offence took place on the 16th of March 2026 around 2100 hrs at #10, Usgala, Andarawewa, Sooriyawewa. Deceased: E. R. Kumara, aged 40, (male). Suspect identified as K. S. Alwis and yet to be arrested. Investigations are being conducted.",
        "hierarchy": ["DIG Hambantota District", "Tangalle Div."],
        "otm": "OTM.1400",
        "province": "SOUTHERN"
    },
    {
        "station": "PUSSELLAWA",
        "summary": "A case of a burglary of Rs. 150,000/= and gold jewellery",
        "body": "A case of a burglary of Rs. 150,000/= and gold jewellery (01 ¾ sovereigns) valued Rs. 600,000/= by breaking and entering through a window of a house was reported to the police station. The offence took place between 0900 hrs on 14th of March 2026 and 1400 hrs on 16th of March 2026 at Mawelakanda, Maswela. Complainant named H. S. Kandegedara, (TP 072-5340753). Suspect: Unknown. The stolen cash and jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Kandy District", "Gampola Div."],
        "ctm": "CTM.522",
        "province": "CENTRAL"
    },
    {
        "station": "GAMPOLA",
        "summary": "A case of a theft of 320m power cable",
        "body": "A case of a theft of 320m power cable valued Rs. 560,000/= was reported to the police station. The offence took place on the 17th of March 2026 around 0130 hrs at Dialog Tower, Delpitiya, Atabage. Complainant named D. W. G. S. Banda, (TP 070-7214708). Suspect: Unknown. The stolen property not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Kandy District", "Gampola Div."],
        "ctm": "CTM.520",
        "province": "CENTRAL"
    },
    {
        "station": "KALPITIYA",
        "summary": "A case of theft of a motorcycle",
        "body": "A case of theft of a motorcycle bearing # NW BEV 7940 worth Rs. 400,000/= was reported to the police station. The offence took place on the 17th of March 2026 between 0530 hrs and 1115 hrs at Kurinchchanpitiya Junction, Kalpitiya. Complainant named M. A. P. Fernando, (TP 076-8043293). Suspect: Unknown. The stolen motorcycle not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Puttalam District", "Puttalam Div."],
        "ctm": "CTM.532",
        "province": "NORTH WESTERN"
    },
    {
        "station": "CHUNNAKAM",
        "summary": "A case of a theft of gold jewellery (05 sovereigns)",
        "body": "A case of a theft of gold jewellery (05 sovereigns) valued Rs. 1,975,000/= was reported to the police station. The offence took place on the 17th of March 2026 between 0430 hrs and 0500 hrs at #18/48, Induvil west, Induvil, Chunnakam. Complainant named S. Sarwalogeshwari, (TP 077-5692523). Suspect: Unknown. The stolen jewellery not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Jaffna District", "Jaffna Div."],
        "ctm": "CTM.524",
        "province": "NORTHERN"
    },
    {
        "station": "MULLIYAVELI",
        "summary": "A case of a robbery of a gold necklace by snatching",
        "body": "A case of a robbery of a gold necklace (02 sovereigns) worth Rs. 700,000/= by snatching was reported to the police station. The offence took place on the 17th of March 2026 around 1400 hrs in Murippu, Mulliyaveli area. Complainant named W. Paleshwary, (TP 074-1334612) Suspect: Unknown. The robbed necklace not recovered and investigations in process. Motive: For illegal gain.",
        "hierarchy": ["DIG Kilinochchi District", "Mulathivu Div."],
        "ctm": "CTM.531",
        "province": "NORTHERN"
    }
]

# 02. RAPE, SEXUAL ASSAULT & CHILD ABUSE (7 incidents)
GENERAL_02_RAPE_ABUSE = [
    {
        "station": "KANDANA",
        "summary": "A case of a rape by using criminal force",
        "body": "A case of a rape by using criminal force which had taken place on a day in the month of October 2025 at #325/A/10/01, Central park, Kandana was reported to the police station. Victim: E. M. Mathushi Sara, aged 17, (female), (076-1198535). Suspect identified as W. D. S. Ansal and yet to be arrested. Investigations are being conducted. Motive: To fulfill sexual desire.",
        "hierarchy": ["DIG WP North District", "Kelaniya Div."],
        "ctm": "CTM.534",
        "province": "WESTERN"
    },
    {
        "station": "RAMBUKKANA",
        "summary": "A case of abduction, rape and child abuse over a love affair",
        "body": "A case of abduction, rape and child abuse over a love affair which had taken place around 0740 hrs on the 13th of March 2026 at Salvation Church, Rambukkana was reported to the police station. Victim: D. G. A. Sathsarani, aged 15, (female). Suspect: A. D. T. Dewmina, aged 19, (male), arrested and released on bail by the court. Motive: To fulfill sexual desire.",
        "hierarchy": ["DIG Kegalle District", "Kegalle Div."],
        "ctm": "CTM.517",
        "province": "SABARAGAMUWA"
    },
    {
        "station": "KARANDUGALA",
        "summary": "A case of a rape and child abuse by using criminal force",
        "body": "A case of a rape and child abuse by using criminal force which had taken place on a day in the month of December 2025 at Perana, Bulupitiya, Nilgala, Bibila was reported to the police station. Victim: D. M. G. Nawanjani, aged 09, (female), (072-4786229). Suspect: T. W. M. Thilakarathna, aged 60, (male), in custody. The suspect is scheduled to be produced before the court. Motive: To fulfill sexual desire.",
        "hierarchy": ["DIG Monaragala District", "Monaragala Div."],
        "ctm": "CTM.523",
        "province": "UVA"
    },
    {
        "station": "DAMBULLA",
        "summary": "A case of abduction, rape and child abuse over a love affair",
        "body": "A case of abduction, rape and child abuse over a love affair which had taken place on the 28th of February 2026 at Maha Yaya, Dambulla was reported to the police station. Victim: D. M. Sewmini Dissanayaka, aged 15, (female), (071-8379051). Suspect: H. A. I. Ranasingha, aged 18, (male), in custody. The suspect is scheduled to be produced before the court. Motive: To fulfill sexual desire.",
        "hierarchy": ["DIG Kandy District", "Matale Div."],
        "ctm": "CTM.528",
        "province": "CENTRAL"
    },
    {
        "station": "NORWOOD",
        "summary": "A case of a grave sexual abuse on a child by using criminal force",
        "body": "A case of a grave sexual abuse on a child by using criminal force which had taken place around 1500 hrs on the 13th of March 2026 at Elbada, Norwood was reported to the police station. Victim: P. Darshika, aged 11, (female), (077-9663625). Suspect identified as Thissaraj and yet to be arrested. Investigations are being conducted. Motive: To fulfill sexual desire.",
        "hierarchy": ["DIG Nuwara-Eliya District", "Hatton Div."],
        "ctm": "CTM.535",
        "province": "CENTRAL"
    },
    {
        "station": "KOSWATTA",
        "summary": "A case of a rape and child abuse by using criminal force",
        "body": "A case of a rape and child abuse by using criminal force which had taken place on a day in the month of January 2026 at #224, Welameda road, Haldaduwana was reported to the police station. Victim: R. M. I. Priyadarshani, aged 13, (female), (077-3205862). Suspect identified as Ajith and yet to be arrested. Investigations are being conducted. Motive: To fulfill sexual desire.",
        "hierarchy": ["DIG Puttalam District", "Chilaw Div."],
        "ctm": "CTM.527",
        "province": "NORTH WESTERN"
    },
    {
        "station": "WAKARE",
        "summary": "A case of abduction, rape and child abuse over a love affair",
        "body": "A case of abduction, rape and child abuse over a love affair which had taken place on a day in the month of November 2025 at Omadiyamadu, Punani was reported to the police station. Victim: N. Ranu, aged 14, (female), (077-9917515). Suspect: P. Danusran, aged 20, (male), in custody. The suspect is scheduled to be produced before the court. Motive: To fulfill sexual desire.",
        "hierarchy": ["DIG Batticaloa District", "Batticaloa Div."],
        "ctm": "CTM.525",
        "province": "EASTERN"
    }
]

# 03. FATAL ACCIDENTS (9 incidents)
GENERAL_03_FATAL_ACCIDENTS = [
    {
        "station": "WELLAMPITIYA",
        "summary": "A case of a fatal accident involving a bus and a pedestrian",
        "body": "A case of a fatal accident involving a bus bearing # ND 1325 and a pedestrian which had taken place around 1656 hrs on the 16th of March 2026 along Avissawella-Colombo road was reported to the police station. Deceased: B. J. Busho, aged 66, (male), the pedestrian, died on the 16th of March 2026. The accident had taken place due to reckless driving of the bus driver named H. A. J. Kumara, aged 42, (male), in custody. The suspect is scheduled to be produced before the court.",
        "hierarchy": ["DIG WP South District", "Nugegoda Div."],
        "ctm": "CTM.514",
        "province": "WESTERN"
    },
    {
        "station": "BADURALIYA",
        "summary": "A case of a fatal accident involving a three-wheeler, motorcycle and pedestrian",
        "body": "A case of a fatal accident involving a three-wheeler bearing # AAF 9871, a motorcycle bearing # BAM 9256 and a pedestrian which had taken place around 1910 hrs on the 16th of March 2026 along Lathpadura-Molkawa road was reported to the police station. Deceased: S. Meiyanadan, aged 73, (male), the pedestrian, died on the 16th of March 2026. The accident had taken place due to reckless driving of the three-wheeler driver named T. Nilanga, aged 36, (male), the Army solider 1024338 attached to the Army Camp, Kukulegaga was admitted to the Teaching Hospital, Nagoda due to injuries. Investigations are being conducted.",
        "hierarchy": ["DIG Kalutara District", "Kalutara Div."],
        "ctm": "CTM.515",
        "province": "WESTERN"
    },
    {
        "station": "KEGALLE",
        "summary": "A case of a fatal accident involving a motorcycle",
        "body": "A case of a fatal accident involving a motorcycle bearing # SP TJ 4493 which had taken place around 1530 hrs on the 17th of March 2026 along Kegalle-Debathgama road was reported to the police station. The rider had lost control and crashed on to a tree. Deceased: W. M. S. R. Wijesingha, aged 41, (male), a pillion rider. (the Army solider S602507 attached to the Army Camp, Dobagoda) Suspect: K. A. N. Jayarathna, aged 43, (male) the rider of the motorcycle admitted to the General Hospital Kegalle due to injuries. Investigations are being conducted.",
        "hierarchy": ["DIG Kegalle District", "Kegalle Div."],
        "ctm": "CTM.529",
        "province": "SABARAGAMUWA"
    },
    {
        "station": "KARUWALAGASWEWA",
        "summary": "A case of a fatal accident involving a tractor and a motorcycle",
        "body": "A case of a fatal accident involving a tractor bearing # RD 2021(46-8622) and a motorcycle bearing # NW BIZ 6439 which had taken place around 1845 hrs on the 2nd of March 2026 along Tewanuwara-Kaluwalagaswewa road was reported to the police station. Deceased: W. A. Somarathna, aged 69, (male), the motorcyclist, died on 17th of March 2026. The accident had taken place due to reckless driving of the tractor driver named H. F. N. M. Fonseka, aged 31, (male), arrested and released on bail by the court. Investigations are being conducted.",
        "hierarchy": ["DIG Puttalam District", "Puttalam Div."],
        "ctm": "CTM.516",
        "province": "NORTH WESTERN"
    },
    {
        "station": "NOROCHCHOLAYA",
        "summary": "A case of a fatal accident involving a lorry and a pedestrian",
        "body": "A case of a fatal accident involving a lorry bearing # NW GE 2436 and a pedestrian which had taken place around 2110 hrs on the 15th of March 2026 along Palaviya-Kalpitiya road was reported to the police station. Deceased: S. P. K. Gamini, aged 54, (male), the pedestrian, died on the 17th of March 2026. The accident had taken place due to reckless driving of the lorry driver named A. M. Ishak, aged 45, (male), in custody. The suspect is scheduled to be produced before the court.",
        "hierarchy": ["DIG Puttalam District", "Puttalam Div."],
        "ctm": "CTM.518",
        "province": "NORTH WESTERN"
    },
    {
        "station": "ALAWWA",
        "summary": "A case of a fatal accident involving a lorry and a motorcycle",
        "body": "A case of a fatal accident involving a lorry bearing #NW LA 1965 and a motorcycle bearing # NW XZ 8912 which had taken place around 1720 hrs on the 17th of March 2026 along Colombo-Kurunegala road was reported to the police station. Deceased: H. G. S. Kumara, aged 62, (male), the motorcyclist, died on the 17th of March 2026. The accident had taken place due to reckless driving of the lorry driver named L. S. N. Liyanage, aged 28, (male), in custody. The suspect is scheduled to be produced before the court.",
        "hierarchy": ["DIG Kurunegala District", "Kurunegala Div."],
        "ctm": "CTM.526",
        "province": "NORTH WESTERN"
    },
    {
        "station": "KULIYAPITIYA",
        "summary": "A case of a fatal accident involving a cab and a pedestrian",
        "body": "A case of a fatal accident involving a cab bearing #DAC 0326 and a pedestrian which had taken place around 1910 hrs on the 17th of March 2026 along Kuliyapitiya-Narammala road was reported to the police station. Deceased: D. U. Karunasena, aged 73, (male), the pedestrian, died on the 17th of March 2026. The accident had taken place due to reckless driving of the cab driver named H. H. A. M. De Silva, aged 49, (male), in custody. The suspect is scheduled to be produced before the court.",
        "hierarchy": ["DIG Kurunegala District", "Kuliyapitiya Div."],
        "ctm": "CTM.533",
        "province": "NORTH WESTERN"
    },
    {
        "station": "DEHIATHTHAKANDIYA",
        "summary": "A case of a fatal accident involving a lorry and a three-wheeler",
        "body": "A case of a fatal accident involving a lorry bearing # NC LA 6890 and a three-wheeler bearing #NC QM 3177 which had taken place around 1245 hrs on the 17th of March 2026 along Mahiyanganaya-Polonnaruwa road was reported to the police station. Deceased: D. M. W. G. K. Kumari, aged 58, (female), a passenger of the three-wheeler, died on the 17th of March 2026. The accident had taken place due to reckless driving of the lorry driver named S. G. K. M. Premarathna, aged 25, (male), in custody. The suspect is scheduled to be produced before the court.",
        "hierarchy": ["DIG Ampara District", "Ampara Div."],
        "otm": "OTM.1419",
        "province": "EASTERN"
    },
    {
        "station": "CHINABAY",
        "summary": "A case of a fatal accident involving a lorry and a motorcycle",
        "body": "A case of a fatal accident involving a lorry bearing #EP LI 8920 and a motorcycle bearing # EP BCV 7368 which had taken place around 2025 hrs on the 17th of March 2026 along Trincomalee-Batticaloa road was reported to the police station. Deceased: M. M. Sabri, aged 40, (male), the motorcyclist, died on the 17th of March 2026. The accident had taken place due to reckless riding of the deceased. Investigations are being conducted.",
        "hierarchy": ["DIG Trincomalee District", "Trincomalee Div."],
        "ctm": "CTM.536",
        "province": "EASTERN"
    }
]

# 09. OTHER MATTERS (48 incidents - largest category)
GENERAL_09_OTHER_MATTERS = [
    # This would contain 48 incidents from the official PDF
    # Including various minor incidents, complaints, etc.
    # Due to volume, these need to be extracted from the PDF systematically
]

# Combine all general incidents
ALL_GENERAL_MARCH17_18 = (
    GENERAL_01_SERIOUS_CRIMES +
    GENERAL_02_RAPE_ABUSE +
    GENERAL_03_FATAL_ACCIDENTS +
    GENERAL_09_OTHER_MATTERS
)

print(f"\n{'='*80}")
print("DATA EXTRACTION STATUS - March 17-18, 2026")
print(f"{'='*80}")
print(f"\nSecurity Report: {len(SECURITY_MARCH17_18)} incidents")
print(f"  • Category 03 (Arms/Ammunition): {len(SECURITY_MARCH17_18)}")
print(f"\nGeneral Report: {len(ALL_GENERAL_MARCH17_18)} incidents extracted so far")
print(f"  • Category 01 (Serious Crimes): {len(GENERAL_01_SERIOUS_CRIMES)}")
print(f"  • Category 02 (Rape/Abuse): {len(GENERAL_02_RAPE_ABUSE)}")
print(f"  • Category 03 (Fatal Accidents): {len(GENERAL_03_FATAL_ACCIDENTS)}")
print(f"  • Category 09 (Other Matters): {len(GENERAL_09_OTHER_MATTERS)}")
print(f"\nOFFICIAL PDF shows 71 total general incidents")
print(f"Still need to extract: {71 - len(ALL_GENERAL_MARCH17_18)} incidents")
print(f"{'='*80}")
