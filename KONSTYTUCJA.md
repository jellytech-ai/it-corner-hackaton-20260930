# KONSTYTUCJA — wspólne zasady dla wszystkich torów

Stan: 30.09.2026, 11:50. Obowiązuje każdy tor i każdą sesję. `KONTRAKT.md` mówi, **co** sobie przekazujemy; ten dokument mówi, **jak** piszemy, żeby całość wyglądała jak dzieło jednego zespołu.

Przy sprzeczności: README Ewy > ta konstytucja > `KONTRAKT.md` > dokumenty torów.

## 1. Zasady nadrzędne

1. **Nigdy po cichu.** Narzędzie niczego nie poprawia, nie odrzuca i nie zakłada bez śladu w `data_report.txt`.
2. **Żadnej liczby na sztywno.** Wszystko, co może się zmienić między kwartałami, jest w `params.csv`.
3. **Liczby do sprawdzenia.** Każdą liczbę w plikach dla Ewy da się odtworzyć z `all_vans.csv` kalkulatorem.
4. **Najgorszy dzień, nie średnia.** Testy wykonalności liczymy na najgorszym dniu z danych (wymóg Witolda).
5. **Każda decyzja ma godzinę i właściciela.** Bez wpisu w dzienniku decyzja nie istnieje.
6. **Analityk uruchamia to bez nas.** Komunikat, który wymaga znajomości naszych rozmów, jest błędem.

## 2. Język

| Co | Język |
|---|---|
| komunikaty narzędzia, `data_report.txt`, pliki wynikowe, `--help`, `saving_basis`, kolumna `reason` | angielski |
| nazwy funkcji, zmiennych, kolumn, parametrów | angielski, `snake_case` |
| docstringi i komentarze w kodzie | angielski |
| `RERUN.md`, `BOARD_NOTE.md`, `ASSUMPTIONS.md` | angielski |
| `HANDOFF.md`, `KONTRAKT.md`, `KONSTYTUCJA.md`, `TOR-*.md`, commity | polski, z polskimi znakami |

Nazwy własne zawsze dokładnie jak w źródle: `van_id` jak w rejestrze, model EV jak w `ev_offers.md` (`Volta Cargo S`), baza `North` / `South`.

## 3. Błędy, ostrzeżenia, komunikaty

### Trzy poziomy

| Poziom | Kiedy | Skutek | Gdzie trafia |
|---|---|---|---|
| **ERROR** | nie da się policzyć wiarygodnego wyniku: brak pliku, brak kolumny, brak parametru, zero użytecznych wierszy | przerwanie, kod wyjścia 1, żadnych plików wynikowych | `stderr`, jedna linia |
| **WARNING** | da się policzyć, ale ktoś musi spojrzeć: odrzucony lub zmieniony wiersz, nieznany van, van bez kursów | liczymy dalej, kod wyjścia 0 | `data_report.txt` i ekran |
| informacja | zwykły przebieg: ile wczytano, ile duplikatów, jaki okres | — | `data_report.txt` i ekran |

### Format

- Linia ostrzeżenia zaczyna się dokładnie od `WARNING: `, linia błędu od `ERROR: `. Informacje nie mają prefiksu.
- Jedna linia = jedno zdarzenie. Bez kropki na końcu, bez wykrzykników, bez wielkich liter dla podkreślenia.
- Kolejność treści: **co się stało**, **gdzie**, **co zrobiło narzędzie**, **co ma zrobić analityk** (jeśli coś ma zrobić).
- „Gdzie” dla wiersza danych to zawsze `<date> <van_id> <route_id>`; dla parametru — jego klucz w apostrofach; dla pliku — ścieżka.
- Wartość, która wywołała problem, cytujemy w apostrofach dokładnie tak, jak była w pliku.

Wzorce (obowiązujące brzmienie):

```
WARNING: odometer_km '-208.6' not usable, gps_km 90.3 used: 2026-08-13 P-27 S-R13
WARNING: van_id 'P-39' is not in the van register; 3 rows excluded. Add it to the register or add van_alias.P-39 to params.csv.
WARNING: row rejected, no usable distance (odometer_km '0', gps_km ''): 2026-10-05 P-21 N-R10
WARNING: van P-40 is in the register but has no trips in this export
ERROR: Trips file not found: trips.csv
ERROR: Trips file trips.csv: missing column(s) gps_km, stops
ERROR: Missing parameter 'winter_range_factor' in params.csv
```

### W kodzie

- Funkcje biblioteczne (`data.py`, `feasibility.py`, `economics.py`) **nie drukują i nie kończą programu**. Problemy z danymi dopisują do listy `report`; problemy uniemożliwiające pracę zgłaszają wyjątkiem.
- Wyjątki: `FileNotFoundError` dla brakującego pliku, `ValueError` dla złych danych, kolumn i parametrów. Treść wyjątku jest gotowym komunikatem po angielsku, bez prefiksu `ERROR:`.
- Tylko punkt wejścia (`ev_shortlist.py`, `main()` w `data.py`) łapie te dwa wyjątki, wypisuje `ERROR: <treść>` na `stderr` i zwraca kod 1. Analityk nie powinien zobaczyć śladu stosu dla przewidywalnego błędu.
- Brakujący parametr zgłasza się zawsze tym samym zdaniem: `Missing parameter '<klucz>' in params.csv`.
- Po udanym przebiegu punkt wejścia wypisuje na ekran: raport, trzy liczby kontrolne, liczbę vanów na shortliście, katalog wyników.
- Liczby, progi i nazwy modeli w komunikatach pochodzą z danych lub `params.csv`, nie z tekstu wpisanego w kod.
- **Każdy nowy komunikat `ERROR` i każdy nowy rodzaj `WARNING`, który może zobaczyć analityk, ma wiersz w tabeli „If something goes wrong” w `RERUN.md`: objaw i co zrobić.** Autor komunikatu zgłasza go torowi C w swoim dzienniku; C dopisuje wiersz przed 15:15 (C10).

## 4. Liczby

- Liczymy na liczbach zmiennoprzecinkowych, **zaokrąglamy dopiero przy zapisie**. Sumy przez `math.fsum`.
- `range_check_km`: 1 miejsce po przecinku. Km i kwoty w plikach Ewy: liczby całkowite (`round`).
- **Sumy w `summary.csv` to sumy zaokrąglonych wierszy `shortlist.csv`**, nie zaokrąglona suma dokładnych wartości — CFO doda kolumnę i ma dostać ten sam wynik.
- `annual_km` = `km_period` × `days_per_year` ÷ `period_days`; nigdy stały mnożnik.
- Porównania z progiem: `≤` przechodzi. Van dokładnie na progu przechodzi i ma to zapisane w `reason`.
- Kwoty w PLN netto, dystanse w km, energia w kWh, ładunek w kg. Jednostka jest w nazwie kolumny lub parametru (`_pln`, `_km`, `_kg`, `_kwh`).
- Liczby czytamy przez `float()`, nigdy przez funkcje zależne od ustawień regionalnych. W powłoce `awk` i `sort` tylko z `LC_ALL=C`.

## 5. Pliki CSV

- UTF-8 bez BOM, przecinek, nagłówek, koniec linii `\n`, kropka dziesiętna, bez separatorów tysięcy.
- Kolejność kolumn dokładnie jak w `KONTRAKT.md`.
- Wartości logiczne: `yes` / `no`. Brak wartości: puste pole, nigdy `None`, `NaN`, `-`.
- Wczytywanie przez `csv.DictReader` z `encoding="utf-8-sig"`; zapis przez `csv.DictWriter` z `lineterminator="\n"`.

## 6. Kod

- Python 3.9+, tylko biblioteka standardowa.
- Tabele to `list[dict]`; funkcje nie zmieniają argumentów, zwracają nowe wiersze.
- Sygnatury publiczne dokładnie jak w `KONTRAKT.md`, sekcja 5. Zmiana sygnatury = zmiana kontraktu.
- Każda funkcja publiczna ma jednozdaniowy docstring mówiący, co zwraca.
- Bez zaślepek w wersji końcowej: po 14:45 w repo nie może zostać żaden `_stub_*` ani tekst „zaślepka”.

## 7. Testy

- Plik `tests/test_<tor>.py`, moduł `unittest`. Całość: `python3 -m unittest discover -s tests`.
- Testy na prawdziwym eksporcie szukają go w `../it-corner-hackathon-20260930` albo w zmiennej `EV_SOURCE_DIR`; gdy go nie ma, są pomijane, nie czerwone.
- Każdy próg i każda reguła czyszczenia ma test z przypadkiem tuż pod, na i tuż nad progiem.
- Liczby kontrolne (38 / 2777 / 344952) są testem. Zmiana którejkolwiek wymaga wpisu w dzienniku.
- Przed każdym wypchnięciem gałęzi wszystkie testy przechodzą.

## 8. Git

- Gałąź bazowa: `devel` (do 11:43 nazywała się `handoff-wstepna-analiza`). Wszystko scalamy do niej. Gałęzie torów: `tor-a`, `tor-b-wykonalnosc`, `tor-c`.
- Tor edytuje tylko swoje pliki (tabela w `KONTRAKT.md`, sekcja 2).
- **`git add <plik>`, nigdy `git add -A` ani `git add .`** — tak trafiły do repo pliki `.pyc`.
- Do repo nie trafia nic generowanego: `__pycache__`, `wyniki/`, zipy, pliki edytora. `.gitignore` jest wspólny.
- Commity po polsku, w trybie rozkazującym, z prefiksem toru lub zadania: `Tor A: …`, `B6: …`.
- Scalamy przez merge, bez `rebase` i bez `push --force` na gałęziach, które ktoś mógł pobrać.
- Dwie sesje w jednym katalogu roboczym pracują w osobnych `git worktree`.

## 9. Decyzje i założenia

- Założenia mają numery `A<n>`, decyzje `D<n>`; numer nadaje tor C przy przenoszeniu do `HANDOFF.md`.
- Wpis w dzienniku toru: godzina, co postanowiono, dlaczego (jedno zdanie).
- Status założenia: `przyjęte`, `czeka na Ewę`, `potwierdzone przez Ewę`, `zmienione` (z numerem następcy).
- Odpowiedź Ewy zmienia wartość w `params.csv` i status założenia — nie kod.
- `ASSUMPTIONS.md` jest angielskim odbiciem sekcji 6 i 10 z `HANDOFF.md`; tor C pilnuje zgodności.

## 10. Słownik — te same słowa we wszystkich dokumentach

| Po polsku (wewnętrznie) | Po angielsku (narzędzie, dokumenty dla Ewy) | Znaczenie |
|---|---|---|
| liczby kontrolne | check figures | `vans_assessed`, `trips_counted`, `total_km` |
| najgorszy dzień | worst day | najwyższa suma km jednego vana jednego dnia |
| zasięg zimowy | winter range | WLTP × `winter_range_factor` |
| próg zimowy | winter range factor | 0,57 bazowo |
| doładowanie między trasami | midday charging | ładowanie w bazie między trasą poranną a popołudniową |
| van dwuzmianowy | two-shift van | van z co najmniej jednym dniem z dwiema trasami |
| blisko progu | near miss | do 10% ponad zasięg albo 1–3 dni ponad ładowność |
| wykonalny | feasible | przechodzi wszystkie filtry |
| świeży eksport | fresh export | dane z kolejnego kwartału |
| ponowne uruchomienie | rerun | uruchomienie narzędzia na świeżym eksporcie |

W tekstach po polsku liczby piszemy z przecinkiem dziesiętnym i spacją jako separatorem tysięcy (344 952 km; 0,57). W plikach CSV i po angielsku — kropka, bez separatora.

## 11. Dokumenty dla Ewy i zarządu

- Wniosek w pierwszym zdaniu, uzasadnienie potem.
- Każda liczba ma jednostkę i źródło (plik wynikowy albo parametr).
- Nie piszemy o tym, czego nie sprawdziliśmy, jakby było pewne: założenie nazywamy założeniem.
- Bez naszych skrótów roboczych (`A6`, `D3`, „tor B”) w `BOARD_NOTE.md`; w `ASSUMPTIONS.md` numery zostają.

## 12. Niezgodności znalezione przy scaleniu toru B (11:45) — do usunięcia

| # | Gdzie | Co | Właściciel |
|---|---|---|---|
| 1 | `ev_shortlist.py` | komunikat końcowy po polsku bez polskich znaków („Zapisano do …: 3 vanow na shortliscie”) — ma być po angielsku | B — rozwiązane (B, 11:48; sprawdzone przez C 12:29) |
| 2 | `ev_shortlist.py` | brak obsługi błędów: brakujący plik daje ślad stosu zamiast `ERROR: …` i kodu 1 | B — rozwiązane (B, 11:48; sprawdzone przez C 12:29) |
| 3 | `ev_shortlist.py` | nie wypisuje raportu ani liczb kontrolnych na ekran | B — rozwiązane (B, 11:48; sprawdzone przez C 12:29) |
| 4 | `ev_shortlist.py`, `--help` | opis i pomoc po polsku | B — rozwiązane (B, 11:48; sprawdzone przez C 12:29) |
| 5 | `ev_shortlist.py` | `saving_basis` z tekstem „zaslepka…” trafia do `summary.csv`, dopóki tor C nie jest scalony | B + C — rozwiązane 11:42 (scalenie `tor-c`: prawdziwe `economics.py`) |
| 6 | `feasibility.py` | docstringi po polsku bez polskich znaków | B — rozwiązane (B, 11:48; sprawdzone przez C 12:29) |
| 7 | `tests/test_a.py` | zmienna `HACKATHON_DATA` zamiast wspólnej `EV_SOURCE_DIR` | A — poprawione 11:50 |
| 9 | `data.py` + `ev_shortlist.py` | zero użytecznych wierszy daje dziś tylko `WARNING` i pliki z zerami; punkt wejścia ma to zamienić na `ERROR` | A + B — rozwiązane (B, 11:48; sprawdzone przez C 12:29): `ERROR: … no usable trip rows; nothing written`, kod 1, brak plików |
| 8 | nazwy gałęzi | `tor-b-wykonalnosc` obok `tor-a`, `tor-c` — zostaje, nie zmieniamy w trakcie | — |
