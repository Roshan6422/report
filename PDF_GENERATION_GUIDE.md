# PDF Generation Guide

## 🎯 Overview

මේ system එකෙන් ඔයාට පුළුවන්:
1. PDF text එකෙන් data extract කරන්න
2. JSON format එකට save කරන්න  
3. Formatted PDF report එකක් generate කරන්න

## 📦 Files Created

### 1. `complete_data_extraction_tool.py`
- PDF text එකෙන් data extract කරනවා
- All 29 categories process කරනවා
- JSON output එකක් generate කරනවා

### 2. `generate_pdf_from_extraction.py`
- JSON data එකෙන් PDF report එකක් හදනවා
- Formatted, professional looking PDF
- Sinhala text support

### 3. `demo_complete_workflow.py`
- Complete workflow demo
- Text → JSON → PDF
- Example සහිතයි

## 🚀 Quick Start

### Method 1: Complete Workflow (Recommended)

```bash
# Run the complete demo
python demo_complete_workflow.py
```

මේකෙන් generate වෙනවා:
- `demo_extracted_data.json` - Structured data
- `demo_summary.txt` - Text summary
- `demo_report.pdf` - PDF report

### Method 2: Step by Step

#### Step 1: Extract Data

```bash
python complete_data_extraction_tool.py your_report.txt
```

Output:
- `your_report_extracted.json`
- `your_report_summary.txt`

#### Step 2: Generate PDF

```bash
python generate_pdf_from_extraction.py your_report_extracted.json your_report.pdf
```

Output:
- `your_report.pdf`

## 💻 Python API Usage

### Complete Workflow

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor
from generate_pdf_from_extraction import PDFReportGenerator

# Read PDF text
with open('report.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract data
extractor = SinhalaPoliceReportExtractor()
data = extractor.extract_all(text)

# Save JSON
extractor.save_to_json(data, 'output.json')

# Generate PDF
generator = PDFReportGenerator()
generator.generate_pdf('output.json', 'report.pdf')

print("✓ PDF generated successfully!")
```

### Extract Only

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor

extractor = SinhalaPoliceReportExtractor()

# Extract header
header = extractor.extract_header(text)
print(f"Period: {header['report_period']}")

# Extract specific category
cat_02 = extractor.extract_category_data(text, "02")
print(f"Weapons: {cat_02['summary']['total_incidents']} incidents")

# Extract all
data = extractor.extract_all(text)
extractor.save_to_json(data, 'data.json')
```

### Generate PDF Only

```python
from generate_pdf_from_extraction import PDFReportGenerator

generator = PDFReportGenerator()
generator.generate_pdf('input.json', 'output.pdf')
```

## 📊 What Gets Generated

### JSON Structure

```json
{
  "header": {
    "report_title": "දෛනික සිදුවීම් වාර්ථාව",
    "date_range": {
      "start_date": "2026.03.22",
      "start_time": "0400",
      "end_date": "2026.03.23",
      "end_time": "0400"
    }
  },
  "categories": {
    "01": {
      "category_name": "ත්‍රස්තවාදී ක්‍රියාකාරකම",
      "status": "නැත",
      "incidents": []
    },
    "02": {
      "category_name": "අවි ආයුධ සොයා ගැනීම",
      "incidents": [
        {
          "police_station": "ඉගිණියාගල",
          "date": "2026.03.22",
          "time": "1440",
          "location": "හිමිදුරාල ලැල රක්ෂිතය",
          "suspect": {
            "name": "රාජ්කුමාර් ඉන්ද දර්ශන",
            "age": "32",
            "gender": "පුරුෂ"
          }
        }
      ]
    }
  }
}
```

### PDF Report Contains

1. **Title Page**
   - Report title (Sinhala + English)
   - Date range
   - Generation timestamp

2. **Summary Statistics**
   - Total categories
   - Categories with incidents
   - Total incidents

3. **Category Details**
   - Each category with incidents
   - Incident details:
     - Police station
     - Date/time
     - Location
     - Victim info
     - Suspect info
     - Financial loss
     - Status
     - Description

## 🎨 PDF Customization

### Change PDF Style

Edit `generate_pdf_from_extraction.py`:

```python
def setup_styles(self):
    # Change title color
    self.styles.add(ParagraphStyle(
        name='SinhalaTitle',
        fontSize=18,  # Bigger title
        textColor=colors.HexColor('#0066cc'),  # Blue color
        spaceAfter=30
    ))
```

### Add Custom Sections

```python
def generate_pdf(self, json_file, output_pdf):
    # ... existing code ...
    
    # Add custom section
    story.append(Paragraph("Custom Section", self.styles['SinhalaHeading']))
    story.append(Paragraph("Your custom content here", self.styles['SinhalaBody']))
```

### Change Page Size

```python
from reportlab.lib.pagesizes import LETTER, LEGAL

doc = SimpleDocTemplate(
    output_pdf,
    pagesize=LEGAL,  # or LETTER
    # ... other settings ...
)
```

## 🔧 Advanced Usage

### Batch Processing

```python
import glob
from complete_data_extraction_tool import SinhalaPoliceReportExtractor
from generate_pdf_from_extraction import PDFReportGenerator

extractor = SinhalaPoliceReportExtractor()
generator = PDFReportGenerator()

# Process all text files
for txt_file in glob.glob('reports/*.txt'):
    print(f"Processing {txt_file}...")
    
    # Read text
    with open(txt_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extract
    data = extractor.extract_all(text)
    
    # Save JSON
    json_file = txt_file.replace('.txt', '.json')
    extractor.save_to_json(data, json_file)
    
    # Generate PDF
    pdf_file = txt_file.replace('.txt', '.pdf')
    generator.generate_pdf(json_file, pdf_file)
    
    print(f"✓ Generated {pdf_file}")
```

### Filter Categories

```python
# Extract only categories with incidents
data = extractor.extract_all(text)

active_categories = {
    num: cat for num, cat in data['categories'].items()
    if cat.get('status') != 'නැත' and cat['summary']['total_incidents'] > 0
}

# Create filtered data
filtered_data = {
    'header': data['header'],
    'categories': active_categories,
    'metadata': data['metadata']
}

# Save and generate PDF
extractor.save_to_json(filtered_data, 'filtered.json')
generator.generate_pdf('filtered.json', 'filtered.pdf')
```

### Add Statistics Page

```python
def add_statistics_page(self, data, story):
    """Add a statistics summary page"""
    story.append(Paragraph("Statistics Summary", self.styles['SinhalaHeading']))
    
    # Calculate stats
    total_incidents = sum(cat['summary']['total_incidents'] 
                         for cat in data['categories'].values())
    
    stats_text = f"""
    <b>Total Incidents:</b> {total_incidents}<br/>
    <b>Active Categories:</b> {data['metadata']['categories_with_incidents']}<br/>
    <b>Nil Categories:</b> {sum(1 for cat in data['categories'].values() if cat.get('status') == 'නැත')}<br/>
    """
    
    story.append(Paragraph(stats_text, self.styles['SinhalaBody']))
    story.append(PageBreak())
```

## 📝 Examples

### Example 1: Process March 22 Report

```bash
# Extract data
python complete_data_extraction_tool.py march22_report.txt

# Generate PDF
python generate_pdf_from_extraction.py march22_report_extracted.json march22_report.pdf
```

### Example 2: Custom Processing

```python
from complete_data_extraction_tool import SinhalaPoliceReportExtractor
from generate_pdf_from_extraction import PDFReportGenerator

# Read report
with open('march22_report.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract
extractor = SinhalaPoliceReportExtractor()
data = extractor.extract_all(text)

# Add custom metadata
data['metadata']['processed_by'] = 'Your Name'
data['metadata']['notes'] = 'Custom processing'

# Save
extractor.save_to_json(data, 'march22_custom.json')

# Generate PDF
generator = PDFReportGenerator()
generator.generate_pdf('march22_custom.json', 'march22_custom.pdf')
```

### Example 3: Generate Multiple Formats

```python
# Extract once
data = extractor.extract_all(text)

# Save JSON
extractor.save_to_json(data, 'report.json')

# Generate text summary
summary = extractor.generate_summary(data)
with open('report_summary.txt', 'w', encoding='utf-8') as f:
    f.write(summary)

# Generate PDF
generator.generate_pdf('report.json', 'report.pdf')

# Generate CSV (custom)
import csv
with open('report.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Category', 'Incidents', 'Status'])
    for num, cat in data['categories'].items():
        writer.writerow([
            cat['category_name'],
            cat['summary']['total_incidents'],
            cat.get('status', 'Active')
        ])
```

## 🐛 Troubleshooting

### Issue: PDF not generating

```bash
# Install reportlab
pip install reportlab

# Test
python -c "import reportlab; print('OK')"
```

### Issue: Sinhala text not showing

The current version uses default fonts. For better Sinhala support:

1. Download a Sinhala Unicode font (e.g., Noto Sans Sinhala)
2. Register it in the PDF generator:

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Sinhala font
pdfmetrics.registerFont(TTFont('Sinhala', 'NotoSansSinhala.ttf'))

# Use in styles
self.styles.add(ParagraphStyle(
    name='SinhalaBody',
    fontName='Sinhala',
    fontSize=10
))
```

### Issue: Large PDF files

```python
# Reduce image quality if any
# Limit description length
def format_incident(self, incident, number):
    desc = incident.get('description', '')[:200]  # Limit to 200 chars
    # ... rest of code
```

## ✅ Checklist

Before generating PDF:
- [ ] reportlab installed (`pip install reportlab`)
- [ ] JSON file exists and is valid
- [ ] UTF-8 encoding used
- [ ] Sufficient disk space

After generation:
- [ ] PDF file created
- [ ] File size reasonable (< 5MB)
- [ ] Content displays correctly
- [ ] Sinhala text visible

## 🎯 Next Steps

1. Test with your March 22 report
2. Customize PDF styling
3. Add more sections if needed
4. Integrate with your workflow

## 📞 Quick Commands

```bash
# Complete workflow
python demo_complete_workflow.py

# Extract only
python complete_data_extraction_tool.py report.txt

# Generate PDF only
python generate_pdf_from_extraction.py data.json output.pdf

# View generated files
ls -la demo_*
```

## 🎉 Success!

You now have:
- ✅ Data extraction tool
- ✅ PDF generation tool
- ✅ Complete workflow
- ✅ Working examples

Just run `python demo_complete_workflow.py` to see it all in action! 🎊
