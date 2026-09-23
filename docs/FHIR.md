# FHIR representation, serialization, and validation

FIRE-EVIDENCE has three separate FHIR-related operations. They must not be conflated:

1. **LLM-generated FHIR-aligned intermediate:** `FHIR_aligned/latest_LLM.py` prompts GPT-4o for a Pydantic-parsed `EvidenceGraph`. `FHIR_aligned/pipeline.py` saves `str(graph_entities)` in DOCX. The schema uses resource-oriented names and local references, but this constructor-style graph is **not** native FHIR R5 JSON and has not been validated by the HL7 Validator.
2. **Native FHIR serialization:** `FHIR_compliant/FHIR-compliant_script.py` reads trusted intermediate DOCX/text, parses constructor assignments, maps supported objects to FHIR resource fields, rewrites known references, and writes a collection `Bundle`. This step does not call a model or validator. It runs lightweight local checks for Bundle/resource identity and unique `fullUrl`s.
3. **External base FHIR R5 validation:** Run the independent HL7 FHIR Validator CLI against the generated JSON using `-version 5.0.0`. This checks the generated Bundle against base R5. It is not equivalent to the serializer's checks and does not assert EBMonFHIR profile conformance.

The [ordered guide](REPRODUCIBILITY.md#7-fhir-aligned-evidence-generation) shows the inputs and command for each step.

## Intermediate contract

`FHIR_aligned/updated_graph.py` defines `EvidenceGraph` with a `ResearchStudy`, `Group` list, four `EvidenceVariable` fields for population/intervention/comparator/outcome, `Evidence` results, a `Citation`, and optional `ArtifactAssessment` objects for evidence-quality assessments. No such quality assessment was performed in the study; their optional presence in the proposed model does not imply they were generated for these examples. The LLM prompt in `latest_LLM.py` requests deterministic-looking IDs and references. Pydantic enforces field types; there is no custom graph-wide validator for ID uniqueness or reference resolution in `updated_graph.py`. `LLM_MODEL` is read into a module variable but the current call takes the function default `gpt-4o`. Each input call is LLM/API-dependent and may vary.

Five committed examples are in [`FHIR_aligned_generations/`](../FHIR_aligned_generations/). They are DOCX files containing the printed Pydantic object representation. The fixed output filename in `FHIR_aligned/pipeline.py` is `batur-2025_computable.docx`, regardless of the text embedded by `main.py`; users must manage names when running other studies. The legacy document heading says “FHIR Compliant Standard Knowledge,” but the body remains an intermediate representation until serialization and validation.

## Deterministic mapping actually implemented

| Intermediate object | Native output |
| --- | --- |
| `research_study` | `ResearchStudy`, with design/context largely in `description`; groups become `comparisonGroup` references, citation becomes `relatedArtifact`. |
| `groups` | `Group`; descriptions/characteristics mapped to R5-compatible fields. |
| `population`, `intervention`, `comparator`, `outcome` | Four `EvidenceVariable` resources. |
| `evidence_results` | `Evidence`; variable roles/references and statistic/sample-size elements are mapped. |
| `citation` | `Citation`; DOI/PMID become identifiers where present. |
| `artifact_assessments` | Optional in the intermediate schema. No evidence-quality assessments were performed for the study examples, so no such native resources are expected. The current `convert()` function does not serialize them if supplied in a future use. |

The serializer emits a collection `Bundle` with `https://fire-evidence.example.org/fhir/...` `fullUrl` identifiers. This host is a placeholder namespace in the code, not a deployed FHIR server. Known local references are rewritten to those full URLs. Generated XHTML narratives and selected code displays support base validation; statistic type is text-only where exact terminology codes were uncertain. Numeric strings are parsed conservatively by the existing code. Do not treat the mapping as lossless: not every intermediate field receives a distinct native field.

The serializer uses restricted `eval` for constructor expressions and `allow_dangerous_deserialization` appears in FAISS loading. These interfaces are for trusted local files only. The evaluated expression has no builtins, but that is not an assertion that arbitrary untrusted input is safe.

## Run the separate serializer

From the repository root, with `python-docx==1.1.2` installed:

```console
python FHIR_compliant/FHIR-compliant_script.py FHIR_aligned_generations/batur_computable.docx --outdir work/native_fhir
```

The script writes `work/native_fhir/batur_computable_fhir_bundle.json` and prints the result of its **basic local pre-validation**. Five intermediate examples were converted during this audit and matched the five committed native JSON files exactly, including their bytes. Their `Bundle.entry` resource types are ResearchStudy, Group, EvidenceVariable, Evidence, and Citation. The serializer does not output ArtifactAssessment resources; this does not leave out a result claimed for the study.

## Run the external HL7 validator

Supply the Validator CLI JAR yourself as `validator_cli.jar`. The repo does not include it. Match Validator **6.9.9** (Git `f50ef63a178c`), Java **23.0.2**, and base FHIR R5 **5.0.0** to the recorded run, then invoke:

```console
java -jar validator_cli.jar work/native_fhir/batur_computable_fhir_bundle.json -version 5.0.0 > work/native_fhir/batur_validation_report.txt 2>&1
```

The validator may fetch packages and terminology from network services. Confirm its version banner and inspect errors, warnings, and notes in the log. A “Success” line with warnings is a successful base validation with caveats, not clean profile-level conformance. The validator executable, package cache, and terminology-service state were not archived, so future diagnostics may differ.

[`Native_FHIR_transformation/`](../Native_FHIR_transformation/) contains five native JSON Bundles and three historical logs. `batur_validation_report_v2.txt` is an earlier **failure** (10 errors); do not cite it as a successful result. `batur_validation_report_v3.txt` records 0 errors, 2 warnings, 4 notes. `updated3_validation_report_v3.txt` records 0 errors, 3 warnings, 6 notes. The supplied technical materials describe a 10-output zero-error native validation subset. The repository intentionally contains representative examples: five Bundle JSON files and three historical reports. Additional Bundles and reports can be generated from their intermediate inputs with the serializer and validator; reproducing the exact historical 10-output subset also requires those original inputs and its run manifest.

The validation here is base FHIR R5 only. It does not demonstrate EBMonFHIR profile-level validation or all possible clinical/semantic constraints. No profile package, pinned terminology snapshot, or complete validator command automation is supplied.
