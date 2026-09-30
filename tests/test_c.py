"""Tests for track C (economics). Run: python3 -m unittest tests.test_c"""
import csv
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from economics import economics, saving_basis  # noqa: E402


def read_csv(name):
    with open(os.path.join(ROOT, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_params():
    return {r["parameter"]: r["value"] for r in read_csv("params.csv")}


def by_van(rows):
    return {r["van_id"]: r for r in rows}


class EconomicsFixtureTest(unittest.TestCase):
    def setUp(self):
        self.params = read_params()
        self.profile = read_csv("fixtures/van_profile.csv")
        self.feasibility = read_csv("fixtures/feasibility.csv")
        self.rows = by_van(economics(self.profile, self.feasibility, self.params, 90))

    def test_annual_km_scales_period_to_year(self):
        # P-26: 8579.7 km in 90 days -> x 365 / 90
        self.assertAlmostEqual(self.rows["P-26"]["annual_km"], 8579.7 * 365 / 90, places=6)
        self.assertEqual(round(self.rows["P-26"]["annual_km"]), 34795)

    def test_annual_km_uses_period_days_argument(self):
        rows = by_van(economics(self.profile, self.feasibility, self.params, 45))
        self.assertAlmostEqual(rows["P-26"]["annual_km"], 8579.7 * 365 / 45, places=6)

    def test_fuel_saving_p14_matches_hand_calculation(self):
        # Brona D35 Long -> Volta Cargo S, night tariff only
        km = 5623.2 * 365 / 90
        diesel = km * 10.9 / 100 * 5.20
        charging = km * 24 / 100 * 1.10 * 0.58
        self.assertAlmostEqual(self.rows["P-14"]["annual_fuel_saving_pln"], diesel - charging, places=6)
        self.assertEqual(round(self.rows["P-14"]["annual_fuel_saving_pln"]), 9434)

    def test_day_tariff_share_blends_electricity_price(self):
        feas = [dict(r) for r in self.feasibility]
        for r in feas:
            if r["van_id"] == "P-14":
                r["day_tariff_share"] = "0.5"
        rows = by_van(economics(self.profile, feas, self.params, 90))
        km = 5623.2 * 365 / 90
        price = 0.5 * 0.58 + 0.5 * 0.92
        expected = km * 10.9 / 100 * 5.20 - km * 24 / 100 * 1.10 * price
        self.assertAlmostEqual(rows["P-14"]["annual_fuel_saving_pln"], expected, places=6)

    def test_one_row_per_van_with_blanks_when_no_ev_model(self):
        self.assertEqual(len(self.rows), 38)
        p01 = self.rows["P-01"]
        self.assertEqual(p01["annual_fuel_saving_pln"], "")
        self.assertEqual(p01["saving_pln"], "")

    def test_infeasible_van_with_ev_model_is_still_priced(self):
        self.assertNotEqual(self.rows["P-05"]["annual_fuel_saving_pln"], "")

    def test_params_drive_the_result(self):
        params = dict(self.params, diesel_price_pln_per_l="6.20")
        rows = by_van(economics(self.profile, self.feasibility, params, 90))
        km = 5623.2 * 365 / 90
        self.assertAlmostEqual(
            rows["P-14"]["annual_fuel_saving_pln"] - self.rows["P-14"]["annual_fuel_saving_pln"],
            km * 10.9 / 100 * 1.00,
            places=6,
        )

    def test_saving_pln_is_annual_fuel_plus_maintenance_saving(self):
        # Decision C1 / D7: variant 1, operating costs only, per year
        km = 5623.2 * 365 / 90
        maintenance = km * (0.34 - 0.14)
        row = self.rows["P-14"]
        self.assertAlmostEqual(row["saving_pln"], row["annual_fuel_saving_pln"] + maintenance, places=6)
        self.assertEqual(round(row["saving_pln"]), 13995)


class SavingBasisTest(unittest.TestCase):
    def test_saving_basis_is_one_english_sentence_naming_what_is_counted(self):
        text = saving_basis(read_params())
        self.assertTrue(text.endswith("."))
        self.assertEqual(text.count(". "), 0)
        for word in ("fuel", "maintenance", "per year", "lease"):
            self.assertIn(word, text)
        self.assertNotIn(",", text)  # stays one field in summary.csv


if __name__ == "__main__":
    unittest.main()
