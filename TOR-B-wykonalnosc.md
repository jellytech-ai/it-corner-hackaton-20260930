# TOR B — Wykonalność, ranking, eksport

Najpierw przeczytaj: `KONTRAKT.md`, potem `HANDOFF.md` sekcje 3, 6 i 8.

## Cel

Dla każdego vana rozstrzygnąć, czy i jakim EV da się go zastąpić, ułożyć ranking i zapisać pliki w formacie Ewy. Jesteś też integratorem: scalasz gałęzie i pilnujesz, że całość działa jednym poleceniem.

## Twoje pliki

`feasibility.py`, `ev_shortlist.py`, `tests/test_b.py`, ten plik.

## Dane na start

Do czasu scalenia toru A (12:20) czytaj `fixtures/van_profile.csv` i `fixtures/clean_trips.csv` — mają dokładnie format z kontraktu.

## Zadania

| # | Do kiedy | Zadanie | Gotowe, gdy |
|---|---|---|---|
| B1 | 11:45 | szkielet `ev_shortlist.py`: argumenty CLI, wywołanie funkcji torów w kolejności A → B → C, zapis czterech plików | działa na plikach testowych z zaślepką ekonomii |
| B2 | 12:05 | `assess`, filtry podstawowe: chłodnia, ładowność, zasięg zimowy na najgorszym dniu, punkty ładowania w bazie | dla vanów jednozmianowych wynik zgodny z `fixtures/feasibility.csv` |
| B3 | 12:20 | dobór modelu: najtańszy model, który przechodzi ładowność i zasięg | P-26 i P-14 → Cargo S |
| B4 | 12:20 | niezależne przeliczenie liczb kontrolnych toru A inną metodą (np. `sort -u` + `awk`) | 2777 / 344952 / 38 potwierdzone |
| B5 | 12:30 | **M1:** scalenie gałęzi, uruchomienie, częściowe `shortlist.csv` i `summary.csv` do wątku | pliki w formacie Ewy, nawet jeśli `saving_pln` jest jeszcze wstępne |
| B6 | 13:00 | symulacja doładowania między trasami (A16) dla dni z dwiema trasami; `midday_charging`, `day_tariff_share` | P-08 i P-12: 0 dni nieudanych na Cargo S; P-09: 2 dni na Cargo L |
| B7 | 13:30–14:00 | odpowiedzi Ewy: limit punktów, EV w North za diesla z South, próg zimowy — przez `params.csv` | ponowne uruchomienie |
| B8 | 14:30 | `sensitivity`: progi 0,50 / 0,57 / 0,65 — ile vanów przechodzi i które | tabela do notatki dla C |
| B9 | 14:30 | lista „blisko progu” (do 10% ponad zasięg albo 1–3 dni ponad ładowność) | kolumna `reason` / `reject_reason` to opisuje |
| B10 | 14:45 | ranking końcowy i zamrożenie liczb | `shortlist.csv` i `summary.csv` ostateczne |
| B11 | 15:15–15:40 | zip narzędzia do wątku; przygotowanie demo (3 kroki z HANDOFF sekcja 9) | demo przechodzi na czysto |

## Reguły (wszystkie wartości z `params.csv`)

- **Zasięg zimowy** = `ev.<model>.range_wltp_km` × `winter_range_factor`.
- **Ładowność**: `max_load_kg` ≤ `ev.<model>.payload_kg`; limit twardy (D3).
- **Chłodnie**: odrzucone, gdy `exclude_refrigerated = yes` (D1).
- **Baza**: `ev_depot` = baza vana; liczba EV w bazie ≤ `chargers.<baza>`; razem ≤ `max_evs_grant`.
- **Doładowanie między trasami**: przyrost km = godziny przerwy (minus `midday_connect_minutes`) × `charger_kw` ÷ zużycie zimowe, gdzie zużycie zimowe = `kwh_per_100km` ÷ 100 ÷ (`winter_temp_factor` × `winter_payload_factor`). Warunek: trasa 1 ≤ zasięg zimowy i stan po doładowaniu ≥ trasa 2, **w każdym dniu** z danych.
- **Ranking**: wykonalne vany malejąco po `saving_pln` z toru C; remis — malejąco po `annual_km`. Limit punktów ucina listę.

## Decyzje do podjęcia w tym torze

| # | Pytanie | Propozycja domyślna |
|---|---|---|
| 1 | Van dokładnie na progu zasięgu (P-14: 148,0 km przy 148,2) | przechodzi; opisać w `reason` jako „na progu” |
| 2 | Co wpisać w `range_check_km` przy doładowaniu między trasami | suma km najgorszego dnia; w założeniach dopisać, że porównanie jest per trasa |
| 3 | Czy vany z South pokazywać w `shortlist.csv` | nie, dopóki Ewa nie odpowie na pytanie 1; są w `all_vans.csv` z powodem |
| 4 | Czy stosować limit 6 punktów, gdy vany dwuzmianowe ładują się też w dzień | tak, jeden punkt na van |

## Czego nie robisz

Czyszczenia danych, kosztów i oszczędności, dokumentów.

## Dziennik

| Godzina | Decyzja / zdarzenie |
|---|---|
| 11:35 | B1 gotowe: `ev_shortlist.py` (CLI, potok, 4 pliki) z zaślepkami A/B/C wyłączającymi się, gdy pojawi się `data.py`/`feasibility.py`/`economics.py`; testy w `tests/test_b.py` |
| 11:29 | B2 gotowe: `feasibility.assess` — chłodnia, ładowność, zasięg zimowy najgorszego dnia, punkty w bazie; zgodne z całym `fixtures/feasibility.csv`. Reguła wyboru: `ev_model` = najtańszy model (po `price_pln`) spełniający ładowność i zasięg; gdy żaden nie pasuje, `reject_reason` wymienia braki najtańszego modelu. Porównania z tolerancją 1e-9 (260 × 0,57 w float = 148,20000000000002). Chłodnie: `ev_model` puste. |
| 11:30 | B3 gotowe: dobór modelu = najtańszy po `price_pln` spełniający ładowność i zasięg (P-26, P-14 → Cargo S; P-08 bez doładowania → Cargo L). Test, że kolejność idzie z `params.csv`. |
| 11:30 | B4 gotowe: liczby kontrolne potwierdzone niezależnie z surowego `trips.csv` (bez Pythona): 2999 wierszy surowych → **2777 / 344952 / 38**. Polecenie niżej. Uwaga: przy regule „wartość bezwzględna” dla P-27 13.08 `total_km` byłoby 345070 (+118) — liczba zależy od decyzji toru A. |

```sh
tail -n +2 trips.csv | LC_ALL=C sort -u | LC_ALL=C awk -F, '
  { km = ($5 == "" || $5 <= 0) ? $6 : $5; tot += km; n++
    v = ($2 == "P-17") ? "P-17B" : $2; vans[v] = 1 }
  END { printf "trips_counted=%d total_km=%.0f vans=%d\n", n, tot, length(vans) }'
```
| 11:32 | B6 gotowe (przed B5 — scalenie czeka na gałęzie A i C o 12:20): symulacja A16 w `feasibility.py` (`van_days`, `simulate_day`, `failed_days`). Odtworzone wszystkie liczby z HANDOFF sekcja 8: P-08/P-12 Cargo S 0 dni, P-09 S 26 / L 2, P-36 S 11 / L 0, P-24 S 43 / L 9. Wynik: P-08 → Cargo S z doładowaniem (`day_tariff_share` 0,484); P-12 → Cargo S, ale South bez ładowarek. `range_check_km` przy doładowaniu = dłuższa trasa najgorszego dnia (za KONTRAKT 6; P-08: 104,8). Doładowanie w przerwie liczone do pełna, maks. tyle, ile zużyła trasa 1. |
| 11:32 | B8 gotowe: `feasibility.sensitivity(profile, trips, params, factors)`. Tabela dla C (dane z fixtures): |

| Próg | Zasięg S / L | Wykonalne (North) | Pasują technicznie (także South) |
|---|---|---|---|
| 0,49 | 127,4 / 186,2 | 0 | 0 |
| 0,50 | 130,0 / 190,0 | 1: P-08 (Cargo L, 190,0 km — dokładnie na progu) | 1 |
| **0,57** | 148,2 / 216,6 | **3: P-08, P-14, P-26** | 8: + P-05, P-10, P-12, P-20, P-25 |
| 0,65 | 169,0 / 247,0 | 8: P-04, P-08, P-13, P-14, P-21, P-26, P-28, P-30 | 15: + P-05, P-10, P-12, P-20, P-25, P-31, P-32 |

| 11:35 | Uwaga: commit B6 (`f52d8c4`) zawierał tylko dziennik — Cursor nadpisał `feasibility.py` i `tests/test_b.py` nieaktualnym buforem przed `git add`. Kod B6 odtworzony w `08808c7`. Od teraz po każdym commicie sprawdzam `git show --stat`. |
| 11:35 | B9 gotowe: vany niewykonalne mają w `reject_reason` dopisek `near threshold: <model> …` (zasięg ≤ 10% ponad próg, 1–3 dni ponad ładowność albo 1–3 dni nieudane z doładowaniem). Nowa kolumna `reason` (poza KONTRAKT 6, trafia do `all_vans.csv` i `shortlist.csv`): zapas zasięgu, `at threshold` przy zapasie < 1% (P-14: 0,2 km; P-25: 0,0 km), albo „midday charging”. Blisko progu: North — P-13 (+0,4%), P-04 (+1,8%), P-21 (+7,0%), P-28 (+8,2%), P-06 i P-02 (1 dzień ładunku), P-22 (2 dni + 1,1%), P-11 (3 dni), P-09 (Cargo L, 2 dni nieudane); South — P-32, P-31, P-18, P-27. |
| 11:35 | Przygotowanie B7: `rank` ucina też po `chargers.<baza>` (decyzja 4: jeden punkt na van), limit dotacji z `max_evs_grant` bez domyślnej wartości w kodzie. Przy progu 0,65 wykonalnych w North jest 8 > 6 punktów → na liście 6. |
| 11:37 | Próba B5 (lokalnie, bez pushu): `tor-b` + `origin/tor-a` (5ff97af) + `origin/tor-c` (c54b3de) scalają się bez konfliktów; testy A/B/C zielone; pełny przebieg na surowych danych: 2777 / 344952 / 38, shortlista P-08 (29 204), P-26 (21 353), P-14 (13 995), `saving_pln` razem 64 552, `annual_fuel_saving_pln` 43 566. Poprawki po próbie: tryb `--fixtures` (testy B na plikach testowych nie mogą iść przez czyszczenie A), zaokrąglanie km i kwot przy eksporcie (C zwraca float), `.gitignore` + usunięcie `.pyc` z repo. Test `PipelineOnSourceData` czyta dane z `EV_SOURCE_DIR` albo `../it-corner-hackathon-20260930/`. |
| 11:44 | Scalony `origin/devel` (06d2d83) do `tor-b-wykonalnosc` bez konfliktów; testy A/B/C zielone. Godziny wpisów powyżej poprawione na rzeczywiste (wcześniej wpisane terminy z harmonogramu). |
| 11:48 | Dostosowanie do `KONSTYTUCJA.md` (64b3964): sekcja 12 poz. 1–4, 6, 9 usunięte — komunikaty i `--help` po angielsku, `ERROR: …` na stderr + kod 1 bez plików wynikowych, raport + liczby kontrolne + liczba vanów + katalog na ekranie, zero wierszy = `ERROR`, docstringi po angielsku. Poza sekcją 12: sumy w `summary.csv` z zaokrąglonych wierszy (`math.fsum`), odczyt `utf-8-sig`, `param()` z komunikatem `Missing parameter '<klucz>' in params.csv` (także `chargers.<baza>`, `exclude_refrigerated`, `ev.<model>.<pole>`), zaślepki usunięte (zostaje tryb `--fixtures` z `load_fixtures`), „near threshold” → „near miss” (słownik), testy progów pod / na / nad. Błąd znaleziony przy analizie: van z rejestru bez kursów (`worst_day_km = 0`) przechodził filtry — teraz `feasible = no`, `reject_reason = no trips in this export`. Progi near miss dopisane do `params.csv` (4c4391c) — plik toru A, patrz Q10. |

### Nowe komunikaty dla `RERUN.md` (KONSTYTUCJA 3 → tor C, C10)

| Komunikat / objaw | Co zrobić |
|---|---|
| `ERROR: Trips file <ścieżka>: no usable trip rows; nothing written. Check that it is the telematics export` | sprawdzić, czy podano właściwy plik; `data_report` nie powstaje |
| `ERROR: Missing parameter '<klucz>' in params.csv` (m.in. `near_miss_range_pct`, `near_miss_days`, `at_threshold_pct`, `chargers.<baza>` dla nowej bazy) | dopisać wiersz do `params.csv` |
| `reject_reason` = `no trips in this export` | van jest w rejestrze, ale nie jeździł w tym eksporcie (towarzyszy mu `WARNING` z `data.py`) |
| `reject_reason` zawiera `near miss: <model> …` | van blisko progu — kandydat do rozmowy, nie do listy |
| `reason` = `at threshold: …` | van przechodzi dokładnie na progu (zapas < `at_threshold_pct`) |
| 12:14 | Scalony `origin/devel` (5ec7255) z regułami Ewy od toru A (KONTRAKT 10). Odpowiedzi Ewy przeczytane u źródła (Discussions, wątek „9” i wątki innych zespołów): 95. percentyl dnia w 60% WLTP; dwuzmianowe „no time to charge. Count their whole day”; North 10 punktów, do 3 vanów z South w North; dla każdego vana model „which works out better over the five years”; ładunek — najcięższy z danych |
| 12:17 | B7 gotowe (494b32f). Zasięg na `range_day_km`; doładowanie tylko przy `midday_charging_allowed = yes` (kod A16 zostaje, wyłączony parametrem); van z South bez ładowarek → `ev_depot = North`, `reason` „South van based at North, routes unchanged”; `choose_models` liczy `economics()` toru C dla każdego pasującego modelu i bierze wyższy `saving_pln` (remis → tańszy), więc zadziała też po zmianie wzoru C na 5 lat. Wynik na surowych danych: 15 vanów pasuje (8 North, 7 South, zgodnie z podglądem A); P-08 i P-12 tylko Cargo L. Shortlista przy obecnej ekonomii C (roczna, wszystkie dodatnie): P-12, P-08, P-30, P-25, P-21, P-05, P-13, P-26, P-04, P-14; poza listą z notatką: P-20, P-31, P-32 (limit 3 vanów z South), P-10, P-28 (limit 10). Błąd znaleziony przy okazji: `load_fixtures` zostawiało `max_load_kg` kursów jako tekst, więc profil przebudowany w trybie `--fixtures` brał maksimum leksykograficzne — poprawione |
| 12:17 | Decyzje B (do rejestru C): (1) na shortlistę trafia tylko van z `saving_pln` > 0 — Ewa: zarząd patrzy na wynik w 5 lat; ujemny = EV kosztuje więcej; (2) miejsca dla vanów z South w North rozdaje ranking (najwyższy `saving_pln` wygrywa); (3) rank 1 = największy `saving_pln` (Ewa innym zespołom: „choose and write it down”); (4) lista ucięta na `max_evs_grant` (10), także dla leasingu — równa się liczbie punktów w North; (5) wykonalny van spoza listy ma w `all_vans.csv` kolumny `shortlisted = no` i `shortlist_note` z powodem |

Wrażliwość według nowych reguł (95. percentyl, bez doładowania, bez limitów listy):

| Próg | Zasięg S / L | Pasują (North + South) |
|---|---|---|
| 0,50 | 130,0 / 190,0 | 2: P-08, P-10 |
| 0,57 | 148,2 / 216,6 | 14: bez P-21 |
| **0,60** | 156,0 / 228,0 | **15**: P-04, P-05, P-08, P-10, P-12, P-13, P-14, P-20, P-21, P-25, P-26, P-28, P-30, P-31, P-32 |
| 0,65 | 169,0 / 247,0 | 15 (P-16: 169,5 km — 0,5 km za progiem) |

Near miss przy 0,60: ładunek — P-02, P-06, P-18 (1 dzień), P-22, P-27 (2), P-11 (3); zasięg — P-16 (+8,7%).

### Nowe komunikaty dla `RERUN.md` (B7)

| `all_vans.csv`, kolumna | Treść | Znaczenie |
|---|---|---|
| `reason` | `…; South van based at North, routes unchanged` | van z South stacjonuje w North (limit `max_south_vans_at_north`) |
| `shortlist_note` | `saving over the horizon is not positive` | EV kosztuje więcej niż oszczędza |
| `shortlist_note` | `grant limit of 10 EVs reached` | lista pełna (`max_evs_grant`) |
| `shortlist_note` | `all N charging points at <baza> taken` | brak wolnego punktu (`chargers.<baza>`) |
| `shortlist_note` | `limit of N vans based away from their depot reached` | wyczerpany limit vanów z South |
| `fit_models` | lista modeli, które przechodzą filtry | `ev_model` = ten z wyższym `saving_pln` |
| 12:18 | Sprawdzenie demo (B11) na `devel` 2c169b0. Krok 3 (świeży eksport `fixtures/fresh_trips.csv` + `vans.csv`): kod 0, trzy `WARNING` (P-39, ujemny licznik P-13, odrzucony wiersz P-21), okres 41 dni, 1310 kursów / 161 957 km, lista 10 vanów. **Krok 2 z `PREZENTACJA.md` (0,57 → 0,65) jest nieaktualny**: bazą jest 0,60, a 0,65 daje tę samą listę. Wyniki zmiany jednego parametru na surowych danych (ekonomia C roczna): |

| Zmiana w `params.csv` | Shortlista | `saving_pln` razem |
|---|---|---|
| bez zmian (0,60, 95. percentyl) | 10: P-12, P-08, P-30, P-25, P-21, P-05, P-13, P-26, P-04, P-14 | 236 863 |
| `winter_range_factor` 0,65 | bez zmian | 236 863 |
| `winter_range_factor` 0,55 | 7: P-12, P-08, P-05, P-20, P-26, P-14, P-28 | 156 335 |
| `winter_range_factor` 0,50 | 2: P-08, P-10 | 43 690 |
| `range_check_percentile` 100 (najgorszy dzień, reguła Witolda) | 8: bez P-30, P-21 | 187 632 |
| `max_south_vans_at_north` 0 | 8: tylko North | 171 305 |

| 12:19 | Scalony `devel` d941b2e (tor C: D13 — `saving_pln` w 5 lat, D14 — `saving_for_model`). `choose_models` używa teraz `economics.saving_for_model`. **B10: ranking końcowy** na surowych danych: 8 vanów — P-12 (L, z South), P-30, P-21, P-08 (L), P-05 (z South), P-25 (z South), P-13, P-04; `saving_pln` razem **95 637 PLN w 5 lat**, `annual_fuel_saving_pln` 136 092 PLN/rok — zgodne z kontrolą toru C. Poza listą z notatką: P-14, P-26, P-10, P-20, P-28, P-32 (wynik w 5 lat ≤ 0), P-31 (+1 589 PLN, ale limit 3 vanów z South). Lista i suma przypięte w teście `PipelineOnSourceData` — zmiana wymaga wpisu tutaj (jak liczby kontrolne). Formalne zamrożenie o 14:45 |
| 12:19 | Demo po D13 (zastępuje tabelę powyżej): świeży eksport — kod 0, 7 vanów, 96 359 PLN. Zmiana jednego parametru na surowych danych: |

| Zmiana w `params.csv` | Shortlista | `saving_pln` (5 lat) |
|---|---|---|
| bez zmian | 8: P-12, P-30, P-21, P-08, P-05, P-25, P-13, P-04 | 95 637 |
| `winter_range_factor` 0,65 | bez zmian | 95 637 |
| `winter_range_factor` 0,55 | 3: P-12, P-08, P-05 | 47 897 |
| `winter_range_factor` 0,50 | 1: P-08 | 15 270 |
| `range_check_percentile` 100 (najgorszy dzień) | 6: bez P-30, P-21 | 59 482 |
| `max_south_vans_at_north` 0 | 5: P-30, P-21, P-08, P-13, P-04 | 56 414 |

| 12:20 | B11 próba na sucho: zip z plikami wymienionymi w `RERUN.md` („What is in the folder”), rozpakowany w pustym katalogu z `trips.csv` i `vans.csv`, polecenie z kroku 3 `RERUN.md` bez zmian → kod 0, 8 vanów; `shortlist.csv`, `summary.csv`, `all_vans.csv`, `data_report.txt` bajt w bajt jak z repo. Zip nie trafia do repo (`.gitignore`); budujemy go po zamrożeniu (14:45) poleceniem niżej. Uwaga dla C: po uruchomieniu w folderze analityka powstaje `__pycache__/` — można wspomnieć w `RERUN.md`, że to normalne |

```sh
zip -j ev_shortlist_tool.zip ev_shortlist.py data.py feasibility.py economics.py params.csv RERUN.md ASSUMPTIONS.md
```
| 12:30 | Scalony `devel` a4bc375: tor C rozstrzygnął Q14, Q15, Q17, Q20, Q22 (A23, A24, D15, D16) — wszystkie zgodne z tym, co już jest w kodzie B; bez zmian w kodzie. `RERUN.md` wymienia `RERUN.md` w spisie zipa i wyjaśnia `__pycache__`. Otwarte pytania B: Q1, Q2, Q10, Q11/Q18/Q21 (kontrakt — tor A), Q23 (demo — tor C) |
| 12:32 | Scalony `devel` e66e30a: tor A zaakceptował progi near miss (Q10) i dopisał `reason`, `fit_models`, `shortlisted`, `shortlist_note` do KONTRAKT 6–7 (Q11, Q18, Q21); kolejność kolumn zgodna z kodem — pilnuje jej nowy test `test_all_vans_columns_in_contract_order`. Kontrola krzyżowa A: 8 vanów / 95 637 PLN identyczne z niezależnym obliczeniem |
| 12:35 | Scalony `devel` 2c68aef (tor C: `BOARD_NOTE.md`, demo krok 2 = percentyl 100 — Q23 rozwiązane). Liczby w `BOARD_NOTE.md` sprawdzone uruchomieniem narzędzia: shortlista i kwoty 8 vanów, sumy 136 092 / 95 637, warianty 59 482 (percentyl 100), 47 897 (0,55), 38 575 (0,52), 56 414 (bez South) — wszystkie zgodne. **B11: testowy zip i demo przygotowane** poza repo w `../demo/` (obok worktree): `ev_shortlist_tool.zip`, `tool/` (rozpakowany zip + `trips.csv`, `vans.csv`, `fresh_trips.csv`, `params_p100.csv`), `demo_backup/` (wyniki i ekran każdego kroku + przypadek `ERROR`), `DEMO.md` (ściąga z poleceniami i oczekiwanymi wynikami). Wszystkie 3 kroki zgodne z `PREZENTACJA.md`. Zip do wątku — po zamrożeniu 14:45, tym samym poleceniem |
| 12:43 | Decyzja B (Q2): gdy żaden model nie pasuje, `reject_reason` wymienia braki najtańszego modelu — zgodne ze wzorem `fixtures/feasibility.csv` i krótsze dla analityka; informację o drugim modelu daje dopisek `near miss`, gdy van jest blisko progu. Q1 i Q4 zamknięte (odpowiedź Ewy, D8). Wszystkie pytania toru B rozstrzygnięte |

## Pytania na koniec pracy

| # | Pytanie | Stan / domyślnie |
|---|---|---|
| Q1 | Chłodnia: wpisywać `ev_model`, jeśli technicznie pasuje? Wpływa na to, czy C liczy dla niej ekonomię w `all_vans.csv` | rozwiązane przez Ewę: „Refrigerated vans are out for year 1” — `ev_model` puste, bez ekonomii |
| Q2 | `reject_reason` przy braku modelu: braki najtańszego modelu (zgodne ze wzorem) czy braki każdego modelu osobno (np. P-04: „S: range; L: payload”)? | decyzja B (12:43): braki najtańszego modelu (zgodne ze wzorem, krótsze); drugi model pokazuje dopisek `near miss` |
| Q3 | P-14 „na progu” (decyzja 1): opis ląduje w `reason` dopiero w B9, bo wzór ma puste `reject_reason` dla wykonalnych | rozwiązane: `at threshold` w kolumnie `reason` (B9) |
| Q4 | P-27 13.08 (licznik −208,6): GPS 90,3 (344952) czy wartość bezwzględna (345070)? Decyzja toru A; B potwierdził obie wersje | rozwiązane: D8 w HANDOFF (licznik ≤ 0 → GPS z ostrzeżeniem); Ewa: „nasza decyzja” — 344 952 km |
| Q5 | `day_tariff_share`: doładowanie w przerwie do pełna (P-08 0,484, P-12 0,476) czy tylko brakujące km (0,112 / 0,153)? Różnica ok. 0,34 PLN/kWh na ~1/3 energii — ważne dla C | nieaktualne po A21 (bez doładowania) |
| Q6 | `range_check_km` przy doładowaniu: KONTRAKT 6 mówi „dłuższa z dwóch tras”, decyzja 2 w tym pliku mówi „suma km najgorszego dnia”. Wdrożone wg KONTRAKTU — C musi to opisać w `ASSUMPTIONS.md` | nieaktualne po A21 (bez doładowania `range_check_km` = `range_day_km`) |
| Q7 | A16: czy vany dwuzmianowe faktycznie wracają do bazy między trasami? Dane pokazują tylko godziny (HANDOFF 8) | rozwiązane przez Ewę: nie wracają na ładowanie (A21) |
| Q8 | Wrażliwość zmienia tylko `winter_range_factor`; zużycie zimowe w symulacji A16 (`winter_temp_factor` × `winter_payload_factor` = 0,63) zostaje stałe. Czy te dwa współczynniki mają być spójne (0,57 vs 0,63)? | nieaktualne po A21 |
| Q9 | `.gitignore` i usunięcie `.pyc` | rozwiązane w `devel` (1d43542) |
| Q10 | Tor B dopisał do `params.csv` (plik toru A) `near_miss_range_pct,10`, `near_miss_days,3`, `at_threshold_pct,1` w osobnym commicie 4c4391c — tor A ma zaakceptować albo przenieść | rozwiązane 12:35: zaakceptowane przez A (KONTRAKT 11) |
| Q11 | Kolumna `reason` w `feasibility` wykracza poza KONTRAKT 6 — dopisać ją do kontraktu (C nie musi jej używać) | rozwiązane 12:35: KONTRAKT 6 |
| Q12 | Język opisów w `reason`/`reject_reason` | rozwiązane: KONSTYTUCJA 2 — angielski |
| Q13 | P-25 (South) jest dokładnie na progu (148,2 = 148,2) — gdyby Ewa pozwoliła na EV z South w North, to kandydat najbardziej ryzykowny | nieaktualne po A19 (0,60, 95. percentyl) |
| Q14 | `annual_km` (tor C) = km z okresu ÷ 90 dni kalendarzowych × 365, niezależnie od liczby dni pracy (P-08: 11 670 km → 47 329 km/rok). Czy to zamierzone (vany jeżdżą też w weekendy/dni bez danych)? | rozwiązane 12:29: A24 |
| Q15 | Raport A: „gps_km missing: 15” po deduplikacji vs 17 w HANDOFF sekcja 4 (surowe) — ujednolicić opis w `HANDOFF.md` | rozwiązane 12:29: HANDOFF 4 poprawiony |
| Q16 | Scalenie B5 do `devel` (dawniej `handoff-wstepna-analiza`) i push — wymaga zgody (gałąź wspólna) | rozwiązane 11:54: scalone i wypchnięte |
| Q17 | KONSTYTUCJA 12 poz. 1–4, 6, 9: tor B zrobił swoją część — właściciel konstytucji ma zaktualizować status w tabeli | rozwiązane 12:29: KONSTYTUCJA 12 zaktualizowana przez C |
| Q18 | Kolumna `reason` jest w `feasibility`, `all_vans.csv` i `shortlist.csv`, ale nie ma jej w KONTRAKT 6 (tabela `feasibility`) — KONSTYTUCJA 5 wymaga kolejności kolumn „dokładnie jak w KONTRAKT” | rozwiązane 12:35: KONTRAKT 6 |
| Q19 | Tor C: `saving_pln` nadal roczny (D7) — po zmianie na 5 lat z ceną EV, dotacją i opłatą za leasing shortlista się zmieni (podgląd A: P-26 i P-14 na minus). `choose_models` i ranking działają bez zmian w B | rozwiązane 12:17: D13 |
| Q20 | Dotacja tylko przy zakupie: czy `saving_pln` liczy zakup dla wszystkich vanów z listy? Wtedy limit 10 z dotacji = limit listy; przy leasingu limit dotacji nie dotyczy | rozwiązane 12:29: D16 — wszystkie EV kupione, limit dotacji = limit listy |
| Q21 | Kolumny `fit_models`, `shortlisted`, `shortlist_note` i `range_day_km` w `all_vans.csv` — dopisać do KONTRAKT 6/7 | rozwiązane 12:35: KONTRAKT 6 i 7 |
| Q22 | Które vany z South trafiają do North: teraz trzy z najwyższym `saving_pln`. Alternatywa: najbliższe końca leasingu. Zapisać w założeniach | rozwiązane 12:29: A23 |
| Q23 | Demo krok 2 (`PREZENTACJA.md`, plik toru C): zamienić 0,57 → 0,65 na `range_check_percentile` 95 → 100 („najgorszy dzień zamiast 95. percentyla: 10 → 8 vanów”) albo `winter_range_factor` 0,60 → 0,55. Po D13: percentyl 100 daje 8 → 6 vanów (95 637 → 59 482 PLN); 0,55 daje 8 → 3 | rozwiązane: tor C zmienił krok 2 na percentyl 100 (a5fb2e4) |
