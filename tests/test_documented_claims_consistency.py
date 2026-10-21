"""Guards the quantitative claims published in the narrative documents.

The proposal, the video script and the specification all quote headline numbers
(record counts, co-incident pair counts, Kolmogorov-Smirnov distances, R^2,
calibration parameters). Those numbers are produced by
``apps/benchmark-cli/run_experiments.py`` and land in
``data/processed/empirical_results.json``.

Prose drifts from data easily: the documents previously still quoted the
metrics of an earlier, smaller FIRMS pull (775,531 records / 5,769 co-incident
pairs / D_KS 0.1180 -> 0.0205) long after the pipeline had moved on to
1,609,182 records / 11,553 pairs / D_KS 0.1166 -> 0.0237. This module asserts
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
MANIFEST_JSON = ROOT / "data" / "raw" / "fetch_manifest.json"

# Documents that publish quantitative claims about the harmonization results.
CLAIM_DOCS = (
    "docs/01_NASA_SpaceApps_Proposal.md",
    "docs/02_Cross_Sensor_Harmonization_Spec.md",
    "docs/03_System_Architecture_and_Data_Pipeline.md",
    "docs/05_Pitch_Deck_and_Video_Script.md",
    "exports/PROPOSAL.md",
    "exports/REPORT.md",
)

# Metrics published by the calibration / benchmark pipeline.
CALIBRATION_DOCS = (
    "docs/01_NASA_SpaceApps_Proposal.md",
    "docs/02_Cross_Sensor_Harmonization_Spec.md",
    "docs/05_Pitch_Deck_and_Video_Script.md",
    "exports/PROPOSAL.md",
)

# Generated artifacts that embed the same claims in hardcoded strings. The PDF
# is built from these, so a stale literal here ships a stale PDF even when
# every markdown file agrees with the artifact.
CLAIM_SOURCES = ("exports/export_pdf.py",)


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
        cls.sources = {
            name: (ROOT / name).read_text(encoding="utf-8") for name in CLAIM_SOURCES
        }

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _manifest_record_count() -> tuple[int, int]:
        """Return ``(detection_rows, csv_slices)`` from the fetch manifest.

        ``data/raw/fetch_manifest.json`` is the authoritative record of the
        archive: one entry per fetched FIRMS CSV slice, valued with that
        slice's detection row count. It is deliberately *not* a glob over
        ``data/raw/*.csv`` -- that directory also holds
        ``firms_data_availability.csv`` (sensor availability metadata, not
        detections) and header-only empty slices, and counting those inflated
        the published total by 12 rows.
        """
        with MANIFEST_JSON.open(encoding="utf-8") as handle:
            manifest = json.load(handle)
        slices = {name: rows for name, rows in manifest.items() if rows > 0}
        return sum(slices.values()), len(slices)

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

    def _assert_present_with_context(
        self,
        doc: str,
        label: str,
        forms: tuple[str, ...],
        context: str,
    ) -> None:
        """Assert a value appears on a line that also states what it counts.

        A bare substring check passes when the number appears somewhere in the
        document under the wrong label. Requiring the surrounding context makes
        the guard fail when a claim is attached to the wrong metric.
        """
        pattern = re.compile(
            r"^(?P<line>.*(?:" + "|".join(re.escape(f) for f in forms) + r").*)$",
            re.MULTILINE,
        )
        for match in pattern.finditer(self.docs[doc]):
            if re.search(context, match.group("line"), re.IGNORECASE):
                return
        self.fail(
            f"{doc}: {label} is missing, or appears only without matching "
            f"context {context!r}. Expected one of {forms!r}."
        )

    # -------------------------------------------------------------------- tests

    def test_fetch_manifest_matches_the_cached_slices(self) -> None:
        """Every manifest entry is a real file, and no real slice is unlisted.

        This keeps the published record count honest: the manifest is the
        source of truth, so a slice dropped into ``data/raw/`` without a
        manifest entry (or a manifest entry without its file) would silently
        desynchronise the count the documents quote.
        """
        with MANIFEST_JSON.open(encoding="utf-8") as handle:
            manifest = json.load(handle)
        raw_dir = ROOT / "data" / "raw"
        for name in manifest:
            self.assertTrue(
                (raw_dir / name).is_file(),
                f"fetch_manifest.json lists {name!r} but the file is missing.",
            )
        # The availability table is metadata written into the same directory by
        # FIRMSClient.check_data_availability(); it must never be counted as a
        # detection slice.
        self.assertNotIn(
            "firms_data_availability.csv",
            manifest,
            "the sensor-availability table is not a detection slice.",
        )

    def test_total_firms_record_count_is_published(self) -> None:
        """The cached archive size is quoted consistently everywhere it appears."""
        total, _ = self._manifest_record_count()
        forms = either(total, 0)
        for doc in (
            "docs/01_NASA_SpaceApps_Proposal.md",
            "docs/03_System_Architecture_and_Data_Pipeline.md",
            "docs/05_Pitch_Deck_and_Video_Script.md",
            "exports/PROPOSAL.md",
        ):
            self._assert_present_with_context(
                doc,
                "total FIRMS record count",
                forms,
                r"bản ghi|records|record count|điểm nóng",
            )
        for source in CLAIM_SOURCES:
            self.assertTrue(
                any(form in self.sources[source] for form in forms),
                f"{source}: total FIRMS record count is missing. "
                f"Expected one of {forms!r}.",
            )

    def test_cached_slice_count_is_published(self) -> None:
        """The number of cached FIRMS CSV slices is quoted where stated."""
        _, slices = self._manifest_record_count()
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
            self._assert_present_with_context(
                doc,
                "co-incident pair count N",
                forms,
                r"cặp|pairs|N\s*=",
            )

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

        These are the values published before the archive was re-pulled and
        the calibration was refitted. Leaving them in place silently understates
        the evidence (5,769 pairs instead of 11,553) or overstates it (82.6%
        instead of 79.7%).
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
        for source in CLAIM_SOURCES:
            for label, forms in superseded.items():
                for form in forms:
                    self.assertNotIn(
                        form,
                        self.sources[source],
                        f"{source}: superseded value {label!r} ({form!r}) "
                        f"is still embedded.",
                    )

    def test_only_one_record_count_is_published(self) -> None:
        """Exactly one record count may appear in the published documents.

        The archive holds 1,609,182 detections across 134 cached CSV slices
        (per ``data/raw/fetch_manifest.json``). An earlier convention counted
        every row in every ``data/raw/*.csv``, which additionally swept in the
        sensor-availability table and three header-only slices, yielding
        1,609,194. Publishing both figures would let the proposal and the
        video contradict each other over 12 rows.
        """
        total, slices = self._manifest_record_count()
        inflated = either(total + 12, 0)
        for doc in CLAIM_DOCS:
            self._assert_none_present(doc, "inflated record count", inflated)
        for source in CLAIM_SOURCES:
            for form in inflated:
                self.assertNotIn(
                    form,
                    self.sources[source],
                    f"{source}: inflated record count ({form!r}) is still embedded.",
                )
        inflated_slices = re.compile(rf"(?<!\d){slices + 4}(?!\d)")
        for doc in ("docs/01_NASA_SpaceApps_Proposal.md", "exports/PROPOSAL.md"):
            self.assertIsNone(
                inflated_slices.search(self.docs[doc]),
                f"{doc}: inflated slice count ({slices + 4}) is still published.",
            )

    def test_step_jump_figure_is_published(self) -> None:
        """The artificial multi-sensor step jump is quoted with its exact value.

        The raw index (2005 = 100) for the 2024 epoch is 1,424.2, i.e. a
        +1,324.2% jump over baseline. The Vietnamese convention puts the
        thousands separator on the dot, so the figure renders as ``1.324,2%``;
        a bare ``1.324%`` reads as 1.3% to an English reader and is the exact
        ambiguity ``docs/media/SOURCES.md`` rule 4 exists to prevent.
        """
        mekong = self.results["regime_shift_series"]["mekong"]
        years = mekong["years"]
        raw_index = mekong["raw_index_2005_eq_100"]
        jump_2024 = (raw_index[years.index(2024)] - 100.0) / 100.0 * 100.0
        self.assertAlmostEqual(jump_2024, 1324.2, delta=0.05)
        for doc in (
            "docs/01_NASA_SpaceApps_Proposal.md",
            "exports/PROPOSAL.md",
            "exports/REPORT.md",
        ):
            self._assert_present_with_context(
                doc,
                "2024 multi-sensor step jump",
                (vi(jump_2024, 1), en(jump_2024, 1)),
                r"bước nhảy|step jump|ảo",
            )
            self._assert_none_present(
                doc,
                "ambiguous step jump (bare 1.324%)",
                ("+1.324%", "+1,324%"),
            )

    def test_early_warning_claim_uses_the_display_threshold(self) -> None:
        """The early-warning claim must name the threshold the figure draws.

        The pitch script claimed "SFAI > +3 sigma" for the early-February
        window in 2010 and 2016. The measured peaks there are +2.58 and
        +2.47, and the cyan outline is drawn at +2.2 -- so "+3 sigma" was
        both unsupported by the data and inconsistent with the figure it
        describes.
        """
        for doc in ("docs/05_Pitch_Deck_and_Video_Script.md",):
            with self.subTest(doc=doc):
                self._assert_none_present(
                    doc, "unsupported +3 sigma early-warning claim", ("+3 sigma",)
                )
                self._assert_present_with_context(
                    doc,
                    "early-warning display threshold",
                    ("+2,2", "+2.2"),
                    r"viền xanh|outline|ngưỡng hiển thị|display threshold",
                )

    def test_sfai_thresholds_are_single_sourced_and_documented(self) -> None:
        """The SFAI thresholds are named, single-sourced, and agree with the docs.

        Three different numbers used to answer the same question -- "what
        SFAI marks a crisis?" -- spread across the code, the figure renderer
        and four documents. The operational boundaries now live in
        ``flare_chronos_core``; the calendar's cyan outline uses a separate,
        deliberately lower *display* threshold that the docs name explicitly.
        """
        from benchmark_cli.figure_renderer import SFAI_HIGHLIGHT_Z
        from flare_chronos_core import (
            SFAI_CRISIS_THRESHOLD_Z,
            SFAI_SEVERE_THRESHOLD_Z,
        )

        self.assertEqual(SFAI_SEVERE_THRESHOLD_Z, 1.75)
        self.assertEqual(SFAI_CRISIS_THRESHOLD_Z, 2.5)
        self.assertEqual(SFAI_HIGHLIGHT_Z, 2.2)

        # the calendar highlights severe anomalies *before* the crisis alarm
        self.assertLess(SFAI_SEVERE_THRESHOLD_Z, SFAI_HIGHLIGHT_Z)
        self.assertLess(SFAI_HIGHLIGHT_Z, SFAI_CRISIS_THRESHOLD_Z)

        # The document expectations are derived from the constants, so a
        # threshold change fails the guard instead of silently drifting.
        wireframe = (ROOT / "docs/04_UI_UX_Burning_Calendar_Wireframe.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"+{SFAI_HIGHLIGHT_Z}\\sigma", wireframe)

        proposal = (ROOT / "docs/01_NASA_SpaceApps_Proposal.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"+{SFAI_CRISIS_THRESHOLD_Z}\\sigma", proposal)

    def test_figure_captions_are_derived_not_hardcoded(self) -> None:
        """Figure captions name the anomaly years and peak the data actually shows.

        The Figure 5 panel caption used to hardcode
        ``Severe El Nino Anomalies: 2004, 2007, 2010, 2015-2016 (SFAI +3.1 sigma)``
        and Figure 4 hardcoded ``+380% to +1,324%``. Both were stale: the
        computed matrix puts 2014 in the mekong anomaly set, leaves 2004 out,
        and peaks at +4.9 sigma. The captions are now derived from the matrix,
        so this test rebuilds it and checks the derived caption agrees.
        """
        from benchmark_cli.run_experiments import build_26yr_calendars_and_series

        _, cal = build_26yr_calendars_and_series(
            list(self.results["mekong_empirical_epochs"]),
            list(self.results["amazon_empirical_epochs"]),
        )
        for region in ("mekong", "amazon"):
            caption = cal[region]["summary_caption"]
            with self.subTest(region=region):
                self.assertIn("Severe", caption)
                # every year named must really reach a severe anomaly
                years = cal[region]["years"]
                sfai = cal[region]["sfai_matrix"]
                named = {
                    int(m.group(0)) for m in re.finditer(r"\b(19|20)\d{2}\b", caption)
                }
                self.assertTrue(named)
                for year in named:
                    self.assertIn(year, years)
                    row = sfai[years.index(year)]
                    self.assertGreaterEqual(
                        max(row),
                        2.2,
                        f"{region}: caption names {year} but its peak SFAI is "
                        f"{max(row)} (< 2.2).",
                    )
                # the peak quoted in the caption is the matrix's real peak
                peaks = re.findall(r"SFAI \+([0-9.]+) sigma", caption)
                self.assertEqual(len(peaks), 1, f"{region}: caption peak ambiguous.")
                peak = float(peaks[0])
                self.assertAlmostEqual(
                    peak,
                    round(max(max(row) for row in sfai), 1),
                    delta=0.05,
                    msg=f"{region}: caption peak {peak} != matrix peak.",
                )

    def test_figure_four_step_bias_annotation_is_derived(self) -> None:
        """Figure 4's step-bias range comes from the raw index, not a literal.

        The annotation used to read ``+380% to +1,324%`` on both regional
        panels, but 380% is not a value the data produces for either region.
        """
        from benchmark_cli.run_experiments import build_26yr_calendars_and_series

        series, _ = build_26yr_calendars_and_series(
            list(self.results["mekong_empirical_epochs"]),
            list(self.results["amazon_empirical_epochs"]),
        )
        expected_max = {"mekong": 1324.2, "amazon": 714.3}
        for region in ("mekong", "amazon"):
            rdata = series[region]
            years = rdata["years"]
            raw_index = rdata["raw_index_2005_eq_100"]
            inflations = [raw_index[years.index(y)] - 100.0 for y in (2012, 2020, 2024)]
            with self.subTest(region=region):
                self.assertNotAlmostEqual(
                    min(inflations), 380.0, delta=1.0, msg=f"{region}: +380%?"
                )
                self.assertAlmostEqual(max(inflations), expected_max[region], delta=0.5)

    def test_no_unexplained_multiplier_on_measured_epochs(self) -> None:
        """A measured epoch's harmonized value must equal the artifact's.

        The published Amazon 2024 index (70.7) once carried an unexplained
        ``x1.55`` multiplier applied *after* harmonization, with no commit,
        comment or document recording what it compensated for. It was the only
        reason that year read as a severe anomaly: without it the index is
        45.6 and the year produces no outlined cells at all. Such a factor
        changes a conclusion, so it may not be reintroduced silently.
        """
        for region in ("mekong", "amazon"):
            with self.subTest(region=region):
                base = next(
                    e
                    for e in self.results[f"{region}_empirical_epochs"]
                    if e["year"] == 2005
                )["harmonized_viirs_eq_episodes"]
                series = self.results["regime_shift_series"][region]
                for epoch in self.results[f"{region}_empirical_epochs"]:
                    year = epoch["year"]
                    if year == 2026:
                        # 2026 is NRT-only; the calendar anchors it to the
                        # observed MODIS count rather than the harmonized
                        # episode count, so it is not comparable.
                        continue
                    harm = epoch["harmonized_viirs_eq_episodes"]
                    idx = series["harmonized_index_2005_eq_100"][
                        series["years"].index(year)
                    ]
                    expected = round(100.0 * harm / base, 1)
                    self.assertAlmostEqual(
                        idx,
                        expected,
                        delta=0.15,
                        msg=(
                            f"{region} {year}: published index {idx} != the "
                            f"artifact's own harmonized value ({expected}). "
                            "A measured epoch must not be scaled after "
                            "harmonization."
                        ),
                    )

    def test_measured_and_interpolated_years_are_disclosed(self) -> None:
        """Documents must say which years are measured and which are modelled.

        The 26-year calendar is built from real annual slices for a subset of
        years only; the rest are interpolated from the observed MODIS counts and
        the regional seasonal envelope. A reader cannot tell an observation
        from a model output unless the documents say so.
        """
        expected = {"mekong": (11, 15), "amazon": (9, 17)}
        for region, (n_measured, n_interpolated) in expected.items():
            with self.subTest(region=region):
                series = self.results["regime_shift_series"][region]
                self.assertEqual(len(series["measured_years"]), n_measured)
                self.assertEqual(len(series["interpolated_years"]), n_interpolated)
                self.assertEqual(
                    len(series["measured_years"]) + len(series["interpolated_years"]),
                    len(series["years"]),
                )
                self.assertFalse(
                    set(series["measured_years"]) & set(series["interpolated_years"])
                )

        for doc in ("docs/01_NASA_SpaceApps_Proposal.md", "exports/PROPOSAL.md"):
            text = self.docs[doc]
            with self.subTest(doc=doc):
                self.assertIn("Measured Epoch", text)
                self.assertIn("Interpolated Year", text)

    def test_published_epoch_tables_list_only_measured_years(self) -> None:
        """Every measured epoch's harmonized value is published verbatim.

        The epoch tables are presented as observed NASA FIRMS data, so each
        measured epoch's harmonized count must appear in the documents exactly
        as the artifact records it -- no rescaling, and no year that is really
        an interpolation presented as an observation.
        """
        published = "".join(self.docs.values())
        for region in ("mekong", "amazon"):
            for epoch in self.results[f"{region}_empirical_epochs"]:
                year = epoch["year"]
                harm = epoch["harmonized_viirs_eq_episodes"]
                with self.subTest(region=region, year=year):
                    self.assertIn(
                        vi(harm, 1),
                        published,
                        msg=(
                            f"{region} {year}: harmonized {harm} is not "
                            "published as the artifact records it."
                        ),
                    )


if __name__ == "__main__":
    unittest.main()
