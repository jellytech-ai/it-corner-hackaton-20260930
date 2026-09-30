# TOR A — Dane

Najpierw przeczytaj: `KONTRAKT.md`, potem `HANDOFF.md` sekcje 4–6.

## Cel

Z surowych `trips.csv` i `vans.csv` zrobić czyste dane, profil każdego vana i trzy liczby kontrolne — tak, żeby działało też na eksporcie z innego kwartału.

## Twoje pliki

`data.py`, `params.csv`, `fixtures/*`, `tests/test_a.py`, `KONTRAKT.md`, ten plik. Niczego innego nie edytujesz.

## Zadania

| # | Do kiedy | Zadanie | Gotowe, gdy |
|---|---|---|---|
| A1 | 11:35 | `load_params`: wczytanie `params.csv` do słownika | zwraca wszystkie klucze; brak pliku = czytelny błąd |
| A2 | 11:50 | `load_and_clean`: wczytanie CSV, sprawdzenie kolumn, usunięcie pełnych duplikatów, `van_alias`, reguła `km` | 2777 wierszy, `total_km` = 344952 |
| A3 | 11:50 | `control_figures` + wypisanie na ekran | zgodne z KONTRAKT sekcja 8; **podaj liczby osobie z B lub C do niezależnego przeliczenia** |
| A4 | 12:10 | `build_van_profile` | wynik identyczny z `fixtures/van_profile.csv` |
| A5 | 12:20 | `report`: lista linii do `data_report.txt` | zawiera: liczbę duplikatów, zastosowane aliasy, wiersze z `km_source = gps`, liczbę braków `gps_km`, `van_id` spoza rejestru, vany z rejestru bez kursów, zakres dat i `period_days` |
| A6 | 12:20 | wypchnięcie gałęzi `tor-a` | B scala |
| A7 | 13:30–14:00 | zmiany po odpowiedziach Ewy (np. P-17) — tylko w `params.csv` | ponowne uruchomienie przechodzi |
| A8 | 14:00–14:45 | pomoc torowi C przy dokumentach; przygotowanie „świeżego eksportu” do testu | plik `fixtures/fresh_trips.csv`: 6 tygodni danych, jeden nieznany `van_id`, jeden ujemny przebieg |
| A9 | 14:45–15:15 | **test ponownego uruchomienia**: uruchom narzędzie wyłącznie z `RERUN.md` na `fresh_trips.csv` | działa bez pytania autorów; uwagi do C |

## Reguły czyszczenia (z HANDOFF)

- Duplikat = wiersz identyczny we wszystkich kolumnach (222 sztuki).
- `van_alias.P-17 = P-17B` (założenie A2).
- Dystans z licznika (A3); GPS tylko awaryjnie.
- Nieznany `van_id` po aliasach: nigdy nie usuwaj po cichu — patrz decyzja 2 poniżej.

## Decyzje do podjęcia w tym torze

| # | Pytanie | Propozycja domyślna |
|---|---|---|
| 1 | Wiersz P-27 z 13.08 (−208,6 km, GPS 90,3) | podmiana na `gps_km`; tak są policzone pliki testowe |
| 2 | Kurs vana spoza rejestru w przyszłym eksporcie | wykluczyć z liczb, wypisać ostrzeżenie w raporcie i na ekranie |
| 3 | Brak `gps_km` i zły licznik jednocześnie | wiersz odrzucony, ostrzeżenie |

Każdą podjętą decyzję wpisz do dziennika niżej z godziną; C przeniesie ją do `HANDOFF.md`.

## Czego nie robisz

Filtrów wykonalności, kosztów, rankingu, plików wynikowych.

## Stan (11:35)

| Zadanie | Stan |
|---|---|
| A1–A5 | zrobione: `data.py`, 12 testów przechodzi (`python3 -m unittest tests.test_a`) |
| A3 | liczby kontrolne 38 / 2777 / 344952 potwierdzone niezależnie (`sort -u` + `awk`) |
| A6 | gałąź `tor-a` wypchnięta |
| A8 | zrobione z wyprzedzeniem: `fixtures/fresh_trips.csv` + generator `fixtures/make_fresh_trips.py` |
| A7 | czeka na odpowiedzi Ewy |
| A9 | czeka na `RERUN.md` od toru C |

Samodzielne uruchomienie toru A:

```
python3 data.py --trips ../it-corner-hackathon-20260930/trips.csv --vans ../it-corner-hackathon-20260930/vans.csv --params params.csv
```

Oczekiwany wynik na `fixtures/fresh_trips.csv` (test ponownego uruchomienia): okres 2026-10-05 do 2026-11-14 (41 dni), 1310 kursów, 161957 km, trzy ostrzeżenia (nieznany van P-39, ujemny licznik P-13, brak dystansu P-21).

## Dziennik

| Godzina | Decyzja / zdarzenie |
|---|---|
| 11:25 | Decyzja 1: wiersz P-27 z 13.08 liczony z `gps_km` (90,3 km). Reguła ogólna: licznik ≤ 0 lub pusty → GPS, z ostrzeżeniem w raporcie |
| 11:25 | Decyzja 2: kursy vana spoza rejestru (po aliasach) są wykluczane z liczb, z ostrzeżeniem wskazującym, co dopisać do rejestru lub `params.csv` |
| 11:25 | Decyzja 3: wiersz bez użytecznego dystansu (zły licznik i brak GPS) jest odrzucany z ostrzeżeniem |
| 11:25 | `vans_assessed` = liczba vanów z rejestru, które mają co najmniej jeden kurs; van bez kursów dostaje ostrzeżenie |
| 11:30 | Wiersze z brakiem `gps_km`: 15 po deduplikacji (17 w surowych danych); bez wpływu, bo dystans jest z licznika |
| 11:30 | Alias P-17 → P-17B dotyczy 30 wierszy po deduplikacji (33 w surowych) |
| 11:33 | Pułapka przy niezależnym przeliczeniu: `awk` z polskimi ustawieniami regionalnymi obcina ułamki (wynik 343699 zamiast 344952). Trzeba uruchamiać z `LC_ALL=C`. Python nie ma tego problemu |
| 11:35 | Raport i komunikaty narzędzia są po angielsku, bo czyta je analityk Ewy |
| 12:08 | Odpowiedzi Ewy zweryfikowane u źródła (Discussions, wątek „9” i wątki innych zespołów). Potwierdzone: ufać licznikowi, P-17 = P-17B; duplikaty i wiersz P-27 — nasza decyzja, zostaje jak było |
| 12:15 | A7: `params.csv` według reguł Ewy (0,60 × WLTP, 95. percentyl, 10 punktów w North, 3 vany z South, dotacja 30%, 5 lat, wyjście z leasingu 3 raty) |
| 12:15 | Nowa kolumna `range_day_km` w `van_profile`; percentyl z interpolacją liniową (jak `PERCENTILE.INC` w Excelu, żeby analityk mógł to sprawdzić w arkuszu) |
| 12:15 | `tor-a` nie jest scalony do `devel`: nowe wartości parametrów wywracają 9 testów toru B, dopóki B i C nie przejdą na nowe reguły (KONTRAKT sekcja 10) |
| 12:35 | Q10, Q11, Q18, Q21 toru B rozstrzygnięte: parametry progu „blisko” zaakceptowane; kolumny `reason`, `fit_models`, `shortlisted`, `shortlist_note` dopisane do KONTRAKT 6 i 7 |
| 12:35 | Kontrola krzyżowa: wynik narzędzia na `devel` (8 vanów, 95 637 PLN w 5 lat) identyczny z niezależnym obliczeniem toru A |
| 12:55 | **A9 zrobione: test ponownego uruchomienia z samego `RERUN.md`.** Zip według polecenia toru B rozpakowany w pustym katalogu, `fixtures/fresh_trips.csv` jako `trips.csv`, zmieniona tylko `lease_reference_date`. Wynik: kod 0, okres 41 dni, 1310 kursów, 161 957 km, 3 ostrzeżenia (P-39, ujemny licznik P-13, brak dystansu P-21), 7 vanów na liście, 96 359 PLN w 5 lat. Instrukcja wystarcza bez pytań do autorów |
| 12:55 | Sprawdzone scenariusze pomyłek analityka — wszystkie kończą się jedną linią `ERROR:` i kodem 1, bez plików wynikowych: zła ścieżka, brak kolumny, brak parametru, nowy model diesla w rejestrze, zła data w `lease_reference_date`. Działa: alias dodany według ostrzeżenia, pliki z BOM i końcami linii Windows, uruchomienie z innego katalogu, ponowny zapis do tego samego katalogu. Składnia wszystkich czterech plików zgodna z Pythonem 3.9 |
| 12:55 | Znalezione i poprawione w `data.py`: plik zapisany przez polskiego Excela (średniki, przecinek dziesiętny) dawał niejasny błąd (`could not convert string to float: '0,60'` bez nazwy parametru). Teraz komunikat nazywa parametr i mówi, jak zapisać plik |
| 12:55 | Do toru C: (1) `RERUN.md` zaczyna się od komentarza `DRAFT` — usunąć; (2) krok 2 radzi otworzyć `params.csv` w Excelu — dopisać, że polski Excel zapisuje średniki i przecinki dziesiętne, bezpieczniej edytor tekstu; (3) odpowiedź dla Ewy obiecuje README — w zipie plik ma się nazywać `README.md` albo odpowiedź ma mówić `RERUN.md` |
| 13:02 | Odpowiedź dla Ewy (analityk + podgląd dla CFO: 8 EV, 95 637 PLN) wysłana w wątku „9” |
| 13:10 | **Wrażliwość na przeliczenie rocznych km — do decyzji toru C.** Eksport ma 77 dni z kursami (pn–sob, bez 15.08). Nasz mnożnik 365 ÷ 90 = 4,056 odpowiada ok. 312 dniom pracy w roku, czyli bez świąt. Mnożnik 300 ÷ 77 = 3,90 (pytanie zespołu 5 do Ewy) daje 6 vanów i 60 247 PLN zamiast 8 i 95 637: P-13 i P-04 wypadają. Przy 3,78 zostaje 5 vanów i 38 021 PLN. Sprawdzone narzędziem przez zmianę `days_per_year` (351 i 340) |
| 13:10 | `data.py`: nowa funkcja `operating_days(trips)` (liczba dat z kursami) i liczba ta w raporcie („90 days, 77 with trips”) — żeby tor C mógł przejść na dni pracy bez zmian w torze A |
| 14:05 | Na prośbę Wojtka tor A domknął trzy pliki toru C (Walerian — do przejrzenia): `BOARD_NOTE.md` i `RERUN.md` bez komentarza `DRAFT`; w `RERUN.md` rada „edytor tekstu zamiast Excela” i trzy nowe wiersze w „If something goes wrong” (średniki, przecinek dziesiętny, niezgodne liczby kontrolne); w `PREZENTACJA.md` oś czasu i macierz śladowania w punkcie 7:00–8:30, wynik testu ponownego uruchomienia w pytaniach. Wszystkie liczby `BOARD_NOTE.md` sprawdzone uruchomieniem na `devel` `7acba93`: tabela 8 vanów, sumy 136 092 / 95 637, rozbicie 1 007 577 − 903 000 − 8 940, cztery warianty wrażliwości, liczniki 6 / 10 / 7 / 15 — zgodne |
| 15:20 | **Wydanie `v1.0`.** PR #5 `devel` → `main` scalony (`f4e8b7a`), automat zielony na Pythonie 3.9 i 3.13, tag `v1.0` wypchnięty. Zip zbudowany z tagu (`git archive v1.0`, potem polecenie B11: 7 plików), rozpakowany w pustym katalogu z `trips.csv` i `vans.csv`, polecenie z `RERUN.md` krok 3: kod 0, liczby kontrolne 38 / 2777 / 344952, 8 vanów, `saving_pln` 95637 i `annual_fuel_saving_pln` 136092 — równe `BOARD_NOTE.md` z tagu. Przegląd PR przez drugą osobę pominięty z braku czasu |
