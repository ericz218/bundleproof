# BundleProof project instructions

- Keep the runtime dependency-free unless a dependency removes substantially more code than it adds.
- Checks must be deterministic, offline, and covered by a minimal regression test.
- Avoid false positives: errors fail releases; uncertain conditions are warnings.
- Update `memory/HANDOFF.md` when a task ends.

