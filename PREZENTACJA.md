# PREZENTACJA — plan (15 min)

Stan: 30.09.2026, 11:55. Właściciel: tor C. Liczby w tym planie pochodzą z uruchomienia o 11:46; po zamrożeniu o 14:45 podmieniamy je na ostateczne.

Ewa: „The focus of today is your process, not the app” oraz „show me it rerunning”. Dlatego ok. 10 min proces, 3 min demo, 2 min zapasu.

**Język prezentacji: polski** (decyzja 11:52). Pliki na ekranie zostają po angielsku, bo takie dostaje Ewa; nazwy z plików (`shortlist.csv`, „check figures”) czytamy tak, jak są, i raz tłumaczymy (słownik: `KONSTYTUCJA.md` sekcja 10).

## Kto mówi co

Wojtek prowadził tor A (dane), Rafał tor B (wykonalność), Walerian tor C (ekonomia i dokumenty).

| Czas | Kto | Temat | Co pokazujemy | Kluczowe zdanie |
|---|---|---|---|---|
| 0:00–1:00 | Walerian | **Odpowiedź na początek** | `BOARD_NOTE.md`, pierwszy akapit | „3 vany w North teraz, nie 10 — i dlaczego to uczciwa odpowiedź” |
| 1:00–3:00 | Walerian | **Handoff jako dziennik decyzji** | `HANDOFF.md` sekcje 6 i 10: założenia z godzinami, D1–D12 | każda decyzja ma godzinę i powód; Ewa dostaje „co i kiedy” w `ASSUMPTIONS.md` |
| | | Selekcja pytań do Ewy | sekcja 7 | limit 5 pytań; P-17 i chłodnie rozstrzygnęliśmy z danych, zamiast pytać |
| 3:00–5:00 | Wojtek | **Dane i liczby kontrolne** | `data_report.txt`, `KONTRAKT.md` sekcja 8 | 2999 → 2777 kursów (222 duplikaty), 344 952 km, 38 vanów; policzone dwa razy dwiema metodami; pułapka `awk` z polskimi ustawieniami regionalnymi |
| 5:00–7:30 | Rafał | **Wykonalność: najgorszy dzień i zima** | `HANDOFF.md` „Skąd 0,57 × WLTP”, `all_vans.csv` | najgorszy dzień zamiast średniej (Witold); 0,57 × WLTP ze źródłami; doładowanie między trasami ratuje P-08; ładowność jako twardy limit |
| 7:30–9:00 | Walerian | **Pieniądze bez upiększania** | `summary.csv`, `BOARD_NOTE.md` | 64 552 PLN/rok oszczędności przy 104 400 PLN/rok leasingu — decyduje dotacja; dlaczego nie „te, co jeżdżą najwięcej” |
| 9:00–10:00 | Rafał | **Jak pracowaliśmy równolegle** | `KONTRAKT.md`, `KONSTYTUCJA.md`, `fixtures/` | trzy tory od 11:20, każdy na plikach testowych w formacie kontraktu; scalenia bez konfliktów; konstytucja jako wspólny styl |
| 10:00–13:00 | Rafał (klawiatura), Wojtek (komentarz) | **Demo** | terminal | patrz niżej |
| 13:00–15:00 | wszyscy | Zapas i pytania | — | patrz „Pytania, których się spodziewamy” |

## Demo (3 min)

Przygotowane wcześniej w jednym oknie terminala, duża czcionka, katalog z rozpakowanym zipem narzędzia.

| # | Polecenie | Co mówi Wojtek | Co widać |
|---|---|---|---|
| 1 | `python3 ev_shortlist.py --trips trips.csv --vans vans.csv --params params.csv --out results/` | „Oryginalny eksport — ten sam wynik, co w wątku” | liczby kontrolne 38 / 2777 / 344952; 3 vany: P-08, P-26, P-14 |
| 2 | w `params.csv` `winter_range_factor` 0.57 → 0.65, to samo polecenie z `--out results_065/` | „Jedna liczba w pliku parametrów, zero zmian w kodzie” | 6 vanów (limit 6 punktów w North); P-14 wypada, wchodzą P-30, P-21, P-13, P-04 |
| 3 | `--trips fresh_trips.csv --out results_fresh/` | „Tak będzie wyglądał następny kwartał: 6 tygodni, nowy van, zły licznik” | roczne km przeliczone z innego okresu; `WARNING` o nieznanym P-39, o ujemnym liczniku i o wierszu bez dystansu; 4 vany |

Zasady demo:

- Polecenia wklejamy z `RERUN.md`, nie piszemy z pamięci — to jednocześnie pokazuje, że instrukcja działa.
- Po kroku 2 przywracamy 0,57 (albo pracujemy na kopii `params_065.csv`).
- Wyniki wszystkich trzech kroków zapisane wcześniej w `demo_backup/` — gdyby coś padło, pokazujemy pliki.

### Warunki, żeby demo wyglądało dobrze (sprawdzone 11:57 na `devel`: wszystkie 3 kroki demo i błąd brakującego pliku)

| # | Stan | Kto |
|---|---|---|
| 1 | komunikat końcowy po angielsku (`Vans on the shortlist: 3`, `Output written to: …`) | Rafał — gotowe, na `devel` od 11:55 (556f9af) |
| 2 | raport, `WARNING` i liczby kontrolne na ekranie — to pokazujemy w krokach 1 i 3 | Rafał — gotowe, jw. |
| 3 | brakujący plik: `ERROR: Trips file not found: …`, kod 1, bez śladu stosu | Rafał — gotowe, jw. |
| 4 | `fresh_trips.csv` istnieje i działa | Wojtek — gotowe |
| 5 | próba generalna demo z samego `RERUN.md` | Wojtek, po teście ponownego uruchomienia (14:45–15:15) |

## Pytania, których się spodziewamy

| Pytanie | Kto | Odpowiedź w skrócie |
|---|---|---|
| Dlaczego tylko 3, skoro dotacja jest na 10? | Walerian | ostre filtry dają 3 w North; South ma 5 kolejnych, które pasują technicznie, ale nie ma ładowarek — z nimi 8 |
| Skąd 0,57? | Rafał | temperatura × 0,70, ładunek × 0,90, rezerwa × 0,90; źródła w `ASSUMPTIONS.md`; wrażliwość 0,50 / 0,57 / 0,65 → 1 / 3 / 8 vanów |
| Czemu nie te, co jeżdżą najwięcej (CFO)? | Walerian | 8 z 10 ma najgorszy dzień 208–302 km przy zasięgu zimowym ok. 148 km, a operacje nie akceptują ani jednego nieudanego kursu |
| Co, jeśli P-14 nie da rady w styczniu? | Rafał | ma 0,2 km zapasu — dlatego zalecamy zostawić wymieniane diesle jako rezerwę |
| Czy to się opłaca? | Walerian | na samej eksploatacji nie: ok. 40 000 PLN/rok na minusie przy leasingu; decyduje dotacja |
| Czy analityk poradzi sobie bez was? | Wojtek | pokazaliśmy to w kroku 3 demo; test z samej instrukcji (14:45–15:15) robi osoba, która nie pisała skryptu — wpisać wynik |
| Czemu nie pytaliście o X? | Walerian | limit 5 pytań; lista „co byśmy zapytali dalej” jest w `ASSUMPTIONS.md` |

## Czego nie mówimy

- Skrótów roboczych bez wyjaśnienia (A6, D3, „tor B”) — na slajdzie tak, ale mówimy pełnym zdaniem.
- Liczb, których nie ma w plikach w wątku.
- Że coś „działa”, jeśli nie pokazaliśmy tego w demo albo w pliku.
