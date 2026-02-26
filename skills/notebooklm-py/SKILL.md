---
name: notebooklm-py
description: Operate NotebookLM via notebooklm-py CLI, including notebook/source management, Q&A, artifact generation/download, notes, sharing, and research workflows.
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
notebooklm use <notebook_id>
notebooklm status
```

### Sources

```bash
notebooklm source add <url_or_file>
notebooklm source list --json
notebooklm source wait <source_id>
notebooklm source guide <source_id> --json
notebooklm source fulltext <source_id> -o <file>
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
