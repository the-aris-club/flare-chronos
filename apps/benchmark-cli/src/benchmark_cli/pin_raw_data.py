"""Pin the raw FIRMS archive: write ``data/raw/SHA256SUMS`` for every CSV.

Run after adding or replacing a slice, then commit the CSVs together with the
refreshed SHA256SUMS. ``tests/test_raw_data_integrity.py`` fails until you do.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[4] / "data" / "raw"


def checksums(raw_dir: Path) -> str:
    """The SHA256SUMS text for every CSV in ``raw_dir``, sorted by name."""
    lines = [
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}"
        for p in sorted(raw_dir.glob("*.csv"))
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    (RAW_DIR / "SHA256SUMS").write_text(checksums(RAW_DIR))
    print(
        f"pinned {len(list(RAW_DIR.glob('*.csv')))} files in {RAW_DIR / 'SHA256SUMS'}"
    )


if __name__ == "__main__":
    main()
