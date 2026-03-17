import csv
import json
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
            handle.write(
                "comment_id,source_agency,comment_text,comment_response,status,revision_id,pdf_page,pdf_line_number,target_excerpt,injection_text,injection_mode,anchor_confidence,notes\n"
            )
            handle.write(
                "C1,Agency A,Missing excerpt,Response,READY,rev-1,1,1,Excerpt text,Injection text,comment,0.5,Note\n"
            )
            bad_matrix = Path(handle.name)
        with self.assertRaises(ValidationError) as ctx:
            validation.ensure_valid(bad_matrix, self.sample_pdf, self.sample_docx)
        self.assertTrue(any(err.get("type") == "missing_column" for err in ctx.exception.errors))

    def test_duplicate_comment_id(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write(
                "comment_id,source_agency,comment_text,comment_response,status,revision_id,pdf_page,pdf_line_number,target_excerpt,target_section_heading,injection_text,injection_mode,anchor_confidence,notes\n"
            )
            handle.write(
                "C1,Agency A,Excerpt text,Response,READY,rev-1,1,1,Excerpt,Heading 1,Injection text,comment,0.5,Note\n"
            )
            handle.write(
                "C1,Agency A,Another excerpt,Response,READY,rev-2,2,2,Another,Heading 2,Injection text,comment,0.5,Note\n"
            )
            dup_matrix = Path(handle.name)
        with self.assertRaises(ValidationError) as ctx:
            validation.ensure_valid(dup_matrix, self.sample_pdf, self.sample_docx)
        self.assertTrue(any(err.get("type") == "duplicate_comment_id" for err in ctx.exception.errors))

    def test_invalid_page_or_line(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write(
                "comment_id,source_agency,comment_text,comment_response,status,revision_id,pdf_page,pdf_line_number,target_excerpt,target_section_heading,injection_text,injection_mode,anchor_confidence,notes\n"
            )
            handle.write(
                "C1,Agency A,Excerpt text,Response,READY,rev-1,-1,0,Excerpt,Heading,Injection text,comment,0.5,Note\n"
            )
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
        self.assertEqual(ready_row["result"], "stubbed")
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


class GovernanceTests(unittest.TestCase):
    """Validate governance artifacts exist and are structurally valid."""

    GOVERNANCE_DIR = ROOT / "governance"
    EVAL_DIR = ROOT / "eval"

    GOVERNANCE_DECLARATION_REQUIRED_FIELDS = [
        "system_id",
        "implementation_repo",
        "architecture_source",
        "contract_pins",
        "schema_pins",
        "rule_version",
        "prompt_set_hash",
        "evaluation_manifest_path",
        "last_evaluation_date",
        "external_storage_policy",
        "governance_declaration_version",
    ]

    SYSTEM_MANIFEST_REQUIRED_FIELDS = [
        "repo_name",
        "repo_type",
        "architecture_layer",
        "system_id",
        "governance_source",
        "contracts_consumed",
        "contracts_produced",
    ]

    EVALUATION_MANIFEST_REQUIRED_FIELDS = [
        "system_id",
        "harness",
        "fixture_paths",
        "evidence_output_path",
    ]

    def _load_json(self, path: Path) -> dict:
        self.assertTrue(path.exists(), f"Expected file not found: {path}")
        with path.open() as handle:
            return json.load(handle)

    def test_governance_declaration_exists_and_is_valid(self) -> None:
        data = self._load_json(self.GOVERNANCE_DIR / "governance-declaration.json")
        missing = [f for f in self.GOVERNANCE_DECLARATION_REQUIRED_FIELDS if f not in data]
        self.assertFalse(
            missing,
            f"governance-declaration.json missing required fields: {missing}",
        )

    def test_system_manifest_exists_and_is_valid(self) -> None:
        data = self._load_json(self.GOVERNANCE_DIR / "system-manifest.json")
        missing = [f for f in self.SYSTEM_MANIFEST_REQUIRED_FIELDS if f not in data]
        self.assertFalse(
            missing,
            f"system-manifest.json missing required fields: {missing}",
        )

    def test_evaluation_manifest_exists_and_is_valid(self) -> None:
        data = self._load_json(self.EVAL_DIR / "evaluation-manifest.json")
        missing = [f for f in self.EVALUATION_MANIFEST_REQUIRED_FIELDS if f not in data]
        self.assertFalse(
            missing,
            f"evaluation-manifest.json missing required fields: {missing}",
        )

    def test_evaluation_manifest_fixture_paths_exist(self) -> None:
        data = self._load_json(self.EVAL_DIR / "evaluation-manifest.json")
        for rel_path in data.get("fixture_paths", []):
            self.assertTrue(
                (ROOT / rel_path).exists(),
                f"evaluation-manifest.json references missing fixture: {rel_path}",
            )

    def test_governance_declaration_contract_pins_exist(self) -> None:
        data = self._load_json(self.GOVERNANCE_DIR / "governance-declaration.json")
        for name, rel_path in data.get("contract_pins", {}).items():
            self.assertTrue(
                (ROOT / rel_path).exists(),
                f"contract_pin '{name}' references missing file: {rel_path}",
            )

    def test_governance_declaration_evaluation_manifest_path_exists(self) -> None:
        data = self._load_json(self.GOVERNANCE_DIR / "governance-declaration.json")
        eval_path = data.get("evaluation_manifest_path", "")
        if eval_path:
            self.assertTrue(
                (ROOT / eval_path).exists(),
                f"evaluation_manifest_path '{eval_path}' does not exist",
            )

    def test_ci_workflow_exists(self) -> None:
        ci_path = ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(ci_path.exists(), f"CI workflow not found: {ci_path}")


class ExamplesTests(unittest.TestCase):
    """Validate contract-aligned examples are structurally consistent."""

    EXAMPLES_DIR = ROOT / "examples"

    def test_example_matrix_has_required_columns(self) -> None:
        from docx_comment_injection_engine.constants import REQUIRED_COLUMNS

        matrix_path = self.EXAMPLES_DIR / "example_matrix.csv"
        self.assertTrue(matrix_path.exists(), f"Example matrix not found: {matrix_path}")
        with matrix_path.open() as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
        self.assertFalse(
            missing,
            f"example_matrix.csv missing required columns: {missing}",
        )

    def test_example_injection_report_has_required_fields(self) -> None:
        report_path = self.EXAMPLES_DIR / "example_injection_report.csv"
        self.assertTrue(report_path.exists(), f"Example injection report not found: {report_path}")
        with report_path.open() as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
        expected_fields = [
            "comment_id",
            "pdf_page",
            "pdf_line_number",
            "target_excerpt",
            "result",
            "reason",
        ]
        missing = [f for f in expected_fields if f not in fieldnames]
        self.assertFalse(
            missing,
            f"example_injection_report.csv missing fields: {missing}",
        )

    def test_example_validation_report_is_valid_json(self) -> None:
        report_path = self.EXAMPLES_DIR / "example_validation_report.json"
        self.assertTrue(report_path.exists(), f"Example validation report not found: {report_path}")
        with report_path.open() as handle:
            data = json.load(handle)
        self.assertIn("valid", data)
        self.assertIn("errors", data)


if __name__ == "__main__":
    unittest.main()
