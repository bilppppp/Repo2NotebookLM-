# repo2nlm

[中文](README.md) | [English](README.en.md)

Convert GitHub repositories into NotebookLM-ready structured learning material.

Outputs:

- `RepoBook/` for code and documentation content
- `GraphBook.md` for directory responsibilities and import relationships
- `manifest.json` for the scanned file index
- `graph.json` for dependency graph data
- `stats.json` for scan and update statistics

## Install for AI Agents

You can send this directly to your AI agent:

```text
Help me install repo2nlm: https://raw.githubusercontent.com/bilppppp/Repo2NotebookLM-/main/install.md
```

Installation document: [`install.md`](install.md)

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
# Unofficial NotebookLM API/CLI
pip install git+https://github.com/teng-lin/notebooklm-py.git
```

> notebooklm-py: https://github.com/teng-lin/notebooklm-py?tab=readme-ov-file

## Usage

```bash
repo2nlm ingest <repo_url> --branch main --out ./out --max-file-kb 200 \
  --exclude "node_modules/**,dist/**,.git/**"

repo2nlm update <repo_url> --out ./out

repo2nlm upload ./out --notebook <name_or_id> --create-if-missing
# Fully refresh matching remote sources
repo2nlm upload ./out --notebook <name_or_id> --replace-existing

# Merge multiple repository outputs into one NotebookLM notebook
# Remote source titles are automatically namespaced as <repo>__<filename>.md
# An extra WorkspaceIndex.md is generated for cross-repo navigation
repo2nlm upload ./out-mlflow ./out-dispatch ./out-hermes-agent \
  --notebook <name_or_id> --create-if-missing
```

## Notes

- `update` reads the previous `manifest.json`, computes changed files, and rebuilds outputs.
- `upload` depends on the `notebooklm` CLI provided by `notebooklm-py`.
- Use `--replace-existing` if you want the remote notebook content to match the local `out/` directory strictly.
- `upload` accepts multiple `out-*` directories in one command. When more than one directory is provided, it uses the `out-` suffix as the repo namespace and uploads sources as `<repo>__<filename>.md` to avoid collisions such as `00_overview.md` or `GraphBook.md`.
- Multi-directory upload also generates `WorkspaceIndex.md`, which summarizes repository metadata, GraphBook entry points, and cross-repo query hints.
- Large repositories automatically switch to batch upload and batch waiting mode to reduce missed sources during long uploads.

## Should You Keep Local `out` Directories?

Recommended policy: keep audit artifacts, delete regenerable content when needed.

- Recommended to keep:
  - `stats.json` for commit and scan statistics
  - `upload_map.json` for remote reconciliation; `missing_titles` must be empty
  - `manifest.json` / `graph.json` for future diffing and structure analysis
- Safe to delete:
  - `RepoBook/*.md`
  - `GraphBook.md` / `GraphBook.part*.md`
  - temporary artifacts, screenshots, and debug output

Cleanup example:

```bash
bash skills/repo2notebooklm/scripts/cleanup_out.sh ./out-<name> --audit-only
```

## Skills

- `skills/repo2notebooklm`: convert Git repositories into RepoBook + GraphBook and upload them to NotebookLM
- `skills/notebooklm-py`: operate NotebookLM through the CLI for notebooks, sources, chat, artifacts, and research workflows
