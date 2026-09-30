<!-- DRAFT (track C, C9), from HANDOFF.md sections 6 and 10 as of 11:41. Update after Ewa's lunch answers (C7) and the 14:45 freeze. -->

# Assumptions and decisions

All times are CEST on 30 Sep 2026. "Open" means we used the stated default and would change it if you tell us otherwise. Every number below is a line in `params.csv`, so changing an assumption means changing a value there, not the code.

## Data

| # | When | Assumption | Status |
|---|---|---|---|
| A1 | 10:15 | Rows identical in every column are duplicates and are removed (222 rows; 2,999 → 2,777 trips). | accepted |
| A2 | 10:42 | `P-17` and `P-17B` are the same van, counted as `P-17B`. Same route (S-R06, nobody else drives it), same driver, P-17 stops on 31 Jul and P-17B starts on 3 Aug, average trip 112 vs 111 km, and the register has 38 vans. Set in `params.csv` as `van_alias.P-17`. | accepted |
| A3 | 10:15 | Distance is the odometer reading. GPS is used only when the odometer value is missing or not positive. Where both exist, the odometer is on average 27 km higher on dense routes with about 34 stops; we trust the odometer, as GPS loses distance between buildings. | accepted |
| A5 | 11:25 | One row (P-27, 13 Aug) has an odometer reading of −208.6 km. We use its GPS distance (90.3 km). General rule: an odometer value that is missing or not positive is replaced by GPS, with a warning. | accepted (decision D8) |
| A11 | 10:30 | There is no other data (for example from winter). | confirmed by you |
| A12 | 10:50 | Routes and loads are the same all year. Annual km are scaled from the number of days in the export (90 days here, × 365 / 90); the winter worst day and maximum load equal the summer ones. Each van drives one fixed route (two-shift vans two), average trip length is flat over four months (122–125 km), and operations plan no route changes. Risk: the pre-Christmas peak. Rerunning the tool on the Q4 export will test this. | accepted |

## Range and winter

| # | When | Assumption | Status |
|---|---|---|---|
| A4 | 10:15 | The range test uses each van's **worst day** (the sum of its trips on that day), not the average day. A van passes only if it would have completed every day in the data. | accepted (operations requirement) |
| A6 | 10:30 | Winter range = **0.57 × WLTP**: Volta Cargo S about 148 km, Cargo L about 217 km. Built from a −10 °C design day in Poznań (temperature × 0.70), load (× 0.90) and a reserve for the drive back (× 0.90). Sensitivity shown at 0.50 and 0.65. | accepted as base case |
| A7 | 10:30 | After 5 years (end of the EV lease) battery ageing takes a further × 0.87, giving 0.49 × WLTP (S about 128 km, L about 187 km). Shown as a stress test, not used for the shortlist. | accepted |
| A8 | 10:30 | Energy use is the dealer's figure plus 10% over the year for winter. | accepted |
| A16 | 10:50 | Two-shift vans (P-08, P-09, P-12, P-24, P-36) top up at the depot between routes on a 22 kW point, minus 15 minutes to plug in. Winter gain is about 58 km per hour on Cargo S and 51 km on Cargo L. Test for every two-route day: route 1 ≤ winter range, and charge after the top-up ≥ route 2. The top-up is counted as a full recharge of what route 1 used, billed at the day tariff (P-08: 48% of its energy), which is the cautious choice for cost. For these vans `range_check_km` is the longer of the two routes on the worst day, since that is what one charge must cover. | accepted |

Why 0.57:

| Factor | Value | Source |
|---|---|---|
| Design day −10 °C | — | Poznań: average January minimum −3 °C, rarely below −12 °C (Weather Spark) |
| Temperature | × 0.70 | about 70% of range at around −7 °C, 30,000+ cars (Recurrent) |
| Load | × 0.90 | mid-size van: −7% at half load, −11% at full load (Arval / What Van?) |
| Reserve to return to depot | × 0.90 | operating margin, our choice |
| Battery ageing, 5 years | × 0.87 | vans lose on average 2.7% a year (Geotab) |

Limits of this estimate: the large temperature studies are mostly passenger cars, and delivery work with 20–35 stops may do worse. Multiplying the factors assumes the longest day falls on the coldest day, which is deliberately cautious.

## Payload and refrigerated vans

| # | When | Assumption | Status |
|---|---|---|---|
| A9 | 10:30 | Payload test: the van's highest observed load must not exceed the EV's rated payload. No seasonal margin (no source for one). | accepted |
| A10 | 10:42 | Refrigerated vans (P-03, P-07, P-19, P-23, P-34, P-35) are left out of the first round. | accepted (decision D1) |

## Charging

| # | When | Assumption | Status |
|---|---|---|---|
| A13 | — | Overnight charging at the night tariff (0.58 PLN/kWh); one charging point per EV. Two-shift vans return about 20:40 and leave about 04:30, so part of their charge may fall in the day tariff. | open |
| A14 | — | At most 6 EVs at North (one per charging point), none at South (no points). | open — waiting for your answer (question 1) |

## Savings

| # | When | Assumption | Status |
|---|---|---|---|
| A15 | 11:26 | `saving_pln` is the **annual operating saving**: diesel fuel cost minus EV charging cost, plus diesel maintenance minus EV maintenance. It does not include the EV lease or purchase price, the remaining diesel lease payments or the grant. `annual_fuel_saving_pln` is fuel minus charging only. | accepted (decision D7) |
| — | 11:26 | Maintenance: diesel 0.34 PLN/km (your figure, one rate for all ages and models); EV 0.14 PLN/km (dealer estimate). The register has no per-van maintenance history, so an older diesel is probably cheaper to replace than these figures show. | accepted |

## The tool

| # | When | Assumption | Status |
|---|---|---|---|
| A17 | 11:13 | Your analyst is comfortable with the command line, has Python 3 and can edit `params.csv`. | accepted (not confirmed by you) |

## Decisions

| # | When | Decision | Why |
|---|---|---|---|
| D1 | 10:42 | Refrigerated vans are not in the first round. | 5 of 6 carry more than 1,050 kg on 22–40 days a quarter (up to 1,247–1,284 kg), above both EV payloads. The sixth (P-19, max 996 kg) has a 150 km worst day, above the 148 km winter range. The dealer offers no refrigerated version, and drivers doubt the cooling unit can run on the battery. |
| D2 | 10:42 | P-17 is merged into P-17B without asking you. | see A2 |
| D3 | 10:50 | EV payload is a hard limit checked on the highest load in the data; we do not propose splitting loads across two vans. | Rated payload is a legal limit; operations require the EV to carry what the vans carry today; splitting loads means changing routes. Vans that fail on 1–3 days only are listed as "near the limit". |
| D4 | 10:50 | Seasonality is handled as assumption A12, without asking you. | There is no winter data; the Q4 rerun will check it. |
| D5 | 11:13 | The tool is a Python script with no dependencies, with all values in `params.csv`, and annual km scaled from the period in the export. | "A script is enough"; everything goes into the Slack thread as files; the analyst reruns it alone. |
| D8 | 11:25 | A missing or non-positive odometer value is replaced by GPS with a warning; a row with neither is rejected with a warning. | No trip is lost silently; the control figures (344,952 km) are counted this way. |
| D9 | 11:25 | Trips of a van that is not in the register (after aliases) are left out of the figures, with a warning saying what to add to `vans.csv` or `van_alias`. | A future export may contain a new van; you should see it rather than get silently changed numbers. |
| D10 | 11:25 | `vans_assessed` counts registered vans with at least one trip; a registered van without trips gets a warning. | The control figure matches what was actually assessed. |
| D6 | 11:20 | The tool is one folder and one command, split into four `.py` files. | Cleaning, feasibility and savings are kept apart so each can be checked separately. |
| D7 | 11:26 | `saving_pln` = annual operating saving (see A15). | Simple and checkable from the rates in `params.csv`, with no guesses about the grant, lease exit or a new diesel's price. The full cost of the EV (Cargo S lease about 34,800 PLN a year against about 14,000 PLN operating saving) is set out in the board note. |

## Your answers

| When | Question | Answer | Effect |
|---|---|---|---|
| before 10:29 | Is there any other data (for example from winter)? | No. | A11 |

## What we would ask next

1. **Charging:** can North get more points, or South any? Can an EV based at North replace a South diesel? This sets whether the shortlist is 3, 6 or 10 vans.
2. **Grant:** how much per van, does it cover leasing or only purchase, and must a specific diesel be retired? This decides whether switching pays off at full cost.
3. **Winter range:** will operations accept about 57% of WLTP? Can the dealer give battery capacity and confirm a heat pump?
4. **Diesel leases:** what does ending a lease early cost, and when could the EVs actually arrive? This affects P-14 (lease to Mar 2027) and P-26 (to Jun 2028).
5. **Retired diesels:** sold (for how much) or kept as spares for the days an EV cannot cover?
6. **Two-shift vans:** do they really return to the depot between routes? The data only shows end and start times.
7. **Maintenance:** is there per-van maintenance history? Older diesels probably cost more than 0.34 PLN/km.
