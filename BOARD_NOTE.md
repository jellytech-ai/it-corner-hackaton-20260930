# Which vans go electric first

**Recommendation: buy 8 Volta Cargo EVs with the grant and base all of them at North. Together they save 95637 PLN over five years after paying for the EVs.** Five are North vans; three are South vans that move to North and keep their routes. Without the grant, none of the 8 would pay back in five years.

## The shortlist

| Rank | Van | Today at | EV | km per year | Fuel saving per year | Five-year saving |
|---|---|---|---|---|---|---|
| 1 | P-12 | South | Volta Cargo L | 49835 | 21994 PLN | 23305 PLN |
| 2 | P-30 | North | Volta Cargo S | 38099 | 17544 PLN | 20818 PLN |
| 3 | P-21 | North | Volta Cargo S | 39218 | 16224 PLN | 15337 PLN |
| 4 | P-08 | North | Volta Cargo L | 47329 | 20888 PLN | 15270 PLN |
| 5 | P-05 | South | Volta Cargo S | 34618 | 15941 PLN | 9322 PLN |
| 6 | P-25 | South | Volta Cargo S | 39283 | 16251 PLN | 6596 PLN |
| 7 | P-13 | North | Volta Cargo S | 39854 | 13793 PLN | 3818 PLN |
| 8 | P-04 | North | Volta Cargo S | 38885 | 13457 PLN | 1171 PLN |
| | **Total** | | | | **136092 PLN** | **95637 PLN** |

Source: `shortlist.csv` and `summary.csv`; every van, including rejected ones, is in `all_vans.csv`. Check figures: 38 vans assessed, 2777 trips counted, 344952 km driven between 15 Jun and 12 Sep 2026.

**How the five-year saving is built**, as you asked: what we save on running the van (fuel minus charging, plus lower maintenance) over five years, minus the EV's purchase price after the 30% grant, minus any lease exit fee. For the 8 vans: about 1007600 PLN saved on running, minus 903000 PLN for the EVs after a grant of 387000 PLN, minus 8940 PLN to end P-25's lease early (3 monthly payments). Diesel lease payments and resale values are left out.

## How the vans were chosen

Every van had to pass four tests: not a refrigerated van (6 are out for year 1); the EV carries the heaviest load the van carried this summer (10 more fail; 6 of them were too heavy on only 1–3 days this summer and are marked as near misses in `all_vans.csv`); its 95th-percentile day fits within 60% of the EV's WLTP range, which is 156 km for the Cargo S and 228 km for the Cargo L (7 more fail); and it has an overnight charging point. 15 vans pass. For each, we took the EV model that saves more over five years and ranked them by that saving. 7 of the 15 do not make the list: six do not pay back in five years: P-14, P-10, P-28 and P-32 drive only 21000–24000 km a year, and P-26 and P-20 would pay back but for the fee to end their leases early (8670 and 8820 PLN). P-31 would, by 1589 PLN, but only 3 South vans can move to North. The 8 EVs use 8 of North's 10 charging points.

## Why not simply "the vans that drive the most"

Mileage is what makes an EV pay, and the two vans that drive the most on the list (P-12 and P-08) are near the top. But of the 10 vans with the highest mileage, 8 cannot switch: their 95th-percentile day is 206–293 km. That is beyond the Cargo S, and the Cargo L reaches only one of them (P-33), which carries more than the Cargo L's 880 kg payload. Three of them drive two routes a day and, as you told us, have no time to charge between them.

## The winter risk

The 95th-percentile rule means a van may have a few days a quarter longer than the range we count on. On the list this matters for two vans: P-30's longest day was 166 km and P-21's 159 km, against 156 km for the Cargo S. The other six stayed within the range on every day in the data. We suggest keeping two of the retired diesels as spares for the longest winter days.

| If we change one rule | Vans on the list | Five-year saving |
|---|---|---|
| **As agreed (95th-percentile day, 60% of WLTP)** | **8** | **95637 PLN** |
| Longest day instead of the 95th percentile ("no van may ever fail") | 6 (without P-30, P-21) | 59482 PLN |
| 55% of WLTP instead of 60% | 3 (P-12, P-08, P-05) | 47897 PLN |
| Batteries after five years (about 52% of WLTP) | 2 (P-12, P-08) | 38575 PLN |
| No South vans at North | 5 | 56414 PLN |

The two Cargo L vans (P-12, P-08) have the most range to spare and stay on the list under every range rule above.

## Next steps

1. Apply for the grant for these 8 vans before 16 Oct 2026, as a purchase.
2. Give notice on P-25's diesel lease; P-04's lease ends in May 2027 and is simply not renewed.
3. Decide which two retired diesels stay as winter spares.
4. Rerun the tool on the Q4 export (same command, new data) to check the pre-Christmas peak.
