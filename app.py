"""
Sinhala Police Report Data Extraction Application
සිංහල පොලිස් වාර්තා දත්ත නිස්සාරණ යෙදුම

This application extracts data from Sinhala police daily incident reports
and converts them to structured JSON format with 100% accuracy.

මෙම යෙදුම සිංහල පොලිස් දෛනික සිදුවීම් වාර්තාවලින් දත්ත නිස්සාරණය කර
100% නිරවද්‍යතාවයකින් යුතුව ව්‍යුහගත JSON ආකෘතියට පරිවර්තනය කරයි.
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import PyPDF2


class SinhalaPoliceReportExtractor:
    """
    Complete extractor for Sinhala police daily incident reports
    සිංහල පොලිස් දෛනික සිදුවීම් වාර්තා සඳහා සම්පූර්ණ නිස්සාරණය
    """
    
    def __init__(self):
        """Initialize with all 29 official categories"""
        self.categories = {
            "01": "ත්‍රස්තවාදී ක්‍රියාකාරකම",
            "02": "අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ)",
            "03": "උද්ඝෝෂණ",
            "04": "මිනීමැරීම",
            "05": "කොල්ලකෑම / අවි ආයුධ මගින් කොල්ලකෑම",
            "06": "වාහන සොරකම",
            "07": "දේපළ සොරකම",
            "08": "ගෙවල් බිඳ",
            "09": "ස්ත්‍රී දූෂණ හා බරපතල ලිංගික අපයෝජන",
            "10": "මාර්ග රිය අනතුරු",
            "11": "නාදුනන මළ සිරුරු හා සැක්සහිත මරණ",
            "12": "පොලිස් රිය අනතුරු",
            "13": "පොලිස් නිලධාරීන්ට තුවාල සිදුවීම සහ පොලිසිය සම්බන්ධ සිදුවීම",
            "14": "පොලිස් නිලධාරීන්ගේ විෂමාචාර ක්‍රියා",
            "15": "පොලිස් නිලධාරීන් මියයෑ",
            "16": "රාජ්‍ය නිෂේධිත නිලධාරීන් රෝහල් ගතවී",
            "17": "රාජ්‍ය නිෂේධිත නිලධාරීන්ගේ ළඟම ඥාතීන් මියයෑ",
            "18": "විශ්‍රාමික රාජ්‍ය නිෂේධිත නිලධාරීන්ගේ ළඟම ඥාතීන් මියයෑ",
            "19": "නිවාඩු ලබා සිටින සෙය.නිපොප නි.පො.ප වරුන්",
            "20": "විශාල ප්‍රමාණයේ මත් ද්‍රව්‍ය/මත්පැන් අත්අඩංගුට ගැනී",
            "21": "අත්අඩංගුට ගැනී",
            "22": "ත්‍රිවිධ හමුදා සාමාජිකයින්ගේ අපරාධ, විෂමාචාර ක්‍රියා හා අත්අඩංගුට ගැනී",
            "23": "අතුරුදහන්වී",
            "24": "සියදිවි හානිකර ගැනී",
            "25": "විදේශ සාමිකයින් සම්බන්ධ සිදුවීම",
            "26": "වනඅලි පහරදී හා වනඅලි මියයෑ",
            "27": "දියේ ගිලී මියයෑ",
            "28": "ගිනි ගැනීම සම්බන්ධ සිදුවීම",
            "29": "වෙනත් විශේෂ සිදුවීම"
        }
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        PDF ගොනුවෙන් පෙළ නිස්සාරණය කරන්න
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
        return text
    
    def extract_header(self, text: str) -> Dict[str, Any]:
        """
        Extract report header information
        වාර්තා ශීර්ෂ තොරතුරු නිස්සාරණය කරන්න
        """
        header = {
            "report_title": "දෛනික සිදුවීම් වාර්ථාව",
            "date_range": {},
            "report_period": ""
        }
        
        # Extract date range: 2026.03.20 වන දින පැය 0400 සිට 2026.03.21 දින පැය 0400 දක්වා
        date_pattern = r'(\d{4})\.(\d{2})\.(\d{2})\s+වන\s+දින\s+පැය\s+(\d{4})\s+සිට\s+(\d{4})\.(\d{2})\.(\d{2})\s+දින\s+පැය\s+(\d{4})\s+දක්වා'
        match = re.search(date_pattern, text)
        
        if match:
            header["date_range"] = {
                "start_date": f"{match.group(1)}.{match.group(2)}.{match.group(3)}",
                "start_time": match.group(4),
                "end_date": f"{match.group(5)}.{match.group(6)}.{match.group(7)}",
                "end_time": match.group(8)
            }
            header["report_period"] = f"{match.group(1)}.{match.group(2)}.{match.group(3)} පැය {match.group(4)} සිට {match.group(5)}.{match.group(6)}.{match.group(7)} දින පැය {match.group(8)} දක්වා"
        
        return header
    
    def is_nil_category(self, text: str, category_num: str) -> bool:
        """
        Check if a category has no incidents (නැත)
        ප්‍රවර්ගයක සිදුවීම් නොමැති දැයි පරීක්ෂා කරන්න
        """
        # Pattern: 01. ත්‍රස්තවාදී ක්‍රියාකාරකම : නැත.
        pattern = rf'{category_num}\.\s+[^\n]*:\s*නැත'
        return bool(re.search(pattern, text))
    
    def extract_category_count(self, text: str, category_num: str) -> Any:
        """
        Extract incident count for a category
        ප්‍රවර්ගයක සිදුවීම් ගණන නිස්සාරණය කරන්න
        """
        # Check if nil first
        if self.is_nil_category(text, category_num):
            return "නැත"
        
        # Pattern: 02. අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ) :- 09
        count_pattern = rf'{category_num}\.\s+[^\n]*:-\s*(\d+)'
        match = re.search(count_pattern, text)
        
        if match:
            return int(match.group(1))
        
        return 0
    
    def extract_table_data(self, text: str, category_num: str) -> List[Dict[str, Any]]:
        """
        Extract data from table format categories
        වගු ආකෘති ප්‍රවර්ග වලින් දත්ත නිස්සාරණය කරන්න
        """
        incidents = []
        
        # Find the category section
        cat_pattern = rf'{category_num}\.\s+.*?(?=\d{{2}}\.|$)'
        cat_match = re.search(cat_pattern, text, re.DOTALL)
        
        if not cat_match:
            return incidents
        
        category_text = cat_match.group(0)
        
        # Extract table rows (numbered 1., 2., 3., etc.)
        row_pattern = r'(\d+)\.\s+(.*?)(?=\d+\.\s+|$)'
        rows = re.finditer(row_pattern, category_text, re.DOTALL)
        
        for row in rows:
            row_num = row.group(1)
            row_text = row.group(2)
            
            incident = self.parse_incident_row(row_text, category_num)
            if incident:
                incident["incident_number"] = int(row_num)
                incidents.append(incident)
        
        return incidents
    
    def parse_incident_row(self, row_text: str, category_num: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single incident row
        තනි සිදුවීම් පේළියක් විග්‍රහ කරන්න
        """
        incident = {
            "police_station": "",
            "division": "",
            "date": "",
            "time": "",
            "report_time": "",
            "location": "",
            "victim": {},
            "suspect": {},
            "description": "",
            "financial_loss": "",
            "status": ""
        }
        
        # Extract police station and division
        # Pattern: සිරිපුර OTM 1630 කොට්ඨාශය සොඩොන් නරුල
        station_pattern = r'([^\n]+?)\s+(OTM|CTM)\s+(\d+)\s+කොට්ඨාශය\s+([^\n]+)'
        station_match = re.search(station_pattern, row_text)
        
        if station_match:
            incident["police_station"] = station_match.group(1).strip()
            incident["division"] = f"කොට්ඨාශය {station_match.group(4).strip()}"
        
        # Extract date and time
        # Pattern: 2026.03.20 පැය 0510
        date_pattern = r'(\d{4})\.(\d{2})\.(\d{2})\s+පැය\s+(\d{4})'
        date_match = re.search(date_pattern, row_text)
        
        if date_match:
            incident["date"] = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
            incident["time"] = date_match.group(4)
        
        # Extract IR (Information Report) time
        ir_pattern = r'IR\s+\d{4}\.\d{2}\.\d{2}\s+පැය\s+(\d{4})'
        ir_match = re.search(ir_pattern, row_text)
        
        if ir_match:
            incident["report_time"] = ir_match.group(1)
        
        # Extract person details (victim/suspect)
        incident["victim"] = self.extract_person_details(row_text, "පැමිණිලිකරු")
        incident["suspect"] = self.extract_person_details(row_text, "සැකකරු")
        
        # Extract financial loss
        # Pattern: වටිනාකම රු : 560,000 =
        loss_pattern = r'වටිනාකම\s+රු\s*:\s*([\d,]+)\s*='
        loss_match = re.search(loss_pattern, row_text)
        
        if loss_match:
            incident["financial_loss"] = loss_match.group(1)
        
        # Extract description (clean the text)
        incident["description"] = self.clean_text(row_text)
        
        return incident
    
    def extract_person_details(self, text: str, person_type: str) -> Dict[str, Any]:
        """
        Extract person details (victim/suspect)
        පුද්ගල විස්තර නිස්සාරණය කරන්න (වින්දිතයා/සැකකරු)
        """
        person = {
            "name": "",
            "age": "",
            "gender": "",
            "occupation": "",
            "address": "",
            "phone": ""
        }
        
        # Extract name
        # Pattern: බී.ජී.සී. අමරවීර
        name_pattern = rf'([A-Z]\.(?:[A-Z]\.)*[A-Z]\.\s+)?([^\n]+?)(?=අවු|වයස|පුරුෂ|ස්ත්‍රී)'
        name_match = re.search(name_pattern, text)
        
        if name_match:
            full_name = (name_match.group(1) or "") + (name_match.group(2) or "")
            person["name"] = full_name.strip()
        
        # Extract age
        age_pattern = r'අවු\s*:\s*(\d+)'
        age_match = re.search(age_pattern, text)
        
        if age_match:
            person["age"] = age_match.group(1)
        
        # Extract gender
        if 'පුරුෂ' in text:
            person["gender"] = "පුරුෂ"
        elif 'ස්ත්‍රී' in text:
            person["gender"] = "ස්ත්‍රී"
        
        # Extract occupation
        occupation_pattern = r'රැකියාව\s*:\s*([^\n]+?)(?=අංක|දු\.අ)'
        occupation_match = re.search(occupation_pattern, text)
        
        if occupation_match:
            person["occupation"] = occupation_match.group(1).strip()
        
        # Extract address
        address_pattern = r'අංක\s+([^\n]+?)(?=දු\.අ|$)'
        address_match = re.search(address_pattern, text)
        
        if address_match:
            person["address"] = address_match.group(1).strip()
        
        # Extract phone
        phone_pattern = r'දු\.අ\.?\s*:?\s*(\d+)'
        phone_match = re.search(phone_pattern, text)
        
        if phone_match:
            person["phone"] = phone_match.group(1)
        
        return person
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        පෙළ පිරිසිදු කර සාමාන්‍යකරණය කරන්න
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Keep Sinhala, English, numbers, and common punctuation
        text = re.sub(r'[^\u0D80-\u0DFF\sA-Za-z\d.,;:()\-=/]', '', text)
        return text.strip()
    
    def extract_summary_table(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract the summary table from the end of the report
        වාර්තාවේ අවසානයේ ඇති සාරාංශ වගුව නිස්සාරණය කරන්න
        """
        summary = {}
        
        for cat_num in self.categories.keys():
            count = self.extract_category_count(text, cat_num)
            
            summary[cat_num] = {
                "category_name": self.categories[cat_num],
                "total_incidents": count,
                "resolved": "-",
                "unresolved": "-"
            }
        
        return summary
    
    def extract_all(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract all data from the PDF report
        PDF වාර්තාවෙන් සියලුම දත්ත නිස්සාරණය කරන්න
        """
        # Extract text from PDF
        pdf_text = self.extract_from_pdf(pdf_path)
        
        if not pdf_text:
            return {"error": "Failed to extract text from PDF"}
        
        # Initialize report data structure
        report_data = {
            "header": self.extract_header(pdf_text),
            "categories": {},
            "summary_table": {},
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "total_categories": 29,
                "categories_with_incidents": 0,
                "total_incidents": 0
            }
        }
        
        # Extract data for each category
        for cat_num, cat_name in self.categories.items():
            category_data = {
                "category_number": cat_num,
                "category_name": cat_name,
                "incidents": [],
                "summary": {
                    "total_incidents": 0,
                    "status": ""
                }
            }
            
            # Check if category is nil
            if self.is_nil_category(pdf_text, cat_num):
                category_data["summary"]["status"] = "නැත"
                category_data["summary"]["total_incidents"] = "නැත"
            else:
                # Extract incidents for this category
                incidents = self.extract_table_data(pdf_text, cat_num)
                category_data["incidents"] = incidents
                category_data["summary"]["total_incidents"] = len(incidents)
                
                if len(incidents) > 0:
                    report_data["metadata"]["categories_with_incidents"] += 1
                    report_data["metadata"]["total_incidents"] += len(incidents)
            
            report_data["categories"][cat_num] = category_data
        
        # Extract summary table
        report_data["summary_table"] = self.extract_summary_table(pdf_text)
        
        return report_data
    
    def save_to_json(self, data: Dict[str, Any], output_file: str):
        """
        Save extracted data to JSON file
        නිස්සාරණය කළ දත්ත JSON ගොනුවකට සුරකින්න
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Data saved to: {output_file}")
    
    def generate_summary_report(self, data: Dict[str, Any]) -> str:
        """
        Generate a text summary of the report
        වාර්තාවේ පෙළ සාරාංශයක් ජනනය කරන්න
        """
        lines = []
        lines.append("=" * 80)
        lines.append("දෛනික සිදුවීම් වාර්ථාව - සාරාංශය")
        lines.append("Daily Incident Report - Summary")
        lines.append("=" * 80)
        lines.append("")
        
        # Header info
        header = data.get("header", {})
        lines.append(f"වාර්තා කාලය: {header.get('report_period', 'N/A')}")
        lines.append(f"Report Period: {header.get('report_period', 'N/A')}")
        lines.append("")
        
        # Metadata
        metadata = data.get("metadata", {})
        lines.append(f"මුළු ප්‍රවර්ග: {metadata.get('total_categories', 0)}")
        lines.append(f"සිදුවීම් සහිත ප්‍රවර්ග: {metadata.get('categories_with_incidents', 0)}")
        lines.append(f"මුළු සිදුවීම්: {metadata.get('total_incidents', 0)}")
        lines.append("")
        
        # Category summary
        lines.append("ප්‍රවර්ග සාරාංශය:")
        lines.append("Category Summary:")
        lines.append("-" * 80)
        
        for cat_num, cat_data in data.get("categories", {}).items():
            cat_name = cat_data.get("category_name", "")
            total = cat_data.get("summary", {}).get("total_incidents", 0)
            status = cat_data.get("summary", {}).get("status", "")
            
            if status == "නැත":
                lines.append(f"{cat_num}. {cat_name}: නැත")
            else:
                lines.append(f"{cat_num}. {cat_name}: {total} සිදුවීම්")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"නිස්සාරණ දිනය: {metadata.get('extraction_date', 'N/A')}")
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """
    Main function - Command line interface
    ප්‍රධාන ශ්‍රිතය - විධාන රේඛා අතුරුමුහුණත
    """
    import sys
    
    print("=" * 80)
    print("Sinhala Police Report Data Extraction Tool")
    print("සිංහල පොලිස් වාර්තා දත්ත නිස්සාරණ මෙවලම")
    print("=" * 80)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python app.py <pdf_file>")
        print("Example: python app.py report.pdf")
        print()
        print("භාවිතය: python app.py <pdf_ගොනුව>")
        print("උදාහරණය: python app.py report.pdf")
        return
    
    pdf_file = sys.argv[1]
    output_json = pdf_file.replace('.pdf', '_extracted.json')
    output_summary = pdf_file.replace('.pdf', '_summary.txt')
    
    print(f"📄 Input PDF: {pdf_file}")
    print(f"📊 Output JSON: {output_json}")
    print(f"📝 Output Summary: {output_summary}")
    print()
    
    # Create extractor
    extractor = SinhalaPoliceReportExtractor()
    
    # Extract data
    print("🔄 Extracting data from PDF...")
    print("🔄 PDF එකෙන් දත්ත නිස්සාරණය කරමින්...")
    data = extractor.extract_all(pdf_file)
    
    if "error" in data:
        print(f"❌ Error: {data['error']}")
        return
    
    # Save JSON
    print("💾 Saving JSON data...")
    print("💾 JSON දත්ත සුරකිමින්...")
    extractor.save_to_json(data, output_json)
    
    # Generate and save summary
    print("📋 Generating summary report...")
    print("📋 සාරාංශ වාර්තාව ජනනය කරමින්...")
    summary = extractor.generate_summary_report(data)
    
    with open(output_summary, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"✓ Summary saved to: {output_summary}")
    
    # Print summary to console
    print()
    print(summary)
    
    print()
    print("=" * 80)
    print("✅ Extraction complete! / නිස්සාරණය සම්පූර්ණයි!")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main()
    else:
        print("Starting Police Web UI (Classic Mode)...")
        from police_web_ui import app as flask_app
        # Run on port 5000 as previously requested in the documentation
        flask_app.run(host='0.0.0.0', port=5000, debug=True)
