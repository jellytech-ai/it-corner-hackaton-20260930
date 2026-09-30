"""Track B: can a van be replaced by an EV, and by which model.

Every threshold and every EV model figure comes from params.csv.
"""

EPS = 1e-9  # 260 * 0.57 = 148.20000000000002 in float; compare with a tolerance


def param(params, key):
    """Return a numeric parameter, or raise ValueError when params.csv does not have it."""
    if params.get(key, "") == "":
        raise ValueError("Missing parameter '%s' in params.csv" % key)
    return float(params[key])


def ev_models(params):
    """Return {model: {field: float}} from the ev.<model>.<field> keys, cheapest model first."""
    models = {}
    for key, value in params.items():
        if key.startswith("ev."):
            model, field = key[3:].rsplit(".", 1)
            models.setdefault(model, {})[field] = float(value)
    if not models:
        raise ValueError("Missing parameter 'ev.<model>.range_wltp_km' in params.csv")
    for model, spec in models.items():
        for field in ("range_wltp_km", "payload_kg", "kwh_per_100km", "price_pln"):
            if field not in spec:
                raise ValueError("Missing parameter 'ev.%s.%s' in params.csv" % (model, field))
    return dict(sorted(models.items(), key=lambda m: m[1]["price_pln"]))


def winter_range_km(spec, params):
    """Return the winter range of a model: WLTP range x winter_range_factor."""
    return spec["range_wltp_km"] * param(params, "winter_range_factor")


def winter_kwh_per_km(spec, params):
    """Return winter consumption in kWh per km."""
    return (spec["kwh_per_100km"] / 100
            / (param(params, "winter_temp_factor") * param(params, "winter_payload_factor")))


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


# --- midday charging between routes (A16) -------------------------------------

def van_days(trips, van_id):
    """Return the van's days as lists of trips, each day sorted by start_time."""
    days = {}
    for t in trips:
        if t["van_id"] == van_id:
            days.setdefault(t["date"], []).append(t)
    return [sorted(d, key=lambda t: t["start_time"]) for _, d in sorted(days.items())]


def midday_gain_km(first, second, spec, params):
    """Return the km of range recovered while charging between two routes."""
    hours = (_minutes(second["start_time"]) - _minutes(first["end_time"])
             - param(params, "midday_connect_minutes")) / 60
    return max(0.0, hours) * param(params, "charger_kw") / winter_kwh_per_km(spec, params)


def simulate_day(day, spec, params):
    """Return (ok, km charged during the day); battery full in the morning, topped up between routes."""
    full = winter_range_km(spec, params)
    km = [float(t["km"]) for t in day]
    if len(day) == 1:
        return km[0] <= full + EPS, 0.0
    first, second = km[0], sum(km[1:])  # the data never has more than two routes a day
    if first > full + EPS:
        return False, 0.0
    refill = min(midday_gain_km(day[0], day[1], spec, params), first)
    return second <= full - first + refill + EPS, refill


def failed_days(days, spec, params):
    """Return the dates on which the model would run out of range even with midday charging."""
    return [d[0]["date"] for d in days if not simulate_day(d, spec, params)[0]]


def day_tariff_share(days, spec, params):
    """Return the share of energy charged at the day tariff."""
    total = sum(float(t["km"]) for d in days for t in d)
    day_km = sum(simulate_day(d, spec, params)[1] for d in days)
    return round(day_km / total, 3) if total else 0


def _longer_route_of_worst_day(days):
    worst = max(days, key=lambda d: sum(float(t["km"]) for t in d))
    return max(float(t["km"]) for t in worst)


# --- assessment ------------------------------------------------------------------

def model_failures(van, spec, params, days=None):
    """Return (failed checks among 'payload' and 'range', whether midday charging is needed)."""
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


def near_miss(van, days, spec, params):
    """Return notes on how close the van is to fitting the model, or None when it is clearly out."""
    max_days = param(params, "near_miss_days")
    notes = []
    payload_days = sum(1 for d in days
                       if max(float(t["max_load_kg"]) for t in d) > spec["payload_kg"] + EPS)
    if payload_days:
        if payload_days > max_days:
            return None
        notes.append("payload over on %d days" % payload_days)
    full = winter_range_km(spec, params)
    worst = float(van["worst_day_km"])
    if worst > full + EPS:
        excess = (worst / full - 1) * 100
        failed = len(failed_days(days, spec, params)) if any(len(d) > 1 for d in days) else 0
        if excess <= param(params, "near_miss_range_pct") + EPS:
            notes.append("range +%.1f%% (%.1f/%.1f km)" % (excess, worst, full))
        elif 0 < failed <= max_days:
            notes.append("range fails %d days with midday charging" % failed)
        else:
            return None
    return notes


def feasible_reason(van, spec, midday, params):
    """Return the reason text for a feasible van: range margin, at threshold, or midday charging."""
    if midday:
        return "midday charging between routes; 0 failed days"
    full = winter_range_km(spec, params)
    margin = full - float(van["worst_day_km"])
    note = "range margin %.1f km (%.1f%%)" % (margin, margin / full * 100)
    if margin / full * 100 < param(params, "at_threshold_pct"):
        note = "at threshold: " + note
    return note


def assess(profile, trips, params):
    """Return the feasibility table: one row per van in the profile.

    ev_model is the cheapest model that carries the van's max load and covers every day
    in winter range (with midday charging on two-route days, A16). When no model fits,
    reject_reason lists what the cheapest model fails, plus any near misses.
    """
    models = ev_models(params)
    cheapest = next(iter(models.values()))
    if params.get("exclude_refrigerated", "") not in ("yes", "no"):
        raise ValueError("Missing parameter 'exclude_refrigerated' in params.csv")
    exclude_refr = params["exclude_refrigerated"] == "yes"
    rows = []
    for van in profile:
        days = van_days(trips, van["van_id"])
        refrigerated = exclude_refr and van["refrigerated"] == "yes"
        fit, midday = "", False
        if days:
            for model, spec in models.items():
                fails, needs_midday = model_failures(van, spec, params, days)
                if not fails:
                    fit, midday = model, needs_midday
                    break
        reasons = []
        if not days:
            reasons.append("no trips in this export")
        if refrigerated:
            reasons.append("refrigerated")
        if days and not fit:
            reasons += model_failures(van, cheapest, params, days)[0]
        if param(params, "chargers." + van["depot"]) <= 0:
            reasons.append("no chargers at depot")
        feasible = "no" if reasons else "yes"
        near = [] if refrigerated or fit or not days else [
            "%s %s" % (m, "; ".join(n)) for m, spec in models.items()
            for n in [near_miss(van, days, spec, params)] if n]
        if near:
            reasons.append("near miss: " + " | ".join(near))
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
    """Return, for each winter range factor, how many vans pass and which.

    feasible_* is the full assessment; fit_* are vans with an ev_model, i.e. a model fits
    whatever the charging points at the depot (e.g. South). Only winter_range_factor
    changes; the winter consumption used for midday charging stays as in params.csv.
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
