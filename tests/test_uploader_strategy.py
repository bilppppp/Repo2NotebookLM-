from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo2nlm.uploader import (
    _AUTO_LARGE_FILE_THRESHOLD,
    _AUTO_LARGE_TOTAL_BYTES_THRESHOLD,
    _choose_upload_strategy,
)


class UploadStrategyTests(unittest.TestCase):
    def _make_files(self, specs: list[tuple[str, int]]) -> list[Path]:
        self._td = tempfile.TemporaryDirectory()
        base = Path(self._td.name)
        paths: list[Path] = []
        for name, size in specs:
            p = base / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"x" * size)
            paths.append(p)
        return paths

    def tearDown(self) -> None:
        td = getattr(self, "_td", None)
        if td:
            td.cleanup()

    def test_choose_standard_for_small_upload(self) -> None:
        files = self._make_files([("a.md", 1024), ("b.md", 2048)])
        strategy = _choose_upload_strategy(files)
        self.assertEqual(strategy["mode"], "standard")
        self.assertEqual(strategy["file_count"], 2)
        self.assertGreater(strategy["batch_size"], 0)

    def test_choose_large_for_many_files(self) -> None:
        files = self._make_files([(f"f{i:03d}.md", 1) for i in range(_AUTO_LARGE_FILE_THRESHOLD)])
        strategy = _choose_upload_strategy(files)
        self.assertEqual(strategy["mode"], "large-auto")
        self.assertEqual(strategy["file_count"], _AUTO_LARGE_FILE_THRESHOLD)

    def test_choose_large_for_total_size(self) -> None:
        files = self._make_files([("big.md", _AUTO_LARGE_TOTAL_BYTES_THRESHOLD)])
        strategy = _choose_upload_strategy(files)
        self.assertEqual(strategy["mode"], "large-auto")
        self.assertEqual(strategy["total_bytes"], _AUTO_LARGE_TOTAL_BYTES_THRESHOLD)


if __name__ == "__main__":
    unittest.main()
