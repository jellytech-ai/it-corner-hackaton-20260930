#!/usr/bin/env python3
"""Entry point: clean data (data.py) -> feasibility -> economics -> output files.

Usage:
    python3 ev_shortlist.py --trips trips.csv --vans vans.csv --params params.csv --out wyniki/

With --fixtures, --trips and --vans are clean_trips.csv and van_profile.csv
(format of fixtures/), and the cleaning step is skipped.
"""
import argparse
import csv
import math
import os
import sys

import data
import economics as econ_mod
import feasibility as feas_mod

HERE = os.path.dirname(os.path.abspath(__file__))

SHORTLIST_COLS = ["rank", "van_id", "ev_model", "ev_depot", "range_check_km",
                  "annual_km", "annual_fuel_saving_pln", "saving_pln", "reason"]
SUMMARY_FIGURES = ["vans_assessed", "trips_counted", "total_km", "recommended_count",
                   "annual_fuel_saving_pln", "saving_pln", "saving_basis"]
NUMERIC_PROFILE = {"km_period", "worst_day_km", "max_load_kg", "days", "trips",
                   "payload_kg", "two_shift_days", "monthly_lease_pln", "year"}
INT_COLS = {"annual_km", "annual_fuel_saving_pln", "saving_pln"}


def export_format(row):
    """Return a copy of the row with range_check_km to 1 decimal and km and money as integers."""
    out = dict(row)
    for k in INT_COLS & set(out):
        if out[k] != "":
            out[k] = round(float(out[k]))
    if out.get("range_check_km", "") != "":
        out["range_check_km"] = "%.1f" % float(out["range_check_km"])
    return out


def read_csv(path, label):
    """Return the rows of a CSV file as a list of dicts."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        raise FileNotFoundError("%s file not found: %s" % (label, path)) from None


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _num(v):
    return float(v) if v not in ("", None) else ""


def load_fixtures(trips_path, profile_path):
    """Return (clean_trips, van_profile, report) read from files already in the contract format."""
    trips = [{**t, "km": float(t["km"])} for t in read_csv(trips_path, "Trips")]
    profile = [{**p, **{k: _num(p[k]) for k in NUMERIC_PROFILE & set(p)}}
               for p in read_csv(profile_path, "Van profile")]
    return trips, profile, ["Fixture mode: clean trips and van profile read as given, no cleaning"]


# --- ranking ----------------------------------------------------------------

def depot_limits(params):
    """Return {depot: number of charging points} from the chargers.<depot> keys (one point per van)."""
    return {k.split(".", 1)[1]: int(float(v)) for k, v in params.items()
            if k.startswith("chargers.")}


def rank(feasibility, economics, limit, depot_limits=None):
    """Return feasible vans by saving_pln then annual_km, descending, cut by grant and depot limits."""
    econ = {e["van_id"]: e for e in economics}
    rows = [{**f, **econ.get(f["van_id"], {})} for f in feasibility if f["feasible"] == "yes"]
    rows.sort(key=lambda r: (-r.get("saving_pln", 0), -r.get("annual_km", 0), r["van_id"]))
    if depot_limits is not None:
        used = {}
        kept = []
        for r in rows:
            depot = r["ev_depot"]
            if used.get(depot, 0) < depot_limits.get(depot, 0):
                used[depot] = used.get(depot, 0) + 1
                kept.append(r)
        rows = kept
    return rows[:limit]


# --- pipeline ---------------------------------------------------------------

def run(trips_path, vans_path, params_path, out_dir, fixture_mode=False):
    """Run the whole pipeline, write the four output files and return shortlist, summary and report."""
    params = data.load_params(params_path)
    if fixture_mode:
        trips, vans, report = load_fixtures(trips_path, vans_path)
        profile = vans
    else:
        trips, vans, report = data.load_and_clean(trips_path, vans_path, params)
        profile = data.build_van_profile(trips, vans)
    if not trips:
        raise ValueError("Trips file %s: no usable trip rows; nothing written. "
                         "Check that it is the telematics export" % trips_path)
    figures = data.control_figures(trips, profile)
    feas = feas_mod.assess(profile, trips, params)
    econ = econ_mod.economics(profile, feas, params, data.period_days(trips))

    limit = int(feas_mod.param(params, "max_evs_grant"))
    ranked = rank(feas, econ, limit, depot_limits(params))
    shortlist = [export_format({**r, "rank": i + 1, "reason": r.get("reason", "")})
                 for i, r in enumerate(ranked)]

    summary = [
        ("vans_assessed", figures["vans_assessed"]),
        ("trips_counted", figures["trips_counted"]),
        ("total_km", figures["total_km"]),
        ("recommended_count", len(shortlist)),
        # sums of the rounded shortlist rows, so the CFO gets the same total by adding the column
        ("annual_fuel_saving_pln", round(math.fsum(r["annual_fuel_saving_pln"] for r in shortlist))),
        ("saving_pln", round(math.fsum(r["saving_pln"] for r in shortlist))),
        ("saving_basis", econ_mod.saving_basis(params)),
    ]

    feas_by = {f["van_id"]: f for f in feas}
    econ_by = {e["van_id"]: e for e in econ}
    all_rows = [export_format({**p, **feas_by[p["van_id"]], **econ_by[p["van_id"]]})
                for p in profile]

    os.makedirs(out_dir, exist_ok=True)
    write_csv(os.path.join(out_dir, "shortlist.csv"), SHORTLIST_COLS, shortlist)
    write_csv(os.path.join(out_dir, "summary.csv"), ["figure", "value"],
              [{"figure": k, "value": v} for k, v in summary])
    all_cols = list(profile[0]) + [c for c in list(feas[0]) + list(econ[0])
                                   if c != "van_id" and c not in profile[0]]
    write_csv(os.path.join(out_dir, "all_vans.csv"), all_cols, all_rows)
    with open(os.path.join(out_dir, "data_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    return {"shortlist": shortlist, "summary": dict(summary), "report": report}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Rank the vans that can be replaced by an EV and write the shortlist files.")
    ap.add_argument("--trips", required=True, help="telematics export (trips.csv)")
    ap.add_argument("--vans", required=True, help="van register (vans.csv)")
    ap.add_argument("--params", default=os.path.join(HERE, "params.csv"),
                    help="parameter file (default: params.csv next to this script)")
    ap.add_argument("--out", default="wyniki", help="output folder (default: wyniki)")
    ap.add_argument("--fixtures", action="store_true",
                    help="--trips and --vans are clean_trips.csv and van_profile.csv from fixtures/")
    a = ap.parse_args(argv)
    try:
        res = run(a.trips, a.vans, a.params, a.out, fixture_mode=a.fixtures)
    except (FileNotFoundError, ValueError) as err:
        print("ERROR: %s" % err, file=sys.stderr)
        return 1
    s = res["summary"]
    print("\n".join(res["report"]))
    print("\nCheck figures")
    for name in ("vans_assessed", "trips_counted", "total_km"):
        print("  %s: %s" % (name, s[name]))
    print("\nVans on the shortlist: %d" % len(res["shortlist"]))
    print("Output written to: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
