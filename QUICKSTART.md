# Quick Start Guide 🚀

Get your Police Report Processing Engine running in 5 minutes!

## Step 1: Verify Installation ✅

```bash
# Run system tests
python test_complete_system.py
```

You should see: `🎉 ALL TESTS PASSED! System is ready for production.`

## Step 2: Start Web Interface 🌐

```bash
python app.py
```

Open browser: **http://localhost:3000**

## Step 3: Process Your First Report 📄

### Option A: Auto Mode (Fastest)

1. Click **"🤖 Auto Engine"** tab
2. Upload a Sinhala PDF
3. Click **"🚀 Start DeepSea Automatic Engine"**
4. Wait 10-30 seconds
5. Download your English PDFs!

### Option B: Manual Mode (ChatGPT Assisted)

1. Click **"📍 Manual Workspace"** tab
2. Upload PDF (appears on left side)
3. Select report type (General/Security)
4. Click **"🧩 Split & Generate"**
5. Click **"🔗 Side ChatGPT"** to open ChatGPT
6. For each section:
   - Click **"Copy Prompt"**
   - Paste into ChatGPT
   - Copy ChatGPT's response
   - Paste back into workspace
7. Click **"🚀 Assemble Final Official English PDF"**
8. Download your reports!

## Step 4: Batch Processing (Multiple PDFs) 📦

```bash
# Place all PDFs in uploads/ folder
# Then run:
python batch_processor.py --input uploads

# With AI enhancement:
python batch_processor.py --input uploads --ai
```

## Common Commands

### Single PDF Processing (CLI)
```bash
# Regex only (fast)
python run_cli.py

# With AI (better quality)
python run_cli.py --ai --engine openrouter
```

### Check API Status
```bash
python test_openrouter.py
```

### View Processing Logs
```bash
# Latest log
ls -lt tmp/processing_logs/ | head -1

# View log content
cat tmp/processing_logs/log_YYYYMMDD_HHMMSS.json
```

## Troubleshooting

### "No module named 'fitz'"
```bash
pip install PyMuPDF
```

### "OpenRouter API Error"
Check your `.env` file has the correct API key:
```env
OPENROUTER_API_KEY=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
```

### "PDF not extracting text"
Try a different PDF or check if it's image-based (requires OCR)

### Web interface not loading
Make sure port 3000 is not in use:
```bash
# Windows
netstat -ano | findstr :3000

# Kill process if needed
taskkill /PID <PID> /F
```

## Output Location

All generated reports are saved to:
```
uploads/sinhala/
├── [filename]_General_Report.html
├── [filename]_General_Report.pdf
├── [filename]_Situation_Report.html
└── [filename]_Situation_Report.pdf
```

## Performance Tips

1. **Use Regex Mode for Daily Processing** - 10x faster, 85-90% accuracy
2. **Use AI Mode for Complex Reports** - Better context understanding
3. **Batch Process at Night** - Process 50+ PDFs while you sleep
4. **Keep PDFs Under 10MB** - Larger files take longer to process

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Customize report templates in `web_report_engine.py`
- Add custom terminology to `translation_vocabulary.py`
- Configure additional AI engines in `.env`

## Support

For issues, check:
1. System tests: `python test_complete_system.py`
2. Processing logs: `tmp/processing_logs/`
3. Error messages in console output

---

**Ready to process reports!** 🎉

System Version: v2.1.0
