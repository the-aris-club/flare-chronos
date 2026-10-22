"""Guards the published figures against the code that draws them.

``docs/figures/*.png`` are build artifacts: they are rendered from
``data/processed/empirical_results.json`` by
``apps/benchmark-cli/run_experiments.py``. A figure can therefore drift out of
sync with the code that produces it -- and it did. Figure 5 was published
while the renderer still drew its outline at SFAI +2.15 while the caption
announced +2.2, so four cells were outlined below the threshold the caption
claimed. PR #6 asserted that the threshold change "touches no cell"; it
touches four.

The outline geometry is font-independent -- the cell rectangles are drawn at
fixed canvas coordinates and the raster is downsampled uniformly, so the same
threshold yields byte-identical outlines whether the figure was rendered with
macOS Arial or Linux DejaVu (verified: IoU 1.0000 between the committed
macOS PNG and a Linux render at the same threshold). That makes it possible
to check the committed PNG against the code in CI, on any machine, without
requiring the reference toolchain.

Only the outline geometry is compared. The typography is not, because it
legitimately differs between the reference machine and a contributor's
machine.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_JSON = ROOT / "data" / "processed" / "empirical_results.json"
FIG5_PNG = ROOT / "docs" / "figures" / "fig5_harmonized_burning_calendar.png"

sys.path.insert(0, str(ROOT / "packages" / "harmonization-core" / "src"))
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))


def _outline_mask(png_path: Path):
    """Return the boolean mask of the figure's cyan outline pixels."""
    import numpy as np
    from PIL import Image

    arr = np.array(Image.open(png_path).convert("RGB"))
    red, green, blue = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    return (blue > 200) & (red < 100) & (green > 150)


class FigureMatchesCodeTest(unittest.TestCase):
    """The published Figure 5 must show what the current code draws."""

    def test_figure_five_outline_matches_the_rendered_threshold(self) -> None:
        """Figure 5's outlined cells equal those the current code produces.

        Regenerates Figure 5 from the committed results artifact and compares
        only the outline geometry, which does not depend on the installed
        fonts. A mismatch means the published PNG is stale: either the
        threshold changed and the figure was not regenerated, or the data
        changed underneath it.
        """
        from benchmark_cli.figure_renderer import render_fig5_burning_activity_calendar
        from benchmark_cli.run_experiments import build_26yr_calendars_and_series

        with RESULTS_JSON.open(encoding="utf-8") as handle:
            results = json.load(handle)

        _, cal = build_26yr_calendars_and_series(
            list(results["mekong_empirical_epochs"]),
            list(results["amazon_empirical_epochs"]),
        )

        with tempfile.TemporaryDirectory() as tmp:
            rendered = Path(tmp) / "fig5.png"
            render_fig5_burning_activity_calendar(rendered, cal)
            fresh = _outline_mask(rendered)

        committed = _outline_mask(FIG5_PNG)

        self.assertEqual(
            fresh.shape,
            committed.shape,
            "Figure 5 size differs from the rendered figure.",
        )

        missing = fresh & ~committed
        extra = committed & ~fresh
        self.assertEqual(
            int(missing.sum()),
            0,
            f"Figure 5 is missing {int(missing.sum())} outline pixels the "
            "current code draws. The published figure is stale -- regenerate "
            "it with `uv run python -m benchmark_cli.run_experiments`.",
        )
        self.assertEqual(
            int(extra.sum()),
            0,
            f"Figure 5 shows {int(extra.sum())} outline pixels the current "
            "code no longer draws. The published figure is stale -- "
            "regenerate it with `uv run python -m benchmark_cli.run_experiments`.",
        )
        self.assertGreater(
            int(fresh.sum()),
            0,
            "no outline detected; the comparison is not meaningful.",
        )


if __name__ == "__main__":
    unittest.main()
