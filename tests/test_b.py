import csv
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import ev_shortlist  # noqa: E402

FX = os.path.join(ROOT, "fixtures")


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class PipelineOnFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = cls.tmp.name
        ev_shortlist.run(
            os.path.join(FX, "clean_trips.csv"),
            os.path.join(FX, "van_profile.csv"),
            os.path.join(ROOT, "params.csv"),
            cls.out,
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_writes_four_files(self):
        for name in ("shortlist.csv", "summary.csv", "all_vans.csv", "data_report.txt"):
            self.assertTrue(os.path.exists(os.path.join(self.out, name)), name)

    def test_shortlist_header_is_eva_format(self):
        with open(os.path.join(self.out, "shortlist.csv"), encoding="utf-8") as f:
            header = f.readline().strip()
        self.assertEqual(
            header,
            "rank,van_id,ev_model,ev_depot,range_check_km,annual_km,"
            "annual_fuel_saving_pln,saving_pln,reason",
        )

    def test_shortlist_ranks_are_consecutive_and_only_feasible(self):
        rows = read(os.path.join(self.out, "shortlist.csv"))
        self.assertEqual([r["rank"] for r in rows], [str(i + 1) for i in range(len(rows))])
        feasible = {r["van_id"] for r in read(os.path.join(FX, "feasibility.csv"))
                    if r["feasible"] == "yes"}
        self.assertEqual({r["van_id"] for r in rows}, feasible)

    def test_range_check_has_one_decimal_and_money_is_integer(self):
        for r in read(os.path.join(self.out, "shortlist.csv")):
            self.assertRegex(r["range_check_km"], r"^\d+\.\d$")
            for k in ("annual_km", "annual_fuel_saving_pln", "saving_pln"):
                self.assertRegex(r[k], r"^-?\d+$")

    def test_summary_figures(self):
        s = {r["figure"]: r["value"] for r in read(os.path.join(self.out, "summary.csv"))}
        self.assertEqual(
            list(s),
            ["vans_assessed", "trips_counted", "total_km", "recommended_count",
             "annual_fuel_saving_pln", "saving_pln", "saving_basis"],
        )
        self.assertEqual(s["vans_assessed"], "38")
        self.assertEqual(s["trips_counted"], "2777")
        self.assertEqual(s["total_km"], "344952")
        self.assertEqual(s["recommended_count"], str(len(read(os.path.join(self.out, "shortlist.csv")))))

    def test_all_vans_has_every_van(self):
        rows = read(os.path.join(self.out, "all_vans.csv"))
        self.assertEqual(len(rows), 38)
        for col in ("van_id", "feasible", "annual_km", "saving_pln"):
            self.assertIn(col, rows[0])


class Ranking(unittest.TestCase):
    def test_sorted_by_saving_then_annual_km_and_cut_by_grant(self):
        feas = [{"van_id": v, "feasible": "yes"} for v in ("A", "B", "C", "D")]
        econ = [
            {"van_id": "A", "saving_pln": 100, "annual_km": 10},
            {"van_id": "B", "saving_pln": 300, "annual_km": 5},
            {"van_id": "C", "saving_pln": 100, "annual_km": 20},
            {"van_id": "D", "saving_pln": 50, "annual_km": 99},
        ]
        ranked = ev_shortlist.rank(feas, econ, limit=3)
        self.assertEqual([r["van_id"] for r in ranked], ["B", "C", "A"])


class Cli(unittest.TestCase):
    def test_cli_runs(self):
        with tempfile.TemporaryDirectory() as out:
            subprocess.run(
                [sys.executable, os.path.join(ROOT, "ev_shortlist.py"),
                 "--trips", os.path.join(FX, "clean_trips.csv"),
                 "--vans", os.path.join(FX, "van_profile.csv"),
                 "--params", os.path.join(ROOT, "params.csv"),
                 "--out", out],
                check=True,
            )
            self.assertTrue(os.path.exists(os.path.join(out, "shortlist.csv")))


if __name__ == "__main__":
    unittest.main()
