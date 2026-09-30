"""Build the presentation PDF: one page = one slide (16:9), in JellyTech colours.

Not part of the tool (the tool uses the standard library only). Needs reportlab and svglib:
    python3 -m venv /tmp/venv-pdf && /tmp/venv-pdf/bin/pip install reportlab svglib
    /tmp/venv-pdf/bin/python prezentacja/build_slides.py

Brand: colours and logo from www.jellytech.com.pl (primary #C2006B, font Poppins, OFL — assets/OFL.txt).
Figures come from the tool run on the source export at devel 35d8e0b (30.09.2026):
8 vans, 95 637 PLN over five years. Update them here after the 14:45 freeze if they change.
"""
import os

from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from svglib.svglib import svg2rlg

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "PREZENTACJA.pdf")

W, H = 960, 540
M = 48  # side margin

pdfmetrics.registerFont(TTFont("Sans", os.path.join(ASSETS, "Poppins-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Medium", os.path.join(ASSETS, "Poppins-Medium.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Bold", os.path.join(ASSETS, "Poppins-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("Mono", "/System/Library/Fonts/Supplemental/Courier New.ttf"))
# Poppins has no arrow glyph; arrows are drawn in a fallback font
pdfmetrics.registerFont(TTFont("Sym", "/System/Library/Fonts/Supplemental/Arial.ttf"))
MISSING = "\u2192"
for bold, italic in ((0, 0), (0, 1)):
    addMapping("Sans", bold, italic, "Sans")
for bold, italic in ((1, 0), (1, 1)):
    addMapping("Sans", bold, italic, "Sans-Bold")

# JellyTech palette (www.jellytech.com.pl)
BRAND = colors.HexColor("#C2006B")
BRAND_DARK = colors.HexColor("#A20059")
BRAND_LIGHT = colors.HexColor("#FF52B1")
BRAND_SOFT = colors.HexColor("#FBE6F1")
PAPER = colors.HexColor("#FCF8F9")
INK = colors.HexColor("#1A1A1A")
MUTED = colors.HexColor("#5D5F5F")
RULE = colors.HexColor("#E5E2E3")
ROW_ALT = colors.HexColor("#FCF8F9")

BODY = ParagraphStyle("body", fontName="Sans", fontSize=15.5, leading=22, textColor=INK)
MID = ParagraphStyle("mid", fontName="Sans", fontSize=14, leading=19, textColor=INK)
SMALL = ParagraphStyle("small", fontName="Sans", fontSize=12, leading=16, textColor=MUTED)
CELL = ParagraphStyle("cell", fontName="Sans", fontSize=11.5, leading=15, textColor=INK)
CELL_B = ParagraphStyle("cellb", parent=CELL, fontName="Sans-Bold")

LOGO = svg2rlg(os.path.join(ASSETS, "jellytech-logo.svg"))

TOTAL = 15


def logo(c, x, y, width):
    scale = width / LOGO.width
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    renderPDF.draw(LOGO, c, 0, 0)
    c.restoreState()


def frame(c, n, title, kicker=""):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(BRAND)
    c.rect(0, H - 6, W, 6, stroke=0, fill=1)
    logo(c, W - M - 118, H - 58, 118)
    if kicker:
        c.setFont("Sans-Bold", 11)
        c.setFillColor(BRAND)
        c.drawString(M, H - 44, kicker.upper())
    c.setFillColor(INK)
    draw(c, M, H - 82, title, "Sans-Bold", 27)
    c.setStrokeColor(RULE)
    c.setLineWidth(1)
    c.line(M, 36, W - M, 36)
    c.setFont("Sans", 9.5)
    c.setFillColor(MUTED)
    c.drawString(M, 20, "JellyTech · Shortlista EV · 30.09.2026")
    c.drawRightString(W - M, 20, "%d / %d" % (n, TOTAL))


def _sym(text):
    for ch in MISSING:
        text = text.replace(ch, "<font name='Sym'>%s</font>" % ch)
    return text


def draw(c, x, y, text, font, size, align="left"):
    """drawString that switches to the fallback font for glyphs Poppins lacks."""
    parts, buf = [], ""
    for ch in text:
        if ch in MISSING:
            parts += [(buf, font), (ch, "Sym")]
            buf = ""
        else:
            buf += ch
    parts.append((buf, font))
    width = sum(pdfmetrics.stringWidth(t, f, size) for t, f in parts)
    x = x - width / 2 if align == "center" else x - width if align == "right" else x
    for t, f in parts:
        c.setFont(f, size)
        c.drawString(x, y, t)
        x += pdfmetrics.stringWidth(t, f, size)


def para(c, text, x, y_top, width, style=BODY):
    p = Paragraph(_sym(text), style)
    _, h = p.wrap(width, H)
    p.drawOn(c, x, y_top - h)
    return y_top - h


def bullets(c, items, x, y_top, width, style=BODY, gap=9):
    y = y_top
    for item in items:
        c.setFillColor(BRAND)
        c.circle(x + 5, y - style.leading / 2 + 2, 3.5, stroke=0, fill=1)
        y = para(c, item, x + 20, y, width - 20, style) - gap
    return y


def table(c, rows, x, y_top, widths, header=True, bold_rows=(), highlight_rows=()):
    data = [[Paragraph(_sym(str(v)), CELL_B if (header and i == 0) or i in bold_rows else CELL)
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
        style += [("BACKGROUND", (0, 0), (-1, 0), BRAND_SOFT),
                  ("LINEBELOW", (0, 0), (-1, 0), 1.2, BRAND)]
    for i in range(1 if header else 0, len(rows)):
        if i % 2 == 0 and i not in highlight_rows:
            style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    for i in highlight_rows:
        style.append(("BACKGROUND", (0, i), (-1, i), BRAND_SOFT))
    t.setStyle(TableStyle(style))
    _, h = t.wrap(sum(widths), H)
    t.drawOn(c, x, y_top - h)
    return y_top - h


def big_number(c, x, y, value, label, color=BRAND, size=50):
    c.setFont("Sans-Bold", size)
    c.setFillColor(color)
    c.drawString(x, y, value)
    c.setFont("Sans", 13.5)
    c.setFillColor(MUTED)
    c.drawString(x, y - 24, label)


def code(c, text, x, y, width):
    c.setFillColor(INK)
    c.roundRect(x, y - 8, width, 30, 6, stroke=0, fill=1)
    c.setFont("Mono", 12.5)
    c.setFillColor(colors.HexColor("#F2F2F2"))
    c.drawString(x + 12, y + 3, text)


# --- slides -------------------------------------------------------------------

def s01_title(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(BRAND)
    c.rect(0, 0, W, 10, stroke=0, fill=1)
    logo(c, 80, 390, 260)
    c.setFont("Sans-Bold", 12)
    c.setFillColor(BRAND)
    c.drawString(80, 318, "IT CORNER HACKATHON · 30.09.2026")
    c.setFont("Sans-Bold", 42)
    c.setFillColor(INK)
    c.drawString(80, 262, "Które vany przejdą na prąd?")
    c.setFont("Sans", 19)
    c.setFillColor(MUTED)
    c.drawString(80, 224, "Shortlista EV dla floty 38 vanów — założenia, wynik i proces")
    c.setFillColor(BRAND)
    c.roundRect(80, 120, 300, 54, 12, stroke=0, fill=1)
    c.setFont("Sans-Bold", 20)
    c.setFillColor(colors.white)
    c.drawString(98, 140, "8 EV · 95 637 PLN w 5 lat")


def s02_answer(c):
    frame(c, 2, "8 EV, 95 637 PLN w 5 lat", "Odpowiedź na początek")
    big_number(c, M, 380, "8", "vanów na liście")
    big_number(c, M, 280, "95 637", "PLN w 5 lat, po zapłacie za EV")
    big_number(c, M, 180, "30%", "dotacji — bez niej żaden się nie zwraca", color=BRAND_DARK, size=38)
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
            "<font name='Mono'>summary.csv</font>.", 390, 118, 520, SMALL)


def _assumptions(c, rows, y_top=420):
    """Table of assumptions: what, value, source/status."""
    return table(c, [["Założenie", "Wartość", "Skąd"]] + rows, M, y_top, [390, 250, 224])


def s03_range(c):
    frame(c, 3, "Założenia: zasięg i ładowność", "Założenia przyjęte do zadania")
    _assumptions(c, [
        ["Van przechodzi, gdy jego <b>95. percentyl dnia</b> mieści się w zasięgu zimowym",
         "60% WLTP: Cargo S 156 km, Cargo L 228 km", "reguła Ewy (12:15)"],
        ["Dzień = suma wszystkich tras vana w danym dniu", "percentyl jak PERCENTILE.INC w Excelu", "nasza decyzja"],
        ["Vany dwuzmianowe <b>nie ładują się w dzień</b>", "cały dzień na jednym ładowaniu nocnym", "potwierdziła Ewa"],
        ["Zużycie energii zimą", "dane dealera + 10% w skali roku", "nasze założenie"],
        ["Starzenie baterii po 5 latach", "× 0,87 → ok. 52% WLTP; tylko test warunków skrajnych",
         "Geotab: −2,7% rocznie"],
        ["EV musi unieść <b>najcięższy ładunek</b>, jaki van wiózł", "twardy limit, bez rozkładania ładunku",
         "potwierdziła Ewa"],
        ["Chłodnie zostają na dieslu w 1. roku", "6 vanów", "potwierdziła Ewa"],
    ])


def s04_money_assumptions(c):
    frame(c, 4, "Założenia: ładowanie i wynik finansowy", "Założenia przyjęte do zadania")
    _assumptions(c, [
        ["Punkty ładowania", "North 10 (6 + 4 zamówione), South 0; jeden EV na punkt", "potwierdziła Ewa"],
        ["Vany z South w North", "najwyżej 3, trasy bez zmian; wybieramy te z najwyższym wynikiem",
         "Ewa + nasza reguła wyboru"],
        ["Ładowanie w nocy", "taryfa nocna 0,58 PLN/kWh", "nasze założenie"],
        ["Wynik = 5 × (paliwo − prąd + różnica serwisu) − cena EV po dotacji − wyjście z leasingu",
         "bez rat diesla i wartości odsprzedaży", "reguła Ewy"],
        ["EV <b>kupione</b>, nie leasingowane", "Cargo S po dotacji 105 000 vs 60 rat 174 000 PLN",
         "wniosek z reguły dotacji"],
        ["Leasing diesla kończący się w ciągu 12 mies.", "bez opłaty (granica włącznie); dłuższy: 3 raty",
         "Ewa; „włącznie” — nasze"],
        ["Serwis", "diesel 0,34 PLN/km, EV 0,14 PLN/km (szacunek dealera)", "dane firmy i dealera"],
        ["Na liście tylko van z dodatnim wynikiem", "wynik ≤ 0 → poza listą, z powodem", "nasza decyzja"],
    ])


def s05_data_assumptions(c):
    frame(c, 5, "Założenia: dane i narzędzie", "Założenia przyjęte do zadania")
    _assumptions(c, [
        ["Trasy i ładunki są takie same przez cały rok", "roczne km = km z okresu × 365 ÷ dni okresu",
         "nasze założenie; sprawdzi eksport z IV kw."],
        ["Dystans z licznika; GPS tylko, gdy licznik pusty lub ≤ 0", "zawsze z ostrzeżeniem w raporcie",
         "Ewa: „trust the odometer”"],
        ["P-17 i P-17B to ten sam van", "liczony jako P-17B", "z danych; potwierdziła Ewa"],
        ["Identyczne wiersze to duplikaty", "usuwane, z liczbą w raporcie", "nasza decyzja"],
        ["Van spoza rejestru", "poza liczbami, z ostrzeżeniem: co dopisać", "nasza decyzja"],
        ["Analityk zna wiersz poleceń i ma Pythona 3", "zmienia tylko <font name='Mono'>params.csv</font>",
         "przyjęte, niepotwierdzone"],
        ["Kolejny eksport ma te same kolumny", "brak kolumny → jasny błąd, bez zgadywania",
         "przyjęte, niepotwierdzone"],
    ])


def s06_winter(c):
    frame(c, 6, "Skąd 60%? Nasze oszacowanie dało 57%", "Założenia przyjęte do zadania")
    table(c, [["Czynnik", "Wartość", "Źródło"],
              ["Dzień projektowy −10 °C", "—", "Poznań: średnie minimum w styczniu −3 °C (Weather Spark)"],
              ["Temperatura", "× 0,70", "ok. 70% zasięgu przy −7 °C, 30 000+ aut (Recurrent)"],
              ["Ładunek", "× 0,90", "van średni: −7% przy połowie, −11% przy pełnym (Arval / What Van?)"],
              ["Rezerwa na powrót do bazy", "× 0,90", "margines operacyjny, nasz wybór"],
              ["Razem", "≈ 0,57", "rano; reguła Ewy o 12:15: 0,60"]],
          M, 420, [230, 90, 544], bold_rows=(5,), highlight_rows=(5,))
    para(c, "Liczyliśmy od rana na własnym, udokumentowanym założeniu. Gdy Ewa podała 60%, "
            "wiedzieliśmy, że to rozsądna liczba na styczeń z marginesem — i ile ryzyka niesie.",
         M, 190, 860, BODY)


def s07_feasibility(c):
    frame(c, 7, "Wykonalność: 38 → 8", "Wynik")
    bullets(c, [
        "<b>15</b> vanów mieści się w zasięgu i ładowności.",
        "<b>9</b> z nich zwraca się w 5 lat.",
        "<b>8</b> mieści się w limitach: P-31 jest na plusie, ale byłby 4. vanem z South.",
        "Model dla każdego vana: ten, który w 5 lat daje lepszy wynik.",
        "Każdy van spoza listy ma w <font name='Mono'>all_vans.csv</font> zapisany powód.",
    ], M, 420, 470, gap=8)
    x0, y0 = 560, 420
    steps = [("38", "vanów w rejestrze"), ("15", "zasięg i ładowność"),
             ("9", "dodatni wynik w 5 lat"), ("8", "w limitach (3 z South)")]
    for i, (n, label) in enumerate(steps):
        w = 340 - i * 40
        y = y0 - i * 78
        last = i == 3
        c.setFillColor(BRAND if last else BRAND_SOFT)
        c.roundRect(x0 + (340 - w) / 2, y - 60, w, 60, 10, stroke=0, fill=1)
        c.setFont("Sans-Bold", 24)
        c.setFillColor(colors.white if last else BRAND)
        c.drawCentredString(x0 + 170, y - 30, n)
        c.setFont("Sans", 11)
        c.setFillColor(colors.white if last else INK)
        c.drawCentredString(x0 + 170, y - 49, label)


def s08_money(c):
    frame(c, 8, "Skąd 95 637 PLN — i gdzie jest ryzyko", "Wynik")
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
    frame(c, 9, "Reguła zasięgu decyduje o liście", "Wrażliwość na założenia")
    table(c, [["Jeśli zmienimy jedno założenie", "Vanów", "Wynik 5 lat (PLN)"],
              ["Jak uzgodniono (95. percentyl, 60% WLTP)", "8", "95 637"],
              ["Najgorszy dzień zamiast 95. percentyla", "6", "59 482"],
              ["55% WLTP zamiast 60%", "3", "47 897"],
              ["Baterie po 5 latach (ok. 52% WLTP)", "2", "38 575"],
              ["Bez vanów z South w North", "5", "56 414"]],
          M, 420, [460, 100, 200], bold_rows=(1,), highlight_rows=(1,))
    para(c, "Kompromis CFO i operacji („January plus a margin”) jest wart ok. 36 000 PLN. "
            "To decyzja o ryzyku, nie o rachunkach. Cargo L (P-12, P-08) zostaje na liście w każdym wariancie zasięgu.",
         M, 170, 860, BODY)


def s10_log(c):
    frame(c, 10, "Każde założenie ma godzinę, powód i status", "Proces")
    bullets(c, [
        "Jeden dziennik od pierwszej godziny: <b>24 założenia, 16 decyzji</b>.",
        "Zmienione założenie nie znika — dostaje status „zmienione” i następcę.",
        "Ewa dostaje ten sam rejestr po angielsku: <i>co założyliśmy i mniej więcej kiedy</i>.",
        "<b>5 pytań do Ewy, każde z planem B</b> — brak odpowiedzi nigdy nas nie zatrzymał.",
        "Nie pytaliśmy o to, co da się rozstrzygnąć z danych (P-17, chłodnie) — Ewa potwierdziła oba wnioski.",
    ], M, 420, 500, MID, gap=10)
    table(c, [["Nr", "Godz.", "Wpis (skrót)"],
              ["A6", "10:30", "zasięg zimowy 0,57 × WLTP (nasze źródła)"],
              ["A19", "12:15", "reguła Ewy: 95. percentyl dnia w 60% WLTP"],
              ["D15", "12:19", "wynik ≤ 0 → poza listą, z powodem"],
              ["D16", "12:29", "wszystkie EV kupione → limit 10"]],
          590, 420, [48, 58, 216])


def s11_change(c):
    frame(c, 11, "Odpowiedzi Ewy o 12:00 — ok. 20 minut na zmianę", "Proces")
    table(c, [["", "Rano (nasze założenia)", "Po odpowiedziach Ewy"],
              ["Zasięg", "najgorszy dzień w 57% WLTP", "95. percentyl dnia w 60% WLTP"],
              ["Dwuzmianowe", "doładowanie między trasami", "cały dzień bez ładowania"],
              ["Ładowanie", "North 6, South 0", "North 10, do 3 vanów z South"],
              ["Wynik", "roczna oszczędność na eksploatacji", "5 lat − cena EV po dotacji − wyjście z leasingu"],
              ["Lista", "3 vany", "8 vanów"]],
          M, 420, [150, 330, 384], bold_rows=(5,))
    bullets(c, [
        "Większość zmian to <b>nowe wartości w <font name='Mono'>params.csv</font></b>, nie nowy kod.",
        "Wynik sprawdzony niezależnie drugą metodą — zgodny co do złotówki.",
    ], M, 180, 860)


def s12_parallel(c):
    frame(c, 12, "Praca równoległa bez konfliktów", "Proces")
    cards = [
        ("Kontrakt", "co sobie przekazujemy: funkcje, kolumny, właściciel każdego pliku"),
        ("Konstytucja", "jak piszemy: język, format błędów i ostrzeżeń, zaokrąglenia, git"),
        ("Parametry", "każda liczba w <font name='Mono'>params.csv</font> — odpowiedź Ewy to zmiana wartości, "
                      "nie kodu"),
        ("Weryfikacja", "liczby kontrolne policzone dwa razy dwiema metodami; każdy próg testowany pod / na / nad"),
    ]
    for i, (head, text) in enumerate(cards):
        x = M + (i % 2) * 438
        y = 420 - (i // 2) * 150
        c.setFillColor(PAPER)
        c.roundRect(x, y - 128, 424, 128, 12, stroke=0, fill=1)
        c.setFillColor(BRAND)
        c.roundRect(x, y - 128, 6, 128, 3, stroke=0, fill=1)
        c.setFont("Sans-Bold", 17)
        c.setFillColor(INK)
        c.drawString(x + 22, y - 34, head)
        para(c, text, x + 22, y - 48, 380, MID)
    para(c, "Testy uruchamiają się automatycznie na GitHubie przy każdym wypchnięciu, na prawdziwym eksporcie.",
         M, 112, 860, SMALL)


def s13_demo(c):
    frame(c, 13, "Demo: to samo polecenie, trzy sytuacje", "Demo")
    items = [
        ("1", "Oryginalny eksport",
         "--trips trips.csv --vans vans.csv --params params.csv --out results/",
         "38 / 2777 / 344952 · WARNING o P-27 · 8 vanów"),
        ("2", "Jedno założenie w params: percentyl 95 → 100",
         "--trips trips.csv --vans vans.csv --params params_p100.csv --out results_p100/",
         "6 vanów (bez P-30, P-21) · 95 637 → 59 482 PLN"),
        ("3", "Następny kwartał",
         "--trips fresh_trips.csv --vans vans.csv --params params.csv --out results_fresh/",
         "41 dni · WARNING: P-39, P-13, P-21 · 7 vanów"),
    ]
    y = 420
    for n, title, cmd, result in items:
        c.setFillColor(BRAND)
        c.circle(M + 16, y - 12, 16, stroke=0, fill=1)
        c.setFont("Sans-Bold", 15)
        c.setFillColor(colors.white)
        c.drawCentredString(M + 16, y - 17, n)
        c.setFillColor(INK)
        draw(c, M + 46, y - 18, title, "Sans-Bold", 16)
        code(c, "python3 ev_shortlist.py " + cmd, M + 46, y - 52, 820)
        c.setFillColor(MUTED)
        draw(c, M + 46, y - 80, result, "Sans", 12.5)
        y -= 118


def s14_analyst(c):
    frame(c, 14, "Co dostaje analityk Ewy", "Wydanie")
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
    ], 660, 330, 250, MID, gap=8)


def s15_close(c):
    frame(c, 15, "Podsumowanie", "Na koniec")
    bullets(c, [
        "<b>Rekomendacja:</b> kupić 8 EV z dotacją (2 × Cargo L, 6 × Cargo S), wszystkie w North; wynik 95 637 PLN w 5 lat.",
        "<b>Kluczowe założenia:</b> 95. percentyl dnia w 60% WLTP, najcięższy ładunek jako limit, "
        "bez ładowania w dzień, zakup z dotacją, horyzont 5 lat.",
        "<b>Ryzyko:</b> dane tylko z lata. Uruchomić narzędzie na eksporcie z IV kwartału przed zakupem.",
        "<b>Proces:</b> zmiana wymagań w połowie dnia zajęła ok. 20 minut, a analityk uruchamia całość bez nas.",
    ], M, 420, 860, gap=14)
    c.setFillColor(BRAND)
    c.roundRect(M, 88, 180, 50, 12, stroke=0, fill=1)
    c.setFont("Sans-Bold", 22)
    c.setFillColor(colors.white)
    c.drawString(M + 26, 106, "Pytania?")


SLIDES = [s01_title, s02_answer, s03_range, s04_money_assumptions, s05_data_assumptions, s06_winter,
          s07_feasibility, s08_money, s09_sensitivity, s10_log, s11_change, s12_parallel,
          s13_demo, s14_analyst, s15_close]


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
