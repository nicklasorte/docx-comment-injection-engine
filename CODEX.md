# CODEX Agent Notes

- Keep changes minimal and governed; do not freelance new behaviors outside the contract.
- Preserve ASCII; match existing comment style and avoid noisy annotations.
- Prefer standard library over new dependencies unless the contract forces otherwise.
- Validate before mutating; fail loudly with structured errors.
- Mirror patterns from other czar engines: deterministic inputs/outputs, small fixtures, and explicit TODOs for deferred features.
- Tests should use the provided fixtures and stay hermetic (no network, no external binaries).
