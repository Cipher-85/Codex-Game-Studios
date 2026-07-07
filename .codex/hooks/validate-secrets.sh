#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
source "$script_dir/../lib/hooks.sh"

payload="$(ccgs_read_stdin)"
command_text="$(ccgs_json_field "$payload" "tool_input.command")"

if [ -z "$command_text" ]; then
  exit 0
fi

python_cmd="$(ccgs_first_python || true)"
if [ -z "$python_cmd" ]; then
  printf 'WARNING: Python not found; cannot inspect Bash command for .env secret access. Hook will fail open.\n' >&2
  exit 0
fi

if "$python_cmd" - "$command_text" <<'PY'
import re
import shlex
import sys

command = sys.argv[1]


def env_path(token: str) -> bool:
    token = token.strip()
    if not token:
        return False
    token = token.strip("\"'")
    token = re.sub(r"^\d+", "", token)
    token = token.lstrip("<>")
    token = token.split("=", 1)[-1] if token.startswith("--") and "=" in token else token
    name = token.rstrip(";|&")
    base = name.rsplit("/", 1)[-1]
    return (
        base == ".env"
        or base.startswith(".env.")
        or base.startswith(".env-")
        or base.startswith(".env_")
        or base.endswith(".env")
        or base.endswith(".env.local")
    )


def redirects_env(text: str) -> bool:
    return bool(re.search(r"(?:^|[^A-Za-z0-9_])(?:\d*)[<>]{1,2}\s*(?:['\"])?(?:[^'\"\s;&|]*/)?(?:\.env(?:[._-][^'\"\s;&|]*)?|[^'\"\s;&|]*\.env(?:\.local)?)(?:['\"])?", text))


try:
    tokens = shlex.split(command, posix=True)
except ValueError:
    tokens = re.findall(r"[^\s;&|]+", command)

read_commands = {
    "awk",
    "cat",
    "cut",
    "grep",
    "head",
    "less",
    "more",
    "sed",
    "tail",
    "type",
    "vim",
    "vi",
}
write_commands = {
    "cp",
    "install",
    "mv",
    "nano",
    "tee",
    "touch",
    "vim",
    "vi",
}

blocked = redirects_env(command)
for index, token in enumerate(tokens):
    cmd = token.rsplit("/", 1)[-1]
    if cmd in read_commands | write_commands:
        for arg in tokens[index + 1 :]:
            if arg.startswith("-") and not env_path(arg):
                continue
            if env_path(arg):
                blocked = True
                break
    if blocked:
        break

sys.exit(0 if blocked else 1)
PY
then
  ccgs_hook_deny "BLOCKED: Bash command attempts to read or write .env secret files"
fi

exit 0
