"""
PDF Generator from Extracted Data
==================================

This script takes the extracted JSON data and generates a formatted PDF report.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
from datetime import datetime

class PDFReportGenerator:
    """Generate PDF reports from extracted data"""
    
    def __init__(self):
        # Register Sinhala font (you'll need to provide a Sinhala Unicode font)
        # For now, we'll use default fonts
        self.styles = getSampleStyleSheet()
        self.setup_styles()
    
    def setup_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='SinhalaTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            alignment=1  # Center
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='SinhalaHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='SinhalaBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#333333')
        ))
        
        # Category style
        self.styles.add(ParagraphStyle(
            name='CategoryStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
    
    def generate_pdf(self, json_file, output_pdf):
        """Generate PDF from JSON data"""
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create PDF
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        
        # Add title
        story.append(Paragraph("දෛනික සිදුවීම් වාර්ථාව", self.styles['SinhalaTitle']))
        story.append(Paragraph("Daily Incident Report", self.styles['SinhalaTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add header information
        header = data.get('header', {})
        date_range = header.get('date_range', {})
        
        header_text = f"""
        <b>Report Period:</b><br/>
        From: {date_range.get('start_date', 'N/A')} at {date_range.get('start_time', 'N/A')} hours<br/>
        To: {date_range.get('end_date', 'N/A')} at {date_range.get('end_time', 'N/A')} hours<br/>
        <br/>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        story.append(Paragraph(header_text, self.styles['SinhalaBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add summary statistics
        metadata = data.get('metadata', {})
        summary_text = f"""
        <b>Summary Statistics:</b><br/>
        Total Categories: {metadata.get('total_categories', 0)}<br/>
        Categories with Incidents: {metadata.get('categories_with_incidents', 0)}<br/>
        """
        story.append(Paragraph(summary_text, self.styles['SinhalaBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add horizontal line
        story.append(Spacer(1, 0.1*inch))
        
        # Add categories
        categories = data.get('categories', {})
        
        for cat_num, cat_data in sorted(categories.items()):
            # Category header
            cat_name = cat_data.get('category_name', '')
            status = cat_data.get('status', '')
            total_incidents = cat_data.get('summary', {}).get('total_incidents', 0)
            
            if status == 'නැත':
                cat_header = f"<b>{cat_num}. {cat_name}</b>: නැත (No incidents)"
                story.append(Paragraph(cat_header, self.styles['CategoryStyle']))
                story.append(Spacer(1, 0.1*inch))
            elif total_incidents > 0:
                cat_header = f"<b>{cat_num}. {cat_name}</b>: {total_incidents} incident(s)"
                story.append(Paragraph(cat_header, self.styles['CategoryStyle']))
                story.append(Spacer(1, 0.1*inch))
                
                # Add incidents
                incidents = cat_data.get('incidents', [])
                for idx, incident in enumerate(incidents, 1):
                    incident_text = self.format_incident(incident, idx)
                    story.append(Paragraph(incident_text, self.styles['SinhalaBody']))
                    story.append(Spacer(1, 0.15*inch))
                
                # Add page break after each category with incidents
                if len(incidents) > 2:
                    story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        print(f"✓ PDF generated: {output_pdf}")
    
    def format_incident(self, incident, number):
        """Format a single incident for display"""
        lines = [f"<b>Incident {number}:</b>"]
        
        if incident.get('police_station'):
            lines.append(f"Police Station: {incident['police_station']}")
        
        if incident.get('date'):
            date_time = f"{incident['date']}"
            if incident.get('time'):
                date_time += f" at {incident['time']} hours"
            lines.append(f"Date/Time: {date_time}")
        
        if incident.get('location'):
            lines.append(f"Location: {incident['location']}")
        
        # Victim details
        victim = incident.get('victim', {})
        if victim.get('name'):
            victim_info = f"Victim: {victim['name']}"
            if victim.get('age'):
                victim_info += f", Age: {victim['age']}"
            if victim.get('gender'):
                victim_info += f", Gender: {victim['gender']}"
            lines.append(victim_info)
        
        # Suspect details
        suspect = incident.get('suspect', {})
        if suspect.get('name'):
            suspect_info = f"Suspect: {suspect['name']}"
            if suspect.get('age'):
                suspect_info += f", Age: {suspect['age']}"
            if suspect.get('gender'):
                suspect_info += f", Gender: {suspect['gender']}"
            if suspect.get('address'):
                suspect_info += f"<br/>Address: {suspect['address']}"
            lines.append(suspect_info)
        
        if incident.get('financial_loss'):
            lines.append(f"Financial Loss: Rs. {incident['financial_loss']}")
        
        if incident.get('status'):
            lines.append(f"Status: {incident['status']}")
        
        if incident.get('description'):
            desc = incident['description'][:200]  # First 200 chars
            if len(incident['description']) > 200:
                desc += "..."
            lines.append(f"Description: {desc}")
        
        return "<br/>".join(lines)


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf_from_extraction.py <json_file> [output_pdf]")
        print("Example: python generate_pdf_from_extraction.py march22_extracted.json march22_report.pdf")
        return
    
    json_file = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else json_file.replace('.json', '.pdf')
    
    print("=" * 80)
    print("Generating PDF Report")
    print("=" * 80)
    print()
    print(f"Input JSON: {json_file}")
    print(f"Output PDF: {output_pdf}")
    print()
    
    generator = PDFReportGenerator()
    generator.generate_pdf(json_file, output_pdf)
    
    print()
    print("=" * 80)
    print("PDF Generation Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
