# ස්වයංක්‍රීය යන්ත්‍රය නිවැරදි කිරීම - මාර්ගෝපදේශය

## ගැටලුව
Auto Engine එකෙන් Sinhala PDF එකෙන් සියලු විස්තර extract වෙන්නේ නැහැ. නම්, වයස්, ලිපිනය, දුරකථන අංක, ප්‍රමාණ, reference codes වගේ විස්තර නැති වෙනවා.

## හේතුව හොයාගත්තා
**CRITICAL BUG**: `app.py` file එකේ වැරදි API method එකක් call කරලා තිබුණා. Translation fail වෙනවා නමුත් error එකක් පෙන්නන්නේ නැහැ.

## නිවැරදි කළා
✅ `app.py` file එකේ bug එක fix කළා
✅ Translation prompt එක දැනටමත් හොඳයි (සියලු data extract කරන්න කියලා තියෙනවා)

## ඔබ කළ යුතු දේ

### 1. Flask App එක Restart කරන්න (අනිවාර්යයි!)

```bash
# දැනට run වෙන app එක නවත්වන්න:
Ctrl+C

# නැවත start කරන්න:
python app.py
```

⚠️ **වැදගත්**: Restart නොකළොත් fix එක work කරන්නේ නැහැ!

### 2. Test කරන්න (Optional)

Translation හොඳින් work කරනවාද බලන්න:

```bash
python test_translation_accuracy.py
```

මේකෙන්:
- AI Engine connection test කරයි
- Sample Sinhala text එකක් translate කරයි
- සියලු data extract වුණාද බලයි (නම්, වයස්, ලිපිනය, etc.)
- Accuracy score එක පෙන්වයි

### 3. ඔබේ PDF එක Test කරන්න

1. Browser එකේ open කරන්න: `http://localhost:5000`
2. "Auto Engine" tab එකට යන්න
3. ඔබේ Sinhala PDF එක upload කරන්න: `2026-03-21 - - -.pdf`
4. "Start DeepSea Automatic Engine" click කරන්න
5. Processing complete වෙනකම් wait කරන්න
6. Reports download කරලා check කරන්න

### 4. Results Verify කරන්න

Generated English report එක original Sinhala PDF එක සමඟ compare කරලා check කරන්න:

✓ සියලු නම් තියෙනවාද (Rev./Mr./Mrs./Miss සමඟ)
✓ සියලු වයස් exact numbers තියෙනවාද
✓ සියලු ලිපින house numbers සමඟ තියෙනවාද (# XX format)
✓ සියලු දුරකථන අංක තියෙනවාද
✓ සියලු මුදල් තියෙනවාද (Rs. X/= format)
✓ සියලු ප්‍රමාණ units සමඟ තියෙනවාද (X sovereigns, Xg, X items)
✓ සියලු වාහන අංක තියෙනවාද
✓ සියලු reference codes තියෙනවාද (CTM.XXX or OTM.XXX)
✓ දිනය සහ වේලාව exact තියෙනවාද
✓ ස්ථාන සම්පූර්ණයි ද
✓ Investigation status තියෙනවාද

## තවමත් Data නැති වෙනවා නම්

Fix එකෙන් පස්සේ තවමත් data නැති වෙනවා නම්, මේ adjustments කරන්න:

### විකල්පය 1: Chunk Size වැඩි කරන්න

`app.py` file එකේ line ~456:
```python
chunk_size = 2000  # මේක 3000 හෝ 4000 දක්වා වැඩි කරන්න
```

### විකල්පය 2: Manual Workspace භාවිතා කරන්න

Auto Engine තවමත් issues තියෙනවා නම්:

1. "Manual Workspace" tab එකට යන්න
2. PDF upload කරන්න
3. Report type select කරන්න (General හෝ Security)
4. "Split & Generate" click කරන්න
5. එක් එක් section prompt එක copy කරලා ChatGPT එකට දාන්න
6. ChatGPT results paste කරන්න
7. "Assemble Final Official English PDF" click කරන්න

## Station Names ගැන

Station names දැනටමත් clean කරනවා:
- ❌ පරණ format: `Div, S/DIG SABARAGAMUWA PROVINCE, EMBILIPITIYA:`
- ✅ නව format: `EMBILIPITIYA:`

මේක `web_report_engine.py` file එකේ දැනටමත් fix කරලා තියෙනවා.

## සාරාංශය

### කළ දේ:
✅ `app.py` file එකේ critical bug එක fix කළා
✅ Translation prompt එක දැනටමත් හොඳයි
✅ Station name cleaning දැනටමත් work කරනවා
✅ Test script එකක් හදලා තියෙනවා

### කළ යුතු දේ:
1. ⏳ Flask app restart කරන්න (Ctrl+C then python app.py)
2. ⏳ ඔබේ PDF එක test කරන්න
3. ⏳ Results verify කරන්න
4. ⏳ ප්‍රතිඵල report කරන්න

---

## උදව් අවශ්‍ය නම්

ඔබට තවමත් ගැටලු තියෙනවා නම්:
1. Test script එක run කරලා results පෙන්වන්න
2. Generated report එකේ screenshot එකක් දාන්න
3. Original PDF එකේ screenshot එකක් දාන්න
4. මොනවා නැති වුණාද කියන්න

**දිනය**: 2026-03-28
**තත්වය**: Fix Applied - Testing Required
