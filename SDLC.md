# SDLC — jak nasz proces pokrywa cały cykl

Stan: 30.09.2026, 15:20. Właściciel: tor A. Ten dokument mówi, **w której fazie cyklu jest który artefakt**, jakie bramki dzielą fazy i co zostało do zrobienia przed 16:00. Nie powtarza treści innych plików, tylko do nich odsyła.

Pracowaliśmy metodą „najpierw specyfikacja, potem kod” (SDD): konstytucja → specyfikacja → kontrakt → zadania → kod z testami. To pokrywa pierwsze trzy fazy. Poniżej domykamy pozostałe: weryfikację, wydanie i utrzymanie.

## 1. Fazy i artefakty

| Faza | Pytanie, na które odpowiada | Artefakt | Stan |
|---|---|---|---|
| 1. Wymagania | co i dla kogo liczymy, czego nie wiemy | `HANDOFF.md` sekcje 1–7 (zadanie, dane, rejestr założeń A1–A24, pytania do Ewy), sekcja 10 (decyzje D1–D16, odpowiedzi Ewy) | gotowe |
| 2. Projekt | jak dzielimy pracę i co sobie przekazujemy | `KONTRAKT.md` (wersja 2.3), `KONSTYTUCJA.md`, `params.csv`, `fixtures/`, `TOR-*.md` | gotowe |
| 3. Implementacja | kod | `data.py`, `feasibility.py`, `economics.py`, `ev_shortlist.py` | gotowe, zamrożenie liczb 14:45 |
| 4. Weryfikacja | czy kod robi to, czego chce Ewa | `tests/` (98 testów), `SLEDZENIE.md`, automat `.github/workflows/tests.yml`, kontrola krzyżowa dwóch torów (`KONTRAKT.md`, sekcja 11) | gotowe; luki L2–L6 w `SLEDZENIE.md` (L1 zamknięta) |
| 5. Wydanie | co dokładnie dostaje Ewa i z której wersji | PR `devel` → `main`, tag `v1.0`, zip zbudowany z tagu | wykonane 15:20 jako `v1.0` — sekcja 4 |
| 6. Akceptacja | czy analityk poradzi sobie bez nas | test ponownego uruchomienia z samego `RERUN.md` (tor A, 12:55; tor B, 12:20) | zrobione — sekcja 5 |
| 7. Utrzymanie | co się dzieje w kolejnym kwartale | `RERUN.md` („Every quarter”, „If something goes wrong”), `ASSUMPTIONS.md`, `KONTRAKT.md` sekcja 12 | gotowe; propozycje w sekcji 6 |

## 2. Bramki między fazami

| Bramka | Warunek przejścia | Kto sprawdza |
|---|---|---|
| wymagania → projekt | każde założenie ma numer, godzinę i status; pytania do Ewy wysłane | tor C w `HANDOFF.md` |
| projekt → kod | zmiana kolumny, sygnatury albo parametru ma nową wersję w `KONTRAKT.md`, sekcja 12 | właściciel kontraktu (A) |
| kod → `devel` | testy przechodzą lokalnie i w automacie (Python 3.9 i 3.13, prawdziwy eksport, żaden test pominięty) | automat na GitHubie |
| `devel` → `main` | PR z przeglądem drugiej osoby; nowa reguła ma wiersz w `SLEDZENIE.md` | osoba spoza toru, który zmieniał |
| `main` → Ewa | tag, zip z tagu, liczby w `BOARD_NOTE.md` równe wynikowi uruchomienia z zipa | tor B (zip), tor C (dokumenty) |

## 3. Oś czasu (materiał na slajd)

Godziny z `git log` i dziennika w `HANDOFF.md`.

| Godzina | Faza | Co się stało |
|---|---|---|
| 10:10 | wymagania | repo organizatorów przeczytane, pierwszy profil danych |
| 10:30 | wymagania | własne oszacowanie zasięgu zimowego 0,57 × WLTP ze źródłami |
| 10:54 | wymagania | `HANDOFF.md` w repo: założenia, decyzje, pytania do Ewy |
| 11:09 | wymagania | pytania wysłane |
| 11:19 | projekt | `KONTRAKT.md` 1.0, `params.csv`, pliki testowe — start trzech torów |
| 11:22–11:35 | implementacja | pierwsze commity trzech torów; tor A oddany z liczbami kontrolnymi |
| 11:50 | projekt | `KONSTYTUCJA.md` — wspólny styl po pierwszym scaleniu |
| 11:55 | weryfikacja | pierwsze pełne scalenie na `devel`: 3 vany |
| ok. 12:00 | **zmiana wymagań** | odpowiedzi Ewy: 60% WLTP, 95. percentyl, 10 punktów, dotacja 30%, 5 lat |
| 12:15 | projekt | `KONTRAKT.md` 2.0: 10 parametrów, jedna nowa kolumna, nowa formuła |
| 12:33 | weryfikacja | `devel` po zmianie: 8 vanów, 95 637 PLN; dwa tory niezależnie, zgodne co do złotówki |
| 12:55 | akceptacja | test ponownego uruchomienia z samego `RERUN.md` przechodzi |
| 13:07 | weryfikacja | macierz śladowania, automat testów, kontrakt 2.2 |
| 14:45 | implementacja | zamrożenie liczb: 8 vanów, 95 637 PLN |
| 15:05–15:12 | **zmiana wymagań** | druga tura odpowiedzi Ewy: „wybierzcie i zapiszcie” — dwa założenia doprecyzowane, kod bez zmian |
| 15:20 | wydanie | `v1.0`: PR do `main`, tag, zip z tagu |

**Zdanie na slajd:** zmiana wymagań w połowie dnia przeszła drogą wymaganie → kontrakt → parametr → kod → test w 33 minuty (12:00–12:33), a wynik zmienił się z 3 na 8 vanów bez przepisywania narzędzia.

**Czego się nauczyliśmy:** raz kod wyprzedził kontrakt (wersja 2.1: cztery kolumny dopisane po fakcie). Wyłapał to tor B pytaniami Q11, Q18, Q21; od wersji 2.2 obowiązuje reguła „najpierw kontrakt” i test kolejności kolumn.

Liczby z historii: 80 commitów, 16 scaleń, 3 osoby, 98 testów.

## 4. Wydanie — lista kroków

Wykonane 30.09.2026 o 15:20 jako `v1.0`. Wynik próby z zipa (krok 5) jest w dzienniku `TOR-A-dane.md`, bo powstaje dopiero po otagowaniu.

1. Automat na `devel` jest zielony.
2. PR `devel` → `main`, przegląd jednej osoby, scalenie przez merge. (Przy `v1.0` z braku czasu PR zatwierdził Wojtek bez drugiej osoby.)
3. `git tag -a v1.0 -m "Wersja dla Ewy, 30.09.2026"` na `main`, `git push origin v1.0`.
4. Zip budujemy **z tagu**, poleceniem toru B z `TOR-B-wykonalnosc.md` (B11), nie z katalogu roboczego.
5. Zip rozpakowany w pustym katalogu, polecenie z `RERUN.md`, krok 3: liczby kontrolne 38 / 2777 / 344952 i suma `saving_pln` równa tej w `BOARD_NOTE.md`.
6. Do wątku: zip, `shortlist.csv`, `summary.csv`, `BOARD_NOTE.md`, `ASSUMPTIONS.md`.

## 5. Akceptacja — zapis testu ponownego uruchomienia

| Kto | Kiedy | Jak | Wynik |
|---|---|---|---|
| tor B | 12:20 | zip z plikami z `RERUN.md`, pusty katalog, oryginalny eksport | kod 0, 8 vanów, pliki bajt w bajt jak z repo |
| tor A | 12:55 | to samo na `fixtures/fresh_trips.csv` (kolejny kwartał), zmieniona tylko `lease_reference_date` | kod 0, 41 dni, 1310 kursów, 161 957 km, 3 ostrzeżenia, 7 vanów |
| tor A | 12:55 | pomyłki analityka: zła ścieżka, brak kolumny, brak parametru, nowy model diesla, zła data, plik ze średnikami | zawsze jedna linia `ERROR:`, kod 1, bez plików |

Szczegóły: `TOR-A-dane.md` i `TOR-B-wykonalnosc.md`, dzienniki. Oba testy robiły osoby, które znają kod; test przez kogoś spoza zespołu nie był możliwy.

## 6. Utrzymanie — propozycje do plików toru C

`RERUN.md` już mówi, co analityk zmienia co kwartał i co robić przy błędzie. Brakuje jednego wiersza; to plik toru C, więc zostawiam go jako propozycję, razem z propozycją do prezentacji:

| Gdzie | Co dopisać |
|---|---|
| `RERUN.md`, tabela „If something goes wrong” | wiersz: liczby kontrolne na ekranie nie zgadzają się z eksportem → przeczytać `WARNING` w `data_report.txt`; różnica to odrzucone wiersze albo vany spoza rejestru |
| `PREZENTACJA.md`, punkt 7:00–8:30 | pokazać oś czasu z sekcji 3 i jeden wiersz z `SLEDZENIE.md` (R1) jako dowód drogi wymaganie → test |
