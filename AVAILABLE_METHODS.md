"""
ai_engine_manager.py — Method Reference Guide (v3.1.0)
All methods are production-ready and thread-safe.
"""

from ai_engine_manager import get_engine

# ══════════════════════════════════════════════════════════
# 🔹 BASIC AI CALLS
# ══════════════════════════════════════════════════════════

engine = get_engine(mode="auto")  # "fast" | "triple" | "consensus"

# ✅ Simple AI call (auto round-robin through available engines)
result = engine.call_ai("Translate: පොලිස් වාර්තාව")
print(f"Response: {result}")

# ✅ With specific engines only (restrict which providers to use)
result = engine.call_ai(
    "Translate this text",
    restricted_list=["ollama", "github", "gemini"]  # Only these 3
)

# ✅ With custom timeout (seconds)
result = engine.call_ai(
    "Long translation task",
    timeout=120  # 120 seconds max wait
)

# ✅ With custom system prompt
result = engine.call_ai(
    "Translate to English",
    system_prompt="You are a professional Sri Lanka Police translator. Use institutional terminology."
)

# ✅ With model override (force specific model)
result = engine.call_ai(
    "Translate this",
    restricted_list=["ollama:llama3"]  # Force llama3 model
)

# ✅ With category context (for police terminology)
result = engine.call_ai(
    "Extract incident details",
    category_context="04. මිනීමැරීම"  # Helps AI use correct terminology
)

# ✅ With task_type for optimal model selection
result = engine.call_ai(
    "Extract JSON with station, date, description",
    task_type="json_extract"  # Uses gpt-4o-mini for strict JSON
)


# ══════════════════════════════════════════════════════════
# 🔹 CONSENSUS & PARALLEL MODES
# ══════════════════════════════════════════════════════════

# ✅ Consensus mode: Ollama primary + cloud validator
engine.mode = "consensus"
result = engine.call_ai("Important translation")
# Returns most reliable response after cross-validation

# ✅ Parallel mode: Call all engines simultaneously, take first winner
results = engine.call_parallel("Test prompt")
# Returns dict: {"ollama": "...", "gemini": "...", "github": "..."}

# ✅ Race dispatch (configured via .env: AI_DISPATCH_MODE=race)
# Automatically returns first successful response from any engine


# ══════════════════════════════════════════════════════════
# 🔹 OLLAMA-SPECIFIC METHODS
# ══════════════════════════════════════════════════════════

# ✅ Get all installed Ollama models (with 60s cache)
models = engine.get_installed_ollama_models()
print(f"Available: {models}")  # ['llama3', 'gemma', 'qwen', ...]

# ✅ Get next model in round-robin rotation
next_model = engine.get_next_ollama_model()
print(f"Next: {next_model}")

# ✅ Set specific Ollama model
engine.set_ollama_model("llama3")

# ✅ Update Ollama URL (switch between local/Kaggle)
engine.set_ollama_preference(
    prefer_kaggle=False,  # Use local
    url="http://localhost:11434/api/generate",
    model="sri-lanka-police-ai"
)

# ✅ Ollama consensus: Try all installed models
result = engine.call_ollama_consensus(
    "Translate this",
    fast_mode=False  # Try all models until one succeeds
)

# ✅ Ollama fast mode: Single model rotation
result = engine.call_ollama_consensus(
    "Quick translation",
    fast_mode=True  # Use only next model in rotation
)


# ══════════════════════════════════════════════════════════
# 🔹 ENGINE HEALTH & MONITORING
# ══════════════════════════════════════════════════════════

# ✅ Check which engines are offline
print(f"Offline engines: {engine.offline_engines}")  # {'gemini', 'github'}

# ✅ Check failure counts per engine
print(f"Failure counts: {engine.failure_counts}")  # {'gemini': 3, 'github': 2}

# ✅ Reset all engines to online state
engine.offline_engines.clear()
engine.failure_counts.clear()
engine.ollama_round_robin_index = 0

# ✅ View usage statistics
print(f"Stats: {engine.stats}")
# {'ollama_calls': 45, 'github_calls': 12, 'gemini_calls': 8, ...}

# ✅ Check last successfully used engine
print(f"Last engine: {engine.last_engine_used}")  # 'ollama:llama3'

# ✅ Check if fallback to Ollama is active
if engine.fallback_active:
    print("⚠️ Using Ollama fallback mode")


# ══════════════════════════════════════════════════════════
# 🔹 SPECIALIZED PIPELINES
# ══════════════════════════════════════════════════════════

# ✅ Triple refinement: Gemini → Ollama → JSON validation
result = engine.triple_refine_pipeline(
    sinhala_text="කොළඹ පොලිසිය, සැකකරුවෙකු අත්අඩංගුවට",
    timeout=120
)
# Returns validated JSON with institutional formatting

# ✅ Fast refinement: Single-call with GitHub/gpt-4o-mini
result = engine.fast_refine(
    text="Raw extracted text",
    system_prompt="Format as police report JSON"
)

# ✅ Validation mode: Primary + validator cross-check
result = engine.call_with_validation(
    prompt="Critical translation",
    system_prompt="Maximum accuracy mode",
    timeout=180
)


# ══════════════════════════════════════════════════════════
# 🔹 ERROR HANDLING PATTERNS
# ══════════════════════════════════════════════════════════

result = engine.call_ai("Translate this")

if result.startswith("❌"):
    # Handle failure
    print(f"Error: {result}")
    
    # Check which engines failed
    print(f"Offline: {engine.offline_engines}")
    
    # Optional: Reset and retry
    engine.offline_engines.clear()
    engine.failure_counts.clear()
    result = engine.call_ai("Translate this")  # Retry
else:
    # Success - process result
    print(f"✅ Success: {result[:100]}...")


# ══════════════════════════════════════════════════════════
# 🔹 BATCH PROCESSING EXAMPLE
# ══════════════════════════════════════════════════════════

def batch_translate(texts: list, task_type: str = "translation"):
    """Process multiple texts with automatic engine rotation."""
    results = []
    
    for i, text in enumerate(texts):
        print(f"[{i+1}/{len(texts)}] Processing...")
        
        result = engine.call_ai(
            text,
            task_type=task_type,
            timeout=60
        )
        
        if result.startswith("❌"):
            print(f"  ⚠️ Failed: {result}")
            results.append(None)
        else:
            results.append(result)
            print(f"  ✅ Success")
        
        # Small delay to avoid rate limits
        time.sleep(0.5)
    
    return results

# Usage
texts = ["පොලිස් වාර්තාව 1", "පොලිස් වාර්තාව 2", "පොලිස් වාර්තාව 3"]
results = batch_translate(texts)


"""
desktop_pipeline.py — PDF Processing Reference
"""

from desktop_pipeline import (
    process_pdf_hyper_hybrid,
    process_pdf_parallel,
    process_pdf_sequentially,
    process_text_report,
    process_image_report,
    _fix_date_format_in_text,
    _ordinal,
    match_province
)


# ══════════════════════════════════════════════════════════
# 🔹 MAIN PDF PROCESSING
# ══════════════════════════════════════════════════════════

# ✅ Hyper-hybrid mode (fastest, round-robin AI)
def progress_callback(category_num: str, data: dict):
    """Optional: Track processing progress."""
    print(f"📁 Category {category_num}: {data.get('count', 0)} incidents")

result = process_pdf_hyper_hybrid(
    pdf_path="report.pdf",
    progress_callback=progress_callback,  # Optional
    output_folder="outputs"  # Where to save generated reports
)

# Check result
if result.get("success"):
    print(f"✅ Generated: {result['generated_pdfs']}")
    print(f"📊 Categories: {result['category_results']['table_counts']}")
else:
    print(f"❌ Failed: {result.get('error')}")


# ✅ Parallel mode (all categories processed simultaneously)
result = process_pdf_parallel(
    pdf_path="report.pdf",
    progress_callback=progress_callback
)

# ✅ Sequential mode (one category at a time, more stable)
result = process_pdf_sequentially(
    pdf_path="report.pdf",
    progress_callback=progress_callback
)


# ══════════════════════════════════════════════════════════
# 🔹 TEXT & IMAGE PROCESSING
# ══════════════════════════════════════════════════════════

# ✅ Process raw Sinhala text directly
result = process_text_report(
    sinhala_text="කොළඹ පොලිසිය, 2024.01.15...",
    output_folder="outputs"
)

# ✅ Process scanned image (OCR + translation)
result = process_image_report(
    image_path="scanned_report.jpg",
    output_folder="outputs"
)


# ══════════════════════════════════════════════════════════
# 🔹 UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════

# ✅ Fix date format: "2026.03.20" → "20th March 2026"
text = "Date: 2026.03.20 පැය 0400"
fixed = _fix_date_format_in_text(text)
print(fixed)  # "Date: 20th March 2026 පැය 0400"

# ✅ Get ordinal suffix
print(_ordinal(1))    # "1st"
print(_ordinal(2))    # "2nd"
print(_ordinal(3))    # "3rd"
print(_ordinal(11))   # "11th"
print(_ordinal(21))   # "21st"

# ✅ Match province variations to official name
province = match_province("N. WESTERN")     # "NORTH WESTERN"
province = match_province("WAYAMBA")        # "NORTH WESTERN"
province = match_province("Western")        # "WESTERN PROVINCE"
province = match_province("උතුරු මැද")      # "NORTH CENTRAL PROVINCE"


"""
gemini_pdf_processor.py — Gemini PDF Processing Reference
"""

from gemini_pdf_processor import GeminiPDFProcessor

processor = GeminiPDFProcessor(api_key="your_key_here")  # Or uses env var


# ══════════════════════════════════════════════════════════
# 🔹 BASIC PDF OPERATIONS
# ══════════════════════════════════════════════════════════

# ✅ Extract text from PDF
text = processor.extract_text("report.pdf", language='sinhala')
print(f"Extracted {len(text)} characters")

# ✅ Summarize PDF content
summary = processor.summarize("report.pdf", language='english', max_tokens=500)
print(f"Summary: {summary}")

# ✅ Translate PDF to Sinhala
sinhala = processor.translate_to_sinhala("english_report.pdf")

# ✅ Translate PDF to English
english = processor.translate_to_english("sinhala_report.pdf")

# ✅ Extract tables as structured data
tables = processor.extract_tables("report.pdf")
for table in tables:
    print(f"Table: {table['headers']}")
    print(f"Rows: {len(table['rows'])}")


# ══════════════════════════════════════════════════════════
# 🔹 Q&A & CUSTOM PROMPTS
# ══════════════════════════════════════════════════════════

# ✅ Answer specific questions about the PDF
questions = [
    "කවදාද මෙය සිදු වුණේ?",      # When did this happen?
    "කොහේද සිදු වුණේ?",          # Where did it happen?
    "සැකකරුවන් කී දෙනෙක්ද?"     # How many suspects?
]
answers = processor.answer_questions("report.pdf", questions)
for q, a in zip(questions, answers):
    print(f"Q: {q}\nA: {a}\n")

# ✅ Custom prompt processing
result = processor.process_pdf(
    pdf_path="report.pdf",
    prompt="Extract all incident details as JSON with fields: station, date, time, description",
    language='english',
    require_json=True  # Force JSON output
)

# ✅ Police report structured extraction
data = processor.extract_police_report_data("report.pdf")
print(f"Categories: {list(data.get('categories', {}).keys())}")
print(f"Total incidents: {data.get('metadata', {}).get('total_incidents')}")


"""
police_desktop_ui.py — Desktop UI Automation Reference
"""

from police_desktop_ui import PoliceDesktopApp

# ✅ Create and control app programmatically
app = PoliceDesktopApp()

# Set PDF to process
app.current_pdf = "path/to/report.pdf"
app.file_label.configure(text="report.pdf")  # Update UI

# Start processing
app.start_processing()

# Monitor progress (optional callback)
def on_progress(category: str, count: int):
    print(f"📁 {category}: {count} incidents")
    app.progress_var.set(count)  # Update progress bar

# Reset AI health (clear offline engines)
app.reset_ai_health()

# Update Ollama connection status
app.update_ollama_status()

# Copy result to clipboard
app.copy_result()

# Update category display
app._update_cat("01", {
    "count": 5,
    "incidents": [{"station": "Colombo", "body": "Incident details..."}]
})

# Show category details popup
app._show_detail("01")

# Run the app (blocking)
app.mainloop()
"""
api_audit.py — API Health Audit Reference
"""

# ══════════════════════════════════════════════════════════
# 🔹 COMMAND LINE USAGE
# ══════════════════════════════════════════════════════════

# Test all configured keys
# python api_audit.py

# Test specific providers only
# python api_audit.py -p gemini github

# Custom timeout (for slow connections)
# python api_audit.py -t 30

# Custom output file
# python api_audit.py -o outputs/audit_2024.json

# Quiet mode (summary only)
# python api_audit.py -q


# ══════════════════════════════════════════════════════════
# 🔹 PROGRAMMATIC USAGE
# ══════════════════════════════════════════════════════════

from api_audit import run_audit

# Run full audit
results = run_audit(
    providers=None,           # None = test all, or ["gemini", "github"]
    timeout=15,               # Seconds per request
    output_file="audit_results.json"
)

# Check results
for provider in ["Gemini", "GitHub"]:
    if results.get(provider):
        active = sum(1 for s in results[provider].values() if "Active" in s)
        total = len(results[provider])
        print(f"{provider}: {active}/{total} keys working")

# Sample result structure:
# {
#   "Gemini": {
#     "Gemini_1": "✅ Active",
#     "Gemini_2": "🔴 Rate Limited"
#   },
#   "GitHub": {
#     "GitHub_Prod": "✅ Active",
#     "GitHub_Dev": "❌ Invalid Key"
#   }
# }
# ══════════════════════════════════════════════════════════
# 🔹 DATE & TEXT UTILITIES
# ══════════════════════════════════════════════════════════

from desktop_pipeline import _fix_date_format_in_text, _ordinal, match_province

# Date formatting
print(_fix_date_format_in_text("2026.03.20"))  # "20th March 2026"
print(_fix_date_format_in_text("2026.01.01"))  # "1st January 2026"

# Ordinal numbers
for i in [1, 2, 3, 11, 21, 22, 23, 31]:
    print(f"{i} → {i}{_ordinal(i)}")

# Province matching (case-insensitive, alias-aware)
aliases = [
    "WESTERN", "Western", "western province",
    "N. WESTERN", "WAYAMBA", "North Western",
    "උතුරු මැද", "NORTH CENTRAL", "North Central"
]
for alias in aliases:
    official = match_province(alias)
    print(f"{alias:20} → {official}")


# ══════════════════════════════════════════════════════════
# 🔹 STATION MAPPING UTILITIES
# ══════════════════════════════════════════════════════════

from station_mapping import get_station_info, SINHALA_TO_ENGLISH

# Get station hierarchy
info = get_station_info("Colombo")
print(f"Province: {info['province']}")
print(f"DIG: {info['dig']}")
print(f"Division: {info['div']}")

# Sinhala → English station name
sinhala_name = "කොළඹ"
english_name = SINHALA_TO_ENGLISH.get(sinhala_name, sinhala_name)
print(f"{sinhala_name} → {english_name}")  # කොළඹ → Colombo

# 1. Import and initialize
from ai_engine_manager import get_engine
engine = get_engine()

# 2. Simple translation
result = engine.call_ai("පොලිස් වාර්තාව", task_type="translation")

# 3. JSON extraction
result = engine.call_ai(
    "Extract: station, date, description",
    task_type="json_extract"
)

# 4. Process PDF
from desktop_pipeline import process_pdf_hyper_hybrid
result = process_pdf_hyper_hybrid("report.pdf", output_folder="outputs")

# 5. Check health
from api_audit import run_audit
audit = run_audit(timeout=10)

# 6. Handle errors
if result.startswith("❌"):
    engine.offline_engines.clear()  # Reset and retry
    result = engine.call_ai("Retry...")