"""
setup.py — System Setup and Verification Script
================================================
Automated setup for Police Report Processing Engine
"""

import os
import sys
import subprocess
import json

def print_header(text):
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60)

def check_python_version():
    """Verify Python version is 3.8+"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    dirs = [
        "uploads",
        "uploads/sinhala",
        "uploads/manual",
        "tmp",
        "tmp/cache",
        "tmp/processing_logs",
        "tmp/batch_logs"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✅ {d}")
    
    return True

def check_env_file():
    """Verify .env configuration"""
    print_header("Checking Configuration")
    
    if not os.path.exists(".env"):
        print("⚠️ .env file not found. Creating default...")
        
        default_env = """OPENROUTER_API_KEY=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
OPENROUTER_MODEL=deepseek/deepseek-r1:free
OLLAMA_BASE_URL=http://localhost:11434/api/generate
DEFAULT_ENGINE=auto
"""
        with open(".env", "w") as f:
            f.write(default_env)
        
        print("✅ Created .env with default settings")
    else:
        print("✅ .env file exists")
    
    # Verify API key
    with open(".env", "r") as f:
        env_content = f.read()
    
    if "OPENROUTER_API_KEY" in env_content:
        print("✅ OpenRouter API key configured")
    else:
        print("⚠️ OpenRouter API key not found in .env")
    
    return True

def test_openrouter():
    """Test OpenRouter API connection"""
    print_header("Testing OpenRouter API")
    
    try:
        from openrouter_client import OpenRouterClient
        
        api_key = os.getenv("OPENROUTER_API_KEY", "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")
        client = OpenRouterClient(api_key)
        
        response = client.chat_completion("Say 'API working' in one sentence.", max_tokens=50)
        
        if response and len(response) > 0:
            print("✅ OpenRouter API connection successful")
            return True
        else:
            print("⚠️ OpenRouter API returned empty response")
            return False
            
    except Exception as e:
        print(f"⚠️ OpenRouter API test failed: {e}")
        print("   (System will fallback to Ollama if needed)")
        return False

def check_edge_browser():
    """Check if Microsoft Edge is available for PDF conversion"""
    print_header("Checking PDF Converter")
    
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    
    for path in edge_paths:
        if os.path.exists(path):
            print(f"✅ Microsoft Edge found: {path}")
            return True
    
    print("⚠️ Microsoft Edge not found")
    print("   PDF conversion may not work. Install Edge or configure alternative.")
    return False

def run_system_tests():
    """Run comprehensive system tests"""
    print_header("Running System Tests")
    
    try:
        result = subprocess.run([sys.executable, "test_complete_system.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ All system tests passed")
            return True
        else:
            print("⚠️ Some tests failed. Check output above.")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Tests timed out")
        return False
    except Exception as e:
        print(f"⚠️ Could not run tests: {e}")
        return False

def print_summary(results):
    """Print setup summary"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  SETUP COMPLETE".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    print("\nSetup Results:")
    for task, status in results.items():
        icon = "✅" if status else "⚠️"
        print(f"  {icon} {task}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 System is ready for production!")
        print("\nNext steps:")
        print("  1. Run: python app.py")
        print("  2. Open: http://localhost:3000")
        print("  3. Upload a PDF and start processing!")
    else:
        print("\n⚠️ Setup completed with warnings.")
        print("   System should still work, but some features may be limited.")
        print("\nYou can still:")
        print("  1. Run: python app.py")
        print("  2. Use regex mode (no AI required)")
        print("  3. Process PDFs with offline engine")

def main():
    """Main setup routine"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  POLICE REPORT PROCESSING ENGINE".center(58) + "█")
    print("█" + "  Setup & Verification".center(58) + "█")
    print("█" + "  Version: v2.1.0".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    results = {}
    
    # Run setup steps
    results["Python Version"] = check_python_version()
    results["Dependencies"] = install_dependencies()
    results["Directories"] = create_directories()
    results["Configuration"] = check_env_file()
    results["OpenRouter API"] = test_openrouter()
    results["PDF Converter"] = check_edge_browser()
    results["System Tests"] = run_system_tests()
    
    # Print summary
    print_summary(results)
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
