import requests
import json
import os

# Prompt versioning — freeze proven prompts
PROMPT_VERSION = "stable_v4_claude"
SECTION_PROMPT_VERSION = "stable_v4_claude"

class ClaudeClient:
    """Lightweight client for Anthropic Claude AI structuring."""
    
    def __init__(self, api_key=None, model="claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = model
        
        # Check if we should use local Ollama (fallback not implemented for Claude yet, but keeping structure)
        self.is_ollama = False
        if not api_key:
             # Fallback to a default or local if needed, but for now we expect a key
             pass

    def structure_text(self, raw_text, report_type="General"):
        """Uses Claude to convert raw report text into structured Markdown with official headers."""
        
        if report_type == "Security":
            sections = """
            01. VERY IMPORTANT MATTERS OF SECURITY INTEREST
            02. SUBVERSIVE ACTIVITIES
            03. RECOVERIES OF ARMS / AMMUNITION / EXPLOSIVES
            """
        else:
            sections = """
            01. SERIOUS CRIMES COMMITTED
            02. RAPE, SEXUAL ASSAULT & CHILD ABUSE
            03. FATAL ACCIDENTS
            04. POLICE OFFICERS/VEHICLES INVOLVED IN ROAD ACCIDENTS AND DAMAGES TO SRI LANKA POLICE PROPERTY
            05. FINDING OF DEAD BODIES UNDER SUSPICIOUS CIRCUMSTANCES
            06. POLICE OFFICERS CHARGED IN COURTS / COMPLAINTS AGAINST POLICE / ALLEGED ACTS OF INDISCIPLINE BY POLICE OFFICERS
            07. SERIOUS INJURY/ ILLNESSES/ DEATHS OF POLICE OFFICERS
            08. DETECTION OF NARCOTIC AND ILLEGAL LIQUOR
            09. ARREST OF TRI-FORCES MEMBERS
            10. OTHER MATTERS
            """

        prompt = f"""
        ### INSTITUTIONAL ROLE:
        You are the Head Translator for the Inspector General's Command & Information Division. 
        Your task is to convert raw Sinhala incident logs into the official English "{report_type} Situation Report" format with 100% institutional parity.

        ### REQUIRED OUTPUT STRUCTURE:
        Use these EXACT numbered English headers for the {report_type} Report:
        {sections}

        ### CRITICAL: INDEPENDENT EXTRACTION
        - **IGNORE SUMMARY TABLES**: The document may contain summary lists at the top where sections are marked as "Nil". **DISREGARD THESE.**
        - **SCAN ENTIRE TEXT**: You MUST scan the whole document for detailed narratives (usually labeled with 'OTM', 'IR', dates, and station names).
        - **EXTRACT EVERY INCIDENT**: If you find an incident narrative, you MUST include it, even if the summary said "Nil".
        - **PROFESSIONAL TONE**: Use the formal "Inspector General of Police" translator style.

        ### GROUND TRUTH RULES FOR INSTITUTIONAL FIDELITY:
        1. **Institutional Hierarchy (MANDATORY):** 
           For EVERY incident, you MUST include the full geographic hierarchy in this exact format:
           S/DIG [PROVINCE (ALL CAPS)]
           DIG [District Name]
           District
           [Division Name] Div.
           [STATION NAME (ALL CAPS)]: [Narrative Start]

        2. **Narrative Excellence (NO SUMMARIES):**
           Do NOT summarize incidents. Provide full, descriptive paragraphs (min 100 words where possible). 
           Include:
           - "A case of [Crime Type] [Details] was reported to the police station."
           - How the offence occurred (e.g., "by breaking and entering through a window").
           - Time/Date: "The offence took place between [Start] and [End] on the [Date with suffix, e.g., 18th of March 2026]".
           - Complainant: "Complainant named [Name] (TP [Number])".
           - Suspect: "Suspect: [Name/Unknown], aged [Age] ([Gender]) [Status]".
           - Property: "The stolen [Property] valued Rs. [Amount]/= [Recovered/Not recovered]".
           - Closing: "Investigations in process. Motive: [Reason]."

        3. **Reference Coding:** 
           Every paragraph MUST end with the bracketed reference code found in the input (e.g., (CTM.553)MS or (OTM.1481)T).

        4. **Standardized Terminology:**
           - "Motive: For illegal gain."
           - "Motive: To fulfill sexual desire."
           - "Died due to drowning."
           - "Reckless driving of the driver."

        5. **Layout:**
           Use Markdown formatting. Use bold for Station names and Hierarchy headers.

        ### INPUT PROCESSING:
        - If a section from the input does not belong in this report type, IGNORE IT.
        - If a section is empty, state "Nil".
        
        ### RAW SINHALA TEXT:
        {raw_text}
        """
        return self._call_api(prompt)

    def structure_section(self, section_title, section_text, report_type="General"):
        """Focused pass for a single section to prevent skipped data."""
        prompt = f"""
        ### INSTITUTIONAL ROLE:
        You are the "Antigravity Data Processor & Translator," a high-precision Data Architect specialized for the Inspector General of Sri Lanka Police.
        Your mission is to achieve 100% data fidelity by following these 4 phases:

        PHASE 1: ANALYSIS & COUNTING (SINHALA)
        - Extract details based on standard security topics (Serious Crimes, Subversive Activities, Recoveries, etc.).
        - COUNT every single incident/entry in the source to ensure zero data loss.

        PHASE 2: TRANSLATION & FORMATTING (ENGLISH)
        - Format: Use "Confidential - IG's Command/Information Division" style.
        - Terminology: Use professional English (Homicide, Theft, Excavation, Recoveries, etc.).
        - Cross-Check: Ensure the number of English entries matches the Sinhala count.

        PHASE 3: ADMINISTRATIVE ENRICHMENT
        - Jurisdiction Mapping: For every Police Station, assign the correct:
            1. S/DIG Province
            2. DIG District/Range
            3. Police Division
            (Hierarchy: Province > DIG Range > Division > Station)

        PHASE 4: FINAL QUALITY AUDIT
        - Verify all fields are filled. Match the layout of official samples.

        ### OUTPUT STRUCTURE (MANDATORY):
        Start with: `## {section_title}`
        For every incident:
        ### [STATION]
        - **Hierarchy**: S/DIG [Province], DIG [District], [Division]
        - **Narrative**: [Professional Police Narration, 50+ words].
        - **Reference**: (CTM.553)MS

        ### INPUT TEXT (PROCESS THIS NOW):
        {section_text}
        """
        return self._call_api(prompt)

    def structure_section_retry(self, section_title, section_text, previous_output="", report_type="General"):
        """Retry with improved prompt when confidence is low."""
        retry_prompt = f"""
        ### CRITICAL RETRY: {section_title}
        The previous extraction was INCOMPLETE. You MUST improve it.
        
        PREVIOUS OUTPUT (LOW QUALITY):
        {previous_output[:1000]}
        
        ### REQUIREMENTS:
        - Extract EVERY incident. Do NOT skip any.
        - Every incident MUST have: Station Name, Full Narrative (50+ words), Reference Code.
        - Use full hierarchy: S/DIG, DIG, Div, Station.
        - Do NOT leave any field blank. Use "Unknown" if truly missing.
        
        ### ORIGINAL INPUT TEXT:
        {section_text}
        """
        return self._call_api(retry_prompt)

    def verify_counts(self, raw_sinhala, structured_english):
        """Cross-checks if the incident count matches between text versions."""
        prompt = f"""
        Compare these two versions of a police report section.
        Count how many distinct incidents are in the Sinhala version vs the English version.
        
        SINHALA:
        {raw_sinhala[:2000]}
        
        ENGLISH:
        {structured_english[:2000]}
        
        Return ONLY a JSON object: {{"sinhala_count": X, "english_count": Y, "mismatch": true/false}}
        """
        return self._call_api(prompt)

    def refine_narrative(self, raw_narrative, report_type="General"):
        """Pass 2: Refines the extracted English text into formal institutional tone."""
        prompt = f"""
        ### MODULAR TASK: NARRATIVE REFINEMENT
        You are the Chief Editor for the Inspector General of Sri Lanka Police.
        Target Tone: Strictly Formal, Institutional, Official.
        
        ### RAW INPUT:
        {raw_narrative}
        
        ### REFINEMENT RULES:
        1. Use formal police vocabulary.
        2. Ensure geographic hierarchy is mentioned if relevant.
        3. Formalize money/value descriptions.
        4. Correct common translation artifacts.
        5. DO NOT change facts.
        6. End with reference code.
        
        ### FINAL REFINED NARRATIVE:
        """
        return self._call_api(prompt)

    def _call_api(self, prompt):
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                return res.json()["content"][0]["text"]
            return f"❌ Claude API Error: {res.status_code} - {res.text}"
        except Exception as e:
            return f"❌ Claude Connection Failed: {str(e)}"

# --- SINGLETON OR FACTORY ---
def get_ai_assistant(api_key=None):
    return ClaudeClient(api_key=api_key)
