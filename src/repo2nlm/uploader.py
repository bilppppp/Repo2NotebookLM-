from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _run(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def upload_to_notebooklm(out_dir: Path, notebook: str, create_if_missing: bool = False) -> None:
    cli = shutil.which("notebooklm")
    if not cli:
        raise RuntimeError("notebooklm CLI not found. Activate venv and install notebooklm-py.")

    rc, _, err = _run([cli, "use", notebook])
    if rc != 0:
        if not create_if_missing:
            raise RuntimeError(f"failed to select notebook '{notebook}': {err}")
        rc, _, err = _run([cli, "create", notebook])
        if rc != 0:
            raise RuntimeError(f"failed to create notebook '{notebook}': {err}")
        rc, _, err = _run([cli, "use", notebook])
        if rc != 0:
            raise RuntimeError(f"created notebook but failed to select '{notebook}': {err}")

    sources = sorted((out_dir / "RepoBook").glob("*.md"))
    graphbook = out_dir / "GraphBook.md"
    if graphbook.exists():
        sources.append(graphbook)

    if not sources:
        raise RuntimeError("no markdown sources found under output directory")

    for src in sources:
        rc, _, err = _run([cli, "source", "add", str(src)])
        if rc != 0:
            raise RuntimeError(f"failed to upload source {src}: {err}")
