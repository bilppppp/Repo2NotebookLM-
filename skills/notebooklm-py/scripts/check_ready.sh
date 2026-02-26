#!/usr/bin/env bash
set -euo pipefail

. .venv/bin/activate
notebooklm auth check
notebooklm status
