from __future__ import annotations

REQUIRED_COLUMNS = [
    "comment_id",
    "source_agency",
    "comment_text",
    "comment_response",
    "status",
    "revision_id",
    "pdf_page",
    "pdf_line_number",
    "target_excerpt",
    "target_section_heading",
    "injection_text",
    "injection_mode",
    "anchor_confidence",
    "notes",
]

OPTIONAL_COLUMNS = ["anchor_hint", "docx_location_hint"]

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
