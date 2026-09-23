import updated_graph as UG
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
import os
import json
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI



# Credentials must be supplied through OPENAI_API_KEY in the environment.

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
client = OpenAI()



def up_Format_evidence(text: str, llm_model: str = "gpt-4o", max_tokens: int = 2500)-> UG.EvidenceGraph:
    parser = PydanticOutputParser(pydantic_object=UG.EvidenceGraph)

    """
    Extracts clinical trial evidence from text into a fully nested EvidenceGraph using LLM.
    """

    # JSON template for LLM to follow
    json_template = {
  "research_study": {
    "resourceType": "ResearchStudy",
    "id": "",
    "title": "",
    "study_design": "",
    "enrollment": "",
    "setting": "",
    "follow_up_duration": "",
    "allocation_concealment": "",
    "blinding": "",
    "intention_to_treat": "",
    "funding_source": "",
    "groups": [
      {
        "id": "",
        "type": "",
        "description": "",
        "characteristics": [
          {
            "id": "",
            "description": ""
          }
        ]
      }
    ],
    "citations": [
      {
        "resourceType": "Citation",
        "id": "",
        "title": "",
        "authors": [],
        "pmid": "",
        "pmcid": "",
        "doi": "",
        "publicationForm": {
          "journal": "",
          "issue": "",
          "volume": "",
          "current_status": "",
          "publication_date": ""
        }
      }
    ]
  },

  "groups": [
    {
      "id": "",
      "type": "",
      "description": "",
      "characteristics": [
        {
          "id": "",
          "description": ""
        }
      ]
    }
  ],

  "evidence_results": [
    {
      "resourceType": "Evidence",
      "id": "",
      "title": "",
      "description": "",
      "variable_definitions": [
        {
          "variableRole": "population",
          "reference": ""
        },
        {
          "variableRole": "intervention",
          "reference": ""
        },
        {
          "variableRole": "comparator",
          "reference": ""
        },
        {
          "variableRole": "outcome",
          "reference": ""
        },
        {"variableRole": "group",
          "reference": ""}
      ],
      "statistics": [
        {
          "description": "",
          "statisticType": "",
          "value": "",
          "unit": "",
          "event_rate": "",
          "sample_size": {
            "description": "",
            "value": ""
          }
        }
      ],
      "generation_model": ""
    }
  ],

  "artifact_assessments": [
    {
      "resourceType": "ArtifactAssessment",
      "id": "",
      "assessment_type": "",
      "score": "",
      "related_artifact": ""
    }
  ],

  "population": {
    "resourceType": "EvidenceVariable",
    "id": "",
    "type": "",
    "description": "",
    "characteristics": [
      {
        "id": "",
        "description": ""
      }
    ]
  },

  "intervention": {
    "resourceType": "EvidenceVariable",
    "id": "",
    "type": "",
    "description": "",
    "characteristics": [
      {
        "id": "",
        "description": ""
      }
    ]
  },

  "comparator": {
    "resourceType": "EvidenceVariable",
    "id": "",
    "type": "",
    "description": "",
    "characteristics": [
      {
        "id": "",
        "description": ""
      }
    ]
  },

  "outcome": {
    "resourceType": "EvidenceVariable",
    "id": "",
    "type": "",
    "description": "",
    "characteristics": [
      {
        "id": "",
        "description": ""
      }
    ]
  },

  "citation": {
    "resourceType": "Citation",
    "id": "",
    "title": "",
    "authors": [],
    "pmid": "",
    "pmcid": "",
    "doi": "",
    "publicationForm": {
      "journal": "",
      "issue": "",
      "volume": "",
      "current_status": "",
      "publication_date": ""
    }
  }
}

    # Prompt instructions for LLM
    prompt = f"""
You are a biomedical evidence extraction assistant. Your task is to convert a clinical or biomedical study description into a structured JSON object that follows the EvidenceGraph schema.

Focus on identifying study entities and relationships. The output must represent the study as a structured evidence graph.

Return only valid JSON following the schema provided in the JSON template.

----------------------------------------------------------------------
GENERAL EXTRACTION PRINCIPLES
----------------------------------------------------------------------

The study should be modeled as a structured evidence graph composed of:

- Citation → publication metadata
- ResearchStudy → study design and context
- Groups → study arms or cohorts
- EvidenceVariables → PICO variables
- Evidence → outcome results
- ArtifactAssessment → optional quality assessments

The graph should be internally consistent and references should use meaningful IDs.

---------------------------------------------------------------------- 
ID GENERATION RULES
----------------------------------------------------------------------

All major objects must have meaningful deterministic IDs.

Use the following ID conventions:

Citation:
citation1

ResearchStudy:
study1

Groups:
group1
group2
group3

EvidenceVariables:
population1
intervention1
comparator1
outcome1

Evidence objects:
evidence1
evidence2

Characteristics:
char1
char2
char3

Artifact assessments:
assessment1

IDs should be unique within the JSON.

---------------------------------------------------------------------- 
REFERENCE RULES
----------------------------------------------------------------------

References must follow the format:

EvidenceVariable/<id>
Group/<id>

Examples:

EvidenceVariable/population1
EvidenceVariable/intervention1
Group/group1

---------------------------------------------------------------------- 
1. CITATION
----------------------------------------------------------------------

The Citation resource captures bibliographic information.

Extract:

- title
- authors
- pmid
- pmcid
- doi

publicationForm contains journal metadata:

publicationForm:
- journal
- issue
- volume
- current_status (published, ahead-of-print, etc.)
- publication_date

Example structure:

Citation → describes the publication of the study.

---------------------------------------------------------------------- 
2. RESEARCH STUDY
----------------------------------------------------------------------

ResearchStudy describes the design and context of the study.

Extract:

- title
- study_design (randomized controlled trial, cohort study, etc.)
- enrollment (number of participants)
- setting (hospital, multicenter, outpatient, etc.)
- follow_up_duration
- allocation_concealment
- blinding
- intention_to_treat
- funding_source

The study may contain one or more citations describing the publication.

Store these in:

research_study.Citation

---------------------------------------------------------------------- 
3. GROUPS
----------------------------------------------------------------------

Groups represent the actual participant arms or cohorts within the study.

Examples:

- intervention arm
- placebo arm
- control group
- subgroup analysis cohort

Each group contains:

- id
- type (intervention-arm, comparator-arm, subgroup, cohort)
- description
- characteristics

Characteristics describe **properties of participants in that group**.

Examples:

- number of participants
- baseline demographics
- treatment received
- subgroup definition

Example:

"group1": Metformin treatment arm  
"group2": Placebo arm

---------------------------------------------------------------------- 
4. EVIDENCE VARIABLES
----------------------------------------------------------------------

EvidenceVariable represents **conceptual variables used in the study question**.

These correspond to PICO elements:

- population
- intervention
- comparator
- outcome

Each EvidenceVariable contains:

- id
- type
- description
- characteristics

Characteristics define **the variable itself**, not the participants.

Examples:

Population characteristics:
- age range
- disease condition
- eligibility criteria

Intervention characteristics:
- drug dosage
- treatment duration

Outcome characteristics:
- measurement definition
- timepoint of measurement

---------------------------------------------------------------------- 
IMPORTANT DISTINCTION
----------------------------------------------------------------------

Group characteristics describe **participants in a specific study arm**.

EvidenceVariable characteristics describe **definitions of variables used in the study question**.

Example:

EvidenceVariable intervention:
"Metformin therapy"

Characteristics:
- dosage 500 mg twice daily
- treatment duration 12 months

Group intervention arm:
Participants receiving metformin

Characteristics:
- 250 participants
- mean age 58 years

---------------------------------------------------------------------- 
5. EVIDENCE
----------------------------------------------------------------------

Evidence objects represent measured results of the study.

Each Evidence contains:

- id
- title
- description
- generation_model (leave empty unless specified)
- variable_definitions
- statistics

variable_definitions define which variables are connected to the evidence.

Each variable_definition contains:

variableRole:
population
intervention
comparator
outcome
group

reference:
EvidenceVariable/<id> or Group/<id>

---------------------------------------------------------------------- 
6. STATISTICS
----------------------------------------------------------------------

Each Evidence object contains a list of statistics describing study results.

Each statistic contains:

- description
- statisticType
- value
- unit
- event_rate
- sample_size

sample_size structure:

"sample_size":
{{
"description": "",
"value": ""
}}

Examples of statisticType:

- risk ratio
- hazard ratio
- odds ratio
- mean difference
- relative risk
- incidence rate

---------------------------------------------------------------------- 
7. ARTIFACT ASSESSMENT
----------------------------------------------------------------------

ArtifactAssessment represents quality or methodological evaluations.

Fields:

- assessment_type
- score
- related_artifact

Examples:

risk of bias  
certainty of evidence  
GRADE score

If no assessment information is present, set artifact_assessments to null.

---------------------------------------------------------------------- 
CHARACTERISTICS STRUCTURE
----------------------------------------------------------------------

All characteristics must follow this structure:

{{
"id": "",
"description": ""
}}

---------------------------------------------------------------------- 
JSON OUTPUT RULES
----------------------------------------------------------------------

Strict rules:

- Output valid JSON only.
- Do not include explanations.
- Do not add extra keys.
- Use empty strings "" when values are missing.
- Use lists [] for collections.
- All IDs must follow the defined ID conventions.
- References must match existing IDs.

---------------------------------------------------------------------- 
ENTITY MAPPING FROM TEXT
----------------------------------------------------------------------

Publication metadata → Citation  
Study design details → ResearchStudy  
Study arms → Groups  
Population definition → population EvidenceVariable  
Treatments → intervention EvidenceVariable  
Control treatments → comparator EvidenceVariable  
Measured endpoints → outcome EvidenceVariable  
Outcome measurements → Evidence.statistics  
Quality evaluations → ArtifactAssessment  

---------------------------------------------------------------------- 
JSON TEMPLATE
----------------------------------------------------------------------

{json.dumps(json_template, indent=2)}

---------------------------------------------------------------------- 
INPUT TEXT
----------------------------------------------------------------------

{text}

---------------------------------------------------------------------- 
OUTPUT
----------------------------------------------------------------------
"""

    # Call the LLM
    chat = ChatOpenAI(model_name=llm_model, temperature=0.0, max_tokens=max_tokens)
    resp = chat([
        SystemMessage(content="Output only valid JSON. No commentary."),
        HumanMessage(content=prompt)
    ])

    # Parse the response using the EvidenceGraph Pydantic model
    resp_text = resp.content.strip()
    return parser.parse(resp_text)