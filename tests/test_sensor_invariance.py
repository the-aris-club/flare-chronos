"""The same fires, scored with fewer sensors, must give the same harmonized count.

Observation effort Omega follows the sensors actually used. Re-scoring a
multi-sensor epoch with its MODIS stream alone is the direct test of
sensor invariance: same fires, same days, only the instrument set differs.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pytest
from flare_chronos_core import compute_effective_observation_effort

ROOT = Path(__file__).resolve().parents[1]
RESULTS = json.loads(
    (ROOT / "data" / "processed" / "empirical_results.json").read_text()
)
EPOCHS = [
    (region, e)
    for region in ("mekong", "amazon")
    for e in RESULTS[f"{region}_empirical_epochs"]
    if "sensor_invariance_ratio" in e
]

# Allowed gap between the all-sensor and MODIS-only harmonized counts.
INVARIANCE_TOLERANCE = 0.10


class TestEffortFollowsSensors(unittest.TestCase):
    def test_modis_only_effort_is_the_dual_modis_baseline_in_any_year(self) -> None:
        self.assertAlmostEqual(
            compute_effective_observation_effort(2024, 0.0, n_viirs_streams=0), 1.0
        )

    def test_effort_never_exceeds_what_the_year_offers(self) -> None:
        self.assertEqual(
            compute_effective_observation_effort(2012, 0.0, n_viirs_streams=3),
            compute_effective_observation_effort(2012, 0.0),
        )

    def test_unspecified_streams_keep_the_year_effort(self) -> None:
        self.assertEqual(compute_effective_observation_effort(2019, 17.2), 1.795)


class TestSensorInvarianceIsPublished(unittest.TestCase):
    def test_every_multi_sensor_epoch_publishes_its_invariance_ratio(self) -> None:
        for region in ("mekong", "amazon"):
            for e in RESULTS[f"{region}_empirical_epochs"]:
                multi = any("VIIRS" in s for s in e["sources"]) and any(
                    "MODIS" in s for s in e["sources"]
                )
                with self.subTest(region=region, year=e["year"]):
                    self.assertEqual("sensor_invariance_ratio" in e, multi)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known limitation: multi-sensor epochs read 0-30% below the MODIS-only "
        "view of the same fires. Remove this mark when the gap closes."
    ),
)
def test_harmonized_count_is_sensor_invariant() -> None:
    assert EPOCHS
    for region, epoch in EPOCHS:
        gap = abs(epoch["sensor_invariance_ratio"] - 1.0)
        assert gap <= INVARIANCE_TOLERANCE, (region, epoch["year"], gap)


if __name__ == "__main__":
    unittest.main()
