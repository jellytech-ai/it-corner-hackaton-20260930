import csv
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import data  # noqa: E402
import ev_shortlist  # noqa: E402

FX = os.path.join(ROOT, "fixtures")


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# Rules before Ewa's answers (30.09, 12:15); the old expected figures hold under them.
OLD_RULES = {"winter_range_factor": "0.57", "range_check_percentile": "100",
             "chargers.North": "6", "max_south_vans_at_north": "0",
             "midday_charging_allowed": "yes"}


def fixture_data(**overrides):
    """Return (params, trips, profile) from fixtures/, profile rebuilt with the given params."""
    params = {**data.load_params(os.path.join(ROOT, "params.csv")), **overrides}
    trips, register, _ = ev_shortlist.load_fixtures(
        os.path.join(FX, "clean_trips.csv"), os.path.join(FX, "van_profile.csv"))
    return params, trips, data.build_van_profile(trips, register, params)


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
            fixture_mode=True,
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
        all_vans = read(os.path.join(self.out, "all_vans.csv"))
        self.assertEqual({r["van_id"] for r in rows},
                         {r["van_id"] for r in all_vans if r["shortlisted"] == "yes"})
        feasible = {r["van_id"] for r in all_vans if r["feasible"] == "yes"}
        self.assertLessEqual({r["van_id"] for r in rows}, feasible)

    def test_every_feasible_van_off_the_list_has_a_note(self):
        for r in read(os.path.join(self.out, "all_vans.csv")):
            if r["feasible"] == "yes" and r["shortlisted"] == "no":
                self.assertNotEqual(r["shortlist_note"], "", r["van_id"])

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

    def test_all_vans_money_is_integer_or_blank(self):
        for r in read(os.path.join(self.out, "all_vans.csv")):
            for k in ("annual_km", "annual_fuel_saving_pln", "saving_pln"):
                self.assertRegex(r[k], r"^(-?\d+)?$", (r["van_id"], k))

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

    def test_depot_charger_limit_cuts_per_depot(self):
        feas = [{"van_id": v, "feasible": "yes", "ev_depot": d}
                for v, d in (("A", "North"), ("B", "North"), ("C", "North"), ("D", "West"))]
        econ = [{"van_id": v, "saving_pln": s, "annual_km": 0}
                for v, s in (("A", 400), ("B", 300), ("C", 200), ("D", 100))]
        ranked = ev_shortlist.rank(feas, econ, limit=10, depot_limits={"North": 2, "West": 5})
        self.assertEqual([r["van_id"] for r in ranked], ["A", "B", "D"])


class AssessBasicFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import feasibility
        cls.feasibility = feasibility
        cls.params, cls.trips, cls.profile = fixture_data(**OLD_RULES)

    def assess(self, **overrides):
        return {r["van_id"]: r for r in self.feasibility.assess(
            self.profile, self.trips, {**self.params, **overrides})}

    def test_single_shift_vans_match_fixture(self):
        got = self.assess(midday_charging_allowed="no")
        single = {p["van_id"] for p in self.profile if p["two_shift"] == "no"}
        for exp in read(os.path.join(FX, "feasibility.csv")):
            if exp["van_id"] not in single:
                continue
            r = dict(got[exp["van_id"]])
            r["reject_reason"] = r["reject_reason"].split("; near miss")[0]
            self.assertEqual(
                {k: str(r[k]) for k in exp if k != "range_check_km"},
                {k: v for k, v in exp.items() if k != "range_check_km"}, exp["van_id"])
            self.assertAlmostEqual(r["range_check_km"], float(exp["range_check_km"]))

    def test_exactly_on_threshold_passes(self):
        self.assertEqual(self.assess()["P-14"]["feasible"], "yes")  # 148.0 against 148.2

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
        self.assertEqual(r["P-08"]["ev_model"], "Volta Cargo S")  # with midday charging (B6)
        r = self.assess(midday_connect_minutes="100000")  # midday charging impossible
        self.assertEqual(r["P-08"]["ev_model"], "Volta Cargo L")

    def test_model_order_follows_price_param(self):
        r = self.assess(**{"ev.Volta Cargo L.price_pln": "100000",
                             "ev.Volta Cargo L.payload_kg": "1100"})
        self.assertEqual(r["P-26"]["ev_model"], "Volta Cargo L")


class MiddayCharging(unittest.TestCase):
    """B6 / A16: midday charging at the depot; expected figures from HANDOFF section 8."""

    @classmethod
    def setUpClass(cls):
        import feasibility
        cls.f = feasibility
        cls.params, cls.trips, cls.profile = fixture_data(**OLD_RULES)
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
            self.assertEqual(self.got[van]["reject_reason"].split("; near miss")[0], "range", van)
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
        params, trips, profile = fixture_data(**OLD_RULES)
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
    """B9: near miss = up to 10% over range or 1-3 days over payload."""

    @classmethod
    def setUpClass(cls):
        import feasibility
        params, trips, profile = fixture_data(**OLD_RULES)
        cls.got = {r["van_id"]: r for r in feasibility.assess(profile, trips, params)}

    def test_range_just_over_is_near(self):
        self.assertIn("near miss: Volta Cargo S range +1.8%", self.got["P-04"]["reject_reason"])
        self.assertIn("near miss", self.got["P-13"]["reject_reason"])

    def test_two_shift_failing_few_days_is_near(self):
        self.assertIn("Volta Cargo L range fails 2 days", self.got["P-09"]["reject_reason"])

    def test_far_vans_are_not_near(self):
        for van in ("P-01", "P-24", "P-38"):
            self.assertNotIn("near miss", self.got[van]["reject_reason"], van)

    def test_refrigerated_not_near(self):
        self.assertNotIn("near miss", self.got["P-19"]["reject_reason"])

    def test_feasible_reason_marks_threshold(self):
        self.assertIn("at threshold", self.got["P-14"]["reason"])
        self.assertNotIn("at threshold", self.got["P-26"]["reason"])
        self.assertIn("midday charging", self.got["P-08"]["reason"])

    def test_shortlist_reason_comes_from_assess(self):
        with tempfile.TemporaryDirectory() as out:
            ev_shortlist.run(os.path.join(FX, "clean_trips.csv"), os.path.join(FX, "van_profile.csv"),
                             os.path.join(ROOT, "params.csv"), out, fixture_mode=True)
            short = {r["van_id"]: r["reason"] for r in read(os.path.join(out, "shortlist.csv"))}
            full = {r["van_id"]: r["reason"] for r in read(os.path.join(out, "all_vans.csv"))}
        self.assertTrue(short)
        for van_id, reason in short.items():
            self.assertEqual(reason, full[van_id])
            self.assertIn("range margin", reason)


def _van(van_id="X-1", worst=100.0, load=500, depot="North", refrigerated="no"):
    return {"van_id": van_id, "depot": depot, "refrigerated": refrigerated,
            "worst_day_km": worst, "range_day_km": worst, "max_load_kg": load}


def _trip(van_id="X-1", km=100.0, load=500, date="2026-07-01", start="06:00", end="12:00"):
    return {"van_id": van_id, "date": date, "km": km, "max_load_kg": load,
            "start_time": start, "end_time": end}


class Thresholds(unittest.TestCase):
    """KONSTYTUCJA 7: every threshold tested just below, at and just above."""

    @classmethod
    def setUpClass(cls):
        import feasibility
        cls.f = feasibility
        cls.params = data.load_params(os.path.join(ROOT, "params.csv"))
        cls.range_s = feasibility.winter_range_km(
            feasibility.ev_models(cls.params)["Volta Cargo S"], cls.params)
        cls.payload_s = float(cls.params["ev.Volta Cargo S.payload_kg"])

    def one(self, km=100.0, load=500, **van):
        v = _van(worst=km, load=load, **van)
        return self.f.assess([v], [_trip(km=km, load=load)], self.params)[0]

    def test_winter_range_below_at_above(self):
        r = self.range_s
        self.assertEqual(self.one(km=r - 0.1)["ev_model"], "Volta Cargo S")
        self.assertEqual(self.one(km=r)["ev_model"], "Volta Cargo S")
        self.assertIn("at threshold", self.one(km=r)["reason"])
        self.assertNotEqual(self.one(km=r + 0.1)["ev_model"], "Volta Cargo S")

    def test_payload_below_at_above(self):
        p = self.payload_s
        self.assertEqual(self.one(load=p - 1)["feasible"], "yes")
        self.assertEqual(self.one(load=p)["feasible"], "yes")
        self.assertIn("payload", self.one(load=p + 1)["reject_reason"])

    def test_near_miss_range_pct_below_at_above(self):
        pct = float(self.params["near_miss_range_pct"])
        load = 1000  # too heavy for Cargo L, so Cargo S decides on range
        at = self.range_s * (1 + pct / 100)
        note = "Volta Cargo S range +"
        self.assertIn(note, self.one(km=at - 0.1, load=load)["reject_reason"])
        self.assertIn(note, self.one(km=at, load=load)["reject_reason"])
        self.assertNotIn(note, self.one(km=at + 0.1, load=load)["reject_reason"])

    def test_near_miss_payload_days_below_at_above(self):
        n = int(self.params["near_miss_days"])
        p = self.payload_s
        for over, expected in ((n - 1, True), (n, True), (n + 1, False)):
            trips = [_trip(load=p + 1 if i < over else p, date="2026-07-%02d" % (i + 1))
                     for i in range(10)]
            v = _van(worst=100.0, load=p + 1)
            got = self.f.assess([v], trips, self.params)[0]["reject_reason"]
            self.assertEqual("near miss" in got, expected, (over, got))

    def test_at_threshold_pct_below_at_above(self):
        pct = float(self.params["at_threshold_pct"])
        r = self.range_s
        self.assertIn("at threshold", self.one(km=r * (1 - pct / 100) + 0.01)["reason"])
        self.assertNotIn("at threshold", self.one(km=r * (1 - pct / 100) - 0.01)["reason"])

    def test_van_without_trips_is_not_feasible(self):
        v = _van(worst=0.0, load=0)
        r = self.f.assess([v], [], self.params)[0]
        self.assertEqual((r["feasible"], r["ev_model"]), ("no", ""))
        self.assertIn("no trips in this export", r["reject_reason"])

    def test_missing_parameter_message(self):
        for key in ("winter_range_factor", "exclude_refrigerated", "chargers.North",
                    "near_miss_days", "midday_charging_allowed"):
            p = {k: v for k, v in self.params.items() if k != key}
            with self.assertRaises(ValueError) as cm:
                self.f.assess([_van(worst=200.0, load=1000)],
                              [_trip(km=200.0, load=1000)], p)
            self.assertEqual(str(cm.exception), "Missing parameter '%s' in params.csv" % key)


class EwaRules(unittest.TestCase):
    """Ewa's answers (30.09): 95th-percentile day in 60% of WLTP, no midday charging,
    up to 3 South vans based at North, 10 points at North, better model over five years."""

    @classmethod
    def setUpClass(cls):
        import feasibility
        cls.f = feasibility
        cls.params, cls.trips, cls.profile = fixture_data()
        cls.got = {r["van_id"]: r for r in feasibility.assess(cls.profile, cls.trips, cls.params)}
        cls.tmp = tempfile.TemporaryDirectory()
        ev_shortlist.run(os.path.join(FX, "clean_trips.csv"), os.path.join(FX, "van_profile.csv"),
                         os.path.join(ROOT, "params.csv"), cls.tmp.name, fixture_mode=True)
        cls.short = read(os.path.join(cls.tmp.name, "shortlist.csv"))
        cls.all = {r["van_id"]: r for r in read(os.path.join(cls.tmp.name, "all_vans.csv"))}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_fifteen_vans_fit_eight_north_seven_south(self):
        fit = [p for p in self.profile if self.got[p["van_id"]]["ev_model"]]
        self.assertEqual(len(fit), 15)
        self.assertEqual(sum(p["depot"] == "North" for p in fit), 8)

    def test_range_is_checked_on_range_day_km(self):
        by_id = {p["van_id"]: p for p in self.profile}
        for van_id, r in self.got.items():
            if r["midday_charging"] == "no":
                self.assertAlmostEqual(r["range_check_km"], by_id[van_id]["range_day_km"])

    def test_two_shift_vans_count_their_whole_day(self):
        for van_id in ("P-08", "P-12"):
            r = self.got[van_id]
            self.assertEqual((r["midday_charging"], r["day_tariff_share"], r["ev_model"]),
                             ("no", 0, "Volta Cargo L"), van_id)

    def test_south_van_is_based_at_north(self):
        r = self.got["P-05"]
        self.assertEqual((r["feasible"], r["ev_depot"]), ("yes", "North"))
        self.assertIn("South van based at North", r["reason"])

    def test_south_vans_off_when_not_allowed(self):
        r = self.f.assess(self.profile, self.trips,
                          {**self.params, "max_south_vans_at_north": "0"})
        p05 = [x for x in r if x["van_id"] == "P-05"][0]
        self.assertEqual((p05["feasible"], p05["ev_depot"]), ("no", "South"))
        self.assertIn("no chargers at depot", p05["reject_reason"])

    def test_shortlist_respects_limits(self):
        south = [r for r in self.short if self.all[r["van_id"]]["depot"] == "South"]
        self.assertLessEqual(len(south), int(self.params["max_south_vans_at_north"]))
        self.assertLessEqual(len(self.short), int(self.params["max_evs_grant"]))
        north = [r for r in self.short if r["ev_depot"] == "North"]
        self.assertLessEqual(len(north), int(self.params["chargers.North"]))

    def test_left_out_south_van_has_note(self):
        notes = [r["shortlist_note"] for r in self.all.values()
                 if r["depot"] == "South" and r["feasible"] == "yes" and r["shortlisted"] == "no"]
        self.assertTrue(notes)
        self.assertTrue(all(notes), notes)


class ModelChoiceAndRanking(unittest.TestCase):
    def test_better_saving_model_is_chosen(self):
        import economics
        import feasibility
        params = data.load_params(os.path.join(ROOT, "params.csv"))
        van = {**_van(worst=100.0, load=500), "model": "Brona D35", "km_period": 9000.0}
        trips = [_trip(km=100.0, load=500)]
        feas = feasibility.assess([van], trips, params)
        self.assertEqual(feas[0]["fit_models"], "Volta Cargo S; Volta Cargo L")
        chosen = ev_shortlist.choose_models([van], trips, feas, params, 90)[0]
        saving = {m: economics.economics([van], [feasibility.assess_van(van, trips, params, m)],
                                         params, 90)[0]["saving_pln"]
                  for m in ("Volta Cargo S", "Volta Cargo L")}
        self.assertEqual(chosen["ev_model"], max(saving, key=saving.get))

    def feas(self, *rows):
        return [{"van_id": v, "feasible": "yes", "ev_depot": d, "depot": h} for v, d, h in rows]

    def test_not_positive_saving_is_left_out_with_note(self):
        feas = self.feas(("A", "North", "North"), ("B", "North", "North"))
        econ = [{"van_id": "A", "saving_pln": 10, "annual_km": 1},
                {"van_id": "B", "saving_pln": -5, "annual_km": 1}]
        kept, notes = ev_shortlist.rank_with_notes(feas, econ, 10)
        self.assertEqual([r["van_id"] for r in kept], ["A"])
        self.assertIn("not positive", notes["B"])

    def test_moved_vans_limit_below_at_above(self):
        feas = self.feas(*[("S%d" % i, "North", "South") for i in range(5)])
        econ = [{"van_id": "S%d" % i, "saving_pln": 100 - i, "annual_km": 1} for i in range(5)]
        for limit in (2, 3, 4):
            kept, notes = ev_shortlist.rank_with_notes(feas, econ, 10, {"North": 10}, limit)
            self.assertEqual(len(kept), limit)
            self.assertIn("limit of %d vans" % limit, notes["S4"])

    def test_charging_points_full_note(self):
        feas = self.feas(("A", "North", "North"), ("B", "North", "North"))
        econ = [{"van_id": v, "saving_pln": s, "annual_km": 1} for v, s in (("A", 2), ("B", 1))]
        kept, notes = ev_shortlist.rank_with_notes(feas, econ, 10, {"North": 1})
        self.assertEqual(notes["B"], "all 1 charging points at North taken")


class EntryPointMessages(unittest.TestCase):
    """KONSTYTUCJA 3: ERROR on stderr with exit code 1, nothing written; summary adds up."""

    def cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(ROOT, "ev_shortlist.py"), *args],
                              capture_output=True, text=True)

    def test_missing_file_is_one_error_line(self):
        with tempfile.TemporaryDirectory() as out:
            res = self.cli("--trips", "nie_ma.csv", "--vans", "nie_ma.csv", "--out", out)
            self.assertEqual(res.returncode, 1)
            self.assertRegex(res.stderr, r"^ERROR: [A-Za-z ]+ file not found: nie_ma\.csv\n$")
            self.assertEqual(os.listdir(out), [])

    def test_missing_parameter_is_error(self):
        with tempfile.TemporaryDirectory() as out:
            params = os.path.join(out, "params.csv")
            with open(os.path.join(ROOT, "params.csv"), encoding="utf-8") as f:
                lines = [l for l in f if not l.startswith("max_evs_grant,")]
            with open(params, "w", encoding="utf-8") as f:
                f.writelines(lines)
            res = self.cli("--trips", os.path.join(FX, "clean_trips.csv"),
                           "--vans", os.path.join(FX, "van_profile.csv"),
                           "--params", params, "--out", os.path.join(out, "w"), "--fixtures")
            self.assertEqual(res.returncode, 1)
            self.assertEqual(res.stderr, "ERROR: Missing parameter 'max_evs_grant' in params.csv\n")
            self.assertFalse(os.path.exists(os.path.join(out, "w")))

    def test_zero_usable_rows_is_error(self):
        with tempfile.TemporaryDirectory() as out:
            trips = os.path.join(out, "trips.csv")
            with open(os.path.join(FX, "clean_trips.csv"), encoding="utf-8") as f:
                header = f.readline()
            with open(trips, "w", encoding="utf-8") as f:
                f.write(header)
            res = self.cli("--trips", trips, "--vans", os.path.join(FX, "van_profile.csv"),
                           "--out", os.path.join(out, "w"), "--fixtures")
            self.assertEqual(res.returncode, 1)
            self.assertTrue(res.stderr.startswith("ERROR: Trips file %s: no usable trip rows" % trips))
            self.assertFalse(os.path.exists(os.path.join(out, "w")))

    def test_success_prints_report_figures_count_and_folder(self):
        with tempfile.TemporaryDirectory() as out:
            res = self.cli("--trips", os.path.join(FX, "clean_trips.csv"),
                           "--vans", os.path.join(FX, "van_profile.csv"), "--out", out, "--fixtures")
            self.assertEqual(res.returncode, 0, res.stderr)
            rows = read(os.path.join(out, "shortlist.csv"))
            for text in ("Fixture mode", "vans_assessed: 38", "trips_counted: 2777",
                         "total_km: 344952", "Vans on the shortlist: %d" % len(rows),
                         "Output written to: " + out):
                self.assertIn(text, res.stdout)
            s = {r["figure"]: r["value"] for r in read(os.path.join(out, "summary.csv"))}
            for k in ("annual_fuel_saving_pln", "saving_pln"):
                self.assertEqual(int(s[k]), sum(int(r[k]) for r in rows), k)

    def test_help_is_english(self):
        res = self.cli("--help")
        self.assertIn("Rank the vans", res.stdout)


class Cli(unittest.TestCase):
    def test_cli_runs(self):
        with tempfile.TemporaryDirectory() as out:
            subprocess.run(
                [sys.executable, os.path.join(ROOT, "ev_shortlist.py"),
                 "--trips", os.path.join(FX, "clean_trips.csv"),
                 "--vans", os.path.join(FX, "van_profile.csv"),
                 "--params", os.path.join(ROOT, "params.csv"),
                 "--out", out, "--fixtures"],
                check=True,
            )
            self.assertTrue(os.path.exists(os.path.join(out, "shortlist.csv")))


SOURCE = os.environ.get("EV_SOURCE_DIR",
                        os.path.join(os.path.dirname(ROOT), "it-corner-hackathon-20260930"))


@unittest.skipUnless(os.path.exists(os.path.join(SOURCE, "trips.csv")) and
                     os.path.exists(os.path.join(ROOT, "data.py")),
                     "source export not found (EV_SOURCE_DIR)")
class PipelineOnSourceData(unittest.TestCase):
    def test_full_run_control_figures(self):
        with tempfile.TemporaryDirectory() as out:
            ev_shortlist.run(os.path.join(SOURCE, "trips.csv"), os.path.join(SOURCE, "vans.csv"),
                             os.path.join(ROOT, "params.csv"), out)
            s = {r["figure"]: r["value"] for r in read(os.path.join(out, "summary.csv"))}
            short = [r["van_id"] for r in read(os.path.join(out, "shortlist.csv"))]
        self.assertEqual((s["vans_assessed"], s["trips_counted"], s["total_km"]),
                         ("38", "2777", "344952"))
        self.assertTrue(0 < len(short) <= 10)


if __name__ == "__main__":
    unittest.main()
