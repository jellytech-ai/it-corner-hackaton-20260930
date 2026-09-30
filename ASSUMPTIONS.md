# Assumptions and decisions

## Afternoon change (your message of 15:18, done by 15:27): new export, new register, worst-day rule

| # | When | Assumption or decision | Status |
|---|---|---|---|
| A26 | 15:21 | **Your new rule:** a van qualifies only if its worst day in the data fits within 60% of the EV's WLTP range. Set in `params.csv` as `range_check_percentile,100`. This replaces the 95th-percentile rule everywhere, for all vans. | your rule |
| A27 | 15:21 | **Both exports are combined** (`trips.csv` 15 Jun–12 Sep and `trips_latest.csv` 14–26 Sep: 104 days, 89 with deliveries) and `vans_latest.csv` replaces the register (40 vans). | your answer |
| A28 | 15:22 | **The new export names the odometer column `odo_km` instead of `odometer_km`.** We treat it as the same column. It is written in `params.csv` (`column_alias.odo_km,odometer_km`); the tool does not guess, and without that line it stops and names the missing column. This breaks our assumption A18 (same column names every quarter) on the first new export. | accepted |
| A29 | 15:23 | **One odometer reading is impossible:** P-13, 22 Sep, 1383.0 km on one route against 136.7 km by GPS. A reading above `max_plausible_trip_km` (500 km; the longest real route in the data is 306 km) is replaced by the GPS distance, with a warning. You told us to trust the odometer; we do, except for a reading no van can drive in one route. Taken literally it would remove P-13 from the list under the worst-day rule. | accepted |
| A30 | 15:24 | **The two new vans (P-39, P-40) are judged on the 12 days they drove** (from 14 Sep). Their yearly km are scaled from their own delivery days, in the same proportion as the rest of the fleet, not from the whole 104 days. A van counts as new when its first trip is more than `new_van_gap_days` (7) after the start of the data. | accepted |
| A31 | 15:24 | The new vans are leased diesels (to Aug 2029), so replacing them costs the early-exit fee of 3 monthly payments (9300 PLN each); it is included in their saving. | follows your lease rule |
| A32 | 15:25 | **`impact.csv` causes:** we rerun the tool four ways (lunch data and rule; new data with the lunch rule; lunch data with the new rule; new data with the new rule). A van that moves only when the data changes is `new data`, only when the rule changes `new rule`, in both cases `both`. P-25 is `new data`: it still fits and pays back, but the new South van P-40 saves more and takes the third South place at North. | accepted |
| A33 | 15:26 | The lunch shortlist is reproduced exactly with `params_lunch.csv` (the lunch rule) on the lunch files, so the comparison starts from what we sent you. | checked |

All times are CEST on 30 Sep 2026. "Confirmed by you" means your lunch answers settled it; "accepted" means we chose it and would change it if you tell us otherwise. Every number below is a line in `params.csv`, so changing an assumption means changing a value there, not the code.

## Data

| # | When | Assumption | Status |
|---|---|---|---|
| A1 | 10:15 | Rows identical in every column are duplicates and are removed (222 rows; 2999 → 2777 trips). | accepted |
| A2 | 10:42 | `P-17` and `P-17B` are the same van, counted as `P-17B`. Same route (S-R06, nobody else drives it), same driver, P-17 stops on 31 Jul and P-17B starts on 3 Aug. Set in `params.csv` as `van_alias.P-17`. | confirmed by you (P-17 was written off; P-17B took over) |
| A3 | 10:15 | Distance is the odometer reading. GPS is used only when the odometer value is missing or not positive. | confirmed by you ("trust the odometer") |
| A5 | 11:25 | One row (P-27, 13 Aug) has an odometer reading of −208.6 km. We use its GPS distance (90.3 km). General rule: an odometer value that is missing or not positive is replaced by GPS, with a warning. | accepted (decision D8) |
| A11 | 10:30 | There is no other data (for example from winter). | confirmed by you |
| A12 | 10:50 | Routes and loads are the same all year. Annual km are scaled from the number of calendar days in the export (90 days here, × 365 / 90), whatever the number of days the van actually drove: a van that drove on 75 of those days is assumed to drive the same way all year. Each van drives one fixed route (two-shift vans two), average trip length is flat over four months (122–125 km), and operations plan no route changes. Risk: the pre-Christmas peak. Rerunning the tool on the Q4 export will test this. **Known weakness, found at 13:10 and kept after the 14:45 freeze:** the export has 77 days with trips (Monday to Saturday, none on the 15 August holiday), so calendar-day scaling assumes about 312 delivery days a year. With 303 delivery days (public holidays off) the shortlist has 7 vans and 67794 PLN (P-04 drops out); with 300 it has 6 vans and 59379 PLN (P-13 drops out too). The board note shows this table. To rerun with 303 days, set `days_per_year` to 354.2 (303 × 90 / 77). | accepted, with the sensitivity shown |

## Range and winter

| # | When | Assumption | Status |
|---|---|---|---|
| A19 | 12:15 | **Your rule:** a van qualifies if its **95th-percentile day** fits within **60% of the EV's WLTP range**: Volta Cargo S 156 km, Cargo L 228 km. The 95th-percentile day is taken from the van's daily totals (all its routes on a day added up), with linear interpolation as in Excel's `PERCENTILE.INC`. Only days on which the van drove are counted; days without trips are not counted as zero. `range_check_km` in `shortlist.csv` is this figure. | rule confirmed by you; which days count is our choice (you asked us to choose, 15:05) |
| A4, A6 | 10:15, 10:30 | Our morning rule was stricter: the van's worst day within 57% of WLTP. It is replaced by A19; the build-up below shows why 60% is a reasonable January figure. | replaced by A19 |
| A7 | 10:30 | After 5 years battery ageing takes a further × 0.87, so 60% of WLTP becomes about 52%. Shown in the board note as a stress test, not used for the shortlist. | accepted |
| A8 | 10:30 | Energy use is the dealer's figure plus 10% over the year for winter. | accepted |
| A21 | 12:15 | Two-shift vans (P-08, P-09, P-12, P-24, P-36) do not charge between routes: their whole day must fit on one overnight charge. | confirmed by you |

How our morning estimate of winter range was built (it came out at 57%, close to your 60%):

| Factor | Value | Source |
|---|---|---|
| Design day −10 °C | — | Poznań: average January minimum −3 °C, rarely below −12 °C (Weather Spark) |
| Temperature | × 0.70 | about 70% of range at around −7 °C, 30000+ cars (Recurrent) |
| Load | × 0.90 | mid-size van: −7% at half load, −11% at full load (Arval / What Van?) |
| Reserve to return to depot | × 0.90 | operating margin, our choice |
| Battery ageing, 5 years | × 0.87 | vans lose on average 2.7% a year (Geotab) |

## Payload and refrigerated vans

| # | When | Assumption | Status |
|---|---|---|---|
| A9 | 10:30 | The EV's rated payload must cover **the heaviest load the van carried** on any route in the telematics export (the load weight recorded for each route). No seasonal margin. | confirmed by you |
| A25 | 15:20 | The load weight recorded for each route is **goods only, without the driver**. The dealer states the EV payload "with a driver on board", so the two figures compare directly and we add nothing for the driver. If the recorded weight included the driver, fewer vans would fit. | accepted (you asked us to choose, 15:12) |
| A10 | 10:42 | Refrigerated vans (P-03, P-07, P-19, P-23, P-34, P-35) stay diesel in year 1. | confirmed by you |

## Charging

| # | When | Assumption | Status |
|---|---|---|---|
| A20 | 12:15 | North has 10 charging points when the EVs arrive (6 today + 4 ordered), one EV per point overnight. South has none in year 1. Up to 3 South vans can be based at North and keep their routes; nothing is added for the drive between depots. | confirmed by you |
| A23 | 12:29 | When more South vans fit than may be based at North (3), we take those with the highest five-year saving. Today this leaves out P-31 (+1589 PLN over 5 years). | accepted |
| A13 | — | All charging is overnight at the night tariff (0.58 PLN/kWh). Two-shift vans return about 20:40 and leave about 04:30, so a small part of their charge may fall in the day tariff; we do not count it. | accepted |

## Savings

| # | When | Assumption | Status |
|---|---|---|---|
| D13 | 12:17 | `saving_pln` follows **your five-year rule**: 5 × (diesel fuel − EV charging + diesel maintenance − EV maintenance) − EV purchase price after the 30% grant − lease exit fee. Diesel lease payments and resale values are left out. `annual_fuel_saving_pln` is fuel minus charging only, per year. | confirmed by you |
| — | 12:17 | EVs are bought, not leased: the grant pays only on purchase, and 60 lease payments on a Cargo S (174000 PLN) cost more than its price after the grant (105000 PLN). | follows from your answer |
| A22 | 12:17 | A diesel lease ending within 12 months of `lease_reference_date` (30 Sep 2026, so by 30 Sep 2027 inclusive) is not renewed and costs nothing; ending a longer lease early costs 3 monthly payments. The analyst moves `lease_reference_date` forward each quarter. | rule confirmed by you; "inclusive" is our reading |
| — | 11:26 | Maintenance: diesel 0.34 PLN/km (your figure, one rate for all ages and models); EV 0.14 PLN/km (dealer estimate). The register has no per-van maintenance history. | accepted |

## The tool

| # | When | Assumption | Status |
|---|---|---|---|
| A17 | 11:13 | Your analyst is comfortable with the command line, has Python 3 and can edit `params.csv`. | accepted; at 15:09 you said "I live in Excel… one command to rerun it", so `RERUN.md` explains how to open a terminal and how to open the results in Excel |
| A18 | 12:12 | The next export has the same two files with the same column names; only the rows and the period change. If a column is missing, the tool stops and names it. | accepted (you asked us to choose, 15:09) |

## Decisions

| # | When | Decision | Why |
|---|---|---|---|
| D1 | 10:42 | Refrigerated vans are not in the first round. | 5 of 6 carry more than 1050 kg on 22–40 days a quarter, above both EV payloads; the dealer offers no refrigerated version; drivers doubt the cooling unit can run on the battery. You confirmed it at lunch. |
| D2 | 10:42 | P-17 is merged into P-17B without asking you. | see A2 |
| D3 | 10:50 | EV payload is a hard limit checked on the heaviest load in the data; we do not propose splitting loads across two vans. | Rated payload is a legal limit; splitting loads means changing routes. Vans that fail on 1–3 days only are listed as near misses. |
| D4 | 10:50 | Seasonality is handled as assumption A12, without asking you. | There is no winter data; the Q4 rerun will check it. |
| D5 | 11:13 | The tool is a Python script with no dependencies, with all values in `params.csv`, and annual km scaled from the period in the export. | "A script is enough"; everything goes into the Slack thread as files; the analyst reruns it alone. |
| D6 | 11:20 | The tool is one folder and one command, split into four `.py` files. | Cleaning, feasibility and savings are kept apart so each can be checked separately. |
| D8 | 11:25 | A missing or non-positive odometer value is replaced by GPS with a warning; a row with neither is rejected with a warning. | No trip is lost silently; the check figures (344952 km) are counted this way. |
| D9 | 11:25 | Trips of a van that is not in the register (after aliases) are left out of the figures, with a warning saying what to add to `vans.csv` or `van_alias`. | A future export may contain a new van; you should see it rather than get silently changed numbers. |
| D10 | 11:25 | `vans_assessed` counts registered vans with at least one trip; a registered van without trips gets a warning. | The check figure matches what was actually assessed. |
| D7 | 11:26 | Morning basis: `saving_pln` = annual operating saving only. | Replaced by D13 after your lunch answer. |
| D15 | 12:19 | Ranking: highest five-year saving first; ties go to the van with more km. A van whose five-year saving is zero or negative is not on the shortlist; nor is a van for which no charging point, South-van place or grant place is left. Every such van has the reason in `all_vans.csv`. | A van that does not pay back in five years is information for the board, not a recommendation (P-14, P-26, P-10, P-20, P-28, P-32). |
| D16 | 12:29 | Every EV on the list is counted as bought, so the grant limit of 10 EVs is the limit of the shortlist. | The grant pays only on purchase, and buying after the grant (105000 PLN for a Cargo S) costs less than 60 lease payments (174000 PLN). |
| D14 | 12:17 | For each van, the EV model is the one with the higher five-year `saving_pln` among the models that pass range and payload. | Your answer: "take whichever EV model works out better over the five years". |

## Your answers

| When | Question | Answer | Effect |
|---|---|---|---|
| before 10:29 | Is there any other data (for example from winter)? | No. | A11 |
| lunch | Charging | North 6 + 4 ordered = 10, one EV per point; none at South in year 1; up to 3 South vans can be based at North. | A20 |
| lunch | Grant | 30% of the purchase price, at most 10 EVs, only if bought. | D13 |
| lunch | Winter range | 95th-percentile day within 60% of WLTP. | A19 |
| lunch | Diesel leases | Leases ending within 12 months are not renewed; ending early costs 3 monthly fees. | A22 |
| lunch (answers to other teams) | Saving basis, model choice, two-shift vans, fridge vans, odometer, P-17 | Five years, EV after grant, lease exit fee, no diesel lease payments or resale; the better model over five years; no charging between routes; fridge vans out in year 1; trust the odometer; P-17B replaced P-17. | D13, D14, A21, A10, A3, A2 |
| 15:09 | How many vans | "As many as make sense, and the grant stops at 10." | 8 vans stay: only vans that pay back in five years are listed (D15) |
| 15:09 | Analyst and rerun | "I live in Excel. Give me CSV, XLSX if you like, and one command to rerun it." | A17; one command in `RERUN.md` |
| 15:05–15:12 (answers to us and other teams) | Same files next quarter, scaling km to a year, winter mileage, which South vans, which days count for the percentile, whether the load includes the driver | "Pick the one that makes sense and put it in your assumptions list." | A18, A12, A23, A19, A25 |

## What we would ask next

1. **Vans with a negative five-year result:** we leave them off the shortlist and list them in the board note as "fits, but does not pay back in five years". Is that how the board should see them?
2. **Grant conditions:** must the application name specific vans, and must the replaced diesel be scrapped?
3. **Retired diesels:** kept as spares for the coldest days, or sold? You asked us to leave resale out of the saving, but spares would cover the winter risk.
4. **Battery capacity after 5 years:** does the dealer guarantee it? The board note shows which vans on the list would still qualify at about 52% of WLTP.
5. **Maintenance:** is there per-van maintenance history? Older diesels probably cost more than 0.34 PLN/km.
6. **Busiest period:** when is it, so the analyst knows which quarter's rerun to watch most closely?
7. **Delivery days a year:** do you deliver on public holidays? The export has none on 15 August. It decides whether P-13 and P-04 stay on the list (assumption A12).
