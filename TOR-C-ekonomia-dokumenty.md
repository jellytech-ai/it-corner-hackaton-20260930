# TOR C — Ekonomia i dokumenty

Najpierw przeczytaj: `KONTRAKT.md`, potem `HANDOFF.md` sekcje 1, 2, 6 i 9.

## Cel

Policzyć dla każdego vana roczne km i oszczędności, a potem napisać wszystko, co Ewa i zarząd przeczytają: notatkę, założenia, instrukcję. Jesteś też właścicielem `HANDOFF.md` i rejestru decyzji.

## Twoje pliki

`economics.py`, `tests/test_c.py`, `RERUN.md`, `BOARD_NOTE.md`, `ASSUMPTIONS.md`, `HANDOFF.md`, `PREZENTACJA.md`, ten plik.

## Dane na start

`fixtures/van_profile.csv` i `fixtures/feasibility.csv` (uproszczony wzór; prawdziwy wynik da tor B o 12:20).

## Zadania

| # | Do kiedy | Zadanie | Gotowe, gdy |
|---|---|---|---|
| C1 | 11:40 | **decyzja o podstawie `saving_pln`** (patrz niżej) — uzgodnić z zespołem | zapisane w dzienniku i w `saving_basis` |
| C2 | 12:00 | `annual_km` = `km_period` × `days_per_year` ÷ `period_days` | P-26: 8580 km × 365 ÷ 90 ≈ 34 797 km |
| C3 | 12:15 | `annual_fuel_saving_pln` = koszt diesla − koszt ładowania | test na jednym vanie policzonym ręcznie |
| C4 | 12:20 | wypchnięcie gałęzi `tor-c` z `economics` zwracającym oba pola | B scala na M1 |
| C5 | 13:00 | `saving_pln` według uzgodnionej podstawy; `saving_basis` jako jedno zdanie po angielsku | suma po shortliście zgadza się z `summary.csv` |
| C6 | 13:00 | szkic `RERUN.md` (EN) | 5–7 kroków, bez odwołań do nas |
| C7 | 13:30–14:00 | odpowiedzi Ewy (dotacja, wyjście z leasingu, los diesla) → parametry i formuła; wpis do `HANDOFF.md` sekcja 10 | ponowne uruchomienie |
| C8 | 14:45 | `BOARD_NOTE.md` (EN, 1 strona): rekomendacja, liczby, dlaczego nie „te, co jeżdżą najwięcej”, ryzyko zimy, wrażliwość, co dalej | liczby z zamrożonego uruchomienia |
| C9 | 15:15 | `ASSUMPTIONS.md` (EN): założenia A1–A17 i decyzje D1–D5 z godzinami, plus „co byśmy zapytali dalej” | zgodne z `HANDOFF.md` |
| C10 | 15:15 | `RERUN.md` poprawiony po teście toru A | A potwierdza |
| C11 | 15:40 | komplet dokumentów w wątku; plan prezentacji (kto mówi co) | — |

## Formuły (wszystkie wartości z `params.csv`)

- **Koszt diesla / rok** = `annual_km` × `fuel_l_per_100km.<model>` ÷ 100 × `diesel_price_pln_per_l`
- **Koszt ładowania / rok** = `annual_km` × `ev.<model>.kwh_per_100km` ÷ 100 × `winter_energy_uplift` × cena, gdzie cena = (1 − `day_tariff_share`) × nocna + `day_tariff_share` × dzienna
- **Oszczędność na serwisie / rok** = `annual_km` × (`maintenance_diesel_pln_per_km` − `maintenance_ev_pln_per_km`)

Przykład kontrolny, P-14 (Brona D35 Long → Cargo S, 5623 km w 90 dni):
`annual_km` ≈ 22 804; diesel ≈ 12 926 PLN; ładowanie ≈ 3 492 PLN; **oszczędność na paliwie ≈ 9 434 PLN**; serwis ≈ 4 561 PLN.

## Decyzja C1 — podstawa `saving_pln` (najważniejsza w tym torze)

> **Rozstrzygnięte 11:26: wariant 1** (tylko eksploatacja, rocznie) — decyzja D7 i założenie A15 w `HANDOFF.md`. Nowe parametry nie są potrzebne. Poniżej zostaje analiza, na podstawie której wybieraliśmy.

Problem: oszczędność na paliwie i serwisie to ok. 14 000 PLN rocznie na van, a leasing Cargo S kosztuje 34 800 PLN rocznie. Liczona „wprost” wymiana jest na minusie dla każdego vana. Wynik zależy od tego, **z czym porównujemy**.

| Wariant | Co wliczamy | Uwaga |
|---|---|---|
| 1. Tylko eksploatacja | paliwo + serwis, rocznie | proste i sprawdzalne, ale pomija koszt EV, o który zarząd zapyta |
| 2. Pełny koszt, 5 lat | (paliwo + serwis) × 5 − 60 rat leasingu EV + uniknięte raty diesla do końca jego leasingu | uczciwe; vany własne wychodzą na minusie bez dotacji |
| 3. Wymiana i tak konieczna | jak wariant 2, ale diesel z kończącym się leasingiem lub stary (np. rocznik do 2018) i tak byłby zastąpiony nowym dieslem w leasingu | najbliższe rzeczywistości, wymaga założenia o racie nowego diesla (w danych: 2390–3240 PLN/mies.) |

Propozycja: **wariant 2 jako `saving_pln`**, z dotacją jako osobnym parametrem (`grant_pln_per_van`, domyślnie 0 do odpowiedzi Ewy), a w notatce jedno zdanie o wariancie 3. `annual_fuel_saving_pln` pozostaje czystą różnicą paliwo − ładowanie, zgodnie z definicją Ewy.

Nowe parametry zgłoś torowi A (właściciel `params.csv`): `grant_pln_per_van`, `saving_horizon_years`, ewentualnie `diesel_resale_pln`, `lease_exit_share`.

## Rejestr decyzji

Zbierasz wpisy z dzienników w `TOR-A-dane.md` i `TOR-B-wykonalnosc.md` przy każdym scaleniu (12:20, 13:50, 14:45) i przenosisz do `HANDOFF.md` sekcje 6 i 10.

## Czego nie robisz

Czyszczenia danych, filtrów, rankingu, zapisu plików wynikowych.

## Dziennik

| Godzina | Decyzja / zdarzenie |
|---|---|
| 11:25 | Start toru C na gałęzi `tor-c`. C2 i C3 gotowe: `economics()` zwraca `annual_km` i `annual_fuel_saving_pln`; test kontrolny P-14 = 9 434 PLN zgodny. P-26: 8579,7 km → 34 795 km (w tabeli zadań 34 797 z zaokrąglonych 8580 km) |
| 11:25 | `economics()` zwraca wiersz dla każdego vana z `van_profile`; bez `ev_model` pola kwot są puste (`""`) — B łączy bez uzupełniania braków. `saving_pln` puste do decyzji C1 |
| 11:26 | **C1: wariant 1** — `saving_pln` = paliwo − ładowanie + (0,34 − 0,14) PLN/km × `annual_km`; bez leasingu, zakupu i dotacji (D7, A15). P-14: 13 995 PLN/rok. `saving_basis()` gotowe. Nowych parametrów dla toru A brak |
| 11:31 | `tor-c` wypchnięte (C4 gotowe przed 12:20) |
| 11:33 | C6: szkic `RERUN.md` (6 kroków + rozwiązywanie problemów). Do sprawdzenia po scaleniu: komunikaty „missing column” (A) i zawartość ekranu (B). `economics()` przy braku parametru rzuca `ValueError` z nazwą klucza i `params.csv` — **prośba do A i B o ten sam styl komunikatów** |
| 11:35 | C9: szkic `ASSUMPTIONS.md` (EN) z A1–A17, D1–D7 i 7 pytaniami „co byśmy zapytali dalej” (5 z listy do Ewy + powrót dwuzmianowych do bazy + historia serwisu). A13 i A14 bez godziny, jak w `HANDOFF.md` |
| 11:37 | Rejestr: decyzje toru A (11:25–11:35) przeniesione do `HANDOFF.md` jako A5 (przyjęte) i D8–D11; to samo w `ASSUMPTIONS.md`. `RERUN.md` krok 5 zgodny z raportem `data.py` (linie `WARNING`) |
| 11:40 | Scalone `handoff-wstepna-analiza` (A + B) do `tor-c`; 56/56 testów OK. Pełny potok na `trips.csv`: 2777 / 344952 / 38, shortlista P-08, P-26, P-14. **C5 potwierdzone:** suma po shortliście = `summary.csv` (paliwo 43 566, `saving_pln` 64 552 PLN/rok). P-08 z taryfą dzienną 0,484 → paliwo 19 738 zamiast 20 888 z fixtures. Q5 i Q6 toru B opisane w `ASSUMPTIONS.md` (A16) |
| 11:41 | Szkic zasad komunikatów w `KONTRAKT.md` sekcja 10; `RERUN.md` opisuje `ERROR:` i `WARNING:` |
| 11:42 | Scalone `tor-c` → `handoff-wstepna-analiza`. Równolegle powstał `KONSTYTUCJA.md` (D12) — sekcja 10 w `KONTRAKT.md` zamieniona na odsyłacz, żeby nie było dwóch wersji |
| 11:44 | `KONSTYTUCJA.md`: dopisana zasada „nowy komunikat → wiersz w `RERUN.md`” i brak liczb na sztywno w komunikatach; niezgodność 5 rozwiązana. `RERUN.md` i `ASSUMPTIONS.md` zgodne ze słownikiem (check figures, near miss) |
| 11:50 | C8: szkic `BOARD_NOTE.md` z liczb pełnego uruchomienia (11:46, niezamrożone): 3 vany, 64 552 PLN/rok przy leasingu 104 400 PLN/rok, zakup zwraca się w ok. 7 lat; 8 z 10 najdłużej jeżdżących odpada na zasięgu; wrażliwość 1 / 3 / 8. Liczby po angielsku bez separatora tysięcy (KONSTYTUCJA 10) — poprawione też w `ASSUMPTIONS.md` |
| 11:55 | C11: `PREZENTACJA.md` — podział 15 min na A/B/C, demo w 3 krokach sprawdzone na `devel` (3 → 6 → 4 vany, 3 ostrzeżenia), pytania z odpowiedziami. Warunek dla B: angielski komunikat, liczby kontrolne i ostrzeżenia na ekranie, `ERROR:` bez śladu stosu. Otwarte: język prezentacji |
| 11:55 | Język prezentacji: **polski** (decyzja zespołu 11:52). Poprawki B (64b3964) sprawdzone w osobnym worktree po scaleniu z `devel`: warunki demo 1–3 spełnione, testy OK. Komunikaty zgłoszone przez B (K7) dopisane do `RERUN.md`; B czeka ze scaleniem do `devel` |
| 11:57 | `devel` (556f9af) zawiera wszystkie trzy tory. Testy OK; demo 1–3 i `ERROR` sprawdzone: 3 / 6 / 4 vany, liczby w `summary.csv` zgodne z `BOARD_NOTE.md` |
