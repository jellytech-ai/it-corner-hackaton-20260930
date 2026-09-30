# Skrypt prezentacji — tekst do czytania

Do pliku `PREZENTACJA.pdf` (13 slajdów, jeden slajd = jedna strona). Czas: 15 minut — ok. 10 minut proces, 3 minuty demo, 2 minuty zapasu. Podział osób i czasu według `PREZENTACJA.md` (plan toru C).

Liczby: narzędzie uruchomione na `devel` 35d8e0b na oryginalnym eksporcie (30.09.2026). Jeśli po zamrożeniu o 14:45 coś się zmieni, podmienić je tutaj i w `build_slides.py`.

Zasady czytania:

- Tekst jest napisany do mówienia — krótkie zdania, liczby zaokrąglone tak, jak się je mówi.
- Nazwy plików czytamy tak, jak są (`shortlist.csv` — „szortlist”), i raz tłumaczymy.
- Na głos nie używamy skrótów roboczych (A6, D3, „tor B”) — mówimy pełnym zdaniem.
- W nawiasach kwadratowych: co robić, nie czytać.

---

## Slajd 1 — Tytuł · Walerian · 0:00–0:15

Dzień dobry. Jesteśmy JellyTech: Wojtek zajmował się danymi, Rafał wykonalnością, a ja ekonomią i dokumentami. Odpowiemy na pytanie Ewy — które vany mogą przejść na prąd — i pokażemy, jak do tej odpowiedzi doszliśmy.

## Slajd 2 — Odpowiedź na początek · Walerian · 0:15–1:00

Zaczynamy od odpowiedzi. Rekomendujemy osiem aut elektrycznych, kupionych z dotacją, wszystkie ładowane w bazie North. W pięć lat, już po zapłaceniu za auta, dają razem około dziewięćdziesiąt pięć i pół tysiąca złotych.

Po prawej jest cała lista, od największego wyniku. Dwa vany dostają większy model, Cargo L, sześć — mniejszy Cargo S. Trzy z nich to vany z bazy South, które będą nocować w North.

I jedno zdanie, które zarząd powinien usłyszeć od razu: bez trzydziestoprocentowej dotacji żaden z tych vanów się nie zwraca.

## Slajd 3 — Handoff jako dziennik decyzji · Walerian · 1:00–2:00

Dziś liczył się proces, więc pokażę, jak go prowadziliśmy. Od pierwszej godziny mamy jeden dokument przekazania, który działa jak dziennik. Każde założenie i każda decyzja ma godzinę, powód i status. Na koniec dnia to dwadzieścia cztery założenia i szesnaście decyzji.

Założenie, które Ewa zmieniła, nie znika. Na przykład nasze rano: zasięg zimowy to pięćdziesiąt siedem procent zasięgu katalogowego. O dwunastej piętnaście Ewa podała swoją regułę i stare założenie dostało status „zmienione” z odsyłaczem do nowego. Ewa dostaje ten sam rejestr po angielsku, w pliku z założeniami — dokładnie to, o co prosiła: co założyliśmy i mniej więcej kiedy.

## Slajd 4 — Pięć pytań do Ewy · Walerian · 2:00–3:00

Mieliśmy limit pięciu pytań. Przy każdym od razu napisaliśmy, co przyjmiemy, jeśli odpowiedź nie przyjdzie na czas. Dzięki temu brak odpowiedzi nigdy nas nie zatrzymał.

Nie pytaliśmy o rzeczy, które da się rozstrzygnąć z danych. Van P-17 i P-17B to ten sam van — ta sama trasa, ten sam kierowca, jeden kończy, gdy drugi zaczyna. Chłodnie odpadają i bez pytania, bo pięć z sześciu wozi więcej, niż uniesie którykolwiek model elektryczny. Ewa potwierdziła wszystkie trzy wnioski. Pięć pytań poszło na to, czego z danych nie wyczytamy: ładowarki, dotację, zasięg zimą, leasingi i los wycofanych diesli.

## Slajd 5 — Dane i liczby kontrolne · Wojtek · 3:00–5:00

Ewa napisała, że CFO najpierw sprawdzi trzy liczby. Dlatego policzyliśmy je dwa razy, dwiema metodami.

Z prawie trzech tysięcy wierszy zostaje dwa tysiące siedemset siedemdziesiąt siedem kursów — dwieście dwadzieścia dwa to dokładne duplikaty. Razem trzysta czterdzieści cztery tysiące dziewięćset pięćdziesiąt dwa kilometry i trzydzieści osiem ocenionych vanów.

Pierwszy raz liczy to skrypt w Pythonie. Drugi raz — niezależnie, samymi narzędziami powłoki, bez Pythona. Wyszło to samo, ale po drodze trafiliśmy na pułapkę: przy polskich ustawieniach regionalnych `awk` obcina ułamki i daje o ponad tysiąc kilometrów mniej. Gdybyśmy liczyli tylko raz, nie zauważylibyśmy tego.

I zasada, której trzymaliśmy się w całym narzędziu: nic po cichu. Ujemny odczyt licznika P-27 zastępujemy odczytem z GPS, ale z ostrzeżeniem w raporcie. Połączenie P-17 z P-17B też jest w raporcie.

## Slajd 6 — Wykonalność według reguł Ewy · Rafał · 5:00–7:00

Teraz: który van w ogóle może jeździć na prądzie. Stosujemy reguły Ewy.

Zasięg: dziewięćdziesiąty piąty percentyl dziennego przebiegu vana — czyli dzień, którego van nie przekracza w dziewięćdziesięciu pięciu procentach dni — musi się zmieścić w sześćdziesięciu procentach zasięgu katalogowego. Dla Cargo S to sto pięćdziesiąt sześć kilometrów, dla Cargo L dwieście dwadzieścia osiem.

Ładowność to twardy limit: auto musi unieść najcięższy ładunek, jaki ten van wiózł w danych. Vany dwuzmianowe nie ładują się w dzień, więc liczymy cały ich dzień na jednym ładowaniu nocnym. South nie ma ładowarek, ale do trzech vanów stamtąd może nocować w North.

Po prawej widać lejek. Z trzydziestu ośmiu vanów piętnaście przechodzi zasięg i ładowność. Dziewięć z nich ma dodatni wynik w pięć lat. Osiem mieści się w limitach — dziewiąty, P-31, jest na plusie, ale byłby czwartym vanem z South. Model dla każdego vana wybiera narzędzie: ten, który w pięć lat daje lepszy wynik. Każdy van, który odpadł, ma w pliku z wszystkimi vanami zapisany powód.

## Slajd 7 — Odpowiedzi Ewy o 12:00 · Walerian · 7:00–8:30

Około dwunastej przyszły odpowiedzi Ewy i zmieniły prawie wszystko. Rano mieliśmy najgorszy dzień w pięćdziesięciu siedmiu procentach, doładowanie w przerwie między trasami, sześć ładowarek i oszczędność liczoną rocznie. Wynik: trzy vany. Po odpowiedziach: percentyl zamiast najgorszego dnia, sześćdziesiąt procent, bez ładowania w dzień, dziesięć ładowarek i wynik w pięć lat po zapłaceniu za auto. Wynik: osiem vanów.

Ważne jest, ile to kosztowało. Większość zmian to były nowe wartości w pliku z parametrami, nie nowy kod. Całość zajęła około dwudziestu minut, a wynik sprawdziły niezależnie dwie osoby — zgodnie co do złotówki. Przy okazji nasze poranne pięćdziesiąt siedem procent, liczone ze źródeł, pokazało, że sześćdziesiąt procent Ewy to rozsądna liczba.

## Slajd 8 — Skąd 95 637 PLN · Walerian · 8:30–9:00

Skąd ta kwota. Osiem vanów przez pięć lat oszczędza na eksploatacji — paliwo minus prąd plus tańszy serwis — około miliona złotych. Odejmujemy cenę aut po dotacji: dziewięćset trzy tysiące. I opłatę za wcześniejsze zakończenie leasingu jednego diesla, P-25: prawie dziewięć tysięcy. Zostaje dziewięćdziesiąt pięć i pół tysiąca.

Dwie uwagi. Po pierwsze — CFO pytała o vany, które jeżdżą najwięcej. Osiem z dziesięciu takich vanów ma dzień dłuższy niż dwieście kilometrów, a zasięg Cargo S to sto pięćdziesiąt sześć. Po drugie — P-30 i P-21 w swoje najdłuższe dni przekraczają ten zasięg o kilka kilometrów. Dlatego radzimy zostawić dwa wycofane diesle jako rezerwę.

## Slajd 9 — Reguła zasięgu decyduje o liście · Walerian · 9:00–9:30

Ta tabela pokazuje, co się stanie, gdy zmienimy jedną regułę. Najgorszy dzień zamiast percentyla — czyli „żaden van nigdy nie zawiedzie” — daje sześć vanów i niecałe sześćdziesiąt tysięcy. Pięćdziesiąt pięć procent zamiast sześćdziesięciu — trzy vany. Baterie po pięciu latach — dwa.

Kompromis między finansami a operacjami jest więc wart około trzydziestu sześciu tysięcy złotych. To decyzja o tym, ile ryzyka firma przyjmuje, a nie o rachunkach. Dwa duże Cargo L zostają na liście w każdym wariancie zasięgu.

## Slajd 10 — Trzy tory równolegle · Rafał · 9:30–10:00

Krótko o tym, jak we trzech pracowaliśmy równolegle. Każdy miał swój zakres i swoje pliki. Wspólny kontrakt mówił, co sobie przekazujemy — funkcje, kolumny i kto jest właścicielem którego pliku — więc scalanie odbywało się bez konfliktów. Wspólna konstytucja mówiła, jak piszemy: język, format błędów, zaokrąglenia, zasady pracy z gitem. Pliki testowe w formacie kontraktu pozwoliły mi i Walerianowi zacząć, zanim Wojtek skończył czyszczenie danych. A każdy próg ma test tuż pod, na i tuż nad progiem; na GitHubie testy uruchamiają się przy każdym wypchnięciu.

## Slajd 11 — Demo · Rafał (klawiatura), Wojtek (komentarz) · 10:00–12:30

[Rafał przełącza na terminal w katalogu z rozpakowanym zipem. Polecenia wkleja z `RERUN.md` albo z `DEMO.md`. Gdyby coś padło — pokazuje pliki z `demo_backup/`.]

**Wojtek, krok 1:** Tak wygląda uruchomienie na oryginalnym eksporcie. [Rafał uruchamia.] Na ekranie raport z czyszczenia, ostrzeżenie o liczniku P-27 i trzy liczby kontrolne: trzydzieści osiem, dwa tysiące siedemset siedemdziesiąt siedem, trzysta czterdzieści cztery tysiące dziewięćset pięćdziesiąt dwa. Na liście osiem vanów — ten sam wynik, który jest w wątku.

**Wojtek, krok 2:** Teraz zmieniamy jedną liczbę w pliku parametrów: percentyl z dziewięćdziesięciu pięciu na sto, czyli najgorszy dzień — reguła „żaden van nigdy nie zawiedzie”. Zero zmian w kodzie. [Rafał uruchamia z `params_p100.csv`.] Wypadają P-30 i P-21, zostaje sześć vanów, wynik spada z dziewięćdziesięciu pięciu do pięćdziesięciu dziewięciu tysięcy.

**Wojtek, krok 3:** I tak będzie wyglądał następny kwartał — sześć tygodni danych, nowy van, zepsuty licznik. [Rafał uruchamia na `fresh_trips.csv`.] Narzędzie samo liczy okres — czterdzieści jeden dni — i przelicza roczne kilometry. Ostrzega o nieznanym vanie P-39, o ujemnym liczniku P-13 i o kursie P-21 bez dystansu. Niczego nie poprawia po cichu. Na liście siedem vanów.

## Slajd 12 — Co dostaje analityk Ewy · Wojtek · 12:30–13:00

Ewa pytała, co jej analityk otworzy i co wpisze. Otworzy jeden folder z zipa i wpisze jedno polecenie — to, które przed chwilą widzieliście. Potrzebuje tylko Pythona. Dostaje dwa pliki w formacie importu Ewy, pełną listę vanów z powodami i raport z czyszczenia. Edytuje tylko plik z parametrami. Instrukcja mówi krok po kroku, co zrobić i jak czytać powody, a każdy błąd to jedna czytelna linia zamiast komunikatu programisty. Zip sprawdziliśmy w pustym katalogu, tak jak zrobi to analityk — wynik jest identyczny co do bajtu.

## Slajd 13 — Podsumowanie · Walerian · 13:00–13:30

Podsumowując. Rekomendujemy kupić osiem aut elektrycznych z dotacją: dwa Cargo L i sześć Cargo S, wszystkie w North. W pięć lat to około dziewięćdziesięciu pięciu i pół tysiąca złotych na plusie.

Główne ryzyko: mamy dane tylko z lata. Zanim firma kupi auta, warto uruchomić narzędzie na eksporcie z czwartego kwartału — analityk zrobi to sam.

A o procesie świadczy jedno: zmiana wymagań w połowie dnia zajęła nam około dwudziestu minut. Dziękujemy — chętnie odpowiemy na pytania.

---

## Pytania, których się spodziewamy (13:30–15:00)

Odpowiedzi do powiedzenia własnymi słowami; pełna lista w `PREZENTACJA.md`.

| Pytanie | Kto | Odpowiedź |
|---|---|---|
| Dlaczego osiem, skoro dotacja jest na dziesięć? | Walerian | Reguły przechodzi piętnaście vanów. Sześć z nich nie zwraca się w pięć lat — to głównie vany z małym przebiegiem albo z opłatą za leasing. P-31 jest na plusie, ale nie mieści się w limicie trzech vanów z South. W North zostają dwie wolne ładowarki. |
| Skąd 95. percentyl i 60%? | Rafał | To reguła Ewy: „styczeń plus margines”. Nasze niezależne oszacowanie rano dało 57% — temperatura, ładunek i rezerwa, ze źródłami w pliku z założeniami. |
| Co, jeśli P-30 albo P-21 nie da rady w styczniu? | Rafał | Ich najdłuższe dni to 166 i 159 km przy 156 km zasięgu. Dlatego rezerwowe diesle. Przy regule „najgorszy dzień” wypadają — to pokazał krok 2 demo. |
| Czemu zakup, a nie leasing? | Walerian | Dotacja jest tylko przy zakupie. Cargo S po dotacji kosztuje 105 tysięcy, a 60 rat leasingu — 174 tysiące. |
| Czy analityk poradzi sobie bez was? | Wojtek | Pokazaliśmy to w kroku 3 demo. Test z samej instrukcji robi osoba, która nie pisała skryptu. |
