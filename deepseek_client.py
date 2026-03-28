import requests
import json
import os
import ai_engine_manager

# Prompt versioning — freeze proven prompts
PROMPT_VERSION = "stable_v3"
SECTION_PROMPT_VERSION = "stable_v3"

class DeepSeekClient:
    """Refactored client that routes through the unified AI Engine Manager."""
    
    def __init__(self, api_key=None, base_url=None, model=None):
        # We now use the unified manager which handles .env and fallback logic
        self.assistant = ai_engine_manager.get_engine(mode="auto")
        self.is_ollama = False # Keep for compatibility, though manager handles it
        self.model = self.assistant.openrouter_model if not self.assistant.fallback_active else self.assistant.ollama_model

    def structure_text(self, raw_text, report_type="General"):
        """Uses DeepSeek to convert raw report text into structured Markdown with official headers."""
        
        # Define standard sections based on report type
        if self.assistant.fallback_active:
            self.is_ollama = True
            
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
        return self.assistant.call_ai(prompt)

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
        ### [STATION TOWN NAME (ONLY ENGLISH, ALL CAPS, NO "POLICE" OR "STATION")]
        - **Hierarchy**: S/DIG [PROVINCE (ALL CAPS)], DIG [DISTRICT (ALL CAPS)], [DIVISION (ALL CAPS)] DIVISION
        - **Summary**: (Short arrest/incident summary in parentheses, e.g. "Arrest of suspects along with a detonator and gunpowder")
        - **Narrative**: On the [Date with suffix, e.g. 14th March 2026], [Professional Narrative... min 50 words].
        - **Reference**: (CTM.553)MS

        ### CRITICAL RULE:
        - NEVER include any Sinhala script in the output.
        - Station header should be just the town (e.g. `### EMBILIPITIYA`).
        - Every incident MUST have a bracketed Summary.

        ### PROVINCE HINTS:
        - Western (Colombo, Gampaha, Kalutara, Negombo, Panadura, Pannipitiya, Welikada)
        - Sabaragamuwa (Ratnapura, Kegalle, Embilipitiya)
        - North Central (Anuradhapura, Polonnaruwa, Thirappane)
        - Uva (Badulla, Monaragala, Dambagalla)
        
        ### SINHALA GLOSSARY (For OCR Recovery):
        - නෆත = Nil / None
        - සඳොලිවහ වහථළනය = Police Station
        - සරොට්ඨළවය / සරොඨවන = Division
        - දිනය / පදිනහය = Date
        - ඳෆය / වෆවළළ = Time
        
        ### FEW-SHOT EXAMPLES (INSTITUTIONAL FORMATTING):
        ### PILIYANDALA POLICE
        - **Hierarchy**: S/DIG WESTERN, DIG WP SOUTH, PILIYANDALA DIVISION
        - **Narrative**: A case of burglary involving the theft of Rs. 20,000/= cash and property valued at Rs. 887,000/= was reported. The entry was gained by breaking through a bathroom window at Pelenwatta, Pannipitiya. Motive: For illegal gain.
        - **Reference**: (CTM.598)MS

        ### WELIKADA POLICE
        - **Hierarchy**: S/DIG WESTERN, DIG WP SOUTH, WELIKADA DIVISION
        - **Narrative**: On information received, police recovered pistol ammunition from a cab (Reg No: # PG 2937) belonging to the Ministry of Agriculture, Natural Resources, Lands and Irrigation. The discovery was made during a vehicle repair at Piyota Motors, Rajagiriya.
        - **Reference**: (OTM.1672)MS

        ### INPUT TEXT (PROCESS THIS NOW):
        {section_text}
        """
        return self.assistant.call_ai(prompt)

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
        - **CRITICAL RULE**: Do NOT output boilerplate about "corrupted Sinhala script" or "fragmented text". 
        
        ### ORIGINAL INPUT TEXT:
        {section_text}
        
        [Prompt Version: {SECTION_PROMPT_VERSION}_retry]
        """
        return self.assistant.call_ai(retry_prompt)

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
        return self.assistant.call_ai(prompt)

    def refine_narrative(self, raw_narrative, report_type="General"):
        """Pass 2: Refines the extracted English text into formal institutional tone."""
        prompt = f"""
        ### MODULAR TASK: NARRATIVE REFINEMENT
        You are the Chief Editor for the Inspector General of Sri Lanka Police.
        Target Tone: Strictly Formal, Institutional, Official.
        
        ### RAW INPUT:
        {raw_narrative}
        
        ### REFINEMENT RULES:
        1. Use formal police vocabulary (e.g., "a case of homicide was reported" instead of "a man was killed").
        2. Ensure geographic hierarchy is mentioned if relevant to the narrative flow.
        3. Formalize money/value descriptions (e.g., "Rs. 50,000/=").
        4. Correct common translation artifacts (e.g., "Motive was for illegal gain" instead of "They did it for money").
        5. DO NOT change the facts (names, dates, locations). Only refine the phrasing.
        6. End with the reference code like (CTM.123)MS.
        
        ### FINAL REFINED NARRATIVE:
        """
        return self.assistant.call_ai(prompt)

# --- SINGLETON OR FACTORY ---
def get_ai_assistant(api_key=None):
    return DeepSeekClient()
