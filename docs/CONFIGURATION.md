# FIRE-EVIDENCE configuration reference

FIRE-EVIDENCE is model-agnostic. The values below describe the configuration used for the reported analyses and provide a reference profile for users. Models and settings can be changed at the configuration points listed in this document.

## Reported software versions

| Component | Version |
| --- | --- |
| OpenAI Python SDK | 1.70.0 |
| LangChain | 0.3.27 |
| langchain-core | 0.3.79 |
| langchain-openai | 0.3.12 |
| langchain-community | 0.3.31 |
| langchain-text-splitters | 0.3.11 |
| FAISS CPU | 1.10.0 |
| PyMuPDF | 1.25.5 |
| pdfplumber | 0.11.6 |
| pdf2image | 1.17.0 |
| pytesseract | 0.3.13 |
| Pillow | 11.1.0 |
| Pydantic | 2.11.1 |
| RAGAS | 0.2.14 |
| pandas | 2.2.3 |
| NumPy | 2.2.4 |
| SciPy | 1.15.2 |
| scikit-learn | 1.6.1 |
| tiktoken | 0.9.0 |
| python-docx | 1.1.2 |
| datasets | 3.5.0 |
| tenacity | 9.1.2 |
| openpyxl | 3.1.5 |
| Anthropic SDK | 0.49.0 |
| langchain-anthropic | 0.3.10 |
| requests | 2.32.5 |
| python-dotenv | 1.1.0 |
| JupyterLab | 4.3.6 |
| IPython kernel | 6.29.5 |
| HL7 FHIR Validator | 6.9.9 (`f50ef63a178c`) |
| Validator build | `2026-05-29T20:15:56.943Z` |
| Java | 23.0.2, 64-bit amd64 |
| FHIR release | R5 5.0.0 |

The installable Python dependencies are defined in the root `requirements.txt` file. Native FHIR serialization alone requires `requirements-fhir.txt`.

## Document processing and retrieval

| Setting | Reported configuration |
| --- | --- |
| Digital PDF extraction | PyMuPDF layout blocks |
| Scan detection | First two pages checked for extractable text |
| OCR | `pdf2image`/Poppler with Tesseract |
| Table extraction | `pdfplumber` |
| Retrieval unit | One nonempty PDF page, including extracted table rows |
| Embedding model | OpenAI `text-embedding-ada-002` |
| Vector store | FAISS |
| Retrieval count | All indexed page units (`k` equals index size) |

These settings are defined in:

```text
Extraction pipeline/test_loading.py
Extraction pipeline/test_preprocessing.py
```

## Evidence extraction

The main extraction analysis used:

| Setting | Value |
| --- | --- |
| Chat model | GPT-4o |
| Temperature | 0.5 |
| Seed | 42 |
| Prompt workflow | Separate PICO and statistical-result `RetrievalQA` chains |

The repository also includes a Llama 3.1/Ollama configuration and saved comparison outputs.

Select the extraction model in:

```text
Extraction pipeline/test_llms_and_chains.py
```

Assign any LangChain-compatible model to `chat_LLM`, for example:

```python
chat_LLM = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.5,
    model_kwargs={"seed": 42},
)
```

or:

```python
chat_LLM = ChatOllama(model="llama3.1", temperature=0.5)
```

## Correctness/completeness evaluation

The reported item-level evaluation configuration is set in the configuration cell of `Evaluation_code/Evaluation_framework.ipynb`:

| Setting | Value |
| --- | --- |
| Embedding model | OpenAI `text-embedding-3-large` |
| Dense candidate `top_k` | 5 |
| Main cosine threshold | 0.75 |
| Sparse threshold | 0.50 |
| Lexical fallback `top_k` | 5 |
| Lexical minimum score | 0.50 |
| Judge model | GPT-5.1 |
| Judge temperature | 0 |

Users can replace the embedding model, judge model, temperature, and retrieval thresholds in the notebook configuration cell.

The evaluation labels used for metric calculation are:

- `agree`
- `contradict`
- `missing`
- `cannot_verify`

Expert decisions are entered through the notebook's adjudication dashboard before exporting final metrics.

## Source-faithfulness evaluation

The RAGAS notebook is:

```text
Evaluation_code/_RAGAS_Evaluation_pipeline.ipynb
```

The reported OpenAI branch uses GPT-5.1 and calculates:

- `faithfulness`
- `context_recall`

An optional Anthropic branch is configured with:

| Setting | Value |
| --- | --- |
| Model | `claude-3-haiku-20240307` |
| Temperature | 0.5 |
| Maximum output tokens | 4096 |

Select the model, provider, credentials, question, evidence file, annotation file, and FAISS index in the notebook configuration cells.

## Baseline configurations

| Workflow | Model configuration | Retrieval configuration |
| --- | --- | --- |
| `Zero_Shot_RAG_extraction.ipynb` | GPT-4o, temperature 0.5 | Full indexed context within the notebook context budget |
| `Zero_Shot_Abstract_extraction.ipynb` | GPT-4o, temperature 0.5 | First indexed unit for the first-unit baseline |

Both notebooks expose the model, temperature, index directory, study index name, and output directory in their configuration cells.

## FHIR-aligned generation

The reported FHIR-aligned generation configuration is:

| Setting | Value |
| --- | --- |
| Model | GPT-4o |
| Temperature | 0.0 |
| Maximum output tokens | 2500 |
| Output parser | `PydanticOutputParser` with the FHIR-aligned evidence-model schema |

The function is defined in `FHIR_aligned/latest_LLM.py`:

```python
up_Format_evidence(text, llm_model="gpt-4o", max_tokens=2500)
```

Users can select another OpenAI model through `llm_model`. To use another provider, replace the model adapter and preserve the Pydantic schema of the FHIR-aligned evidence model.

## Native FHIR and validation

Native FHIR R5 Bundle serialization is a separate conversion stage and does not use an LLM. Run:

```console
python FHIR_compliant/FHIR-compliant_script.py INPUT.docx --outdir work/native_fhir
```

Validate the resulting Bundle with the reported validation profile:

```console
java -jar validator_cli.jar BUNDLE.json -version 5.0.0
```

The recorded validation session loaded `hl7.fhir.r5.core#5.0.0`, `hl7.fhir.xver-extensions#0.1.0`, `hl7.terminology.r5#6.2.0`, `hl7.fhir.uv.extensions.r5#5.2.0`, and `hl7.terminology#7.1.0`, and connected to `http://tx.fhir.org`. The recorded `updated3_computable_fhir_bundle.json` run completed with **0 errors, 3 warnings, and 6 notes**.

The [FHIR guide](FHIR.md) describes the intermediate representation, native resource mapping, and validator workflow.
