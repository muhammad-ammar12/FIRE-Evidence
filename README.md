# FIRE-EVIDENCE

![FIRE-EVIDENCE: clinical study reports to structured evidence and FHIR R5](assets/fire-evidence-poster.png)

FIRE-EVIDENCE processes clinical-study PDFs into structured evidence and a constrained FHIR-aligned evidence graph. It includes evidence-extraction code, reference-based evaluation notebooks, a separate deterministic native FHIR R5 serializer, and representative outputs. The implementation was developed for evidence synthesis in women's health.

**Start here:** [Reproducibility guide](docs/REPRODUCIBILITY.md) · [Software and model configuration](docs/SOFTWARE.md) · [FHIR workflow](docs/FHIR.md).

## Overview

```text
PDF / clinical-study report
  -> layout-aware text / OCR and table processing
  -> page-level embeddings and FAISS retrieval
  -> structured evidence extraction
       -> reference-based evaluation and source-faithfulness evaluation
       -> LLM-generated, constrained FHIR-aligned EvidenceGraph
            -> separate deterministic native FHIR R5 Bundle serialization
            -> separate HL7 FHIR Validator invocation
```

Evaluation and standardization are separate workflows; there is no automatic end-to-end scheduler or evaluation gate. The intermediate EvidenceGraph is not native FHIR. Serialization and external validation are also distinct steps.

This repository contains the source code used for the reported analyses. The analyses were originally executed in local and/or Google Colab environments, and the repository was subsequently created to make the implementation publicly available. See [snapshot provenance](docs/PROVENANCE.md) for the source commit, cleanup scope, and exact-checkout identification.

**Reproduction scope:** this repository intentionally contains code and representative outputs, rather than a full copy of every input and run artifact. GPT-4o was used for the main extraction analysis; the uploaded script currently selects Llama 3.1 because it was configured for the separate exploratory comparison. The GPT-4o setting remains in the code as a commented alternative. Per-study outputs can be regenerated when the corresponding lawful source PDFs, reference data, model access, and run settings are supplied. The per-study results and evaluations were produced with the repository code; aggregate compilation was performed separately. Exact historical totals require the original cohort/adjudication inputs and that separate compilation record.

## Key capabilities

- Digital-PDF text extraction with PyMuPDF, scanned-PDF OCR with Tesseract, and table extraction with pdfplumber.
- Page-level OpenAI embeddings, a local FAISS index, and two retrieval/extraction chains for PICO information and statistical results.
- Ground-truth-focused correctness/completeness evaluation, expert adjudication, and a separate RAGAS notebook.
- Pydantic-parsed, LLM-generated FHIR-aligned evidence graphs.
- Offline conversion of saved intermediate DOCX/text representations to native FHIR R5 Bundles.
- Saved extraction examples, baseline outputs, native Bundles, and historical validation reports.

## Repository structure

| Path | Purpose |
| --- | --- |
| [Extraction pipeline/](Extraction%20pipeline/) | PDF loading, page indexing, prompts, extraction, and DOCX export. Files named `test_*` are implementation modules, not a test suite. |
| [Baseline_pipeline/](Baseline_pipeline/) | Full-retrieval and first-indexed-unit baseline notebooks. |
| [Evaluation_code/](Evaluation_code/) | Item-level evaluation/adjudication and RAGAS notebooks. |
| [FHIR_aligned/](FHIR_aligned/) | Intermediate schema, LLM prompt, and standardization example. |
| [FHIR_compliant/FHIR-compliant_script.py](FHIR_compliant/FHIR-compliant_script.py) | Separate deterministic DOCX/text-to-native-FHIR serializer and lightweight checks. |
| [Annotations/](Annotations/) | 14 reference DOCX files; not the complete research corpus. |
| [GPT_4o_extractions_full_pipe/](GPT_4o_extractions_full_pipe/) | 45 saved DOCX extraction files with extensionless filenames. |
| [Llama 3.1 extractions/](Llama%203.1%20extractions/) | Six saved DOCX comparison outputs; filenames do not end in `.docx`. |
| [FHIR_aligned_generations/](FHIR_aligned_generations/) | Five intermediate EvidenceGraph DOCX examples. |
| [Native_FHIR_transformation/](Native_FHIR_transformation/) | Five native Bundle JSON files and three historical validator logs. |
| [zero_shot_extractions.zip](zero_shot_extractions.zip), [RAG_ZERO_Abstract_extractions.zip](RAG_ZERO_Abstract_extractions.zip) | 14 text outputs per baseline archive. |
| [Extraction pipeline.zip](Extraction%20pipeline.zip) | Duplicate distribution of the six extraction source files; use the directory for development. |
| [assets/](assets/) | FIRE-EVIDENCE logo and repository poster. |
| [docs/](docs/) | Execution instructions, software configuration, FHIR boundaries, and provenance. |

## Installation

This is a collection of Python scripts and notebooks, not an installable Python package. From the repository root, create an isolated environment:

```console
python -m venv .venv
```

Activate it using `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in a POSIX shell, then install:

```console
python -m pip install -r requirements.txt
python -m pip check
```

For offline FHIR serialization only:

```console
python -m pip install -r requirements-fhir.txt
```

Known versions are preserved in the requirements and [environment record](docs/environment-record.txt). The two unrecorded notebook dependencies are explicitly unpinned. This is not a complete historical lockfile; see [software verification and limitations](docs/SOFTWARE.md).

## System requirements

- Python 3: the original exact interpreter version was not recorded. Audit checks used Python 3.12.14; this does not establish the historical Python version or universal platform support.
- For scanned PDFs: Tesseract executable and Poppler tools available to `pytesseract` and `pdf2image`. Their historical binary versions and OCR language configuration were not recorded.
- For external FHIR validation: Java and the separately obtained HL7 FHIR Validator JAR. Saved reports identify Java **23.0.2**, Validator **6.9.9** (`f50ef63a178c`), and base FHIR R5 **5.0.0**.
- The active full extraction configuration needs a local Ollama service serving the `llama3.1` model. Its server version and model digest are not recorded. OpenAI credentials are still needed for embeddings.
- Paid API access is required for OpenAI stages; optional Anthropic evaluation cells require separate access. No hardware/RAM minimum has been established.

## Environment variables

Supply your own `OPENAI_API_KEY` in the shell or notebook kernel. `ANTHROPIC_API_KEY` is only needed for the optional Anthropic RAGAS cells. [.env.example](.env.example) contains placeholders; creating `.env` alone does **not** load credentials into these scripts. The item-evaluation notebook supports Colab Secrets or a secure prompt. Never save credentials in notebook cells or outputs.

## Input data

Supply lawfully obtained clinical-study PDFs. The main extraction example expects `inputs/tanner.pdf`, labels the run `tanner-2025`, and writes into the current working directory. These defaults identify an example, not a complete study manifest. The loader selects OCR if neither of the first two sampled pages has extractable text, and appends table rows to page text. Mixed scanned/digital documents and image-only tables need inspection; there is no separate table-OCR algorithm.

Reference evaluation uses paired annotation/extraction DOCX files, including the extensionless saved DOCX outputs. Native serialization takes trusted intermediate DOCX or constructor-style text, not arbitrary JSON. Source article PDFs and FAISS indexes are not included. The software license does not grant rights to third-party publications or their content.

## Running FIRE-EVIDENCE

Run commands from the repository root. Read the [ordered guide](docs/REPRODUCIBILITY.md) before API calls or notebook execution.

| Stage | Entry point | Key prerequisite / output |
| --- | --- | --- |
| Document processing | `test_loading.extract_pdf_structured` and `write_to_word` | PDF to optional page-indexed DOCX; exact invocation in the guide. |
| Full extraction | `python "Extraction pipeline/main.py"` | `inputs/tanner.pdf`, embeddings access and Ollama; writes `tanner-2025_index/` and `tanner-2025_extraction_LLama3.1`. **The uploaded default is Llama 3.1; the main extraction analysis used GPT-4o.** |
| Evaluation | `python -m jupyterlab Evaluation_code/Evaluation_framework.ipynb` | Paired DOCX inputs; follow cells in the guide for JSON/CSV/XLSX outputs and adjudication. |
| Source faithfulness | `python -m jupyterlab Evaluation_code/_RAGAS_Evaluation_pipeline.ipynb` | Trusted FAISS index, extraction, annotation; produces in-memory dataframes/saved cell displays. |
| Baselines | The two notebooks in `Baseline_pipeline/` | Trusted indexes; text outputs and optional combined JSON. |
| FHIR-aligned generation | `python FHIR_aligned/main.py` | Uses the embedded `pico_text` example and OpenAI; writes `batur-2025_computable.docx` in the working directory. |
| Native serialization | Command below | Existing intermediate example; no LLM/API call. |
| FHIR validation | Separate Java invocation in [FHIR.md](docs/FHIR.md) | External JAR required; serializer's basic checks are not HL7 validation. |

The included native example can be rebuilt without API calls:

```console
python FHIR_compliant/FHIR-compliant_script.py FHIR_aligned_generations/batur_computable.docx --outdir work/native_fhir
```

Output: `work/native_fhir/batur_computable_fhir_bundle.json`. All five supplied intermediate examples reproduced their committed native JSON during the audit. No claim of fresh HL7 validation follows from that comparison.

### Analysis and outputs

The evaluation notebook calculates item-level correctness/completeness and exports audit/adjudication files. Baseline notebooks produce extraction outputs. Per-study artifacts can be regenerated with the supplied workflows and required inputs. Aggregate compilation was performed separately from this repository. The checked-in tree does not include that compilation procedure or its full input tables for statistical summaries, confidence intervals, significance tests, aggregate F1, convergence figures, cost/timing summaries, or the full ablation analysis.

## Security, citation, and license

Use trusted local inputs: the serializer evaluates constructor-style expressions and FAISS loading enables pickle deserialization. Neither is a safe interface for untrusted uploads. Historical notebook credentials require rotation and a separately authorized history cleanup; removing them from the current files does not revoke them.

Use [CITATION.cff](CITATION.cff) and record the exact Git SHA with `git rev-parse HEAD`. Software is licensed under the [MIT License](LICENSE). No publication DOI, release date, or archive DOI is asserted.
