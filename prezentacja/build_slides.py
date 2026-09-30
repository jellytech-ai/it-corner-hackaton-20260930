"""Build the presentation PDF: one page = one slide (16:9).

Not part of the tool (the tool uses the standard library only). Needs reportlab:
    python3 -m venv /tmp/venv-pdf && /tmp/venv-pdf/bin/pip install reportlab
    /tmp/venv-pdf/bin/python prezentacja/build_slides.py

Figures come from the tool run on the source export at devel 35d8e0b (30.09.2026):
8 vans, 95 637 PLN over five years. Update them here after the 14:45 freeze if they change.
"""
import os

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "PREZENTACJA.pdf")

W, H = 960, 540
M = 48  # side margin

FONT_DIR = "/System/Library/Fonts/Supplemental"
pdfmetrics.registerFont(TTFont("Sans", os.path.join(FONT_DIR, "Arial.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Bold", os.path.join(FONT_DIR, "Arial Bold.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(FONT_DIR, "Courier New.ttf")))
addMapping("Sans", 0, 0, "Sans")
addMapping("Sans", 1, 0, "Sans-Bold")
addMapping("Sans", 0, 1, "Sans")
addMapping("Sans", 1, 1, "Sans-Bold")

INK = colors.HexColor("#1B2A41")
MUTED = colors.HexColor("#5B6B7F")
ACCENT = colors.HexColor("#0F7B6C")
ACCENT_SOFT = colors.HexColor("#E3F2EF")
WARN = colors.HexColor("#B4532A")
RULE = colors.HexColor("#D5DCE4")
ROW_ALT = colors.HexColor("#F4F6F8")

BODY = ParagraphStyle("body", fontName="Sans", fontSize=17, leading=23, textColor=INK)
MID = ParagraphStyle("mid", fontName="Sans", fontSize=15, leading=20, textColor=INK)
SMALL = ParagraphStyle("small", fontName="Sans", fontSize=13, leading=17, textColor=MUTED)
CELL = ParagraphStyle("cell", fontName="Sans", fontSize=13, leading=16, textColor=INK)
CELL_B = ParagraphStyle("cellb", parent=CELL, fontName="Sans-Bold")

TOTAL = 13


def frame(c, n, title, kicker=""):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.rect(0, H - 8, W, 8, stroke=0, fill=1)
    if kicker:
        c.setFont("Sans-Bold", 12)
        c.setFillColor(ACCENT)
        c.drawString(M, H - 44, kicker.upper())
    c.setFont("Sans-Bold", 30)
    c.setFillColor(INK)
    c.drawString(M, H - 82, title)
    c.setStrokeColor(RULE)
    c.setLineWidth(1)
    c.line(M, 36, W - M, 36)
    c.setFont("Sans", 10)
    c.setFillColor(MUTED)
    c.drawString(M, 20, "JellyTech · EV shortlist · 30.09.2026")
    c.drawRightString(W - M, 20, "%d / %d" % (n, TOTAL))


def para(c, text, x, y_top, width, style=BODY):
    p = Paragraph(text, style)
    _, h = p.wrap(width, H)
    p.drawOn(c, x, y_top - h)
    return y_top - h


def bullets(c, items, x, y_top, width, style=BODY, gap=10):
    y = y_top
    for item in items:
        c.setFillColor(ACCENT)
        c.circle(x + 5, y - style.leading / 2 + 3, 3.5, stroke=0, fill=1)
        y = para(c, item, x + 20, y, width - 20, style) - gap
    return y


def table(c, rows, x, y_top, widths, header=True, bold_rows=(), highlight_rows=()):
    data = [[Paragraph(str(v), CELL_B if (header and i == 0) or i in bold_rows else CELL)
             for v in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, RULE),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), ACCENT_SOFT),
                  ("LINEBELOW", (0, 0), (-1, 0), 1.2, ACCENT)]
    for i in range(1 if header else 0, len(rows)):
        if (i % 2 == 0) and i not in highlight_rows:
            style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    for i in highlight_rows:
        style.append(("BACKGROUND", (0, i), (-1, i), ACCENT_SOFT))
    t.setStyle(TableStyle(style))
    _, h = t.wrap(sum(widths), H)
    t.drawOn(c, x, y_top - h)
    return y_top - h


def big_number(c, x, y, value, label, color=ACCENT, size=54):
    c.setFont("Sans-Bold", size)
    c.setFillColor(color)
    c.drawString(x, y, value)
    c.setFont("Sans", 15)
    c.setFillColor(MUTED)
    c.drawString(x, y - 24, label)


def code(c, text, x, y, width):
    c.setFillColor(colors.HexColor("#1E1E1E"))
    c.roundRect(x, y - 8, width, 30, 4, stroke=0, fill=1)
    c.setFont("Mono", 12.5)
    c.setFillColor(colors.HexColor("#E6E6E6"))
    c.drawString(x + 12, y + 3, text)


# --- slides -------------------------------------------------------------------

def s01_title(c):
    c.setFillColor(INK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.rect(0, 0, 14, H, stroke=0, fill=1)
    c.setFont("Sans-Bold", 14)
    c.setFillColor(colors.HexColor("#8FD3C7"))
    c.drawString(80, 360, "IT CORNER HACKATHON · 30.09.2026")
    c.setFont("Sans-Bold", 46)
    c.setFillColor(colors.white)
    c.drawString(80, 300, "Które vany przejdą na prąd?")
    c.setFont("Sans", 22)
    c.setFillColor(colors.HexColor("#C9D3DE"))
    c.drawString(80, 262, "Shortlista EV dla floty 38 vanów — i proces, który do niej doprowadził")
    c.setFont("Sans", 16)
    c.drawString(80, 150, "JellyTech: Wojtek (dane) · Rafał (wykonalność) · Walerian (ekonomia i dokumenty)")
    c.setFont("Sans", 12)
    c.setFillColor(colors.HexColor("#8A99AB"))
    c.drawString(80, 120, "Liczby: narzędzie uruchomione na eksporcie 15.06–12.09.2026, reguły Ewy z 30.09")


def s02_answer(c):
    frame(c, 2, "8 EV, 95 637 PLN w 5 lat", "Odpowiedź na początek")
    big_number(c, M, 380, "8", "vanów na liście")
    big_number(c, M, 280, "95 637", "PLN w 5 lat, po zapłacie za EV")
    big_number(c, M, 180, "30%", "dotacji — bez niej żaden się nie zwraca", color=WARN, size=40)
    rows = [["#", "Van", "Model", "Baza EV", "Wynik 5 lat"],
            ["1", "P-12", "Cargo L", "North (z South)", "23 305"],
            ["2", "P-30", "Cargo S", "North", "20 818"],
            ["3", "P-21", "Cargo S", "North", "15 337"],
            ["4", "P-08", "Cargo L", "North", "15 270"],
            ["5", "P-05", "Cargo S", "North (z South)", "9 322"],
            ["6", "P-25", "Cargo S", "North (z South)", "6 596"],
            ["7", "P-13", "Cargo S", "North", "3 818"],
            ["8", "P-04", "Cargo S", "North", "1 171"]]
    table(c, rows, 390, 430, [34, 70, 90, 170, 110])
    para(c, "Kupione z dotacją, wszystkie ładowane w North. Źródło: <font name='Mono'>shortlist.csv</font>, "
            "<font name='Mono'>summary.csv</font>.", 390, 120, 520, SMALL)


def s03_handoff(c):
    frame(c, 3, "Handoff jako dziennik decyzji", "Proces")
    bullets(c, [
        "<b>Każde założenie i decyzja ma godzinę, powód i status</b> — 24 założenia (A1–A24), 16 decyzji (D1–D16).",
        "Założenie zmienione przez Ewę nie znika: dostaje status „zmienione” i numer następcy (np. A4 → A19).",
        "Ewa dostaje to samo po angielsku w <font name='Mono'>ASSUMPTIONS.md</font>: <i>co założyliśmy i mniej więcej kiedy</i>.",
        "Każdy tor prowadzi dziennik; tor C przenosi wpisy do jednego rejestru.",
    ], M, 420, 520)
    table(c, [["Nr", "Godz.", "Wpis (skrót)"],
              ["A6", "10:30", "zasięg zimowy 0,57 × WLTP (nasze źródła)"],
              ["A19", "12:15", "reguła Ewy: 95. percentyl dnia w 60% WLTP"],
              ["D15", "12:19", "wynik ≤ 0 → poza listą, z notatką"],
              ["D16", "12:29", "wszystkie EV kupione → limit 10"]],
          600, 420, [50, 60, 202])


def s04_questions(c):
    frame(c, 4, "Pięć pytań do Ewy — każde z planem B", "Proces")
    bullets(c, [
        "Limit 5 pytań, więc <b>przy każdym napisaliśmy, co przyjmiemy bez odpowiedzi</b> — brak odpowiedzi nigdy nas nie blokował.",
        "Nie pytaliśmy o to, co da się rozstrzygnąć z danych:",
    ], M, 420, 860)
    table(c, [["Rozstrzygnięte z danych", "Jak", "Ewa"],
              ["P-17 = P-17B", "ta sama trasa i kierowca; jeden kończy, drugi zaczyna", "potwierdziła"],
              ["Chłodnie poza pierwszą turą", "5 z 6 przekracza ładowność obu EV", "potwierdziła"],
              ["Ładowność = twardy limit", "najcięższy ładunek z danych", "potwierdziła"]],
          M + 20, 300, [250, 430, 140])
    para(c, "Pytaliśmy o: ładowanie, dotację, zasięg zimowy, leasing diesli, los wycofanych diesli.",
         M + 20, 150, 840, SMALL)


def s05_data(c):
    frame(c, 5, "Dane i liczby kontrolne — policzone dwa razy", "Dane")
    big_number(c, M, 370, "2 777", "kursów (z 2 999; 222 duplikaty)")
    big_number(c, M + 300, 370, "344 952", "km łącznie")
    big_number(c, M + 620, 370, "38", "vanów ocenionych")
    bullets(c, [
        "Druga, niezależna metoda: <font name='Mono'>sort -u</font> + <font name='Mono'>awk</font> w powłoce, bez Pythona — ten sam wynik.",
        "Pułapka: <font name='Mono'>awk</font> z polskimi ustawieniami regionalnymi obcina ułamki (343 699 km). Trzeba <font name='Mono'>LC_ALL=C</font>.",
        "Nic po cichu: ujemny licznik P-27 → GPS 90,3 km z <font name='Mono'>WARNING</font>; P-17 → P-17B z wpisem w raporcie.",
    ], M, 250, 860)


def s06_feasibility(c):
    frame(c, 6, "Wykonalność według reguł Ewy", "Wykonalność")
    bullets(c, [
        "<b>Zasięg:</b> 95. percentyl dnia ≤ 60% WLTP (Cargo S 156 km, Cargo L 228 km).",
        "<b>Ładowność:</b> najcięższy ładunek z danych ≤ ładowność EV — twardy limit.",
        "<b>Dwuzmianowe:</b> cały dzień na jednym ładowaniu nocnym.",
        "<b>South:</b> brak ładowarek; do 3 vanów stacjonuje w North.",
        "<b>Model:</b> ten, który w 5 lat daje lepszy wynik.",
    ], M, 420, 470, gap=8)
    x0, y0 = 560, 420
    steps = [("38", "vanów w rejestrze"), ("15", "przechodzi zasięg i ładowność"),
             ("9", "ma dodatni wynik w 5 lat"), ("8", "mieści się w limitach (3 z South)")]
    for i, (n, label) in enumerate(steps):
        w = 340 - i * 40
        y = y0 - i * 78
        c.setFillColor(ACCENT if i == 3 else ACCENT_SOFT)
        c.roundRect(x0 + (340 - w) / 2, y - 60, w, 60, 6, stroke=0, fill=1)
        c.setFont("Sans-Bold", 26)
        c.setFillColor(colors.white if i == 3 else ACCENT)
        c.drawCentredString(x0 + 170, y - 32, n)
        c.setFont("Sans", 12)
        c.setFillColor(colors.white if i == 3 else INK)
        c.drawCentredString(x0 + 170, y - 50, label)


def s07_change(c):
    frame(c, 7, "Odpowiedzi Ewy o 12:00 — ok. 20 minut na zmianę", "Zmiana wymagań")
    table(c, [["", "Rano (nasze założenia)", "Po odpowiedziach Ewy"],
              ["Zasięg", "najgorszy dzień w 57% WLTP", "95. percentyl dnia w 60% WLTP"],
              ["Dwuzmianowe", "doładowanie między trasami", "cały dzień bez ładowania"],
              ["Ładowanie", "North 6, South 0", "North 10, do 3 vanów z South"],
              ["Wynik", "roczna oszczędność na eksploatacji", "5 lat − cena EV po dotacji − wyjście z leasingu"],
              ["Lista", "3 vany", "8 vanów"]],
          M, 420, [150, 330, 384], bold_rows=(5,))
    bullets(c, [
        "Większość zmian to <b>nowe wartości w <font name='Mono'>params.csv</font></b>, nie nowy kod.",
        "Wynik sprawdzony niezależnie przez dwa tory — zgodny co do złotówki.",
    ], M, 180, 860)


def s08_money(c):
    frame(c, 8, "Skąd 95 637 PLN — i gdzie jest ryzyko", "Pieniądze")
    table(c, [["Składnik (8 vanów, 5 lat)", "PLN"],
              ["Oszczędność na eksploatacji (paliwo − prąd + serwis)", "ok. 1 007 600"],
              ["− cena EV po 30% dotacji", "903 000"],
              ["− wyjście z leasingu (P-25, 3 raty)", "8 940"],
              ["= wynik w 5 lat", "95 637"]],
          M, 420, [360, 130], bold_rows=(4,), highlight_rows=(4,))
    bullets(c, [
        "<b>Nie „te, co jeżdżą najwięcej”:</b> 8 z 10 najdłużej jeżdżących ma dzień 206–293 km przy 156 km zasięgu.",
        "<b>P-30 i P-21</b> mają najdłuższe dni 166 i 159 km — zalecamy zostawić dwa diesle jako rezerwę.",
        "Bez dotacji żaden van się nie zwraca: dotacja na jeden Cargo S to 45 000 PLN.",
    ], 580, 420, 330, MID, gap=14)


def s09_sensitivity(c):
    frame(c, 9, "Reguła zasięgu decyduje o liście", "Wrażliwość")
    table(c, [["Jeśli zmienimy jedną regułę", "Vanów", "Wynik 5 lat (PLN)"],
              ["Jak uzgodniono (95. percentyl, 60% WLTP)", "8", "95 637"],
              ["Najgorszy dzień zamiast 95. percentyla", "6", "59 482"],
              ["55% WLTP zamiast 60%", "3", "47 897"],
              ["Baterie po 5 latach (ok. 52% WLTP)", "2", "38 575"],
              ["Bez vanów z South w North", "5", "56 414"]],
          M, 420, [460, 100, 200], bold_rows=(1,), highlight_rows=(1,))
    para(c, "Kompromis CFO i operacji („January plus a margin”) jest wart ok. 36 000 PLN. "
            "To decyzja o ryzyku, nie o rachunkach. Cargo L (P-12, P-08) zostaje na liście w każdym wariancie zasięgu.",
         M, 170, 860, BODY)


def s10_parallel(c):
    frame(c, 10, "Trzy tory równolegle — bez konfliktów", "Jak pracowaliśmy")
    table(c, [["Tor", "Kto", "Zakres"],
              ["A — dane", "Wojtek", "czyszczenie, profil vanów, liczby kontrolne, parametry"],
              ["B — wykonalność", "Rafał", "filtry, wybór modelu, ranking, integracja, eksport"],
              ["C — ekonomia i dokumenty", "Walerian", "wynik w 5 lat, notatka, założenia, instrukcja"]],
          M, 420, [220, 100, 544])
    bullets(c, [
        "<b>KONTRAKT</b> — co sobie przekazujemy: funkcje, kolumny, właściciel każdego pliku.",
        "<b>KONSTYTUCJA</b> — jak piszemy: język, <font name='Mono'>ERROR</font> / <font name='Mono'>WARNING</font>, zaokrąglenia, git.",
        "<b>Pliki testowe w formacie kontraktu</b> — B i C startują, zanim A odda dane.",
        "<b>Testy</b> każdego progu (pod / na / nad) i automat na GitHubie przy każdym wypchnięciu.",
    ], M, 270, 860, gap=6)


def s11_demo(c):
    frame(c, 11, "Demo: to samo polecenie, trzy sytuacje", "Demo")
    items = [
        ("1", "Oryginalny eksport", "--trips trips.csv --vans vans.csv --params params.csv --out results/",
         "38 / 2777 / 344952 · WARNING o P-27 · 8 vanów"),
        ("2", "Jedna liczba w params: percentyl 95 → 100", "--trips trips.csv --vans vans.csv --params params_p100.csv --out results_p100/",
         "6 vanów (bez P-30, P-21) · 95 637 → 59 482 PLN"),
        ("3", "Następny kwartał", "--trips fresh_trips.csv --vans vans.csv --params params.csv --out results_fresh/",
         "41 dni · WARNING: P-39, P-13, P-21 · 7 vanów"),
    ]
    y = 420
    for n, title, cmd, result in items:
        c.setFillColor(ACCENT)
        c.circle(M + 16, y - 12, 16, stroke=0, fill=1)
        c.setFont("Sans-Bold", 16)
        c.setFillColor(colors.white)
        c.drawCentredString(M + 16, y - 18, n)
        c.setFont("Sans-Bold", 17)
        c.setFillColor(INK)
        c.drawString(M + 46, y - 18, title)
        code(c, "python3 ev_shortlist.py " + cmd, M + 46, y - 52, 820)
        c.setFont("Sans", 13)
        c.setFillColor(MUTED)
        c.drawString(M + 46, y - 80, result)
        y -= 118


def s12_analyst(c):
    frame(c, 12, "Co dostaje analityk Ewy", "Wydanie")
    para(c, "Jeden folder (zip), jedno polecenie, Python 3.9+ i nic więcej.", M, 420, 860)
    code(c, "python3 ev_shortlist.py --trips trips.csv --vans vans.csv --params params.csv --out results/",
         M, 368, 864)
    table(c, [["Plik", "Co zawiera"],
              ["shortlist.csv", "lista w formacie importu Ewy"],
              ["summary.csv", "liczby kontrolne i sumy (= sumy kolumn listy)"],
              ["all_vans.csv", "każdy van z powodem: dlaczego na liście albo nie"],
              ["data_report.txt", "co wyczyszczono; każdy WARNING z datą, vanem, trasą"]],
          M, 330, [180, 400])
    bullets(c, [
        "<font name='Mono'>params.csv</font>: jedyne miejsce do edycji.",
        "<font name='Mono'>RERUN.md</font>: kroki, jak czytać powody, co zrobić przy błędzie.",
        "Błąd = jedna linia <font name='Mono'>ERROR</font>, bez śladu stosu.",
        "Zip sprawdzony w pustym katalogu: wynik bajt w bajt jak u nas.",
    ], 660, 330, 250, MID, gap=10)


def s13_close(c):
    frame(c, 13, "Podsumowanie", "Na koniec")
    bullets(c, [
        "<b>Rekomendacja:</b> kupić 8 EV z dotacją (2 × Cargo L, 6 × Cargo S), wszystkie w North; wynik 95 637 PLN w 5 lat.",
        "<b>Ryzyko:</b> dane tylko z lata. Uruchomić narzędzie na eksporcie z IV kwartału przed zakupem.",
        "<b>Proces:</b> założenia z godzinami, kontrakt między torami, parametry zamiast kodu, liczby policzone dwa razy.",
        "<b>Dowód:</b> zmiana wymagań w połowie dnia zajęła ok. 20 minut, a analityk uruchamia całość bez nas.",
    ], M, 420, 860, gap=14)
    c.setFont("Sans-Bold", 28)
    c.setFillColor(ACCENT)
    c.drawString(M, 110, "Pytania?")


SLIDES = [s01_title, s02_answer, s03_handoff, s04_questions, s05_data, s06_feasibility,
          s07_change, s08_money, s09_sensitivity, s10_parallel, s11_demo, s12_analyst, s13_close]


def main():
    assert len(SLIDES) == TOTAL
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Które vany przejdą na prąd? — JellyTech, 30.09.2026")
    c.setAuthor("JellyTech")
    for slide in SLIDES:
        slide(c)
        c.showPage()
    c.save()
    print("Zapisano %s (%d slajdów)" % (OUT, len(SLIDES)))


if __name__ == "__main__":
    main()
