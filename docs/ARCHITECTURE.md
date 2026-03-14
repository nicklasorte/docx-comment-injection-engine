# Pipeline Shape

Matrix + PDF + DOCX → anchor resolution → DOCX insertion → injection report

MVP behavior:
1) Load and validate required inputs (files + matrix schema).
2) Normalize statuses and select eligible rows (`READY`, `APPROVED`).
3) Stub anchor resolution; annotate rows as `pending` or `skipped`.
4) Copy source DOCX to `commented.docx` placeholder.
5) Emit `injection_report.csv` and `validation_report.json` for auditability.

Deferred (explicit TODO):
- PDF anchor extraction and excerpt verification.
- DOCX text mapping and comment insertion.
- Ambiguity handling and confidence tuning.
- End-to-end integration with spectrum governance pipelines.
