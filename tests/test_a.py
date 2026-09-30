"""Track A tests. Run from the repo root: python3 -m unittest tests.test_a -v

The checks against the real export need the organisers' repo next to this one
(or HACKATHON_DATA pointing at it); they are skipped when it is missing.
"""
import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import data  # noqa: E402

SOURCE = os.environ.get("HACKATHON_DATA", os.path.join(ROOT, "..", "it-corner-hackathon-20260930"))
HAS_SOURCE = os.path.exists(os.path.join(SOURCE, "trips.csv"))

TRIP_HEADER = "date,van_id,driver,route_id,odometer_km,gps_km,start_time,end_time,stops,max_load_kg"
VAN_HEADER = "van_id,model,year,depot,ownership,lease_end,monthly_lease_pln,refrigerated,payload_kg"
VANS = [VAN_HEADER, "V-1,Brona D35,2020,North,owned,,,no,1150", "V-2,Brona D35,2021,South,leased,2027-01-31,2500,no,1150"]


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class SyntheticExport(unittest.TestCase):
    def run_clean(self, trip_lines, params=None, van_lines=VANS):
        with tempfile.TemporaryDirectory() as tmp:
            trips_path, vans_path = os.path.join(tmp, "t.csv"), os.path.join(tmp, "v.csv")
            with open(trips_path, "w", encoding="utf-8") as f:
                f.write("\n".join([TRIP_HEADER] + trip_lines) + "\n")
            with open(vans_path, "w", encoding="utf-8") as f:
                f.write("\n".join(van_lines) + "\n")
            return data.load_and_clean(trips_path, vans_path, params or {})

    def test_exact_duplicates_removed(self):
        line = "2026-10-01,V-1,A,R1,100.0,99.0,05:00,11:00,20,800"
        trips, _, report = self.run_clean([line, line, line])
        self.assertEqual(len(trips), 1)
        self.assertIn("Exact duplicate rows removed: 2", report)

    def test_alias_applied(self):
        trips, _, report = self.run_clean(["2026-10-01,OLD,A,R1,100.0,99.0,05:00,11:00,20,800"],
                                          params={"van_alias.OLD": "V-1"})
        self.assertEqual(trips[0]["van_id"], "V-1")
        self.assertTrue(any("OLD -> V-1 on 1 rows" in line for line in report))

    def test_unknown_van_excluded_with_warning(self):
        trips, _, report = self.run_clean(["2026-10-01,V-9,A,R1,100.0,99.0,05:00,11:00,20,800",
                                           "2026-10-01,V-1,A,R1,50.0,49.0,05:00,11:00,20,800"])
        self.assertEqual([t["van_id"] for t in trips], ["V-1"])
        self.assertTrue(any(line.startswith("WARNING") and "V-9" in line for line in report))

    def test_bad_odometer_falls_back_to_gps(self):
        trips, _, report = self.run_clean(["2026-10-01,V-1,A,R1,-208.6,90.3,05:00,11:00,20,800"])
        self.assertEqual((trips[0]["km"], trips[0]["km_source"]), (90.3, "gps"))
        self.assertTrue(any(line.startswith("WARNING") and "gps_km 90.3 used" in line for line in report))

    def test_missing_gps_keeps_odometer(self):
        trips, _, _ = self.run_clean(["2026-10-01,V-1,A,R1,120.5,,05:00,11:00,20,800"])
        self.assertEqual((trips[0]["km"], trips[0]["km_source"]), (120.5, "odometer"))

    def test_no_usable_distance_rejected(self):
        trips, _, report = self.run_clean(["2026-10-01,V-1,A,R1,-5,,05:00,11:00,20,800"])
        self.assertEqual(trips, [])
        self.assertTrue(any("no usable distance" in line for line in report))

    def test_missing_column_is_a_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            trips_path, vans_path = os.path.join(tmp, "t.csv"), os.path.join(tmp, "v.csv")
            with open(trips_path, "w", encoding="utf-8") as f:
                f.write("date,van_id\n2026-10-01,V-1\n")
            with open(vans_path, "w", encoding="utf-8") as f:
                f.write("\n".join(VANS) + "\n")
            with self.assertRaisesRegex(ValueError, "missing column"):
                data.load_and_clean(trips_path, vans_path, {})

    def test_profile_sums_the_day_and_flags_two_shifts(self):
        trips, vans, report = self.run_clean([
            "2026-10-01,V-1,A,R1,100.0,99.0,05:00,11:00,20,800",
            "2026-10-01,V-1,B,R2,80.0,79.0,13:00,18:00,15,900",
            "2026-10-02,V-1,A,R1,120.0,119.0,05:00,11:00,20,700",
        ])
        profile = {p["van_id"]: p for p in data.build_van_profile(trips, vans)}
        v1 = profile["V-1"]
        self.assertEqual((v1["days"], v1["trips"], v1["km_period"], v1["worst_day_km"]), (2, 3, 300.0, 180.0))
        self.assertEqual((v1["max_load_kg"], v1["two_shift"], v1["two_shift_days"]), (900, "yes", 1))
        self.assertEqual(profile["V-2"]["trips"], 0)
        self.assertTrue(any("V-2 is in the register but has no trips" in line for line in report))
        figures = data.control_figures(trips, list(profile.values()))
        self.assertEqual(figures, {"vans_assessed": 1, "trips_counted": 3, "total_km": 300})
        self.assertEqual(data.period_days(trips), 2)

    def test_missing_params_file(self):
        with self.assertRaises(FileNotFoundError):
            data.load_params("/nonexistent/params.csv")


@unittest.skipUnless(HAS_SOURCE, "source export not found")
class RealExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = data.load_params(os.path.join(ROOT, "params.csv"))
        cls.trips, cls.vans, cls.report = data.load_and_clean(
            os.path.join(SOURCE, "trips.csv"), os.path.join(SOURCE, "vans.csv"), cls.params)
        cls.profile = data.build_van_profile(cls.trips, cls.vans)

    def test_check_figures(self):
        self.assertEqual(data.control_figures(self.trips, self.profile),
                         {"vans_assessed": 38, "trips_counted": 2777, "total_km": 344952})
        self.assertEqual(data.period_days(self.trips), 90)

    def test_report_mentions_the_known_problems(self):
        text = "\n".join(self.report)
        self.assertIn("Exact duplicate rows removed: 222", text)
        self.assertIn("P-17 -> P-17B", text)
        self.assertIn("gps_km 90.3 used: 2026-08-13 P-27", text)

    def test_matches_fixtures(self):
        for name, rows, columns in (("clean_trips.csv", self.trips, data.CLEAN_TRIP_COLUMNS),
                                    ("van_profile.csv", self.profile, data.PROFILE_COLUMNS)):
            with tempfile.TemporaryDirectory() as tmp:
                out = os.path.join(tmp, name)
                data.write_csv(out, rows, columns)
                self.assertEqual(read_rows(out), read_rows(os.path.join(ROOT, "fixtures", name)), name)


if __name__ == "__main__":
    unittest.main()
