"""Guards the quantitative claims published in the narrative documents.

The proposal, the video script and the specification all quote headline numbers
(record counts, co-incident pair counts, Kolmogorov-Smirnov distances, R^2,
calibration parameters). Those numbers are produced by
``apps/benchmark-cli/run_experiments.py`` and land in
``data/processed/empirical_results.json``.

Prose drifts from data easily: the documents previously still quoted the
metrics of an earlier, smaller FIRMS pull (775,531 records / 5,769 co-incident
pairs / D_KS 0.1180 -> 0.0205) long after the pipeline had moved on to
1,609,194 records / 11,553 pairs / D_KS 0.1166 -> 0.0237. This module asserts
that every published claim still agrees with the committed results artifact, so
a future data refresh fails loudly instead of shipping a stale pitch.

Values are compared as *strings* because the documents render numbers in the
Vietnamese decimal convention (``.`` = thousands separator, ``,`` = decimal
separator). Each claim therefore lists the acceptable renderings.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_JSON = ROOT / "data" / "processed" / "empirical_results.json"

# Documents that publish quantitative claims about the harmonization results.
CLAIM_DOCS = (
    "docs/01_NASA_SpaceApps_Proposal.md",
    "docs/02_Cross_Sensor_Harmonization_Spec.md",
    "docs/03_System_Architecture_and_Data_Pipeline.md",
    "docs/05_Pitch_Deck_and_Video_Script.md",
    "exports/PROPOSAL.md",
)

# Metrics published by the calibration / benchmark pipeline.
CALIBRATION_DOCS = (
    "docs/01_NASA_SpaceApps_Proposal.md",
    "docs/02_Cross_Sensor_Harmonization_Spec.md",
    "docs/05_Pitch_Deck_and_Video_Script.md",
    "exports/PROPOSAL.md",
)


def vi(value: float, decimals: int = 1) -> str:
    """Render a number the way the Vietnamese-language documents do.

    ``1234.5`` becomes ``1.234,5`` (dot = thousands separator, comma = decimal).
    """
    return (
        f"{value:,.{decimals}f}".replace(",", "\x00")
        .replace(".", ",")
        .replace("\x00", ".")
    )


def en(value: float, decimals: int = 1) -> str:
    """Render a number the way the English-language documents do."""
    return f"{value:,.{decimals}f}"


def either(value: float, decimals: int = 1) -> tuple[str, ...]:
    """Both accepted renderings of a number."""
    return (en(value, decimals), vi(value, decimals))


class DocumentedClaimsConsistencyTest(unittest.TestCase):
    """Assert published claims match ``data/processed/empirical_results.json``."""

    @classmethod
    def setUpClass(cls) -> None:
        with RESULTS_JSON.open(encoding="utf-8") as handle:
            cls.results = json.load(handle)
        cls.docs = {
            name: (ROOT / name).read_text(encoding="utf-8") for name in CLAIM_DOCS
        }

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _cached_archive_row_count() -> tuple[int, int]:
        """Return ``(detection_rows, csv_slices)`` for the cached FIRMS archive."""
        total = 0
        slices = 0
        for path in sorted((ROOT / "data" / "raw").glob("*.csv")):
            slices += 1
            with path.open("rb") as handle:
                newlines = sum(
                    chunk.count(b"\n")
                    for chunk in iter(lambda: handle.read(1 << 20), b"")
                )
            total += max(0, newlines - 1)
        return total, slices

    def _assert_any_present(self, doc: str, label: str, forms: tuple[str, ...]) -> None:
        text = self.docs[doc]
        self.assertTrue(
            any(form in text for form in forms),
            f"{doc}: {label} is missing. Expected one of {forms!r}.",
        )

    def _assert_none_present(
        self, doc: str, label: str, forms: tuple[str, ...]
    ) -> None:
        text = self.docs[doc]
        for form in forms:
            self.assertNotIn(
                form,
                text,
                f"{doc}: superseded value {label!r} ({form!r}) is still published.",
            )

    # -------------------------------------------------------------------- tests

    def test_total_firms_record_count_is_published(self) -> None:
        """The cached archive size is quoted consistently everywhere it appears."""
        total, _ = self._cached_archive_row_count()
        forms = either(total, 0)
        for doc in (
            "docs/01_NASA_SpaceApps_Proposal.md",
            "docs/03_System_Architecture_and_Data_Pipeline.md",
            "docs/05_Pitch_Deck_and_Video_Script.md",
            "exports/PROPOSAL.md",
        ):
            self._assert_any_present(doc, "total FIRMS record count", forms)

    def test_cached_slice_count_is_published(self) -> None:
        """The number of cached FIRMS CSV slices is quoted where stated."""
        _, slices = self._cached_archive_row_count()
        pattern = re.compile(rf"(?<!\d){slices}(?!\d)")
        for doc in ("docs/01_NASA_SpaceApps_Proposal.md", "exports/PROPOSAL.md"):
            self.assertTrue(
                pattern.search(self.docs[doc]),
                f"{doc}: cached CSV slice count ({slices}) is missing.",
            )

    def test_coincident_pair_count_is_published(self) -> None:
        """The co-incident Aqua-SNPP pair count matches the calibration artifact."""
        n_pairs = self.results["coincident_calibration"]["n_pairs"]
        forms = either(n_pairs, 0)
        for doc in CALIBRATION_DOCS:
            self._assert_any_present(doc, "co-incident pair count N", forms)

    def test_kolmogorov_smirnov_distance_is_published(self) -> None:
        """D_KS before/after harmonization matches the calibration artifact."""
        calib = self.results["coincident_calibration"]
        for doc in CALIBRATION_DOCS:
            self._assert_any_present(
                doc, "D_KS before harmonization", either(calib["ks_before"], 4)
            )
            self._assert_any_present(
                doc, "D_KS after harmonization", either(calib["ks_after"], 4)
            )

    def test_kolmogorov_smirnov_reduction_percentage_is_published(self) -> None:
        """The advertised KS-error reduction matches the calibration artifact."""
        calib = self.results["coincident_calibration"]
        reduction = (1.0 - calib["ks_after"] / calib["ks_before"]) * 100.0
        forms = (f"{reduction:.1f}",) + either(reduction, 1)
        for doc in CALIBRATION_DOCS:
            self._assert_any_present(doc, "KS-error reduction percentage", forms)

    def test_calibration_parameters_are_published(self) -> None:
        """alpha and beta of the fitted power-law transfer function are published."""
        calib = self.results["coincident_calibration"]
        self._assert_any_present(
            "docs/01_NASA_SpaceApps_Proposal.md",
            "power-law alpha",
            either(calib["alpha"], 4),
        )
        self._assert_any_present(
            "docs/01_NASA_SpaceApps_Proposal.md",
            "power-law beta",
            either(calib["beta"], 4),
        )

    def test_cross_sensor_count_and_frp_ratios_are_published(self) -> None:
        """The VIIRS/MODIS count and FRP ratios match the calibration artifact."""
        calib = self.results["coincident_calibration"]
        count_ratio = calib["mean_coincident_viirs_to_modis_count_ratio"]
        frp_ratio = calib["mean_coincident_viirs_to_modis_frp_ratio"]
        for doc in (
            "docs/01_NASA_SpaceApps_Proposal.md",
            "docs/02_Cross_Sensor_Harmonization_Spec.md",
            "exports/PROPOSAL.md",
        ):
            self._assert_any_present(
                doc,
                "VIIRS/MODIS detection count ratio",
                (f"{count_ratio:.3f}",) + either(count_ratio * 1000, 0),
            )
            self._assert_any_present(
                doc,
                "VIIRS/MODIS FRP ratio",
                (f"{frp_ratio:.3f}",) + either(frp_ratio * 1000, 0),
            )

    def test_scan_angle_area_ratio_is_published(self) -> None:
        """The MODIS-edge / VIIRS-nadir footprint area ratio matches the artifact."""
        ratio = self.results["scan_angle_physics"][
            "max_area_ratio_modis_edge_to_viirs_nadir"
        ]
        self._assert_any_present(
            "docs/01_NASA_SpaceApps_Proposal.md",
            "MODIS-edge / VIIRS-nadir area ratio",
            either(ratio, 2),
        )

    def test_superseded_metrics_are_not_published(self) -> None:
        """Metrics from the superseded FIRMS pull must not appear anywhere.

        These are the values published before the archive was re-pulled and the
        calibration was refitted. Leaving them in place silently understates the
        evidence (5,769 pairs instead of 11,553) or overstates it (82.6% instead
        of 79.7%).
        """
        superseded = {
            "record count": ("775.531", "775,531"),
            "co-incident pair count": ("5.769", "5,769"),
            "KS reduction percentage": ("82,6", "82.6%"),
            "D_KS before": ("0.1180", "0,1180"),
            "D_KS after": ("0.0205", "0,0205"),
            "harmonized R^2": ("0.7463", "0,7463"),
            "power-law alpha": ("1.7284",),
            "power-law beta": ("0.9267",),
            "detection count ratio": ("3,751",),
            "FRP ratio": ("1,377",),
        }
        for doc in CLAIM_DOCS:
            for label, forms in superseded.items():
                self._assert_none_present(doc, label, forms)

    def test_legacy_record_count_variant_is_not_published(self) -> None:
        """Only one record count is published.

        ``data/raw/fetch_manifest.json`` sums to a slightly different figure
        than the published convention, which counts every detection row across
        every cached CSV slice. Mixing the two would make the proposal and the
        video contradict each other.
        """
        for doc in CLAIM_DOCS:
            self._assert_none_present(
                doc, "alternate record count", ("1.609.182", "1,609,182")
            )


if __name__ == "__main__":
    unittest.main()
