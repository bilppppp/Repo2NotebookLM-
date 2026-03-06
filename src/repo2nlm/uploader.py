from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

_AUTO_LARGE_FILE_THRESHOLD = 80
_AUTO_LARGE_TOTAL_BYTES_THRESHOLD = 64 * 1024 * 1024
_AUTO_LARGE_BATCH_SIZE = 20


def _run(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _run_json(args: list[str]) -> dict[str, Any]:
    rc, out, err = _run(args)
    if rc != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}: {err or out}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid json output from: {' '.join(args)}") from exc


def _resolve_notebook_id(cli: str, notebook: str, create_if_missing: bool) -> str:
    payload = _run_json([cli, "list", "--json"])
    notebooks = payload.get("notebooks", [])
    for nb in notebooks:
        if nb.get("id") == notebook or nb.get("title") == notebook:
            return str(nb["id"])

    if not create_if_missing:
        raise RuntimeError(f"notebook not found: {notebook}")

    created = _run_json([cli, "create", notebook, "--json"])
    nb = created.get("notebook", {})
    nb_id = nb.get("id")
    if not nb_id:
        raise RuntimeError(f"failed to create notebook: {notebook}")
    return str(nb_id)


def _split_markdown(src: Path, dst_dir: Path, chunk_bytes: int = 2 * 1024 * 1024) -> list[Path]:
    text = src.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    parts: list[str] = []
    buf: list[str] = []
    size = 0
    for line in lines:
        line_size = len(line.encode("utf-8", errors="ignore"))
        if buf and size + line_size > chunk_bytes:
            parts.append("".join(buf))
            buf = []
            size = 0
        buf.append(line)
        size += line_size
    if buf:
        parts.append("".join(buf))

    out: list[Path] = []
    for i, part in enumerate(parts, start=1):
        p = dst_dir / f"{src.stem}.part{i:02d}{src.suffix}"
        header = (
            f"# Split Source: {src.name} (part {i}/{len(parts)})\n\n"
            "This file was auto-split for NotebookLM upload reliability.\n\n"
        )
        p.write_text(header + part, encoding="utf-8")
        out.append(p)
    return out


def _prepare_sources_for_upload(sources: list[Path], tmp_dir: Path, max_bytes: int = 4 * 1024 * 1024) -> tuple[list[Path], set[str]]:
    upload_paths: list[Path] = []
    purge_titles: set[str] = set()
    for src in sources:
        if src.stat().st_size <= max_bytes:
            upload_paths.append(src)
            continue
        purge_titles.add(src.name)
        upload_paths.extend(_split_markdown(src, tmp_dir))
    return upload_paths, purge_titles


def _list_sources(cli: str, notebook_id: str) -> list[dict[str, Any]]:
    payload = _run_json([cli, "source", "list", "-n", notebook_id, "--json"])
    return payload.get("sources", [])


def _delete_source(cli: str, notebook_id: str, source_id: str) -> None:
    rc, out, err = _run([cli, "source", "delete", source_id, "-n", notebook_id, "-y"])
    if rc != 0:
        raise RuntimeError(f"failed to delete source {source_id}: {err or out}")


def _upload_and_wait(cli: str, notebook_id: str, src: Path) -> bool:
    rc, out, err = _run([cli, "source", "add", str(src), "-n", notebook_id, "--json"])
    if rc != 0:
        return False
    _ = out, err
    return True


def _is_split_title(title: str) -> bool:
    return bool(re.search(r"\.part\d{2}\.md$", title))


def _chunked(items: list[Path], chunk_size: int) -> list[list[Path]]:
    if chunk_size <= 0:
        return [items]
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def _choose_upload_strategy(upload_sources: list[Path]) -> dict[str, int | str]:
    total_bytes = sum(p.stat().st_size for p in upload_sources)
    file_count = len(upload_sources)
    large = (
        file_count >= _AUTO_LARGE_FILE_THRESHOLD
        or total_bytes >= _AUTO_LARGE_TOTAL_BYTES_THRESHOLD
    )
    return {
        "mode": "large-auto" if large else "standard",
        "file_count": file_count,
        "total_bytes": total_bytes,
        "batch_size": _AUTO_LARGE_BATCH_SIZE if large else file_count,
    }


def _read_local_commit(out_dir: Path) -> str | None:
    stats_file = out_dir / "stats.json"
    if not stats_file.exists():
        return None
    try:
        payload = json.loads(stats_file.read_text(encoding="utf-8"))
    except Exception:
        return None
    commit = payload.get("commit")
    return str(commit) if commit else None


def upload_to_notebooklm(
    out_dir: Path,
    notebook: str,
    create_if_missing: bool = False,
    replace_existing: bool = False,
) -> None:
    cli = shutil.which("notebooklm")
    if not cli:
        raise RuntimeError("notebooklm CLI not found. Activate venv and install notebooklm-py.")

    notebook_id = _resolve_notebook_id(cli, notebook, create_if_missing=create_if_missing)

    sources = sorted((out_dir / "RepoBook").glob("*.md"))
    graphbook = out_dir / "GraphBook.md"
    if graphbook.exists():
        sources.append(graphbook)

    if not sources:
        raise RuntimeError("no markdown sources found under output directory")

    with tempfile.TemporaryDirectory(prefix="repo2nlm_upload_") as td:
        upload_sources, purge_titles = _prepare_sources_for_upload(sources, Path(td))
        strategy = _choose_upload_strategy(upload_sources)
        expected_titles = {p.name for p in upload_sources}
        local_commit = _read_local_commit(out_dir)
        by_original: dict[str, list[str]] = {}
        source_name_set = {s.name for s in sources}
        for p in upload_sources:
            if p.name in source_name_set:
                by_original[p.name] = [p.name]
            else:
                prefix = p.name.split(".part", 1)[0] + ".md"
                by_original.setdefault(prefix, []).append(p.name)

        # Remove stale errored files that are replaced by split chunks.
        remote = _list_sources(cli, notebook_id)
        for r in remote:
            if r.get("title") in purge_titles:
                _delete_source(cli, notebook_id, str(r["id"]))
            # Remove stale split leftovers from previous uploads.
            if _is_split_title(str(r.get("title", ""))) and r.get("title") not in expected_titles:
                _delete_source(cli, notebook_id, str(r["id"]))

        # Upload/recover per source (batch mode for large projects).
        batches = _chunked(upload_sources, int(strategy["batch_size"]))
        for batch in batches:
            remote = _list_sources(cli, notebook_id)
            by_title: dict[str, list[dict[str, Any]]] = {}
            for r in remote:
                by_title.setdefault(str(r.get("title")), []).append(r)

            pending_titles: list[str] = []
            for src in batch:
                title = src.name
                same_title = by_title.get(title, [])
                if replace_existing:
                    for r in same_title:
                        _delete_source(cli, notebook_id, str(r["id"]))
                elif any(r.get("status") == "ready" for r in same_title):
                    for r in same_title:
                        if r.get("status") != "ready":
                            _delete_source(cli, notebook_id, str(r["id"]))
                    continue
                else:
                    for r in same_title:
                        _delete_source(cli, notebook_id, str(r["id"]))

                ok = False
                for _ in range(3):
                    if _upload_and_wait(cli, notebook_id, src):
                        ok = True
                        break
                if not ok:
                    raise RuntimeError(f"failed to upload source {src}")
                pending_titles.append(title)

            if not pending_titles:
                continue

            # For large uploads, checkpoint readiness per batch to avoid late surprises.
            remote = _list_sources(cli, notebook_id)
            by_title = {}
            for r in remote:
                by_title.setdefault(str(r.get("title")), []).append(r)
            for title in pending_titles:
                rows = by_title.get(title, [])
                if any(r.get("status") == "ready" for r in rows):
                    continue
                for r in rows:
                    if r.get("status") == "processing":
                        _run([cli, "source", "wait", str(r["id"]), "-n", notebook_id, "--timeout", "300"])

        # Reconciliation: ensure every expected source exists and is ready.
        remote = _list_sources(cli, notebook_id)
        by_title: dict[str, list[dict[str, Any]]] = {}
        for r in remote:
            by_title.setdefault(str(r.get("title")), []).append(r)

        # Wait for processing sources before final verdict.
        for title, rows in by_title.items():
            if title not in expected_titles:
                continue
            if any(r.get("status") == "ready" for r in rows):
                continue
            for r in rows:
                if r.get("status") == "processing":
                    _run([cli, "source", "wait", str(r["id"]), "-n", notebook_id, "--timeout", "300"])

        remote = _list_sources(cli, notebook_id)
        ready_titles = {r.get("title") for r in remote if r.get("status") == "ready"}
        missing = sorted(t for t in expected_titles if t not in ready_titles)
        if missing:
            raise RuntimeError(f"upload verification failed, missing/not-ready sources: {missing}")

        # Upload reconciliation map for auditing.
        by_title: dict[str, list[dict[str, Any]]] = {}
        for r in remote:
            by_title.setdefault(str(r.get("title")), []).append(
                {
                    "id": r.get("id"),
                    "status": r.get("status"),
                    "type": r.get("type"),
                    "created_at": r.get("created_at"),
                }
            )

        mapping_items: list[dict[str, Any]] = []
        for original in sorted(by_original):
            uploaded_titles = sorted(by_original[original])
            remote_sources: list[dict[str, Any]] = []
            for t in uploaded_titles:
                remote_sources.extend(by_title.get(t, []))
            mapping_items.append(
                {
                    "original": original,
                    "uploaded_titles": uploaded_titles,
                    "split": len(uploaded_titles) > 1,
                    "remote_sources": remote_sources,
                }
            )

        upload_map = {
            "notebook_id": notebook_id,
            "requested_notebook": notebook,
            "local_commit": local_commit,
            "replace_existing": replace_existing,
            "upload_mode": strategy["mode"],
            "batch_size": strategy["batch_size"],
            "file_count": strategy["file_count"],
            "total_bytes": strategy["total_bytes"],
            "expected_titles_count": len(expected_titles),
            "ready_titles_count": len(ready_titles),
            "missing_titles": missing,
            "items": mapping_items,
        }
        (out_dir / "upload_map.json").write_text(
            json.dumps(upload_map, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
