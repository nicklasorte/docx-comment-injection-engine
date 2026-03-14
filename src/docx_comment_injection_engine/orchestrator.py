from __future__ import annotations

import csv
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping

from . import validation
from .constants import (
    ELIGIBLE_STATUSES,
    INJECTION_REPORT_NAME,
    OUTPUT_DOCX_NAME,
    REPORT_FIELDS,
    VALIDATION_REPORT_NAME,
)
from .errors import ValidationError


@dataclass
class OrchestrationResult:
    injection_report_path: Path
    output_docx_path: Path
    validation_report_path: Path
    eligible_count: int
    skipped_count: int


def _normalized_row(row: Mapping[str, str]) -> Dict[str, object]:
    status = validation.normalize_status(row.get("status", ""))
    return {
        "comment_id": (row.get("comment_id") or "").strip(),
        "status": status,
        "pdf_page": int((row.get("pdf_page") or "0").strip()),
        "pdf_line_number": int((row.get("pdf_line_number") or "0").strip()),
        "target_excerpt": (row.get("target_excerpt") or "").strip(),
        "comment_text": (row.get("comment_text") or "").strip(),
        "anchor_hint": (row.get("anchor_hint") or "").strip(),
    }


def _build_injection_records(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for row in rows:
        status = row["status"]
        eligible = status in ELIGIBLE_STATUSES
        result = "pending" if eligible else "skipped"
        reason = (
            "Insertion stubbed; awaiting PDF anchor resolution and DOCX comment insertion TODOs."
            if eligible
            else f"Status '{status}' is not eligible for insertion."
        )
        records.append(
            {
                "comment_id": row["comment_id"],
                "pdf_page": row["pdf_page"],
                "pdf_line_number": row["pdf_line_number"],
                "target_excerpt": row["target_excerpt"],
                "result": result,
                "reason": reason,
                "matched_pdf_text": "",
                "matched_docx_text": "",
                "matched_location": "",
                "confidence": "",
            }
        )
    return records


def _write_injection_report(path: Path, records: List[Dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def _write_validation_report(path: Path, passed: bool, errors: List[Mapping[str, object]]) -> None:
    payload = {"passed": passed, "errors": errors}
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _copy_placeholder_docx(source_docx: Path, output_dir: Path) -> Path:
    target = output_dir / OUTPUT_DOCX_NAME
    shutil.copy(source_docx, target)
    return target


def run_pipeline(matrix_path: Path, pdf_path: Path, docx_path: Path, output_dir: Path) -> OrchestrationResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        rows, _fieldnames = validation.ensure_valid(matrix_path, pdf_path, docx_path)
        validation_errors: List[Mapping[str, object]] = []
    except ValidationError as exc:
        validation_report_path = output_dir / VALIDATION_REPORT_NAME
        _write_validation_report(validation_report_path, passed=False, errors=exc.errors)
        raise

    normalized_rows = [_normalized_row(row) for row in rows]
    records = _build_injection_records(normalized_rows)
    injection_report_path = output_dir / INJECTION_REPORT_NAME
    _write_injection_report(injection_report_path, records)

    validation_report_path = output_dir / VALIDATION_REPORT_NAME
    _write_validation_report(validation_report_path, passed=True, errors=validation_errors)

    output_docx_path = _copy_placeholder_docx(docx_path, output_dir)

    eligible_count = sum(1 for row in normalized_rows if row["status"] in ELIGIBLE_STATUSES)
    skipped_count = len(normalized_rows) - eligible_count

    # TODO: replace placeholder insertion with real PDF anchor resolution and DOCX comment application.
    return OrchestrationResult(
        injection_report_path=injection_report_path,
        output_docx_path=output_docx_path,
        validation_report_path=validation_report_path,
        eligible_count=eligible_count,
        skipped_count=skipped_count,
    )
