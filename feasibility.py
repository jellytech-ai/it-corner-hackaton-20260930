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

# max_south_vans_at_north: vans from this depot may be based at the other one (Ewa, 30.09)
MOVE_FROM, MOVE_TO = "South", "North"


def midday_allowed(params):
    """Return True when two-route vans may charge at the depot between routes."""
    value = params.get("midday_charging_allowed", "")
    if value not in ("yes", "no"):
        raise ValueError("Missing parameter 'midday_charging_allowed' in params.csv")
    return value == "yes"


def model_failures(van, spec, params, days=None):
    """Return (failed checks among 'payload' and 'range', whether midday charging is needed)."""
    fails = []
    if float(van["max_load_kg"]) > spec["payload_kg"] + EPS:
        fails.append("payload")
    midday = False
    if float(van["range_day_km"]) > winter_range_km(spec, params) + EPS:
        if (midday_allowed(params) and days and any(len(d) > 1 for d in days)
                and not failed_days(days, spec, params)):
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
    check = float(van["range_day_km"])
    if check > full + EPS:
        excess = (check / full - 1) * 100
        two_route = midday_allowed(params) and any(len(d) > 1 for d in days)
        failed = len(failed_days(days, spec, params)) if two_route else 0
        if excess <= param(params, "near_miss_range_pct") + EPS:
            notes.append("range +%.1f%% (%.1f/%.1f km)" % (excess, check, full))
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
    margin = full - float(van["range_day_km"])
    note = "range margin %.1f km (%.1f%%)" % (margin, margin / full * 100)
    if margin / full * 100 < param(params, "at_threshold_pct"):
        note = "at threshold: " + note
    return note


def _ev_depot(van, params):
    """Return (depot where the EV would be based, note) or (own depot, '') when it has no chargers."""
    depot = van["depot"]
    if param(params, "chargers." + depot) > 0:
        return depot, ""
    if (depot == MOVE_FROM and param(params, "max_south_vans_at_north") > 0
            and param(params, "chargers." + MOVE_TO) > 0):
        return MOVE_TO, "%s van based at %s, routes unchanged" % (MOVE_FROM, MOVE_TO)
    return depot, ""


def fitting_models(van, days, params):
    """Return [(model, needs midday charging)] for every model that carries the load and covers the range."""
    if not days:
        return []
    out = []
    for model, spec in ev_models(params).items():
        fails, midday = model_failures(van, spec, params, days)
        if not fails:
            out.append((model, midday))
    return out


def assess_van(van, trips, params, model=None):
    """Return the feasibility row for one van, for the given fitting model or the cheapest one."""
    models = ev_models(params)
    cheapest = next(iter(models.values()))
    if params.get("exclude_refrigerated", "") not in ("yes", "no"):
        raise ValueError("Missing parameter 'exclude_refrigerated' in params.csv")
    days = van_days(trips, van["van_id"])
    refrigerated = params["exclude_refrigerated"] == "yes" and van["refrigerated"] == "yes"
    fits = fitting_models(van, days, params)
    chosen = [f for f in fits if f[0] == model] or fits[:1]
    fit, midday = chosen[0] if chosen else ("", False)
    ev_depot, depot_note = _ev_depot(van, params)

    reasons = []
    if not days:
        reasons.append("no trips in this export")
    if refrigerated:
        reasons.append("refrigerated")
    if days and not fit:
        reasons += model_failures(van, cheapest, params, days)[0]
    if param(params, "chargers." + ev_depot) <= 0:
        reasons.append("no chargers at depot")
    feasible = "no" if reasons else "yes"
    near = [] if refrigerated or fit or not days else [
        "%s %s" % (m, "; ".join(n)) for m, spec in models.items()
        for n in [near_miss(van, days, spec, params)] if n]
    if near:
        reasons.append("near miss: " + " | ".join(near))
    reason = ""
    if fit:
        reason = "; ".join(x for x in (feasible_reason(van, models[fit], midday, params),
                                       depot_note) if x)
    return {
        "van_id": van["van_id"],
        "feasible": feasible,
        "ev_model": "" if refrigerated else fit,
        "ev_depot": ev_depot,
        "range_check_km": (_longer_route_of_worst_day(days) if midday
                           else float(van["range_day_km"])),
        "midday_charging": "yes" if midday else "no",
        "day_tariff_share": day_tariff_share(days, models[fit], params) if midday else 0,
        "reject_reason": "; ".join(reasons),
        "reason": reason,
        "fit_models": "" if refrigerated else "; ".join(m for m, _ in fits),
    }


def assess(profile, trips, params):
    """Return the feasibility table: one row per van in the profile.

    A model fits when it carries the heaviest load the van carried and the van's
    range_day_km (95th-percentile day) fits in its winter range; with midday charging
    allowed, two-route days may top up between routes (A16). ev_model is the cheapest
    fitting model here; the entry point replaces it with the one that saves more (Ewa).
    When no model fits, reject_reason lists what the cheapest model fails, plus near misses.
    """
    return [assess_van(van, trips, params) for van in profile]


def sensitivity(profile, trips, params, factors):
    """Return, for each winter range factor, how many vans pass and which.

    feasible_* is the full assessment; fit_* are vans with an ev_model, i.e. a model fits
    whatever the charging points at the depot. Only winter_range_factor changes; the
    shortlist limits (charging points, grant, South vans at North) are not applied here.
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
