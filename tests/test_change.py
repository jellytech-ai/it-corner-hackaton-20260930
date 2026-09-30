"""Tests for the afternoon change: combined exports, the renamed column, the worst-day rule, impact.csv.

Run from the repo root: python3 -m unittest tests.test_change -v
Needs the organisers' repo next to this one (or EV_SOURCE_DIR); skipped otherwise.
"""
import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import data  # noqa: E402
import ev_shortlist  # noqa: E402
import impact  # noqa: E402

SOURCE = os.environ.get("EV_SOURCE_DIR", os.path.join(ROOT, "..", "it-corner-hackathon-20260930"))
HAS_SOURCE = os.path.exists(os.path.join(SOURCE, "trips_latest.csv"))
OLD = os.path.join(SOURCE, "trips.csv")
NEW = os.path.join(SOURCE, "trips_latest.csv")


@unittest.skipUnless(HAS_SOURCE, "latest export not found")
class CombinedExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = data.load_params(os.path.join(ROOT, "params.csv"))
        cls.trips, cls.vans, cls.report = data.load_and_clean(
            [OLD, NEW], os.path.join(SOURCE, "vans_latest.csv"), cls.params)
        cls.profile = {p["van_id"]: p for p in data.build_van_profile(cls.trips, cls.vans, cls.params)}

    def test_check_figures(self):
        self.assertEqual(data.control_figures(self.trips, list(self.profile.values())),
                         {"vans_assessed": 40, "trips_counted": 3227, "total_km": 401186})
        self.assertEqual((data.period_days(self.trips), data.operating_days(self.trips)), (104, 89))

    def test_renamed_column_is_read_through_the_alias(self):
        self.assertTrue(any("odo_km -> odometer_km" in line for line in self.report))

    def test_renamed_column_without_alias_is_a_clear_error(self):
        params = {k: v for k, v in self.params.items() if not k.startswith("column_alias.")}
        with self.assertRaisesRegex(ValueError, "missing column.*odometer_km"):
            data.load_and_clean([OLD, NEW], os.path.join(SOURCE, "vans_latest.csv"), params)

    def test_impossible_odometer_reading_uses_gps(self):
        self.assertTrue(any("'1383.0' is above max_plausible_trip_km" in line and "P-13" in line
                            for line in self.report))
        self.assertEqual(self.profile["P-13"]["worst_day_km"], 148.8)

    def test_new_van_is_scaled_from_its_own_delivery_days(self):
        self.assertEqual(self.profile["P-39"]["scale_days"], round(104 * 12 / 89, 2))
        self.assertEqual(self.profile["P-01"]["scale_days"], "")

    def test_final_shortlist_and_impact(self):
        with tempfile.TemporaryDirectory() as out:
            res = ev_shortlist.run([OLD, NEW], os.path.join(SOURCE, "vans_latest.csv"),
                                   os.path.join(ROOT, "params.csv"), out)
        self.assertEqual([r["van_id"] for r in res["shortlist"]],
                         ["P-12", "P-39", "P-40", "P-08", "P-05", "P-13", "P-04"])
        self.assertEqual(res["summary"]["saving_pln"], 85750)
        rows = impact.impact(OLD, os.path.join(SOURCE, "vans.csv"),
                             data.load_params(os.path.join(ROOT, "params_lunch.csv")),
                             [OLD, NEW], os.path.join(SOURCE, "vans_latest.csv"), self.params)
        self.assertEqual([(r["van_id"], r["change"], r["cause"]) for r in rows],
                         [("P-21", "left", "new rule"), ("P-25", "left", "new data"),
                          ("P-30", "left", "new rule"), ("P-39", "entered", "new data"),
                          ("P-40", "entered", "new data")])


if __name__ == "__main__":
    unittest.main()
