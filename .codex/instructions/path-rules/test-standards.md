# Test Standards

---
paths:
  - "tests/**"
  - "Assets/Tests/**"
  - "Source/*/Tests/**"
  - "Source/*/Private/Tests/**"
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

## Engine test locations

Read `.codex/docs/coding-standards.md` for the engine test roots and execution
contract. Godot tests use `tests/`; Unity tests use test assemblies under
`Assets/Tests/`; Unreal tests belong to a compiled module under
`Source/<Module>/Private/Tests/` (or the project's existing test module).
Use the language's naming conventions: `test_*` GDScript functions, NUnit
`[Test]` methods, unique Unreal automation classes and matching test filters.
A test file's existence is not proof it compiled, was discovered, or passed.

Read `.codex/docs/qa-policy.md` for effective level/strictness and the mandatory
evidence floor. Use `.codex/docs/technical-config.md` to verify the installed
runner and engine pin; lower QA settings never excuse a required failing test.
