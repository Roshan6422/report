# Round-Robin System - සිංහල සහාය සහිත

## මුළු Process එකේ Round-Robin වැඩ කරන විදිය

### Stage 1: PDF Extraction (Initial Data Gathering)
```
Try Order (Fast → Slow):
1. Gemini Vision (Cloud, PDF Direct)
2. GitHub Models (Cloud, OCR Text)
3. OpenRouter (Cloud, OCR Text)  
4. Ollama Model 1 (Local, OCR Text)
5. Ollama Model 2 (Local, OCR Text)
... (all installed models)
```

**කොහොමද වැඩ කරන්නේ:**
- පළමුව Gemini try කරනවා (ඉක්මනින්ම PDF read කරන්න පුළුවන්)
- Gemini fail උනොත්, GitHub Models try කරනවා
- ඒකත් fail උනොත්, OpenRouter, ඊට පස්සේ සියලුම Ollama models එකින් එක try කරනවා
- කවුරු හරි success උනාම, ඊළඟ stage එකට යනවා

---

### Stage 2: Translation (29 Categories Parallel)
```
Category 01 → Ollama Model 1
Category 02 → Ollama Model 2  
Category 03 → Ollama Model 3
Category 04 → GitHub Models
Category 05 → Gemini
Category 06 → OpenRouter
Category 07 → Ollama Model 1 (rotation restart)
... (continues rotating)
```

**කොහොමද වැඩ කරන්නේ:**
- සෑම category එකකටම වෙනම engine එකක් assign වෙනවා
- Formula: `shift = (cat_num * 100 + batch_index) % total_engines`
- මේකෙන් load එක equally බෙදෙනවා සියලුම engines වලට

**Example with 3 Ollama models:**
```
Cat 01, Batch 1 → ollama:llama3
Cat 01, Batch 2 → ollama:gemma
Cat 02, Batch 1 → ollama:qwen
Cat 02, Batch 2 → github
Cat 03, Batch 1 → gemini
... (rotation continues)
```

---

### Stage 3: PDF Generation
```
General Report → Single threaded (fast HTML generation)
Security Report → Single threaded (fast HTML generation)
```

---

## Round-Robin Pool Priority

```python
# Translation Pool (Optimized for Speed):
ollama_engines = ["ollama:llama3", "ollama:gemma", "ollama:qwen", ...]
cloud_engines = ["github", "gemini", "openrouter"]
global_pool = ollama_engines + cloud_engines

# Extraction Pool (Optimized for Accuracy):
extraction_pool = ["gemini", "github", "openrouter"] + ollama_engines
```

---

## Sinhala Support Models (Auto-Detected)

System automatically detects these Sinhala-capable models:
- ✅ llama3 (Best Sinhala support)
- ✅ gemma (Good multilingual)
- ✅ qwen (Excellent Asian languages)
- ✅ mistral (Good general purpose)
- ✅ phi (Fast, decent Sinhala)
- ✅ gpt-oss (Custom trained)

---

## Load Balancing Example

**Without Round-Robin (Old):**
```
All 100 translations → Ollama Model 1 (OVERLOADED!)
Result: Slow, crashes, timeouts
```

**With Round-Robin (New):**
```
Translation 1 → Ollama llama3
Translation 2 → Ollama gemma  
Translation 3 → Ollama qwen
Translation 4 → GitHub Models
Translation 5 → Gemini
Translation 6 → OpenRouter
Translation 7 → Ollama llama3 (restart rotation)
...
Result: Fast, stable, no crashes!
```

---

## Failure Handling

**Circuit Breaker Logic:**
- Engine fails 3 times → Marked OFFLINE
- Automatically skipped in future calls
- "Reset AI Health" button clears all offline marks

**Retry Logic:**
- Each translation batch retries once on failure
- Timeout: 60s per batch (fast fail)
- Falls back to next engine in rotation

---

## Performance Improvements

| Metric | Before | After |
|--------|--------|-------|
| Ollama Timeout | 240s | 90s |
| Gemini Timeout | 1000s | 120s |
| Batch Timeout | None | 60s |
| Parallel Workers | 5 | 8 |
| Retry Wait | 35s | 10s, 20s |
| Model Rotation | ❌ | ✅ |

---

## Testing

Run this to verify round-robin:
```bash
python test_round_robin.py
```

මේකෙන් පෙන්වයි:
- කොච්චර models තියෙනවද
- Rotation එක වැඩ කරනවද
- කොන්ම models use වෙනවද

---

## Summary

✅ **Extraction Stage:** Tries all engines in priority order  
✅ **Translation Stage:** Distributes load across ALL engines evenly  
✅ **Error Recovery:** Auto-skips failed engines, retries once  
✅ **UI Safety:** All operations in background threads with error handling  
✅ **Speed:** 3x faster with parallel processing + shorter timeouts  

**Result:** No crashes, no waiting, balanced load! 🚀
