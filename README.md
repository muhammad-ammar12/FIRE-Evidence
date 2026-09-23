# FIRE-EVIDENCE

![FIRE-EVIDENCE: clinical study reports to structured evidence and FHIR R5](assets/fire-evidence-poster.png)

FIRE-EVIDENCE is a research pipeline for extracting structured evidence from clinical-study reports, evaluating the extracted evidence, representing it using a constrained FHIR-aligned evidence model, and converting that representation into native FHIR R5 resources for validation. The workflow is model-agnostic: users can select the language model, provider, temperature, seed, and related settings at the model-configuration points in the scripts and notebooks.

**Documentation:** [Step-by-step user guide](docs/USER_GUIDE.md) · [Reported configuration](docs/CONFIGURATION.md) · [FHIR workflow](docs/FHIR.md)

## Workflow

```text
Clinical-study PDF
  -> document processing, OCR, and table extraction
  -> page-level embedding and FAISS retrieval
  -> structured evidence extraction
  -> correctness/completeness and source-faithfulness evaluation
  -> LLM-generated FHIR-aligned evidence model
  -> native FHIR R5 Bundle serialization
  -> HL7 FHIR Validator
```

The FHIR-aligned evidence model is an intermediate representation. Native FHIR R5 Bundle serialization is performed separately by `FHIR_compliant/FHIR-compliant_script.py`, followed by a separate HL7 FHIR Validator invocation.

## Key capabilities

- Digital-PDF text extraction with PyMuPDF.
- OCR for scanned PDFs with Tesseract and `pdf2image`/Poppler.
- Table extraction with `pdfplumber`.
- Page-level embeddings and FAISS retrieval.
- PICO and statistical-result extraction with configurable language models.
- Item-level correctness/completeness evaluation with [TRACE-Eval](https://github.com/muhammad-ammar12/TRACE-Eval), plus the included RAGAS evaluation notebook.
- Pydantic-constrained FHIR-aligned evidence generation.
- Conversion to native FHIR R5 `Bundle` resources.
- Base FHIR R5 validation with the HL7 FHIR Validator.

## Repository structure

| Path | Purpose |
| --- | --- |
| [Extraction pipeline/](Extraction%20pipeline/) | PDF processing, indexing, prompts, retrieval, and evidence extraction. |
| [Evaluation_code/](Evaluation_code/) | Source-faithfulness and context-recall evaluation with RAGAS. |
| [Baseline_pipeline/](Baseline_pipeline/) | Full-retrieval and first-indexed-unit baseline notebooks. |
| [FHIR_aligned/](FHIR_aligned/) | Pydantic schema and LLM-based generation of the FHIR-aligned evidence model. |
| [FHIR_compliant/FHIR-compliant_script.py](FHIR_compliant/FHIR-compliant_script.py) | Native FHIR R5 Bundle serialization. |
| [FHIR_aligned_generations/](FHIR_aligned_generations/) | Example FHIR-aligned intermediate DOCX files. |
| [Native_FHIR_transformation/](Native_FHIR_transformation/) | Example native FHIR Bundles and validator reports. |
| [Annotations/](Annotations/) | Reference annotations used by the RAGAS workflow and shared evaluation examples. |
| [GPT_4o_extractions_full_pipe/](GPT_4o_extractions_full_pipe/) | Saved GPT-4o extraction outputs used by evaluation examples. |
| [Llama 3.1 extractions/](Llama%203.1%20extractions/) | Saved Llama 3.1 extraction outputs. |
| [docs/](docs/) | User guide, configuration reference, and FHIR documentation. |

## Installation

From the repository root:

```console
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the project dependencies:

```console
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For native FHIR serialization alone:

```console
python -m pip install -r requirements-fhir.txt
```

System tools used by specific stages:

- Tesseract and Poppler for scanned-PDF OCR.
- A local Ollama service when selecting an Ollama-hosted model.
- Java and the HL7 FHIR Validator JAR for FHIR validation.

## Environment variables

Set credentials for the providers selected for your run. The supplied OpenAI-based embedding and model configurations use:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

The optional Anthropic RAGAS configuration uses:

```text
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

[`.env.example`](.env.example) contains placeholders. The scripts read environment variables from the shell or notebook kernel.

## Quick start

Run commands from the repository root. The [user guide](docs/USER_GUIDE.md) gives the complete input and output details for every stage.

### 1. Prepare a PDF

Create local working directories and place a clinical-study PDF at `inputs/tanner.pdf`:

```console
python -c "from pathlib import Path; [Path(p).mkdir(parents=True, exist_ok=True) for p in ('inputs', 'work', 'work/indexes')]"
```

### 2. Run evidence extraction

Set the input path and run name in `Extraction pipeline/main.py`, then select the chat model in `Extraction pipeline/test_llms_and_chains.py` and run:

```console
python "Extraction pipeline/main.py"
```

The example writes a FAISS index and an extraction DOCX in the current directory.

### 3. Run evaluation

Use [TRACE-Eval](https://github.com/muhammad-ammar12/TRACE-Eval) for item-level completeness, correctness, F1, cannot-verify reporting, and expert adjudication. Its user guide provides the environment setup, aligned input pairs, model and retrieval configuration, notebook order, and output files.

For source-faithfulness and context-recall evaluation:

```console
python -m jupyterlab Evaluation_code/_RAGAS_Evaluation_pipeline.ipynb
```

### 4. Generate the FHIR-aligned representation

Place the extracted PICO and statistical text in `pico_text` in `FHIR_aligned/main.py`. Select the model passed to `up_Format_evidence` in `FHIR_aligned/latest_LLM.py`, then run:

```console
python FHIR_aligned/main.py
```

The example writes `batur-2025_computable.docx`, containing the Pydantic-parsed FHIR-aligned evidence model.

### 5. Serialize native FHIR R5

Run the separate native FHIR R5 Bundle serializer:

```console
python FHIR_compliant/FHIR-compliant_script.py batur-2025_computable.docx --outdir work/native_fhir
```

Output:

```text
work/native_fhir/batur-2025_computable_fhir_bundle.json
```

You can also run the serializer directly on a supplied example:

```console
python FHIR_compliant/FHIR-compliant_script.py FHIR_aligned_generations/batur_computable.docx --outdir work/native_fhir
```

### 6. Validate with the HL7 FHIR Validator

Place the Validator CLI JAR at `validator_cli.jar`, then run base FHIR R5 validation:

```console
java -jar validator_cli.jar work/native_fhir/batur-2025_computable_fhir_bundle.json -version 5.0.0 > work/native_fhir/batur-2025_validation_report.txt 2>&1
```

The reported validation configuration used HL7 FHIR Validator **6.9.9** (Git `f50ef63a178c`, built `2026-05-29T20:15:56.943Z`), Java **23.0.2**, and FHIR R5 **5.0.0**.

## Model configuration

FIRE-EVIDENCE separates workflow logic from model selection:

- Evidence extraction: configure `chat_LLM` in `Extraction pipeline/test_llms_and_chains.py` with a LangChain-compatible chat model.
- Correctness/completeness evaluation: configure the embedding and judge models in the [TRACE-Eval](https://github.com/muhammad-ammar12/TRACE-Eval) notebook.
- RAGAS evaluation: configure the evaluation model in `Evaluation_code/_RAGAS_Evaluation_pipeline.ipynb`.
- FHIR-aligned generation: set the `llm_model` passed to `up_Format_evidence` in `FHIR_aligned/latest_LLM.py`.

The [configuration reference](docs/CONFIGURATION.md) lists the settings used for the reported analyses. Users may select other compatible models and settings for new runs.

## Citation and license

Citation metadata is provided in [CITATION.cff](CITATION.cff). FIRE-EVIDENCE is distributed under the [MIT License](LICENSE).
