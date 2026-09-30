<!-- DRAFT (track C, C8), numbers from the 11:46 run on the full export, not yet frozen. Refresh from summary.csv / shortlist.csv / all_vans.csv after the 14:45 freeze and after Ewa's lunch answers (grant, chargers, lease exit). -->

# Which vans go electric first

**Recommendation: replace 3 diesel vans at North with Volta Cargo S now (P-08, P-26, P-14), not 10.** They are the only vans that would complete every day in our data on a winter charge, carry their current loads and have a charging point. Each further EV needs either charging points at South or a decision to accept a lower winter margin.

## The numbers

| Rank | Van | EV | Distance per year | Fuel saving per year | Fuel + maintenance saving per year | Why it qualifies |
|---|---|---|---|---|---|---|
| 1 | P-08 | Volta Cargo S | 47329 km | 19738 PLN | 29204 PLN | two routes a day; tops up at the depot between them, no failed day |
| 2 | P-26 | Volta Cargo S | 34795 km | 14394 PLN | 21353 PLN | worst day 141.8 km against 148 km winter range |
| 3 | P-14 | Volta Cargo S | 22805 km | 9434 PLN | 13995 PLN | worst day 148.0 km: exactly at the limit |
| | **Total** | | | **43566 PLN** | **64552 PLN** | |

Source: `shortlist.csv` and `summary.csv`; every van, including rejected ones, is in `all_vans.csv`.

Check figures: 38 vans assessed, 2777 trips counted, 344952 km driven between 15 Jun and 12 Sep 2026. Savings are at current prices (diesel 5.20 PLN/l, mostly night charging at 0.58 PLN/kWh) and include a 10% winter energy uplift.

**The savings do not pay for the vans on their own.** Leasing three Cargo S costs 104400 PLN a year (2900 PLN a month each), against 64552 PLN saved: about 40000 PLN a year short before any grant. Buying them costs 450000 PLN, which the savings repay in about 7 years, longer than the 5-year lease term the dealer offers. The case therefore rests on the grant, whose amount we do not yet know. P-14 and P-26 are leased diesels (to Mar 2027 and Jun 2028); the cost of ending those leases early is not included.

## Why not "the vans that drive the most"

Of the 10 vans with the highest mileage, 8 have a worst day of 208–302 km. All are beyond what the Cargo S can be relied on to do in January (about 148 km); the Cargo L (about 217 km) would cover only one of them, P-33, which carries more than the Cargo L's 880 kg payload. A van that drives far on an average day also has long single days, and one failed route is not acceptable to operations. The one high-mileage van that fits, P-08, qualifies only because it splits its day into two routes and recharges in between. The next one, P-12, would qualify in the same way, but it is based at South, which has no charging points.

## Winter risk

The winter range is our estimate, not a measured figure: 57% of the brochure (WLTP) range, built from published data on cold-weather range loss (−10 °C day), a full load and a reserve for the return to the depot. There is no winter data from the fleet.

| Winter range assumed | Vans that qualify |
|---|---|
| 50% of WLTP (colder, or battery aged) | 1: P-08 |
| **57% (our base case)** | **3: P-08, P-26, P-14** |
| 65% (milder) | 8, of which 6 fit the 6 charging points at North |

P-14 passes with 0.2 km to spare, so it is the most exposed van on the list. After 5 years of battery ageing (about 49% of WLTP) only P-08 would still qualify. Keeping the replaced diesels as spares for the coldest days would cover this risk.

## What would change the answer

1. **Charging points at South.** Five South vans (P-05, P-10, P-12, P-20, P-25) already fit on range and load; with points installed, the list grows to 8, within the 10-van grant.
2. **The grant** — how much per van, and whether it covers leasing — decides whether the switch pays at full cost.
3. **Early lease exit** for P-14 and P-26, and whether the replaced diesels are sold or kept.

## Next steps

- Confirm the grant terms and apply for 3 vans before 16 Oct 2026, with the South charging decision as the route to more.
- Rerun the tool on the Q4 export (same command, fresh data) to check the pre-Christmas peak and, from January, real winter days.
