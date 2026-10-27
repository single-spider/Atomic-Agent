# Requirement-to-code traceability (MVP)

Traceability is now represented as immutable, version-bound **human-reviewed links** between each acceptance criterion ID and an implementation file explicitly named in the current `code` artifact's changed-path inventory. The operator records `ac_id`, exact code revision, path, reviewer identity and timestamp. `Store.traceability` and `GET /runs/{id}/traceability` expose all historical links plus current-coverage and unmapped-criterion lists. The dashboard supports adding and viewing these links.

Before evaluating release, a developer/reviewer must record criterion coverage using `POST /runs/{id}/traceability` with `{"ac_id":"AC-001","file_path":"app/main.py"}` and an authorized operator token. The control plane rejects unknown criteria, paths absent from the declared changed paths, path traversal, and requests outside the `VALIDATING` state. A new code revision makes all earlier links **stale** automatically; they remain in history for audits.

The release gate requires **both** mapped mandatory criteria to current code paths and executed passing tests mapped to every mandatory criterion. A model's proposed mapping or prose assertion alone cannot satisfy either requirement. This is a traceability *record* and reviewer attestation, not mathematical proof that implementation semantics match the requirement. The actual code revision and changed-path list still require independent sandbox/workspace verification before a live harness run can be trusted.

The synthetic Docker walkthrough records links for all six fixture criteria to the single approved changed source path. The dataset and review are explicitly synthetic; the trusted dependency audit remains missing, so release assessment still returns NOT_READY.
