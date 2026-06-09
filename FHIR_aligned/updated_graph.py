from typing import List, Optional
from pydantic import BaseModel, Field


# --------------------------------------------------
# Citation Resource
# --------------------------------------------------
class PublicationForm(BaseModel):
    journal: Optional[str] = None
    issue: Optional[str] = None
    volume: Optional[str] = None
    current_status:Optional[str] = None
    publication_date: Optional[str] = None

class Citation(BaseModel):
    resourceType: str = "Citation"
    id: Optional[str] = None
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    doi: Optional[str] = None
    publicationForm: Optional[PublicationForm] = None

# --------------------------------------------------
# ResearchStudy Resource
# --------------------------------------------------
class ResearchStudy(BaseModel):
    resourceType: str = "ResearchStudy"
    id: Optional[str] = None
    title: Optional[str] = None
    study_design: Optional[str] = None
    enrollment: Optional[str] = None
    setting: Optional[str] = None
    follow_up_duration: Optional[str] = None
    allocation_concealment: Optional[str] = None
    blinding: Optional[str] = None
    intention_to_treat: Optional[str] = None
    funding_source: Optional[str] = None
    groups: List["Group"] = Field(default_factory=list)
    citations: List["Citation"] = Field(default_factory=list)

# --------------------------------------------------
# Group Resource
# --------------------------------------------------
class Characteristic(BaseModel):
    id: Optional[str] = None
    description: str

class Group(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    characteristics: List[Characteristic] = Field(default_factory=list)

# --------------------------------------------------
# EvidenceVariable Resource
# --------------------------------------------------
class EvidenceVariable(BaseModel):
    resourceType: str = "EvidenceVariable"
    id: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    characteristics: List[Characteristic] = Field(default_factory=list)

# --------------------------------------------------
# Evidence Resource
# --------------------------------------------------
class VariableDefinition(BaseModel):
    variableRole: str  # population | exposure | comparator | outcome | group
    reference: str     # EvidenceVariable/<id> or Group/<id>



class SampleSize(BaseModel):
    description: Optional[str] = None
    value: Optional[str] = None

class Statistic(BaseModel):
    description: str
    statisticType: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    event_rate: Optional[str] = None
    sample_size: Optional[SampleSize] = None

class Evidence(BaseModel):
    resourceType: str = "Evidence"
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    variable_definitions: List[VariableDefinition] = Field(default_factory=list)
    statistics: List[Statistic] = Field(default_factory=list)
    generation_model : Optional[str] = None

# --------------------------------------------------
# ArtifactAssessment Resource
# --------------------------------------------------
class ArtifactAssessment(BaseModel):
    resourceType: str = "ArtifactAssessment"
    id: Optional[str] = None
    assessment_type: Optional[str] = None
    score: Optional[str] = None
    related_artifact: Optional[str] = None

# --------------------------------------------------
# EvidenceReport Resource
# --------------------------------------------------


# --------------------------------------------------
# Complete Evidence Graph
# --------------------------------------------------
class EvidenceGraph(BaseModel):
    
    research_study: ResearchStudy
    groups: List[Group] = Field(default_factory=list)
    evidence_results: List[Evidence] = Field(default_factory=list)
    artifact_assessments: Optional[List[ArtifactAssessment]] = None
    population: EvidenceVariable
    intervention: EvidenceVariable
    comparator: EvidenceVariable
    outcome: EvidenceVariable
    citation: Citation
    