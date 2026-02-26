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
```

## Expected outputs

- `out-<name>/RepoBook/*.md`
- `out-<name>/GraphBook.md`
- `out-<name>/manifest.json`
- `out-<name>/graph.json`
- `out-<name>/stats.json`

## Notes

- `ingest` supports `--branch`, `--commit`, `--include`, `--exclude`, `--max-file-kb`
- `update` compares with existing `manifest.json` and reports changed/deleted files
- If upload fails, verify NotebookLM login with `notebooklm login`
