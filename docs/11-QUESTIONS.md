# Open questions and clarification register

**Status:** Open unless marked otherwise. Assign owners and resolutions through issues/ADRs. These questions are intentionally visible rather than disguised as requirements.

| ID | Question | Impact | Suggested next action |
| --- | --- | --- | --- |
| Q-01 | Which harness should power code execution? | adapter/session model | run candidate spike |
| Q-02 | Greenfield generation, existing repo edits, or both in MVP? | scope and fixtures | choose target scenario |
| Q-03 | Exact supported language/framework for demo? | toolchain | select one reference stack |
| Q-04 | What approvals require distinct identities? | identity/security | define MVP roles |
| Q-05 | Are changes returned as patch, branch, or PR? | Git integration | pick minimum testable output |
| Q-06 | Which scanner set and severity thresholds are mandatory? | release policy | approve security policy |
| Q-07 | What minimum acceptable AC-to-test coverage applies? | traceability gate | choose measurable rule |
| Q-08 | Which model/provider and budget can be used? | cost, privacy, reproducibility | set configuration requirements |
| Q-09 | What network egress does code execution need? | sandbox threat model | allowlist by fixture |
| Q-10 | How are artifacts and logs retained/redacted? | privacy/storage | define retention policy |
| Q-11 | React dashboard or Streamlit prototype? | build effort/UX | prototype critical screens |
| Q-12 | Does a conditional release require waiver approval? | governance | model exceptions |
| Q-13 | Should reviewers approve an AI-generated remediation before it is applied in sandbox? | human control | set approval policy |
| Q-14 | How are dependency installs and model skills sourced? | supply-chain risk | pin/check revisions |
| Q-15 | What benchmark would substantiate productivity improvement? | claims/evaluation | define baseline methodology |
| Q-16 | What is the project license and contributor policy? | redistribution | decide before copying code |
| Q-17 | Are generated artifacts allowed to include private repository content? | data handling | define data boundary |
| Q-18 | Who owns release recommendation versus branch merge authority? | accountability | document role mapping |

## Provisional defaults only

For a rapid demo, assume one user, one repository, Python/FastAPI target, manual merge, local storage, and limited remediation iterations. These defaults are **not approvals**; retain the ability to change them after the harness spike.
