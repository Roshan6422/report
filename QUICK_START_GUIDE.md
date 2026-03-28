# Quick Start Guide - Complete Your Reports

## 🎯 Current Status

**Security Report:** ✅ COMPLETE (3/3 incidents)
**General Report:** ⚠️ PARTIAL (23/71 incidents)

**Missing:** 48 incidents from General Report

---

## 🚀 How to Complete the Reports (FASTEST METHOD)

### Step 1: Launch the Sinhala Data Processor

```bash
python sinhala_data_processor.py interactive
```

### Step 2: Extract Data from PDF

1. Open your official General Report PDF
2. Find the incidents in categories 04-09 (the missing ones)
3. Copy the Sinhala text for each incident
4. Paste into the processor (press Enter twice after pasting)
5. The tool will automatically:
   - Translate Sinhala to English
   - Extract all details (names, ages, addresses, phone numbers, quantities)
   - Categorize into the correct section
   - Show you a summary

### Step 3: Repeat for All Missing Incidents

**Categories to extract (48 incidents total):**
- Category 04: Police Officers/Vehicles (2 incidents)
- Category 05: Dead Bodies (2 incidents)
- Category 06: Police Injuries/Deaths (2 incidents)
- Category 07: Narcotics (14 incidents)
- Category 08: Tri-forces Arrests (4 incidents)
- Category 09: Other Matters (24 incidents)

### Step 4: Generate Complete Reports

When you've pasted all incidents, type:
```
done
```

Then enter:
- Date range: `From 0400 hrs. on 17th March 2026 to 0400 hrs. on 18th March 2026`
- Output prefix: `March17_18_Complete`

The tool will generate:
- `March17_18_Complete_Security.html`
- `March17_18_Complete_Security.pdf`
- `March17_18_Complete_General.html`
- `March17_18_Complete_General.pdf`

---

## ✅ What's Already Working

1. **Province Ordering** - ALL 9 provinces displayed in official order
   - Western, Sabaragamuwa, Southern, Uva, Central, North Western, North Central, Eastern, Northern
   - Empty provinces show "Nil"

2. **Automatic Translation** - Sinhala to English using AI

3. **Automatic Categorization** - Security vs General reports

4. **Data Extraction** - Names, ages, addresses, phone numbers, quantities

5. **Report Generation** - Pixel-perfect formatting matching official samples

---

## 📋 Alternative: Manual Data Entry

If you prefer to enter data manually:

### Option 1: Use the extraction tool
```bash
python complete_data_extraction_tool.py
```

### Option 2: Edit the data file directly
Edit `extract_ALL_march17_18_data.py` and add incidents to the appropriate category lists.

---

## 🔍 Verify Your Reports

After generation, check:
1. ✅ Total incidents: 71 for General, 3 for Security
2. ✅ All 9 provinces displayed in official order
3. ✅ Empty provinces show "Nil"
4. ✅ All names, ages, addresses, phone numbers included
5. ✅ Reference codes (CTM.XXX or OTM.XXX) present
6. ✅ Formatting matches official samples

---

## 💡 Tips for Efficient Extraction

1. **Work by category** - Extract all Category 04 incidents first, then Category 05, etc.

2. **Use the summary table** - The official PDF has a summary table showing incident counts per category

3. **Save frequently** - In the interactive mode, type `save` to save your progress

4. **Check as you go** - Type `summary` to see how many incidents you've processed

5. **Don't worry about categorization** - The tool automatically categorizes incidents based on content

---

## 🆘 If You Need Help

### Commands in Interactive Mode:
- `done` - Finish and generate reports
- `summary` - Show current progress
- `save` - Save data to file
- `load` - Load data from file
- `quit` - Exit without generating reports

### Common Issues:

**Issue:** Translation not working
**Solution:** Check that `ai_engine_manager.py` is configured with valid API keys

**Issue:** Categorization incorrect
**Solution:** The tool uses keywords to categorize. If an incident is miscategorized, you can manually move it in the generated data file

**Issue:** Missing details in output
**Solution:** Make sure you paste the COMPLETE Sinhala text including all names, addresses, and details

---

## 📊 Expected Output

### Security Report (3 incidents):
- Category 01: Nil
- Category 02: Nil
- Category 03: 3 incidents (Arms/Ammunition)

### General Report (71 incidents):
- Category 01: 7 incidents (Serious Crimes)
- Category 02: 7 incidents (Rape/Abuse)
- Category 03: 9 incidents (Fatal Accidents)
- Category 04: 2 incidents (Police Accidents)
- Category 05: 2 incidents (Dead Bodies)
- Category 06: 2 incidents (Police Injuries)
- Category 07: 14 incidents (Narcotics)
- Category 08: 4 incidents (Tri-forces)
- Category 09: 24 incidents (Other Matters)
- Category 10: 0 incidents (Reserved)

### Province Distribution:
All 9 provinces in official order, with "Nil" for empty ones:
1. Western
2. Sabaragamuwa
3. Southern
4. Uva
5. Central
6. North Western
7. North Central
8. Eastern
9. Northern

---

## 🎉 You're Almost Done!

The system is fully functional and ready to process your data. Just feed it the remaining 48 incidents from your PDF and you'll have complete, pixel-perfect reports!

**Estimated time:** 1-2 hours using the Sinhala Data Processor

**Start now:**
```bash
python sinhala_data_processor.py interactive
```

Good luck! 🚀
