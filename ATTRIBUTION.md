# Attribution

Codex Game Studios is an unofficial Codex-native port of
[Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios).

The port is pinned to upstream commit
`984023ddac0d5e27624f2baacde6105e45de375f` for mapping, attribution, and
verification evidence. Upstream-origin files remain tracked in
`.codex/manifest/upstream-assets.json`.

The upstream project is distributed under the MIT License. This source
distribution keeps the original license text and copyright notice in the root
`LICENSE` file. Installed target game repositories receive the same upstream
license text at `.codex/docs/UPSTREAM-LICENSE.md` so Codex Game Studios does
not overwrite the target project's own root license.

Runtime coexistence constraints for this port:

- Codex-owned files do not modify `.claude/`.
- Codex-owned files do not require or modify `CLAUDE.md`.
- Shared neutral project state remains available to both toolchains.
