# Skrypt prezentacji — tekst do czytania

Do pliku `PREZENTACJA.pdf` (15 slajdów, jeden slajd = jedna strona, barwy i logo JellyTech). Czas: 15 minut — ok. 10,5 minuty treść, 2,5 minuty demo, 2 minuty na pytania.

Zasady:

- Nie mówimy, kto za co odpowiadał, i nie opisujemy danych wejściowych — każdy zespół dostał te same. Mówimy o **założeniach, które przyjęliśmy**, o wyniku i o procesie.
- Tekst jest napisany do mówienia — krótkie zdania, liczby zaokrąglone tak, jak się je mówi.
- Nazwy plików czytamy tak, jak są, i raz tłumaczymy. Bez skrótów roboczych (A19, D15) — pełnym zdaniem.
- W nawiasach kwadratowych: co robić, nie czytać.

Liczby: narzędzie uruchomione na `devel` 35d8e0b na oryginalnym eksporcie (30.09.2026). Jeśli po zamrożeniu o 14:45 coś się zmieni, podmienić je tutaj i w `build_slides.py`.

---

## AKTUALIZACJA 15:40 — po zmianie Ewy z 15:18 (czytać to zamiast starych akapitów)

PDF ma teraz **16 slajdów**: doszedł slajd 12 o zmianie z 15:18, a dawne slajdy 12–15 to teraz 13–16. Tekst poniżej zastępuje odpowiednie akapity w dalszej części skryptu; slajdy 4, 6, 10, 11 i 13 czytamy bez zmian.

**Slajd 2 — Odpowiedź na początek.** Rekomendujemy zakup siedmiu aut elektrycznych z dotacją, wszystkie ładowane w bazie North. W pięć lat dają 85 750 złotych oszczędności, już po zapłaceniu za auta. To wynik na wszystkich danych, jakie Ewa przysłała, łącznie z eksportem, który dostaliśmy o 15:18, i według reguły, którą wtedy zmieniła. W południe było osiem vanów i 95 637 złotych.

**Slajd 3 — Zasięg i ładowność.** Najważniejsze dotyczy zasięgu. Od 15:18 van przechodzi tylko wtedy, gdy jego najgorszy dzień w danych mieści się w sześćdziesięciu procentach zasięgu katalogowego: 156 kilometrów dla Cargo S i 228 dla Cargo L. W południe obowiązywał dziewięćdziesiąty piąty percentyl; operacje wygrały spór i teraz liczy się każdy dzień.

**Slajd 5 — Dane i narzędzie (dopowiedzieć).** Trzy rzeczy z nowego eksportu. Kolumna licznika zmieniła nazwę — nasze założenie, że nazwy się nie zmienią, upadło przy pierwszym nowym pliku; narzędzie zatrzymało się i nazwało kolumnę, a poprawka to jedna linia w parametrach. Jeden odczyt licznika jest niemożliwy: 1383 kilometry na jednej porannej trasie; bierzemy dla niego dystans z GPS. I dwa nowe vany mają tylko dwanaście dni danych, więc ich roczny przebieg liczymy z ich własnych dni.

**Slajd 7 — Wykonalność: 40 → 7.** Z czterdziestu vanów czternaście mieści się w zasięgu i ładowności. Osiem z nich zwraca się w pięć lat. Siedem mieści się w limitach: P-25 jest na plusie, ale byłby czwartym vanem z South, a w North mogą stacjonować trzy.

**Slajd 8 — Skąd 85 750 PLN.** Siedem vanów przez pięć lat oszczędza na eksploatacji około 902 tysięcy złotych. Auta po dotacji kosztują 798 tysięcy, a wyjście z leasingu dwóch nowych diesli 18 600. Zostaje 85 750. Dwa ostatnie vany, P-13 i P-04, zwracają się ledwo — o trzy i pół oraz dwa tysiące złotych.

**Slajd 9 — Reguła zasięgu decyduje o liście.** Reguła najgorszego dnia daje siedem vanów. Ta sama flota na regule z południa dałaby dziewięć vanów i prawie 123 tysiące. Zasada „żaden van nigdy nie zawiedzie” kosztuje więc dwa vany i około 37 tysięcy złotych. Dalej: przy 55 procentach zostają trzy vany, po pięciu latach baterii jeden. Gdyby liczyć 303 dni dostaw w roku zamiast dni kalendarzowych — sześć. A gdyby wziąć dosłownie licznik 1383 kilometry — też sześć, bo wypada P-13.

**Slajd 12 (nowy) — 15:18: nowe dane i nowa reguła.** O 15:18 Ewa dołożyła nowy eksport, nowy rejestr z dwoma vanami i zmieniła regułę zasięgu. O 15:27 mieliśmy nowy wynik z testami, o 15:33 wpis w wątku i nowe wydanie. Wypadły P-30 i P-21 — przez nową regułę, bo ich najgorsze dni to 166 i 159 kilometrów. Wypadł P-25 — przez nowe dane, bo jego miejsce zajął nowy van P-40 z wyższym wynikiem. Weszły dwa nowe vany. Każda z trzech pułapek w nowych danych została złapana przez narzędzie, a nie przez nas: zmieniona nazwa kolumny, niemożliwy licznik i vany z dwunastoma dniami danych.

**Slajd 14 — Demo.** Krok 1: stan z południa — jeden eksport, parametry z południa; osiem vanów, 95 637 złotych. Krok 2: to samo polecenie z dwoma plikami eksportu, nowym rejestrem i aktualnymi parametrami — na ekranie alias kolumny, ostrzeżenie o liczniku P-13, siedem vanów, 85 750 złotych. Krok 3: drugi skrypt porównuje oba stany i zapisuje `impact.csv` — kto wszedł, kto wypadł i dlaczego. Polecenia wklejamy z `RERUN.md`.

**Slajd 16 — Podsumowanie.** Rekomendacja: siedem aut elektrycznych z dotacją, 85 750 złotych w pięć lat. Wynik stoi na regule najgorszego dnia w sześćdziesięciu procentach zasięgu, najcięższym ładunku jako limicie i zakupie z dotacją. Ryzyko: dane z lata i września, a dwa nowe vany oceniamy na dwunastu dniach. I proces: dwie zmiany wymagań w ciągu dnia — dwadzieścia minut w południe, dziesięć minut po piętnastej — a analityk uruchamia całość bez nas.

**Spodziewane pytania — nowe odpowiedzi.** „Dlaczego 7, a nie 10?” — tylko osiem vanów zwraca się w pięć lat, a jeden z nich nie mieści się w limicie trzech vanów z South. „Skąd reguła najgorszego dnia?” — to reguła Ewy z 15:18; wcześniej 95. percentyl, a rano nasze własne 57 procent. „Czy nowe vany to pewny wybór?” — mają 12 dni danych i świeży leasing; liczymy je tak, jak Ewa kazała, i mówimy o tym wprost.

---

## Slajd 1 — Tytuł · 0:00–0:15

Dzień dobry, jesteśmy JellyTech. Odpowiemy na pytanie Ewy — które vany mogą przejść na prąd — powiemy, na jakich założeniach oparliśmy odpowiedź, i pokażemy, jak do niej doszliśmy.

## Slajd 2 — Odpowiedź na początek · 0:15–1:00

Zaczynamy od odpowiedzi. Rekomendujemy osiem aut elektrycznych, kupionych z dotacją, wszystkie ładowane w bazie North. W pięć lat, już po zapłaceniu za auta, dają razem około dziewięćdziesięciu pięciu i pół tysiąca złotych.

Po prawej cała lista, od największego wyniku. Dwa vany dostają większy model, Cargo L, sześć — mniejszy Cargo S. Trzy z nich to vany z bazy South, które będą nocować w North.

I jedno zdanie, które zarząd powinien usłyszeć od razu: bez trzydziestoprocentowej dotacji żaden z tych vanów się nie zwraca.

## Slajd 3 — Założenia: zasięg i ładowność · 1:00–2:15

Ten wynik stoi na założeniach — pokażemy je, zanim pokażemy liczby.

Najważniejsze dotyczy zasięgu. Van przechodzi, jeśli jego dziewięćdziesiąty piąty percentyl dnia — czyli dzień, którego nie przekracza w dziewięćdziesięciu pięciu procentach dni — mieści się w sześćdziesięciu procentach zasięgu katalogowego. To reguła Ewy. Dla Cargo S daje sto pięćdziesiąt sześć kilometrów, dla Cargo L dwieście dwadzieścia osiem. Dzień to suma wszystkich tras vana — a vany dwuzmianowe nie ładują się w przerwie, więc cały ich dzień musi się zmieścić na jednym ładowaniu nocnym.

Zużycie energii bierzemy od dealera i dokładamy dziesięć procent na zimę. Starzenie baterii po pięciu latach traktujemy jako test warunków skrajnych, nie jako regułę listy.

Ładowność to twardy limit: auto musi unieść najcięższy ładunek, jaki ten van kiedykolwiek wiózł. I chłodnie zostają na dieslu w pierwszym roku.

## Slajd 4 — Założenia: ładowanie i wynik finansowy · 2:15–3:30

Druga grupa założeń: ładowanie i pieniądze.

North będzie miał dziesięć punktów ładowania, jeden samochód na punkt. South nie ma żadnego, ale do trzech vanów stamtąd może nocować w North. Gdy chętnych jest więcej, wybieramy te z najwyższym wynikiem. Ładujemy w nocy, po taryfie nocnej.

Wynik liczymy tak, jak patrzy zarząd: pięć lat oszczędności na paliwie i serwisie, minus cena auta po dotacji, minus opłata za wcześniejsze zakończenie leasingu diesla. Raty obecnych diesli i ich wartość odsprzedaży pomijamy — tak chciała Ewa.

Auta kupujemy, nie leasingujemy: dotacja jest tylko przy zakupie, a Cargo S po dotacji kosztuje sto pięć tysięcy, podczas gdy sześćdziesiąt rat leasingu to sto siedemdziesiąt cztery. Leasing diesla, który kończy się w ciągu dwunastu miesięcy, po prostu wygasa — granicę liczymy włącznie, to nasza interpretacja. I na listę trafia tylko van z dodatnim wynikiem.

## Slajd 5 — Założenia: dane i narzędzie · 3:30–4:15

Kilka założeń o danych i o tym, kto będzie używał narzędzia.

Przyjmujemy, że trasy i ładunki są takie same przez cały rok — roczne kilometry skalujemy z długości okresu w danych. To założenie sprawdzi eksport z czwartego kwartału. Dystans bierzemy z licznika, a GPS tylko wtedy, gdy licznik jest pusty albo ujemny — zawsze z ostrzeżeniem. P-17 i P-17B to ten sam van.

O narzędziu zakładamy, że analityk Ewy zna wiersz poleceń i ma Pythona, a kolejny eksport ma te same kolumny. Tych dwóch rzeczy Ewa jeszcze nie potwierdziła — dlatego gdy kolumny brakuje, narzędzie mówi to wprost, zamiast zgadywać.

## Slajd 6 — Skąd 60%? · 4:15–5:00

Skąd sześćdziesiąt procent? To liczba Ewy, ale rano, zanim ją podała, policzyliśmy własną. Dzień projektowy minus dziesięć stopni. Temperatura zabiera około trzydziestu procent zasięgu, ładunek około dziesięciu, i zostawiamy dziesięć procent rezerwy na powrót do bazy. Razem wyszło pięćdziesiąt siedem procent — każda liczba ze źródłem.

Dzięki temu, gdy Ewa podała sześćdziesiąt, wiedzieliśmy, że to rozsądna liczba na styczeń z marginesem — i ile ryzyka za sobą niesie.

## Slajd 7 — Wykonalność: 38 → 8 · 5:00–6:00

Teraz wynik. Z trzydziestu ośmiu vanów piętnaście mieści się w zasięgu i ładowności. Dziewięć z nich zwraca się w pięć lat. Osiem mieści się w limitach — dziewiąty, P-31, jest na plusie, ale byłby czwartym vanem z South.

Model dla każdego vana wybiera narzędzie: ten, który w pięć lat daje lepszy wynik. A każdy van, który nie trafił na listę, ma w pliku ze wszystkimi vanami zapisany powód — nic nie znika po cichu.

## Slajd 8 — Skąd 95 637 PLN · 6:00–7:00

Skąd ta kwota. Osiem vanów przez pięć lat oszczędza na eksploatacji — paliwo minus prąd plus tańszy serwis — około miliona złotych. Odejmujemy cenę aut po dotacji: dziewięćset trzy tysiące. I opłatę za wcześniejsze zakończenie jednego leasingu, P-25: prawie dziewięć tysięcy. Zostaje dziewięćdziesiąt pięć i pół tysiąca.

Dwie uwagi. Po pierwsze — pojawił się pomysł, żeby wymieniać vany, które jeżdżą najwięcej. Osiem z dziesięciu takich vanów ma dzień dłuższy niż dwieście kilometrów, a zasięg Cargo S to sto pięćdziesiąt sześć. Po drugie — P-30 i P-21 w swoje najdłuższe dni przekraczają ten zasięg o kilka kilometrów. Dlatego radzimy zostawić dwa wycofane diesle jako rezerwę.

## Slajd 9 — Reguła zasięgu decyduje o liście · 7:00–7:45

Ta tabela pokazuje, co się stanie, gdy zmienimy jedno założenie. Najgorszy dzień zamiast percentyla — czyli „żaden van nigdy nie zawiedzie” — daje sześć vanów i niecałe sześćdziesiąt tysięcy. Pięćdziesiąt pięć procent zamiast sześćdziesięciu — trzy vany. Baterie po pięciu latach — dwa.

Kompromis między finansami a operacjami jest więc wart około trzydziestu sześciu tysięcy złotych. To decyzja o tym, ile ryzyka firma przyjmuje, a nie o rachunkach. Dwa duże Cargo L zostają na liście w każdym wariancie zasięgu.

## Slajd 10 — Każde założenie ma godzinę, powód i status · 7:45–8:45

Jak pracowaliśmy. Od pierwszej godziny prowadziliśmy jeden dziennik: każde założenie i każda decyzja ma godzinę, powód i status. Na koniec dnia to dwadzieścia cztery założenia i szesnaście decyzji. Założenie, które się zmieniło, nie znika — dostaje status „zmienione” i następcę. Ewa dostaje ten sam rejestr po angielsku: co założyliśmy i mniej więcej kiedy.

Mieliśmy limit pięciu pytań do Ewy. Przy każdym od razu napisaliśmy, co przyjmiemy bez odpowiedzi, więc brak odpowiedzi nigdy nas nie zatrzymał. Nie pytaliśmy o to, co da się rozstrzygnąć z danych: że P-17 i P-17B to ten sam van i że chłodnie odpadają już na ładowności. Ewa potwierdziła oba wnioski.

## Slajd 11 — Odpowiedzi Ewy o 12:00 · 8:45–9:45

Około dwunastej przyszły odpowiedzi Ewy i zmieniły prawie wszystko. Rano mieliśmy najgorszy dzień w pięćdziesięciu siedmiu procentach, doładowanie w przerwie, sześć ładowarek i oszczędność liczoną rocznie — wynik: trzy vany. Po odpowiedziach: percentyl, sześćdziesiąt procent, bez ładowania w dzień, dziesięć ładowarek i pięć lat po zapłaceniu za auto — wynik: osiem vanów.

Ważne jest, ile to kosztowało. Większość zmian to były nowe wartości w pliku z parametrami, nie nowy kod. Całość zajęła około dwudziestu minut, a wynik sprawdziliśmy drugą, niezależną metodą — zgodnie co do złotówki.

## Slajd 12 — Praca równoległa bez konfliktów · 9:45–10:30

Pracowaliśmy równolegle i bez konfliktów dzięki czterem rzeczom. Kontrakt mówił, co sobie przekazujemy — funkcje, kolumny i do kogo należy który plik. Konstytucja mówiła, jak piszemy: język, format błędów, zaokrąglenia, zasady pracy z gitem. Każda liczba siedzi w pliku z parametrami, więc odpowiedź Ewy to zmiana wartości, a nie kodu. I weryfikacja: liczby kontrolne policzyliśmy dwa razy dwiema metodami, a każdy próg ma test tuż pod, na i tuż nad progiem. Testy uruchamiają się automatycznie na GitHubie przy każdym wypchnięciu.

## Slajd 13 — Demo · 10:30–13:00

[Przełączyć na terminal w katalogu z rozpakowanym zipem. Polecenia wklejać z `RERUN.md` albo z `DEMO.md`. Gdyby coś padło — pokazać pliki z `demo_backup/`.]

**Krok 1.** Tak wygląda uruchomienie na oryginalnym eksporcie. [Uruchomić.] Na ekranie raport, ostrzeżenie o liczniku P-27 i trzy liczby kontrolne: trzydzieści osiem, dwa tysiące siedemset siedemdziesiąt siedem, trzysta czterdzieści cztery tysiące dziewięćset pięćdziesiąt dwa. Na liście osiem vanów — ten sam wynik, który jest w wątku.

**Krok 2.** Teraz zmieniamy jedno założenie w pliku parametrów: percentyl z dziewięćdziesięciu pięciu na sto, czyli najgorszy dzień. Zero zmian w kodzie. [Uruchomić z `params_p100.csv`.] Wypadają P-30 i P-21, zostaje sześć vanów, wynik spada z dziewięćdziesięciu pięciu do pięćdziesięciu dziewięciu tysięcy.

**Krok 3.** I tak będzie wyglądał następny kwartał — sześć tygodni danych, nowy van, zepsuty licznik. [Uruchomić na `fresh_trips.csv`.] Narzędzie samo liczy okres — czterdzieści jeden dni — i przelicza roczne kilometry. Ostrzega o nieznanym vanie P-39, o ujemnym liczniku P-13 i o kursie P-21 bez dystansu. Niczego nie poprawia po cichu. Na liście siedem vanów.

## Slajd 14 — Co dostaje analityk Ewy · 13:00–13:30

Ewa pytała, co jej analityk otworzy i co wpisze. Otworzy jeden folder z zipa i wpisze jedno polecenie — to, które przed chwilą widzieliście. Potrzebuje tylko Pythona. Dostaje listę w formacie importu Ewy, podsumowanie, pełną listę vanów z powodami i raport z czyszczenia. Edytuje tylko plik z parametrami. Każdy błąd to jedna czytelna linia. Zip sprawdziliśmy w pustym katalogu, tak jak zrobi to analityk — wynik identyczny co do bajtu.

## Slajd 15 — Podsumowanie · 13:30–14:00

Podsumowując. Rekomendujemy kupić osiem aut elektrycznych z dotacją: dwa Cargo L i sześć Cargo S, wszystkie w North — około dziewięćdziesięciu pięciu i pół tysiąca złotych na plusie w pięć lat.

Ten wynik stoi na kilku założeniach: dziewięćdziesiąty piąty percentyl dnia w sześćdziesięciu procentach zasięgu, najcięższy ładunek jako limit, bez ładowania w dzień, zakup z dotacją i horyzont pięciu lat. Każde z nich to jedna wartość w pliku parametrów.

Główne ryzyko: mamy dane tylko z lata. Zanim firma kupi auta, warto uruchomić narzędzie na eksporcie z czwartego kwartału — analityk zrobi to sam. Dziękujemy, chętnie odpowiemy na pytania.

---

## Pytania, których się spodziewamy (14:00–15:00)

| Pytanie | Odpowiedź |
|---|---|
| Dlaczego osiem, skoro dotacja jest na dziesięć? | Założenia przechodzi piętnaście vanów. Sześć z nich nie zwraca się w pięć lat — głównie vany z małym przebiegiem albo z opłatą za leasing. P-31 jest na plusie, ale nie mieści się w limicie trzech vanów z South. W North zostają dwie wolne ładowarki. |
| Skąd 95. percentyl i 60%? | To reguła Ewy: „styczeń plus margines”. Nasze niezależne oszacowanie dało 57% — slajd 6. |
| Co, jeśli P-30 albo P-21 nie da rady w styczniu? | Ich najdłuższe dni to 166 i 159 km przy 156 km zasięgu. Dlatego rezerwowe diesle. Przy regule „najgorszy dzień” wypadają — krok 2 demo. |
| Czemu zakup, a nie leasing? | Dotacja tylko przy zakupie. Cargo S po dotacji 105 tysięcy, 60 rat leasingu 174 tysiące. |
| Które założenie jest najsłabsze? | Że trasy są takie same przez cały rok — mamy dane tylko z lata. Dlatego zalecamy uruchomienie na eksporcie z IV kwartału. |
| Czy analityk poradzi sobie bez was? | Pokazaliśmy to w kroku 3 demo; zip sprawdziliśmy w pustym katalogu. |
