# Contributing to Atomic-Agent

Atomic-Agent is in early architecture discovery. Start with the [documentation index](README.md), [open questions](docs/11-QUESTIONS.md), and [decision log](docs/10-DECISIONS.md).

## PR workflow

1. Open a focused issue or reference an existing open question/ADR.
2. Branch from `main`, e.g. `docs/...`, `feat/...`, or `fix/...`.
3. Make a small, reviewable change; update relevant contract docs.
4. Include test/reproduction evidence, security impact, and follow-up decisions in the PR description.
5. Request review. Merge only once required checks and approvals pass. Prefer squash merges for a clear history where repository settings allow.

## PR description checklist

- [ ] Motivation and linked issue/ADR
- [ ] User-visible behavior and architecture impact
- [ ] Requirements/criteria covered, with IDs
- [ ] Commands run and evidence of success/failure (or explain docs-only)
- [ ] Security/privacy impact and external dependencies
- [ ] Decisions made, open questions, limitations
- [ ] Rollback or migration consideration

## Documentation conventions

Use Markdown; cross-link related specs; mark unapproved choices **PROPOSED** or **OPEN**. Update the requirements table, ADR and demo acceptance material when implementation contracts change. Do not assert a gate is passing based only on agent prose.

## Source, privacy, and safety

Keep confidential/internal briefs, customer data, personal credentials, private repository source, proprietary benchmarks, and secrets out of public issues/PRs. Treat repository content and model/tool outputs as untrusted. Disclose third-party code dependencies and verify their licenses before copying any source.

## Review standards

Correctness, clear ownership boundaries, reproducible test evidence, explicit assumptions, minimal privileges, and maintainable interface contracts take priority over speed. Human approvals remain necessary at defined quality and merge gates.
