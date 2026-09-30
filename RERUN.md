<!-- DRAFT (track C, C6). Check against the real ev_shortlist.py after the 12:20 merge; final version after the rerun test (C10). -->

# Rerunning the EV shortlist

This tool reads a telematics export and the van register and writes the EV shortlist, the control figures and a per-van report. It needs **Python 3.9 or newer** and nothing else: no packages to install.

## What is in the folder

| File | What it is |
|---|---|
| `ev_shortlist.py` | the command you run |
| `data.py`, `feasibility.py`, `economics.py` | the steps it calls (cleaning, feasibility, savings); no need to open them |
| `params.csv` | every price, rate and threshold the tool uses; edit this, not the code |
| `ASSUMPTIONS.md` | what the numbers are based on |

## Steps

1. **Get the new export.** Save the fresh telematics export and the current van register as CSV files, for example `trips.csv` and `vans.csv`. The column names must be the same as in the previous export:
   - trips: `date, van_id, driver, route_id, odometer_km, gps_km, start_time, end_time, stops, max_load_kg`
   - vans: `van_id, model, year, depot, ownership, lease_end, monthly_lease_pln, refrigerated, payload_kg`

   The export can cover any period; annual km are scaled from the number of days in the file.

2. **Update `params.csv` if anything has changed.** Open it in Excel or a text editor and change only the `value` column. Typical changes:

   | What changed | Parameter(s) |
   |---|---|
   | fuel price | `diesel_price_pln_per_l` |
   | electricity tariff | `electricity_night_pln_per_kwh`, `electricity_day_pln_per_kwh` |
   | new charging points at a depot | `chargers.North`, `chargers.South` |
   | a new diesel model in the register | add `fuel_l_per_100km.<model>` |
   | a van renamed in telematics | add `van_alias.<old id>` with the new id as value |
   | a different winter range assumption | `winter_range_factor` (0.57 = 57% of WLTP range) |

   Keep the file as CSV with a comma separator and a dot as the decimal mark.

3. **Run the tool** from the tool folder:

   ```
   python3 ev_shortlist.py --trips trips.csv --vans vans.csv --params params.csv --out results/
   ```

4. **Check the control figures on screen.** The tool prints the number of vans assessed, trips counted and total km. Compare them with the export: trips counted is the number of rows after removing exact duplicates, and total km is their sum.

5. **Read the warnings in `results/data_report.txt`.** Lines starting with `WARNING` need a look; nothing is dropped silently. The report lists removed duplicates, applied van aliases, rows where GPS distance replaced a broken odometer reading, trips of vans that are not in the register (left out of the figures), registered vans without trips, and the date range used. If an unknown van appears, add it to `vans.csv` or to `van_alias` in `params.csv` and run again.

6. **Use the results** in `results/`:

   | File | What it holds |
   |---|---|
   | `shortlist.csv` | recommended vans in rank order, with the EV model, depot and savings |
   | `summary.csv` | control figures, totals and a one-line description of how savings are counted |
   | `all_vans.csv` | every van with the reason it was accepted or rejected |
   | `data_report.txt` | what was cleaned and why |

## If something goes wrong

A problem that stops the tool is printed as one line starting with `ERROR:`, naming the file and the column or parameter to fix. Problems in the data that do not stop it are lines starting with `WARNING:` in `data_report.txt`.

| Message or symptom | What to do |
|---|---|
| `python3: command not found` | install Python 3 from python.org, or try `python` instead of `python3` |
| missing column | the export has different column names; rename them to the ones in step 1 |
| missing parameter, e.g. `fuel_l_per_100km.<model>` | a new model is in the register; add the line to `params.csv` |
| shortlist is empty | check `all_vans.csv`, column `reject_reason`, to see which rule rejects the vans |
