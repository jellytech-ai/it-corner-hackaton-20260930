# Propozycja: sekcja o procesie w prezentacji

Stan: 30.09.2026, 14:56. Autor: Rafał (z asystentem AI), gałąź `prezentacja-propozycja-procesu`. **Do przeglądu przez cały zespół przed wygenerowaniem PDF.**

Cel: po ustaleniach prezentacja ma pokazać (1) nasz proces SDLC, (2) co byśmy zmienili, robiąc to jeszcze raz, (3) nasz tooling, (4) gdzie decydował człowiek, a co zrzuciliśmy na AI.

Propozycja: obecne slajdy procesu (10–12 w `PREZENTACJA.pdf`) zastępuje sekcja pięciu slajdów A–E poniżej. Bez zmian zostają: tytuł, odpowiedź, założenia (3–6), wynik (7–9), demo, analityk, podsumowanie. Razem 17 slajdów w 15 minut.

Źródła: `SDLC.md` (tor A, na `devel`), historia gita, dzienniki torów. **Slajd D opisuje na razie tylko tor B** — Wojtek i Walerian dopisują swoje punkty.

---

## Slajd A — „Nasz SDLC: najpierw specyfikacja, potem kod”

Schemat 7 faz w poziomie; pod każdą fazą jej artefakt.

| Faza | Artefakt | Bramka do kolejnej fazy |
|---|---|---|
| 1. Wymagania | rejestr założeń i decyzji z godzinami, 5 pytań do Ewy z planem B | każde założenie ma numer, godzinę i status |
| 2. Projekt | kontrakt (wersje 1.0 → 2.3), konstytucja, `params.csv`, pliki testowe | zmiana kolumny lub parametru = najpierw nowa wersja kontraktu |
| 3. Implementacja | 4 moduły, 3 tory równolegle | testy lokalnie |
| 4. Weryfikacja | 98 testów, macierz wymaganie → test, CI, liczby liczone dwiema metodami | CI zielone, żaden test pominięty |
| 5. Wydanie | PR `devel` → `main`, tag `v1.0`, zip z tagu | przegląd drugiej osoby |
| 6. Akceptacja | zip w pustym katalogu; świeży eksport; 6 typowych pomyłek analityka | wynik bajt w bajt, zawsze czytelny `ERROR` |
| 7. Utrzymanie | `RERUN.md`: co zmieniać co kwartał, co robić przy błędzie | — |

**Zdanie na slajd:** zmiana wymagań przeszła drogę wymaganie → kontrakt → parametr → kod → test w 33 minuty (12:00–12:33), a lista zmieniła się z 3 na 8 vanów bez przepisywania narzędzia.

## Slajd B — „Oś czasu”

Oś 10:10 → 15:40 z kamieniami milowymi z `SDLC.md` sekcja 3; wyróżniona zmiana wymagań o 12:00.

Pod osią: 80+ commitów, 16+ scaleń, 3 osoby, 98 testów (**odświeżyć liczby tuż przed prezentacją**).

## Slajd C — „Tooling”

| Obszar | Narzędzie | Do czego |
|---|---|---|
| Asystent AI | Claude Code (model Opus) w terminalu | implementacja, testy, integracja, weryfikacja, dokumenty |
| Izolacja pracy | git worktree na tor (Orca) | każda sesja we własnym katalogu |
| Edytor | Cursor | podgląd i ręczne poprawki (patrz slajd E) |
| Repozytorium | GitHub: gałęzie torów, `devel`, PR do `main` | scalanie przez merge, bez rebase i force push |
| CI | GitHub Actions: Python 3.9 i 3.13 na prawdziwym eksporcie | pominięty test = czerwone CI |
| Kontakt z klientem | GitHub Discussions (wątek z Ewą), Slack (wątek wydania) | pytania, odpowiedzi, dostawa |
| Narzędzie dla Ewy | Python, tylko biblioteka standardowa, `unittest` | zero instalacji u analityka |
| Kontrola niezależna | `sort -u` + `awk` w powłoce (`LC_ALL=C`) | druga metoda na liczby kontrolne |
| Ciągłość sesji AI | pliki przekazania (`.remember/`), skille (TDD, planowanie, przegląd kodu) | kontekst między sesjami, stały sposób pracy |

## Slajd D — „Gdzie decydował człowiek, a co zrzuciliśmy na AI”

Dwie kolumny i pasek pośrodku: „AI proponuje → człowiek zatwierdza”.

**Człowiek decydował:**

- co jest problemem Ewy; które 5 pytań zadać i jaki plan B przy każdym;
- podział na tory, kontrakt i konstytucja — reguły gry;
- każde wypchnięcie na wspólną gałąź i każde scalenie do `devel`;
- rozstrzygnięcia z konsekwencją biznesową (np. zamknięcie pytań Q1, Q2, Q4; przyjęcie reguł rankingu do rejestru);
- zakres i forma wydania: co idzie do Ewy, co do prezentacji, co pomijamy;
- zatrzymanie pracy AI („przestań obserwować”).

**AI zrobiło samo:**

- kod i testy z kryterium „gotowe, gdy” (najpierw test, potem kod);
- odczyt odpowiedzi Ewy u źródła, także z wątków innych zespołów (reguła „no time to charge”);
- próbne scalenia, testy integracyjne, obserwowanie `devel` i scalanie po każdej zmianie;
- przegląd kodu pod kątem konstytucji — znalazł 2 realne błędy (van bez kursów przechodził filtry; maksimum ładunku liczone na tekście);
- sprawdzenie każdej liczby w notatce i na slajdach przez uruchomienie narzędzia;
- przygotowanie demo, zipa i prezentacji.

**Na styku (AI proponowało, człowiek zatwierdzał):**

- reguły rankingu (wynik ≤ 0 poza listą, wybór 3 vanów z South) — przyjęte do rejestru (D15, A23);
- nowe parametry progu „near miss” — przyjęte przez właściciela `params.csv`.

**Zdanie na slajd:** AI napisało większość kodu i sprawdzeń, ale żadna decyzja o tym, co Ewa dostaje i na jakich założeniach, nie zapadła bez człowieka — każda jest w rejestrze z godziną.

**Do uzupełnienia:** tor A (Wojtek) i tor C (Walerian) — co w waszych torach robiło AI, a co decydowaliście sami.

## Slajd E — „Co byśmy zmienili, robiąc to jeszcze raz”

| Co się stało | Co zrobilibyśmy inaczej |
|---|---|
| Reguła Ewy o 12:00 zmieniła wszystko (3 → 8 vanów) | pytać najpierw o to, co najbardziej zmienia wynik (zasięg, dotacja); od rana czytać wątki innych zespołów |
| Kod wyprzedził kontrakt (wersja 2.1 — cztery kolumny dopisane po fakcie) | „najpierw kontrakt” od pierwszej minuty, nie od 13:15 |
| Pliki `.pyc` w repo, CI dopiero o 13:07 | `.gitignore`, CI i test na prawdziwych danych w kroku 0 |
| Edytor nadpisał pliki nieaktualnym buforem — commit bez kodu | jedno narzędzie edytuje plik naraz; po każdym commicie `git show --stat` |
| Godziny w dzienniku wpisane z harmonogramu, nie z zegara | godziny brać z commitów |
| Scenariusz demo przestał działać po zmianie reguł | test scenariusza demo w CI |
| Dane źródłowe w katalogu tymczasowym zniknęły w trakcie | stała ścieżka z kontraktu od początku |
| Ten sam fakt w kilku dokumentach (HANDOFF, ASSUMPTIONS, KONTRAKT) | jedno źródło, reszta tylko odsyła |
| Akceptację robiły osoby, które znają kod | test przez kogoś spoza zespołu, choćby 10 minut |

---

## Do decyzji zespołu przed wygenerowaniem PDF

1. **Liczba slajdów:** 17 w 15 minut to dużo — połączyć A z B albo skrócić założenia z 4 slajdów do 3?
2. **Slajd D:** dopiski torów A i C (bez nich slajd opisuje tylko tor B).
3. **Kolejność:** sekcja procesu przed wynikiem („focus on process”) czy po nim, jak teraz?

Po decyzjach: slajdy dopisuje `prezentacja/build_slides.py`, tekst do czytania — `prezentacja/SKRYPT.md`.
