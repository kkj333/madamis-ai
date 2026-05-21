#!/usr/bin/env bash
# Scan commit-target paths for non-placeholder ops values (madamis-ai).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PATHS=(
  README.md
  spec.md
  backend/docs
  backend/.env.example
  interface/.env.example
  terraform/*.tfvars.example
  .github/workflows
  .cursor/skills/redact-project-info
)

search() {
  local pattern="$1"
  local desc="$2"
  echo "=== ${desc} ==="
  if command -v rg >/dev/null 2>&1; then
    rg -n --no-heading -S "$pattern" "${PATHS[@]}" 2>/dev/null \
      | rg -v 'patterns\.local\.example|/SKILL\.md.*YOUR_|scan\.sh|your-gcp-project-id|your-discord' || true
  else
    grep -RIn -E "$pattern" "${PATHS[@]}" 2>/dev/null || true
  fi
  echo
}

echo "Scanning for non-placeholder ops values..."
echo "Ignored: terraform.tfvars, backend/.env, interface/.env, patterns.local"
echo

HITS=0
run() {
  local out
  out="$(search "$1" "$2")"
  echo "$out"
  if echo "$out" | grep -qE '^[^=]+:[0-9]+:'; then
    HITS=1
  fi
}

run 'project_id[[:space:]]*=[[:space:]]*"(?!your-|YOUR_)[^"]{3,}"' \
  'project_id literal (not your-* / YOUR_*)'

run '--project=(?!YOUR_)[a-z][a-z0-9-]{5,}' \
  'gcloud --project (not YOUR_*)'

run 'https://[a-z0-9-]+\.run\.app' \
  'https://*.run.app URL'

run 'MTQ[A-Za-z0-9._-]{20,}' \
  'Discord bot token pattern'

run 'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+\.' \
  'JWT-like token'

run 'projects/[0-9]{10,}/' \
  'GCP numeric project in path'

LOCAL="${SKILL_DIR}/patterns.local"
if [[ -f "$LOCAL" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="$(echo "$line" | xargs 2>/dev/null || true)"
    [[ -z "$line" ]] && continue
    run "$line" "patterns.local: ${line}"
  done <"$LOCAL"
fi

if [[ "$HITS" -eq 1 ]]; then
  echo "=> Review hits. Use placeholders per .cursor/skills/redact-project-info/SKILL.md"
  exit 1
fi

echo "=> No obvious non-placeholder ops literals in scanned paths."
exit 0
