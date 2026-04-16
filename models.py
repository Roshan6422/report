
from pydantic import BaseModel, Field, field_validator


class IncidentRecord(BaseModel):
    """
    Official 8-field Sri Lanka Police institutional incident schema.
    Used for final PDF generation and database storage.
    """
    station: str = Field(..., description="Name of the Police Station (e.g., MATARA, FORT)")
    division: str = Field(..., description="Police Division (e.g., Matara Div., Colombo Central Div.)")
    date: str = Field(..., description="Date of occurrence (YYYY-MM-DD or official format)")
    time: str = Field(..., description="Time of occurrence (HH:MM or CTM/OTM time)")
    description: str = Field(..., description="Full English translated narrative of the incident")
    financial_loss: str = Field(default="Nil", description="Monetary value of loss/damage")
    status: str = Field(default="Confirmed", description="Investigation status (e.g., Confirmed, Ongoing, Arrested)")
    victim_suspect_names: str = Field(default="N/A", description="Names of involved parties")

    # Optional metadata for routing
    province: str | None = "WESTERN PROVINCE"
    category_num: str | None = "00"
    origin_block: str | None = "General"

    @field_validator("station")
    def clean_station(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("province")
    def normalize_province(cls, v: str | None) -> str:
        if not v: return "WESTERN PROVINCE"
        return v.strip().upper()

class CategorizationOutput(BaseModel):
    """
    AI Output for incident classification.
    """
    category_num: str = Field(..., pattern=r"^\d{2}$")
    category_name: str
    is_security_related: bool = False
    confidence: float = Field(ge=0.0, le=1.0)

class TranslationRefinement(BaseModel):
    """
    AI output for the linguistic refinement stage.
    """
    refined_narrative: str
    technical_terms_fixed: list[str]
    detected_station: str | None = None
    detected_date: str | None = None

class AnalyticsInsight(BaseModel):
    """
    Summary for dashboard charts.
    """
    province: str
    total_count: int
    security_count: int
    general_count: int
    top_categories: list[str]
