# Test Standards

---
paths:
  - "tests/**"
---

## Code-Turn Discipline

1. Identify the behavior under test and the bug or contract the test should
   catch.
2. Define assertions that fail for the broken behavior and pass for the intended
   behavior.
3. Prefer small deterministic tests with local fixtures.
4. Do not rewrite unrelated tests or shared fixtures unless required.

## Rules

- Test naming: `test_[system]_[scenario]_[expected_result]`.
- Every test must have a clear arrange/act/assert structure.
- Unit tests must not depend on external state such as filesystem, network, or
  database.
- Integration tests must clean up after themselves.
- Performance tests must specify acceptable thresholds and fail if exceeded.
- Test data must be defined in the test or in dedicated fixtures, never shared
  mutable state.
- Mock external dependencies; tests should be fast and deterministic.
- Every bug fix must have a regression test that would have caught the original
  bug.
