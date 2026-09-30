#!/usr/bin/env python3
"""Punkt wejscia: A (dane) -> B (wykonalnosc) -> C (ekonomia) -> pliki wynikowe.

Uzycie:
    python3 ev_shortlist.py --trips T --vans V --params params.csv --out wyniki/

Dopoki brakuje modulow innych torow (data.py, economics.py) lub feasibility.py,
uzywane sa zaslepki pracujace na plikach testowych z fixtures/ w formacie
kontraktu: --trips = clean_trips.csv, --vans = van_profile.csv.
"""
import argparse
import csv
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))

SHORTLIST_COLS = ["rank", "van_id", "ev_model", "ev_depot", "range_check_km",
                  "annual_km", "annual_fuel_saving_pln", "saving_pln", "reason"]
SUMMARY_FIGURES = ["vans_assessed", "trips_counted", "total_km", "recommended_count",
                   "annual_fuel_saving_pln", "saving_pln", "saving_basis"]
NUMERIC_PROFILE = {"km_period", "worst_day_km", "max_load_kg", "days", "trips",
                   "payload_kg", "two_shift_days", "monthly_lease_pln", "year"}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _num(v):
    return float(v) if v not in ("", None) else ""


# --- zaslepki (do czasu scalenia torow) ------------------------------------

def _stub_load_params(path):
    return {r["parameter"]: r["value"] for r in read_csv(path)}


def _stub_load_and_clean(trips_path, vans_path, params):
    trips = read_csv(trips_path)
    for t in trips:
        t["km"] = float(t["km"])
    profile = read_csv(vans_path)
    for p in profile:
        for k in NUMERIC_PROFILE & set(p):
            p[k] = _num(p[k])
    return trips, profile, ["Tryb testowy: dane z fixtures/, bez czyszczenia (brak data.py)."]


def _stub_build_van_profile(trips, vans):
    return vans  # w trybie testowym --vans jest juz van_profile


def _stub_control_figures(trips, profile):
    return {"vans_assessed": len(profile), "trips_counted": len(trips),
            "total_km": round(sum(t["km"] for t in trips))}


def _stub_period_days(trips):
    ds = sorted(date.fromisoformat(t["date"]) for t in trips)
    return (ds[-1] - ds[0]).days + 1


def _stub_assess(profile, trips, params):
    by_id = {r["van_id"]: r for r in read_csv(os.path.join(HERE, "fixtures", "feasibility.csv"))}
    for r in by_id.values():
        r["range_check_km"] = float(r["range_check_km"])
    return [by_id[p["van_id"]] for p in profile]


def _stub_economics(profile, feasibility, params, period_days):
    days_per_year = float(params.get("days_per_year", 365))
    return [{"van_id": p["van_id"],
             "annual_km": round(p["km_period"] / period_days * days_per_year),
             "annual_fuel_saving_pln": 0, "saving_pln": 0}
            for p in profile]


def _stub_saving_basis(params):
    return "zaslepka: ekonomia toru C jeszcze nie podlaczona"


def _pick(module, name, stub):
    try:
        return getattr(__import__(module), name)
    except (ImportError, AttributeError):
        return stub


# --- ranking ----------------------------------------------------------------

def rank(feasibility, economics, limit):
    """Wykonalne vany malejaco po saving_pln, remis malejaco po annual_km, ucinane do limitu."""
    econ = {e["van_id"]: e for e in economics}
    rows = [{**f, **econ.get(f["van_id"], {})} for f in feasibility if f["feasible"] == "yes"]
    rows.sort(key=lambda r: (-r.get("saving_pln", 0), -r.get("annual_km", 0), r["van_id"]))
    return rows[:limit]


# --- potok ------------------------------------------------------------------

def run(trips_path, vans_path, params_path, out_dir):
    load_params = _pick("data", "load_params", _stub_load_params)
    load_and_clean = _pick("data", "load_and_clean", _stub_load_and_clean)
    build_van_profile = _pick("data", "build_van_profile", _stub_build_van_profile)
    control_figures = _pick("data", "control_figures", _stub_control_figures)
    period_days = _pick("data", "period_days", _stub_period_days)
    assess = _pick("feasibility", "assess", _stub_assess)
    economics = _pick("economics", "economics", _stub_economics)
    saving_basis = _pick("economics", "saving_basis", _stub_saving_basis)

    params = load_params(params_path)
    trips, vans, report = load_and_clean(trips_path, vans_path, params)
    profile = build_van_profile(trips, vans)
    figures = control_figures(trips, profile)
    feas = assess(profile, trips, params)
    econ = economics(profile, feas, params, period_days(trips))

    ranked = rank(feas, econ, int(params.get("max_evs_grant", 10)))
    shortlist = [{**r, "rank": i + 1, "reason": r.get("reason", r.get("reject_reason", "")),
                 "range_check_km": "%.1f" % r["range_check_km"]}
                 for i, r in enumerate(ranked)]

    summary = [
        ("vans_assessed", figures["vans_assessed"]),
        ("trips_counted", figures["trips_counted"]),
        ("total_km", figures["total_km"]),
        ("recommended_count", len(ranked)),
        ("annual_fuel_saving_pln", round(sum(r["annual_fuel_saving_pln"] for r in ranked))),
        ("saving_pln", round(sum(r["saving_pln"] for r in ranked))),
        ("saving_basis", saving_basis(params)),
    ]

    feas_by = {f["van_id"]: f for f in feas}
    econ_by = {e["van_id"]: e for e in econ}
    all_rows = [{**p, **feas_by[p["van_id"]], **econ_by[p["van_id"]]} for p in profile]

    os.makedirs(out_dir, exist_ok=True)
    write_csv(os.path.join(out_dir, "shortlist.csv"), SHORTLIST_COLS, shortlist)
    write_csv(os.path.join(out_dir, "summary.csv"), ["figure", "value"],
              [{"figure": k, "value": v} for k, v in summary])
    all_cols = list(profile[0]) + [c for c in list(feas[0]) + list(econ[0])
                                   if c != "van_id" and c not in profile[0]]
    write_csv(os.path.join(out_dir, "all_vans.csv"), all_cols, all_rows)
    with open(os.path.join(out_dir, "data_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    return {"shortlist": shortlist, "summary": dict(summary)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Ktore vany przechodza na elektryczne")
    ap.add_argument("--trips", required=True)
    ap.add_argument("--vans", required=True)
    ap.add_argument("--params", default=os.path.join(HERE, "params.csv"))
    ap.add_argument("--out", default="wyniki")
    a = ap.parse_args(argv)
    res = run(a.trips, a.vans, a.params, a.out)
    print("Zapisano do %s: %d vanow na shortliscie" % (a.out, len(res["shortlist"])))


if __name__ == "__main__":
    main()
