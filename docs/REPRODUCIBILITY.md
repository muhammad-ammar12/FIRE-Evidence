# Reproducibility guide

Read [scope and rerun requirements](KNOWN_GAPS.md) first. These instructions describe the uploaded configuration, manual handoffs, and inputs needed to regenerate additional artifacts. The saved files are representative examples rather than a complete archive of every study run.

## 1. Establish the environment and inputs

Use the root [installation instructions](../README.md#installation), the recorded [software versions](SOFTWARE.md), and an isolated virtual environment. Supply credentials through the environment. For an interactive shell/kernel, this Python snippet sets the OpenAI key without echoing it:

```python
import getpass
import os
os.environ['OPENAI_API_KEY'] = getpass.getpass('OPENAI_API_KEY: ')
```

A key set inside a Python process is only available to that process and its children. Set it in each notebook kernel or use your shell's secure credential mechanism for script execution. No script automatically loads `.env`. Optional Anthropic cells similarly need `ANTHROPIC_API_KEY`.

All commands below assume the repository root. Prepare local working directories:

```console
python -c "from pathlib import Path; [Path(p).mkdir(parents=True, exist_ok=True) for p in ('inputs', 'work', 'work/indexes')]"
```

Place the lawfully obtained example PDF at `inputs/tanner.pdf`. No source articles are distributed here. New inputs, indexes, and scratch outputs are ignored by Git. Retain a local manifest linking study IDs, source publications, input checksums, run settings, and output files; a complete historical manifest is missing.

## 2. Document/PDF processing

The following calls the existing loader and optional DOCX exporter without embedding or LLM requests:

```console
python -c "import sys; sys.path.insert(0, 'Extraction pipeline'); import test_loading as loader; loader.write_to_word(loader.extract_pdf_structured('inputs/tanner.pdf'), 'work/tanner_parsed.docx')"
```

Input: `inputs/tanner.pdf`. Output: `work/tanner_parsed.docx` with page headings, text, and tables. Internally, `extract_pdf_structured` returns a dictionary keyed by page number. Digital text blocks are sorted by vertical and horizontal position. If no text is found in either of the first two sampled pages, the entire PDF is rasterized with `pdf2image` and OCR is run through `pytesseract`. `pdfplumber` extracts tables independently of that decision.

For indexing, `test_preprocessing.py` cleans text, appends tab-delimited table rows, and treats each nonempty page as one retrieval unit. It does not save page-number metadata. There is no fixed-length chunking in the active path, no mixed-page OCR fallback, and no dedicated OCR table parser. Check the parsed DOCX before spending API credits.

## 3. Evidence extraction

### Current full-pipeline entry point

```console
python "Extraction pipeline/main.py"
```

Inputs/configuration: `inputs/tanner.pdf`, `filename='tanner-2025'`, `OPENAI_API_KEY` for `text-embedding-ada-002`, and an Ollama service with `llama3.1`. The script has no CLI options. Its `decider(..., store_and_load=True)` builds and reloads a FAISS index, then calls the two `RetrievalQA` chains. Outputs in the working directory are:

- `tanner-2025_index/index.faiss` and `tanner-2025_index/index.pkl`;
- `tanner-2025_extraction_LLama3.1`, a DOCX file despite having no `.docx` extension;
- the PICO response printed to the terminal.

**This command runs the uploaded Llama 3.1 configuration used for the separate exploratory comparison.** The main extraction analysis used GPT-4o. To run that model with the same implementation, select the existing commented `ChatOpenAI(model_name="gpt-4o", temperature=0.5, model_kwargs={"seed": 42})` assignment in `test_llms_and_chains.py` and disable the active `ChatOllama` assignment in your local run. The cleanup preserves the uploaded default. Record which setting you used: the current output filename remains Llama-specific even after a local model switch and does not prove a result's model provenance.

For another study, supply its path/identifier through the existing `main.decider` function or edit only the example path/identifier in a local copy. There is no batch CLI. Keep the model, prompts, retriever settings, and parser behavior explicit in your run record.

### Build an index for the evaluation/baseline notebooks

The notebook defaults look in `work/indexes`. This invokes existing loader/indexing functions with the example PDF and writes the index there; it makes paid embedding calls but no chat-model calls:

```console
python -c "import os, sys; from pathlib import Path; sys.path.insert(0, str(Path('Extraction pipeline').resolve())); import test_loading as loader; import test_preprocessing as pre; data=loader.extract_pdf_structured('inputs/tanner.pdf'); os.chdir('work/indexes'); pre.chunk_vectorize_and_store_from_data(data, 'tanner')"
```

Outputs: `work/indexes/tanner_index/index.faiss` and `index.pkl`. Existing indexes can be reused only if their input/configuration provenance is known. The loader enables dangerous deserialization; never load an untrusted index.

### Statistical-output parsing boundary

`systematic_prompts.py` uses `JsonOutputParser.get_format_instructions()` in the statistical prompt. The active extraction chain does not call `parser.parse()` on the result: it wraps the returned text and writes DOCX. A JSON-formatted prompt is not a guarantee of syntactically valid JSON. No automatic repair or schema enforcement should be inferred here.

## 4. Correctness/completeness evaluation and adjudication

```console
python -m jupyterlab Evaluation_code/Evaluation_framework.ipynb
```

This opens a notebook; it does not execute it. Jupyter may start its kernel in `Evaluation_code/`. Set the kernel working directory to the repository root before executing path-dependent cells (for a kernel started in that directory, `%cd ..` does this). Verify `README.md` and `Annotations/` are visible from the kernel. In Colab, place/clone the repository in a working directory and change to that root; mounting Drive alone does not create its contents.

Use these zero-based cell indices (including markdown cells):

1. Skip cell 0's unpinned installer after using the requirements file. Cell 2 obtains credentials from Colab Secrets or a secure prompt. Cell 3 optionally mounts Drive.
2. Run cell 5 to write `llm_extraction_eval_framework_item_level.py` into the kernel working directory, then cell 6 to import it. This module is generated by the notebook and is not a missing checked-in source file.
3. Cell 8 configures the example: `study_id='tanner'`, `Annotations/tanner.docx`, `GPT_4o_extractions_full_pipe/tanner_extraction_4o`, and `work/corr_comp_eval_outputs`. Both example inputs are present. Preserve its explicit thresholds; `EvalConfig()` defaults differ.
4. Cell 10 makes paid calls for item/block extraction, embeddings, candidate judging, and writes the initial evaluation outputs.
5. Cell 12 displays results. Cell 14 opens the expert-adjudication widget and saves progress when its save controls are used.
6. After saving decisions, cell 16 reloads the progress CSV, computes final metrics, and writes final files. Cell 18 optionally downloads outputs in Colab.

For this example the output prefix is `work/corr_comp_eval_outputs/tanner`. Initial outputs are `_evaluation_results.json`, `_evaluation_audit.xlsx`, `_human_review_dashboard.csv`, and `_human_review_dashboard.xlsx`. The widget saves `tanner_adjudicated_review_in_progress.csv`. Final outputs are `tanner_final_adjudicated_review.csv`, `tanner_final_adjudicated_metrics.xlsx`, and `tanner_final_adjudicated_metrics.json`.

The unit of analysis is a reference item/claim group. `agree`, `contradict`, and system-assigned `missing` contribute to completeness; correctness uses `agree` and `contradict`. `cannot_verify` is excluded from these two denominators and reported separately. Blank expert decisions fall back to provisional labels; a saved “final” filename does not establish complete human adjudication. Check the exported completion rate. The code exports subfact coverage as a diagnostic, not the primary metric, and does not calculate aggregate F1 or cross-study significance tests.

## 5. Source-faithfulness evaluation (RAGAS)

```console
python -m jupyterlab Evaluation_code/_RAGAS_Evaluation_pipeline.ipynb
```

Use a repository-root kernel working directory as above. Skip cell 0's installer after the pinned environment setup; it specifies a conflicting historical `sentence-transformers` version and an incompatible `requests` pin (see [software notes](SOFTWARE.md)). Cell 2 is a Colab-only Drive mount; skip it locally.

Run cells 1, 3–12 after configuring cell 4. Default inputs are the missing local index `work/indexes/worringer_index`, plus the supplied `GPT_4o_extractions_full_pipe/worringer_extraction_4o` and `Annotations/worringer.docx`. Rebuild the matching index from the original source PDF or supply a trusted copy. Cell 8 contains a fixed WHI retrieval query even though the default file ID is `worringer`; confirm the intended study/query pairing before interpreting a reproduction. The query has not been altered.

For the OpenAI branch, skip optional Anthropic cell 13, run cell 14 (`gpt-5.1`, no explicit temperature), then cell 15 (`faithfulness` and `context_recall`). The result is `df`, a dataframe; this notebook does not save a CSV. Cells 16–44 and many later cells retain displays from separate interactive runs and are not a study loop. Running them now redisplays the current `df`. Later cells 45, 47, 48, 50, and 51 make additional evaluation calls and can incur charges.

The optional Anthropic branch defines `claude-3-haiku-20240307`, temperature `0.2`, `max_tokens=4096` in cell 13 and needs `ANTHROPIC_API_KEY`. The notebook does not establish a single model/temperature or complete run manifest for every saved result. Its `RunConfig(timeout=120, log_tenacity=True)` variable is created but not passed to the shown `evaluate` calls.

## 6. Baseline extraction workflows

```console
python -m jupyterlab Baseline_pipeline/Zero_Shot_RAG_extraction.ipynb
python -m jupyterlab Baseline_pipeline/Zero_Shot_Abstract_extraction.ipynb
```

Open and run these independently; use a repository-root kernel working directory. Skip cell 0 after installing requirements and skip the Colab Drive-mount cell 1 locally. In each notebook, cell 2 defines `BASE_INDEX_DIR=work/indexes`, an output directory, and credential setup. Cells 3–6 define the configuration/functions. Set the single-run cell 7's `INDEX_NAME` to the **actual folder name**, such as `tanner_index`: the loader does not append `_index`. The original `batur` example/comment is inconsistent with the batch list and must not be assumed to locate `batur_index` automatically.

- Full-retrieval notebook: GPT-4o, temperature `0.5`, no explicit seed; `k=None` retrieves all units; context stops at a 120,000-character budget. Cell 7 runs once, cell 8 optionally runs the 14-name batch, and cell 9 optionally writes `all_extractions.json`. Per-study output: `work/zero_shot_extractions/{index_folder}_extraction.txt`.
- First-indexed-unit notebook: GPT-4o, temperature `0`, no explicit seed. Cell 7 selects stored unit 0 only; this is the first nonempty indexed page, not a separately segmented abstract. Cell 8 is an optional additional full-retrieval run, cell 9 is the optional 14-name batch, and cell 10 writes `all_indexed_unit_extractions.json`. Per-study output: `work/RAG_ZERO_Abstract_extractions/{index_folder}_indexed_unit_0_n_1_extraction.txt`. Retrieval mode instead uses a `retrieval_k_{k}` filename component.

Do not call these experimentally matched conditions without resolving the temperature/seed differences. Saved examples are in the two root ZIP archives. The archives contain outputs, not the input FAISS indexes or aggregate comparison statistics.

## 7. FHIR-aligned evidence generation

```console
python FHIR_aligned/main.py
```

Input is the embedded `pico_text` example in `FHIR_aligned/main.py`; there is no input-file CLI. For another study, supply its extracted PICO/statistical text to `pipeline.run_standardization(pico_text)` from that module environment. The call uses `gpt-4o`, temperature `0.0`, and `max_tokens=2500`. It parses the response with the `EvidenceGraph` Pydantic model and writes **`batur-2025_computable.docx` in the current directory**, overwriting that filename on another run. The output name is fixed independently of input content; archive each run under its correct study ID yourself.

The DOCX contains `str(graph_entities)`, a Python/Pydantic constructor-style representation. It is not native FHIR JSON, even though the legacy document heading calls it compliant. The schema constrains object structure but does not implement global reference-resolution/unique-ID validators. The `LLM_MODEL` environment lookup in `latest_LLM.py` is unused by this entry point; changing it does not change the invoked function's model default.

## 8. Deterministic native FHIR serialization

Existing intermediate files allow this step without regenerating evidence:

```console
python FHIR_compliant/FHIR-compliant_script.py --help
python FHIR_compliant/FHIR-compliant_script.py FHIR_aligned_generations/batur_computable.docx --outdir work/native_fhir
```

Input: trusted constructor-style intermediate DOCX/text. Output: `work/native_fhir/batur_computable_fhir_bundle.json`. Multiple positional input paths are supported. The serializer itself does not call an LLM, contact a terminology server, or execute Java. [FHIR.md](FHIR.md) details mappings and boundaries.

## 9. Separate HL7 FHIR validation

Obtain the external Validator 6.9.9 JAR and put it at `validator_cli.jar` in the repository root; it is not distributed here. Using Java 23.0.2 matches the recorded runtime. After step 8:

```console
java -jar validator_cli.jar work/native_fhir/batur_computable_fhir_bundle.json -version 5.0.0 > work/native_fhir/batur_validation_report.txt 2>&1
```

The flags reproduce the actual process recorded in the serializer/logs. Output is the console validation report captured at `work/native_fhir/batur_validation_report.txt`. Confirm the banner identifies the expected validator and FHIR versions. The validator can download specification packages and contact terminology services. Historical successes and warnings are described in [FHIR.md](FHIR.md). They are not a promise of an identical future log.

## 10. Analysis, outputs, and reproducibility limits

The repository supplies the code used to produce per-study results and evaluations and can regenerate indexes, extractions, evaluations, intermediate evidence, native Bundles, and validator reports when their source inputs and services are available. It intentionally includes representative saved outputs rather than every run. Aggregate compilation of those results was performed separately; its complete procedure and input tables are not checked in. Original study inputs, adjudications, and that compilation record are needed for exact historical cohort-level tables, confidence intervals, significance tests, convergence figures, cost/timing analyses, and ablation summaries. Do not infer aggregate commands from filenames or invent missing source data.

| Stage | Reproducibility boundary |
| --- | --- |
| PDF processing | Local library/OCR-dependent; binary versions, language data and input PDF affect output. |
| Embedding/retrieval | API-dependent embedding generation; local FAISS operations use the supplied index/configuration. |
| Evidence extraction and standardization | LLM-dependent; aliases, seed, and temperature do not ensure byte-for-byte repeatability. |
| Candidate/item judging and RAGAS | API-dependent; human adjudication is a separate required input to fully adjudicated metrics. |
| Metric recomputation from a fixed dashboard | Deterministic formulas for fixed data; missing decisions fall back to provisional labels. |
| Native serialization | Deterministic for the same trusted intermediate and code; five examples matched committed JSON. |
| HL7 validation | Version/package/terminology-service-dependent; separate from serialization. |

Record input hashes, exact Git SHA, dependency resolution, service/model identifiers, complete configuration, and adjudication files for any new run. Keep new runs distinct from the saved historical outputs.
