# Known reproduction gaps and scope

This page distinguishes the uploaded configuration, representative examples, and inputs needed for reruns. The repository remains a general software project; values below describe its code and data, not a claimed new run. No scientific setting or saved numerical result has been changed during the repository cleanup.

| Area | What is present | What remains unresolved |
| --- | --- | --- |
| Full extraction model | The main analysis used GPT-4o at temperature 0.5/seed 42. The uploaded script actively selects Llama 3.1 at temperature 0.5 because it was last configured for the separate exploratory comparison; the GPT-4o assignment remains commented. `main.py` writes a Llama-named DOCX. | Users can select the existing GPT-4o assignment for a new main-configuration run and must record that choice; the current default/output filename alone does not identify the model used for historical results. No scientific model setting was changed in the cleanup. |
| Statistical parser | `JsonOutputParser` creates format instructions; `extract_evidence` does not invoke the parser on the model output. | The description of JSON parsing is stronger than what the active chain enforces. The output may need manual inspection. |
| Study inputs and FAISS | 14 annotation DOCX files, 45 GPT-4o extraction DOCX files, six Llama DOCX files, and baseline output archives are representative materials. | The code can regenerate per-study indexes and extraction outputs when lawful source PDFs, API/local model access, and run settings are supplied. Exact historical cohort totals also need the original 26-trial/18-study input manifests, reference/adjudication records, and run provenance, which are not checked in. Counts of sample files do not prove cohort membership. |
| Evaluation | Item-level evaluation notebook creates its Python module at runtime and exports JSON/CSV/XLSX. RAGAS notebook contains interactive cells and saved displays. | The evaluation default thresholds differ from cell-8 explicit settings; the RAGAS notebook uses a hard-coded question for a default file with another study name. Neither notebook is a complete batch runner. Several RAGAS cells use different judge models/settings. |
| Baseline ablations | Two baseline notebooks and 14 outputs per ZIP archive. | Their active temperatures differ (0.5 vs 0), and neither supplies a fixed seed. Do not assume the saved examples represent otherwise identical conditions or that the first indexed page always equals an abstract. No aggregate ablation script/results table is included. |
| FHIR-aligned generation | Pydantic `EvidenceGraph` schema, GPT-4o call, and five DOCX examples. | The heading in generated DOCX files uses legacy compliance language. The object is intermediate, and the schema does not check global reference consistency/ID uniqueness. The example has a fixed output filename independent of input. |
| Native FHIR serialization | Separate deterministic CLI and five representative native JSON Bundles. It reproduces the five committed Bundle bytes. | `ArtifactAssessment` is optional in the proposed intermediate model for future evidence-quality assessments. None were performed or claimed for this study, so its absence from these Bundles is expected. The current serializer does not map it if a future input includes one. |
| External FHIR validation | Three historical logs and five Bundles are representative examples; one log shows an earlier failure and two show later success. Validator 6.9.9 / Java 23.0.2 / R5 5.0.0 are recorded. | The serializer and validator workflow can produce additional Bundle/report files from intermediate inputs. Recreating the exact historical 10-output subset still requires its original inputs and run manifest. The validator JAR is external; profile-level validation was not performed. |
| Aggregation/figures | The repository code produced per-study results and evaluations; aggregate compilation was done separately. The tree contains representative extraction/native examples. | The separate compilation procedure and complete source tables for cohort statistics, confidence intervals, significance tests, F1 summary, cost/timing analysis, convergence figures, and full ablation comparison are not checked in. The exact historical aggregate still needs those inputs and the compilation record. |
| Environment | Direct package versions and a sanitized broad environment inventory. | Historical Python version, Tesseract/Poppler versions, OCR data, precise model snapshots, local Ollama digest, two notebook-package versions, and complete OS setup are unrecorded. |
| Security/provenance | Current notebook credential literals were removed; generated examples retained. | Credential-shaped values remain in prior public Git history. Rotate affected OpenAI and Anthropic credentials and consider a separately planned history purge. The new snapshot cannot erase prior clones. |

## Output map

- **Source input:** user-supplied PDF under ignored `inputs/` (not committed).
- **Intermediate parsed/indexed data:** optional parsed DOCX under ignored `work/`, FAISS files in a named `*_index/` directory; no historical indexes in the repository.
- **Extraction outputs:** `GPT_4o_extractions_full_pipe/`, `Llama 3.1 extractions/`, plus output text files inside the two baseline ZIPs. Historical files are retained as supplied.
- **Reference/evaluation input:** `Annotations/` contains 14 DOCX annotations. Run-specific adjudication CSV/XLSX/JSON is absent from the source tree.
- **FHIR-aligned intermediate:** `FHIR_aligned_generations/*.docx` (five saved examples).
- **Native FHIR:** `Native_FHIR_transformation/*.json` (five saved examples).
- **Validation reports:** three `Native_FHIR_transformation/*validation_report*.txt` files; only two are final success logs.
- **Aggregate tables/figures:** compiled separately from the per-study code; the compilation procedure and complete input tables are not checked in. Per-study files can be regenerated with supplied inputs; do not infer historical aggregate totals from the example collection.

## Security and data handling

Credential literals were present in notebook source and a prior Git blob. They were not printed or copied into the new documentation. Sanitizing the current tree does not remove their historical exposure; rotate the credentials. `.gitignore` prevents common future secret/cache commits but does not remove anything already tracked. No third-party source PDFs were added, and the software MIT license does not license research articles, annotations, or generated content from third parties.

The serializer uses restricted Python `eval` on its expected constructor representation; FAISS loads pickled index data. Both require trusted local inputs. The old `requirements.txt` included non-portable package URLs with build-machine paths; they were converted to a sanitized historical record and removed from installation requirements. No repository history was rewritten.

## Work deliberately deferred

Changing the active extraction model, JSON parsing behavior, retrieval settings, evaluation thresholds, FHIR mappings, statistical formulas, or saved outputs could alter scientific behavior. These need a separately verified scientific decision. A release/tag is optional; the Git commit SHA is the traceable source snapshot. Add missing source/reference manifests, the separate aggregate compilation procedure, and validation reports only when authentic materials are available. Do not synthesize replacement results.
