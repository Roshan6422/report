# 🛠️ Available Methods - Use කරන්න පුළුවන් විදි

## 1️⃣ AI Engine Manager Methods

### Basic AI Calls

```python
from ai_engine_manager import get_engine

engine = get_engine(mode="auto")

# Simple AI call (auto round-robin)
result = engine.call_ai("Translate: පොලිස් වාර්තාව")

# With specific engines only
result = engine.call_ai(
    "Translate this text",
    restricted_list=["ollama", "github", "gemini"]
)

# With timeout
result = engine.call_ai(
    "Long translation task",
    timeout=120  # 120 seconds
)

# With custom system prompt
result = engine.call_ai(
    "Translate to English",
    system_prompt="You are a professional police translator"
)

# With specific model override
result = engine.call_ai(
    "Translate this",
    restricted_list=["ollama:llama3"]  # Force specific model
)
```

---

### Vision AI (Image/PDF OCR)

```python
# OCR from image
import base64

with open("image.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode("utf-8")

result = engine.call_vision_ai(
    "Extract all Sinhala text from this image",
    img_base64
)

# With JSON response
result = engine.call_vision_ai(
    "Extract data as JSON",
    img_base64,
    require_json=True
)
```

---

### Consensus Mode (Multiple Models)

```python
# Call multiple models and compare
engine.mode = "consensus"
result = engine.call_ai("Important translation")
# Uses Ollama + Cloud validator for accuracy

# Parallel calls to all engines
results = engine.call_parallel("Test prompt")
# Returns: {"ollama": "...", "gemini": "...", "github": "..."}
```

---

### Ollama Specific

```python
# Get all installed models
models = engine.get_installed_ollama_models()
print(models)  # ['llama3', 'gemma', 'qwen', ...]

# Get next model in rotation
next_model = engine.get_next_ollama_model()
print(next_model)  # 'llama3'

# Set specific model
engine.set_ollama_model("llama3")

# Consensus with all Ollama models
result = engine.call_ollama_consensus(
    "Translate this",
    fast_mode=False  # Use all models
)

# Fast mode (single model rotation)
result = engine.call_ollama_consensus(
    "Quick translation",
    fast_mode=True  # Use only next in rotation
)
```

---

### Engine Health Management

```python
# Check offline engines
print(engine.offline_engines)  # {'gemini', 'github'}

# Check failure counts
print(engine.failure_counts)  # {'gemini': 3, 'github': 2}

# Reset all engines to online
engine.offline_engines.clear()
engine.failure_counts.clear()
engine.ollama_round_robin_index = 0

# Check statistics
print(engine.stats)
# {'ollama_calls': 45, 'github_calls': 12, 'gemini_calls': 8, ...}

# Check last used engine
print(engine.last_engine_used)  # 'ollama:llama3'
```

---

## 2️⃣ PDF Processing Methods

### Gemini PDF Processor

```python
from gemini_pdf_processor import GeminiPDFProcessor

processor = GeminiPDFProcessor()

# Extract text
text = processor.extract_text("report.pdf", language='sinhala')

# Summarize
summary = processor.summarize("report.pdf", language='english')

# Translate to Sinhala
sinhala = processor.translate_to_sinhala("report.pdf")

# Translate to English
english = processor.translate_to_english("report.pdf")

# Extract tables
tables = processor.extract_tables("report.pdf")

# Answer questions
questions = ["කවදාද මෙය සිදු වුණේ?", "කොහේද සිදු වුණේ?"]
answers = processor.answer_questions("report.pdf", questions)

# Custom prompt
result = processor.process_pdf(
    "report.pdf",
    "Extract all incident details as JSON",
    language='english'
)

# Extract police report data
data = processor.extract_police_report_data("report.pdf")
```

---

### Desktop Pipeline Methods

```python
from desktop_pipeline import (
    process_pdf_hyper_hybrid,
    process_pdf_parallel,
    process_pdf_sequentially,
    process_text_report,
    process_image_report
)

# Main method (fastest, round-robin)
def progress_callback(cat_num, data):
    print(f"Category {cat_num}: {data['count']} incidents")

result = process_pdf_hyper_hybrid(
    "report.pdf",
    progress_callback=progress_callback,
    output_folder="outputs"
)

# Parallel processing (all categories at once)
result = process_pdf_parallel(
    "report.pdf",
    progress_callback=progress_callback
)

# Sequential processing (one by one)
result = process_pdf_sequentially(
    "report.pdf",
    progress_callback=progress_callback
)

# Process raw text
result = process_text_report(
    "සිංහල text here...",
    output_folder="outputs"
)

# Process image (OCR + translate)
result = process_image_report(
    "scanned_report.jpg",
    output_folder="outputs"
)
```

---

## 3️⃣ UI Methods (Desktop App)

```python
from police_desktop_ui import PoliceDesktopApp

app = PoliceDesktopApp()

# Programmatically select PDF
app.current_pdf = "path/to/report.pdf"
app.file_label.configure(text="report.pdf")

# Start processing
app.start_processing()

# Reset AI health
app.reset_ai_health()

# Update Ollama status
app.update_ollama_status()

# Copy results
app.copy_result()

# Update category display
app._update_cat("01", {"count": 5, "incidents": [...]})

# Show category details
app._show_detail("01")

# Run app
app.mainloop()
```

---

## 4️⃣ Utility Methods

### Date Formatting

```python
from desktop_pipeline import _fix_date_format_in_text, _ordinal

# Convert numeric dates to English
text = "Date: 2026.03.20"
fixed = _fix_date_format_in_text(text)
print(fixed)  # "Date: 20th March 2026"

# Get ordinal
print(_ordinal(1))   # "1st"
print(_ordinal(2))   # "2nd"
print(_ordinal(13))  # "13th"
```

### Province Matching

```python
from desktop_pipeline import match_province

province = match_province("N. WESTERN")
print(province)  # "NORTH WESTERN"

province = match_province("WAYAMBA")
print(province)  # "NORTH WESTERN"
```

---

## 5️⃣ Testing & Monitoring

### Test Round-Robin

```bash
python test_round_robin.py
```

```python
# Or programmatically
from test_round_robin import test_round_robin
test_round_robin()
```

### Show Status

```bash
python show_round_robin_status.py
```

```python
# Or programmatically
from show_round_robin_status import show_status
show_status()
```

---

## 6️⃣ Advanced Usage Examples

### Custom Round-Robin Pool

```python
engine = get_engine()

# Create custom engine pool
custom_pool = ["ollama:llama3", "ollama:gemma", "github"]

# Use in translation
result = engine.call_ai(
    "Translate this",
    restricted_list=custom_pool
)
```

### Batch Processing with Progress

```python
def process_multiple_pdfs(pdf_list):
    results = []
    
    for i, pdf_path in enumerate(pdf_list):
        print(f"Processing {i+1}/{len(pdf_list)}: {pdf_path}")
        
        def progress(cat, data):
            print(f"  Cat {cat}: {data['count']} incidents")
        
        result = process_pdf_hyper_hybrid(
            pdf_path,
            progress_callback=progress
        )
        results.append(result)
    
    return results

# Use it
pdfs = ["report1.pdf", "report2.pdf", "report3.pdf"]
results = process_multiple_pdfs(pdfs)
```

### Error Recovery

```python
engine = get_engine()

# Try with automatic fallback
result = engine.call_ai("Translate this")

if result.startswith("❌"):
    print("All engines failed!")
    
    # Check which engines are offline
    print(f"Offline: {engine.offline_engines}")
    
    # Reset and retry
    engine.offline_engines.clear()
    engine.failure_counts.clear()
    
    result = engine.call_ai("Translate this")
```

### Custom Timeout Strategy

```python
# Short timeout for quick tasks
result = engine.call_ai("Quick task", timeout=30)

# Long timeout for complex tasks
result = engine.call_ai("Complex analysis", timeout=300)

# No timeout (wait forever)
result = engine.call_ai("Very long task", timeout=None)
```

---

## 7️⃣ Configuration

### Environment Variables (.env)

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3
OLLAMA_SINHALA_MODEL=llama3

# Gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash

# GitHub Models
GITHUB_API_KEY=your_key_here
GITHUB_MODEL=gpt-4o-mini
GITHUB_BASE_URL=https://models.inference.ai.azure.com

# OpenRouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=deepseek/deepseek-r1:free

# Default engine mode
DEFAULT_ENGINE=auto  # or "consensus"
```

---

## 8️⃣ Return Formats

### AI Call Result

```python
result = engine.call_ai("Test")
# Returns: String (translation/response)
# Or: "❌ Error message" if failed
```

### PDF Processing Result

```python
result = process_pdf_hyper_hybrid("report.pdf")
# Returns:
{
    "success": True,
    "full_translation": "...",
    "category_results": {
        "01": {"count": 2, "incidents": [...], "raw_incidents": [...]},
        "02": {"count": 0, "incidents": [], "raw_incidents": []},
        ...
        "table_counts": {"01": 2, "02": 0, ...},
        "date_range": "From 0400 hrs. on 12th March 2026..."
    },
    "generated_pdfs": ["outputs/General_Report_20260401.pdf", ...]
}
```

---

## 9️⃣ Best Practices

### ✅ DO:

```python
# Use round-robin for load balancing
result = engine.call_ai("Task")  # Auto round-robin

# Set reasonable timeouts
result = engine.call_ai("Task", timeout=60)

# Check for errors
if result.startswith("❌"):
    handle_error(result)

# Use progress callbacks for long tasks
process_pdf_hyper_hybrid(pdf, progress_callback=my_callback)

# Reset engines when needed
engine.offline_engines.clear()
```

### ❌ DON'T:

```python
# Don't use infinite timeout for user-facing tasks
result = engine.call_ai("Task", timeout=None)  # Bad!

# Don't ignore error messages
result = engine.call_ai("Task")
# Process without checking if result.startswith("❌")

# Don't hammer single engine
for i in range(100):
    engine.call_ai("Task", restricted_list=["ollama:llama3"])  # Bad!
```

---

## 🎯 Summary

**Available Methods:**
- ✅ `call_ai()` - Main AI call with round-robin
- ✅ `call_vision_ai()` - OCR/Image processing
- ✅ `call_parallel()` - Multi-engine consensus
- ✅ `call_ollama_consensus()` - Ollama-specific rotation
- ✅ `get_installed_ollama_models()` - List models
- ✅ `get_next_ollama_model()` - Next in rotation
- ✅ `process_pdf_hyper_hybrid()` - Fast PDF processing
- ✅ `process_pdf_parallel()` - Parallel processing
- ✅ `GeminiPDFProcessor` - Gemini-specific PDF tools

**කිසිම code එකක් වෙනස් කරන්න එපා - මේ methods දැනටමත් තියෙනවා!** 🚀
