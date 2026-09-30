from pydantic import BaseModel, Field
from typing import List, Optional


class Document(BaseModel):
    name: str
    text: str


class CaseRequest(BaseModel):
    documents: List[Document] = Field(min_length=1)


class Claim(BaseModel):
    topic: str
    value: str
    source: str
    evidence: str


class Contradiction(BaseModel):
    topic: str
    values: List[str]
    sources: List[str]
    explanation: str
    severity: str = "HIGH"


class EvidenceGap(BaseModel):
    topic: str
    claim: str
    reason: str
    severity: str = "MEDIUM"
