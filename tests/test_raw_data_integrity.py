"""The archive the published numbers came from is pinned byte for byte."""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


class TestRawDataIntegrity(unittest.TestCase):
    def test_every_pinned_file_matches_its_checksum(self) -> None:
        pinned: dict[str, str] = {}
        for line in (RAW / "SHA256SUMS").read_text().splitlines():
            digest, name = line.split("  ", 1)
            pinned[name] = digest
        self.assertTrue(pinned)
        for name, digest in pinned.items():
            with self.subTest(file=name):
                self.assertEqual(
                    hashlib.sha256((RAW / name).read_bytes()).hexdigest(), digest
                )

    def test_no_csv_in_the_archive_is_unpinned(self) -> None:
        pinned = {
            line.split("  ", 1)[1]
            for line in (RAW / "SHA256SUMS").read_text().splitlines()
        }
        self.assertEqual({p.name for p in RAW.glob("*.csv")} - pinned, set())


if __name__ == "__main__":
    unittest.main()
