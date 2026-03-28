import os
import sys
import markdown
import logging
from web_report_engine import HTML_TEMPLATE, html_to_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_md_to_pdf(md_path, pdf_path, title="Security Report"):
    """
    Converts the generated security report Markdown to a professional PDF.
    """
    if not os.path.exists(md_path):
        logger.error(f"MD file not found: {md_path}")
        return False
        
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    # Convert Markdown to HTML body
    html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Wrap in our institutional template (simplified for MD output)
    # We use a simple wrapper since the MD already has headers
    full_html = HTML_TEMPLATE.replace("{{ REPORT_TYPE }}", title)
    # The template expects {{ ALL_PAGES }}, we'll wrap our body in a .page div
    page_html = f'<div class="page" style="height:auto; min-height:297mm;">{html_body}</div>'
    full_html = full_html.replace("{{ ALL_PAGES }}", page_html)
    
    # Save temp HTML
    temp_html = md_path.replace(".md", ".html")
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(full_html)
        
    # Convert to PDF
    success = html_to_pdf(temp_html, pdf_path)
    if success:
        logger.info(f"Successfully generated PDF: {pdf_path}")
    else:
        logger.error(f"Failed to generate PDF")
        
    return success

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python md_to_pdf.py <input_md> <output_pdf>")
    else:
        convert_md_to_pdf(sys.argv[1], sys.argv[2])
