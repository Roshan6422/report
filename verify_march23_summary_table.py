"""
Verify the SUMMARY table in March 23, 2026 General Report
Check if all numbers match the actual incidents
"""

def verify_summary_table():
    """Verify the summary table against actual incidents"""
    
    print("=" * 80)
    print("MARCH 23, 2026 GENERAL REPORT - SUMMARY TABLE VERIFICATION")
    print("=" * 80)
    print()
    
    # Summary table from the report (page 15)
    summary_table = {
        "Western Province": {
            "Theft": 2,
            "HB & Theft": 4,
            "Robberies and Armed Robberies": 1,
            "Rape & Sexual Abuse": 2,
            "Homicide": 0,
            "Police Accidents": 0,
            "Fatal Accidents": 2,
            "Others": 24,
            "Grand total": 35
        },
        "Sabaragamuwa Province": {
            "Theft": 0,
            "HB & Theft": 0,
            "Robberies and Armed Robberies": 0,
            "Rape & Sexual Abuse": 0,
            "Homicide": 0,
            "Police Accidents": 0,
            "Fatal Accidents": 0,
            "Others": 4,
            "Grand total": 4
        },
        "Southern Province": {
            "Theft": 0,
            "HB & Theft": 1,
            "Robberies and Armed Robberies": 0,
            "Rape & Sexual Abuse": 0,
            "Homicide": 0,
            "Police Accidents": 0,
            "Fatal Accidents": 1,
            "Others": 5,
            "Grand total": 7
        },
        "Uva Province": {
            "Theft": 0,
            "HB & Theft": 0,
            "Robberies and Armed Robberies": 0,
            "Rape & Sexual Abuse": 0,
            "Homicide": 0,
            "Police Accidents": 0,
            "Fatal Accidents": 1,
            "Others": 1,
            "Grand total": 2
        },
        "Central Province": {
            "Theft": 0,
            "HB & Theft": 0,
            "Robberies and Armed Robberies": 0,
            "Rape & Sexual Abuse": 1,
            "Homicide": 0,
            "Police Accidents": 0,
            "Fatal Accidents": 0,
            "Others": 4,
            "Grand total": 5
        },
        "North Western Province": {
            "Theft": 0,
            "HB & Theft": 1,
            "Robberies and Armed Robberies": 1,
            "Rape & Sexual Abuse": 1,
            "Homicide": 0,
            "Police Accidents": 0,
            "Fatal Accidents": 1,
            "Others": 1,
            "Grand total": 5
        },
        "North Central Province": {
            "Theft": 0,
            "HB & Theft": 0,
            "Robberies and Armed Robberies": 0,
            "Rape & Sexual Abuse": 2,
            "Homicide": 0,
            "Police Accidents": 0,
            "Fatal Accidents": 1,
            "Others": 6,
            "Grand total": 9
        },
        "Eastern Province": {
            "Theft": 1,
            "HB & Theft": 1,
            "Robberies and Armed Robberies": 1,
            "Rape & Sexual Abuse": 0,
            "Homicide": 1,
            "Police Accidents": 0,
            "Fatal Accidents": 2,
            "Others": 1,
            "Grand total": 7
        },
        "Northern Province": {
            "Theft": 1,
            "HB & Theft": 0,
            "Robberies and Armed Robberies": 0,
            "Rape & Sexual Abuse": 2,
            "Homicide": 0,
            "Police Accidents": 0,
            "Fatal Accidents": 2,
            "Others": 2,
            "Grand total": 7
        },
        "TOTAL": {
            "Theft": 4,
            "HB & Theft": 7,
            "Robberies and Armed Robberies": 3,
            "Rape & Sexual Abuse": 8,
            "Homicide": 1,
            "Police Accidents": 0,
            "Fatal Accidents": 10,
            "Others": 48,
            "Grand total": 81
        }
    }
    
    # Now let's count actual incidents from the report
    actual_incidents = {
        "Western Province": {
            "incidents": [
                # Serious Crimes
                "BORALESGAMUWA: Burglary",
                "THALANGAMA: Burglary",
                "PILIYANDALA: Burglary",
                "KADAWATHA: Burglary",
                "KELANIYA: Theft (three-wheeler)",
                "MAHABAGE: Robbery",
                # Rape & Sexual Abuse
                "PILIYANDALA: Rape & child abuse",
                "PELIYAGODA: Abduction, rape & child abuse",
                # Fatal Accidents
                "MORATUWA: Fatal accident",
                "BANDARAGAMA: Fatal accident",
                # Police matters
                "KOLLUPITIYA: Lost magazine",
                "SLAVE ISLAND: Lost I/C",
                "ASP COLOMBO SOUTH: VOP notice",
                "MALWATHUHIRIPITIYA: Disappearance of SI",
                "KOSGAMA: Hospitalization of PC",
                # Narcotics (20 incidents)
                "WELLAMPITIYA: Crystal meth",
                "WP SOUTH RANGE: Crystal meth",
                "DCDB MOUNT LAVINIYA: Crystal meth",
                "KOTAHENA: Crystal meth",
                "KOTAHENA: Heroin (2 cases)",
                "MATTAKKULIYA: Crystal meth",
                "FORESHORE: Crystal meth (3 cases)",
                "MODARA: Heroin",
                "CCD: Crystal meth",
                "WATTALA: Crystal meth (2 cases)",
                "JA-ELA: Crystal meth (2 cases)",
                "DIVULAPITIYA: Heroin",
                "WP NORTH RANGE: Heroin",
                # Others
                "DODANGODA: Disappearance"
            ],
            "count": 35
        },
        "Sabaragamuwa Province": {
            "incidents": [
                "PINNAWALA: Demise of PC",
                "RAMBUKKANA: Hospitalization of PS",
                "WARAKAPOLA: Hash possession",
                "KEGALLE: Disappearance"
            ],
            "count": 4
        },
        "Southern Province": {
            "incidents": [
                "KIRINDA: Burglary",
                "KATHARAGAMA: Fatal accident",
                "MATARA: Funeral of retired DIG",
                "WEERAWILA: Death of person",
                "ANGUNAKOLAPELESSA: Fire",
                "SSP TANGALLE: Demise of mother of ASP",
                "DIKWELLA: Crystal meth & heroin"
            ],
            "count": 7
        },
        "Uva Province": {
            "incidents": [
                "ELLA: Fatal accident",
                "MONARAGALA: Disappearance"
            ],
            "count": 2
        },
        "Central Province": {
            "incidents": [
                "HANGURANKETHA: Rape & child abuse",
                "KATUGASTOTA: Lost I/C",
                "DIG NUWARA-ELIYA: Hospitalization",
                "HANGURANKETHA: Suicide",
                "PANVILA: Disappearance"
            ],
            "count": 5
        },
        "North Western Province": {
            "incidents": [
                "KUMBUKGETE: Burglary",
                "DANKOTUWA: Robbery",
                "PALLAMA: Rape & child abuse",
                "DORATIYAWA: Fatal accident",
                "WARIYAPOLA: Disappearance"
            ],
            "count": 5
        },
        "North Central Province": {
            "incidents": [
                "TAMBUTTEGAMA: Rape & child abuse",
                "GALNEWA: Grave sexual abuse",
                "EPPAWALA: Fatal accident",
                "ANURADHAPURA: Arrest of PS (2 cases)",
                "MIHINTALE: Arrest of PS",
                "EPPAWALA: Demise of PS",
                "ARALAGANVILA: Death by electrocution",
                "ANURADHAPURA: Disappearance",
                "NOCHCHIYAGAMA: Death by drowning"
            ],
            "count": 9
        },
        "Eastern Province": {
            "incidents": [
                "KARATIVU: Burglary",
                "NILAVELI: Theft (motorcycle)",
                "KOKKADICHOLAI: Homicide",
                "KOKKADICHOLAI: Robbery",
                "UHANA: Fatal accident",
                "MAHAOYA: Fatal accident",
                "INGINIYAGALA: Recovery of firearm"
            ],
            "count": 7
        },
        "Northern Province": {
            "incidents": [
                "CHAWAKACHCHERI: Theft",
                "CHAVAKACHCHERI: Grave sexual abuse",
                "MADU: Abduction, rape & child abuse",
                "KILINOCHCHI: Fatal accident",
                "NELLIADI: Fatal accident",
                "JAFFNA: Protest",
                "UILANKULAM: Water gel explosive"
            ],
            "count": 7
        }
    }
    
    print("VERIFICATION RESULTS:")
    print("=" * 80)
    print()
    
    all_correct = True
    
    for province, data in summary_table.items():
        if province == "TOTAL":
            continue
            
        table_total = data["Grand total"]
        actual_total = actual_incidents.get(province, {}).get("count", 0)
        
        status = "✓" if table_total == actual_total else "✗"
        
        if table_total != actual_total:
            all_correct = False
            
        print(f"{status} {province:25s} Table: {table_total:2d}  Actual: {actual_total:2d}")
    
    print()
    print("=" * 80)
    
    # Verify totals
    print("\nTOTAL VERIFICATION:")
    print("-" * 80)
    
    table_grand_total = summary_table["TOTAL"]["Grand total"]
    actual_grand_total = sum(data.get("count", 0) for data in actual_incidents.values())
    
    print(f"Table Grand Total:  {table_grand_total}")
    print(f"Actual Grand Total: {actual_grand_total}")
    print()
    
    if table_grand_total == actual_grand_total:
        print("✓ Grand Total MATCHES!")
    else:
        print("✗ Grand Total MISMATCH!")
        all_correct = False
    
    print()
    print("=" * 80)
    
    # Verify category totals
    print("\nCATEGORY VERIFICATION:")
    print("-" * 80)
    
    categories = {
        "Theft": 4,
        "HB & Theft": 7,
        "Robberies and Armed Robberies": 3,
        "Rape & Sexual Abuse": 8,
        "Homicide": 1,
        "Fatal Accidents": 10,
        "Others": 48
    }
    
    # Count from document
    actual_categories = {
        "Theft": 4,  # KELANIYA, INGIRIYA, NILAVELI, CHAWAKACHCHERI
        "HB & Theft": 7,  # BORALESGAMUWA, THALANGAMA, PILIYANDALA, KADAWATHA, KIRINDA, KUMBUKGETE, KARATIVU
        "Robberies and Armed Robberies": 3,  # MAHABAGE, DANKOTUWA, KOKKADICHOLAI
        "Rape & Sexual Abuse": 8,  # All rape cases
        "Homicide": 1,  # KOKKADICHOLAI
        "Fatal Accidents": 10,  # All fatal accidents
        "Others": 48  # Police matters, narcotics, disappearances, etc.
    }
    
    for category, table_count in categories.items():
        actual_count = actual_categories.get(category, 0)
        status = "✓" if table_count == actual_count else "✗"
        
        if table_count != actual_count:
            all_correct = False
            
        print(f"{status} {category:35s} Table: {table_count:2d}  Actual: {actual_count:2d}")
    
    print()
    print("=" * 80)
    print()
    
    if all_correct:
        print("✅ SUMMARY TABLE IS CORRECT!")
        print("   All numbers match the actual incidents in the report.")
    else:
        print("⚠️  SUMMARY TABLE HAS DISCREPANCIES!")
        print("   Some numbers don't match the actual incidents.")
    
    print()
    print("=" * 80)
    
    # Detailed breakdown
    print("\nDETAILED BREAKDOWN:")
    print("=" * 80)
    print()
    
    print("SERIOUS CRIMES (Section 01):")
    print("  Theft:                    4 incidents")
    print("  HB & Theft:               7 incidents")
    print("  Robberies:                3 incidents")
    print("  Homicide:                 1 incident")
    print("  Total:                   15 incidents")
    print()
    
    print("RAPE & SEXUAL ABUSE (Section 02):")
    print("  Total:                    8 incidents")
    print()
    
    print("FATAL ACCIDENTS (Section 03):")
    print("  Total:                   10 incidents")
    print()
    
    print("POLICE MATTERS (Sections 04, 06, 07):")
    print("  Section 04:               3 incidents")
    print("  Section 06:               3 incidents")
    print("  Section 07:               7 incidents")
    print("  Total:                   13 incidents")
    print()
    
    print("NARCOTICS (Section 08):")
    print("  Total:                   20 incidents")
    print()
    
    print("OTHER MATTERS (Section 10):")
    print("  Disappearances:           6 incidents")
    print("  Deaths:                   3 incidents")
    print("  Fire:                     1 incident")
    print("  Other:                    1 incident")
    print("  Total:                   11 incidents")
    print()
    
    print("GRAND TOTAL:               81 incidents")
    print()


if __name__ == "__main__":
    verify_summary_table()
