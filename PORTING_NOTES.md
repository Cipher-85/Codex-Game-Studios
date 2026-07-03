# Porting Notes

Codex Game Studios preserves the upstream studio workflow while replacing
Claude-specific runtime surfaces with Codex-native equivalents.

## Lineage

- Upstream: [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
- Pinned upstream commit: `984023ddac0d5e27624f2baacde6105e45de375f`
- Port target: Codex custom agents, repo-local skills, hooks, rules, install
  manifests, and `AGENTS.md` startup instructions

## Porting Principles

- Preserve upstream role names and workflow intent.
- Use exact hyphenated Codex agent names.
- Keep Claude runtime files out of the Codex install surface.
- Preserve target project ownership, especially root instructions and licenses.
- Validate package shape through `.codex/audit.sh` before release.

## Evidence

Detailed conversion evidence is kept under
[docs/codex-conversion/](docs/codex-conversion/). That directory is historical
porting evidence; the release-facing usage path starts in [README.md](README.md)
and [.codex/docs/README.md](.codex/docs/README.md).

Key evidence files:

- [docs/codex-conversion/upstream-inventory.md](docs/codex-conversion/upstream-inventory.md)
- [docs/codex-conversion/codex-mapping-matrix.md](docs/codex-conversion/codex-mapping-matrix.md)
- [docs/codex-conversion/implementation-plan.md](docs/codex-conversion/implementation-plan.md)
- [docs/codex-conversion/validation-suite.md](docs/codex-conversion/validation-suite.md)
