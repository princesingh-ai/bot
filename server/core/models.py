from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ProblemSearchFilters(BaseModel):
    """
    Defines all optional filters that can be applied
    while searching problem statements.
    Each field is optional and applied only if provided.
    """
    problem_id: Optional[str] = Field(default=None, description="Exact match for problem ID")
    title: Optional[str] = Field(default=None, description="Partial match for title")
    technology_bucket: Optional[str] = Field(default=None, description="Partial match for technology bucket")
    category: Optional[str] = Field(default=None, description="Partial match for category")
    description: Optional[str] = Field(default=None, description="Partial match for description")
    organization: Optional[str] = Field(default=None, description="Partial match for organization")


class ProblemSearchResponse(BaseModel):
    """
    Standard response structure for problem search.
    - count   : number of matching records
    - results : list of problem statement records
    """
    count: int = Field(description="Number of matching records")
    results: List[Dict[str, Any]] = Field(description="List of problem statement records")


class InnovationProcessFilters(BaseModel):
    process_no: Optional[int] = Field(default=None, description="Filter by process number")
    stages: bool = Field(default=False, description="Return stages if true")
    field: Optional[str] = Field(default=None, description="Specific field to target")


class InnovationProcessResponse(BaseModel):
    count: int = Field(description="Number of matching records")
    results: List[Dict[str, Any]] = Field(description="List of records")


class CrieyaPreincubationHubQARequest(BaseModel):
    question: str = Field(description="Question about CRIEYA pre-incubation hub")


class CrieyaPreincubationHubQAResponse(BaseModel):
    answer: str = Field(description="Answer to the question")
    source: str = Field(description="Source document")


class CrieyaFocusQARequest(BaseModel):
    question: str = Field(description="Question about CRIEYA focus")


class CrieyaFocusQAResponse(BaseModel):
    answer: str = Field(description="Answer to the question")
    source: str = Field(description="Source document")


class TrlLevelRequest(BaseModel):
    question: str = Field(description="Question about Technology Readiness Levels")


class TrlLevelResponse(BaseModel):
    answer: str = Field(description="Answer to the question")
    source: str = Field(description="Source document")