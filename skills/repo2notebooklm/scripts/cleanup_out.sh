#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <out_dir> [--audit-only]"
  exit 1
fi

OUT_DIR="$1"
MODE="${2:-}"

if [ ! -d "$OUT_DIR" ]; then
  echo "Directory not found: $OUT_DIR"
  exit 1
fi

if [ "$MODE" = "--audit-only" ]; then
  # Keep only small audit files for upload traceability.
  find "$OUT_DIR" -mindepth 1 -maxdepth 1 \
    ! -name "stats.json" \
    ! -name "upload_map.json" \
    ! -name "manifest.json" \
    ! -name "graph.json" \
    -exec rm -rf {} +
  echo "Cleaned $OUT_DIR (audit-only kept: stats/upload_map/manifest/graph)."
  exit 0
fi

rm -rf "$OUT_DIR"
echo "Removed $OUT_DIR"
