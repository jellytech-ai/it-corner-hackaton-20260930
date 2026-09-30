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
            r = dict(got[exp["van_id"]])
            r["reject_reason"] = r["reject_reason"].split("; near threshold")[0]
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
        self.assertEqual(r["P-08"]["ev_model"], "Volta Cargo S")  # z doladowaniem miedzy trasami (B6)
        r = self.assess(midday_connect_minutes="100000")  # doladowanie niemozliwe
        self.assertEqual(r["P-08"]["ev_model"], "Volta Cargo L")

    def test_model_order_follows_price_param(self):
        r = self.assess(**{"ev.Volta Cargo L.price_pln": "100000",
                             "ev.Volta Cargo L.payload_kg": "1100"})
        self.assertEqual(r["P-26"]["ev_model"], "Volta Cargo L")


class MiddayCharging(unittest.TestCase):
    """B6 / A16: doladowanie w bazie miedzy trasami; oczekiwane liczby z HANDOFF sekcja 8."""

    @classmethod
    def setUpClass(cls):
        import feasibility
        cls.f = feasibility
        cls.params = ev_shortlist._stub_load_params(os.path.join(ROOT, "params.csv"))
        cls.trips, cls.profile, _ = ev_shortlist._stub_load_and_clean(
            os.path.join(FX, "clean_trips.csv"), os.path.join(FX, "van_profile.csv"), cls.params)
        cls.models = feasibility.ev_models(cls.params)
        cls.got = {r["van_id"]: r for r in feasibility.assess(cls.profile, cls.trips, cls.params)}

    def failed(self, van_id, model):
        days = self.f.van_days(self.trips, van_id)
        return len(self.f.failed_days(days, self.models["Volta Cargo " + model], self.params))

    def test_failed_days_match_handoff(self):
        expected = {("P-08", "S"): 0, ("P-12", "S"): 0, ("P-09", "S"): 26, ("P-09", "L"): 2,
                    ("P-36", "S"): 11, ("P-36", "L"): 0, ("P-24", "S"): 43, ("P-24", "L"): 9}
        for (van, model), n in expected.items():
            self.assertEqual(self.failed(van, model), n, (van, model))

    def test_p08_goes_to_cargo_s_with_midday_charging(self):
        r = self.got["P-08"]
        self.assertEqual((r["feasible"], r["ev_model"], r["midday_charging"]),
                         ("yes", "Volta Cargo S", "yes"))
        self.assertGreater(r["day_tariff_share"], 0)
        self.assertLess(r["day_tariff_share"], 1)

    def test_p12_fits_cargo_s_but_south_has_no_chargers(self):
        r = self.got["P-12"]
        self.assertEqual((r["ev_model"], r["midday_charging"], r["reject_reason"]),
                         ("Volta Cargo S", "yes", "no chargers at depot"))

    def test_p09_and_p24_rejected_on_range(self):
        for van in ("P-09", "P-24"):
            self.assertEqual(self.got[van]["reject_reason"].split("; near")[0], "range", van)
            self.assertEqual(self.got[van]["ev_model"], "", van)

    def test_range_check_is_longer_route_of_worst_day(self):
        days = self.f.van_days(self.trips, "P-08")
        worst = max(days, key=lambda d: sum(t["km"] for t in d))
        self.assertAlmostEqual(self.got["P-08"]["range_check_km"], max(t["km"] for t in worst))

    def test_single_shift_vans_have_no_midday_charging(self):
        self.assertEqual(self.got["P-26"]["midday_charging"], "no")
        self.assertEqual(self.got["P-26"]["day_tariff_share"], 0)


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


class NearThreshold(unittest.TestCase):
    """B9: do 10% ponad zasieg albo 1-3 dni ponad ladownosc."""

    @classmethod
    def setUpClass(cls):
        import feasibility
        params = ev_shortlist._stub_load_params(os.path.join(ROOT, "params.csv"))
        trips, profile, _ = ev_shortlist._stub_load_and_clean(
            os.path.join(FX, "clean_trips.csv"), os.path.join(FX, "van_profile.csv"), params)
        cls.got = {r["van_id"]: r for r in feasibility.assess(profile, trips, params)}

    def test_range_just_over_is_near(self):
        self.assertIn("near threshold: Volta Cargo S range +1.8%", self.got["P-04"]["reject_reason"])
        self.assertIn("near threshold", self.got["P-13"]["reject_reason"])

    def test_two_shift_failing_few_days_is_near(self):
        self.assertIn("Volta Cargo L range fails 2 days", self.got["P-09"]["reject_reason"])

    def test_far_vans_are_not_near(self):
        for van in ("P-01", "P-24", "P-38"):
            self.assertNotIn("near threshold", self.got[van]["reject_reason"], van)

    def test_refrigerated_not_near(self):
        self.assertNotIn("near threshold", self.got["P-19"]["reject_reason"])

    def test_feasible_reason_marks_threshold(self):
        self.assertIn("at threshold", self.got["P-14"]["reason"])
        self.assertNotIn("at threshold", self.got["P-26"]["reason"])
        self.assertIn("midday charging", self.got["P-08"]["reason"])

    def test_shortlist_reason_comes_from_assess(self):
        with tempfile.TemporaryDirectory() as out:
            ev_shortlist.run(os.path.join(FX, "clean_trips.csv"), os.path.join(FX, "van_profile.csv"),
                             os.path.join(ROOT, "params.csv"), out)
            rows = {r["van_id"]: r for r in read(os.path.join(out, "shortlist.csv"))}
        self.assertIn("at threshold", rows["P-14"]["reason"])


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
