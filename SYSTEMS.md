# Systems Alignment

This engine fits into the czar spectrum-systems family as the component that:
- accepts governed inputs (resolution matrix + source PDF + source DOCX),
- validates them against the shared contract,
- produces governed outputs (commented DOCX placeholder + injection report + validation artifacts),
- fails loudly with structured errors to keep the pipeline deterministic.

Operational expectations:
- Deterministic input/output paths and filenames.
- No implicit network or side effects.
- Validation runs before any mutation.
- Audit artifacts are always emitted when the pipeline is invoked.

Interfaces:
- Inputs: see `contracts/engine_contract.md`.
- Outputs: `commented.docx`, `injection_report.csv`, `validation_report.json` in the provided output directory.
- CLI: `python -m docx_comment_injection_engine.cli` (or `scripts/run_engine.sh`).

Evolution:
- Replace stubbed insertion with real PDF anchor resolution and DOCX comment injection.
- Integrate with upstream spectrum governance once the anchor resolution primitives are ready.
