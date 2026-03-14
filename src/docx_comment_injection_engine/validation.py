from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .constants import ELIGIBLE_STATUSES, REQUIRED_COLUMNS, VALID_STATUSES
from .errors import ValidationError


def normalize_status(value: str) -> str:
    return value.strip().upper() if isinstance(value, str) else ""


def load_matrix(matrix_path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    with matrix_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, fieldnames


def validate_required_files(matrix_path: Path, pdf_path: Path, docx_path: Path) -> List[Mapping[str, object]]:
    errors: List[Mapping[str, object]] = []
    for label, path in [
        ("matrix", matrix_path),
        ("pdf", pdf_path),
        ("docx", docx_path),
    ]:
        if not path.exists():
            errors.append(
                {
                    "type": "missing_file",
                    "field": label,
                    "path": str(path),
                    "message": f"Required {label} file not found: {path}",
                }
            )
    return errors


class MatrixValidator:
    def __init__(self, required_columns: Sequence[str] | None = None):
        self.required_columns = list(required_columns or REQUIRED_COLUMNS)

    def validate(self, rows: List[Dict[str, str]], fieldnames: List[str]) -> List[Mapping[str, object]]:
        errors: List[Mapping[str, object]] = []
        errors.extend(self._validate_required_columns(fieldnames))
        errors.extend(self._validate_rows(rows))
        errors.extend(self._validate_comment_id_uniqueness(rows))
        return errors

    def _validate_required_columns(self, fieldnames: List[str]) -> List[Mapping[str, object]]:
        errors: List[Mapping[str, object]] = []
        missing = [col for col in self.required_columns if col not in fieldnames]
        for col in missing:
            errors.append(
                {
                    "type": "missing_column",
                    "column": col,
                    "message": f"Required column '{col}' is missing from matrix",
                }
            )
        return errors

    def _validate_rows(self, rows: List[Dict[str, str]]) -> List[Mapping[str, object]]:
        errors: List[Mapping[str, object]] = []
        for idx, row in enumerate(rows, start=2):  # header is line 1
            status = normalize_status(row.get("status", ""))
            comment_id = (row.get("comment_id") or "").strip()
            if not status:
                errors.append(
                    {
                        "type": "missing_status",
                        "row": idx,
                        "message": "Status is required",
                    }
                )
            elif status not in VALID_STATUSES:
                errors.append(
                    {
                        "type": "invalid_status",
                        "row": idx,
                        "value": status,
                        "message": f"Status '{status}' is not allowed",
                    }
                )
            if not comment_id:
                errors.append(
                    {
                        "type": "missing_comment_id",
                        "row": idx,
                        "message": "comment_id is required",
                    }
                )
            errors.extend(self._validate_positive_integer(row, idx, "pdf_page"))
            errors.extend(self._validate_positive_integer(row, idx, "pdf_line_number"))

            if status in ELIGIBLE_STATUSES:
                for field in ("target_excerpt", "comment_text"):
                    if not (row.get(field) or "").strip():
                        errors.append(
                            {
                                "type": "missing_field",
                                "row": idx,
                                "field": field,
                                "message": f"{field} is required for eligible rows",
                            }
                        )
        return errors

    def _validate_positive_integer(self, row: Dict[str, str], idx: int, field: str) -> List[Mapping[str, object]]:
        errors: List[Mapping[str, object]] = []
        raw_value = (row.get(field) or "").strip()
        try:
            value = int(raw_value)
            if value <= 0:
                raise ValueError
        except ValueError:
            errors.append(
                {
                    "type": "invalid_integer",
                    "row": idx,
                    "field": field,
                    "value": raw_value,
                    "message": f"{field} must be a positive integer",
                }
            )
        return errors

    def _validate_comment_id_uniqueness(self, rows: List[Dict[str, str]]) -> List[Mapping[str, object]]:
        errors: List[Mapping[str, object]] = []
        seen: Dict[str, int] = {}
        for idx, row in enumerate(rows, start=2):
            comment_id = (row.get("comment_id") or "").strip()
            if not comment_id:
                continue
            if comment_id in seen:
                errors.append(
                    {
                        "type": "duplicate_comment_id",
                        "row": idx,
                        "comment_id": comment_id,
                        "message": f"comment_id '{comment_id}' is duplicated (first seen at row {seen[comment_id]})",
                    }
                )
            else:
                seen[comment_id] = idx
        return errors


def ensure_valid(matrix_path: Path, pdf_path: Path, docx_path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    file_errors = validate_required_files(matrix_path, pdf_path, docx_path)
    if any(err.get("field") == "matrix" for err in file_errors):
        raise ValidationError(file_errors)

    rows, fieldnames = load_matrix(matrix_path)
    validator = MatrixValidator()
    matrix_errors = validator.validate(rows, fieldnames)
    errors = file_errors + matrix_errors
    if errors:
        raise ValidationError(errors)
    return rows, fieldnames
