from pydantic import BaseModel, Field
from typing import List, Optional


class EmbeddedTactic(BaseModel):
    phrase: str
    tactic: str  # e.g., 'Loaded Language', 'Sales Tactic'
    explanation: str
    type: str  # e.g., 'framing', 'Urgency'


class SynthesizedSentence(BaseModel):
    sentence: str
    bias_score: float = Field(..., ge=-1.0, le=1.0)
    justification: str
    tactics: List[EmbeddedTactic]


class Omission(BaseModel):
    omitted_perspective: str
    potential_impact: str


class SynthesisResult(BaseModel):
    foundational_assumptions: List[str]
    synthesized_text: List[SynthesizedSentence]
    omissions: Optional[List[Omission]] = None


class SynthesisRequest(BaseModel):
    text: str
