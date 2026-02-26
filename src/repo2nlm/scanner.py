from __future__ import annotations

import fnmatch
import hashlib
from pathlib import Path

from .config import LANG_BY_EXT, TEXT_EXTENSIONS
from .types import FileRecord


def _is_text(data: bytes, ext: str) -> bool:
    if ext in TEXT_EXTENSIONS:
        return True
    if b"\0" in data:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _is_excluded(rel_path: str, patterns: list[str]) -> bool:
    norm = rel_path.replace("\\", "/")
    return any(fnmatch.fnmatch(norm, pat) for pat in patterns)


def scan_files(repo_root: Path, exclude: list[str], max_file_kb: int) -> tuple[list[FileRecord], list[dict[str, str]]]:
    files: list[FileRecord] = []
    skipped: list[dict[str, str]] = []
    max_bytes = max_file_kb * 1024

    for abs_path in sorted(p for p in repo_root.rglob("*") if p.is_file()):
        rel = abs_path.relative_to(repo_root).as_posix()
        if _is_excluded(rel, exclude):
            skipped.append({"path": rel, "reason": "excluded"})
            continue

        data = abs_path.read_bytes()
        ext = abs_path.suffix.lower()
        text = _is_text(data[:4096], ext)
        if not text:
            skipped.append({"path": rel, "reason": "binary"})
            files.append(
                FileRecord(
                    path=rel,
                    abs_path=abs_path,
                    size=len(data),
                    sha256=hashlib.sha256(data).hexdigest(),
                    lang=LANG_BY_EXT.get(ext, ext.removeprefix(".")),
                    text=False,
                    truncated=False,
                    content="",
                )
            )
            continue

        truncated = len(data) > max_bytes
        if truncated:
            head = data[: max_bytes // 2]
            tail = data[-(max_bytes // 2) :]
            payload = head + b"\n\n...TRUNCATED...\n\n" + tail
        else:
            payload = data

        content = payload.decode("utf-8", errors="replace")
        files.append(
            FileRecord(
                path=rel,
                abs_path=abs_path,
                size=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                lang=LANG_BY_EXT.get(ext, ext.removeprefix(".")),
                text=True,
                truncated=truncated,
                content=content,
            )
        )

    return files, skipped
