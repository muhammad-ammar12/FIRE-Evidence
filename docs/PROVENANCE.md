# Source and public snapshot provenance

The repository was created after the local and/or Google Colab analyses to make the same implementation publicly available. Per-study results and evaluations were produced with this code; their aggregate compilation was performed separately. A Git checkout should not be described as the environment in which those analyses originally ran. The pre-cleanup public source head was:

```text
678b351295509f634eb731d209741ba6a91dbde6
```

The cleanup commit adds documentation, portable dependency instructions, MIT license/citation metadata, credential hygiene, and narrow runtime-only fixes. It does not change prompts, selected models, temperatures, seeds, retrieval formulas, evaluation formulas, FHIR mapping semantics, or numerical outputs. The final public implementation snapshot is the **exact Git commit used to obtain this file**. Record it after checkout:

```console
git rev-parse HEAD
```

A Git commit cannot reliably contain its own final SHA in a committed file. The final cleanup SHA is therefore recorded in the delivery report and visible in Git history; use `git rev-parse HEAD` for independent verification. No semantic release/tag is required. Compare scientific implementation against the pre-cleanup commit before rerunning; the uploaded Llama configuration and main-analysis GPT-4o configuration are distinguished in [the software notes](SOFTWARE.md).

This snapshot is a code and representative-output archive, not proof that a Git-hosted execution generated the original measurements. No unpublished publication identifier, DOI, or release date is implied.
