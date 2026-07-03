# Security Policy

## Supported Project

Security reports for this repository should target the Codex-native Game Studios
port and its installer/runtime files. The upstream Claude runtime is preserved as
source context only and is not an active Codex dependency in this fork.

## Reporting a Vulnerability

Please open a private security advisory on the `Cipher-85/Codex-Game-Studios`
repository when possible. If that is not available, open a minimal public issue
that avoids exploit details and asks the maintainer to coordinate disclosure.

Include:

- Affected file or workflow.
- Reproduction steps.
- Expected impact.
- Any local commands used to verify the finding.

## Boundaries

Do not include secrets, API keys, private game project assets, or player data in
reports. Do not run destructive proof-of-concept commands against user projects.

## Verification

Security fixes should run the narrowest relevant check and, before release, the
standard gates:

```bash
python3 .codex/lib/validate_manifest.py --root "$PWD"
./.codex/audit.sh all --root "$PWD"
```
