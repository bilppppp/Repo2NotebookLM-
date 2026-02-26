#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <repo_url> <out_dir> [extra repo2nlm args...]"
  exit 1
fi

REPO_URL="$1"
OUT_DIR="$2"
shift 2

. .venv/bin/activate
./repo2nlm ingest "$REPO_URL" --out "$OUT_DIR" "$@"
