"""Tests for track C (economics). Run: python3 -m unittest tests.test_c"""
import csv
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from economics import economics, lease_exit_fee, saving_basis, saving_for_model  # noqa: E402


def read_csv(name):
    with open(os.path.join(ROOT, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_params():
    return {r["parameter"]: r["value"] for r in read_csv("params_lunch.csv")}


def by_van(rows):
    return {r["van_id"]: r for r in rows}


class EconomicsFixtureTest(unittest.TestCase):
    def setUp(self):
        self.params = read_params()
        self.profile = read_csv("fixtures/van_profile.csv")
        self.feasibility = read_csv("fixtures/feasibility.csv")
        self.rows = by_van(economics(self.profile, self.feasibility, self.params, 90))
        self.rows_profile = by_van(self.profile)

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

    def test_saving_pln_is_five_years_running_minus_ev_after_grant(self):
        # Ewa: five years of running saving, minus EV price after the 30% grant, minus lease exit fee.
        # P-14: lease ends 2027-03-31, within 12 months of 2026-09-30, so no exit fee.
        km = 5623.2 * 365 / 90
        running = self.rows["P-14"]["annual_fuel_saving_pln"] + km * (0.34 - 0.14)
        self.assertAlmostEqual(self.rows["P-14"]["saving_pln"], 5 * running - 150000 * 0.70, places=6)
        self.assertEqual(round(self.rows["P-14"]["saving_pln"]), -35025)

    def test_saving_pln_subtracts_exit_fee_for_long_lease(self):
        # P-26: lease ends 2028-06-30, beyond 12 months: 3 monthly fees of 2890
        km = 8579.7 * 365 / 90
        running = self.rows["P-26"]["annual_fuel_saving_pln"] + km * (0.34 - 0.14)
        self.assertAlmostEqual(self.rows["P-26"]["saving_pln"], 5 * running - 105000 - 3 * 2890, places=6)
        self.assertEqual(round(self.rows["P-26"]["saving_pln"]), -6904)

    def test_saving_pln_uses_the_model_from_feasibility(self):
        # P-08 goes to Volta Cargo L in the fixture: 27 kWh/100 km, 195000 PLN, owned (no fee)
        km = 11670.2 * 365 / 90
        fuel = km * 11.8 / 100 * 5.20 - km * 27 / 100 * 1.10 * 0.58
        expected = 5 * (fuel + km * 0.20) - 195000 * 0.70
        self.assertAlmostEqual(self.rows["P-08"]["saving_pln"], expected, places=6)

    def test_horizon_and_grant_come_from_params(self):
        params = dict(self.params, saving_horizon_years="4", grant_share_of_price="0")
        rows = by_van(economics(self.profile, self.feasibility, params, 90))
        km = 5623.2 * 365 / 90
        running = rows["P-14"]["annual_fuel_saving_pln"] + km * 0.20
        self.assertAlmostEqual(rows["P-14"]["saving_pln"], 4 * running - 150000, places=6)

    def test_saving_for_model_compares_models_for_one_van(self):
        van = self.rows_profile["P-08"]
        s = saving_for_model(van, "Volta Cargo S", 0, self.params, 90)
        l = saving_for_model(van, "Volta Cargo L", 0, self.params, 90)
        self.assertAlmostEqual(l["saving_pln"], self.rows["P-08"]["saving_pln"], places=6)
        self.assertGreater(s["saving_pln"], l["saving_pln"])  # S is cheaper and uses less energy
        self.assertEqual(set(s), {"annual_km", "annual_fuel_saving_pln", "saving_pln"})

    def test_unknown_diesel_model_names_the_missing_parameter(self):
        profile = [dict(r) for r in self.profile]
        for r in profile:
            if r["van_id"] == "P-14":
                r["model"] = "Brona D40"
        with self.assertRaises(ValueError) as ctx:
            economics(profile, self.feasibility, self.params, 90)
        self.assertIn("fuel_l_per_100km.Brona D40", str(ctx.exception))
        self.assertIn("params.csv", str(ctx.exception))


class LeaseExitFeeTest(unittest.TestCase):
    PARAMS = {"lease_exit_fee_months": "3", "lease_free_exit_within_months": "12",
              "lease_reference_date": "2026-09-30"}

    def fee(self, ownership, lease_end, monthly="2000"):
        van = {"ownership": ownership, "lease_end": lease_end, "monthly_lease_pln": monthly}
        return lease_exit_fee(van, self.PARAMS)

    def test_owned_van_has_no_fee(self):
        self.assertEqual(self.fee("owned", "", ""), 0)

    def test_lease_ending_just_before_twelve_months_is_free(self):
        self.assertEqual(self.fee("leased", "2027-09-29"), 0)

    def test_lease_ending_exactly_at_twelve_months_is_free(self):
        self.assertEqual(self.fee("leased", "2027-09-30"), 0)

    def test_lease_ending_just_after_twelve_months_costs_three_fees(self):
        self.assertEqual(self.fee("leased", "2027-10-01"), 6000)

    def test_reference_at_month_end_is_clamped(self):
        params = dict(self.PARAMS, lease_reference_date="2027-02-28", lease_free_exit_within_months="1")
        van = {"ownership": "leased", "lease_end": "2027-03-28", "monthly_lease_pln": "1000"}
        self.assertEqual(lease_exit_fee(van, params), 0)
        van["lease_end"] = "2027-03-29"
        self.assertEqual(lease_exit_fee(van, params), 3000)

    def test_bad_lease_end_names_the_van_field(self):
        van = {"van_id": "P-99", "ownership": "leased", "lease_end": "31.05.2027", "monthly_lease_pln": "1"}
        with self.assertRaises(ValueError) as ctx:
            lease_exit_fee(van, self.PARAMS)
        self.assertIn("P-99", str(ctx.exception))
        self.assertIn("lease_end", str(ctx.exception))

class SavingBasisTest(unittest.TestCase):
    def test_saving_basis_follows_params(self):
        params = dict(read_params(), saving_horizon_years="4", grant_share_of_price="0.25")
        text = saving_basis(params)
        self.assertIn("4 years", text)
        self.assertIn("25% grant", text)

    def test_saving_basis_is_one_english_sentence_naming_what_is_counted(self):
        text = saving_basis(read_params())
        self.assertTrue(text.endswith("."))
        self.assertEqual(text.count(". "), 0)
        for word in ("5 years", "fuel", "maintenance", "30% grant", "lease exit fee", "3 monthly"):
            self.assertIn(word, text)
        self.assertNotIn(",", text)  # stays one field in summary.csv


if __name__ == "__main__":
    unittest.main()
