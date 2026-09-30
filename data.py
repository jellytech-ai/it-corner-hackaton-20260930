"""Track A: load, clean and profile the telematics export.

Standard library only. Every number that can change between quarters comes
from params.csv, never from this file.

Run on its own to check the data and the three check figures:

    python3 data.py --trips trips.csv --vans vans.csv --params params.csv
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import defaultdict
from datetime import date

TRIP_COLUMNS = ["date", "van_id", "driver", "route_id", "odometer_km", "gps_km",
                "start_time", "end_time", "stops", "max_load_kg"]
VAN_COLUMNS = ["van_id", "model", "year", "depot", "ownership", "lease_end",
               "monthly_lease_pln", "refrigerated", "payload_kg"]
CLEAN_TRIP_COLUMNS = ["date", "van_id", "driver", "route_id", "km", "km_source",
                      "start_time", "end_time", "stops", "max_load_kg"]
PROFILE_COLUMNS = VAN_COLUMNS + ["days", "trips", "km_period", "worst_day_km", "range_day_km",
                                 "max_load_kg", "two_shift", "two_shift_days"]

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


_DECIMAL_COMMA_RE = re.compile(r"^-?\d+,\d+$")


def _semicolon_hint(fieldnames):
    """Extra sentence for the usual cause of a broken header: a spreadsheet saved the CSV with semicolons."""
    if fieldnames and any(";" in (name or "") for name in fieldnames):
        return ". The file uses semicolons; save it as CSV with a comma separator and a dot as the decimal mark"
    return ""


def load_params(path):
    """Read params.csv (columns parameter,value) into a dict of strings."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or [c.strip() for c in reader.fieldnames[:2]] != ["parameter", "value"]:
                raise ValueError(f"{path}: expected header 'parameter,value'" + _semicolon_hint(reader.fieldnames))
            params = {}
            for row in reader:
                key = (row["parameter"] or "").strip()
                if key:
                    value = (row["value"] or "").strip()
                    if _DECIMAL_COMMA_RE.match(value):
                        raise ValueError(f"Parameter '{key}' in params.csv has a decimal comma '{value}'; "
                                         f"use a dot: {value.replace(',', '.')}")
                    params[key] = value
    except FileNotFoundError:
        raise FileNotFoundError(f"Parameter file not found: {path}") from None
    if not params:
        raise ValueError(f"{path}: no parameters found")
    return params


def _read_csv(path, required, label):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            header = [c.strip() for c in (reader.fieldnames or [])]
            missing = [c for c in required if c not in header]
            if missing:
                raise ValueError(f"{label} file {path}: missing column(s) {', '.join(missing)}"
                                 + _semicolon_hint(reader.fieldnames))
            return [{k.strip(): (v or "").strip() for k, v in row.items() if k is not None} for row in reader]
    except FileNotFoundError:
        raise FileNotFoundError(f"{label} file not found: {path}") from None


def _to_float(text):
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _van_aliases(params):
    prefix = "van_alias."
    return {k[len(prefix):]: v for k, v in params.items() if k.startswith(prefix) and v}


def _load_vans(path):
    vans = []
    for row in _read_csv(path, VAN_COLUMNS, "Van register"):
        van = {c: row[c] for c in VAN_COLUMNS}
        van["year"] = int(van["year"]) if van["year"].isdigit() else ""
        lease = _to_float(van["monthly_lease_pln"])
        van["monthly_lease_pln"] = "" if lease is None else lease
        payload = _to_float(van["payload_kg"])
        van["payload_kg"] = "" if payload is None else int(payload)
        vans.append(van)
    return vans


def load_and_clean(trips_path, vans_path, params):
    """Return (trips, vans, report).

    trips: cleaned rows with CLEAN_TRIP_COLUMNS, sorted by date, van, start time.
    vans: the register, one dict per van.
    report: lines for data_report.txt; lines starting with 'WARNING' need a look.
    """
    vans = _load_vans(vans_path)
    raw = _read_csv(trips_path, TRIP_COLUMNS, "Trips")
    report = [f"Trip rows read: {len(raw)}", f"Vans in register: {len(vans)}"]

    # 1. Exact duplicate rows (every column identical).
    seen, rows = set(), []
    for row in raw:
        key = tuple(row[c] for c in TRIP_COLUMNS)
        if key not in seen:
            seen.add(key)
            rows.append(row)
    report.append(f"Exact duplicate rows removed: {len(raw) - len(rows)}")

    # 2. Van aliases from params (van_alias.<old>,<new>).
    aliases = _van_aliases(params)
    alias_counts = defaultdict(int)
    for row in rows:
        if row["van_id"] in aliases:
            alias_counts[row["van_id"]] += 1
            row["van_id"] = aliases[row["van_id"]]
    for old in sorted(aliases):
        report.append(f"Alias applied: {old} -> {aliases[old]} on {alias_counts[old]} rows")

    # 3. Rows for vans that are not in the register are never dropped silently.
    known = {v["van_id"] for v in vans}
    unknown = defaultdict(int)
    kept = []
    for row in rows:
        if row["van_id"] in known:
            kept.append(row)
        else:
            unknown[row["van_id"]] += 1
    for van_id in sorted(unknown):
        report.append(f"WARNING: van_id '{van_id}' is not in the van register; {unknown[van_id]} rows "
                      f"excluded. Add it to the register or add van_alias.{van_id} to params.csv.")
    rows = kept

    # 4. Distance: odometer, falling back to GPS when the odometer is missing or not positive.
    trips, missing_gps = [], 0
    for row in rows:
        where = f"{row['date']} {row['van_id']} {row['route_id']}"
        if not _DATE_RE.match(row["date"]):
            report.append(f"WARNING: row rejected, bad date: {where}")
            continue
        try:
            date.fromisoformat(row["date"])
        except ValueError:
            report.append(f"WARNING: row rejected, bad date: {where}")
            continue
        odometer, gps = _to_float(row["odometer_km"]), _to_float(row["gps_km"])
        if gps is None:
            missing_gps += 1
        if odometer is not None and odometer > 0:
            km, source = odometer, "odometer"
        elif gps is not None and gps > 0:
            km, source = gps, "gps"
            report.append(f"WARNING: odometer_km '{row['odometer_km']}' not usable, gps_km {gps} used: {where}")
        else:
            report.append(f"WARNING: row rejected, no usable distance "
                          f"(odometer_km '{row['odometer_km']}', gps_km '{row['gps_km']}'): {where}")
            continue
        load, stops = _to_float(row["max_load_kg"]), _to_float(row["stops"])
        if load is None or load < 0:
            report.append(f"WARNING: row rejected, bad max_load_kg '{row['max_load_kg']}': {where}")
            continue
        for col in ("start_time", "end_time"):
            if not _TIME_RE.match(row[col]):
                report.append(f"WARNING: {col} '{row[col]}' is not HH:MM: {where}")
        trips.append({
            "date": row["date"], "van_id": row["van_id"], "driver": row["driver"],
            "route_id": row["route_id"], "km": km, "km_source": source,
            "start_time": row["start_time"], "end_time": row["end_time"],
            "stops": "" if stops is None else int(stops),
            "max_load_kg": int(load) if load == int(load) else load,
        })
    trips.sort(key=lambda t: (t["date"], t["van_id"], t["start_time"]))

    report.append(f"Rows with gps_km missing (odometer used, no action needed): {missing_gps}")
    report.append(f"Rows where GPS distance replaced the odometer: {sum(t['km_source'] == 'gps' for t in trips)}")
    with_trips = {t["van_id"] for t in trips}
    for van in vans:
        if van["van_id"] not in with_trips:
            report.append(f"WARNING: van {van['van_id']} is in the register but has no trips in this export")
    if trips:
        report.append(f"Period: {trips[0]['date']} to {trips[-1]['date']} ({period_days(trips)} days, "
                      f"{operating_days(trips)} with trips)")
    else:
        report.append("WARNING: no usable trip rows")
    report.append(f"Trip rows kept: {len(trips)}")
    return trips, vans, report


def period_days(trips):
    """Calendar days from the first to the last trip date, inclusive."""
    if not trips:
        return 0
    dates = [t["date"] for t in trips]
    return (date.fromisoformat(max(dates)) - date.fromisoformat(min(dates))).days + 1


def percentile(values, pct):
    """Percentile with linear interpolation (same as Excel PERCENTILE.INC); 100 gives the maximum."""
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * pct / 100.0
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def operating_days(trips):
    """Number of distinct dates with at least one trip by any van."""
    return len({t["date"] for t in trips})


def build_van_profile(trips, vans, params=None):
    """One row per van in the register, with PROFILE_COLUMNS.

    range_day_km is the daily distance compared with the EV range: the
    range_check_percentile (from params) of the van's daily totals. Without
    params it equals worst_day_km.
    """
    pct = 100.0
    if params is not None:
        if params.get("range_check_percentile", "") == "":
            raise ValueError("Missing parameter 'range_check_percentile' in params.csv")
        pct = _to_float(params["range_check_percentile"])
        if pct is None or not 0 < pct <= 100:
            raise ValueError("Parameter 'range_check_percentile' must be a number above 0 and up to 100, "
                             f"got '{params['range_check_percentile']}'")
    by_day = defaultdict(lambda: defaultdict(list))
    for t in trips:
        by_day[t["van_id"]][t["date"]].append(t)
    profile = []
    for van in vans:
        days = by_day.get(van["van_id"], {})
        day_km = [math.fsum(t["km"] for t in day) for day in days.values()]
        loads = [t["max_load_kg"] for day in days.values() for t in day]
        two_shift_days = sum(1 for day in days.values() if len(day) > 1)
        row = dict(van)
        row.update({
            "days": len(days),
            "trips": sum(len(day) for day in days.values()),
            "km_period": round(math.fsum(day_km), 1),
            "worst_day_km": round(max(day_km), 1) if day_km else 0.0,
            "range_day_km": round(percentile(day_km, pct), 1),
            "max_load_kg": max(loads) if loads else 0,
            "two_shift": "yes" if two_shift_days else "no",
            "two_shift_days": two_shift_days,
        })
        profile.append(row)
    return profile


def control_figures(trips, profile):
    """The three figures the CFO checks first."""
    return {
        "vans_assessed": sum(1 for p in profile if p["trips"] > 0),
        "trips_counted": len(trips),
        "total_km": int(round(math.fsum(t["km"] for t in trips))),
    }


def write_csv(path, rows, columns):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Clean the trips export and print the check figures.")
    parser.add_argument("--trips", required=True)
    parser.add_argument("--vans", required=True)
    parser.add_argument("--params", default="params.csv")
    parser.add_argument("--out", help="optional folder for clean_trips.csv, van_profile.csv, data_report.txt")
    args = parser.parse_args(argv)
    try:
        params = load_params(args.params)
        trips, vans, report = load_and_clean(args.trips, args.vans, params)
    except (FileNotFoundError, ValueError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    profile = build_van_profile(trips, vans, params)
    print("\n".join(report))
    print("\nCheck figures")
    for name, value in control_figures(trips, profile).items():
        print(f"  {name}: {value}")
    if args.out:
        import os
        os.makedirs(args.out, exist_ok=True)
        write_csv(os.path.join(args.out, "clean_trips.csv"), trips, CLEAN_TRIP_COLUMNS)
        write_csv(os.path.join(args.out, "van_profile.csv"), profile, PROFILE_COLUMNS)
        with open(os.path.join(args.out, "data_report.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(report) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
