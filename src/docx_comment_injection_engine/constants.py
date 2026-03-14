from __future__ import annotations

REQUIRED_COLUMNS = [
    "comment_id",
    "status",
    "pdf_page",
    "pdf_line_number",
    "target_excerpt",
    "comment_text",
]

OPTIONAL_COLUMNS = ["anchor_hint", "docx_location_hint", "notes"]

ELIGIBLE_STATUSES = {"READY", "APPROVED"}
SKIP_STATUSES = {"SKIP", "HOLD", "REJECTED"}
VALID_STATUSES = ELIGIBLE_STATUSES | SKIP_STATUSES

REPORT_FIELDS = [
    "comment_id",
    "pdf_page",
    "pdf_line_number",
    "target_excerpt",
    "result",
    "reason",
    "matched_pdf_text",
    "matched_docx_text",
    "matched_location",
    "confidence",
]

INJECTION_REPORT_NAME = "injection_report.csv"
VALIDATION_REPORT_NAME = "validation_report.json"
OUTPUT_DOCX_NAME = "commented.docx"

# TODO: add PDF anchor extraction and DOCX insertion configurations once primitives exist.
