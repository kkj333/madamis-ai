#!/usr/bin/env bash
# Cursor hook: run Ruff on edited Python under backend/ or interface/ (mirrors CI).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
INPUT=$(cat)

read -r TARGET <<< "$(echo "$INPUT" | python3 -c "
import json, sys, os

root = os.path.abspath(sys.argv[1])
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
fp = (data.get('file_path') or '').strip()
if not fp.endswith('.py'):
    sys.exit(0)
try:
    abs_fp = os.path.abspath(fp)
except OSError:
    sys.exit(0)
if not abs_fp.startswith(root + os.sep):
    sys.exit(0)
if f'{os.sep}interface{os.sep}' in abs_fp:
    print('interface')
elif f'{os.sep}backend{os.sep}' in abs_fp:
    print('backend')
" "$REPO_ROOT")"

if [[ -z "${TARGET:-}" ]]; then
  echo '{}'
  exit 0
fi

cd "$REPO_ROOT"
if ! command -v uv >/dev/null 2>&1; then
  echo '{}' >&2
  exit 0
fi

(cd "$TARGET" && uv run ruff format . && uv run ruff check .)

echo '{}'
