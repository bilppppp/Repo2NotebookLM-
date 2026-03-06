---
name: repo2notebooklm
description: Convert a Git repository into NotebookLM-ready structured sources (RepoBook + GraphBook), then optionally upload to NotebookLM. Use when user asks to import/ingest/update a repo into NotebookLM.
---

# repo2notebooklm

Use this skill to run the local `repo2nlm` tool end-to-end.

## When to use

- User asks to ingest a GitHub repo to NotebookLM
- User asks to generate RepoBook/GraphBook from code repositories
- User asks to update previously generated outputs incrementally

## Preconditions

- Run in project root: `/Users/gravity/Desktop/AI/Repo 到NotebookLM `
- Activate venv: `. .venv/bin/activate`
- `repo2nlm` executable exists in root

## Workflow

1. Ingest repository

```bash
./repo2nlm ingest <repo_url> --out ./out-<name> --max-file-kb 200
```

2. Incremental update (optional)

```bash
./repo2nlm update <repo_url> --out ./out-<name>
```

3. Upload to NotebookLM (optional)

```bash
./repo2nlm upload ./out-<name> --notebook "<name_or_id>" --create-if-missing
# 强制替换同名远端 source，避免保留旧内容
./repo2nlm upload ./out-<name> --notebook "<name_or_id>" --replace-existing
```

4. Cleanup local outputs (optional)

```bash
# 仅保留审计文件（stats/upload_map/manifest/graph）
bash skills/repo2notebooklm/scripts/cleanup_out.sh ./out-<name> --audit-only
```

## Expected outputs

- `out-<name>/RepoBook/*.md`
- `out-<name>/GraphBook.md`
- `out-<name>/manifest.json`
- `out-<name>/graph.json`
- `out-<name>/stats.json`
- `out-<name>/upload_map.json` (generated after `upload`)

## Notes

- `ingest` supports `--branch`, `--commit`, `--include`, `--exclude`, `--max-file-kb`
- `update` compares with existing `manifest.json` and reports changed/deleted files
- If upload fails, verify NotebookLM login with `notebooklm login`
- `upload` includes auto-recovery behavior:
  - auto-split large markdown files to `*.partNN.md`
  - clean stale/errored duplicate sources before retry
  - auto-switch to `large-auto` batching mode for very large uploads
  - reconcile local expected titles vs remote ready sources
- `upload_map.json` is the audit artifact for upload correctness:
  - `upload_mode` / `batch_size` / `file_count` / `total_bytes`: upload strategy evidence
  - `items[].original`: original local markdown file
  - `items[].uploaded_titles`: actual source titles uploaded to NotebookLM
  - `items[].split`: whether file was split
  - `items[].remote_sources[]`: remote `id/status/type/created_at`
  - acceptance rule: `missing_titles` must be empty
