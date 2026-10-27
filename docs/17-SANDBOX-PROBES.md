# Docker isolation development probes

This is a **development smoke test**, not the final ADR-012 security preflight or production sandbox attestation.

On GitHub Actions, `Development Docker sandbox probes` builds `docker/Dockerfile.fixture-dev` in a trusted CI bootstrap environment and obtains its **immutable local image ID** (`sha256:...`). `DockerRunner` accepts that ID or a repository digest, refusing floating tags. Code/test/scanner checks run with `--network=none`, `--read-only`, a source-only read-only bind, a restricted temp filesystem, dropped capabilities, no new privileges, UID 65534, and memory/CPU/PID limits. The runtime does not fetch packages or advisories.

`python -m atomic_agent.sandbox_probe --image sha256:<...> --workspace fixtures/customer_profile` checks: attempts to edit the source are denied, outward TCP connectivity fails, no Docker socket is mounted, and no model API key is available in the container. It executes the **real** fixture Pytest, Ruff and Bandit binaries and checks parsed outputs; the golden Pytest baseline must still fail only AC-003. The resulting report is for the reviewed synthetic benchmark only.

This probe currently does not establish: immutable upstream base image/provenance, full hash-locked transitive dependencies, complete `pip-audit` vulnerability results, robust cancellation of child process trees, host-level rootless Docker isolation, seccomp/adversarial escape resistance, prompt-injection resistance, secret redaction in arbitrary outputs, model gateway credential separation, cost limits, or live harness safety. Dedicated adversarial tests and exact-version manifests must be reviewed before any untrusted model-generated code execution or harness comparison.
