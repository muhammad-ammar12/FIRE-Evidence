# FIRE-EVIDENCE user guide

This guide runs FIRE-EVIDENCE in the following order:

```text
PDF processing
  -> evidence extraction
  -> evaluation
  -> FHIR-aligned evidence generation
  -> native FHIR R5 serialization
  -> HL7 FHIR validation
```

Run all commands from the repository root.

## 1. Install the environment

Create and activate a virtual environment:

```console
python -m venv .venv
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```console
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install these system tools for the corresponding stages:

- Tesseract and Poppler for scanned-PDF OCR.
- Ollama when using a locally hosted Ollama model.
- Java and the HL7 FHIR Validator JAR for native FHIR validation.

## 2. Configure credentials and working directories

Set the credentials required by the providers selected for the run. The supplied OpenAI configurations use `OPENAI_API_KEY`; the optional Anthropic RAGAS cells use `ANTHROPIC_API_KEY`.

PowerShell:

```powershell
$env:OPENAI_API_KEY = "your_openai_api_key_here"
```

macOS/Linux:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

For a notebook kernel, credentials can be entered without displaying them:

```python
import getpass
import os

os.environ["OPENAI_API_KEY"] = getpass.getpass("OPENAI_API_KEY: ")
```

Create local input and output directories:

```console
python -c "from pathlib import Path; [Path(p).mkdir(parents=True, exist_ok=True) for p in ('inputs', 'work', 'work/indexes', 'work/corr_comp_eval_outputs', 'work/native_fhir')]"
```

## 3. Prepare the clinical-study PDF

Place a clinical-study PDF at `inputs/tanner.pdf`, or update `pdf_path` in `Extraction pipeline/main.py` to another file.

To inspect the extracted text and tables before running an LLM:

```console
python -c "import sys; sys.path.insert(0, 'Extraction pipeline'); import test_loading as loader; loader.write_to_word(loader.extract_pdf_structured('inputs/tanner.pdf'), 'work/tanner_parsed.docx')"
```

This writes `work/tanner_parsed.docx`.

The loader:

- extracts positioned text blocks from digital PDFs with PyMuPDF;
- uses `pdf2image` and Tesseract for scanned PDFs;
- extracts tables with `pdfplumber`;
- groups the resulting content by page.

## 4. Select extraction models and settings

The workflow is model-agnostic. Configure the chat model in `Extraction pipeline/test_llms_and_chains.py` by assigning a LangChain-compatible model to `chat_LLM`.

OpenAI example matching the reported main extraction configuration:

```python
chat_LLM = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.5,
    model_kwargs={"seed": 42},
)
```

Ollama example:

```python
chat_LLM = ChatOllama(model="llama3.1", temperature=0.5)
```

The page embeddings are configured in `Extraction pipeline/test_preprocessing.py`. The supplied configuration uses:

```python
OpenAIEmbeddings(model="text-embedding-ada-002")
```

Users may replace the chat or embedding model with another compatible provider and select their own settings.

## 5. Run evidence extraction

Set these values in `Extraction pipeline/main.py`:

```python
pdf_path = "inputs/tanner.pdf"
filename = "tanner-2025"
```

Run:

```console
python "Extraction pipeline/main.py"
```

The example creates:

```text
tanner-2025_index/index.faiss
tanner-2025_index/index.pkl
tanner-2025_extraction_LLama3.1
```

The extraction output is a DOCX document with an extensionless filename. Update the output suffix in `Extraction pipeline/test_llms_and_chains.py` when selecting another model or naming convention.

To build an index under `work/indexes/` for the evaluation and baseline notebooks:

```console
python -c "import os, sys; from pathlib import Path; sys.path.insert(0, str(Path('Extraction pipeline').resolve())); import test_loading as loader; import test_preprocessing as pre; data=loader.extract_pdf_structured('inputs/tanner.pdf'); os.chdir('work/indexes'); pre.chunk_vectorize_and_store_from_data(data, 'tanner')"
```

This writes:

```text
work/indexes/tanner_index/index.faiss
work/indexes/tanner_index/index.pkl
```

## 6. Run correctness/completeness evaluation

Start JupyterLab:

```console
python -m jupyterlab Evaluation_code/Evaluation_framework.ipynb
```

Use the repository root as the notebook working directory. If the kernel starts in `Evaluation_code/`, run:

```python
%cd ..
```

Then follow the notebook in this order:

1. Run the imports and credential setup cells.
2. Run the cell that writes `llm_extraction_eval_framework_item_level.py`.
3. Run the following import cell.
4. In the configuration cell, set:
   - `study_id`;
   - the reference annotation DOCX path;
   - the extracted-evidence DOCX path;
   - the output directory;
   - the embedding model;
   - the judge model and temperature;
   - retrieval and lexical-matching thresholds.
5. Run the evaluation cell to generate the initial results and review dashboard.
6. Run the expert-adjudication widget and save the decisions.
7. Run the final metrics cell to export adjudicated results.

For the included Tanner example, the notebook configuration uses:

```text
study_id: tanner
reference: Annotations/tanner.docx
extraction: GPT_4o_extractions_full_pipe/tanner_extraction_4o
output directory: work/corr_comp_eval_outputs
```

The notebook exports JSON, CSV, and XLSX files for item-level results, the human-review dashboard, adjudicated decisions, and final correctness/completeness metrics.

## 7. Run source-faithfulness evaluation

Start the RAGAS notebook:

```console
python -m jupyterlab Evaluation_code/_RAGAS_Evaluation_pipeline.ipynb
```

Use the repository root as the working directory. In the notebook configuration cells, set:

- the FAISS index directory;
- the extracted-evidence file;
- the reference annotation file;
- the study question;
- the selected evaluation model and provider credentials.

Run the OpenAI or Anthropic evaluation branch selected for the experiment. The main RAGAS call computes `faithfulness` and `context_recall` and returns a dataframe.

## 8. Run the optional baseline workflows

Full-retrieval baseline:

```console
python -m jupyterlab Baseline_pipeline/Zero_Shot_RAG_extraction.ipynb
```

First-indexed-unit baseline:

```console
python -m jupyterlab Baseline_pipeline/Zero_Shot_Abstract_extraction.ipynb
```

In each notebook, set `BASE_INDEX_DIR`, the output directory, the model configuration, and `INDEX_NAME`. For the index created above, use `tanner_index`.

## 9. Generate FHIR-aligned evidence

Open `FHIR_aligned/main.py` and replace the example `pico_text` with the extracted PICO and statistical evidence for the study.

The model call is defined by `up_Format_evidence` in `FHIR_aligned/latest_LLM.py`:

```python
up_Format_evidence(
    text,
    llm_model="gpt-4o",
    max_tokens=2500,
)
```

Select the model name and output-token limit for the run. The supplied OpenAI implementation uses temperature `0.0`. Another provider can be used by replacing the model adapter while preserving the Pydantic schema of the FHIR-aligned evidence model.

Run:

```console
python FHIR_aligned/main.py
```

The example writes:

```text
batur-2025_computable.docx
```

This DOCX contains the FHIR-aligned evidence model. Its principal objects are `ResearchStudy`, `Group`, `EvidenceVariable`, `Evidence`, and `Citation`, with optional `ArtifactAssessment` objects.

## 10. Serialize native FHIR R5 resources

The native serializer is a separate conversion process. It reads the FHIR-aligned constructor representation and writes a native FHIR R5 collection `Bundle`.

Serialize the output produced in step 9:

```console
python FHIR_compliant/FHIR-compliant_script.py batur-2025_computable.docx --outdir work/native_fhir
```

Output:

```text
work/native_fhir/batur-2025_computable_fhir_bundle.json
```

To run the serializer on a supplied example:

```console
python FHIR_compliant/FHIR-compliant_script.py FHIR_aligned_generations/batur_computable.docx --outdir work/native_fhir
```

Output:

```text
work/native_fhir/batur_computable_fhir_bundle.json
```

## 11. Validate the native Bundle

Download the HL7 FHIR Validator CLI and place the JAR at `validator_cli.jar` in the repository root. The reported configuration used:

```text
HL7 FHIR Validator: 6.9.9 (Git f50ef63a178c; built 2026-05-29T20:15:56.943Z)
Java: 23.0.2
FHIR release: R5 5.0.0
```

Validate the Bundle generated in step 10:

```console
java -jar validator_cli.jar work/native_fhir/batur-2025_computable_fhir_bundle.json -version 5.0.0 > work/native_fhir/batur-2025_validation_report.txt 2>&1
```

For the supplied Batur example:

```console
java -jar validator_cli.jar work/native_fhir/batur_computable_fhir_bundle.json -version 5.0.0 > work/native_fhir/batur_validation_report.txt 2>&1
```

Open the generated report and review the validator summary, errors, warnings, and informational notes.

## 12. Main outputs

| Stage | Output |
| --- | --- |
| Document processing | Page-structured DOCX under `work/`. |
| Evidence extraction | FAISS index and extraction DOCX. |
| Correctness/completeness evaluation | JSON/CSV/XLSX result and adjudication files. |
| RAGAS evaluation | Evaluation dataframe and notebook outputs. |
| FHIR-aligned generation | Constructor-style FHIR-aligned evidence-model DOCX. |
| Native serialization | FHIR R5 collection `Bundle` JSON. |
| FHIR validation | Validator text report. |

The [configuration reference](CONFIGURATION.md) lists the settings used for the reported analyses. The [FHIR guide](FHIR.md) describes the intermediate representation, native mapping, and validation sequence.
