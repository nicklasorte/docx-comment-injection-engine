# Engine Contract

## Inputs
- Resolution matrix: CSV with header.
- Source PDF: path to the PDF used for page/line anchors.
- Source DOCX: path to the Word document that will receive comments.

## Required matrix columns
- `comment_id` – unique identifier for the comment row.
- `status` – lifecycle indicator; normalized to uppercase.
- `pdf_page` – positive integer page index (1-based).
- `pdf_line_number` – positive integer line number within the page (1-based).
- `target_excerpt` – excerpt expected to align to the PDF anchor.
- `comment_text` – text to insert as a comment in the DOCX.

Optional columns recognized (preserved but not enforced): `anchor_hint`, `docx_location_hint`, `notes`.

## Status handling
- Eligible for insertion: `READY`, `APPROVED`.
- Allowed but skipped: `SKIP`, `HOLD`, `REJECTED`.
- Any other value triggers validation failure.

## Outputs
All artifacts are written into the provided output directory:
- `commented.docx` – copy of the source DOCX (until real insertion is implemented).
- `injection_report.csv` – row-wise results of insertion attempts.
- `validation_report.json` – structured summary of validation pass/fail.

Injection report fields:
- `comment_id`
- `pdf_page`
- `pdf_line_number`
- `target_excerpt`
- `result` (`pending`, `skipped`)
- `reason`
- `matched_pdf_text`
- `matched_docx_text`
- `matched_location`
- `confidence`

## Failure behavior
- Validation runs before any mutation; failures abort the run.
- Errors are emitted as structured records that identify type, field/column, and row where possible.
- No artifacts are mutated when validation fails.

## Audit expectations
- Validation report captures pass/fail and the list of errors.
- Injection report records per-row outcomes and placeholder matching data.
