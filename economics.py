"""Track C: annual km and savings per van. All numbers come from params.csv."""


def _f(value):
    return float(value) if value not in ("", None) else 0.0


def _electricity_price(params, day_share):
    night = _f(params["electricity_night_pln_per_kwh"])
    day = _f(params["electricity_day_pln_per_kwh"])
    return (1 - day_share) * night + day_share * day


def economics(profile, feasibility, params, period_days):
    """One row per van in `profile`: van_id, annual_km, annual_fuel_saving_pln, saving_pln.

    Savings are blank ("") for vans without an ev_model in `feasibility`.
    saving_pln follows decision D7 (variant 1): see saving_basis().
    """
    feas = {r["van_id"]: r for r in feasibility}
    days_per_year = _f(params["days_per_year"])
    diesel_price = _f(params["diesel_price_pln_per_l"])
    winter_uplift = _f(params["winter_energy_uplift"])
    maintenance_saving_per_km = _f(params["maintenance_diesel_pln_per_km"]) - _f(params["maintenance_ev_pln_per_km"])

    rows = []
    for van in profile:
        annual_km = _f(van["km_period"]) * days_per_year / period_days
        row = {
            "van_id": van["van_id"],
            "annual_km": annual_km,
            "annual_fuel_saving_pln": "",
            "saving_pln": "",
        }
        f = feas.get(van["van_id"], {})
        ev_model = f.get("ev_model", "")
        if ev_model:
            diesel_cost = annual_km * _f(params["fuel_l_per_100km." + van["model"]]) / 100 * diesel_price
            kwh = annual_km * _f(params["ev." + ev_model + ".kwh_per_100km"]) / 100 * winter_uplift
            charging_cost = kwh * _electricity_price(params, _f(f.get("day_tariff_share")))
            row["annual_fuel_saving_pln"] = diesel_cost - charging_cost
            row["saving_pln"] = row["annual_fuel_saving_pln"] + annual_km * maintenance_saving_per_km
        rows.append(row)
    return rows


def saving_basis(params):
    """One sentence for summary.csv describing what saving_pln counts."""
    return (
        "Operating saving per van per year: diesel fuel minus EV charging plus diesel minus EV maintenance"
        " at current prices; EV lease or purchase cost and the grant are not included."
    )
