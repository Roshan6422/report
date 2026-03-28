# නිවැරදි දත්ත උකහා ගැනීමේ මාර්ගෝපදේශය
## How to Ensure Accurate Data Extraction Every Time

---

## 🎯 Tool එක හැම වෙලාවෙම නිවැරදිව වැඩ කරන්නේ කෙසේද

### ✅ දැන් Tool එක උකහා ගන්නේ:

1. **පළාත් නම් (Province Names)**
   - DIG District එකෙන් ස්වයංක්‍රීයව හඳුනා ගනී
   - උදාහරණ: DIG Jaffna District → NORTHERN Province

2. **පොලිස් ස්ථාන නම් (Police Station Names)**
   - සිංහලෙන් ඉංග්‍රීසියට නිවැරදිව පරිවර්තනය කරයි
   - උදාහරණ: චුන්නාකම් → CHUNNAKAM

3. **DIG දිස්ත්‍රික්කය සහ කොට්ඨාසය (DIG District & Division)**
   - පූර්ණ hierarchy එක උකහා ගනී
   - උදාහරණ: ["DIG Jaffna District", "Jaffna Div."]

4. **මිනිසුන්ගේ නම් සහ වයස් (Human Names & Ages)**
   - සියලු නම් (වින්දිතයන්, සැකකරුවන්, පැමිණිලිකරුවන්)
   - සියලු වයස්
   - ලිංගය (male/female)
   - රැකියාව (occupation)

5. **ලිපින (Addresses)**
   - ගෘහ අංක සමඟ (# XX ආකෘතිය)
   - සම්පූර්ණ ලිපිනය

6. **දුරකථන අංක (Phone Numbers)**
   - XXX-XXXXXXX ආකෘතිය
   - උදාහරණ: 077-5692523

7. **ප්‍රමාණ සහ වටිනාකම් (Quantities & Values)**
   - මුදල්: Rs. X/= ආකෘතිය
   - රන්: X sovereigns
   - බර: Xg, Xkg
   - වාහන අංක

8. **යොමු කේත (Reference Codes)**
   - CTM.XXX හෝ OTM.XXX

---

## 📝 නිවැරදි ආදානය සඳහා උපදෙස්

### 1. සම්පූර්ණ පෙළ අලවන්න (Paste Complete Text)

✅ **හරි:**
```
චුන්නාකම් පොලිස් ස්ථානයට රන් ආභරණ (05 sovereign) රු. 1,975,000/= වටිනා 
සොරකම් සිද්ධියක් වාර්තා විය. සිද්ධිය 2026 මාර්තු 17 වන දින 0430 පැය සිට 
0500 පැය අතර # 18/48, ඉඳුවිල් බටහිර, ඉඳුවිල්, චුන්නාකම් හිදී සිදුවිය. 
පැමිණිලිකරු S. Sarwalogeshwari, වයස 45, (දු.ක. 077-5692523). සැකකරු: නොදනී. 
සොරකම් කළ ආභරණ සොයා නොගත් අතර පරීක්ෂණ ක්‍රියාත්මකයි. චේතනාව: නීති විරෝධී 
ලාභය සඳහා. (CTM.524) DIG යාපනය දිස්ත්‍රික්කය, යාපනය කොට්ඨාසය.
```

❌ **වැරදි:**
```
චුන්නාකම් - රන් සොරකම්
```

### 2. සියලු විස්තර ඇතුළත් කරන්න (Include All Details)

Tool එක සොයන්නේ:
- ✅ නම් (සියලු පුද්ගලයින්)
- ✅ වයස් (සියලු පුද්ගලයින්)
- ✅ ලිපින (ගෘහ අංක සමඟ)
- ✅ දුරකථන අංක
- ✅ ප්‍රමාණ (මුදල්, බර, ගණන)
- ✅ වාහන අංක
- ✅ දිනය සහ වේලාව
- ✅ යොමු කේතය (CTM/OTM)
- ✅ DIG දිස්ත්‍රික්කය සහ කොට්ඨාසය

### 3. ප්‍රතිදානය පරීක්ෂා කරන්න (Check Output)

Tool එක පෙන්වනු ඇත:

```
📊 Data Quality Score: 85/100

✅ Added to GENERAL REPORT

📋 Extracted Details:
   Station: CHUNNAKAM
   Type: theft
   Province: NORTHERN
   Hierarchy: DIG Jaffna District → Jaffna Div.
   Reference: CTM.524

👥 Persons Extracted (1):
   • S. Sarwalogeshwari (Age: 45, Role: complainant)

💰 Values Extracted:
   • Cash: Rs. 1,975,000/=
   • Items: 05 sovereigns of gold jewellery
```

### 4. Data Quality Score අර්ථ දැක්වීම

- **90-100:** ඉතා හොඳයි! සියලු දත්ත නිවැරදිව උකහා ගත්තා
- **70-89:** හොඳයි! බොහෝ දත්ත නිවැරදියි
- **50-69:** සාමාන්‍යයි - සමහර දත්ත අතුරුදහන් විය හැක
- **< 50:** දුර්වලයි - බොහෝ දත්ත අතුරුදහන්

### 5. Warnings සහ Errors

⚠️ **Warnings** (අනතුරු ඇඟවීම්):
```
⚠️  WARNINGS (2):
   • Body text missing phone number
   • No persons extracted
```
→ මේවා නිවැරදි කරන්න පෙළ නැවත අලවන්න

❌ **Errors** (දෝෂ):
```
❌ ERRORS (1):
   • Invalid province: UNKNOWN
```
→ මේවා නිවැරදි කළ යුතුයි

---

## 🗺️ පළාත් හඳුනා ගැනීම (Province Identification)

Tool එක DIG District එකෙන් ස්වයංක්‍රීයව පළාත හඳුනා ගනී:

| DIG District | Province |
|--------------|----------|
| DIG Colombo/Gampaha/Kalutara District | WESTERN |
| DIG Kegalle/Ratnapura District | SABARAGAMUWA |
| DIG Galle/Matara/Hambantota District | SOUTHERN |
| DIG Badulla/Monaragala District | UVA |
| DIG Kandy/Matale/Nuwara-Eliya District | CENTRAL |
| DIG Kurunegala/Puttalam District | NORTH WESTERN |
| DIG Anuradhapura/Polonnaruwa District | NORTH CENTRAL |
| DIG Ampara/Batticaloa/Trincomalee District | EASTERN |
| DIG Jaffna/Kilinochchi/Mannar/Mullaitivu/Vavuniya/Wanni District | NORTHERN |

---

## 💡 උදාහරණ: සම්පූර්ණ සිද්ධියක්

### ආදානය (Input):
```
චුන්නාකම් පොලිස් ස්ථානයට රන් ආභරණ (05 sovereign) රු. 1,975,000/= වටිනා 
සොරකම් සිද්ධියක් වාර්තා විය. සිද්ධිය 2026 මාර්තු 17 වන දින 0430 පැය සිට 
0500 පැය අතර # 18/48, ඉඳුවිල් බටහිර, ඉඳුවිල්, චුන්නාකම් හිදී සිදුවිය. 
පැමිණිලිකරු S. Sarwalogeshwari, වයස 45, ස්ත්‍රී, (දු.ක. 077-5692523). 
සැකකරු: නොදනී. සොරකම් කළ ආභරණ සොයා නොගත් අතර පරීක්ෂණ ක්‍රියාත්මකයි. 
චේතනාව: නීති විරෝධී ලාභය සඳහා. (CTM.524) 
DIG යාපනය දිස්ත්‍රික්කය, යාපනය කොට්ඨාසය.
```

### ප්‍රතිදානය (Output):
```
📊 Data Quality Score: 95/100

✅ Added to GENERAL REPORT

📋 Extracted Details:
   Station: CHUNNAKAM
   Type: theft
   Province: NORTHERN
   Hierarchy: DIG Jaffna District → Jaffna Div.
   Reference: CTM.524

👥 Persons Extracted (1):
   • S. Sarwalogeshwari (Age: 45, Role: complainant)

💰 Values Extracted:
   • Cash: Rs. 1,975,000/=
   • Items: 05 sovereigns of gold jewellery

📄 Generated Body Text:
A case of a theft of gold jewellery (05 sovereigns) valued Rs. 1,975,000/= 
was reported to the police station. The offence took place on the 17th of 
March 2026 between 0430 hrs and 0500 hrs at # 18/48, Induvil west, Induvil, 
Chunnakam. Complainant named S. Sarwalogeshwari, aged 45, (female), 
(TP 077-5692523). Suspect: Unknown. The stolen jewellery not recovered and 
investigations in process. Motive: For illegal gain. (CTM.524)
```

---

## 🚀 භාවිතා කරන්නේ කෙසේද

### පියවර 1: Tool එක ආරම්භ කරන්න
```bash
python sinhala_data_processor.py interactive
```

### පියවර 2: සිංහල පෙළ අලවන්න
- PDF එකෙන් සම්පූර්ණ සිද්ධිය පිටපත් කරන්න
- Tool එකට අලවන්න
- Enter දෙවරක් ඔබන්න

### පියවර 3: ප්‍රතිදානය පරීක්ෂා කරන්න
- Data Quality Score බලන්න (80+ අවශ්‍යයි)
- Warnings ඇත්නම් නිවැරදි කරන්න
- Errors ඇත්නම් පෙළ නැවත අලවන්න

### පියවර 4: නැවත කරන්න
- සියලු සිද්ධීන් සඳහා නැවත කරන්න
- අතර අතර `summary` ටයිප් කරන්න ප්‍රගතිය බැලීමට
- අතර අතර `save` ටයිප් කරන්න දත්ත සුරැකීමට

### පියවර 5: වාර්තා ජනනය කරන්න
- සියල්ල අවසන් වූ පසු `done` ටයිප් කරන්න
- දින පරාසය ඇතුළත් කරන්න
- Tool එක ස්වයංක්‍රීයව දෙ වාර්තා ජනනය කරනු ඇත

---

## ✅ සාරාංශය

**Tool එක දැන් නිවැරදිව උකහා ගන්නේ:**
- ✅ පළාත් නම් (Province names)
- ✅ පොලිස් ස්ථාන නම් (Police station names)
- ✅ DIG දිස්ත්‍රික්කය සහ කොට්ඨාසය (DIG District & Division)
- ✅ මිනිසුන්ගේ නම් සහ වයස් (Human names & ages)
- ✅ ලිපින (ගෘහ අංක සමඟ) (Addresses with house numbers)
- ✅ දුරකථන අංක (Phone numbers)
- ✅ ප්‍රමාණ සහ වටිනාකම් (Quantities & values)
- ✅ වාහන අංක (Vehicle numbers)
- ✅ යොමු කේත (Reference codes)

**ඔබ කළ යුතු එකම දෙය:**
1. සම්පූර්ණ සිංහල පෙළ අලවන්න
2. Data Quality Score පරීක්ෂා කරන්න (80+ අවශ්‍යයි)
3. Warnings ඇත්නම් නිවැරදි කරන්න

**Tool එක ස්වයංක්‍රීයව කරනු ඇත:**
- පරිවර්තනය (Translation)
- වර්ගීකරණය (Categorization)
- දත්ත උකහා ගැනීම (Data extraction)
- වලංගු කිරීම (Validation)
- වාර්තා ජනනය (Report generation)

---

## 🎉 ඔබ සූදානම්!

Tool එක සම්පූර්ණයෙන්ම ක්‍රියාත්මකයි. දැන් ආරම්භ කරන්න:

```bash
python sinhala_data_processor.py interactive
```

හැම වෙලාවෙම නිවැරදි දත්ත ලබා ගැනීමට මෙම මාර්ගෝපදේශය අනුගමනය කරන්න! 🚀
