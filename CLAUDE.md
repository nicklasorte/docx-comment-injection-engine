# Claude Agent Notes

- Adhere to the documented contract in `contracts/engine_contract.md`.
- Keep outputs deterministic and side-effect free beyond the declared artifacts.
- When extending functionality, preserve validation-first flow and structured error reporting.
- Use existing fixtures and schemas for guidance; add new ones only when the contract evolves.
- TODO markers identify deferred work (PDF anchors, DOCX insertion, ambiguity handling); do not silently implement speculative behavior.
