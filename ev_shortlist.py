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
    trips = [{**t, "km": float(t["km"]), "max_load_kg": float(t["max_load_kg"]),
              "stops": int(t["stops"]) if t.get("stops") else ""}
             for t in read_csv(trips_path, "Trips")]
    profile = [{**p, **{k: _num(p[k]) for k in NUMERIC_PROFILE & set(p)}}
               for p in read_csv(profile_path, "Van profile")]
    return trips, profile, ["Fixture mode: clean trips and van profile read as given, no cleaning"]


# --- ranking ----------------------------------------------------------------

def depot_limits(params):
    """Return {depot: number of charging points} from the chargers.<depot> keys (one point per van)."""
    return {k.split(".", 1)[1]: int(float(v)) for k, v in params.items()
            if k.startswith("chargers.")}


def rank_with_notes(feasibility, economics, limit, depot_limits=None, max_moved=None):
    """Return (shortlisted rows, {van_id: why a feasible van is not on the shortlist}).

    Feasible vans go by saving_pln then annual_km, descending. A van is left out when its
    saving is not positive, when its EV depot has no free charging point, when the limit
    of South vans based at North is reached, or when the grant limit is reached.
    """
    econ = {e["van_id"]: e for e in economics}
    rows = [{**f, **econ.get(f["van_id"], {})} for f in feasibility if f["feasible"] == "yes"]
    rows.sort(key=lambda r: (-_money(r.get("saving_pln")), -_money(r.get("annual_km")),
                             r["van_id"]))
    kept, notes, used, moved = [], {}, {}, 0
    for r in rows:
        depot = r.get("ev_depot", "")
        is_moved = depot != r.get("depot", depot)
        if _money(r.get("saving_pln")) <= 0:
            notes[r["van_id"]] = "saving over the horizon is not positive"
        elif len(kept) >= limit:
            notes[r["van_id"]] = "grant limit of %d EVs reached" % limit
        elif depot_limits is not None and used.get(depot, 0) >= depot_limits.get(depot, 0):
            notes[r["van_id"]] = "all %d charging points at %s taken" % (depot_limits.get(depot, 0), depot)
        elif is_moved and max_moved is not None and moved >= max_moved:
            notes[r["van_id"]] = "limit of %d vans based away from their depot reached" % max_moved
        else:
            used[depot] = used.get(depot, 0) + 1
            moved += is_moved
            kept.append(r)
    return kept, notes


def rank(feasibility, economics, limit, depot_limits=None, max_moved=None):
    """Return the shortlisted rows (see rank_with_notes)."""
    return rank_with_notes(feasibility, economics, limit, depot_limits, max_moved)[0]


def _money(value):
    return float(value) if value not in ("", None) else 0.0


def choose_models(profile, trips, feasibility, params, period_days):
    """Return the feasibility rows with ev_model set to the fitting model that saves more (Ewa, 30.09)."""
    by_id = {p["van_id"]: p for p in profile}
    out = []
    for row in feasibility:
        models = [m for m in row.get("fit_models", "").split("; ") if m]
        if len(models) > 1:
            van = by_id[row["van_id"]]
            options = [feas_mod.assess_van(van, trips, params, model=m) for m in models]
            savings = [_money(econ_mod.economics([van], [o], params, period_days)[0]["saving_pln"])
                       for o in options]
            best = max(range(len(options)), key=lambda i: (savings[i], -i))  # tie: cheaper model
            row = options[best]
        out.append(row)
    return out


# --- pipeline ---------------------------------------------------------------

def run(trips_path, vans_path, params_path, out_dir, fixture_mode=False):
    """Run the whole pipeline, write the four output files and return shortlist, summary and report."""
    params = data.load_params(params_path)
    if fixture_mode:
        trips, vans, report = load_fixtures(trips_path, vans_path)
        profile = vans
    else:
        trips, vans, report = data.load_and_clean(trips_path, vans_path, params)
        profile = data.build_van_profile(trips, vans, params)
    if not trips:
        raise ValueError("Trips file %s: no usable trip rows; nothing written. "
                         "Check that it is the telematics export" % trips_path)
    figures = data.control_figures(trips, profile)
    period = data.period_days(trips)
    feas = choose_models(profile, trips, feas_mod.assess(profile, trips, params), params, period)
    econ = econ_mod.economics(profile, feas, params, period)

    limit = int(feas_mod.param(params, "max_evs_grant"))
    max_moved = int(feas_mod.param(params, "max_south_vans_at_north"))
    depot_of = {p["van_id"]: p["depot"] for p in profile}
    ranked, left_out = rank_with_notes([{**f, "depot": depot_of[f["van_id"]]} for f in feas],
                                       econ, limit, depot_limits(params), max_moved)
    on_list = {r["van_id"] for r in ranked}
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
    all_rows = [export_format({**p, **feas_by[p["van_id"]], **econ_by[p["van_id"]],
                               "shortlisted": "yes" if p["van_id"] in on_list else "no",
                               "shortlist_note": left_out.get(p["van_id"], "")})
                for p in profile]

    os.makedirs(out_dir, exist_ok=True)
    write_csv(os.path.join(out_dir, "shortlist.csv"), SHORTLIST_COLS, shortlist)
    write_csv(os.path.join(out_dir, "summary.csv"), ["figure", "value"],
              [{"figure": k, "value": v} for k, v in summary])
    all_cols = list(profile[0]) + [c for c in list(feas[0]) + list(econ[0])
                                   if c != "van_id" and c not in profile[0]]
    all_cols += ["shortlisted", "shortlist_note"]
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
