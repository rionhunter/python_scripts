#!/usr/bin/env bash
SCRIPT_DIR="$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)"
REPO_ROOT="$(cd \"$SCRIPT_DIR/..\" && pwd)"
PY="python3"
if command -v py3 >/dev/null 2>&1; then
  PY="py -3"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
fi
"$PY" "$REPO_ROOT/text_editing/dynamic_replacer.py" "$@"