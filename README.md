# it-corner-hackaton-20260930

Materiały zespołu 9 z hackatonu „Which Vans Go Electric?” (30.09.2026): narzędzie, które z eksportu telematyki i rejestru vanów wybiera diesle do wymiany na elektryczne, oraz dokumenty opisujące, jak do tego doszliśmy.

Materiały źródłowe organizatorów: https://github.com/handsonarchitects/it-corner-hackathon-20260930

## Uruchomienie

Python 3.9 lub nowszy, bez dodatkowych pakietów. Dane źródłowe w sąsiednim katalogu `../it-corner-hackathon-20260930/`.

```
python3 ev_shortlist.py --trips ../it-corner-hackathon-20260930/trips.csv --vans ../it-corner-hackathon-20260930/vans.csv --params params.csv --out wyniki/
python3 -m unittest discover -s tests
```

Wynik: `shortlist.csv`, `summary.csv`, `all_vans.csv`, `data_report.txt` w katalogu `wyniki/`. Instrukcja dla analityka Ewy: `RERUN.md`.

## Od czego zacząć czytanie

| Chcesz wiedzieć | Plik |
|---|---|
| co rekomendujemy zarządowi | `BOARD_NOTE.md` |
| na jakich założeniach stoją liczby | `ASSUMPTIONS.md` |
| jak uruchomić narzędzie w kolejnym kwartale | `RERUN.md` |
| jak wyglądał proces, faza po fazie | `SDLC.md` |
| co ustaliliśmy i kiedy (założenia, decyzje, odpowiedzi Ewy, dziennik) | `HANDOFF.md` |
| który test pilnuje której reguły | `SLEDZENIE.md` |
| co tory przekazują sobie nawzajem (interfejsy, kolumny, wersje) | `KONTRAKT.md` |
| jak piszemy kod, komunikaty i dokumenty | `KONSTYTUCJA.md` |
| co robił każdy tor i jego dziennik | `TOR-A-dane.md`, `TOR-B-wykonalnosc.md`, `TOR-C-ekonomia-dokumenty.md` |
| plan prezentacji i demo | `PREZENTACJA.md` |

## Kod

| Plik | Co robi | Tor |
|---|---|---|
| `data.py` | czyści eksport, buduje profil vanów, liczy liczby kontrolne | A |
| `feasibility.py` | sprawdza zasięg, ładowność i ładowanie dla każdego vana | B |
| `economics.py` | liczy oszczędność w 5 lat | C |
| `ev_shortlist.py` | punkt wejścia: wybór modelu, ranking, zapis plików | B |
| `params.csv` | wszystkie ceny, stawki i progi; kod nie ma liczb na sztywno | A |
| `fixtures/` | pliki wzorcowe do testów i świeży eksport do próby ponownego uruchomienia | A |
| `tests/` | testy trzech torów (`unittest`) | A, B, C |

## Gałęzie

Pracujemy na `devel`; testy uruchamiają się automatycznie przy każdym wypchnięciu i w każdym PR (`.github/workflows/tests.yml`). `main` dostaje wydanie przez PR z `devel` — kroki w `SDLC.md`, sekcja 4.
