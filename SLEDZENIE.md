# SLEDZENIE — od wymagania do testu i kolumny wyniku

Stan: 30.09.2026, 13:15, na `devel` (`9a72ed6`). Właściciel: tor A. Każdy wiersz mówi, skąd wzięło się wymaganie, który parametr je niesie, który kod je liczy, który test go pilnuje i gdzie Ewa zobaczy skutek.

Nowa reguła albo parametr dostaje tu wiersz **razem z testem** (`KONSTYTUCJA.md`, sekcja 7). Wiersz bez testu trafia do sekcji 3.

Skróty: `a`, `b`, `c` = `tests/test_a.py`, `test_b.py`, `test_c.py`. Numery A i D: `HANDOFF.md`, sekcje 6 i 10.

## 1. Reguły Ewy (odpowiedzi z ok. 12:00 i README)

| # | Wymaganie (źródło) | Parametr | Kod | Testy | Gdzie w wyniku |
|---|---|---|---|---|---|
| R1 | Van przechodzi, gdy jego 95. percentyl dnia mieści się w 60% zasięgu WLTP (A19) | `winter_range_factor`, `range_check_percentile` | `data.percentile`, `data.build_van_profile`, `feasibility.assess` | a: `test_percentile_is_linear_like_excel`, `test_range_day_uses_percentile_from_params` · b: `test_winter_factor_comes_from_params`, `test_winter_range_below_at_above`, `test_range_is_checked_on_range_day_km`, `test_exactly_on_threshold_passes` | `range_check_km`, `reject_reason` |
| R2 | North ma 10 punktów, jeden EV na punkt (A20) | `chargers.North` | `ev_shortlist.rank_with_notes` | b: `test_depot_charger_limit_cuts_per_depot`, `test_charging_points_full_note`, `test_shortlist_respects_limits` | `shortlist_note` |
| R3 | South bez ładowarek; do 3 vanów z South stacjonuje w North (A20, A23) | `chargers.South`, `max_south_vans_at_north` | `feasibility.assess`, `ev_shortlist.rank_with_notes` | b: `test_south_van_is_based_at_north`, `test_south_vans_off_when_not_allowed`, `test_moved_vans_limit_below_at_above`, `test_left_out_south_van_has_note` | `ev_depot`, `shortlist_note` |
| R4 | Vany dwuzmianowe nie ładują się w dzień; liczy się cały dzień (A21) | `midday_charging_allowed` | `feasibility.assess` | b: `test_two_shift_vans_count_their_whole_day` | `midday_charging`, `day_tariff_share` |
| R5 | Dotacja: 30% ceny zakupu, najwyżej 10 EV (D13, D16) | `grant_share_of_price`, `max_evs_grant` | `economics.saving_for_model`, `ev_shortlist.rank_with_notes` | c: `test_horizon_and_grant_come_from_params` · b: `test_sorted_by_saving_then_annual_km_and_cut_by_grant`, `test_shortlist_respects_limits` | `saving_pln`, `recommended_count` |
| R6 | Wynik w 5 lat: oszczędność z eksploatacji − cena EV po dotacji − opłata za leasing (D13) | `saving_horizon_years` | `economics.economics`, `economics.saving_basis` | c: `test_saving_pln_is_five_years_running_minus_ev_after_grant`, `test_horizon_and_grant_come_from_params`, `test_saving_basis_follows_params` | `saving_pln`, `saving_basis` |
| R7 | Wyjście z leasingu: 3 raty; leasing kończący się w 12 miesięcy bez opłaty (A22) | `lease_exit_fee_months`, `lease_free_exit_within_months`, `lease_reference_date` | `economics.lease_exit_fee` | c: cała klasa `LeaseExitFeeTest` (tuż przed, na i tuż za granicą), `test_saving_pln_subtracts_exit_fee_for_long_lease` | `saving_pln` |
| R8 | Dla każdego vana model EV z lepszym wynikiem w 5 lat (D14) | — | `ev_shortlist.choose_models`, `economics.saving_for_model` | b: `test_better_saving_model_is_chosen` · c: `test_saving_for_model_compares_models_for_one_van` | `ev_model`, `fit_models` |
| R9 | Analityk uruchamia narzędzie bez nas na kolejnym eksporcie (pytanie Ewy z 12:03; A17, A18) | — | `ev_shortlist.main`, `data.main` | b: klasa `EntryPointMessages`, `test_cli_runs` · a: `test_trips_saved_with_semicolons_says_so`, `test_params_saved_with_semicolons_says_so`, `test_decimal_comma_in_a_parameter_names_the_parameter`, `test_missing_params_file` | ekran, `data_report.txt`, `RERUN.md` |
| R10 | Pliki w formacie importu Ewy (README) | — | `ev_shortlist.run` | b: `test_shortlist_header_is_eva_format`, `test_summary_figures`, `test_range_check_has_one_decimal_and_money_is_integer`, `test_all_vans_columns_in_contract_order` | `shortlist.csv`, `summary.csv`, `all_vans.csv` |
| R11 | Liczby kontrolne 38 / 2777 / 344952 (README; `KONTRAKT.md`, sekcja 8) | — | `data.control_figures` | a: `test_check_figures`, `test_matches_fixtures` · b: `test_full_run_control_figures` | `summary.csv`, ekran |

## 2. Nasze decyzje i założenia

| # | Wymaganie (źródło) | Parametr | Kod | Testy | Gdzie w wyniku |
|---|---|---|---|---|---|
| W1 | Chłodnie poza pierwszą turą (D1) | `exclude_refrigerated` | `feasibility.assess` | b: `test_refrigerated_rule_from_params`, `test_refrigerated_not_near` | `reject_reason` |
| W2 | P-17 to ten sam van co P-17B (D2) | `van_alias.P-17` | `data.load_and_clean` | a: `test_alias_applied` | `data_report.txt` |
| W3 | Ładowność EV to twardy limit na maksimum z danych (D3) | `ev.<model>.payload_kg` | `feasibility.assess` | b: `test_payload_below_at_above` | `reject_reason` |
| W4 | Dokładne duplikaty kursów usuwamy | — | `data.load_and_clean` | a: `test_exact_duplicates_removed` | `data_report.txt`, `trips_counted` |
| W5 | Zły licznik → dystans z GPS; brak obu → wiersz odrzucony, zawsze z ostrzeżeniem (D8) | — | `data.load_and_clean` | a: `test_bad_odometer_falls_back_to_gps`, `test_missing_gps_keeps_odometer`, `test_no_usable_distance_rejected` | `data_report.txt` |
| W6 | Van spoza rejestru nie wchodzi do liczb (D9) | — | `data.load_and_clean` | a: `test_unknown_van_excluded_with_warning` | `data_report.txt` |
| W7 | Van bez kursów nie jest oceniany (D10) | — | `feasibility.assess` | b: `test_van_without_trips_is_not_feasible` | `reject_reason` |
| W8 | Ranking malejąco po `saving_pln`; van z wynikiem ≤ 0 poza listą, z notatką (D15) | — | `ev_shortlist.rank_with_notes` | b: `test_sorted_by_saving_then_annual_km_and_cut_by_grant`, `test_not_positive_saving_is_left_out_with_note`, `test_every_feasible_van_off_the_list_has_a_note` | `rank`, `shortlist_note` |
| W9 | Roczne km z długości okresu, nie ze stałego mnożnika (A24) | `days_per_year` | `economics.economics` | c: `test_annual_km_scales_period_to_year`, `test_annual_km_uses_period_days_argument` | `annual_km` |
| W10 | „Blisko progu” pokazujemy zarządowi | `near_miss_range_pct`, `near_miss_days`, `at_threshold_pct` | `feasibility.assess` | b: klasy `NearThreshold` i `Thresholds` (pod, na, nad progiem) | `reject_reason`, `reason` |
| W11 | Błąd to jedna linia `ERROR:`, kod 1, bez plików (`KONSTYTUCJA.md`, sekcja 3) | — | `ev_shortlist.main` | b: `test_missing_file_is_one_error_line`, `test_missing_parameter_is_error`, `test_zero_usable_rows_is_error` · a: `test_missing_column_is_a_clear_error` | `stderr` |

## 3. Luki znalezione przy budowie macierzy

| # | Co | Skutek | Propozycja | Właściciel |
|---|---|---|---|---|
| L1 | `ev_lease_months`, `ev.Volta Cargo S.lease_pln_per_month`, `ev.Volta Cargo L.lease_pln_per_month` są w `params.csv`, ale nie czyta ich żaden plik `.py` | analityk mógł je zmienić i nie zobaczyć żadnej różnicy; po D16 wszystkie EV liczymy jako kupione | **zamknięte 13:20**: usunięte z `params.csv` (`KONTRAKT.md` 2.3); wynik na prawdziwym eksporcie identyczny przed i po. Porównanie „60 rat leasingu = 174 000 PLN” w `BOARD_NOTE.md` i `PREZENTACJA.md` ma odtąd źródło tylko w `ev_offers.md` | A |
| L2 | Żaden test nie wymienia z nazwy: `electricity_night_pln_per_kwh`, `electricity_day_pln_per_kwh`, `maintenance_diesel_pln_per_km`, `maintenance_ev_pln_per_km`, `winter_energy_uplift` | zmianę tych stawek pilnują tylko testy z obliczeniem ręcznym (`test_fuel_saving_p14_matches_hand_calculation`, `test_params_drive_the_result`), nie test „parametr zmienia wynik” | jeden test w `test_c.py`: zmiana każdej stawki zmienia `saving_pln` w oczekiwaną stronę | C |
| L3 | `winter_temp_factor`, `winter_payload_factor`, `charger_kw`, `midday_connect_minutes` działają tylko przy `midday_charging_allowed = yes`, czyli dziś nigdy | martwa ścieżka według reguły R4; nie wpływa na wynik | zostawić (przełącznik dla kolejnych kwartałów), dopisać zdanie w `RERUN.md` | B, C |
| L4 | Reguła „dotacja tylko przy zakupie” (R5) nie ma parametru ani testu — jest decyzją D16 | gdyby Ewa dopuściła leasing EV, trzeba zmienić kod, nie parametr | wystarczy wpis w `ASSUMPTIONS.md`; nie ruszać kodu przed 14:45 | C |
| L5 | `fixtures/feasibility.csv` ma nagłówek bez `reason` i `fit_models` | wzór nie odpowiada `KONTRAKT.md`, sekcja 6 (kontrakt mówi o tym wprost: „wzór uproszczony”) | zostawić; służył tylko do startu toru C | A |

Żadna z luk (ani zamknięcie L1) nie zmienia dzisiejszych liczb (8 vanów, 95 637 PLN w 5 lat).
