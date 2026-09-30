"""Tor B: wykonalnosc zamiany vana na EV.

Wszystkie progi i dane modeli z params.csv (KONTRAKT sekcja 4).
"""

EPS = 1e-9  # 260 * 0.57 = 148.20000000000002 w float; porownujemy z tolerancja


def ev_models(params):
    """{model: {pole: float}} z kluczy ev.<model>.<pole>, posortowane od najtanszego."""
    models = {}
    for key, value in params.items():
        if key.startswith("ev."):
            model, field = key[3:].rsplit(".", 1)
            models.setdefault(model, {})[field] = float(value)
    return dict(sorted(models.items(), key=lambda m: m[1]["price_pln"]))


def winter_range_km(spec, params):
    return spec["range_wltp_km"] * float(params["winter_range_factor"])


def winter_kwh_per_km(spec, params):
    return (spec["kwh_per_100km"] / 100
            / (float(params["winter_temp_factor"]) * float(params["winter_payload_factor"])))


def _param(params, key, default):
    """Progi B9 — w params.csv; domyslna wartosc do czasu dopisania przez tor A."""
    return float(params.get(key, default))


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


# --- doladowanie miedzy trasami (A16) ----------------------------------------

def van_days(trips, van_id):
    """Dni vana: lista list kursow, kazdy dzien posortowany po start_time."""
    days = {}
    for t in trips:
        if t["van_id"] == van_id:
            days.setdefault(t["date"], []).append(t)
    return [sorted(d, key=lambda t: t["start_time"]) for _, d in sorted(days.items())]


def midday_gain_km(first, second, spec, params):
    """Km odzyskane podczas przerwy miedzy kursami."""
    hours = (_minutes(second["start_time"]) - _minutes(first["end_time"])
             - float(params["midday_connect_minutes"])) / 60
    return max(0.0, hours) * float(params["charger_kw"]) / winter_kwh_per_km(spec, params)


def simulate_day(day, spec, params):
    """(ok, km doladowane w dzien). Rano bateria pelna; w przerwie ladowanie do pelna."""
    full = winter_range_km(spec, params)
    km = [float(t["km"]) for t in day]
    if len(day) == 1:
        return km[0] <= full + EPS, 0.0
    first, second = km[0], sum(km[1:])  # wiecej niz dwa kursy w danych nie wystepuje
    if first > full + EPS:
        return False, 0.0
    refill = min(midday_gain_km(day[0], day[1], spec, params), first)
    return second <= full - first + refill + EPS, refill


def failed_days(days, spec, params):
    """Daty, w ktorych zabrakloby zasiegu mimo doladowania miedzy trasami."""
    return [d[0]["date"] for d in days if not simulate_day(d, spec, params)[0]]


def day_tariff_share(days, spec, params):
    total = sum(float(t["km"]) for d in days for t in d)
    day_km = sum(simulate_day(d, spec, params)[1] for d in days)
    return round(day_km / total, 3) if total else 0


def _longer_route_of_worst_day(days):
    worst = max(days, key=lambda d: sum(float(t["km"]) for t in d))
    return max(float(t["km"]) for t in worst)


# --- ocena ---------------------------------------------------------------------

def model_failures(van, spec, params, days=None):
    """(lista niespelnionych warunkow, czy potrzebne doladowanie miedzy trasami)."""
    fails = []
    if float(van["max_load_kg"]) > spec["payload_kg"] + EPS:
        fails.append("payload")
    midday = False
    if float(van["worst_day_km"]) > winter_range_km(spec, params) + EPS:
        if days and any(len(d) > 1 for d in days) and not failed_days(days, spec, params):
            midday = True
        else:
            fails.append("range")
    return fails, midday


def near_threshold(van, days, spec, params):
    """B9: lista uwag, jak blisko modelu jest van; None, gdy ktorys warunek odpada wyraznie."""
    notes = []
    payload_days = sum(1 for d in days
                       if max(float(t["max_load_kg"]) for t in d) > spec["payload_kg"] + EPS)
    if payload_days:
        if payload_days > _param(params, "near_payload_days", 3):
            return None
        notes.append("payload over on %d days" % payload_days)
    full = winter_range_km(spec, params)
    worst = float(van["worst_day_km"])
    if worst > full + EPS:
        excess = (worst / full - 1) * 100
        failed = len(failed_days(days, spec, params)) if any(len(d) > 1 for d in days) else 0
        if excess <= _param(params, "near_range_pct", 10) + EPS:
            notes.append("range +%.1f%% (%.1f/%.1f km)" % (excess, worst, full))
        elif 0 < failed <= _param(params, "near_payload_days", 3):
            notes.append("range fails %d days with midday charging" % failed)
        else:
            return None
    return notes


def feasible_reason(van, spec, midday, params):
    if midday:
        return "midday charging between routes; 0 failed days"
    full = winter_range_km(spec, params)
    margin = full - float(van["worst_day_km"])
    note = "range margin %.1f km (%.1f%%)" % (margin, margin / full * 100)
    if margin / full * 100 < _param(params, "at_threshold_pct", 1):
        note = "at threshold: " + note
    return note


def assess(profile, trips, params):
    """Tabela feasibility (KONTRAKT 6): jeden wiersz na van z profilu.

    ev_model = najtanszy model, ktory miesci ladunek i kazdy dzien w zasiegu zimowym
    (dla dni z dwiema trasami: z doladowaniem w przerwie, A16).
    Gdy zaden nie pasuje, reject_reason podaje braki najtanszego modelu
    i ewentualnie modele „blisko progu” (B9). Kolumna reason: opis dla wykonalnych.
    """
    models = ev_models(params)
    cheapest = next(iter(models.values()))
    exclude_refr = params.get("exclude_refrigerated", "yes") == "yes"
    rows = []
    for van in profile:
        days = van_days(trips, van["van_id"])
        refrigerated = exclude_refr and van["refrigerated"] == "yes"
        fit, midday = "", False
        for model, spec in models.items():
            fails, needs_midday = model_failures(van, spec, params, days)
            if not fails:
                fit, midday = model, needs_midday
                break
        reasons = []
        if refrigerated:
            reasons.append("refrigerated")
        if not fit:
            reasons += model_failures(van, cheapest, params, days)[0]
        if float(params.get("chargers." + van["depot"], 0)) <= 0:
            reasons.append("no chargers at depot")
        feasible = "no" if reasons else "yes"
        near = [] if refrigerated or fit else [
            "%s %s" % (m, "; ".join(n)) for m, spec in models.items()
            for n in [near_threshold(van, days, spec, params)] if n]
        if near:
            reasons.append("near threshold: " + " | ".join(near))
        rows.append({
            "van_id": van["van_id"],
            "feasible": feasible,
            "ev_model": "" if refrigerated else fit,
            "ev_depot": van["depot"],
            "range_check_km": (_longer_route_of_worst_day(days) if midday
                               else float(van["worst_day_km"])),
            "midday_charging": "yes" if midday else "no",
            "day_tariff_share": day_tariff_share(days, models[fit], params) if midday else 0,
            "reject_reason": "; ".join(reasons),
            "reason": feasible_reason(van, models[fit], midday, params) if fit else "",
        })
    return rows


def sensitivity(profile, trips, params, factors):
    """Dla kazdego progu zimowego: ile vanow przechodzi i ktore.

    feasible_* = pelna ocena jak w assess; fit_* = vany z dobranym ev_model,
    czyli pasujace technicznie niezaleznie od ladowarek w bazie (np. South).
    Zmienia sie tylko winter_range_factor; zuzycie zimowe w symulacji A16 zostaje.
    """
    rows = []
    for factor in factors:
        p = {**params, "winter_range_factor": str(factor)}
        res = assess(profile, trips, p)
        feasible = sorted(r["van_id"] for r in res if r["feasible"] == "yes")
        fit = sorted(r["van_id"] for r in res if r["ev_model"])
        rows.append({
            "winter_range_factor": factor,
            "winter_range_km": "; ".join("%s %.1f" % (m, winter_range_km(s, p))
                                         for m, s in ev_models(p).items()),
            "feasible_count": len(feasible),
            "feasible_vans": " ".join(feasible),
            "fit_count": len(fit),
            "fit_vans": " ".join(fit),
        })
    return rows
