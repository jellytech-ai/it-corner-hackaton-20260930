<!-- DRAFT (track C, C6). Check against the real ev_shortlist.py after the 12:20 merge; final version after the rerun test (C10). -->

# Rerunning the EV shortlist

This tool reads a telematics export and the van register and writes the EV shortlist, the check figures and a per-van report. It needs **Python 3.9 or newer** and nothing else: no packages to install.

## What is in the folder

| File | What it is |
|---|---|
| `ev_shortlist.py` | the command you run |
| `data.py`, `feasibility.py`, `economics.py` | the steps it calls (cleaning, feasibility, savings); no need to open them |
| `params.csv` | every price, rate and threshold the tool uses; edit this, not the code |
| `RERUN.md` | these instructions |
| `ASSUMPTIONS.md` | what the numbers are based on |

After the first run Python creates a `__pycache__` folder next to the scripts. That is normal; you can ignore or delete it.

## Steps

1. **Get the new export.** Save the fresh telematics export and the current van register as CSV files, for example `trips.csv` and `vans.csv`. The column names must be the same as in the previous export:
   - trips: `date, van_id, driver, route_id, odometer_km, gps_km, start_time, end_time, stops, max_load_kg`
   - vans: `van_id, model, year, depot, ownership, lease_end, monthly_lease_pln, refrigerated, payload_kg`

   The export can cover any period; annual km are scaled from the number of days in the file.

2. **Update `params.csv`.** Open it in Excel or a text editor and change only the `value` column.

   **Every quarter:** set `lease_reference_date` to the date of the analysis (YYYY-MM-DD). It decides which diesel leases end within 12 months and so cost nothing to leave.

   **When something has changed:**

   | What changed | Parameter(s) |
   |---|---|
   | fuel price | `diesel_price_pln_per_l` |
   | electricity tariff | `electricity_night_pln_per_kwh`, `electricity_day_pln_per_kwh` |
   | new charging points at a depot | `chargers.North`, `chargers.South` |
   | how many South vans may be based at North | `max_south_vans_at_north` |
   | EV prices or the grant | `ev.<model>.price_pln`, `grant_share_of_price` (0.30 = 30%) |
   | years the board looks at | `saving_horizon_years` |
   | cost of ending a diesel lease early | `lease_exit_fee_months`, `lease_free_exit_within_months` |
   | a new diesel model in the register | add `fuel_l_per_100km.<model>` |
   | a van renamed in telematics | add `van_alias.<old id>` with the new id as value |
   | the winter range rule | `winter_range_factor` (0.60 = 60% of WLTP range) and `range_check_percentile` (95 = the van's 95th-percentile day) |

   Keep the file as CSV with a comma separator and a dot as the decimal mark.

3. **Run the tool** from the tool folder:

   ```
   python3 ev_shortlist.py --trips trips.csv --vans vans.csv --params params.csv --out results/
   ```

4. **Check the check figures on screen.** The tool prints the number of vans assessed, trips counted and total km. Compare them with the export: trips counted is the number of rows after removing exact duplicates, and total km is their sum.

5. **Read the warnings in `results/data_report.txt`.** Lines starting with `WARNING` need a look; nothing is dropped silently. The report lists removed duplicates, applied van aliases, rows where GPS distance replaced a broken odometer reading, trips of vans that are not in the register (left out of the figures), registered vans without trips, and the date range used. If an unknown van appears, add it to `vans.csv` or to `van_alias` in `params.csv` and run again.

6. **Use the results** in `results/`:

   | File | What it holds |
   |---|---|
   | `shortlist.csv` | recommended vans in rank order, with the EV model, depot and savings |
   | `summary.csv` | check figures, totals and a one-line description of how savings are counted |
   | `all_vans.csv` | every van with the reason it was accepted or rejected |
   | `data_report.txt` | what was cleaned and why |

## Reading the reasons in the results

`N`, `<model>` and `<depot>` below are filled in from the data and `params.csv`.

**`reason`** (in `shortlist.csv` and `all_vans.csv`) says why a feasible van fits:

| Text | Meaning |
|---|---|
| `range margin X km (Y%)` | the van's 95th-percentile day is X km shorter than the EV's winter range |
| `at threshold: range margin …` | the van fits, but the margin is below `at_threshold_pct` (1%); a slightly longer route would push it out |
| `…; South van based at North, routes unchanged` | a South van that would be based at North, because South has no charging points (`max_south_vans_at_north`) |
| `midday charging between routes; 0 failed days` | appears only if `midday_charging_allowed` is `yes`: the van fits because it charges at the depot between its two routes |

**`reject_reason`** (in `all_vans.csv`) says why a van is not feasible. Several reasons are separated by `; `:

| Text | Meaning |
|---|---|
| `refrigerated` | refrigerated vans are out (`exclude_refrigerated`) |
| `payload` | the heaviest load the van carried is more than the cheapest EV model can carry |
| `range` | the van's 95th-percentile day is longer than the cheapest EV model's winter range |
| `no chargers at depot` | the van's depot has no charging points and it cannot be based elsewhere |
| `no trips in this export` | the van is in the register but did not drive in this period |
| `near miss: <model> …` | the van is close to fitting that model: range at most `near_miss_range_pct` (10%) over, or load over the limit on at most `near_miss_days` (3) days. Worth a conversation, not a place on the list |

**`fit_models`** (in `all_vans.csv`) lists every EV model that passes range and load; `ev_model` is the one with the higher `saving_pln`.

**`shortlisted`** and **`shortlist_note`** (in `all_vans.csv`): a feasible van with `shortlisted` = `no` has one of these notes:

| Text | Meaning |
|---|---|
| `saving over N years is not positive` | the EV costs more than it saves over `saving_horizon_years` |
| `grant limit of N EVs reached` | the list is full (`max_evs_grant`) |
| `all N charging points at <depot> taken` | no free charging point at that depot (`chargers.<depot>`) |
| `limit of N vans based away from their depot reached` | no more South vans may be based at North (`max_south_vans_at_north`) |

## If something goes wrong

A problem that stops the tool is printed as one line starting with `ERROR:`, naming the file and the column or parameter to fix. Problems in the data that do not stop it are lines starting with `WARNING:` in `data_report.txt`.

| Message or symptom | What to do |
|---|---|
| `python3: command not found` | install Python 3 from python.org, or try `python` instead of `python3` |
| `ERROR: … file not found: …` | check the path; run the command from the tool folder or give the full path |
| `ERROR: … missing column(s) …` | the export has different column names; rename them to the ones in step 1 |
| `ERROR: Trips file …: no usable trip rows; nothing written` | the file is not the telematics export, or every row was rejected; check the file you passed to `--trips` |
| `ERROR: Missing parameter '<key>' in params.csv` | add the line to `params.csv`. Usual cause: a new diesel model in the register (`fuel_l_per_100km.<model>`) or a new depot (`chargers.<depot>`) |
| `reject_reason` is `no trips in this export` | the van is in the register but did not drive in this period; `data_report.txt` has a matching `WARNING` |
| shortlist is empty | check `all_vans.csv`, column `reject_reason`, to see which rule rejects the vans |
