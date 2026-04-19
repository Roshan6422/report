import os
import zipfile
import tempfile
from datetime import datetime
from docxtpl import DocxTemplate
from police_patterns import GENERAL_SECTIONS, PROVINCE_LIST, SECURITY_SECTIONS

class WordReportEngine:
    """
    World-class Word Report Engine with support for 10-category General and 4-category Security structures.
    Uses .dotx templates and outputs .docx files.
    """
    def __init__(self, templates_dir="sample"):
        self.templates_dir = templates_dir
        self.gen_template_path = None
        self.sec_template_path = None
        
        # Find templates in the directory (General and Security)
        if os.path.exists(templates_dir):
            for f in os.listdir(templates_dir):
                if f.startswith("~$"): continue
                low_f = f.lower()
                if "general" in low_f and (f.endswith(".dotx") or f.endswith(".docx")):
                    self.gen_template_path = os.path.join(templates_dir, f)
                elif "security" in low_f and (f.endswith(".dotx") or f.endswith(".docx")):
                    self.sec_template_path = os.path.join(templates_dir, f)

        if not self.gen_template_path: print(f"  [Word] Warning: No General template found in {templates_dir}")
        else: print(f"  [Word] Found General template: {self.gen_template_path}")
        if not self.sec_template_path: print(f"  [Word] Warning: No Security template found in {templates_dir}")
        else: print(f"  [Word] Found Security template: {self.sec_template_path}")

    def _convert_to_docx_format(self, template_path, temp_name):
        """Fix for python-docx rejecting .dotx templates by rewriting internal content type."""
        with zipfile.ZipFile(template_path, 'r') as zin:
            with zipfile.ZipFile(temp_name, 'w') as zout:
                for item in zin.infolist():
                    content = zin.read(item.filename)
                    if item.filename == '[Content_Types].xml':
                        content = content.replace(
                            b'application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml',
                            b'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'
                        )
                    zout.writestr(item, content)

    def _get_province_structure(self):
        """Create a fresh list of province structures."""
        return [{"name": p, "incidents": [], "nil": True} for p in PROVINCE_LIST]

    def _prepare_context(self, category_results, sections_list, is_security=False):
        """
        Convert category_results into a context dictionary for docxtpl.
        Now context-aware: only includes incidents destined for this report type.
        """
        date_range = category_results.get("date_range", "")
        if not date_range:
            current_date = datetime.now().strftime('%d %B %Y')
            date_range = f"From 0400 hrs. on {current_date} to 0400 hrs. on {current_date}"

        # Initialize sections map
        sections_map = {t: {"title": t, "provinces": self._get_province_structure()} for t in sections_list}

        for cat_num, data in category_results.items():
            if not str(cat_num).isdigit():
                continue

            num = int(cat_num)
            raw_incidents = data.get("raw_incidents", [])
            if not raw_incidents:
                continue

            for inc in raw_incidents:
                origin = inc.get("origin_block", "General")

                # Safety net: categories 01/02/03 always Security
                if num in [1, 2, 3]:
                    origin = "Security"

                target_section_title = None

                # SECURITY REPORT MAPPING
                if is_security:
                    if origin == "Security":
                        if num == 1: target_section_title = SECURITY_SECTIONS[0]
                        elif num == 3: target_section_title = SECURITY_SECTIONS[1]
                        elif num == 2: target_section_title = SECURITY_SECTIONS[2]
                        else: target_section_title = SECURITY_SECTIONS[3]
                    else: continue  # Skip general incidents in security report

                # GENERAL REPORT MAPPING
                else:
                    if origin == "Security": continue  # Skip security incidents in general report

                    if num in [4, 5, 6, 7, 8]: target_section_title = GENERAL_SECTIONS[0]  # 01. SERIOUS CRIMES
                    elif num == 9: target_section_title = GENERAL_SECTIONS[1]  # 02. RAPE / ABUSE
                    elif num == 10: target_section_title = GENERAL_SECTIONS[2]  # 03. FATAL ACCIDENTS
                    elif num == 12: target_section_title = GENERAL_SECTIONS[3]  # 04. POLICE ACCIDENTS
                    elif num == 11: target_section_title = GENERAL_SECTIONS[4]  # 05. DEAD BODIES
                    elif num == 14: target_section_title = GENERAL_SECTIONS[5]  # 06. POLICE MISCONDUCT
                    elif num in [15, 16, 17, 18, 19]: target_section_title = GENERAL_SECTIONS[6]  # 07. POLICE INJURY/ILLNESSES/DEATHS
                    elif num == 20: target_section_title = GENERAL_SECTIONS[7]  # 08. NARCOTIC / LIQUOR (cat 20, not 19)
                    elif num == 22: target_section_title = GENERAL_SECTIONS[8]  # 09. TRI-FORCES ARREST (cat 22, not 21)
                    elif num == 13:
                        desc = (inc.get("body") or "").lower()
                        if "property" in desc or "vehicle" in desc or "damage" in desc:
                            target_section_title = GENERAL_SECTIONS[3]  # 04. POLICE ACCIDENTS
                        else:
                            target_section_title = GENERAL_SECTIONS[6]  # 07. POLICE INJURY/DEATH
                    else: target_section_title = GENERAL_SECTIONS[9]  # 10. OTHER

                if not target_section_title:
                    continue

                # Map standardized incident fields to template-friendly names
                entry = {
                    "station": str(inc.get("station", "Unknown")).upper(),
                    "summary": inc.get("summary", ""),
                    "body": inc.get("body", ""),
                    "reference": str(inc.get("ctm", inc.get("otm", inc.get("ir", "")))).strip(),
                    "province": str(inc.get("province", "WESTERN")).upper()
                }

                # Find correct province bucket
                p_base = entry["province"].upper()
                placed = False
                for p_struct in sections_map[target_section_title]["provinces"]:
                    if p_struct["name"] in p_base or p_base in p_struct["name"]:
                        p_struct["incidents"].append(entry)
                        p_struct["nil"] = False
                        placed = True
                        break

                if not placed:
                    # Fallback to Western
                    for p_struct in sections_map[target_section_title]["provinces"]:
                        if p_struct["name"] == "WESTERN":
                            p_struct["incidents"].append(entry)
                            p_struct["nil"] = False
                            break

        # Final context
        return {
            "date_range": date_range,
            "report_date": date_range,
            "gen_date": datetime.now().strftime("%d %B %Y"),
            "sections": [sections_map[t] for t in sections_list]
        }

    def generate_reports(self, category_results, output_folder="outputs"):
        """
        Generate both General and Security Word reports.
        """
        os.makedirs(output_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = []

        # Process General Word Report
        if self.gen_template_path:
            try:
                # Convert .dotx to .docx by hacking the internal Content Types XML
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
                    temp_name = tf.name
                self._convert_to_docx_format(self.gen_template_path, temp_name)

                try:
                    tpl = DocxTemplate(temp_name)
                    ctx = self._prepare_context(category_results, GENERAL_SECTIONS, is_security=False)
                    tpl.render(ctx)
                    out_path = os.path.join(output_folder, f"General_Report_{timestamp}.docx")
                    tpl.save(out_path)
                    results.append(out_path)
                    print(f"  [Word] General Report Generated: {os.path.basename(out_path)}")
                finally:
                    if os.path.exists(temp_name):
                        os.remove(temp_name)
            except Exception as e:
                print(f"  [Word] Error: General Report Failed: {e}")

        # Process Security Word Report
        if self.sec_template_path:
            try:
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
                    temp_name = tf.name
                self._convert_to_docx_format(self.sec_template_path, temp_name)

                try:
                    tpl = DocxTemplate(temp_name)
                    ctx = self._prepare_context(category_results, SECURITY_SECTIONS, is_security=True)
                    tpl.render(ctx)
                    out_path = os.path.join(output_folder, f"Security_Report_{timestamp}.docx")
                    tpl.save(out_path)
                    results.append(out_path)
                    print(f"  [Word] Security Report Generated: {os.path.basename(out_path)}")
                finally:
                    if os.path.exists(temp_name):
                        os.remove(temp_name)
            except Exception as e:
                print(f"  [Word] Error: Security Report Failed: {e}")

        return results