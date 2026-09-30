# Change log

## Phase two — 30 September 2026

- Added `phase2.py`, `review_tools.py`, executed `Fraud_Phase2.ipynb`, and `CASE_STUDY.md`.
- Added independent calibration, uncertainty estimates, development-only stability checks, and error analysis.
- Updated the README to lead with current evidence while preserving its phase-one content.
- Added focused tests. Preserved existing files, phase-one results, notebooks, and Git history.
- Run `python demo.py`, then open the local URL printed by the server. The demo scores public validation examples and compares frozen validation-derived review policies. Costs are hypothetical relative units; the cost recommendation uses validation outcomes only. The server binds to loopback, restricts routes and payload size, and writes no request data.

Data provenance and download checks are documented in `data/`. File paths and before/after SHA-256 hashes
are recorded in `AUDIT/phase2-file-changes.json`. Commit and push receipts are retained in the local audit log.
