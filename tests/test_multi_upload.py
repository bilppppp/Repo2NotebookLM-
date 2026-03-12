from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo2nlm.cli import build_parser
from repo2nlm.uploader import UploadSource, _collect_upload_sources, _prepare_sources_for_upload


class MultiUploadTests(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.base = Path(self._td.name)

    def tearDown(self) -> None:
        self._td.cleanup()

    def _make_out(self, name: str, files: list[str]) -> Path:
        out_dir = self.base / name
        repobook = out_dir / "RepoBook"
        repobook.mkdir(parents=True, exist_ok=True)
        for filename in files:
            if filename == "GraphBook.md":
                target = out_dir / filename
            else:
                target = repobook / filename
            target.write_text(f"# {name} {filename}\n", encoding="utf-8")
        stats = {
            "repo": f"https://github.com/example/{name}.git",
            "branch": "main",
            "commit": f"{name}-commit",
            "file_count": len(files),
            "text_file_count": len(files),
            "outputs": {
                "repobook_files": [
                    str(repobook / filename)
                    for filename in files
                    if filename != "GraphBook.md"
                ],
                "graphbook": str(out_dir / "GraphBook.md"),
            },
        }
        (out_dir / "stats.json").write_text(json.dumps(stats), encoding="utf-8")
        return out_dir

    def test_parser_accepts_multiple_out_directories(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "upload",
                "./out-mlflow",
                "./out-dispatch",
                "--notebook",
                "agents-compare",
            ]
        )
        self.assertEqual(args.out, ["./out-mlflow", "./out-dispatch"])

    def test_collect_upload_sources_prefixes_titles_for_multiple_out_dirs(self) -> None:
        mlflow = self._make_out("out-mlflow", ["00_overview.md", "GraphBook.md"])
        dispatch = self._make_out("out-dispatch", ["00_overview.md", "GraphBook.md"])
        staged_dir = self.base / "staged"
        staged_dir.mkdir()

        upload_sources = _collect_upload_sources(
            [mlflow, dispatch],
            staged_dir=staged_dir,
        )

        self.assertEqual(
            [p.name for p in upload_sources],
            [
                "WorkspaceIndex.md",
                "dispatch__00_overview.md",
                "dispatch__GraphBook.md",
                "mlflow__00_overview.md",
                "mlflow__GraphBook.md",
            ],
        )
        for src in upload_sources:
            self.assertTrue(src.exists())
        self.assertIn("Cross-Repo Questions", (staged_dir / "WorkspaceIndex.md").read_text(encoding="utf-8"))
        self.assertIn("https://github.com/example/out-mlflow.git", (staged_dir / "WorkspaceIndex.md").read_text(encoding="utf-8"))
        self.assertIn("https://github.com/example/out-dispatch.git", (staged_dir / "WorkspaceIndex.md").read_text(encoding="utf-8"))

    def test_collect_upload_sources_keeps_original_titles_for_single_out_dir(self) -> None:
        mlflow = self._make_out("out-mlflow", ["00_overview.md", "GraphBook.md"])

        upload_sources = _collect_upload_sources([mlflow], staged_dir=self.base / "staged-single")

        self.assertEqual(
            [p.name for p in upload_sources],
            ["00_overview.md", "GraphBook.md"],
        )
        self.assertFalse((self.base / "staged-single" / "WorkspaceIndex.md").exists())

    def test_prepare_sources_splits_namespaced_large_files(self) -> None:
        source = self.base / "dispatch__18_tools.md"
        source.write_text(("0123456789abcdef\n" * 8), encoding="utf-8")

        upload_specs, purge_titles = _prepare_sources_for_upload(
            [
                UploadSource(
                    out_dir=self.base / "out-dispatch",
                    namespace="dispatch",
                    original_title="18_tools.md",
                    upload_path=source,
                )
            ],
            self.base / "split-output",
            max_bytes=16,
        )

        self.assertEqual(purge_titles, {"dispatch__18_tools.md"})
        self.assertGreaterEqual(len(upload_specs), 1)
        self.assertTrue(all(spec.upload_path.exists() for spec in upload_specs))
        self.assertTrue(all(spec.upload_path.name.startswith("dispatch__18_tools.part") for spec in upload_specs))


if __name__ == "__main__":
    unittest.main()
