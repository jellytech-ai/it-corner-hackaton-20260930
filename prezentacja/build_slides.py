"""Build the presentation PDF: one page = one slide (16:9), in JellyTech colours.

Not part of the tool (the tool uses the standard library only). Needs reportlab and svglib:
    python3 -m venv /tmp/venv-pdf && /tmp/venv-pdf/bin/pip install reportlab svglib
    /tmp/venv-pdf/bin/python prezentacja/build_slides.py

Brand: colours and logo from www.jellytech.com.pl (primary #C2006B, font Poppins, OFL — assets/OFL.txt).
Figures come from the tool run at tag v1.1 (30.09.2026, after Ewa's change of 15:18): both exports,
40 vans, worst-day rule. 7 vans, 85 750 PLN over five years.
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

TOTAL = 18
CURRENT = 0  # slide number, set in main() so slides can be reordered freely


def logo(c, x, y, width):
    scale = width / LOGO.width
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    renderPDF.draw(LOGO, c, 0, 0)
    c.restoreState()


def frame(c, n, title, kicker=""):
    n = CURRENT or n
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
    size = 12.5
    while size > 7 and pdfmetrics.stringWidth(text, "Mono", size) > width - 24:
        size -= 0.25  # long commands shrink to stay inside the box
    c.setFont("Mono", size)
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
    c.drawString(80, 224, "Shortlista EV dla floty 40 vanów — założenia, wynik i proces")
    c.setFillColor(BRAND)
    c.roundRect(80, 120, 300, 54, 12, stroke=0, fill=1)
    c.setFont("Sans-Bold", 20)
    c.setFillColor(colors.white)
    c.drawString(98, 140, "7 EV · 85 750 PLN w 5 lat")


def s02_answer(c):
    frame(c, 2, "7 EV, 85 750 PLN w 5 lat", "Odpowiedź na początek")
    big_number(c, M, 380, "7", "vanów na liście")
    big_number(c, M, 280, "85 750", "PLN w 5 lat, po zapłacie za EV")
    big_number(c, M, 180, "30%", "dotacji — bez niej żaden się nie zwraca", color=BRAND_DARK, size=38)
    rows = [["#", "Van", "Model", "Baza EV", "Wynik 5 lat"],
            ["1", "P-12", "Cargo L", "North (z South)", "21 680"],
            ["2", "P-39", "Cargo S", "North (nowy van)", "17 092"],
            ["3", "P-40", "Cargo S", "North (z South, nowy)", "17 092"],
            ["4", "P-08", "Cargo L", "North", "14 589"],
            ["5", "P-05", "Cargo S", "North (z South)", "9 549"],
            ["6", "P-13", "Cargo S", "North", "3 551"],
            ["7", "P-04", "Cargo S", "North", "2 197"]]
    table(c, rows, 390, 430, [34, 70, 90, 170, 110])
    para(c, "Kupione z dotacją, wszystkie ładowane w North. Źródło: <font name='Mono'>shortlist.csv</font>, "
            "<font name='Mono'>summary.csv</font>.", 390, 118, 520, SMALL)


def _assumptions(c, rows, y_top=420):
    """Table of assumptions: what, value, source/status."""
    return table(c, [["Założenie", "Wartość", "Skąd"]] + rows, M, y_top, [390, 250, 224])


def s03_range(c):
    frame(c, 3, "Założenia: zasięg i ładowność", "Założenia przyjęte do zadania")
    _assumptions(c, [
        ["Van przechodzi, gdy jego <b>najgorszy dzień</b> mieści się w zasięgu zimowym",
         "60% WLTP: Cargo S 156 km, Cargo L 228 km", "reguła Ewy z 15:18 (w południe: 95. percentyl)"],
        ["Dzień = suma wszystkich tras vana w danym dniu", "oba eksporty razem: 104 dni, 89 z dostawami",
         "Ewa: łączyć eksporty"],
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
        ["Analityk zna wiersz poleceń i ma Pythona 3", "zmienia tylko <font name='Mono'>params.csv</font>",
         "Ewa: „one command to rerun it”"],
        ["Kolejny eksport ma te same kolumny — <b>obalone o 15:18</b> (<font name='Mono'>odo_km</font>)",
         "jasny błąd z nazwą kolumny; jawny alias w <font name='Mono'>params.csv</font>", "obsłużone bez zgadywania"],
        ["Niemożliwy odczyt licznika (P-13: 1383 km na jednej trasie)", "powyżej 500 km → GPS, z ostrzeżeniem",
         "nasza decyzja"],
        ["Nowe vany P-39 i P-40: 12 dni danych", "roczne km z ich własnych dni dostaw", "Ewa: oceniać na tym, co jest"],
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
    frame(c, 7, "Wykonalność: 40 → 7", "Wynik")
    bullets(c, [
        "<b>14</b> vanów mieści się w zasięgu i ładowności.",
        "<b>8</b> z nich zwraca się w 5 lat.",
        "<b>7</b> mieści się w limitach: P-25 jest na plusie, ale byłby 4. vanem z South.",
        "Model dla każdego vana: ten, który w 5 lat daje lepszy wynik.",
        "Każdy van spoza listy ma w <font name='Mono'>all_vans.csv</font> zapisany powód.",
    ], M, 420, 470, gap=8)
    x0, y0 = 560, 420
    steps = [("40", "vanów w rejestrze"), ("14", "zasięg i ładowność"),
             ("8", "dodatni wynik w 5 lat"), ("7", "w limitach (3 z South)")]
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
    frame(c, 8, "Skąd 85 750 PLN — i gdzie jest ryzyko", "Wynik")
    table(c, [["Składnik (7 vanów, 5 lat)", "PLN"],
              ["Oszczędność na eksploatacji (paliwo − prąd + serwis)", "ok. 902 350"],
              ["− cena EV po 30% dotacji", "798 000"],
              ["− wyjście z leasingu (P-39, P-40, po 3 raty)", "18 600"],
              ["= wynik w 5 lat", "85 750"]],
          M, 420, [360, 130], bold_rows=(4,), highlight_rows=(4,))
    bullets(c, [
        "<b>Nie „te, co jeżdżą najwięcej”:</b> 8 z 10 vanów o największym przebiegu ma najgorszy dzień 208–306 km.",
        "<b>P-13 i P-04</b> zwracają się ledwo (3 551 i 2 197 PLN); przy 303 dniach dostaw w roku P-04 wypada.",
        "<b>P-39 i P-40</b> oceniamy na 12 dniach jazdy.",
        "Bez dotacji żaden van się nie zwraca: dotacja na jeden Cargo S to 45 000 PLN.",
    ], 580, 420, 330, MID, gap=14)


def s09_sensitivity(c):
    frame(c, 9, "Reguła zasięgu decyduje o liście", "Wrażliwość na założenia")
    table(c, [["Jeśli zmienimy jedno założenie", "Vanów", "Wynik 5 lat (PLN)"],
              ["Reguła Ewy z 15:18 (najgorszy dzień, 60% WLTP)", "7", "85 750"],
              ["95. percentyl dnia (reguła z południa) na nowych danych", "9", "122 868"],
              ["55% WLTP zamiast 60%", "3", "53 361"],
              ["Baterie po 5 latach (ok. 52% WLTP)", "1", "14 589"],
              ["Bez vanów z South w North", "4", "37 429"],
              ["303 dni dostaw w roku (święta wolne)", "6", "59 743"],
              ["Licznik P-13 (1383 km) wzięty dosłownie", "6", "82 199"]],
          M, 420, [460, 100, 200], bold_rows=(1,), highlight_rows=(1,))
    para(c, "Zasada „żaden van nigdy nie zawiedzie” kosztuje dwa vany i ok. 37 000 PLN względem reguły z południa. "
            "To decyzja o ryzyku, nie o rachunkach. P-08 zostaje na liście w każdym wariancie.",
         M, 118, 860, MID)


def s10_log(c):
    frame(c, 10, "Każde założenie ma godzinę, powód i status", "Proces")
    bullets(c, [
        "Jeden dziennik od pierwszej godziny: <b>33 założenia, 19 decyzji</b>.",
        "Zmienione założenie nie znika — dostaje status „zmienione” i następcę.",
        "Ewa dostaje ten sam rejestr po angielsku: <i>co założyliśmy i mniej więcej kiedy</i>.",
        "<b>5 pytań do Ewy, każde z planem B</b> — brak odpowiedzi nigdy nas nie zatrzymał.",
        "Nie pytaliśmy o to, co da się rozstrzygnąć z danych (P-17, chłodnie) — Ewa potwierdziła oba wnioski.",
    ], M, 420, 500, MID, gap=10)
    table(c, [["Nr", "Godz.", "Wpis (skrót)"],
              ["A6", "10:30", "zasięg zimowy 0,57 × WLTP (nasze źródła)"],
              ["A19", "12:15", "reguła Ewy: 95. percentyl dnia w 60% WLTP"],
              ["D15", "12:19", "wynik ≤ 0 → poza listą, z powodem"],
              ["A26", "15:21", "reguła Ewy: najgorszy dzień w 60% WLTP"]],
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


def s12_second_change(c):
    frame(c, 12, "15:18: nowe dane i nowa reguła — 15:27 gotowe", "Proces")
    table(c, [["Van", "Zmiana", "Przyczyna", "Dlaczego"],
              ["P-30", "wypadł", "nowa reguła", "najgorszy dzień 166,2 km przy 156 km zasięgu zimowego Cargo S"],
              ["P-21", "wypadł", "nowa reguła", "najgorszy dzień 158,6 km"],
              ["P-25", "wypadł", "nowe dane", "trzecie miejsce dla vana z South bierze nowy P-40 (wyższy wynik)"],
              ["P-39", "wszedł", "nowe dane", "nowy van; pasuje do Cargo S i się zwraca"],
              ["P-40", "wszedł", "nowe dane", "nowy van z South; pasuje do Cargo S i się zwraca"]],
          M, 420, [70, 90, 120, 584])
    bullets(c, [
        "Kolumna <font name='Mono'>odo_km</font> zamiast <font name='Mono'>odometer_km</font>: narzędzie stanęło "
        "i nazwało kolumnę; poprawka to jedna linia w <font name='Mono'>params.csv</font>.",
        "Nowa reguła to jedna liczba: <font name='Mono'>range_check_percentile</font> 95 → 100.",
        "Licznik 1383 km na jednej trasie (P-13): ostrzeżenie i dystans z GPS — wzięty dosłownie wyrzuciłby P-13.",
        "<font name='Mono'>impact.csv</font> z czterech uruchomień: stare i nowe dane × stara i nowa reguła. "
        "O 15:33 wpis w wątku i wydanie v1.1.",
    ], M, 232, 864, MID, gap=6)


def s12_parallel(c):
    frame(c, 13, "Praca równoległa bez konfliktów", "Proces")
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


def sA_sdlc(c):
    frame(c, 0, "Nasz SDLC: najpierw specyfikacja, potem kod", "Proces")
    table(c, [["Faza", "Artefakt", "Bramka do kolejnej fazy"],
              ["1. Wymagania", "rejestr 33 założeń i 19 decyzji z godzinami; 5 pytań do Ewy z planem B",
               "każde założenie ma numer, godzinę i status"],
              ["2. Projekt", "kontrakt (wersje 1.0 → 2.3), konstytucja, <font name='Mono'>params.csv</font>, pliki testowe",
               "zmiana kolumny lub parametru = najpierw nowa wersja kontraktu"],
              ["3. Implementacja", "4 moduły + <font name='Mono'>impact.py</font>, 3 tory równolegle", "testy lokalnie"],
              ["4. Weryfikacja", "104 testy, macierz wymaganie → test, CI, liczby liczone dwiema metodami",
               "CI zielone, żaden test pominięty"],
              ["5. Wydanie", "PR <font name='Mono'>devel</font> → <font name='Mono'>main</font>, tagi v1.0 i v1.1, zip z tagu",
               "przegląd drugiej osoby (z braku czasu: jednej)"],
              ["6. Akceptacja", "zip w pustym katalogu; świeży eksport; typowe pomyłki analityka",
               "wynik bajt w bajt, zawsze czytelny ERROR"],
              ["7. Utrzymanie", "<font name='Mono'>RERUN.md</font>: co zmieniać co kwartał, co robić przy błędzie", "—"]],
          M, 424, [130, 420, 314])
    para(c, "Dwie zmiany wymagań przeszły tę samą drogę — wymaganie → kontrakt → parametr → kod → test: "
            "w południe w 33 minuty (3 → 8 vanów), o 15:18 w kwadrans do wpisu w wątku (8 → 7 vanów). "
            "Bez przepisywania narzędzia.", M, 128, 864, MID)


def sB_timeline(c):
    frame(c, 0, "Oś czasu: 10:10 → 15:33", "Proces")
    x0, x1, y = M + 10, W - M - 10, 262
    start, end = 10 * 60, 16 * 60
    c.setStrokeColor(RULE)
    c.setLineWidth(3)
    c.line(x0, y, x1, y)
    c.setFont("Sans", 10)
    c.setFillColor(MUTED)
    for hour in range(10, 17):
        hx = x0 + (hour * 60 - start) / (end - start) * (x1 - x0)
        c.setLineWidth(1)
        c.line(hx, y - 5, hx, y + 5)
    events = [("10:10", "start: profil danych", 1, False), ("11:09", "5 pytań do Ewy", -1, False),
              ("11:19", "kontrakt, 3 tory", 2, False), ("11:55", "pierwsze scalenie: 3 vany", -2, False),
              ("12:00", "odpowiedzi Ewy: nowe reguły", 3, True), ("12:33", "8 vanów, 95 637 PLN", -3, False),
              ("12:55", "test ponownego uruchomienia", 1, False), ("13:07", "CI, macierz śladowania", -1, False),
              ("14:45", "zamrożenie liczb", 2, False), ("15:18", "Ewa: nowe dane, nowa reguła", -2, True),
              ("15:20", "wydanie v1.0", 3, False), ("15:33", "v1.1: 7 vanów, wpis w wątku", 1, False)]
    label = ParagraphStyle("tl", parent=SMALL, fontSize=10.5, leading=13, alignment=1, textColor=INK)
    label_b = ParagraphStyle("tlb", parent=label, fontName="Sans-Bold", textColor=BRAND)
    for hhmm, text, level, major in events:
        h, m = hhmm.split(":")
        ex = x0 + (int(h) * 60 + int(m) - start) / (end - start) * (x1 - x0)
        ey = y + level * 44
        c.setStrokeColor(BRAND if major else RULE)
        c.setLineWidth(1.4 if major else 0.8)
        c.line(ex, y, ex, ey - (0 if level < 0 else 4))
        c.setFillColor(BRAND if major else BRAND_LIGHT)
        c.circle(ex, y, 7 if major else 4.5, stroke=0, fill=1)
        pgh = Paragraph("<b>%s</b><br/>%s" % (hhmm, text), label_b if major else label)
        w, hgt = pgh.wrap(104, 80)
        lx = min(max(ex - 52, M - 6), W - M - 98)
        pgh.drawOn(c, lx, ey if level > 0 else ey - hgt)
    para(c, "105 commitów · 23 scalenia · 3 osoby · 104 testy · 2 wydania. Dwie zmiany wymagań od klientki "
            "(wyróżnione): po każdej nowy wynik powstał przez zmianę parametrów i danych, nie przez przepisanie kodu.",
         M, 84, 864, MID)


def sC_tooling(c):
    frame(c, 0, "Tooling", "Proces")
    table(c, [["Obszar", "Narzędzie", "Do czego"],
              ["Asystent AI", "Claude Code (model Opus) w terminalu", "implementacja, testy, integracja, weryfikacja, dokumenty"],
              ["Izolacja pracy", "git worktree na tor (Orca)", "każda sesja we własnym katalogu"],
              ["Edytor", "Cursor", "podgląd i ręczne poprawki"],
              ["Repozytorium", "GitHub: gałęzie torów, <font name='Mono'>devel</font>, PR do <font name='Mono'>main</font>",
               "scalanie przez merge, bez rebase i force push"],
              ["CI", "GitHub Actions: Python 3.9 i 3.13", "pominięty test = czerwone CI"],
              ["Kontakt z klientką", "GitHub Discussions (wątek z Ewą), Slack", "pytania, odpowiedzi, dostawa"],
              ["Narzędzie dla Ewy", "Python, tylko biblioteka standardowa, <font name='Mono'>unittest</font>",
               "zero instalacji u analityka"],
              ["Kontrola niezależna", "<font name='Mono'>sort -u</font> + <font name='Mono'>awk</font> (LC_ALL=C); drugie obliczenie w innej sesji",
               "druga metoda na liczby kontrolne i na shortlistę"],
              ["Ciągłość sesji AI", "pliki przekazania, wiadomości między sesjami, skille",
               "kontekst między sesjami, stały sposób pracy"]],
          M, 424, [170, 370, 324])


def _card(c, x, y_top, width, height, head, items, accent=BRAND):
    c.setFillColor(PAPER)
    c.roundRect(x, y_top - height, width, height, 10, stroke=0, fill=1)
    c.setFillColor(accent)
    c.roundRect(x, y_top - height, 5, height, 2.5, stroke=0, fill=1)
    c.setFont("Sans-Bold", 14)
    c.setFillColor(INK)
    c.drawString(x + 16, y_top - 26, head)
    style = ParagraphStyle("card", parent=CELL, fontSize=10.5, leading=13.5)
    y = y_top - 40
    for item in items:
        c.setFillColor(accent)
        c.circle(x + 20, y - 7, 2.5, stroke=0, fill=1)
        y = para(c, item, x + 30, y, width - 42, style) - 5


def sD_human_ai(c):
    frame(c, 0, "Gdzie decydował człowiek, a co zrzuciliśmy na AI", "Proces")
    w, h, top = 280, 296, 428
    _card(c, M, top, w, h, "Człowiek decydował", [
        "co jest problemem Ewy; które 5 pytań zadać i jaki plan B przy każdym",
        "podział na tory, kontrakt i konstytucja — reguły gry",
        "każde scalenie do <font name='Mono'>devel</font> i każda wysyłka do Ewy",
        "rozstrzygnięcia biznesowe: na liście tylko vany, które się zwracają; po zamrożeniu zastrzeżenie "
        "zamiast zmiany formuły",
        "zakres wydania: co idzie do Ewy, co do prezentacji",
        "zatrzymanie pracy AI",
    ], BRAND_DARK)
    _card(c, M + w + 12, top, w, h, "AI proponowało, człowiek zatwierdzał", [
        "zasięg zimowy 0,57 × WLTP ze źródłami — przyjęty rano jako założenie",
        "wybór pytań: P-17 i chłodnie rozstrzygnięte z danych zamiast pytać Ewę",
        "reguły rankingu (wynik ≤ 0 poza listą, 3 vany z South) — do rejestru",
        "nowe parametry progu „blisko” — przyjęte przez właściciela <font name='Mono'>params.csv</font>",
        "o 15:18, pod presją czasu: GPS dla licznika 1383 km i skalowanie nowych vanów — AI wybrało, "
        "zapisało w rejestrze i zgłosiło",
    ], BRAND)
    _card(c, M + 2 * (w + 12), top, w, h, "AI zrobiło samo", [
        "profil danych i pułapki: duplikaty, P-17, ujemny licznik, <font name='Mono'>odo_km</font>, 1383 km",
        "kod i testy z kryterium „gotowe, gdy”",
        "odczyt odpowiedzi Ewy u źródła, także z wątków innych zespołów",
        "kontrola krzyżowa: liczby i shortlista policzone drugą metodą",
        "przegląd kodu pod kątem konstytucji — 2 realne błędy",
        "demo, zip, wydanie, prezentacja",
    ], BRAND_LIGHT)
    para(c, "AI napisało większość kodu i sprawdzeń, ale żadna decyzja o tym, co Ewa dostaje i na jakich "
            "założeniach, nie zapadła bez człowieka — każda jest w rejestrze z godziną.", M, 116, 864, MID)


def sE_lessons(c):
    frame(c, 0, "Co byśmy zmienili, robiąc to jeszcze raz", "Proces")
    table(c, [["Co się stało", "Co zrobilibyśmy inaczej"],
              ["Reguła Ewy o 12:00 zmieniła wszystko (3 → 8 vanów)",
               "pytać najpierw o to, co najbardziej zmienia wynik; od rana czytać wątki innych zespołów"],
              ["Kod wyprzedził kontrakt (cztery kolumny dopisane po fakcie)", "„najpierw kontrakt” od pierwszej minuty"],
              ["Pliki <font name='Mono'>.pyc</font> w repo, CI dopiero o 13:07",
               "<font name='Mono'>.gitignore</font>, CI i test na prawdziwych danych w kroku 0"],
              ["Edytor nadpisał pliki nieaktualnym buforem — commit bez kodu",
               "jedno narzędzie edytuje plik naraz; po commicie <font name='Mono'>git show --stat</font>"],
              ["Godziny w dzienniku wpisane z szacunku, nie z zegara", "godziny brać z commitów"],
              ["Scenariusz demo przestał działać po zmianie reguł", "test scenariusza demo w CI"],
              ["Założenie „te same kolumny co kwartał” upadło przy pierwszym nowym eksporcie",
               "aliasy kolumn i test na „zepsutym” eksporcie od początku"],
              ["Ten sam fakt w kilku dokumentach", "jedno źródło, reszta tylko odsyła"],
              ["Akceptację robiły osoby, które znają kod", "test przez kogoś spoza zespołu, choćby 10 minut"]],
          M, 424, [420, 444])


def s13_demo(c):
    frame(c, 14, "Demo: to samo narzędzie przed zmianą i po niej", "Demo")
    items = [
        ("1", "Stan z południa: jeden eksport, reguła 95. percentyla",
         "ev_shortlist.py --trips trips.csv --vans vans.csv --params params_lunch.csv --out lunch/",
         "38 / 2777 / 344952 · WARNING o P-27 · 8 vanów · 95 637 PLN"),
        ("2", "Po 15:18: drugi eksport, nowy rejestr, reguła najgorszego dnia",
         "ev_shortlist.py --trips trips.csv trips_latest.csv --vans vans_latest.csv --params params.csv --out new/",
         "40 / 3227 / 401186 · alias odo_km · WARNING: licznik P-13 1383 km · 7 vanów · 85 750 PLN"),
        ("3", "Co weszło, co wypadło i dlaczego",
         "impact.py --old-params params_lunch.csv … --params params.csv --out new/   (pełne polecenie: RERUN.md)",
         "impact.csv: P-30 i P-21 wypadły (nowa reguła) · P-25 wypadł (nowe dane) · P-39 i P-40 weszły"),
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
        code(c, "python3 " + cmd, M + 46, y - 52, 864 - 46)
        c.setFillColor(MUTED)
        draw(c, M + 46, y - 80, result, "Sans", 12.5)
        y -= 118


def s14_analyst(c):
    frame(c, 15, "Co dostaje analityk Ewy", "Wydanie")
    para(c, "Jeden folder (zip), jedno polecenie, Python 3.9+ i nic więcej.", M, 420, 860)
    code(c, "python3 ev_shortlist.py --trips trips.csv trips_latest.csv --vans vans_latest.csv --params params.csv --out results/",
         M, 368, 864)
    table(c, [["Plik", "Co zawiera"],
              ["shortlist.csv", "lista w formacie importu Ewy"],
              ["summary.csv", "liczby kontrolne i sumy (= sumy kolumn listy)"],
              ["all_vans.csv", "każdy van z powodem: dlaczego na liście albo nie"],
              ["data_report.txt", "co wyczyszczono; każdy WARNING z datą, vanem, trasą"],
              ["impact.csv", "co weszło, co wypadło i dlaczego (impact.py)"]],
          M, 330, [180, 400])
    bullets(c, [
        "<font name='Mono'>params.csv</font>: jedyne miejsce do edycji.",
        "<font name='Mono'>RERUN.md</font>: kroki, jak czytać powody, co zrobić przy błędzie.",
        "Błąd = jedna linia <font name='Mono'>ERROR</font>, bez śladu stosu.",
        "Zip sprawdzony w pustym katalogu: wynik bajt w bajt jak u nas.",
    ], 660, 330, 250, MID, gap=8)


def s15_close(c):
    frame(c, 16, "Podsumowanie", "Na koniec")
    bullets(c, [
        "<b>Rekomendacja:</b> kupić 7 EV z dotacją (2 × Cargo L, 5 × Cargo S), wszystkie w North; wynik 85 750 PLN w 5 lat.",
        "<b>Kluczowe założenia:</b> najgorszy dzień w 60% WLTP, najcięższy ładunek jako limit, "
        "bez ładowania w dzień, zakup z dotacją, horyzont 5 lat.",
        "<b>Ryzyko:</b> dane z lata i września; P-39 i P-40 ocenione na 12 dniach. Uruchomić narzędzie na eksporcie z IV kwartału przed zakupem.",
        "<b>Proces:</b> dwie zmiany wymagań w ciągu dnia — ok. 20 minut w południe i ok. 10 minut o 15:18 — a analityk uruchamia całość bez nas.",
    ], M, 420, 860, gap=14)
    c.setFillColor(BRAND)
    c.roundRect(M, 88, 180, 50, 12, stroke=0, fill=1)
    c.setFont("Sans-Bold", 22)
    c.setFillColor(colors.white)
    c.drawString(M + 26, 106, "Pytania?")


SLIDES = [s01_title, s02_answer, s03_range, s04_money_assumptions, s05_data_assumptions, s06_winter,
          s07_feasibility, s08_money, s09_sensitivity,
          sA_sdlc, sB_timeline, s12_second_change, sC_tooling, sD_human_ai, sE_lessons,
          s13_demo, s14_analyst, s15_close]


def main():
    assert len(SLIDES) == TOTAL
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Które vany przejdą na prąd? — JellyTech, 30.09.2026")
    c.setAuthor("JellyTech")
    global CURRENT
    for number, slide in enumerate(SLIDES, 1):
        CURRENT = number
        slide(c)
        c.showPage()
    c.save()
    print("Zapisano %s (%d slajdów)" % (OUT, len(SLIDES)))


if __name__ == "__main__":
    main()
