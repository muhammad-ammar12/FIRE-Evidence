# Software and model configuration

The versions below were recorded in the original root environment export and the supplied technical materials. `requirements.txt` now pins direct packages used by this repository and applies the sanitized historical environment inventory as constraints. `docs/environment-record.txt` is a broad `pip freeze`-style record, **not** an installable environment: local build-machine URLs had no portable version record and were removed. The install resolves successfully on Python 3.12/Windows in a dry run, but a dependency resolver can still choose versions for packages that the original record did not pin. This is not proof of the historical interpreter or a bit-for-bit environment recreation.

## Recorded software

| Component | Version | Repo evidence / role |
| --- | --- | --- |
| OpenAI Python SDK | 1.70.0 | API calls and embeddings |
| LangChain | 0.3.27 | `RetrievalQA` and notebook orchestration |
| langchain-core | 0.3.79 | Parsers/documents/prompts |
| langchain-openai | 0.3.12 | `ChatOpenAI`, `OpenAIEmbeddings` |
| langchain-community | 0.3.31 | FAISS and Ollama integration |
| FAISS CPU | 1.10.0 | Local page-level index |
| PyMuPDF | 1.25.5 | Digital PDF text and scan detection |
| pdfplumber | 0.11.6 | Table extraction |
| pdf2image | 1.17.0 | Scanned-page rasterization |
| pytesseract | 0.3.13 | OCR interface; Tesseract binary version unrecorded |
| Pydantic | 2.11.1 | Intermediate evidence schema/parser |
| RAGAS | 0.2.14 | Source faithfulness notebook |
| pandas | 2.2.3 | Evaluation tables and metrics |
| NumPy | 2.2.4 | Evaluation arrays |
| SciPy | 1.15.2 | Recorded environment; aggregate compilation was performed separately |
| scikit-learn | 1.6.1 | Recorded environment |
| tiktoken | 0.9.0 | Recorded environment; cost/timing scripts absent |
| python-docx | 1.1.2 | Saved evidence/reference files |
| transformers | 4.50.3 | Exploratory local model software in record; no complete executable workflow here |
| torch | 2.6.0 | Exploratory local model software in record |
| sentence-transformers | 4.0.2 | Exploratory model software in record |
| matplotlib | 3.10.1 | Recorded environment; figure compilation was performed separately |
| HL7 FHIR Validator | 6.9.9, Git `f50ef63a178c` | Historical validation reports |
| Java | 23.0.2 | Historical validator runtime |
| FHIR target | R5, 5.0.0 | Validator flag/report |

Python's historical version, Poppler/Tesseract binary versions, OCR language packs, Ollama version/model digest, OpenAI server-side snapshots, and the external validator JAR are not in the repository. `ipywidgets` and `nest-asyncio` are used by notebooks but were not pinned in the original export. `requirements.txt` leaves these two versions open rather than fabricating them. The notebook cell installers are historical and use unpinned packages; the RAGAS cell's `sentence-transformers==2.2.2` and `requests==2.32.4` differ from the recorded environment (`4.0.2` and `2.32.5`). Use the root requirements file for setup and skip those installer cells.

The original broad environment includes packages unrelated to the current workflows (TensorFlow, web frameworks, cloud SDKs, etc.). They remain in the sanitized record for traceability and are not installed as direct requirements. A local dry run with the recorded constraints resolved on Windows/Python 3.12; actual notebook execution and external service compatibility are separate checks. The old `pip freeze` included machine-specific `file://` origins, which cannot work on an independent user's machine. Their exact versions were not recoverable from those lines.

## Document processing and retrieval

- Digitally generated PDFs: PyMuPDF text blocks sorted by `(y, x)` position.
- Scanned detection: first two sampled pages with no extractable text. OCR: all pages through `pdf2image` and Tesseract via `pytesseract`.
- Tables: `pdfplumber.extract_tables()`, appended to the corresponding page as tab-delimited rows.
- Text cleanup: null bytes and nonprintable controls removed.
- Indexing unit: one nonempty page. The source has comments about earlier chunk configurations; no fixed-size chunk splitter is called in the active indexer.
- Embedding: `text-embedding-ada-002`. Index: FAISS, saved per study. Retrieval: `k = ceil(number_of_indexed_pages / 1)` in the active path. `RetrievalQA` uses `chain_type='stuff'`.
- PICO and statistical prompts are in `Extraction pipeline/systematic_prompts.py`. `JsonOutputParser` supplies format instructions for the statistical prompt, but the extraction code does not parse the returned string with it.

## Model settings by entry point

| Workflow | Model and settings in current code | Boundary |
| --- | --- | --- |
| Full extraction `test_llms_and_chains.py` | Uploaded default `ChatOllama(model='llama3.1', temperature=0.5)`; commented GPT-4o line has `temperature=0.5`, `seed=42` | The main analysis used GPT-4o; the uploaded setting reflects the separate Llama 3.1 comparison. The `main.py` output name is Llama-specific. |
| Baseline full-retrieval notebook | `gpt-4o`, temperature `0.5`; no explicit seed | Separate baseline, not the full extraction chain. |
| Baseline first-unit notebook | `gpt-4o`, temperature `0`; no explicit seed | First stored page/indexed unit, not a general abstract parser. |
| FHIR-aligned generation `latest_LLM.py` | `gpt-4o`, temperature `0.0`, `max_tokens=2500`; `PydanticOutputParser` | Generates intermediate `EvidenceGraph`, not a native Bundle. The module's `LLM_MODEL` environment variable is assigned but not passed into `up_Format_evidence`. |
| Item-level evaluation notebook | `gpt-5.1` to extract reference items/blocks and judge candidates, temperature `0`; OpenAI `text-embedding-3-large` | Cell 8 overrides retrieval thresholds. Model identifiers are aliases, with no fixed server-side snapshot. |
| RAGAS notebook | GPT-5.1, no explicit temperature, for the shown OpenAI branch. Optional `claude-3-haiku-20240307`, temperature `0.2`, `max_tokens=4096` | Notebook runs are interactive; model use differs across cells. |

The main extraction analysis used GPT-4o with temperature `0.5`, seed `42`, and no explicit output-token cap; GPT-4o FHIR-aligned generation used temperature `0`, `max_tokens=2500`. The public code retains the main-analysis GPT-4o setting as a commented assignment beside the uploaded Llama default. A user may select the appropriate model configuration for a new run; the script's current default alone does not reproduce the GPT-4o condition. API responses can vary even when temperature is zero or a seed is supplied.

## Item-level evaluation configuration

Cell 8 of `Evaluation_code/Evaluation_framework.ipynb` explicitly sets OpenAI `text-embedding-3-large`, `top_k=5`, main cosine threshold `0.75`, sparse threshold `0.50`, lexical fallback `top_k=5`, lexical minimum score `0.50`, `gpt-5.1`, and temperature `0`. These match the reported configuration. The `EvalConfig` class defaults inside the notebook's generated module are instead `0.25`, `0.14`, `3`, and `0.18`; invoking it without the cell-8 overrides changes candidate retrieval. Similarity is used to find candidates, not as the final correctness score. Final labels can be changed through expert adjudication; missing is system-assigned when no plausible candidate is found.

The RAGAS notebook uses faithfulness and context recall in its first OpenAI evaluation call. It has a hard-coded WHI question with a Worringer default filename, and no batch manifest. The saved notebook results should not be mistaken for a self-contained dataset-wide evaluation command.

## What has and has not been checked

The repository cleanup did not change prompts, numerical settings, mapping semantics, results, or model selections. The FHIR serializer was run on five committed intermediate DOCX files and generated byte-for-byte equivalent JSON structures. The package resolver completed a dry run with the recorded constraints. External model calls, new OCR, full notebook execution, and fresh HL7 validation were intentionally not run as part of this no-cost audit.
