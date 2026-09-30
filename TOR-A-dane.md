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
