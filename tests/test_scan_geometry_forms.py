"""The two published forms of the MODIS along-scan size are the same function."""

from __future__ import annotations

import math
import unittest
from pathlib import Path

from flare_chronos_core.geometry_h3 import (
    MODIS_ORBIT_RADIUS_KM,
    MODIS_SAMPLING_RAD,
    R_EARTH_KM,
    modis_dimensions_from_scan_angle,
)

ROOT = Path(__file__).resolve().parents[1]
SCAN_ANGLES_DEG = (0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 55.0)


def along_scan_from_along_track(theta_rad: float) -> float:
    """Delta S = r s (cos t - q) * (Re/r) * (1/q), with q = sqrt((Re/r)^2 - sin^2 t)."""
    ratio = R_EARTH_KM / MODIS_ORBIT_RADIUS_KM
    q = math.sqrt(ratio**2 - math.sin(theta_rad) ** 2)
    return (
        MODIS_ORBIT_RADIUS_KM
        * MODIS_SAMPLING_RAD
        * (math.cos(theta_rad) - q)
        * ratio
        / q
    )


class TestScanGeometryForms(unittest.TestCase):
    def test_both_forms_of_delta_s_agree_across_the_swath(self) -> None:
        for deg in SCAN_ANGLES_DEG:
            with self.subTest(theta_deg=deg):
                theta = math.radians(deg)
                delta_s, _ = modis_dimensions_from_scan_angle(theta)
                self.assertAlmostEqual(along_scan_from_along_track(theta), delta_s, 9)

    def test_the_nadir_pixel_is_one_kilometre_and_the_edge_is_the_published_bow_tie(
        self,
    ) -> None:
        nadir_s, nadir_t = modis_dimensions_from_scan_angle(0.0)
        edge_s, edge_t = modis_dimensions_from_scan_angle(math.radians(55.0))
        self.assertAlmostEqual(nadir_s, 1.0, 3)
        self.assertAlmostEqual(nadir_t, 1.0, 3)
        self.assertAlmostEqual(edge_s, 4.83, 2)
        self.assertAlmostEqual(edge_t, 2.01, 2)

    def test_the_specification_prints_the_along_track_based_form(self) -> None:
        for doc in (
            "docs/02_Cross_Sensor_Harmonization_Spec.md",
            "exports/PROPOSAL.md",
        ):
            with self.subTest(doc=doc):
                text = (ROOT / doc).read_text(encoding="utf-8")
                self.assertIn(r"\frac{R_e}{r} \cdot \frac{1}{\sqrt{", text)


if __name__ == "__main__":
    unittest.main()
