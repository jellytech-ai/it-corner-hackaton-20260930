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


class AssessBasicFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import feasibility
        cls.feasibility = feasibility
        cls.params = ev_shortlist._stub_load_params(os.path.join(ROOT, "params.csv"))
        cls.trips, cls.profile, _ = ev_shortlist._stub_load_and_clean(
            os.path.join(FX, "clean_trips.csv"), os.path.join(FX, "van_profile.csv"), cls.params)

    def assess(self, **overrides):
        return {r["van_id"]: r for r in self.feasibility.assess(
            self.profile, self.trips, {**self.params, **overrides})}

    def test_single_shift_vans_match_fixture(self):
        got = self.assess()
        single = {p["van_id"] for p in self.profile if p["two_shift"] == "no"}
        for exp in read(os.path.join(FX, "feasibility.csv")):
            if exp["van_id"] not in single:
                continue
            r = got[exp["van_id"]]
            self.assertEqual(
                {k: str(r[k]) for k in exp if k != "range_check_km"},
                {k: v for k, v in exp.items() if k != "range_check_km"}, exp["van_id"])
            self.assertAlmostEqual(r["range_check_km"], float(exp["range_check_km"]))

    def test_exactly_on_threshold_passes(self):
        self.assertEqual(self.assess()["P-14"]["feasible"], "yes")  # 148.0 przy 148.2

    def test_winter_factor_comes_from_params(self):
        r = self.assess(winter_range_factor="0.65")  # Cargo S: 169 km
        self.assertEqual(r["P-04"]["feasible"], "yes")
        self.assertEqual(r["P-04"]["ev_model"], "Volta Cargo S")

    def test_refrigerated_rule_from_params(self):
        self.assertIn("refrigerated", self.assess()["P-19"]["reject_reason"])
        self.assertNotIn("refrigerated",
                         self.assess(exclude_refrigerated="no")["P-19"]["reject_reason"])

    def test_depot_chargers_from_params(self):
        r = self.assess(**{"chargers.South": "3"})
        self.assertEqual(r["P-05"]["feasible"], "yes")
        self.assertEqual(r["P-05"]["reject_reason"], "")

    def test_cheapest_model_that_fits(self):
        r = self.assess()
        self.assertEqual(r["P-26"]["ev_model"], "Volta Cargo S")
        self.assertEqual(r["P-14"]["ev_model"], "Volta Cargo S")
        self.assertEqual(r["P-08"]["ev_model"], "Volta Cargo L")  # bez doladowania S nie starcza

    def test_model_order_follows_price_param(self):
        r = self.assess(**{"ev.Volta Cargo L.price_pln": "100000",
                             "ev.Volta Cargo L.payload_kg": "1100"})
        self.assertEqual(r["P-26"]["ev_model"], "Volta Cargo L")


class Sensitivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import feasibility
        params = ev_shortlist._stub_load_params(os.path.join(ROOT, "params.csv"))
        trips, profile, _ = ev_shortlist._stub_load_and_clean(
            os.path.join(FX, "clean_trips.csv"), os.path.join(FX, "van_profile.csv"), params)
        cls.rows = {r["winter_range_factor"]: r
                    for r in feasibility.sensitivity(profile, trips, params, [0.50, 0.57, 0.65])}

    def test_one_row_per_factor(self):
        self.assertEqual(sorted(self.rows), [0.50, 0.57, 0.65])

    def test_baseline_matches_assess(self):
        r = self.rows[0.57]
        self.assertEqual(r["feasible_vans"], "P-08 P-14 P-26")
        self.assertEqual(r["feasible_count"], 3)

    def test_more_vans_pass_with_higher_factor(self):
        counts = [self.rows[f]["feasible_count"] for f in (0.50, 0.57, 0.65)]
        self.assertEqual(counts, sorted(counts))
        self.assertGreater(counts[2], counts[1])

    def test_fit_ignoring_chargers_includes_south(self):
        self.assertIn("P-25", self.rows[0.57]["fit_vans"].split())


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
