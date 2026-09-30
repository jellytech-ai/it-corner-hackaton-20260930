# HANDOFF — Which Vans Go Electric?

Dokument roboczy zespołu. Stan na **30.09.2026, 10:35 CEST**. Wersja 0.1 (wstępna).
To jest baza do dalszej analizy: każdą nową decyzję, założenie i odpowiedź Ewy dopisujemy tutaj.

> Materiały dla Ewy (`shortlist.csv`, `summary.csv`, notatka dla zarządu, instrukcja, lista założeń) piszemy **po angielsku**. Ten dokument jest wewnętrzny.

---

## 1. Zadanie

Pyrlandia Dostawy (fikcyjna firma, Poznań) ma 38 diesli w dwóch bazach: North (Suchy Las) i South (Luboń). Zarząd decyduje w przyszłym tygodniu, które vany jako pierwsze wymienić na elektryczne. Dotacja obejmuje do 10 EV, wnioski do 16.10.2026.

Oceniany jest **proces, nie aplikacja**. Prezentacja ok. 15 minut: najpierw proces, potem krótkie demo.

### Co dostarczamy (do wątku na Slacku)

| # | Rzecz | Uwagi |
|---|---|---|
| 1 | `shortlist.csv` | jeden wiersz na rekomendowany van, w kolejności rankingu; format w `README.md` |
| 2 | `summary.csv` | kolumny `figure,value`; trzy liczby kontrolne na górze |
| 3 | Notatka dla zarządu | jedna strona z uzasadnieniem |
| 4 | Narzędzie + instrukcja | skrypt, który analityk uruchomi za kwartał na świeżym eksporcie, bez nas |
| 5 | Lista założeń | co przyjęliśmy, mniej więcej kiedy, o co byśmy dopytali |

### Terminy

- **Rano:** pierwsza tura odpowiedzi Ewy (pytania wysłane przed pierwszym warsztatem).
- **Lunch:** podgląd dla CFO — bieżąca shortlista i co najmniej trzy liczby kontrolne. Druga tura odpowiedzi.
- **Przed prezentacjami:** komplet z tabeli powyżej.

### Format plików (skrót)

UTF-8 CSV, przecinek, wiersz nagłówka, kropka dziesiętna, bez separatorów tysięcy, PLN, km.

- `shortlist.csv`: `rank, van_id, ev_model, ev_depot, range_check_km (1 miejsce po przecinku), annual_km (int), annual_fuel_saving_pln (int), saving_pln (int), reason`
- `summary.csv`, w tej kolejności: `vans_assessed, trips_counted, total_km, recommended_count, annual_fuel_saving_pln, saving_pln, saving_basis`

---

## 2. Dane wejściowe

| Plik | Zawartość |
|---|---|
| `vans.csv` | rejestr 38 vanów: model, rok, baza, własność/leasing, koniec leasingu, rata, chłodnia, ładowność |
| (źródło) | pliki źródłowe leżą w repo organizatorów: https://github.com/handsonarchitects/it-corner-hackathon-20260930 |
| `trips.csv` | telematyka 15.06–12.09.2026 (README mówi „do 13.09”), 2999 wierszy: jeden kurs jednego vana jednego dnia |
| `ev_offers.md` | oferta dealera na dwa modele EV |
| `costs.md` | paliwo, serwis, taryfy prądu, ładowarki, skrót dotacji |
| `emails.txt` | wątek CFO / szef operacji / przedstawiciel kierowców |

### Parametry z `costs.md` i `ev_offers.md`

| Parametr | Wartość |
|---|---|
| Diesel | 5,20 PLN/l |
| Spalanie | Brona D35 9,6 · Brona D35 Long 10,9 · Kestrel Cargo 3.5 11,8 l/100 km |
| Serwis | diesel 0,34 PLN/km · EV 0,14 PLN/km |
| Prąd | noc (22–06) 0,58 PLN/kWh · dzień 0,92 PLN/kWh |
| Ładowarki | North: 6 punktów 22 kW AC · South: brak |
| Volta Cargo S | 260 km WLTP · 1050 kg · 24 kWh/100 km · 150 000 PLN lub 2 900 PLN/mies. |
| Volta Cargo L | 380 km WLTP · 880 kg · 27 kWh/100 km · 195 000 PLN lub 3 770 PLN/mies. |
| Leasing EV | 60 rat, bez wpłaty, bez wykupu, bez serwisu i energii |
| Ładowanie do pełna | Cargo S poniżej 5 h · Cargo L poniżej 7 h (22 kW AC) |

---

## 3. Ograniczenia od interesariuszy (`emails.txt`)

| Kto | Wymóg |
|---|---|
| Jolanta (CFO) | „vany, które jeżdżą najwięcej”, oszczędność na paliwie per van, liczby do sprawdzenia; 10 aut, jeśli się da; nie płaci za wyjście z leasingu, chyba że się opłaca; zakup czy leasing — otwarte |
| Witold (operacje) | **żaden van nigdy nie może zawieść trasy** (liczy się najgorszy dzień, nie średnia); WLTP to „liczba z broszury”, zwłaszcza w styczniu; EV musi unieść obecny ładunek; zarząd zapyta o koszt zakupu; bez zmian tras przed świętami, szczególnie dla vanów dwuzmianowych |
| Marek (kierowcy) | chłodnie: agregat pracuje cały kurs, w sierpniu na maksimum — wątpliwe na baterii; kierowca musi mieć pewność powrotu do bazy |
| Infrastruktura | North 6 punktów, South 0, a w South jest prawie połowa floty |

---

## 4. Jakość danych — co znaleźliśmy w `trips.csv`

| Problem | Skala | Wstępna decyzja |
|---|---|---|
| Pełne duplikaty wierszy | 222 (zostaje 2777) | usuwamy |
| `P-17` nie ma w rejestrze | 33 wiersze surowe, 30 dni od 15.06; `P-17B` jeździ od 03.08, ten sam kierowca (Waldemar Kasprzak) | traktujemy jako ten sam van (`P-17B`) — założenie A2 |
| Ujemny przebieg | 1 wiersz: P-27, 13.08, −208,6 km przy GPS 90,3 | **do decyzji:** podmiana na GPS albo wartość bezwzględna |
| Brak `gps_km` | 17 wierszy w danych surowych, 15 po deduplikacji (tyle podaje `data_report.txt`) | dystans bierzemy z licznika |
| Licznik dużo wyższy niż GPS | 250 wierszy, średnio o 27 km; tylko P-02, P-06, P-10, P-11, P-16, P-18 (trasy z ok. 34 przystankami) | ufamy licznikowi (GPS gubi dystans w gęstej zabudowie) |
| Dwie trasy dziennie | P-08, P-09, P-12, P-24, P-36 (ok. 60 dni każdy) | zasięg liczymy **na dzień**, nie na kurs |
| Tylko lato | brak danych z zimy; Ewa potwierdziła, że więcej danych nie ma | współczynnik zimowy z literatury (sekcja 6) |

### Liczby kontrolne (stan wstępny)

| Figura | Surowe | Po deduplikacji |
|---|---|---|
| `vans_assessed` | 39 identyfikatorów | **38** (jeśli P-17 = P-17B) |
| `trips_counted` | 2999 | **2777** |
| `total_km` (licznik) | 372 059 | **344 952** (wiersz P-27 z 13.08 liczony z GPS 90,3 km — reguła domyślna, do potwierdzenia w torze A) |

---

## 5. Profil floty (po deduplikacji, dystans z licznika)

Najgorszy dzień = najwyższa suma km jednego dnia. Km z 13 tygodni. P-27 zawiera jeszcze błędny ujemny wiersz.

| Van | Model | Baza | Chłodnia | Własność (koniec leasingu) | Dni | Km (13 tyg.) | Najgorszy dzień | Maks. ładunek kg | Dwie zmiany |
|---|---|---|---|---|---|---|---|---|---|
| P-01 | Brona D35 | North | nie | własny | 56 | 11 682 | 271 | 1086 | |
| P-02 | Brona D35 | South | nie | własny | 63 | 5 211 | 124 | 1071 | |
| P-03 | Kestrel | North | tak | własny | 69 | 7 947 | 153 | 1262 | |
| P-04 | Brona D35 | North | nie | leasing (05.2027) | 72 | 9 588 | 151 | 968 | |
| P-05 | Kestrel | South | nie | własny | 70 | 8 536 | 144 | 1041 | |
| P-06 | Brona D35 | North | nie | własny | 51 | 4 280 | 116 | 1062 | |
| P-07 | Kestrel | South | tak | własny | 68 | 8 424 | 164 | 1247 | |
| P-08 | Kestrel | North | nie | własny | 75 | 11 670 | 190 | 812 | tak |
| P-09 | Brona D35 | North | nie | własny | 71 | 15 486 | 261 | 790 | tak |
| P-10 | Brona D35 Long | South | nie | leasing (01.2027) | 55 | 5 358 | 144 | 936 | |
| P-11 | Brona D35 | North | nie | własny | 63 | 5 801 | 134 | 1118 | |
| P-12 | Kestrel | South | nie | własny | 75 | 12 288 | 201 | 838 | tak |
| P-13 | Brona D35 | North | nie | własny | 72 | 9 827 | 149 | 1031 | |
| P-14 | Brona D35 Long | North | nie | leasing (03.2027) | 56 | 5 623 | 148 | 1038 | |
| P-15 | Kestrel | South | nie | własny | 50 | 4 827 | 131 | 1196 | |
| P-16 | Kestrel | North | nie | własny | 75 | 10 653 | 174 | 1018 | |
| P-17 | (brak w rejestrze) | ? | ? | ? | 30 | 3 369 | 150 | 1104 | |
| P-17B | Brona D35 | South | nie | własny | 32 | 3 542 | 158 | 1094 | |
| P-18 | Brona D35 | South | nie | własny | 55 | 5 210 | 124 | 1057 | |
| P-19 | Kestrel | North | tak | własny | 75 | 9 804 | 150 | 996 | |
| P-20 | Brona D35 Long | South | nie | leasing (11.2028) | 70 | 9 014 | 142 | 924 | |
| P-21 | Brona D35 Long | North | nie | własny | 71 | 9 670 | 159 | 941 | |
| P-22 | Brona D35 | North | nie | własny | 67 | 7 186 | 150 | 1097 | |
| P-23 | Kestrel | South | tak | własny | 65 | 7 779 | 148 | 1271 | |
| P-24 | Brona D35 Long | North | nie | własny | 68 | 17 560 | 302 | 846 | tak |
| P-25 | Brona D35 Long | South | nie | leasing (04.2028) | 72 | 9 686 | 148 | 1003 | |
| P-26 | Brona D35 Long | North | nie | leasing (06.2028) | 72 | 8 580 | 142 | 957 | |
| P-27 | Brona D35 | South | nie | własny | 57 | 5 575 | 157 | 1093 | |
| P-28 | Brona D35 Long | North | nie | leasing (11.2026) | 49 | 5 374 | 160 | 976 | |
| P-29 | Brona D35 Long | South | nie | leasing (06.2029) | 57 | 12 208 | 271 | 1019 | |
| P-30 | Kestrel | North | nie | własny | 71 | 9 394 | 166 | 997 | |
| P-31 | Brona D35 | South | nie | własny | 73 | 9 626 | 150 | 977 | |
| P-32 | Brona D35 Long | South | nie | leasing (08.2027) | 52 | 5 862 | 149 | 1041 | |
| P-33 | Brona D35 Long | North | nie | leasing (09.2028) | 76 | 14 314 | 208 | 962 | |
| P-34 | Kestrel | South | tak | własny | 66 | 7 734 | 157 | 1258 | |
| P-35 | Kestrel | North | tak | własny | 65 | 7 296 | 144 | 1284 | |
| P-36 | Brona D35 Long | South | nie | leasing (02.2028) | 68 | 14 347 | 253 | 998 | tak |
| P-37 | Brona D35 Long | North | nie | leasing (03.2029) | 58 | 12 259 | 264 | 1011 | |
| P-38 | Brona D35 | South | nie | własny | 58 | 12 062 | 285 | 1129 | |

Obserwacje:

- Każdy van jeździ stałą trasą (dwuzmianowe — dwiema). Średni dystans kursu jest płaski od czerwca do września (122–125 km).
- Vany o największym przebiegu (największa oszczędność na paliwie — tego chce CFO) to te same, które mają najdłuższe dni (największe ryzyko zasięgu — tego boi się Witold). To jest sedno sporu z maili.

---

## 6. Założenia (rejestr)

Każde założenie ma godzinę przyjęcia; Ewa chce wiedzieć „co i mniej więcej kiedy”.

| # | Kiedy (30.09) | Założenie | Status |
|---|---|---|---|
| A1 | 10:15 | Pełne duplikaty wierszy usuwamy | przyjęte |
| A2 | 10:42 | P-17 i P-17B to ten sam van; łączymy pod `P-17B`. Dowody: ta sama trasa (S-R06, nikt inny jej nie jeździ), ten sam kierowca, P-17 kończy się 31.07, P-17B zaczyna 03.08, średni dystans 112 i 111 km, rejestr ma 38 vanów jak w liście Ewy | przyjęte; **potwierdzone przez Ewę** (P-17 skasowany pod koniec lipca, P-17B przejął trasy) |
| A3 | 10:15 | Dystans = `odometer_km`; GPS tylko pomocniczo | przyjęte; **potwierdzone przez Ewę** („Trust the odometer”) |
| A4 | 10:15 | Test zasięgu na **najgorszym dniu** (suma kursów dnia), nie na średniej | **zmienione → A19** (reguła Ewy: 95. percentyl dnia) |
| A5 | 10:15 / 11:25 | Wiersz P-27 z 13.08 (−208,6 km) jest błędem; liczymy go z `gps_km` (90,3 km). Reguła ogólna: licznik ≤ 0 lub pusty → GPS, z ostrzeżeniem w raporcie | przyjęte (tor A, D8) |
| A6 | 10:30 | Zasięg zimowy = **0,57 × WLTP** (Cargo S ok. 148 km, Cargo L ok. 217 km); warianty 0,50 i 0,65 | **zmienione → A19** (reguła Ewy: 0,60 × WLTP) |
| A7 | 10:30 | Po 5 latach (koniec leasingu EV) dodatkowo × 0,87 → 0,49 × WLTP (S ok. 128 km, L ok. 187 km) | pokazujemy w notatce jako test odporności |
| A8 | 10:30 | Zużycie energii: liczby dealera + 10% rocznie na zimę | przyjęte |
| A9 | 10:30 | Ładowność: maks. zaobserwowany `max_load_kg` vana ≤ ładowność EV; bez narzutu sezonowego (brak źródła) | przyjęte; decyzja D3 |
| A10 | 10:42 | Chłodnie (P-03, P-07, P-19, P-23, P-34, P-35) wykluczone z pierwszej tury | decyzja D1; **potwierdzone przez Ewę** („out for year 1”) |
| A11 | 10:30 | Ewa nie ma danych z zimy ani innych danych — nie pytamy o nie | potwierdzone |
| A12 | 10:50 | Sezonowość: trasy i ładunki są takie same przez cały rok. Roczne km = km z 13 tygodni × 4; zimowy najgorszy dzień i maks. ładunek = letnie z danych. Przesłanki: każdy van jeździ jedną stałą trasą (dwuzmianowe — dwiema), średni dystans kursu jest płaski przez 4 miesiące (122–125 km), Witold pisze o utrzymaniu tras bez zmian. Ryzyko: szczyt przedświąteczny — sprawdzi to ponowne uruchomienie narzędzia na eksporcie za IV kwartał | przyjęte (nie pytamy Ewy) |
| A13 | — | Ładowanie nocne w taryfie 0,58 PLN/kWh; jeden punkt = jeden van | do potwierdzenia (vany dwuzmianowe wracają ok. 20:40, startują ok. 04:30) |
| A14 | — | Limit EV w North = 6 (liczba punktów), South = 0 | **zmienione → A20** (odpowiedź Ewy) |
| A16 | 10:50 | Vany dwuzmianowe (świt + popołudnie: P-08, P-09, P-12, P-24, P-36) doładowują się w bazie między trasami z punktu 22 kW. Zimą daje to ok. 58 km zasięgu na godzinę ładowania dla Cargo S i ok. 51 km dla Cargo L; odliczamy 15 min na podłączenie. Test: pierwsza trasa ≤ zasięg zimowy oraz stan po doładowaniu ≥ druga trasa, dla każdego dnia z danych. Wymaga: powrotu do bazy między trasami, wolnego punktu w dzień, energii w taryfie dziennej (0,92 PLN/kWh) | **zmienione → A21** (Ewa: brak czasu na ładowanie) |
| A17 | 11:13 | Analityk Ewy jest osobą techniczną i ma Pythona 3; uruchamia skrypt z wiersza poleceń i edytuje `params.csv` | przyjęte (niepotwierdzone przez Ewę); **do wpisania w odpowiedzi dla Ewy** — sekcja 7 |
| A18 | 12:12 | Struktura danych się nie zmieni: kolejny eksport ma te same pliki (`trips.csv`, `vans.csv`) i te same nazwy kolumn co dzisiejszy. Zmieniają się tylko wiersze i okres. Gdy kolumny brakuje, narzędzie zatrzymuje się z komunikatem `ERROR: … missing column(s) …` | przyjęte; **do wpisania w odpowiedzi dla Ewy** — sekcja 7 |
| A15 | 11:26 | Podstawa `saving_pln` = **wariant 1, tylko eksploatacja, rocznie**: (koszt diesla − koszt ładowania) + (serwis diesla − serwis EV), z `params.csv`. Nie wliczamy raty leasingu ani ceny zakupu EV, rat diesla ani dotacji. Serwis: diesel 0,34 PLN/km (dane firmy, jedna stawka niezależnie od rocznika), EV 0,14 PLN/km (**szacunek dealera**); w `vans.csv` brak kosztów serwisu per van. `annual_fuel_saving_pln` zostaje czystą różnicą paliwo − ładowanie | **zmienione → D13** (reguła Ewy: 5 lat) |
| A19 | 12:15 | **Reguła zasięgu Ewy:** van przechodzi, jeśli jego dzień z 95. percentyla (percentyl dziennych sum km, interpolacja liniowa jak `PERCENTILE.INC`) mieści się w **0,60 × WLTP** (Cargo S 156 km, Cargo L 228 km). Zastępuje A4 i A6; nasz rozkład 0,57 zostaje w notatce jako uzasadnienie, że 0,60 to rozsądny kompromis | potwierdzone przez Ewę |
| A20 | 12:15 | Ładowanie: North 10 punktów (6 + 4 zamówione, gotowe przed dostawą EV), jeden EV na punkt; South bez ładowarek w pierwszym roku; do 3 vanów z South może stacjonować w North, trasy bez zmian, bez doliczania dojazdu | potwierdzone przez Ewę |
| A21 | 12:15 | Vany dwuzmianowe nie ładują się między trasami („only come back for a driver change”); cały dzień na jednym ładowaniu nocnym | potwierdzone przez Ewę |
| A23 | 12:29 | Gdy z South pasuje więcej vanów, niż może stacjonować w North (`max_south_vans_at_north` = 3), bierzemy te z najwyższym `saving_pln`. Dziś odpada P-31 (+1 589 PLN w 5 lat) | przyjęte (Q22 toru B) |
| A24 | 12:29 | `annual_km` = km z okresu × 365 ÷ liczba dni kalendarzowych okresu (90), niezależnie od liczby dni pracy vana. Van, który w 13 tygodni jeździł 75 dni, jeździ tak samo przez cały rok (A12) | przyjęte (Q14 toru B; doprecyzowanie A12 i D5) |
| A25 | 15:12 | Zapisany ładunek kursu (`max_load_kg`) to sam towar, bez kierowcy; dealer podaje ładowność EV „z kierowcą na pokładzie”, więc porównujemy wprost i nic nie doliczamy | przyjęte (Ewa 15:12: „Pick the one that makes sense and put it in your assumptions list”) |
| A22 | 12:17 | Wcześniejsze wyjście z leasingu diesla = 3 raty; leasing kończący się w ciągu 12 miesięcy od `lease_reference_date` (dziś 2026-09-30) — bez opłaty (nie odnawiamy). Granica „w ciągu 12 miesięcy” liczona włącznie (koniec 2027-09-30 = bez opłaty) | reguła potwierdzona przez Ewę; granica włącznie — nasza decyzja |

### Skąd 0,57 × WLTP (A6–A8)

| Czynnik | Wartość | Uzasadnienie | Źródło |
|---|---|---|---|
| Dzień projektowy | −10°C | Poznań: średnie minimum stycznia −3°C, „rzadko poniżej −12°C” | Weather Spark |
| Temperatura | × 0,70 | średnio 78% zasięgu przy 0°C i 70% przy ok. −7°C (ponad 30 tys. aut); pompa ciepła ok. +10% | Recurrent |
| Temperatura, skrajność | wariant × 0,55 | średnio 54% zasięgu znamionowego przy −15°C (4200 aut, 5,2 mln przejazdów) | Geotab / Electric Autonomy |
| Ładunek | × 0,90 | van średniej wielkości: −7% przy połowie ładunku, −11% przy pełnym | Arval / What Van? |
| Rezerwa na powrót | × 0,90 | założenie operacyjne zespołu, bez źródła zewnętrznego | — |
| Degradacja | × 0,87 po 5 latach | vany: średnio 2,7% rocznie (22,7 tys. aut) | Geotab 2026 |
| Energia zimą | +10% rocznie | zima ok. 3,7 mies. przy ok. 0°C → +28% zużycia w tym okresie | wyliczenie własne z Recurrent i Weather Spark |

Zastrzeżenia:

- Recurrent porównuje z zasięgiem w idealnych warunkach, Geotab ze znamionowym (prawdopodobnie EPA — nasz wniosek). Żadne nie mierzy wprost względem WLTP.
- Oba duże badania temperatury dotyczą głównie aut osobowych; praca dostawcza z 20–35 przystankami może wypaść gorzej.
- Mnożenie czynników zakłada, że najdłuższy dzień trafi na najzimniejszy. To celowo ostrożne.
- Dwie liczby zgodne z naszym wynikiem znamy tylko z wyników wyszukiwania (stron nie otwieraliśmy): vany tracą 20–35% poniżej 5°C; mróz z pełnym ładunkiem to ok. 50% WLTP (OVL Group, Motorwatt).

Linki:

- https://www.recurrentauto.com/research/winter-ev-range-loss
- https://electricautonomy.ca/2020/05/26/affect-of-temperature-on-ev-range/
- https://www.geotab.com/blog/ev-range-impact-of-speed-and-temperature/
- https://www.whatvan.co.uk/news/effects-of-payload-and-towing-on-electric-van-range-revealed-by-arval-research/
- https://www.geotab.com/blog/ev-battery-health/
- https://pl.weatherspark.com/y/81756/%C5%9Arednie-warunki-pogodowe-w:-Pozna%C5%84-Polska-w-ci%C4%85gu-roku
- https://www.ovl.co.uk/news/electric-van-range-vs-payload-business-guide (tylko wynik wyszukiwania)
- https://motorwatt.com/ev-blog/reviews/electric-delivery-van-range-comparison-2025 (tylko wynik wyszukiwania)

---

## 7. Pytania do Ewy (limit: 5)

Propozycja z 10:53. Pytania 1–4 uzgodnione, pytanie 5 jest kandydatem do zatwierdzenia.

| # | Pytanie | Co od niego zależy | Co przyjmiemy bez odpowiedzi |
|---|---|---|---|
| 1 | **Ładowanie:** czy North zostaje przy 6 punktach, czy można dobudować (także w South)? Czy EV może stacjonować w North, a wycofany zostanie diesel z South? | liczba aut (3, 6 czy 10) i to, czy South w ogóle wchodzi w grę | North maks. 6, South 0 (A14) |
| 2 | **Dotacja:** ile na van, czy obejmuje leasing, czy tylko zakup, i czy wymaga wycofania konkretnego diesla? | `saving_pln`, wybór zakup/leasing | oszczędność liczona bez dotacji, pokazana osobno |
| 3 | **Próg zimowy:** czy Witold zaakceptuje ok. 57% WLTP jako „zasięg zimowy”? Czy dealer poda pojemność baterii i informację o pompie ciepła? | próg testu zasięgu, czyli cała shortlista | 0,57 z wariantami 0,50 i 0,65 (A6) |
| 4 | **Leasing:** ile kosztuje wcześniejsze zakończenie leasingu diesla i kiedy realnie EV mogłyby wejść do floty? | P-26 (do 06.2028) i P-14 (do 03.2027), czyli dwa z trzech vanów przechodzących w North | do zapłaty zostają wszystkie pozostałe raty |
| 5 | *(kandydat)* **Zastępowany diesel:** sprzedaż (za ile) czy rezerwa? | `saving_pln` dla vanów własnych; rezerwa odpowiada na obawę o dzień, w którym EV nie da rady | bez wartości odsprzedaży, diesel wycofany |

Uwaga: pytanie 3 jest najsłabsze (Ewa w trasie raczej nie zapyta Witolda ani dealera) — do rozważenia zamiana na założenie.

### Wersja do wklejenia na Slacku (EN)

1. Charging: is North fixed at 6 points, or can more be added (also at South)? Can an EV be based at North while the diesel we retire is a South van?
2. Grant: how much per van, does it cover leasing or purchase only, and does it require retiring a specific diesel?
3. Winter range: we plan to use about 57% of WLTP as the worst-day winter range (Cargo S about 148 km, Cargo L about 217 km). Is that acceptable to Witold? Can the dealer give battery capacity and whether the vans have a heat pump?
4. Diesel leases: what does early termination cost, and when could the EVs realistically enter the fleet?
5. Replaced diesels: are they sold (at what value) or kept as spares?

Status: **wysłane 30.09 ok. 11:09**, czekamy na odpowiedzi. Odpowiedzi wpisać do sekcji 10.

Jeśli Ewa nie odpowie na czas: działamy na założeniach z sekcji 6 i zapisujemy to wprost.

### Odpowiedź dla Ewy o analityku i podgląd dla CFO — **wysłane 30.09, 13:02**

Wysłane jako komentarz w wątku „9”: https://github.com/handsonarchitects/it-corner-hackathon-20260930/discussions/4#discussioncomment-18677756

Wysłana wersja zawiera tekst poniżej oraz, przed nim, podgląd dla CFO: rekomendację (8 EV, 95 637 PLN w 5 lat) i zawartość `summary.csv` i `shortlist.csv` z `devel` a767bdc. Wpis Ewy z 12:03 chwilowo zniknął (problem z jej kontem), więc odpowiedź poszła jako komentarz najwyższego poziomu.

Ewa zapytała o 12:03: „my analyst will rerun this next quarter without you. What will they open, and what will they type?”. W odpowiedzi w naszym wątku muszą się znaleźć trzy rzeczy o analityku oraz (uzgodnione 12:52) decyzja o 8 vanach zamiast 10:

| # | Co wpisać | Założenie |
|---|---|---|
| 1 | Analityk ma zainstalowanego Pythona 3 (3.9 lub nowszy); niczego więcej nie instaluje | A17 |
| 2 | Dostarczamy README (`RERUN.md`) z instrukcją uruchomienia skryptu krok po kroku: co otworzyć, co wpisać, co sprawdzić | D5, D6 |
| 3 | Struktura danych się nie zmieni: te same dwa pliki CSV z tymi samymi kolumnami; gdy kolumny zabraknie, skrypt powie której | A18 |

Szkic odpowiedzi (EN), do wklejenia po uzgodnieniu:

```
Hi Ewa,

Your analyst opens one folder and types one command.

What they open: the folder we post here as a zip. It holds the script, a
parameter file (params.csv) and a README.

What they type:
  python3 ev_shortlist.py --trips trips.csv --vans vans.csv --params params.csv --out results/

What they get: shortlist.csv and summary.csv in your import format, plus a
list of every van with the reason it is in or out, and a data report that
says what was cleaned. The three check figures are printed on screen.

We are assuming four things. Tell us if any is wrong:
1. Your analyst has Python 3 installed (3.9 or newer). Nothing else needs
   installing.
2. The README (RERUN.md) is what they follow. It says step by step what to
   open, what to type and what to check, including which prices and dates
   to update in params.csv each quarter.
3. The data keeps its structure: the same two CSV files with the same
   column names as today. If a column is missing, the script stops and
   names it; it never guesses.
4. We shortlist only vans that pay back within the five years. That gives
   8 vans, not 10. The ninth would lose about 6,900 PLN over five years.
   Tell us if the board would rather use all ten grant places.

Thanks,
JellyTech
```

---

## 8. Wstępny obraz wykonalności (ręczny odczyt z tabeli, do potwierdzenia skryptem)

> **Nieaktualne od 12:15** — obraz sprzed odpowiedzi Ewy (0,57 × WLTP, najgorszy dzień, doładowanie między trasami, 6 punktów). Obowiązują A19–A24 i D13–D16; aktualny wynik: `TOR-B-wykonalnosc.md` (B10). Sekcja zostaje jako zapis rozumowania.

Filtry: nie chłodnia · maks. ładunek ≤ ładowność EV · najgorszy dzień ≤ zasięg zimowy (S 148 km, L 217 km).

| Baza | Przechodzą | Tuż za progiem |
|---|---|---|
| North | P-26 (Cargo S), P-14 (Cargo S, dokładnie na progu), P-08 (Cargo S z doładowaniem między trasami albo Cargo L bez) | P-13 (149 km), P-04 (151 km), P-06 (ładunek 1062 kg), P-21 (159 km) |
| South (brak ładowarek) | P-20, P-05, P-10, P-25 (Cargo S), P-12 (Cargo S z doładowaniem albo Cargo L bez) | P-32 (149 km), P-31 (150 km), P-02 i P-18 (ładunek 1057–1071 kg) |

### Vany dwuzmianowe z doładowaniem między trasami (założenie A16)

Symulacja na wszystkich dniach z dwiema trasami, próg 0,57 × WLTP, 15 min na podłączenie. „Dni nieudane” = dni, w których zabrakłoby zasięgu.

| Van | Baza | Dni | Cargo S: dni nieudane | Cargo L: dni nieudane | Ładunek |
|---|---|---|---|---|---|
| P-08 | North | 63 | **0** | 0 | 812 kg — oba modele |
| P-12 | South | 63 | **0** | 0 | 838 kg — oba modele |
| P-09 | North | 60 | 26 | 2 | 790 kg — oba modele |
| P-36 | South | 61 | 11 | 0 | 998 kg — tylko Cargo S |
| P-24 | North | 62 | 43 | 9 | 846 kg — oba modele |

- P-08 i P-12 mieszczą się już w tańszym Cargo S (150 000 zamiast 195 000 PLN). Bez doładowania Cargo S nie wystarcza na żaden dzień z dwiema trasami.
- P-09 na Cargo L zawodzi w 2 dniach z 60 (przerwa 21 i 24 min) — przy zasadzie „nigdy” odpada.
- P-36 zasięgowo pasuje do Cargo L, ale ma ładunek 998 kg (limit 880 kg); na Cargo S zawodzi 11 dni.
- Przy progu 0,49 (po 5 latach) P-08 i P-12 na Cargo S zawodzą po 1 dniu.
- Nie wiemy, czy vany faktycznie wracają do bazy między trasami — dane pokazują tylko godziny końca i startu.

Wnioski wstępne:

- Przy ostrych filtrach w North przechodzą **tylko ok. 3 vany**, a nie 6 ani 10. Wynik jest bardzo wrażliwy na próg: przy 0,65 × WLTP (169 km) dochodzi kilka kolejnych.
- Ładowność Cargo S (1050 kg) odcina vany, których maksymalny ładunek przekroczył próg o kilkanaście kg jednego dnia. Warto sprawdzić, jak często to się zdarza (percentyl zamiast maksimum?) — ale to kłóci się z zasadą „nigdy”.
- Żaden van z długimi dniami (powyżej 250 km) nie mieści się w żadnym wariancie. Propozycja CFO („te, które jeżdżą najwięcej”) jest niewykonalna bez zmiany tras.
- Leasingi kończące się wkrótce: P-28 (11.2026), P-10 (01.2027), P-14 (03.2027), P-04 (05.2027). Z nich P-14 przechodzi filtry, P-10 jest w South, P-04 i P-28 są tuż za progiem zasięgu.

---

## 9. Plan (3 deweloperów, praca równoległa)

Stan na 11:10. Kroki 1–3 z wersji 0.1 (repo, profil danych, założenia zimowe) są zrobione; pytania do Ewy gotowe do wysłania.

### Dokumenty robocze torów

| Plik | Dla kogo |
|---|---|
| `KONTRAKT.md` | wszyscy: stanowisko pracy, własność plików, interfejsy, schematy tabel, godziny scalania |
| `TOR-A-dane.md` | tor A: zadania z godzinami, reguły czyszczenia, decyzje |
| `TOR-B-wykonalnosc.md` | tor B: filtry, ranking, eksport, integracja |
| `TOR-C-ekonomia-dokumenty.md` | tor C: formuły, podstawa `saving_pln`, dokumenty |
| `params.csv` | wspólne parametry (właściciel: A) |
| `fixtures/` | pliki testowe w formacie kontraktu — B i C pracują na nich od razu |

### Krok 0 — wspólny kontrakt (wszyscy, 15 min)

Bez tego tory nie są niezależne. Ustalamy i zapisujemy:

- **`config`** (plik `params.csv`) — jeden plik z parametrami (ceny, spalanie, współczynnik zimowy, ładowność i zasięg EV, liczba punktów ładowania, mapowanie P-17 → P-17B).
- **`van_profile`** — tabela pośrednia, jeden wiersz na van: `van_id, model, depot, refrigerated, ownership, lease_end, monthly_lease_pln, days, km_13w, worst_day_km, max_load_kg, two_shift`. Tor A ją produkuje, tory B i C ją czytają.
- **`feasibility`** — wynik toru B: `van_id, feasible, ev_model, ev_depot, range_check_km, reject_reason`. Tor C ją czyta.
- Do czasu, aż tor A odda prawdziwe dane, B i C pracują na tabeli z sekcji 5 jako danych testowych.
- Jeden plik `ev_shortlist.py` bez zewnętrznych bibliotek; tory pracują nad osobnymi funkcjami i scalają je do tego pliku (szczegóły w „Narzędzie dla analityka”).

### Trzy tory

| Tor | Zakres | Wynik | Zależy od |
|---|---|---|---|
| **A — Dane** | wczytanie, czyszczenie (duplikaty, P-17, wiersz P-27, dystans z licznika), agregacja do dnia, raport z czyszczenia, trzy liczby kontrolne | `van_profile`, oczyszczone kursy, pierwsze trzy wiersze `summary.csv` | tylko kontrakt |
| **B — Wykonalność** | filtry: zasięg zimowy na najgorszym dniu, ładowność, chłodnie, baza i limit punktów; symulacja doładowania między trasami (A16); dobór modelu S/L; analiza wrażliwości 0,50 / 0,57 / 0,65 | `feasibility`, tabela wrażliwości, lista „blisko progu” | kontrakt; dane testowe z sekcji 5 |
| **C — Ekonomia i dokumenty** | roczne km, paliwo minus ładowanie (z +10% na zimę i taryfą dzienną dla doładowań), serwis, zakup/leasing, koszt wyjścia z leasingu, `saving_basis`; notatka dla zarządu, lista założeń i instrukcja (EN) | oszczędności per van, szkice dokumentów | kontrakt; dane testowe z sekcji 5 |

Integracja (ranking i eksport `shortlist.csv` + `summary.csv`) należy do toru B, bo jest końcem potoku. Dokumenty należą do toru C.

### Harmonogram — twardy termin: koniec przed 16:00

Założenie: lunch ok. 13:00 (godzina niepotwierdzona — jeśli jest inna, przesuwamy M1 i M2, reszta zostaje).

| Godzina | Kamień | Co | Kto |
|---|---|---|---|
| 11:10–11:25 | M0 | kontrakt (`config`, `van_profile`, `feasibility`), podział torów | wszyscy |
| do 11:50 | | trzy liczby kontrolne gotowe i przeliczone drugi raz | A + osoba z B lub C |
| do 12:30 | M1 | częściowa shortlista i `summary.csv` w wątku — podgląd dla CFO | A liczby, B shortlista, C oszczędność na paliwie |
| 12:30–13:00 | | pełny potok działa jednym poleceniem na prawdziwych danych | B integruje |
| 13:00–13:30 | | lunch, odpowiedzi Ewy | |
| 13:30–14:00 | M2 | odpowiedzi Ewy naniesione na `config` i założenia; ponowne uruchomienie | wszyscy |
| 14:00–14:45 | | analiza wrażliwości, pełna ekonomia, szkic notatki i instrukcji | B, C; A pomaga C przy dokumentach |
| **14:45** | **zamrożenie liczb** | po tej godzinie zmieniamy tylko błędy, nie założenia | wszyscy |
| 14:45–15:15 | | test ponownego uruchomienia przez osobę, która nie pisała skryptu; notatka i założenia (EN) na czysto | A testuje, C pisze |
| 15:15–15:40 | M3 | komplet w wątku: oba CSV, notatka, instrukcja, założenia | wszyscy |
| 15:40–16:00 | | prezentacja procesu (kto mówi co) i zapas | wszyscy |

### Co tniemy, jeśli brakuje czasu (w tej kolejności)

1. Plik XLSX obok CSV (mile widziany, nie wymagany; nie jest potrzebny jako zamiennik skryptu — A17).
2. Wariant po 5 latach degradacji (0,49) — zostaje jedno zdanie w notatce.
3. Pełne porównanie zakup/leasing — zostaje jeden wariant z opisaną podstawą w `saving_basis`.
4. Analiza wrażliwości skrócona do trzech progów bez osobnych tabel per van.

Nie tniemy: liczb kontrolnych, formatu obu CSV, instrukcji uruchomienia, listy założeń z godzinami.

### Zabezpieczenia

- **Liczby kontrolne liczone dwa razy.** CFO sprawdza je najpierw, więc osoba spoza toru A przelicza je niezależnie, inną metodą.
- **Test ponownego uruchomienia.** Przed M3 ktoś, kto nie pisał skryptu, uruchamia go z samej instrukcji na zmienionym eksporcie (np. obciętym do 6 tygodni, z nowym nieznanym `van_id`).
- **Jeden właściciel rejestru założeń.** Tor C dopisuje każdą decyzję z godziną do sekcji 6 i 10; pozostali zgłaszają je od razu.
- **Parametry tylko w `config`.** Odpowiedzi Ewy po lunchu mają się sprowadzać do zmiany wartości, nie kodu.

### Narzędzie dla analityka

Co mówi README:

| Wymóg | Cytat | Wniosek |
|---|---|---|
| Ponowne uruchomienie | „Something I can rerun next quarter on a fresh export. My analyst will rerun this next quarter without you.” | działa na innym okresie i innych danych, bez naszej pomocy |
| Forma | „A script is enough.” | bez interfejsu i serwera |
| Pokaz | „show me it rerunning, and post the instructions to run it” | pokazujemy uruchomienie, instrukcja trafia do wątku |
| Komplet | „Whatever my analyst needs to rerun it without you.” | skrypt, parametry, instrukcja, założenia |
| Dostawa | „Everything you deliver goes into your thread. Sharing your code or repository is voluntary.” | wszystko musi dać się wrzucić na Slacka jako pliki |
| Ocena | „The focus of today is your process, not the app.” | demo krótkie, większość czasu na proces |

Decyzje projektowe (D5, 11:13):

- **Jeden plik `ev_shortlist.py`, tylko biblioteka standardowa Pythona.** Bez instalacji; da się wkleić do wątku.
- **Parametry w `params.csv`** (kolumny `parameter,value`): ceny, spalanie, dane EV, współczynnik zimowy, liczba punktów ładowania, mapowanie P-17 → P-17B. Analityk edytuje je w Excelu, nie w kodzie.
- **Jedno polecenie:** `python3 ev_shortlist.py --trips trips.csv --vans vans.csv --params params.csv --out wyniki/`
- **Wyniki:** `shortlist.csv`, `summary.csv`, `all_vans.csv` (każdy van z powodem przyjęcia lub odrzucenia), `data_report.txt` (co wyczyszczono).
- **Roczne km z długości okresu w danych**, nie ze stałego mnożnika × 4 (doprecyzowanie A12) — następny eksport może mieć inną liczbę tygodni.
- **Ostrzeżenia zamiast cichych poprawek:** nieznany `van_id`, ujemny przebieg, brak kolumny, duplikaty — wszystko trafia do `data_report.txt`.
- **Liczby kontrolne na ekranie** po każdym uruchomieniu.
- Zakładamy, że analityk jest osobą techniczną i ma Pythona 3 (A17), więc nie robimy wariantu zapasowego w XLSX.

Do wątku trafia: `ev_shortlist.py`, `params.csv`, `RERUN.md` (krótka instrukcja po angielsku), lista założeń, wynik uruchomienia jako dowód.

### Prezentacja (15 min)

Podział: ok. 10 min proces, 3 min demo, 2 min zapasu.

Proces:

- dokument handoff jako żywy dziennik decyzji,
- selekcja pytań do Ewy: które odpadły i dlaczego (P-17 i chłodnie rozstrzygnięte z danych),
- założenia z godzinami i źródłami (współczynnik zimowy),
- liczby kontrolne liczone dwa razy,
- trzy równoległe tory z kontraktem.

Demo w trzech krokach:

1. Uruchomienie na oryginalnym eksporcie — wynik zgodny z plikami w wątku.
2. Zmiana jednego parametru w `params.csv` (np. próg zimowy 0,57 → 0,65) i ponowne uruchomienie — shortlista się zmienia.
3. Uruchomienie na „świeżym eksporcie” (spreparowany plik z innym okresem i nieznanym vanem) — skrypt przelicza roczne km i zgłasza ostrzeżenie. Plik powstaje przy teście ponownego uruchomienia o 14:45.

---

## 10. Otwarte decyzje i dziennik

### Podjęte decyzje

| # | Kiedy (30.09) | Decyzja | Uzasadnienie |
|---|---|---|---|
| D1 | 10:42 | Chłodnie nie wchodzą do pierwszej tury; nie pytamy o nie Ewy | 5 z 6 chłodni wozi ponad 1050 kg przez 22–40 dni w kwartale (maks. 1247–1284 kg), więc odpadają na ładowności obu modeli EV niezależnie od agregatu. Zostaje tylko P-19 (maks. 996 kg), ale ma najgorszy dzień 150 km, ponad próg 148 km. Oferta dealera nie zawiera wersji chłodni, a kierowca P-35 zgłasza wątpliwości co do agregatu na baterii. |
| D2 | 10:42 | P-17 łączymy z P-17B bez pytania Ewy | patrz założenie A2 |
| D3 | 10:50 | Ładowność EV to twardy limit, sprawdzany na maksimum z danych; nie pytamy Ewy i nie proponujemy rozkładania ładunku na dwa auta | Ładowność znamionowa to granica prawna; Witold: EV „musi unieść to, co vany wożą dziś”; rozłożenie ładunku oznacza zmianę tras i dodatkowy kurs. Vany odpadające przez pojedyncze dni powyżej 1050 kg (P-06, P-02, P-18: 1 dzień; P-22: 2; P-11: 3) pokazujemy w notatce jako „blisko progu” |
| D4 | 10:50 | Sezonowość przyjmujemy jako założenie A12, bez pytania Ewy | Ewa nie ma danych z zimy; narzędzie zweryfikuje to na eksporcie za IV kwartał |
| D5 | 11:13 | Narzędzie to jeden plik `ev_shortlist.py` bez zależności, z parametrami w `params.csv`; roczne km liczone z długości okresu w danych | Ewa: „a script is enough”, materiały idą do wątku jako pliki, analityk uruchamia bez nas |
| D7 | 11:26 | `saving_pln` liczymy jako roczną oszczędność eksploatacyjną: paliwo − ładowanie + różnica serwisu (wariant 1 z `TOR-C`); `saving_basis` opisuje to jednym zdaniem po angielsku | proste i sprawdzalne dla CFO z samych stawek w `params.csv`; nie wymaga założeń o dotacji, wyjściu z leasingu ani racie nowego diesla. Pełny koszt (leasing EV ok. 34 800 PLN/rok przy ok. 14 000 PLN oszczędności) opisujemy w notatce dla zarządu, żeby nie było wrażenia, że wymiana „zarabia” |
| D8 | 11:25 | Licznik ≤ 0 lub pusty → `gps_km` z ostrzeżeniem; brak obu → wiersz odrzucony z ostrzeżeniem | nie gubimy kursu po cichu; tak są policzone liczby kontrolne (344 952 km) |
| D9 | 11:25 | Kursy vana spoza rejestru (po aliasach) nie wchodzą do liczb; ostrzeżenie mówi, co dopisać do `vans.csv` lub `van_alias` | następny eksport może mieć nowego vana; analityk ma to zobaczyć, a nie dostać cicho zmienione liczby |
| D10 | 11:25 | `vans_assessed` = vany z rejestru z co najmniej jednym kursem; van bez kursów dostaje ostrzeżenie | liczba kontrolna musi odpowiadać temu, co naprawdę oceniliśmy |
| D11 | 11:35 | Raport i komunikaty narzędzia są po angielsku | czyta je analityk Ewy |
| D12 | 11:50 | Wspólne zasady języka, błędów, liczb, CSV i gita w `KONSTYTUCJA.md` (m.in. angielski dla analityka, `ERROR:` bez śladu stosu, `WARNING:` w raporcie, liczby kontrolne na ekranie, słownik pojęć). Pierwszeństwo: README Ewy > konstytucja > `KONTRAKT.md`. 11:44 tor C dopisał: każdy nowy komunikat ma wiersz w `RERUN.md` | analityk ma naprawić problem bez czytania kodu i bez nas (A17); dokumenty mają wyglądać jak dzieło jednego zespołu |
| D13 | 12:17 | `saving_pln` = 5 × (paliwo − ładowanie + różnica serwisu) − cena zakupu EV × (1 − 30% dotacji) − opłata za wyjście z leasingu; bez rat diesla i wartości odsprzedaży. Zastępuje D7. `annual_fuel_saving_pln` bez zmian | Ewa: „The board looks at five years: what we save on running the van, minus what the EV costs us after the grant, minus any lease exit fee … Leave our diesel lease payments and resale values out”. Dotacja tylko przy zakupie, więc liczymy zakup (leasing EV: 60 × 2900 = 174 000 PLN > 105 000 PLN po dotacji) |
| D14 | 12:17 | Model EV dla vana: spośród modeli, które przechodzą zasięg i ładowność, ten z wyższym `saving_pln` w 5 lat (`economics.saving_for_model`); wybiera tor B | Ewa: „take whichever EV model works out better over the five years” |
| D15 | 12:19 | Ranking: malejąco po `saving_pln`, przy remisie po `annual_km`. Na shortlistę nie trafia van z `saving_pln` ≤ 0; odpada też van, dla którego brakuje wolnego punktu w bazie, limitu vanów z South albo limitu dotacji (10). Każdy taki van ma w `all_vans.csv` notatkę z powodem | Jolanta czyta najpierw oszczędność; van, który w 5 lat nie zarabia, nie jest rekomendacją, tylko informacją dla zarządu (P-14, P-26, P-10, P-20, P-28, P-32) |
| D16 | 12:29 | Wszystkie EV z listy liczymy jako kupione, więc limit dotacji (10 EV) jest limitem shortlisty | dotacja tylko przy zakupie, a zakup po dotacji (105 000 PLN za Cargo S) jest tańszy niż 60 rat leasingu (174 000 PLN) — D13 (Q20 toru B) |
| D6 | 11:20 | Korekta D5: narzędzie to jeden katalog i jedno polecenie, ale cztery pliki `.py` (`data.py`, `feasibility.py`, `economics.py`, `ev_shortlist.py`) | trzy osoby nie mogą równolegle edytować jednego pliku; do wątku trafia zip |

### Otwarte

- Brak. Vany z ujemnym wynikiem, kolejność rankingu i wybór vanów z South rozstrzygnięte o 12:19–12:29 (D15, D16, A23).

### Odpowiedzi Ewy

| Kiedy | Pytanie | Odpowiedź |
|---|---|---|
| przed 10:29 | Czy są inne dane (np. z zimy)? | Nie, więcej danych nie ma. |
| ok. 12:00 (Discussions, wątek „9”; zweryfikowane przez tor A o 12:08) | 1. Ładowanie | „North has 6 charging points today. Four more are ordered … so 10. One EV per point overnight. South gets no chargers in year 1. Up to 3 South vans can be based at North and keep their routes … don't add anything for getting there.” → A20 |
| jw. | 2. Dotacja | „The grant pays 30% of the purchase price, for at most 10 EVs, and only if we buy them. Leased EVs get nothing. Any other grant rules: choose and write it down.” → D13 |
| jw. | 3. Zasięg zimowy | „a van qualifies if its 95th-percentile day fits within 60% of the EV's WLTP range. That's our 'January plus a margin' rule. On the dealer's side, I've sent you everything I have today.” → A19 |
| jw. | 4. Leasing diesli | „Leases that end within the next 12 months are the easy ones: we just don't renew. Ending a lease early costs us 3 monthly fees.” → A22 |
| jw. (odpowiedzi dla innych zespołów, obowiązują wszystkich) | 5. Podstawa oszczędności i model | „The board looks at five years: what we save on running the van, minus what the EV costs us after the grant, minus any lease exit fee. 'Fuel saving' is just the CFO's shorthand. Leave our diesel lease payments and resale values out” · „For each van, take whichever EV model works out better over the five years. It has to carry the heaviest load that van carried.” · „Double-shift vans only come back for a driver change; there's no time to charge. Count their whole day.” · „Refrigerated vans are out for year 1.” · „Trust the odometer … P-17B took over its routes and drivers.” → D13, D14, A21, A10, A2, A3 |
| 12:03 | Pytanie Ewy do nas | „my analyst will rerun this next quarter without you. What will they open, and what will they type?” — szkic odpowiedzi w sekcji 7 (A17, A18) |

### Dziennik

| Godzina | Co |
|---|---|
| 10:10 | Repo sklonowane, materiały przeczytane, pierwszy profil danych |
| 10:20 | Analiza wpływu braku danych zimowych |
| 10:29 | Decyzja: nie pytamy o dane zimowe; pytanie o chłodnie wraca do piątki |
| 10:30 | Współczynnik zimowy 0,57 × WLTP ze źródłami |
| 10:35 | Ten dokument, wersja 0.1 |
| 10:42 | Przegląd pytań: P-17 → założenie A2, chłodnie → decyzja D1; lista pytań skrócona do 3 |
| 10:50 | D3 (ładowność twarda), D4 i A12 (sezonowość jako założenie), A16 (doładowanie między trasami), pytanie o leasing dodane |
| 10:53 | Propozycja pytań do Ewy spisana (PL + EN), dokument wypchnięty do repo zespołu |
| 11:06 | Plan na 3 deweloperów (sekcja 9) |
| 11:09 | Pytania wysłane do Ewy |
| 11:10 | Harmonogram z terminem 16:00 i lista cięć (sekcja 9) |
| 11:13 | Zakres narzędzia dla analityka i scenariusz prezentacji (sekcja 9, D5) |
| 11:13 | A17: analityk jest techniczny i ma Pythona |
| 11:20 | Dokumenty torów, `KONTRAKT.md`, `params.csv` i pliki testowe; D6 |
| 11:31 | Tor C: `economics()` z `annual_km`, `annual_fuel_saving_pln`, `saving_pln` wypchnięte na `tor-c` |
| 11:33 | Tor A: liczby kontrolne 2777 / 344952 / 38 potwierdzone przez `data.py` i niezależnie w powłoce. Pułapka: `awk` przy polskich ustawieniach regionalnych obcina ułamki (343 699) — trzeba `LC_ALL=C` |
| 11:35 | Tor A: `data.py` wypchnięte na `tor-a` |
| 11:37 | Tor C: szkice `RERUN.md` i `ASSUMPTIONS.md`; decyzje toru A przeniesione do rejestru |
| 11:40 | `handoff-wstepna-analiza` (A + B) scalone do `tor-c`; pełny potok na `trips.csv`: shortlista P-08, P-26, P-14; `saving_pln` razem 64 552 PLN/rok |
| 11:42 | `tor-c` scalone do `handoff-wstepna-analiza`; `KONSTYTUCJA.md` (D12) zastępuje szkic sekcji 10 w `KONTRAKT.md` |
| 11:44 | Tor C: uzupełnienie `KONSTYTUCJA.md` (komunikaty → `RERUN.md`), dokumenty EN zgodne ze słownikiem (check figures, near miss) |
| 12:17 | Tor C: `saving_pln` według D13 (`ac53902`), `saving_for_model` dla wyboru modelu (D14); odpowiedzi Ewy przeniesione do rejestru (A19–A22, D13, D14). Kontrola na prawdziwych danych zgodna z podglądem toru A: 15 vanów pasuje, 9 dodatnich, 8 wybranych = 95 637 PLN w 5 lat |
| 12:19 | Tor B: B10 — ranking końcowy po D13 (8 vanów, 95 637 PLN w 5 lat), wybór modelu przez `saving_for_model`; B11 — próba zipa oczami analityka OK |
| 12:29 | Tor C: pytania B Q14, Q15, Q17, Q20, Q22 rozstrzygnięte (A23, A24, D15, D16; KONSTYTUCJA 12 zaktualizowana); sekcja 8 oznaczona jako nieaktualna |
| 12:35 | Tor A: progi „blisko progu” (`near_miss_range_pct` 10, `near_miss_days` 3) przyjęte w `params.csv`; kolumny `reason`, `fit_models`, `shortlisted`, `shortlist_note` dopisane do KONTRAKT 6–7 (kolejności pilnuje test). Kontrola krzyżowa: wynik narzędzia (8 vanów, 95 637 PLN w 5 lat) identyczny z niezależnym obliczeniem toru A |
| 12:35 | Tor C: `BOARD_NOTE.md` i `PREZENTACJA.md` według reguł Ewy; demo krok 2 = percentyl 95 → 100 (8 → 6 vanów) |
| 12:40 | Tor B: liczby w `BOARD_NOTE.md` sprawdzone uruchomieniem narzędzia (shortlista, sumy 136 092 / 95 637, warianty 59 482 / 47 897 / 38 575 / 56 414) — zgodne. B11: testowy zip i demo przygotowane poza repo |
| 12:43 | Odpowiedź dla Ewy na pytanie z 12:03 (sekcja 7) wysyła tor A (Wojtek) |
| 13:07 | Tor A: proces opisany jako pełny cykl — `SDLC.md`, `SLEDZENIE.md`, automat testów na GitHubie, `KONTRAKT.md` 2.2; 13:09 usunięte trzy nieużywane parametry leasingu EV (2.3) |
| 14:45 | Zamrożenie liczb: 8 vanów, 95 637 PLN w 5 lat. Roczne km zostają liczone z dni kalendarzowych (× 365 ÷ 90); wrażliwość na liczbę dni dostaw (8 / 7 / 6 vanów) opisana w `BOARD_NOTE.md` i A12 |
| 15:05–15:12 | Druga tura odpowiedzi Ewy (nam i innym zespołom): „Pick the one that makes sense and put it in your assumptions list” — A18, A12, A23 bez zmian; A19 doprecyzowane (do percentyla liczą się tylko dni z kursami); nowe A25 (ładunek bez kierowcy). Kod i `params.csv` bez zmian; szczegóły w `ASSUMPTIONS.md` |
| 15:20 | Wydanie `v1.0`: PR `devel` → `main`, tag, zip z tagu (`SDLC.md`, sekcja 4) |
