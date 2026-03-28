"""
Test script to verify Sinhala PDF translation accuracy
Tests the improved translation prompt with complete data extraction
"""

import os
import sys
import re

# Add project root to path
sys.path.append(r"d:\PROJECTS\pdf convert tool")

from ai_engine_manager import AIEngineManager
import translator_pipeline

def test_translation_with_sample():
    """Test translation with a sample Sinhala text"""
    
    # Sample Sinhala text (you can replace this with actual text from your PDF)
    sample_sinhala = """
    රත්නපුර දිස්ත්‍රික් පොලිස් ප්‍රධානී කාර්යාලය
    එඹිලිපිටිය පොලිස් ස්ථානය
    
    දිනය: 2026.03.17
    වේලාව: 1421 පැය
    
    සැකකරුවන් දෙදෙනෙකු විදුලි විස්ෆෝටකයක් සහ වෙඩි බෙහෙත් සමඟ අත්අඩංගුවට ගැනීම
    
    2026 මාර්තු 17 වන දින 1-1-9 ව්‍යාපෘතිය හරහා ලැබුණු තොරතුරක් මත ක්‍රියා කරමින්, 
    එඹිලිපිටිය දර්ශනාගම ශ්‍රී දර්ශනගිරි විහාරස්ථානයේ ප්‍රධාන හිමි 68 හැවිරිදි 
    පූජ්‍ය එඹිලිපිටියේ ඉන්ද්‍රරත්න හිමි සහ සේවනගල මයුරාගම අංක 896 හි 56 හැවිරිදි 
    එන්.යූ. සමන්චන්ද්‍ර යන පුද්ගලයා විහාරස්ථානයේ භූමියේ නිධන් සෙවීමේ අරමුණින් 
    උමග හාරමින් සිටියදී විදුලි විස්ෆෝටකයක් සහ ග්‍රෑම් 80ක වෙඩි බෙහෙත් සමඟ 
    පොලිසිය විසින් අත්අඩංගුවට ගන්නා ලදී.
    
    සැකකරුවන් 2026 මාර්තු 18 වන දින එඹිලිපිටිය මහේස්ත්‍රාත් අධිකරණය ඉදිරියේ 
    පැමිණිලි කිරීමට නියමිතය.
    
    (OTM.1421)
    """
    
    print("=" * 80)
    print("TRANSLATION ACCURACY TEST")
    print("=" * 80)
    print("\nOriginal Sinhala Text:")
    print("-" * 80)
    print(sample_sinhala)
    print("-" * 80)
    
    # Initialize AI Engine
    print("\n[1] Initializing AI Engine...")
    engine = AIEngineManager()
    
    # Create the improved translation prompt
    prompt = f"""Translate this Sinhala police report text to English with COMPLETE DATA EXTRACTION.

CRITICAL REQUIREMENTS - EXTRACT ALL DATA:
✓ ALL names with titles (Rev./Mr./Mrs./Miss) - EXACT spelling
✓ ALL ages (exact numbers)
✓ ALL addresses with house numbers (# XX format)
✓ ALL phone numbers (XXX-XXXXXXX format)
✓ ALL monetary values (Rs. X/= format)
✓ ALL quantities with units (X sovereigns, Xg, X items)
✓ ALL vehicle numbers (keep as shown)
✓ ALL reference codes (CTM.XXX or OTM.XXX or IR numbers)
✓ Date and time (exact - keep superscripts like 17th, 18th)
✓ Location (complete address with all details)
✓ Investigation status
✓ ALL details from tables (station, date, suspect info, incident details)

FORMATTING RULES:
- Use proper English grammar and sentence structure
- Keep all Sinhala names transliterated accurately
- Preserve all numbers, codes, and references EXACTLY
- Use professional police report terminology
- Format addresses as: # XX, Street, Area, City
- Format dates as: 17th March 2026, 0400 hrs
- Format ages as: aged XX
- Format occupations as: Occupation: XXXX

Sinhala text:
{sample_sinhala}

Translate to English with ALL data preserved:"""
    
    print("\n[2] Sending translation request to AI Engine...")
    print(f"    Engine Mode: {engine.mode}")
    print(f"    Model: {engine.openrouter_model if engine.mode != 'ollama' else engine.ollama_model}")
    
    # Call AI
    response = engine.call_ai(prompt, timeout=120)
    
    print("\n[3] Translation Result:")
    print("-" * 80)
    
    if response and not response.startswith("❌"):
        print(response)
        print("-" * 80)
        
        # Verify data extraction
        print("\n[4] Data Extraction Verification:")
        print("-" * 80)
        
        checks = {
            "Names": [
                ("Rev. Embilipitiye Indrarathana", "පූජ්‍ය එඹිලිපිටියේ ඉන්ද්‍රරත්න"),
                ("N.U. Samanchandra", "එන්.යූ. සමන්චන්ද්‍ර")
            ],
            "Ages": [
                ("68", "68 හැවිරිදි"),
                ("56", "56 හැවිරිදි")
            ],
            "Addresses": [
                ("# 896", "අංක 896"),
                ("Mayuragama", "මයුරාගම"),
                ("Sewanagala", "සේවනගල")
            ],
            "Quantities": [
                ("80g", "ග්‍රෑම් 80"),
                ("detonator", "විස්ෆෝටකයක්")
            ],
            "Dates": [
                ("17th March 2026", "2026 මාර්තු 17"),
                ("18th March 2026", "2026 මාර්තු 18")
            ],
            "Reference": [
                ("OTM.1421", "OTM.1421")
            ],
            "Location": [
                ("Embilipitiya", "එඹිලිපිටිය"),
                ("Darshanagama", "දර්ශනාගම"),
                ("Sri Darshanagiri viharaya", "ශ්‍රී දර්ශනගිරි විහාරස්ථානය")
            ]
        }
        
        total_checks = 0
        passed_checks = 0
        
        for category, items in checks.items():
            print(f"\n{category}:")
            for english_term, sinhala_term in items:
                total_checks += 1
                # Check if the English term appears in the response
                found = english_term.lower() in response.lower()
                status = "✓ FOUND" if found else "✗ MISSING"
                color = "green" if found else "red"
                print(f"  {status}: {english_term} (from: {sinhala_term})")
                if found:
                    passed_checks += 1
        
        print("\n" + "=" * 80)
        print(f"ACCURACY SCORE: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")
        print("=" * 80)
        
        if passed_checks == total_checks:
            print("\n✅ PERFECT! All data extracted correctly!")
        elif passed_checks >= total_checks * 0.8:
            print("\n⚠️  GOOD! Most data extracted, but some details missing.")
        else:
            print("\n❌ NEEDS IMPROVEMENT! Many details missing from translation.")
        
    else:
        print(f"❌ Translation failed: {response}")
        print("-" * 80)
    
    print(f"\n[5] Engine Statistics:")
    print(f"    Last Engine Used: {engine.last_engine_used}")
    print(f"    OpenRouter Calls: {engine.stats['openrouter_calls']}")
    print(f"    Ollama Calls: {engine.stats['ollama_calls']}")
    print(f"    Failures: {engine.stats['failures']}")

if __name__ == "__main__":
    test_translation_with_sample()
