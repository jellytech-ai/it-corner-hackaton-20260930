# KONTRAKT — wspólne ustalenia dla torów A, B, C

Stan: 30.09.2026, 11:20. Ten plik czyta każdy tor przed startem. Zmiana kontraktu = wiadomość do pozostałych dwóch osób, potem edycja tutaj.

Kontekst, założenia (A1–A17) i decyzje (D1–D5): `HANDOFF.md`.

Jak piszemy (język, format błędów i ostrzeżeń, zaokrąglenia, CSV, git, słownik): **`KONSTYTUCJA.md`** — obowiązuje wszystkie tory.

## 1. Stanowisko pracy

```
git clone https://github.com/handsonarchitects/it-corner-hackathon-20260930   # dane źródłowe (tylko odczyt)
git clone https://github.com/jellytech-ai/it-corner-hackaton-20260930         # nasze repo
cd it-corner-hackaton-20260930
git checkout handoff-wstepna-analiza
git checkout -b tor-a        # albo tor-b, tor-c
```

- Python 3.9+, **tylko biblioteka standardowa** (bez pandas).
- Dane źródłowe leżą w sąsiednim katalogu `../it-corner-hackathon-20260930/`. Nie kopiujemy ich do naszego repo.

## 2. Kto jest właścicielem czego

Każdy tor edytuje **wyłącznie swoje pliki**. Dzięki temu scalanie gałęzi nie daje konfliktów.

| Plik | Właściciel | Pozostali |
|---|---|---|
| `data.py`, `fixtures/*` | A | czytają |
| `feasibility.py`, `ev_shortlist.py` (punkt wejścia, ranking, eksport) | B | czytają |
| `economics.py`, `RERUN.md`, `BOARD_NOTE.md`, `ASSUMPTIONS.md` | C | czytają |
| `HANDOFF.md` | C | zgłaszają decyzje w swoim pliku `TOR-*.md`, sekcja „Dziennik” |
| `params.csv`, `KONTRAKT.md` | A | zgłaszają potrzebę nowego parametru |
| `TOR-A-dane.md`, `TOR-B-wykonalnosc.md`, `TOR-C-ekonomia-dokumenty.md` | odpowiedni tor | — |
| `tests/test_a.py`, `tests/test_b.py`, `tests/test_c.py` | odpowiedni tor | — |

Uwaga do D5: narzędzie to **jeden katalog i jedno polecenie**, ale cztery pliki `.py` zamiast jednego — inaczej trzy osoby edytowałyby ten sam plik. Do wątku trafia jako zip.

## 3. Scalanie

| Godzina | Co |
|---|---|
| 12:20 | każdy wypycha swoją gałąź; B scala `tor-a`, `tor-b`, `tor-c` do `handoff-wstepna-analiza` i uruchamia całość |
| 13:50 | to samo po naniesieniu odpowiedzi Ewy |
| 14:45 | zamrożenie liczb; ostatnie scalenie kodu |
| 15:15 | ostatnie scalenie dokumentów |

## 4. Parametry — `params.csv`

Kolumny `parameter,value`. Klucze z kropką to grupy (`ev.<model>.<pole>`, `fuel_l_per_100km.<model diesla>`, `chargers.<baza>`, `van_alias.<stary>`). Plik już istnieje w repo z wartościami z `costs.md`, `ev_offers.md` i założeń.

Żadna liczba z tego pliku nie może być wpisana na sztywno w kodzie.

## 5. Interfejsy funkcji

Wszystkie tabele to `list[dict]` z kluczami jak kolumny poniżej. Liczby jako `float`/`int`, puste pole jako `""`.

```python
# data.py (tor A)
load_params(path) -> dict[str, str]
load_and_clean(trips_path, vans_path, params) -> (trips, vans, report)   # report: list[str]
build_van_profile(trips, vans) -> list[dict]
control_figures(trips, profile) -> dict      # vans_assessed, trips_counted, total_km
period_days(trips) -> int                    # liczba dni kalendarzowych od pierwszej do ostatniej daty włącznie

# feasibility.py (tor B)
assess(profile, trips, params) -> list[dict]           # tabela feasibility
sensitivity(profile, trips, params, factors) -> list[dict]

# economics.py (tor C)
economics(profile, feasibility, params, period_days) -> list[dict]
saving_basis(params) -> str

# ev_shortlist.py (tor B)
# CLI: python3 ev_shortlist.py --trips T --vans V --params params.csv --out wyniki/
```

## 6. Tabele

### `clean_trips` (A → B) — wzór: `fixtures/clean_trips.csv`

`date, van_id, driver, route_id, km, km_source, start_time, end_time, stops, max_load_kg`

- bez duplikatów; `van_id` po zastosowaniu `van_alias`
- `km` = `odometer_km`; jeśli ≤ 0 lub puste, to `gps_km` i `km_source = gps` (dotyczy wiersza P-27 z 13.08 — reguła do potwierdzenia, patrz TOR-A)

### `van_profile` (A → B, C) — wzór: `fixtures/van_profile.csv`

`van_id, model, year, depot, ownership, lease_end, monthly_lease_pln, refrigerated, payload_kg, days, trips, km_period, worst_day_km, max_load_kg, two_shift, two_shift_days`

- jeden wiersz na van z rejestru (38)
- `worst_day_km` = najwyższa suma km jednego dnia

### `feasibility` (B → C) — wzór: `fixtures/feasibility.csv`

`van_id, feasible, ev_model, ev_depot, range_check_km, midday_charging, day_tariff_share, reject_reason`

- `feasible`: `yes`/`no`; `ev_model` puste, jeśli żaden model nie pasuje
- `range_check_km`: dystans porównany z zasięgiem (najgorszy dzień; dla doładowania między trasami — dłuższa z dwóch tras najgorszego dnia, do opisania w założeniach)
- `day_tariff_share`: jaka część energii jest ładowana w dzień (0 bez doładowania między trasami)
- **wzór w `fixtures/` jest uproszczony** (bez doładowania między trasami, South odrzucony) — służy tylko do pracy toru C, zanim B odda prawdziwy wynik

### `economics` (C → B)

`van_id, annual_km, annual_fuel_saving_pln, saving_pln`

- liczone dla **każdego** vana, który ma `ev_model`, także niewykonalnego (potrzebne do `all_vans.csv`)

## 7. Pliki wynikowe (pisze `ev_shortlist.py`)

| Plik | Zawartość |
|---|---|
| `shortlist.csv` | format Ewy: `rank, van_id, ev_model, ev_depot, range_check_km, annual_km, annual_fuel_saving_pln, saving_pln, reason` |
| `summary.csv` | `figure,value`: `vans_assessed, trips_counted, total_km, recommended_count, annual_fuel_saving_pln, saving_pln, saving_basis` |
| `all_vans.csv` | `van_profile` + `feasibility` + `economics` dla wszystkich 38 vanów |
| `data_report.txt` | raport z czyszczenia (A) |

Format: UTF-8, przecinek, kropka dziesiętna, bez separatorów tysięcy; `range_check_km` z 1 miejscem po przecinku, kwoty i km jako liczby całkowite.

## 8. Liczby kontrolne — wartości oczekiwane

Z plików testowych (pandas, poza repo). Tor A ma je odtworzyć w czystym Pythonie.

| Figura | Wartość |
|---|---|
| wiersze surowe | 2999 |
| `trips_counted` | 2777 |
| `total_km` | 344952 |
| `vans_assessed` | 38 |
| okres | 2026-06-15 do 2026-09-12 (90 dni) |

Potwierdzone 11:33 przez `data.py` i niezależnie poleceniem powłoki. Uwaga: `awk` wymaga `LC_ALL=C`, inaczej przy polskich ustawieniach regionalnych obcina ułamki.

```
tail -n +2 ../it-corner-hackathon-20260930/trips.csv | LC_ALL=C sort -u | LC_ALL=C awk -F, '{n++; s+=($5>0)?$5:$6; v[($2=="P-17")?"P-17B":$2]=1} END{c=0; for(k in v)c++; printf "trips=%d total_km=%.1f vans=%d\n", n, s, c}'
```

## 9. Stan toru A (11:35)

`data.py` jest gotowy i zgodny z plikami w `fixtures/`. Tory B i C mogą importować `data` po scaleniu gałęzi `tor-a`; interfejs bez zmian względem sekcji 5. Komunikaty i raport są po angielsku.
