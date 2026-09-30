"""Compare the new shortlist with the one sent before and say why each van entered or left.

Runs the tool four times: the earlier data with the earlier rule (the shortlist
sent before), the new data with the earlier rule, the earlier data with the new
rule, and the new data with the new rule. Writes impact.csv with the columns
van_id, change, cause, note.

    python3 impact.py --old-trips trips.csv --old-vans vans.csv --old-params params_lunch.csv \
        --trips trips.csv trips_latest.csv --vans vans_latest.csv --params params.csv --out results/
"""
import argparse
import csv
import os
import sys
import tempfile

import data
import ev_shortlist

RULE_PREFIXES = ("range_check_percentile", "winter_range_factor")


def _run(trips, vans, params, tmp, name):
    params_path = os.path.join(tmp, name + ".csv")
    with open(params_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["parameter", "value"])
        writer.writerows(params.items())
    out = os.path.join(tmp, name)
    ev_shortlist.run(trips, vans, params_path, out)
    with open(os.path.join(out, "all_vans.csv"), newline="", encoding="utf-8") as f:
        return {row["van_id"]: row for row in csv.DictReader(f)}


def _on(rows, van_id):
    return rows.get(van_id, {}).get("shortlisted") == "yes"


def _pays(rows, van_id):
    """The van itself passes every filter and pays back, whatever the limits on places."""
    row = rows.get(van_id, {})
    return row.get("feasible") == "yes" and row.get("saving_pln", "") not in ("", None) and float(row["saving_pln"]) > 0


def _note(change, van_id, before, after, base_rows):
    row = after.get(van_id, {})
    if change == "entered":
        if van_id not in base_rows:
            return "new van in the register; fits %s, saves %s PLN over 5 years" % (row["ev_model"], row["saving_pln"])
        return "now fits %s and saves %s PLN over 5 years" % (row["ev_model"], row["saving_pln"])
    if row.get("feasible") != "yes":
        return "worst day %s km; %s" % (row.get("worst_day_km", "?"), row.get("reject_reason", ""))
    note = row.get("shortlist_note", "") or "no longer on the list"
    if "limit" in note:
        note += "; the place goes to a van with a higher saving"
    return note


def impact(old_trips, old_vans, old_params, new_trips, new_vans, new_params):
    """Return impact rows: one per van that entered or left the shortlist."""
    rule_keys = [k for k in new_params if k.startswith(RULE_PREFIXES)]
    old_rule_on_new_data = dict(new_params, **{k: old_params[k] for k in rule_keys if k in old_params})
    new_rule_on_old_data = dict(old_params, **{k: new_params[k] for k in rule_keys})
    with tempfile.TemporaryDirectory() as tmp:
        base = _run(old_trips, old_vans, old_params, tmp, "before")
        data_only = _run(new_trips, new_vans, old_rule_on_new_data, tmp, "new_data")
        rule_only = _run(old_trips, old_vans, new_rule_on_old_data, tmp, "new_rule")
        final = _run(new_trips, new_vans, new_params, tmp, "after")
    rows = []
    for van_id in sorted(set(base) | set(final)):
        was, now = _on(base, van_id), _on(final, van_id)
        if was == now:
            continue
        change = "entered" if now else "left"
        by_data = _on(data_only, van_id) != was
        by_rule = _on(rule_only, van_id) != was
        if by_data and by_rule:
            cause = "both"
        elif by_data:
            cause = "new data"
        elif by_rule:
            cause = "new rule"
        elif _pays(base, van_id) != _pays(final, van_id):
            cause = "both"  # neither change alone moves the van, the two together do
        else:
            cause = "other"
        rows.append({"van_id": van_id, "change": change, "cause": cause,
                     "note": _note(change, van_id, base, final, base)})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write impact.csv: which vans entered or left the shortlist, and why.")
    ap.add_argument("--old-trips", required=True, nargs="+")
    ap.add_argument("--old-vans", required=True)
    ap.add_argument("--old-params", required=True)
    ap.add_argument("--trips", required=True, nargs="+")
    ap.add_argument("--vans", required=True)
    ap.add_argument("--params", required=True)
    ap.add_argument("--out", default="results")
    a = ap.parse_args(argv)
    one = lambda paths: paths[0] if len(paths) == 1 else paths
    try:
        rows = impact(one(a.old_trips), a.old_vans, data.load_params(a.old_params),
                      one(a.trips), a.vans, data.load_params(a.params))
    except (FileNotFoundError, ValueError) as err:
        print("ERROR: %s" % err, file=sys.stderr)
        return 1
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "impact.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["van_id", "change", "cause", "note"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print("%(van_id)s %(change)s (%(cause)s): %(note)s" % row)
    print("Impact written to: %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
