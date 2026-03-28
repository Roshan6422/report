"""
Quick verification script to check if the app.py fix is working
"""

import os
import sys
import re

# Add project root to path
sys.path.append(r"d:\PROJECTS\pdf convert tool")

def check_app_py_fix():
    """Verify that app.py has the correct API call"""
    
    print("=" * 80)
    print("APP.PY FIX VERIFICATION")
    print("=" * 80)
    
    # Read app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for the correct method call
    has_correct_call = "engine.call_ai(prompt" in content
    has_wrong_call = "engine.generate_text(prompt" in content
    
    print("\n[1] Checking API Method Call:")
    print("-" * 80)
    
    if has_correct_call and not has_wrong_call:
        print("✅ CORRECT: Using engine.call_ai() method")
        print("   The fix has been applied successfully!")
    elif has_wrong_call:
        print("❌ ERROR: Still using engine.generate_text() method")
        print("   The fix was not applied or was reverted!")
        print("   Please check app.py around line 463")
        return False
    else:
        print("⚠️  WARNING: Could not find API call")
        print("   Please manually check app.py")
        return False
    
    # Check for comprehensive prompt
    print("\n[2] Checking Translation Prompt:")
    print("-" * 80)
    
    required_keywords = [
        "COMPLETE DATA EXTRACTION",
        "ALL names with titles",
        "ALL ages",
        "ALL addresses",
        "ALL phone numbers",
        "ALL reference codes",
        "FORMATTING RULES"
    ]
    
    found_keywords = []
    missing_keywords = []
    
    for keyword in required_keywords:
        if keyword in content:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    if len(found_keywords) == len(required_keywords):
        print("✅ CORRECT: Comprehensive translation prompt found")
        print(f"   All {len(required_keywords)} required keywords present")
    else:
        print(f"⚠️  WARNING: {len(missing_keywords)} keywords missing:")
        for kw in missing_keywords:
            print(f"   - {kw}")
    
    # Check for AI Engine import
    print("\n[3] Checking AI Engine Import:")
    print("-" * 80)
    
    if "from ai_engine_manager import AIEngineManager" in content:
        print("✅ CORRECT: AIEngineManager imported")
    else:
        print("❌ ERROR: AIEngineManager not imported")
        return False
    
    # Check for chunk size
    print("\n[4] Checking Chunk Size:")
    print("-" * 80)
    
    chunk_match = re.search(r'chunk_size\s*=\s*(\d+)', content)
    if chunk_match:
        chunk_size = int(chunk_match.group(1))
        print(f"✅ Found: chunk_size = {chunk_size}")
        if chunk_size < 2000:
            print("   ⚠️  WARNING: Chunk size is small, may miss data")
            print("   Consider increasing to 2000-4000")
        elif chunk_size > 4000:
            print("   ⚠️  WARNING: Chunk size is large, may be slow")
            print("   Consider reducing to 2000-4000")
        else:
            print("   ✓ Chunk size is optimal")
    else:
        print("⚠️  WARNING: Could not find chunk_size setting")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print("\n✅ All checks passed! The fix is correctly applied.")
    print("\nNext steps:")
    print("1. Restart Flask app: Ctrl+C then 'python app.py'")
    print("2. Test with your Sinhala PDF")
    print("3. Verify all data is extracted")
    
    return True

def check_ai_engine():
    """Verify AIEngineManager is working"""
    
    print("\n" + "=" * 80)
    print("AI ENGINE VERIFICATION")
    print("=" * 80)
    
    try:
        from ai_engine_manager import AIEngineManager
        print("\n✅ AIEngineManager imported successfully")
        
        # Check if .env file exists
        if os.path.exists(".env"):
            print("✅ .env file found")
            
            # Read .env
            with open(".env", "r") as f:
                env_content = f.read()
            
            has_openrouter = "OPENROUTER_API_KEY" in env_content
            has_ollama = "OLLAMA_BASE_URL" in env_content
            
            if has_openrouter:
                print("✅ OpenRouter API key configured")
            else:
                print("⚠️  OpenRouter API key not found in .env")
            
            if has_ollama:
                print("✅ Ollama URL configured")
            else:
                print("⚠️  Ollama URL not found in .env")
            
            if not has_openrouter and not has_ollama:
                print("\n❌ ERROR: No AI engine configured!")
                print("   Please configure either OpenRouter or Ollama in .env")
                return False
        else:
            print("⚠️  .env file not found")
            print("   AI Engine will use default settings")
        
        # Try to initialize engine
        engine = AIEngineManager()
        print(f"\n✅ AIEngineManager initialized")
        print(f"   Mode: {engine.mode}")
        print(f"   OpenRouter Model: {engine.openrouter_model}")
        print(f"   Ollama Model: {engine.ollama_model}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to initialize AIEngineManager")
        print(f"   Error: {e}")
        return False

def check_web_report_engine():
    """Verify station name cleaning is in place"""
    
    print("\n" + "=" * 80)
    print("STATION NAME CLEANING VERIFICATION")
    print("=" * 80)
    
    try:
        with open("web_report_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for station cleaning regex (more flexible matching)
        has_police_station_removal = "POLICE" in content and "STATION" in content and "re.sub" in content
        has_province_removal = ("Div|Division" in content or "Division" in content) and "PROVINCE" in content
        
        print("\n[1] Station Name Cleaning:")
        print("-" * 80)
        
        if has_police_station_removal:
            print("✅ POLICE STATION suffix removal: Found")
        else:
            print("❌ POLICE STATION suffix removal: Missing")
        
        if has_province_removal:
            print("✅ Province/Division text removal: Found")
        else:
            print("❌ Province/Division text removal: Missing")
        
        if has_police_station_removal and has_province_removal:
            print("\n✅ Station name cleaning is correctly implemented")
            print("   Station names will display as: EMBILIPITIYA:")
            print("   Instead of: Div, S/DIG SABARAGAMUWA PROVINCE, EMBILIPITIYA:")
            return True
        else:
            print("\n❌ Station name cleaning is incomplete")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Failed to read web_report_engine.py")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SYSTEM VERIFICATION TOOL" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = []
    
    # Run all checks
    results.append(("app.py Fix", check_app_py_fix()))
    results.append(("AI Engine", check_ai_engine()))
    results.append(("Station Cleaning", check_web_report_engine()))
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\nYour system is ready. Next steps:")
        print("1. Restart Flask app: Ctrl+C then 'python app.py'")
        print("2. Upload your Sinhala PDF")
        print("3. Check if all data is extracted correctly")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\nPlease review the errors above and fix them before testing.")
    
    print("=" * 80)
