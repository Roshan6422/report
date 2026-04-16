"""
schemas.py — Sri Lanka Police AI Pipeline · Pydantic v2 Schema Registry
========================================================================
All validated data contracts for the full PDF-to-report pipeline.

Sections:
  A. Core incident models        (IncidentRecord, CategorizationOutput, ...)
  B. Report structure models     (SectionRecord, ProvinceRecord, FullReportOutput)
  C. Summary / statistics        (SummaryMatrixRow, CaseDataRow, SummaryMatrix)
  D. Pipeline utility models     (ConfidenceScore, ValidationResult, PatternExtractionResult)
  E. Processing / logging        (ProcessingLog, QualityGateResult)
  F. API / key management        (APIKeyStatus, KeyHealthReport)
  G. Translation pipeline        (TranslationRefinement, TranslationChunkResult)
  H. AI extraction configs       (TurboExtractionConfig, OCRConfig)
  I. Analytics / dashboard       (AnalyticsInsight, ProvinceSummary, DailySnapshot)

System Version : v2.1.0
Prompt Version : stable_v4
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Province(str, Enum):
    WESTERN        = "WESTERN"
    SOUTHERN       = "SOUTHERN"
    CENTRAL        = "CENTRAL"
    NORTHERN       = "NORTHERN"
    EASTERN        = "EASTERN"
    NORTH_WESTERN  = "NORTH WESTERN"
    NORTH_CENTRAL  = "NORTH CENTRAL"
    UVA            = "UVA"
    SABARAGAMUWA   = "SABARAGAMUWA"
    NATIONAL       = "NATIONAL"          # fallback / unresolved


class InvestigationStatus(str, Enum):
    CONFIRMED        = "Confirmed"
    ONGOING          = "Ongoing"
    ARRESTED         = "Arrested"
    REMANDED         = "Remanded"
    SUSPECT_IDENTIFIED = "Suspect Identified"
    SOLVED           = "Solved"
    UNSOLVED         = "Unsolved"
    RECOVERED        = "Recovered"
    SECURED          = "Secured"
    UNKNOWN          = "Unknown"


class ExtractionEngine(str, Enum):
    GEMINI      = "gemini"
    OPENAI      = "openai"
    GITHUB      = "github"
    OPENROUTER  = "openrouter"
    GROQ        = "groq"
    AIMLAPI     = "aimlapi"
    OLLAMA      = "ollama"
    TESSERACT   = "tesseract"
    PYPDF2      = "pypdf2"


class KeyStatus(str, Enum):
    ACTIVE        = "✅ Active"
    RATE_LIMITED  = "🔴 Rate Limited"
    EXHAUSTED     = "🔴 Exhausted"
    INVALID       = "❌ Invalid"
    ERROR         = "⚠️ Error"
    UNTESTED      = "⬜ Untested"


# ---------------------------------------------------------------------------
# A. CORE INCIDENT MODELS
# ---------------------------------------------------------------------------

class IncidentRecord(BaseModel):
    """
    Official 8-field Sri Lanka Police institutional incident schema.
    Used for final PDF generation and database storage.
    """
    station:              str  = Field(..., description="Police Station name (e.g., MATARA, FORT)")
    division:             str  = Field(..., description="Police Division (e.g., Matara Div.)")
    date:                 str  = Field(..., description="Date of occurrence (YYYY-MM-DD)")
    time:                 str  = Field(..., description="Time of occurrence (HH:MM, 24-hr)")
    description:          str  = Field(..., description="Full English narrative of the incident")
    financial_loss:       str  = Field(default="Nil",     description="Monetary value of loss/damage (Rs.)")
    status:               str  = Field(default="Confirmed", description="Investigation status")
    victim_suspect_names: str  = Field(default="N/A",     description="Names of involved parties")

    # Optional routing / classification metadata
    province:     str | None = Field(default="WESTERN", description="Province (uppercase)")
    category_num: str | None = Field(default="00",      description="2-digit category (01–29)")
    origin_block: str | None = Field(default="General", description="Source block label")

    # Internal scoring (populated by pipeline_utils)
    _confidence:            float | None = None
    _validation_issues:     list[str] | None = None
    _filled_from_context:   bool | None = None
    _multiple_suspects:     list[str] | None = None
    _no_victim_info:        bool | None = None
    _past_incident:         bool | None = None

    @field_validator("station")
    @classmethod
    def clean_station(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("province")
    @classmethod
    def normalize_province(cls, v: str | None) -> str:
        if not v:
            return Province.WESTERN.value
        v = v.strip().upper().replace(" PROVINCE", "")
        try:
            return Province(v).value
        except ValueError:
            return v  # Keep unknown values instead of failing

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Accept YYYY-MM-DD; attempt fix for common OCR variants."""
        if not v or v.strip().lower() in ("unknown", "-", "nil", "n/a"):
            return v
        v = v.strip().replace(".", "-").replace("/", "-")
        # Handle DD-MM-YYYY → YYYY-MM-DD
        if re.match(r"^\d{2}-\d{2}-\d{4}$", v):
            d, m, y = v.split("-")
            v = f"{y}-{m}-{d}"
        return v

    @field_validator("financial_loss")
    @classmethod
    def format_financial_loss(cls, v: str) -> str:
        if not v or v.strip().lower() in ("nil", "none", "n/a", "0", ""):
            return "Nil"
        # Normalize Rs prefix
        v = re.sub(r"(?i)^rs\.?\s*", "Rs. ", v.strip())
        return v

    @field_validator("category_num")
    @classmethod
    def zero_pad_category(cls, v: str | None) -> str | None:
        if v and v.strip().isdigit():
            return v.strip().zfill(2)
        return v

    model_config = {"populate_by_name": True}


class CategorizationOutput(BaseModel):
    """AI output for incident classification into one of the 29 official SLP categories."""
    category_num:        str   = Field(..., pattern=r"^\d{2}$", description="01–29")
    category_name:       str   = Field(..., description="Official English category name")
    is_security_related: bool  = Field(default=False, description="True for categories 01–03")
    confidence:          float = Field(..., ge=0.0, le=1.0, description="Model confidence [0, 1]")
    reasoning:           str | None = Field(default=None, description="Model's brief reasoning")

    @field_validator("category_num")
    @classmethod
    def validate_range(cls, v: str) -> str:
        num = int(v)
        if not (1 <= num <= 29):
            raise ValueError(f"category_num must be 01–29, got {v}")
        return v.zfill(2)


# ---------------------------------------------------------------------------
# B. REPORT STRUCTURE MODELS
# ---------------------------------------------------------------------------

class ProvinceRecord(BaseModel):
    """A province bucket within a crime section, containing its incident list."""
    name:      str               = Field(..., description="Province name (e.g., WESTERN PROVINCE)")
    incidents: list[dict[str, Any]] = Field(default_factory=list)

    @property
    def incident_count(self) -> int:
        return len(self.incidents)


class SectionRecord(BaseModel):
    """
    One of the 29 official crime categories (sections) in the daily report.
    Contains province-grouped incidents and optional confidence metadata.
    """
    title:       str                  = Field(..., description="Section heading (e.g., '04. Homicides')")
    count:       str | None        = Field(default="00", description="Zero-padded incident count")
    provinces:   list[ProvinceRecord] = Field(default_factory=list)

    # Populated by pipeline_utils
    _confidence: float | None = None

    @property
    def total_incidents(self) -> int:
        return sum(p.incident_count for p in self.provinces)

    @field_validator("count", mode="before")
    @classmethod
    def pad_count(cls, v: Any) -> str:
        if v is None:
            return "00"
        return str(v).zfill(2)


class ReportHeader(BaseModel):
    """Metadata block at the top of every daily SLP report."""
    date_range:       str            = Field(..., description="'From 0400 hrs. on Xth Month YYYY to 0400 hrs. on Yth Month YYYY'")
    report_date:      str | None  = Field(default=None, description="Primary report date (YYYY-MM-DD)")
    report_type:      str            = Field(default="Daily Incident Report")
    issuing_unit:     str            = Field(default="Sri Lanka Police — Operations Room")
    classification:   str            = Field(default="OFFICIAL")
    serial_number:    str | None  = Field(default=None, description="Report serial / file ref")

    @field_validator("date_range")
    @classmethod
    def check_date_range_format(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError("date_range is too short to be valid")
        return v.strip()


class FullReportOutput(BaseModel):
    """
    Top-level model for the complete structured daily report.
    Mirrors the dict shape returned by parse_high_fidelity_markdown().
    """
    header:         ReportHeader               = Field(default_factory=lambda: ReportHeader(date_range="Unknown"))
    date_range:     str                        = Field(default="Unknown", description="Convenience alias")
    sections:       list[SectionRecord]        = Field(default_factory=list)
    summary_matrix: dict[str, Any] | None  = Field(default=None, description="Province × category matrix")
    case_data:      list[dict[str, Any]] | None = Field(default=None, description="29-row case breakdown")

    # Pipeline-injected
    _confidence:  float | None        = None
    _enhancement: dict[str, Any] | None = None

    @property
    def total_incidents(self) -> int:
        return sum(s.total_incidents for s in self.sections)

    @property
    def section_count(self) -> int:
        return len(self.sections)

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# C. SUMMARY / STATISTICS MODELS
# ---------------------------------------------------------------------------

class SummaryMatrixRow(BaseModel):
    """
    One row in the 29-row official statistics table.
    Columns: serial | crime type | reported | solved | unsolved
    """
    serial:       str  = Field(..., description="Row serial (01–29)")
    crime_type:   str  = Field(..., description="Official English crime category")
    reported:     str  = Field(default="-", description="Total reported cases")
    solved:       str  = Field(default="-", description="Solved / detected cases")
    unsolved:     str  = Field(default="-", description="Remaining unsolved")

    @field_validator("serial")
    @classmethod
    def pad_serial(cls, v: str) -> str:
        return str(v).strip().zfill(2)

    @field_validator("reported", "solved", "unsolved", mode="before")
    @classmethod
    def coerce_zero(cls, v: Any) -> str:
        if v is None or str(v).strip() in ("0", ""):
            return "-"
        return str(v).zfill(2) if str(v).isdigit() else str(v)

    @model_validator(mode="after")
    def check_arithmetic(self) -> SummaryMatrixRow:
        """Warn (not raise) if reported ≠ solved + unsolved."""
        try:
            r = int(self.reported) if self.reported != "-" else 0
            s = int(self.solved)   if self.solved   != "-" else 0
            u = int(self.unsolved) if self.unsolved  != "-" else 0
            if r != s + u:
                object.__setattr__(self, "_arithmetic_warning", True)
        except ValueError:
            pass
        return self


class CaseDataRow(BaseModel):
    """One row of the _calculate_case_data() output (28-row breakdown)."""
    index:    int  = Field(..., ge=0, le=27)
    reported: str  = Field(default="-")
    solved:   str  = Field(default="-")
    unsolved: str  = Field(default="-")


class SummaryMatrix(BaseModel):
    """Full province × crime-category count matrix for the report dashboard."""
    headers:         list[str]             = Field(default_factory=list)
    rows:            list[dict[str, Any]]  = Field(default_factory=list)
    totals:          list[str]             = Field(default_factory=list)
    grand_total_all: int                   = Field(default=0)


# ---------------------------------------------------------------------------
# D. PIPELINE UTILITY MODELS
# ---------------------------------------------------------------------------

class ExtractedDate(BaseModel):
    raw: str
    pos: int
    normalized: str | None = None


class ExtractedMoney(BaseModel):
    raw:   str
    value: str   # digits-only, no commas
    pos:   int
    formatted: str | None = None   # e.g. "Rs. 50,000/="


class ExtractedVehicle(BaseModel):
    raw: str
    pos: int


class ExtractedPhone(BaseModel):
    raw:    str
    number: str
    pos:    int


class PatternExtractionResult(BaseModel):
    """Output of pipeline_utils.extract_all_patterns()."""
    dates:           list[ExtractedDate]    = Field(default_factory=list)
    money:           list[ExtractedMoney]   = Field(default_factory=list)
    vehicles:        list[ExtractedVehicle] = Field(default_factory=list)
    phones:          list[ExtractedPhone]   = Field(default_factory=list)
    extraction_time: str                    = Field(default_factory=lambda: datetime.now().isoformat())


class ConfidenceScore(BaseModel):
    """
    Structured result from pipeline_utils.calculate_confidence().
    Mirrors the 7-component scoring breakdown.
    """
    total:              float = Field(..., ge=0.0, le=1.0)
    field_completeness: float = Field(ge=0.0, le=1.0, default=0.0)
    body_quality:       float = Field(ge=0.0, le=1.0, default=0.0)
    reference_code:     float = Field(ge=0.0, le=1.0, default=0.0)
    hierarchy_depth:    float = Field(ge=0.0, le=1.0, default=0.0)
    date_presence:      float = Field(ge=0.0, le=1.0, default=0.0)
    person_info:        float = Field(ge=0.0, le=1.0, default=0.0)
    money_info:         float = Field(ge=0.0, le=1.0, default=0.0)
    label: str = Field(default="")

    @model_validator(mode="after")
    def set_label(self) -> ConfidenceScore:
        if self.total >= 0.85:
            object.__setattr__(self, "label", "HIGH")
        elif self.total >= 0.60:
            object.__setattr__(self, "label", "MEDIUM")
        else:
            object.__setattr__(self, "label", "LOW")
        return self


class ValidationResult(BaseModel):
    """Per-incident validation outcome from pipeline_utils.validate_incident()."""
    incident_station: str             = Field(default="UNKNOWN")
    issues:           list[str]       = Field(default_factory=list)
    auto_fixed:       list[str]       = Field(default_factory=list)
    passed:           bool            = Field(default=True)

    @model_validator(mode="after")
    def derive_passed(self) -> ValidationResult:
        critical = [i for i in self.issues if i.startswith("EMPTY_BODY") or i.startswith("MISSING_STATION")]
        object.__setattr__(self, "passed", len(critical) == 0)
        return self


class ReportValidationSummary(BaseModel):
    """Aggregate validation result for an entire report."""
    total_incidents:  int         = 0
    total_issues:     int         = 0
    critical_issues:  int         = 0
    warning_issues:   int         = 0
    results:          list[ValidationResult] = Field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total_incidents == 0:
            return 1.0
        passed = sum(1 for r in self.results if r.passed)
        return round(passed / self.total_incidents, 3)


# ---------------------------------------------------------------------------
# E. PROCESSING / LOGGING MODELS
# ---------------------------------------------------------------------------

class QualityGateResult(BaseModel):
    """Output of pipeline_utils.quality_gate_check()."""
    passed:     bool  = Field(..., description="True if confidence ≥ threshold")
    confidence: float = Field(..., ge=0.0, le=1.0)
    message:    str   = Field(default="")
    threshold_used: float = Field(default=0.50)

    @property
    def status_emoji(self) -> str:
        if self.passed and self.confidence >= 0.70:
            return "✅"
        elif self.passed:
            return "⚠️"
        return "❌"


class ContextMemorySnapshot(BaseModel):
    """Serialisable snapshot of ContextMemory at a point in time."""
    last_location:  str | None = None
    last_date:      str | None = None
    last_province:  str | None = None
    last_dig:       str | None = None
    last_div:       str | None = None
    stations_seen:  int           = 0


class ProcessingLog(BaseModel):
    """
    Full processing log entry — mirrors create_processing_log() output dict.
    Stored in tmp/processing_logs/log_YYYYMMDD_HHMMSS.json.
    """
    log_id:            str               = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    timestamp:         str               = Field(default_factory=lambda: datetime.now().isoformat())
    system_version:    str               = Field(default="v2.1.0")
    prompt_version:    str               = Field(default="stable_v4")
    report_type:       str               = Field(default="General")
    use_ai:            bool              = Field(default=False)
    input_length:      int               = Field(default=0)
    input_hash:        str               = Field(default="")
    sections_processed: int              = Field(default=0)
    total_incidents:   int               = Field(default=0)
    confidence_score:  float             = Field(default=0.0, ge=0.0, le=1.0)
    validation_issues: int               = Field(default=0)
    cache_hit:         bool              = Field(default=False)
    retry_count:       int               = Field(default=0, ge=0)
    patterns_extracted: dict[str, Any]  = Field(default_factory=dict)
    processing_time_ms: float            = Field(default=0.0, ge=0.0)
    errors:            list[str]         = Field(default_factory=list)
    status:            str               = Field(default="started")
    engine_used:       str | None     = None
    quality_gate:      QualityGateResult | None = None
    context_summary:   ContextMemorySnapshot | None = None

    @property
    def succeeded(self) -> bool:
        return self.status == "completed" and not self.errors


class EnhancementResult(BaseModel):
    """Metadata injected into FullReportOutput._enhancement by enhance_pipeline_output()."""
    system_version:      str                      = "v2.1.0"
    prompt_version:      str                      = "stable_v4"
    confidence:          float                    = Field(ge=0.0, le=1.0)
    validation_issues:   int                      = 0
    quality_gate:        str                      = ""
    quality_gate_passed: bool                     = False
    context_summary:     ContextMemorySnapshot | None = None
    processing_time_ms:  float                    = 0.0


# ---------------------------------------------------------------------------
# F. API / KEY MANAGEMENT MODELS
# ---------------------------------------------------------------------------

class SingleKeyStatus(BaseModel):
    """Status of one API key from get_api_health()."""
    key_id:          str        = Field(..., description="Key identifier (e.g., Gemini_Key1)")
    provider:        str        = Field(..., description="Provider (Gemini / GitHub / OpenAI)")
    status:          KeyStatus  = Field(default=KeyStatus.UNTESTED)
    usage_today:     int        = Field(default=0, ge=0)
    remaining_quota: int | None = None
    last_checked:    str | None = None

    @property
    def is_usable(self) -> bool:
        return self.status in (KeyStatus.ACTIVE,)


class KeyHealthReport(BaseModel):
    """Full health report across all providers — output of MachineTranslator.get_api_health()."""
    checked_at:   str                        = Field(default_factory=lambda: datetime.now().isoformat())
    gemini_keys:  list[SingleKeyStatus]      = Field(default_factory=list)
    github_keys:  list[SingleKeyStatus]      = Field(default_factory=list)
    openai_keys:  list[SingleKeyStatus]      = Field(default_factory=list)

    @property
    def active_gemini_count(self) -> int:
        return sum(1 for k in self.gemini_keys if k.is_usable)

    @property
    def active_github_count(self) -> int:
        return sum(1 for k in self.github_keys if k.is_usable)

    @property
    def has_any_active_key(self) -> bool:
        return self.active_gemini_count > 0 or self.active_github_count > 0


# ---------------------------------------------------------------------------
# G. TRANSLATION PIPELINE MODELS
# ---------------------------------------------------------------------------

class TranslationChunkResult(BaseModel):
    """Result of translating one text chunk (used in parallel workers)."""
    chunk_index:     int   = Field(..., ge=0)
    chunk_total:     int   = Field(..., ge=1)
    engine_used:     str   = Field(default="unknown")
    verified:        bool  = Field(default=False, description="True if Checker AI confirmed translation")
    translated_text: str   = Field(default="")
    original_length: int   = Field(default=0)
    translated_length: int = Field(default=0)
    error:           str | None = None

    @property
    def succeeded(self) -> bool:
        return bool(self.translated_text) and not self.error


class TranslationRefinement(BaseModel):
    """AI output for the linguistic refinement / checker stage."""
    refined_narrative:     str            = Field(..., description="Corrected, institutional English text")
    technical_terms_fixed: list[str]      = Field(default_factory=list, description="Terms that were corrected")
    detected_station:      str | None  = None
    detected_date:         str | None  = None
    sinhala_chars_removed: bool           = Field(default=False)
    confidence_boost:      float | None= Field(default=None, ge=0.0, le=1.0)


class FullTranslationOutput(BaseModel):
    """Complete translation pipeline result for one PDF."""
    source_pdf:        str                       = Field(..., description="Original PDF path")
    sinhala_text:      str | None             = None
    english_text:      str                       = Field(default="")
    pages_processed:   int                       = Field(default=0, ge=0)
    chunk_results:     list[TranslationChunkResult] = Field(default_factory=list)
    primary_engine:    str                       = Field(default="gemini")
    fallback_used:     bool                      = Field(default=False)
    processing_time_s: float                     = Field(default=0.0, ge=0.0)
    output_txt_path:   str | None             = None

    @property
    def success_rate(self) -> float:
        if not self.chunk_results:
            return 1.0
        passed = sum(1 for c in self.chunk_results if c.succeeded)
        return round(passed / len(self.chunk_results), 3)


# ---------------------------------------------------------------------------
# H. AI EXTRACTION CONFIGURATION MODELS
# ---------------------------------------------------------------------------

class TurboExtractionConfig(BaseModel):
    """
    Runtime configuration for extract_pdf_to_json_turbo().
    Mirrors env-var controlled settings so they can be validated up front.
    """
    gemini_model_list:      list[str] = Field(
        default=["gemini-3-flash-preview", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
        description="Ordered list of Gemini model IDs to attempt"
    )
    max_output_tokens:      int       = Field(default=65536, ge=1024)
    skip_gemini:            bool      = Field(default=False, description="TURBO_SKIP_GEMINI")
    pdf_extract_ai_engine:  str | None = Field(default=None, description="PDF_EXTRACT_AI_ENGINE")
    github_turbo_chunk_chars: int     = Field(default=24000, ge=1000)
    github_chunk_cooldown_s: float    = Field(default=0.0, ge=0.0, le=120.0)
    github_turbo_timeout_s:  int      = Field(default=360, ge=120, le=900)

    @field_validator("pdf_extract_ai_engine")
    @classmethod
    def validate_engine(cls, v: str | None) -> str | None:
        allowed = {None, "gemini", "openrouter", "groq", "github", "aimlapi"}
        if v not in allowed:
            raise ValueError(f"pdf_extract_ai_engine must be one of {allowed}")
        return v


class OCRConfig(BaseModel):
    """
    Configuration for pdf_parts_for_gemini_upload() and local Tesseract fallback.
    """
    page_split_enabled:     bool  = Field(default=True,  description="GEMINI_OCR_PAGE_SPLIT")
    pages_per_part:         int   = Field(default=6,     ge=1, description="GEMINI_OCR_PAGES_PER_PART")
    split_min_pages:        int   = Field(default=8,     ge=2, description="GEMINI_OCR_SPLIT_MIN_PAGES")
    skip_local_ocr_fallback: bool = Field(default=False, description="MT_SKIP_LOCAL_OCR_FALLBACK")
    strict_gemini_only:     bool  = Field(default=False, description="MT_STRICT_PDF_GEMINI_ONLY")
    no_tesseract:           bool  = Field(default=False, description="PDF_EXTRACT_NO_TESSERACT")
    allow_local_ocr:        bool  = Field(default=False, description="PDF_EXTRACT_ALLOW_LOCAL_OCR")
    post_ai_workers:        int   = Field(default=4,     ge=1, description="TESSERACT_POST_AI_WORKERS")


# ---------------------------------------------------------------------------
# I. ANALYTICS / DASHBOARD MODELS
# ---------------------------------------------------------------------------

class AnalyticsInsight(BaseModel):
    """Summary for dashboard charts — one row per province."""
    province:        str        = Field(..., description="Province name")
    total_count:     int        = Field(..., ge=0)
    security_count:  int        = Field(default=0, ge=0,  description="Categories 01–03")
    general_count:   int        = Field(default=0, ge=0,  description="Categories 04–29")
    top_categories:  list[str]  = Field(default_factory=list, description="Top 3 crime types")

    @model_validator(mode="after")
    def check_totals(self) -> AnalyticsInsight:
        if self.security_count + self.general_count > self.total_count:
            # Clamp general_count if it overflows
            object.__setattr__(self, "general_count", self.total_count - self.security_count)
        return self


class ProvinceSummary(BaseModel):
    """Richer province summary used by the report dashboard."""
    province:          str               = Field(...)
    total_incidents:   int               = Field(default=0, ge=0)
    by_category:       dict[str, int]    = Field(default_factory=dict, description="category_num → count")
    highest_category:  str | None     = None
    date_range:        str | None     = None

    @model_validator(mode="after")
    def compute_highest(self) -> ProvinceSummary:
        if self.by_category:
            top = max(self.by_category, key=self.by_category.get)  # type: ignore[arg-type]
            object.__setattr__(self, "highest_category", top)
        return self


class DailySnapshot(BaseModel):
    """
    Top-level analytics snapshot for one report date.
    Suitable for serialization to JSON/DB for trend dashboards.
    """
    report_date:       str                    = Field(..., description="YYYY-MM-DD")
    date_range:        str                    = Field(default="")
    total_incidents:   int                    = Field(default=0, ge=0)
    province_summaries: list[ProvinceSummary] = Field(default_factory=list)
    insights:          list[AnalyticsInsight] = Field(default_factory=list)
    summary_matrix:    SummaryMatrix | None= None
    generated_at:      str                    = Field(default_factory=lambda: datetime.now().isoformat())

    @property
    def top_province(self) -> str | None:
        if not self.province_summaries:
            return None
        return max(self.province_summaries, key=lambda p: p.total_incidents).province


# ---------------------------------------------------------------------------
# QUICK SELF-TEST
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("schemas.py — Self-Test")
    print("=" * 60)

    # IncidentRecord
    inc = IncidentRecord(
        station="matara",
        division="Matara Div.",
        date="18.03.2026",
        time="20:30",
        description="A case of robbery was reported. Suspect arrested.",
        financial_loss="Rs. 50000",
        province="western province",
        category_num="5",
    )
    assert inc.station == "MATARA"
    assert inc.date == "2026-03-18"
    assert inc.province == "WESTERN"
    assert inc.category_num == "05"
    assert inc.financial_loss == "Rs. 50000"
    print(f"  ✅ IncidentRecord  → station={inc.station}, date={inc.date}, province={inc.province}, cat={inc.category_num}")

    # SummaryMatrixRow arithmetic warning flag
    row = SummaryMatrixRow(serial="4", crime_type="Homicide", reported="10", solved="06", unsolved="03")
    assert row.serial == "04"
    assert hasattr(row, "_arithmetic_warning")   # 10 ≠ 6 + 3
    print(f"  ✅ SummaryMatrixRow → serial={row.serial}, arithmetic_warning detected")

    # ConfidenceScore labelling
    cs = ConfidenceScore(total=0.87, field_completeness=1.0, body_quality=0.8,
                         reference_code=1.0, hierarchy_depth=1.0,
                         date_presence=1.0, person_info=1.0, money_info=0.0)
    assert cs.label == "HIGH"
    print(f"  ✅ ConfidenceScore → {cs.total:.0%} → label={cs.label}")

    # QualityGateResult emoji
    qg = QualityGateResult(passed=True, confidence=0.91, message="All good")
    assert qg.status_emoji == "✅"
    print(f"  ✅ QualityGateResult → {qg.status_emoji} confidence={qg.confidence:.0%}")

    # KeyHealthReport
    khr = KeyHealthReport(
        gemini_keys=[SingleKeyStatus(key_id="Gemini_Key1", provider="Gemini", status=KeyStatus.ACTIVE)],
        github_keys=[SingleKeyStatus(key_id="GH_Key1",     provider="GitHub", status=KeyStatus.RATE_LIMITED)],
    )
    assert khr.active_gemini_count == 1
    assert khr.active_github_count == 0
    assert khr.has_any_active_key
    print(f"  ✅ KeyHealthReport → {khr.active_gemini_count} active Gemini key(s)")

    # DailySnapshot top_province
    snap = DailySnapshot(
        report_date="2026-03-18",
        province_summaries=[
            ProvinceSummary(province="WESTERN",  total_incidents=42),
            ProvinceSummary(province="SOUTHERN", total_incidents=18),
        ]
    )
    assert snap.top_province == "WESTERN"
    print(f"  ✅ DailySnapshot → top_province={snap.top_province}")

    print("\n✅ All self-tests passed!")
