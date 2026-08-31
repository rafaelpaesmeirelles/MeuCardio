from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class AttachmentRef(BaseModel):
    kind: Literal["scientific_document", "patient_exam", "upload"]
    reference_id: str
    media_type: str | None = None
    sha256: str | None = None


class HeartTeamCaseCreate(BaseModel):
    question: str | None = Field(default=None, max_length=4000)
    analysis_scope: Literal["global", "specific"] = "global"
    selected_agents: list[str] = Field(default_factory=list, max_length=16)
    case_text: str | None = Field(default=None, max_length=30000)
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = Field(default=None, max_length=40)
    symptoms: list[str] = Field(default_factory=list, max_length=100)
    vital_signs: dict[str, Any] = Field(default_factory=dict)
    comorbidities: list[str] = Field(default_factory=list, max_length=100)
    medications: list[str] = Field(default_factory=list, max_length=200)
    allergies: list[str] = Field(default_factory=list, max_length=100)
    laboratory_tests: list[dict[str, Any]] = Field(default_factory=list, max_length=500)
    attachments: list[AttachmentRef] = Field(default_factory=list, max_length=25)
    source_patient_id: int | None = None
    source_patient_authorized: bool = False

    @field_validator("selected_agents")
    @classmethod
    def unique_agents(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))


class HeartTeamCasePatch(BaseModel):
    question: str | None = Field(default=None, max_length=4000)
    selected_agents: list[str] | None = Field(default=None, max_length=16)
    input_data: dict[str, Any] | None = None


class AnalyzeRequest(BaseModel):
    confirm_deidentified: bool
    confirm_medical_review: bool


class SuggestionReviewRequest(BaseModel):
    decision: Literal["accepted", "rejected", "edited"]
    final_text: str | None = Field(default=None, max_length=12000)
    note: str | None = Field(default=None, max_length=2000)


class FinalReviewRequest(BaseModel):
    decision: Literal["accepted", "rejected"]
    medical_responsibility_confirmed: bool
    human_decisions_confirmed: bool
    note: str | None = Field(default=None, max_length=4000)

