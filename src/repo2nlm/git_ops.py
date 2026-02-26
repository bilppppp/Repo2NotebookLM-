from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def run_git(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def detect_default_branch(repo_url: str) -> str | None:
    out = run_git(["ls-remote", "--symref", repo_url, "HEAD"])
    for line in out.splitlines():
        if line.startswith("ref:") and "\tHEAD" in line:
            ref = line.split()[1]
            if ref.startswith("refs/heads/"):
                return ref.removeprefix("refs/heads/")
    return None


def prepare_repo_snapshot(repo_url: str, dest_dir: Path, branch: str | None, commit: str | None) -> tuple[str, str]:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    target_branch = branch or detect_default_branch(repo_url) or "main"
    run_git(["clone", "--depth", "1", "--branch", target_branch, repo_url, str(dest_dir)])

    if commit:
        run_git(["fetch", "--depth", "1", "origin", commit], cwd=dest_dir)
        run_git(["checkout", commit], cwd=dest_dir)

    final_commit = run_git(["rev-parse", "HEAD"], cwd=dest_dir)
    return target_branch, final_commit
