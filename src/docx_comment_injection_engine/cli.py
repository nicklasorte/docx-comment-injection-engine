from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import ValidationError
from .orchestrator import run_pipeline


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PDF-anchored DOCX comment injection MVP (validation + report only)."
    )
    parser.add_argument("--matrix", required=True, help="Path to the resolution matrix CSV")
    parser.add_argument("--pdf", required=True, help="Path to the source PDF")
    parser.add_argument("--docx", required=True, help="Path to the source DOCX")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where commented DOCX, injection report, and validation report are written",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    matrix_path = Path(args.matrix)
    pdf_path = Path(args.pdf)
    docx_path = Path(args.docx)
    output_dir = Path(args.output_dir)

    try:
        result = run_pipeline(matrix_path, pdf_path, docx_path, output_dir)
    except ValidationError as exc:
        sys.stderr.write("Validation failed; see validation_report.json for details.\n")
        for error in exc.errors:
            sys.stderr.write(f"- {error.get('message')}\n")
        return 1

    sys.stdout.write(f"Injection report: {result.injection_report_path}\n")
    sys.stdout.write(f"Validation report: {result.validation_report_path}\n")
    sys.stdout.write(f"Commented DOCX placeholder: {result.output_docx_path}\n")
    sys.stdout.write(
        f"Eligible rows: {result.eligible_count}, skipped rows: {result.skipped_count}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
