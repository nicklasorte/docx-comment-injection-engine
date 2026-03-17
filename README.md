# DOCX Comment Injection Engine

Governed MVP scaffold for injecting governed comments into DOCX files based on a resolution matrix anchored to a source PDF. The current implementation focuses on deterministic validation, orchestration shape, and audit/report generation; actual anchor resolution and Word comment insertion are stubbed and intentionally marked TODO.

## Ecosystem context

This engine is part of the **spectrum-systems** ecosystem.

| Field | Value |
|-------|-------|
| `system_id` | `docx-comment-injection-engine` |
| `repo_type` | `operational-engine` |
| `architecture_layer` | `injection` |
| `governance_source` | `spectrum-systems` |
| Governing contract | `contracts/engine_contract.md` |
| Governance declaration | `governance/governance-declaration.json` |
| System manifest | `governance/system-manifest.json` |
| Evaluation manifest | `eval/evaluation-manifest.json` |

See `docs/repo-standardization-summary.md` for a full normalization record.

## MVP scope
- Inputs: resolution matrix (CSV), source PDF, source DOCX.
- Outputs: commented DOCX placeholder (copied from source), structured injection report, validation/audit artifacts.
- Behaviors: validate inputs and matrix schema, normalize statuses, decide eligible rows, emit report with stubbed insertion results, fail loudly when validation fails.

## Repository layout
- `src/` – engine code and CLI entry point.
- `tests/` – unit tests covering validation and report generation.
- `fixtures/` – sample matrix/PDF/DOCX and expected report fixture.
- `examples/` – minimal contract-aligned input/output examples.
- `outputs/` – target directory for generated artifacts (ignored except for `.gitkeep`).
- `contracts/` – local contract and schema notes.
- `docs/` – architecture note and supporting docs.
- `governance/` – machine-readable governance declaration and system manifest.
- `eval/` – evaluation manifest scaffold.
- `scripts/` – helper script for running the engine locally.
- `.github/workflows/ci.yml` – CI: unit tests and governance validation.

## Quickstart
Ensure Python 3.10+ is available.

```bash
export PYTHONPATH=src
python -m docx_comment_injection_engine.cli \
  --matrix fixtures/sample_matrix.csv \
  --pdf fixtures/sample_source.pdf \
  --docx fixtures/sample_source.docx \
  --output-dir outputs
```

Artifacts produced:
- `outputs/commented.docx` – direct copy of the source DOCX (stubbed insertion).
- `outputs/injection_report.csv` – structured report of each matrix row and insertion result.
- `outputs/validation_report.json` – validation pass/fail summary.

See `scripts/run_engine.sh` for a wrapper that sets `PYTHONPATH` for you.

## Matrix contract (summary)
Required columns (must be present): `comment_id`, `source_agency`, `comment_text`, `comment_response`, `status`, `revision_id`, `pdf_page`, `pdf_line_number`, `target_excerpt`, `target_section_heading`, `injection_text`, `injection_mode`, `anchor_confidence`, `notes`. Optional but preserved: `anchor_hint`, `docx_location_hint`.

Status normalization:
- Eligible for insertion: `READY`, `APPROVED`.
- Skipped but allowed: `SKIP`, `HOLD`, `REJECTED`.
- Anything else fails validation.

Validation rules:
- All required files must exist.
- Required columns must be present.
- `comment_id` must be unique and non-empty.
- `pdf_page` and `pdf_line_number` must be positive integers.
- Eligible rows must have non-empty `target_excerpt`, `comment_text`, `comment_response`, `target_section_heading`, `injection_text`, `injection_mode`, `source_agency`, `revision_id`.
- `anchor_confidence`, when provided, must be numeric between 0 and 1.
- Structured errors are emitted when validation fails.

Output report fields:
`comment_id, pdf_page, pdf_line_number, target_excerpt, result, reason, matched_pdf_text, matched_docx_text, matched_location, confidence` (eligible rows are marked `stubbed` until real insertion lands).

Full contract details live in `contracts/engine_contract.md`.

## Tests
```bash
export PYTHONPATH=src
python -m unittest discover -s tests -v
```

## Roadmap / TODO
- PDF anchor extraction and excerpt verification (TODO).
- DOCX text mapping and actual Word comment insertion (TODO).
- Ambiguity handling and confidence scoring (TODO).
- Robust PDF parsing and DOCX manipulation once stubs are replaced.
