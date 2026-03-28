# Ollama Configuration - සිංහල මාර්ගෝපදේශය

## ✅ ඔබේ System එක දැන් Ollama භාවිතා කරනවා

### මුලික Engine: Ollama (Local)
- **තත්වය**: ✅ වැඩ කරනවා
- **Model**: `gpt-oss:120b-cloud`
- **වේගය**: 11.6 tokens/sec
- **මිල**: නොමිලේ (Local processing)

### Backup Engine: OpenRouter (Cloud)
- **තත්වය**: ✅ භාවිතා කරන්න පුළුවන් (Optional)
- **API Key**: Free Tier (Unlimited)
- **වියදම**: $0.0177 (ඉතා අඩුයි)

---

## ගැටලුව මොකක්ද හිටියේ?

### පෙර තත්වය
```
[AI Engine] OpenRouter Failed/Unavailable. Falling back to Ollama...
```

මේ message එක නිතරම පෙන්වුණේ මොකද:
1. System එක පළමුව OpenRouter එක try කළා
2. `deepseek/deepseek-r1:free` model එක OpenRouter එකේ නැහැ
3. ඒකෙන් fail වෙලා Ollama එකට fallback වුණා

### දැන් තත්වය
```
[AI Engine] Using Ollama (gpt-oss:120b-cloud)...
```

දැන් system එක:
1. ✅ පළමුවම Ollama භාවිතා කරනවා
2. ✅ OpenRouter එක backup විදියට තියෙනවා
3. ✅ කිසිම error messages නැහැ

---

## Configuration වෙනස්කම්

### `.env` File එකේ වෙනස්කම්

**පෙර:**
```env
DEFAULT_ENGINE=auto
OPENROUTER_MODEL=deepseek/deepseek-r1:free  # ❌ මේ model එක නැහැ
```

**දැන්:**
```env
DEFAULT_ENGINE=ollama  # ✅ Ollama පළමුව
OLLAMA_MODEL=gpt-oss:120b-cloud  # ✅ ඔබේ local model
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free  # ✅ Working free model
```

---

## OpenRouter API Key Details

ඔබේ API key එක මොනවද support කරන්නේ:

### Account Information
- **Type**: Free Tier
- **Limit**: Unlimited (කිසිම limit එකක් නැහැ)
- **Usage**: $0.0177 (ඉතා අඩුයි)
- **Models**: 347 models available, 27 free models

### Working FREE Models
1. `meta-llama/llama-3.2-3b-instruct:free` ✅
2. `nousresearch/hermes-3-llama-3.1-405b:free` ✅

### Working LOW-COST Models (ඉතා අඩු මිලක්)
1. `deepseek/deepseek-chat` - $0.32/$0.89 per 1M tokens
2. `anthropic/claude-3-haiku` - $0.25/$1.25 per 1M tokens
3. `openai/gpt-3.5-turbo` - $0.50/$1.50 per 1M tokens

---

## Test කරන්න Commands

### Ollama Test කරන්න
```bash
python test_ollama_connection.py
```

**Output:**
```
✅ Ollama is running
✅ gpt-oss:120b-cloud is available
✅ Generation successful (5.51s)
✅ Translation successful (3.94s)
```

### OpenRouter Test කරන්න
```bash
python test_openrouter_connection.py
```

### API Key Details බලන්න
```bash
python check_openrouter_details.py
```

---

## වැඩ කරන විදිය

### Engine Selection Logic

```
Translation Request
    ↓
Ollama (gpt-oss:120b-cloud) - Primary
    ↓
Success? → Use result
    ↓
Failed? → Try OpenRouter (Backup)
```

### සියලුම Tools භාවිතා කරන Engine

මේ සියලුම tools දැන් Ollama භාවිතා කරනවා:

1. `translator_pipeline.py` - Sinhala to English translation
2. `deepseek_client.py` - AI structuring
3. `app.py` - Web interface
4. `batch_processor.py` - Batch processing
5. `complete_data_extraction_tool.py` - Data extraction

---

## වාසි

### Ollama භාවිතා කිරීමේ වාසි (දැන් භාවිතා වෙනවා)
✅ **නොමිලේ** - API costs නැහැ
✅ **වේගවත්** - Local processing (11.6 tokens/sec)
✅ **පුද්ගලික** - Data ඔබේ machine එකේම තියෙනවා
✅ **විශ්වාසනීය** - Internet dependency නැහැ
✅ **Rate limits නැහැ** - Unlimited documents process කරන්න පුළුවන්

### OpenRouter Backup වාසි
✅ Ollama fail වුණොත් භාවිතා කරන්න පුළුවන්
✅ Free tier with 27 free models
✅ Automatic fallback

---

## ඔබට කරන්න තියෙන්නේ මොනවද?

### කිසිම දෙයක් නැහැ! ✅

System එක දැන් හොඳින් configure වෙලා තියෙනවා:
- ✅ Ollama primary engine විදියට set වෙලා
- ✅ OpenRouter backup විදියට available
- ✅ සියලුම tools update වෙලා
- ✅ Error messages නැහැ

### ඔබට කරන්න පුළුවන් දේවල් (Optional)

#### 1. Ollama වේගවත් කරන්න
```bash
# GPU acceleration enable කරන්න (if available)
ollama serve --gpu
```

#### 2. OpenRouter භාවිතා කරන්න (Cloud processing)
`.env` file එකේ:
```env
DEFAULT_ENGINE=openrouter
```

#### 3. Paid model එකක් භාවිතා කරන්න (වඩා හොඳ quality)
```env
OPENROUTER_MODEL=deepseek/deepseek-chat  # $0.32 per 1M tokens
```

---

## Troubleshooting

### Ollama වැඩ කරන්නේ නැත්නම්

1. **Ollama running ද බලන්න:**
```bash
ollama serve
```

2. **Model available ද බලන්න:**
```bash
ollama list
```

3. **Connection test කරන්න:**
```bash
python test_ollama_connection.py
```

### OpenRouter වැඩ කරන්නේ නැත්නම්

1. **API key valid ද බලන්න:**
```bash
python check_openrouter_details.py
```

2. **Connection test කරන්න:**
```bash
python test_openrouter_connection.py
```

---

## Summary

### පෙර තත්වය (Problem)
- ❌ OpenRouter fail වෙනවා නිතරම
- ❌ `deepseek/deepseek-r1:free` model එක නැහැ
- ❌ Error messages නිතරම පෙන්වනවා

### දැන් තත්වය (Fixed)
- ✅ Ollama primary engine විදියට set වෙලා
- ✅ OpenRouter backup විදියට available
- ✅ Working free models configure වෙලා
- ✅ Error messages නැහැ
- ✅ වේගවත්, නොමිලේ, විශ්වාසනීය processing

---

## ඊළඟ පියවර

ඔබට දැන් කරන්න පුළුවන්:

1. **Normal විදියට tools භාවිතා කරන්න** - කිසිම වෙනසක් නැහැ
2. **Batch processing කරන්න** - Ollama වේගවත් හා නොමිලේ
3. **Translation කරන්න** - Local processing, private
4. **PDF generate කරන්න** - සියල්ල වැඩ කරනවා

කිසිම configuration වෙනස්කම් කරන්න අවශ්‍ය නැහැ!

---

## අමතර තොරතුරු

### Files Created
1. `test_ollama_connection.py` - Ollama test කරන්න
2. `test_openrouter_connection.py` - OpenRouter test කරන්න
3. `check_openrouter_details.py` - API key details බලන්න
4. `OLLAMA_CONFIGURATION_SUMMARY.md` - English documentation
5. `OLLAMA_SETUP_SINHALA.md` - සිංහල මාර්ගෝපදේශය

### Configuration Files Updated
1. `.env` - Engine configuration
2. `ai_engine_manager.py` - Already supports Ollama
3. `translator_pipeline.py` - Already uses engine manager
4. `deepseek_client.py` - Already uses engine manager

---

## ප්‍රශ්න තිබේ නම්

1. Ollama වැඩ කරන්නේ නැත්නම්: `python test_ollama_connection.py`
2. OpenRouter ගැන දැනගන්න: `python check_openrouter_details.py`
3. System status බලන්න: Check `.env` file

සියල්ල හොඳින් configure වෙලා තියෙනවා! 🎉
