# Setup Requirements

This template requires a few tools to be installed for full functionality.
All hooks fail gracefully if tools are missing — nothing will break, but
you'll lose validation features.

## Required

| Tool | Purpose | Install |
| ---- | ---- | ---- |
| **Git** | Version control, branch management | [git-scm.com](https://git-scm.com/) |
| **Codex** | AI agent CLI | Use the OpenAI Codex install path for your environment |
| **Python 3** | Shared hook JSON parsing and data-file validation | [python.org](https://www.python.org/) |
| **Bash** | Hook script execution | Included with Git for Windows |

## Recommended

| Tool | Used By | Purpose | Install |
| ---- | ---- | ---- | ---- |
| **jq** | Manual debugging only | Optional JSON inspection while troubleshooting hook payloads | See below |

### Installing jq

**Windows** (any of these):
```
winget install jqlang.jq
choco install jq
scoop install jq
```

**macOS**:
```
brew install jq
```

**Linux**:
```
sudo apt install jq     # Debian/Ubuntu
sudo dnf install jq     # Fedora
sudo pacman -S jq       # Arch
```

## Platform Notes

### Windows
- Git for Windows includes **Git Bash**, which provides the `bash` command
  used by all hooks in `.codex/hooks.json`
- Ensure Git Bash is on your PATH (default if installed via the Git installer)
- Hooks are dispatched through `.codex/hooks.json` with `CCGS_ROOT` set to the
  project root, so they work even when Codex starts from a subdirectory

### macOS / Linux
- Bash is available natively
- Python 3 is usually available; install it if hook parsing or JSON validation
  reports it missing

## Verifying Your Setup

Run these commands to check prerequisites:

```bash
git --version          # Should show git version
bash --version         # Should show bash version
jq --version           # Should show jq version (optional)
python3 --version      # Should show python version
```

## What Happens Without Optional Tools

| Missing Tool | Effect |
| ---- | ---- |
| **jq** | No runtime effect; hook scripts use the shared Python parser. |
| **Python 3** | Hook payload parsing and JSON data validation fail. Install Python 3 before relying on hook validation. |

## Recommended IDE

Codex works with any editor, but the template is optimized for:
- **VS Code** with the Codex extension
- **Cursor** (Codex compatible)
- Terminal-based Codex CLI
