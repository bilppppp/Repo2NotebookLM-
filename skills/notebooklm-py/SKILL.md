---
name: notebooklm-py
description: Use when the user wants to operate NotebookLM directly from the CLI, including notebook/source management, source polling and verification, Q&A, artifact generation, notes, sharing, or research workflows.
---

# notebooklm-py

Use this skill when the task is to automate NotebookLM actions through CLI.

## Preconditions

- Activate venv: `. .venv/bin/activate`
- `notebooklm` command is available
- Auth is ready: `notebooklm auth check` (or run `notebooklm login`)

## Core commands

### Notebook

```bash
notebooklm list
notebooklm create "<title>"
notebooklm rename -n <notebook_id> "<new_title>"
notebooklm use <notebook_id>
notebooklm status
```

### Sources

```bash
notebooklm source add <url_or_file>
notebooklm source list --json
notebooklm source delete <source_id> -n <notebook_id> -y
notebooklm source wait <source_id>
notebooklm source guide <source_id> --json
notebooklm source fulltext <source_id> -o <file>
```

Useful polling pattern:

```bash
notebooklm source list -n <notebook_id> --json
# verify all sources are ready before claiming completion
```

### Chat

```bash
notebooklm ask --new --json "<question>"
notebooklm history -l 10
```

### Artifacts

```bash
notebooklm generate report --format study-guide --wait --json "<desc>"
notebooklm artifact list
notebooklm download report --latest <file>
```

Other types: `audio`, `video`, `slide-deck`, `infographic`, `mind-map`, `data-table`, `quiz`, `flashcards`.

### Notes / Share / Research

```bash
notebooklm note create "<content>" -t "<title>"
notebooklm share status
notebooklm source add-research "<query>" --mode fast --no-wait
notebooklm research wait --import-all
```

## Reliability guidance

- Prefer `--json` for machine-readable outputs
- Use explicit notebook IDs in automation (`--notebook` or `-n` when supported)
- For long generation, trigger first then poll/wait
- For source verification, prefer comparing `source list --json` against your local expected title set instead of assuming upload success from the command exit code alone
- `source wait` is useful, but for batch uploads you should still do a final `source list --json` reconciliation
