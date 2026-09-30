"""Build fixtures/fresh_trips.csv: a pretend next-quarter export for the rerun test.

Takes the first six weeks of the real export, moves the dates 16 weeks forward
(so weekdays stay the same) and plants three problems the tool must report:
a van that is not in the register, a negative odometer reading with a usable
GPS distance, and a row with no usable distance at all.

    python3 fixtures/make_fresh_trips.py ../it-corner-hackathon-20260930/trips.csv
"""
import csv
import os
import sys
from datetime import date, timedelta

SHIFT = timedelta(weeks=16)
LAST_DAY = "2026-07-26"


def main(source):
    with open(source, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = [r for r in reader if r["date"] <= LAST_DAY]
    for r in rows:
        r["date"] = (date.fromisoformat(r["date"]) + SHIFT).isoformat()
    planted = {"unknown": 0, "negative": False, "nodistance": False}
    for r in rows:
        if r["van_id"] == "P-05" and planted["unknown"] < 3:
            r["van_id"] = "P-39"
            planted["unknown"] += 1
        elif r["van_id"] == "P-13" and not planted["negative"]:
            r["odometer_km"] = "-" + r["odometer_km"]
            planted["negative"] = True
        elif r["van_id"] == "P-21" and not planted["nodistance"]:
            r["odometer_km"], r["gps_km"] = "0", ""
            planted["nodistance"] = True
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fresh_trips.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{out}: {len(rows)} rows")


if __name__ == "__main__":
    main(sys.argv[1])
