"""
models.py
=========
Pydantic schemas for Sri Lanka Police incident data.
Used by desktop_pipeline.py, database modules, and report engines.
"""
from __future__ import annotations  # Allows str | None syntax on Python 3.9+

import re
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class IncidentRecord(BaseModel):
    """
    Official 8-field Sri Lanka Police institutional incident schema.
    Used for final PDF generation and database storage.
    """
    model_config = ConfigDict(
        extra="ignore",  # Ignore extra fields from AI output to prevent crashes
        validate_assignment=True,
        str_strip_whitespace=True
    )

    station: str = Field(..., description="Name of the Police Station (e.g., MATARA, FORT)")
    division: str = Field(default="Unknown", description="Police Division (e.g., Matara Div.)")
    date: str = Field(..., description="Date of occurrence (YYYY-MM-DD or official format)")
    time: str = Field(..., description="Time of occurrence (HH:MM or CTM/OTM time)")
    description: str = Field(..., description="Full English translated narrative")
    financial_loss: str = Field(default="Nil", description="Monetary value (e.g., Rs. 40,000/=)")
    status: str = Field(default="Confirmed", description="Investigation status")
    victim_suspect_names: str = Field(default="N/A", description="Names of involved parties")

    # Optional metadata for routing
    province: str | None = "WESTERN PROVINCE"
    category_num: str | None = "00"
    origin_block: str | None = "General"

    @field_validator("station")
    @classmethod
    def clean_station(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("province")
    @classmethod
    def normalize_province(cls, v: str | None) -> str:
        if not v:
            return "WESTERN PROVINCE"
        
        v = v.strip().upper()
        # Handle common abbreviations
        if "N. WESTERN" in v or "WAYAMBA" in v:
            return "NORTH WESTERN PROVINCE"
        if "N. CENTRAL" in v or "RAJARATA" in v:
            return "NORTH CENTRAL PROVINCE"
        if "SABARA" in v:
            return "SABARAGAMUWA PROVINCE"
        
        # Ensure PROVINCE suffix
        if "PROVINCE" not in v:
            return f"{v} PROVINCE"
        return v

    @field_validator("category_num")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        if not v:
            return None
        # Ensure it's a 2-digit number between 01 and 29
        if not re.match(r"^\d{2}$", v):
            raise ValueError("Category must be 2 digits (e.g., '04')")
        num = int(v)
        if not (1 <= num <= 28):
            raise ValueError("Category must be between 01 and 29")
        return v.zfill(2)


class CategorizationOutput(BaseModel):
    """
    AI Output for incident classification.
    """
    model_config = ConfigDict(extra="ignore")

    category_num: str = Field(..., pattern=r"^\d{2}$", description="01-29")
    category_name: str
    is_security_related: bool = False
    confidence: float = Field(ge=0.0, le=1.0)


class TranslationRefinement(BaseModel):
    """
    AI output for the linguistic refinement stage.
    """
    model_config = ConfigDict(extra="ignore")

    refined_narrative: str
    technical_terms_fixed: list[str] = []
    detected_station: str | None = None
    detected_date: str | None = None


class AnalyticsInsight(BaseModel):
    """
    Summary for dashboard charts.
    """
    model_config = ConfigDict(extra="ignore")

    province: str
    total_count: int
    security_count: int = 0
    general_count: int = 0
    top_categories: list[str] = []