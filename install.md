# repo2nlm — Installation Guide

## For Humans

Copy this to your AI agent:

```text
帮我安装 repo2nlm：https://raw.githubusercontent.com/bilppppp/Repo2NotebookLM-/main/install.md
```

English version:

```text
Help me install repo2nlm: https://raw.githubusercontent.com/bilppppp/Repo2NotebookLM-/main/install.md
```

---

## For AI Agents

### Goal

Install `repo2nlm` in the current project so the user can:

- ingest GitHub repositories into RepoBook + GraphBook outputs
- upload one or more `out-*` directories to NotebookLM
- merge multiple repos into one NotebookLM notebook
- generate `WorkspaceIndex.md` for cross-repo navigation

### Boundaries

- Do not use `sudo` unless the user explicitly approves it
- Do not modify files outside this project unless required by Python/venv setup
- Prefer using the project-local virtual environment at `.venv/`
- If NotebookLM authentication is missing, stop and ask the user to log in

### Step 1: Set up the virtual environment

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
```

### Step 2: Install repo2nlm and NotebookLM CLI

```bash
pip install -e .
pip install git+https://github.com/teng-lin/notebooklm-py.git
```

### Step 3: Verify commands

```bash
./repo2nlm --help
notebooklm --help
```

### Step 4: Check NotebookLM auth

```bash
notebooklm auth check
```

If auth is not ready, ask the user to run:

```bash
notebooklm login
```

### Step 5: Smoke test

Single repo flow:

```bash
./repo2nlm ingest <repo_url> --out ./out-<name> --max-file-kb 200
./repo2nlm upload ./out-<name> --notebook "<name_or_id>" --create-if-missing
```

Multi-repo flow:

```bash
./repo2nlm upload ./out-foo ./out-bar --notebook "<name_or_id>" --create-if-missing
```

### Step 6: Verify upload correctness

For a single repo:

```bash
jq '{requested_notebook, expected_titles_count, ready_titles_count, missing_titles}' ./out-<name>/upload_map.json
```

For a merged notebook:

1. Read all relevant `upload_map.json` files
2. Union every `items[].uploaded_titles`
3. Compare that union with:

```bash
notebooklm source list -n <notebook_id> --json
```

Acceptance rule:

- no missing titles
- no extra titles
- all remote sources are `ready`

### Quick Reference

```bash
./repo2nlm ingest <repo_url> --out ./out-<name> --max-file-kb 200
./repo2nlm update <repo_url> --out ./out-<name>
./repo2nlm upload ./out-<name> --notebook "<name_or_id>" --create-if-missing
./repo2nlm upload ./out-foo ./out-bar --notebook "<name_or_id>" --create-if-missing
notebooklm auth check
notebooklm source list -n <notebook_id> --json
```
