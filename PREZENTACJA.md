# PREZENTACJA — plan (15 min)

Stan: 30.09.2026, 14:05. Właściciel: tor C. Liczby sprawdzone uruchomieniem na `devel` (`7acba93`) o 14:00 — zgodne z tymi z 12:31; po zamrożeniu o 14:45 sprawdzamy jeszcze raz.

Ewa: „The focus of today is your process, not the app” oraz „show me it rerunning”. Dlatego ok. 10 min proces, 3 min demo, 2 min zapasu.

**Język prezentacji: polski** (decyzja 11:52). Pliki na ekranie zostają po angielsku, bo takie dostaje Ewa; nazwy z plików (`shortlist.csv`, „check figures”) czytamy tak, jak są, i raz tłumaczymy (słownik: `KONSTYTUCJA.md` sekcja 10).

## Kto mówi co

Wojtek prowadził tor A (dane), Rafał tor B (wykonalność), Walerian tor C (ekonomia i dokumenty).

| Czas | Kto | Temat | Co pokazujemy | Kluczowe zdanie |
|---|---|---|---|---|
| 0:00–1:00 | Walerian | **Odpowiedź na początek** | `BOARD_NOTE.md`, pierwszy akapit | „8 EV, kupione z dotacją, wszystkie w North — 95 637 PLN w 5 lat po zapłaceniu za auta. Bez dotacji żaden się nie zwraca” |
| 1:00–3:00 | Walerian | **Handoff jako dziennik decyzji** | `HANDOFF.md` sekcje 6 i 10: założenia z godzinami, decyzje D1–D16 | każda decyzja ma godzinę i powód; Ewa dostaje „co i kiedy” w `ASSUMPTIONS.md` |
| | | Selekcja pytań do Ewy | sekcja 7 | limit 5 pytań; P-17 i chłodnie rozstrzygnęliśmy z danych, zamiast pytać — Ewa potwierdziła oba wnioski |
| 3:00–5:00 | Wojtek | **Dane i liczby kontrolne** | `data_report.txt`, `KONTRAKT.md` sekcja 8 | 2999 → 2777 kursów (222 duplikaty), 344 952 km, 38 vanów; policzone dwa razy dwiema metodami; pułapka `awk` z polskimi ustawieniami regionalnymi |
| 5:00–7:00 | Rafał | **Wykonalność według reguł Ewy** | `all_vans.csv`, kolumny `range_check_km`, `reject_reason` | 95. percentyl dnia w 60% WLTP (156 / 228 km); ładowność jako twardy limit; vany dwuzmianowe bez ładowania w dzień; 15 z 38 przechodzi; model wybrany po wyniku w 5 lat |
| 7:00–8:30 | Walerian | **Odpowiedzi Ewy o 12:00 — jak proces je wchłonął** | `SDLC.md` sekcja 3 (oś czasu), `SLEDZENIE.md` wiersz R1, `KONTRAKT.md` sekcje 10 i 12, `params.csv` | rano: 3 vany i „bez dotacji się nie opłaca”; po odpowiedziach: nowe wartości w `params.csv` i jedna formuła `saving_pln` — w ok. 20 min 8 vanów, liczby sprawdzone niezależnie przez dwa tory co do złotówki; nasze 0,57 × WLTP ze źródłami potwierdziło, że 60% Ewy to rozsądna liczba. Każda reguła Ewy ma w `SLEDZENIE.md` swój parametr, test i kolumnę wyniku |
| 8:30–9:30 | Walerian | **Pieniądze i ryzyko** | `BOARD_NOTE.md` | skąd 95 637 PLN (ok. 1 007 600 oszczędności z eksploatacji − 903 000 za EV po dotacji − 8 940 opłaty za leasing P-25); dlaczego nie „te, co jeżdżą najwięcej”; P-30 i P-21 mają najdłuższe dni ponad 156 km — rezerwowe diesle |
| 9:30–10:00 | Rafał | **Jak pracowaliśmy równolegle** | `KONTRAKT.md`, `KONSTYTUCJA.md`, `fixtures/`, zielony automat testów na GitHubie | trzy tory od 11:20, każdy na plikach testowych w formacie kontraktu; scalenia bez konfliktów; konstytucja jako wspólny styl; testy uruchamiają się same przy każdym wypchnięciu. Raz kod wyprzedził kontrakt (cztery kolumny) — wyłapały to pytania toru B, stąd reguła „najpierw kontrakt” |
| 10:00–13:00 | Rafał (klawiatura), Wojtek (komentarz) | **Demo** | terminal | patrz niżej |
| 13:00–15:00 | wszyscy | Zapas i pytania | — | patrz „Pytania, których się spodziewamy” |

## Demo (3 min)

Przygotowane wcześniej w jednym oknie terminala, duża czcionka, katalog z rozpakowanym zipem narzędzia.

| # | Polecenie | Co mówi Wojtek | Co widać |
|---|---|---|---|
| 1 | `python3 ev_shortlist.py --trips trips.csv --vans vans.csv --params params.csv --out results/` | „Oryginalny eksport — ten sam wynik, co w wątku” | liczby kontrolne 38 / 2777 / 344952; ostrzeżenie o P-27; 8 vanów |
| 2 | w kopii `params_p100.csv` `range_check_percentile` 95 → 100, to samo polecenie z `--params params_p100.csv --out results_p100/` | „Najgorszy dzień zamiast 95. percentyla — czyli reguła Witolda »żaden van nigdy nie zawiedzie«. Jedna liczba w pliku parametrów, zero zmian w kodzie” | 6 vanów: P-30 i P-21 wypadają; 95 637 → 59 482 PLN. Tyle wart jest kompromis CFO i operacji |
| 3 | `--trips fresh_trips.csv --out results_fresh/` | „Tak będzie wyglądał następny kwartał: 6 tygodni, nowy van, zły licznik” | okres 41 dni, roczne km przeliczone; `WARNING` o nieznanym P-39, o ujemnym liczniku P-13 i o wierszu P-21 bez dystansu; 7 vanów |

Zasady demo:

- Polecenia wklejamy z `RERUN.md`, nie piszemy z pamięci — to jednocześnie pokazuje, że instrukcja działa.
- Krok 2 na kopii `params_p100.csv`, żeby oryginał się nie zmienił.
- Wyniki wszystkich trzech kroków zapisane wcześniej w `demo_backup/` — gdyby coś padło, pokazujemy pliki.

### Warunki, żeby demo wyglądało dobrze (sprawdzone 12:33 na `devel`: kroki 1–3)

| # | Stan | Kto |
|---|---|---|
| 1 | komunikaty po angielsku (`Vans on the shortlist: 8`, `Output written to: …`) | Rafał — gotowe |
| 2 | raport, `WARNING` i liczby kontrolne na ekranie — to pokazujemy w krokach 1 i 3 | Rafał — gotowe |
| 3 | brakujący plik: `ERROR: Trips file not found: …`, kod 1, bez śladu stosu | Rafał — gotowe |
| 4 | `fresh_trips.csv` istnieje i działa | Wojtek — gotowe |
| 5 | próba generalna demo z samego `RERUN.md` | Wojtek — test ponownego uruchomienia zrobiony 12:55 (`SDLC.md` sekcja 5); próba generalna po zamrożeniu (14:45–15:15) |

## Pytania, których się spodziewamy

| Pytanie | Kto | Odpowiedź w skrócie |
|---|---|---|
| Dlaczego 8, skoro dotacja jest na 10? | Walerian | reguły przechodzi 15 vanów; 6 z nich nie zwraca się w 5 lat (głównie leasingowane z małym przebiegiem albo z opłatą za wyjście z leasingu), a P-31 (+1 589 PLN) nie mieści się w limicie 3 vanów z South. Wolne zostają 2 z 10 punktów w North |
| Skąd 95. percentyl i 60%? | Rafał | to reguła Ewy („January plus a margin”); nasze niezależne oszacowanie rano dało 57% — temperatura × 0,70, ładunek × 0,90, rezerwa × 0,90, źródła w `ASSUMPTIONS.md` |
| Czemu nie te, co jeżdżą najwięcej (CFO)? | Walerian | przebieg to źródło oszczędności i dwa takie vany są na liście (P-12, P-08), ale 8 z 10 najdłużej jeżdżących ma 95. percentyl dnia 206–293 km przy 156 km (Cargo S); Cargo L sięga tylko P-33, który jest za ciężki |
| Co, jeśli P-30 albo P-21 nie da rady w styczniu? | Rafał | ich najdłuższe dni to 166 i 159 km przy 156 km — dlatego zalecamy zostawić dwa wymieniane diesle jako rezerwę; przy regule „najgorszy dzień” wypadają (krok 2 demo) |
| Czy to się opłaca? | Walerian | tak, ale tylko z dotacją: najlepszy van zarabia w 5 lat 23 305 PLN, a dotacja na jeden Cargo S to 45 000 PLN |
| Czemu zakup, a nie leasing? | Walerian | dotacja tylko przy zakupie; Cargo S po dotacji 105 000 PLN, 60 rat leasingu 174 000 PLN |
| Czy analityk poradzi sobie bez was? | Wojtek | pokazaliśmy to w kroku 3 demo; test z samej instrukcji zrobiliśmy dwa razy (12:20 i 12:55): zip w pustym katalogu, świeży eksport, kod 0, 7 vanów; typowe pomyłki (zła ścieżka, brak kolumny, brak parametru, plik ze średnikami) kończą się jedną linią `ERROR:`. Testowały osoby z zespołu — nikt z zewnątrz nie próbował |
| Czemu nie pytaliście o X? | Walerian | limit 5 pytań; lista „co byśmy zapytali dalej” jest w `ASSUMPTIONS.md` |

## Czego nie mówimy

- Skrótów roboczych bez wyjaśnienia (A6, D3, „tor B”) — na slajdzie tak, ale mówimy pełnym zdaniem.
- Liczb, których nie ma w plikach w wątku.
- Że coś „działa”, jeśli nie pokazaliśmy tego w demo albo w pliku.
