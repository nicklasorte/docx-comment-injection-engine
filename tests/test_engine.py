import csv
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from docx_comment_injection_engine import validation
from docx_comment_injection_engine.errors import ValidationError
from docx_comment_injection_engine.orchestrator import run_pipeline


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixtures = ROOT / "fixtures"
        self.sample_matrix = self.fixtures / "sample_matrix.csv"
        self.sample_pdf = self.fixtures / "sample_source.pdf"
        self.sample_docx = self.fixtures / "sample_source.docx"

    def test_validation_success(self) -> None:
        rows, fieldnames = validation.ensure_valid(self.sample_matrix, self.sample_pdf, self.sample_docx)
        self.assertEqual(len(rows), 3)
        self.assertIn("comment_id", fieldnames)

    def test_missing_required_column(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write("comment_id,status,pdf_page,pdf_line_number,comment_text\n")
            handle.write("C1,READY,1,1,Missing excerpt\n")
            bad_matrix = Path(handle.name)
        with self.assertRaises(ValidationError) as ctx:
            validation.ensure_valid(bad_matrix, self.sample_pdf, self.sample_docx)
        self.assertTrue(any(err.get("type") == "missing_column" for err in ctx.exception.errors))

    def test_duplicate_comment_id(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write(
                "comment_id,status,pdf_page,pdf_line_number,target_excerpt,comment_text\n"
            )
            handle.write("C1,READY,1,1,Excerpt,Text\n")
            handle.write("C1,READY,2,2,Another,Text\n")
            dup_matrix = Path(handle.name)
        with self.assertRaises(ValidationError) as ctx:
            validation.ensure_valid(dup_matrix, self.sample_pdf, self.sample_docx)
        self.assertTrue(any(err.get("type") == "duplicate_comment_id" for err in ctx.exception.errors))

    def test_invalid_page_or_line(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write(
                "comment_id,status,pdf_page,pdf_line_number,target_excerpt,comment_text\n"
            )
            handle.write("C1,READY,-1,0,Excerpt,Text\n")
            bad_numbers = Path(handle.name)
        with self.assertRaises(ValidationError) as ctx:
            validation.ensure_valid(bad_numbers, self.sample_pdf, self.sample_docx)
        errors = [err.get("type") for err in ctx.exception.errors]
        self.assertIn("invalid_integer", errors)


class OrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixtures = ROOT / "fixtures"
        self.sample_matrix = self.fixtures / "sample_matrix.csv"
        self.sample_pdf = self.fixtures / "sample_source.pdf"
        self.sample_docx = self.fixtures / "sample_source.docx"

    def test_eligible_vs_skipped_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = run_pipeline(self.sample_matrix, self.sample_pdf, self.sample_docx, output_dir)
            with result.injection_report_path.open() as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(result.eligible_count, 2)
        self.assertEqual(result.skipped_count, 1)
        ready_row = next(row for row in rows if row["comment_id"] == "CMT-001")
        self.assertEqual(ready_row["result"], "pending")
        skipped_row = next(row for row in rows if row["comment_id"] == "CMT-002")
        self.assertEqual(skipped_row["result"], "skipped")
        self.assertIn("not eligible", skipped_row["reason"])

    def test_injection_report_generation(self) -> None:
        expected_report = self.fixtures / "expected_injection_report.csv"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = run_pipeline(self.sample_matrix, self.sample_pdf, self.sample_docx, output_dir)
            with result.injection_report_path.open() as handle:
                actual_rows = list(csv.DictReader(handle))
        with expected_report.open() as handle:
            expected_rows = list(csv.DictReader(handle))
        self.assertEqual(len(actual_rows), len(expected_rows))
        # Compare a subset of critical fields to allow for future extension.
        for actual, expected in zip(actual_rows, expected_rows):
            self.assertEqual(actual["comment_id"], expected["comment_id"])
            self.assertEqual(actual["result"], expected["result"])
            self.assertEqual(actual["reason"], expected["reason"])


if __name__ == "__main__":
    unittest.main()
