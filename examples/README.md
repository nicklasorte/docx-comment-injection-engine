# Examples

This directory contains minimal, contract-aligned examples illustrating the expected inputs and outputs of the DOCX Comment Injection Engine.

## Files

| File | Description |
|------|-------------|
| `example_matrix.csv` | Minimal resolution matrix with two rows (one eligible, one skipped) |
| `example_injection_report.csv` | Expected injection report output for `example_matrix.csv` |
| `example_validation_report.json` | Expected validation report output for a successful run |

## Usage

These examples demonstrate the shape of data the engine expects and produces.  
All fields conform to `contracts/engine_contract.md`.

Run the engine against the sample fixtures in `fixtures/` to see live output:

```bash
export PYTHONPATH=src
python -m docx_comment_injection_engine.cli \
  --matrix fixtures/sample_matrix.csv \
  --pdf fixtures/sample_source.pdf \
  --docx fixtures/sample_source.docx \
  --output-dir outputs
```
