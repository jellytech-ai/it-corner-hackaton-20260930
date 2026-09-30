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
| | |
| 11:35 | B1 gotowe: `ev_shortlist.py` (CLI, potok, 4 pliki) z zaślepkami A/B/C wyłączającymi się, gdy pojawi się `data.py`/`feasibility.py`/`economics.py`; testy w `tests/test_b.py` |
