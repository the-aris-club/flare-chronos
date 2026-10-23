"""The archive the published numbers came from is pinned byte for byte."""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))

from benchmark_cli.pin_raw_data import checksums

RAW = ROOT / "data" / "raw"


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

    def test_the_pin_script_reproduces_the_committed_checksums(self) -> None:
        self.assertEqual(checksums(RAW), (RAW / "SHA256SUMS").read_text())


if __name__ == "__main__":
    unittest.main()
