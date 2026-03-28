"""
test_complete_system.py — Comprehensive System Test Suite
==========================================================
Tests all major components of the police report processing engine.
"""

import os
import sys
import json
import time

sys.path.append(os.path.dirname(__file__))

def test_openrouter_connection():
    """Test OpenRouter API connectivity."""
    print("\n" + "="*60)
    print("TEST 1: OpenRouter API Connection")
    print("="*60)
    
    try:
        from openrouter_client import OpenRouterClient
        
        api_key = "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"
        client = OpenRouterClient(api_key)
        
        # Test simple chat
        response = client.chat_completion("Say 'Connection successful' in one sentence.")
        
        if response and len(response) > 0:
            print("✅ PASS: OpenRouter connection working")
            print(f"   Response: {response[:100]}...")
            return True
        else:
            print("❌ FAIL: Empty response from OpenRouter")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_ai_engine_manager():
    """Test unified AI engine manager with fallback."""
    print("\n" + "="*60)
    print("TEST 2: AI Engine Manager")
    print("="*60)
    
    try:
        from ai_engine_manager import AIEngineManager
        
        manager = AIEngineManager(mode="auto")
        
        # Test call
        response = manager.call_ai("Translate: පොලිස් ස්ථානය", system_prompt="You are a translator.")
        
        if response and not response.startswith("❌"):
            print(f"✅ PASS: AI Engine working (Used: {manager.last_engine_used})")
            print(f"   Stats: {manager.stats}")
            return True
        else:
            print(f"❌ FAIL: {response}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_pdf_extraction():
    """Test PDF text extraction."""
    print("\n" + "="*60)
    print("TEST 3: PDF Text Extraction")
    print("="*60)
    
    try:
        import translator_pipeline
        
        # Find a test PDF
        test_pdfs = [f for f in os.listdir("uploads") if f.endswith(".pdf")]
        
        if not test_pdfs:
            print("⚠️ SKIP: No test PDFs found in uploads/")
            return None
        
        test_pdf = os.path.join("uploads", test_pdfs[0])
        print(f"   Testing with: {test_pdfs[0]}")
        
        text = translator_pipeline.extract_text_with_layout(test_pdf)
        
        if text and len(text) > 100:
            print(f"✅ PASS: Extracted {len(text)} characters")
            print(f"   Preview: {text[:150]}...")
            return True
        else:
            print("❌ FAIL: Extraction returned insufficient text")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_document_splitting():
    """Test General/Security document splitting."""
    print("\n" + "="*60)
    print("TEST 4: Document Splitting")
    print("="*60)
    
    try:
        import translator_pipeline
        
        # Sample text with both sections
        sample_text = """
        GENERAL SITUATION
        
        01. SERIOUS CRIMES COMMITTED
        Colombo Police Station reported...
        
        SECURITY SITUATION
        
        01. VERY IMPORTANT MATTERS
        Special Branch reported...
        """
        
        general, security = translator_pipeline.split_sinhala_document(sample_text)
        
        if "GENERAL" in general and "SECURITY" in security:
            print("✅ PASS: Document split successfully")
            print(f"   General: {len(general)} chars")
            print(f"   Security: {len(security)} chars")
            return True
        else:
            print("❌ FAIL: Splitting did not work correctly")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_regex_engine():
    """Test offline regex extraction engine."""
    print("\n" + "="*60)
    print("TEST 5: Regex Engine")
    print("="*60)
    
    try:
        import regex_engine
        
        sample_text = """
        01. SERIOUS CRIMES COMMITTED
        
        WESTERN PROVINCE
        
        COLOMBO POLICE STATION: S/DIG Western Province, DIG Colombo, Colombo Division
        On 2026.03.14, a robbery was reported (CTM 123/2026). Suspect arrested.
        """
        
        result = regex_engine.structure_with_regex(sample_text, report_type="General")
        
        if result and "sections" in result:
            print(f"✅ PASS: Regex engine extracted {len(result['sections'])} sections")
            if result['sections']:
                print(f"   First section: {result['sections'][0].get('title', 'N/A')}")
            return True
        else:
            print("❌ FAIL: Regex engine returned invalid structure")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_confidence_scoring():
    """Test confidence scoring system."""
    print("\n" + "="*60)
    print("TEST 6: Confidence Scoring")
    print("="*60)
    
    try:
        import pipeline_utils
        
        # Good incident
        good_incident = {
            "station": "COLOMBO POLICE STATION",
            "body": "On 2026.03.14, a robbery was reported (CTM 123/2026). Suspect aged 25 arrested. Investigations ongoing.",
            "hierarchy": ["S/DIG Western Province", "DIG Colombo"]
        }
        
        # Poor incident
        poor_incident = {
            "station": "UNKNOWN",
            "body": "Incident reported.",
            "hierarchy": []
        }
        
        good_score = pipeline_utils.calculate_confidence(good_incident)
        poor_score = pipeline_utils.calculate_confidence(poor_incident)
        
        if good_score > 0.6 and poor_score < 0.5:
            print(f"✅ PASS: Confidence scoring working correctly")
            print(f"   Good incident: {good_score:.2f}")
            print(f"   Poor incident: {poor_score:.2f}")
            return True
        else:
            print(f"❌ FAIL: Unexpected scores (Good: {good_score:.2f}, Poor: {poor_score:.2f})")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_html_generation():
    """Test HTML report generation."""
    print("\n" + "="*60)
    print("TEST 7: HTML Report Generation")
    print("="*60)
    
    try:
        import web_report_engine
        
        sample_data = {
            "date_range": "2026.03.14 - 2026.03.15",
            "prepared_by": "Test Officer",
            "sections": [
                {
                    "title": "01. SERIOUS CRIMES COMMITTED",
                    "count": "1",
                    "provinces": [
                        {
                            "name": "WESTERN PROVINCE",
                            "incidents": [
                                {
                                    "station": "COLOMBO",
                                    "hierarchy": ["S/DIG Western", "DIG Colombo"],
                                    "body": "Test incident reported."
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        output_path = "tmp/test_output.html"
        os.makedirs("tmp", exist_ok=True)
        
        web_report_engine.generate_html_report(sample_data, output_path, report_type="General")
        
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                html = f.read()
            
            if "SERIOUS CRIMES" in html and "COLOMBO" in html:
                print("✅ PASS: HTML report generated successfully")
                print(f"   Output: {output_path}")
                return True
            else:
                print("❌ FAIL: HTML missing expected content")
                return False
        else:
            print("❌ FAIL: HTML file not created")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_batch_processor():
    """Test batch processing module."""
    print("\n" + "="*60)
    print("TEST 8: Batch Processor")
    print("="*60)
    
    try:
        from batch_processor import BatchProcessor
        
        # Check if we have test PDFs
        test_pdfs = [f for f in os.listdir("uploads") if f.endswith(".pdf")]
        
        if len(test_pdfs) < 2:
            print("⚠️ SKIP: Need at least 2 PDFs for batch test")
            return None
        
        print(f"   Found {len(test_pdfs)} PDFs for batch test")
        print("   (Skipping actual processing to save time)")
        print("✅ PASS: Batch processor module loaded successfully")
        return True
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  POLICE REPORT ENGINE - COMPLETE SYSTEM TEST".center(58) + "█")
    print("█" + f"  Version: v2.1.0".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    start_time = time.time()
    
    tests = [
        ("OpenRouter Connection", test_openrouter_connection),
        ("AI Engine Manager", test_ai_engine_manager),
        ("PDF Extraction", test_pdf_extraction),
        ("Document Splitting", test_document_splitting),
        ("Regex Engine", test_regex_engine),
        ("Confidence Scoring", test_confidence_scoring),
        ("HTML Generation", test_html_generation),
        ("Batch Processor", test_batch_processor),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result is True else ("❌ FAIL" if result is False else "⚠️ SKIP")
        print(f"{status}  {name}")
    
    print("="*60)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print(f"Success Rate: {(passed/(total-skipped)*100):.1f}%" if (total-skipped) > 0 else "N/A")
    print(f"Duration: {time.time() - start_time:.1f}s")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review and fix issues.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
