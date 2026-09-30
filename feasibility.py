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


def model_failures(van, spec, params):
    """Lista niespelnionych warunkow ('payload', 'range') dla danego modelu."""
    fails = []
    if float(van["max_load_kg"]) > spec["payload_kg"] + EPS:
        fails.append("payload")
    if float(van["worst_day_km"]) > winter_range_km(spec, params) + EPS:
        fails.append("range")
    return fails


def assess(profile, trips, params):
    """Tabela feasibility (KONTRAKT 6): jeden wiersz na van z profilu.

    ev_model = najtanszy model, ktory miesci ladunek i najgorszy dzien w zasiegu zimowym.
    Gdy zaden nie pasuje, reject_reason podaje braki najtanszego modelu.
    """
    models = ev_models(params)
    cheapest = next(iter(models.values()))
    exclude_refr = params.get("exclude_refrigerated", "yes") == "yes"
    rows = []
    for van in profile:
        refrigerated = exclude_refr and van["refrigerated"] == "yes"
        fit = next((m for m, spec in models.items() if not model_failures(van, spec, params)), "")
        reasons = []
        if refrigerated:
            reasons.append("refrigerated")
        if not fit:
            reasons += model_failures(van, cheapest, params)
        if float(params.get("chargers." + van["depot"], 0)) <= 0:
            reasons.append("no chargers at depot")
        rows.append({
            "van_id": van["van_id"],
            "feasible": "no" if reasons else "yes",
            "ev_model": "" if refrigerated else fit,
            "ev_depot": van["depot"],
            "range_check_km": float(van["worst_day_km"]),
            "midday_charging": "no",
            "day_tariff_share": 0,
            "reject_reason": "; ".join(reasons),
        })
    return rows
