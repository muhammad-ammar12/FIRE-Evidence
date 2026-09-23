# FHIR-aligned generation, native serialization, and validation

FIRE-EVIDENCE implements three separate FHIR-related stages:

1. **FHIR-aligned evidence generation:** an LLM generates a Pydantic-parsed representation based on the FHIR-aligned evidence model.
2. **Native FHIR R5 serialization:** a separate Python conversion script converts the saved intermediate representation into native FHIR R5 resources in a collection `Bundle`.
3. **FHIR R5 validation:** the independent HL7 FHIR Validator validates the native Bundle against FHIR R5.

The FHIR-aligned evidence model and native FHIR R5 Bundle are different representations. Run the stages in order.

## 1. FHIR-aligned intermediate representation

The schema is defined in:

```text
FHIR_aligned/updated_graph.py
```

The FHIR-aligned evidence model contains:

- `ResearchStudy`
- `Group` objects
- population, intervention, comparator, and outcome `EvidenceVariable` objects
- study-result `Evidence` objects
- `Citation`
- optional `ArtifactAssessment` objects

The LLM call and Pydantic parser are defined in:

```text
FHIR_aligned/latest_LLM.py
```

The reported configuration used GPT-4o, temperature `0.0`, and `max_tokens=2500`. Users can select another model through the `llm_model` parameter or replace the provider adapter while preserving the Pydantic schema of the FHIR-aligned evidence model.

Place the extracted PICO and statistical evidence in `pico_text` in `FHIR_aligned/main.py`, then run:

```console
python FHIR_aligned/main.py
```

The example writes:

```text
batur-2025_computable.docx
```

The DOCX contains the constructor-style FHIR-aligned evidence model. Additional examples are available in [`FHIR_aligned_generations/`](../FHIR_aligned_generations/).

## 2. Native FHIR R5 serialization

The native serializer is:

```text
FHIR_compliant/FHIR-compliant_script.py
```

It performs the conversion without calling an LLM. The core mapping is:

| Intermediate object | Native FHIR R5 output |
| --- | --- |
| `research_study` | `ResearchStudy` |
| `groups` | `Group` resources |
| `population` | Population `EvidenceVariable` |
| `intervention` | Intervention `EvidenceVariable` |
| `comparator` | Comparator `EvidenceVariable` |
| `outcome` | Outcome `EvidenceVariable` |
| `evidence_results` | `Evidence` resources |
| `citation` | `Citation` |

The serializer builds a collection `Bundle`, creates resource `fullUrl` values, rewrites internal references, adds generated narratives, and runs local structural checks.

Serialize the output from the FHIR-aligned stage:

```console
python FHIR_compliant/FHIR-compliant_script.py batur-2025_computable.docx --outdir work/native_fhir
```

Output:

```text
work/native_fhir/batur-2025_computable_fhir_bundle.json
```

Serialize a supplied example:

```console
python FHIR_compliant/FHIR-compliant_script.py FHIR_aligned_generations/batur_computable.docx --outdir work/native_fhir
```

Output:

```text
work/native_fhir/batur_computable_fhir_bundle.json
```

Use trusted local DOCX/text input files for this step.

## 3. Validate the native Bundle

Install Java, download the HL7 FHIR Validator CLI, and place the JAR at `validator_cli.jar` in the repository root.

The reported validation configuration used:

| Component | Version |
| --- | --- |
| HL7 FHIR Validator | 6.9.9 (`f50ef63a178c`) |
| Validator build | `2026-05-29T20:15:56.943Z` |
| Java | 23.0.2 |
| FHIR release | R5 5.0.0 |

The validation run loaded:

```text
hl7.fhir.r5.core#5.0.0
hl7.fhir.xver-extensions#0.1.0
hl7.terminology.r5#6.2.0
hl7.fhir.uv.extensions.r5#5.2.0
hl7.terminology#7.1.0
```

The validator connected to `http://tx.fhir.org` for terminology services.

Validate the Bundle generated from `batur-2025_computable.docx`:

```console
java -jar validator_cli.jar work/native_fhir/batur-2025_computable_fhir_bundle.json -version 5.0.0 > work/native_fhir/batur-2025_validation_report.txt 2>&1
```

Validate the supplied Batur example:

```console
java -jar validator_cli.jar work/native_fhir/batur_computable_fhir_bundle.json -version 5.0.0 > work/native_fhir/batur_validation_report.txt 2>&1
```

Review the generated report for the validator summary, errors, warnings, and informational notes.

For `updated3_computable_fhir_bundle.json`, the recorded validator summary was:

```text
Success: 0 errors, 3 warnings, 6 notes
```

The three warnings concerned `Evidence.statistic.statisticType` elements containing text without a code from the FHIR R5 `Statistic Type` value set. The six informational notes reported base-FHIR validation for `Group.code` and `Group.characteristic.code` bindings.

## Example outputs

[`Native_FHIR_transformation/`](../Native_FHIR_transformation/) contains example native FHIR R5 Bundle JSON files and validator reports produced by this workflow.

The complete ordered pipeline is documented in the [user guide](USER_GUIDE.md).
