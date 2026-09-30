"""Track C: annual km and savings per van. All numbers come from params.csv."""

import calendar
import datetime


def _f(value):
    return float(value) if value not in ("", None) else 0.0


def _param(params, key):
    if key not in params:
        raise ValueError("Missing parameter '%s' in params.csv" % key)
    return _f(params[key])


def _date(value, what):
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        raise ValueError("%s '%s' is not a date in YYYY-MM-DD format" % (what, value)) from None


def _add_months(day, months):
    month = day.month - 1 + months
    year, month = day.year + month // 12, month % 12 + 1
    return datetime.date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def _electricity_price(params, day_share):
    night = _param(params, "electricity_night_pln_per_kwh")
    day = _param(params, "electricity_day_pln_per_kwh")
    return (1 - day_share) * night + day_share * day


def lease_exit_fee(van, params):
    """Return the fee for ending the van's diesel lease early (0 if owned or the lease ends soon)."""
    if van.get("ownership") != "leased":
        return 0
    if "lease_reference_date" not in params:
        raise ValueError("Missing parameter 'lease_reference_date' in params.csv")
    reference = _date(params["lease_reference_date"], "Parameter 'lease_reference_date' in params.csv")
    free_until = _add_months(reference, int(_param(params, "lease_free_exit_within_months")))
    lease_end = _date(van.get("lease_end", ""), "Van %s: lease_end" % van.get("van_id", "?"))
    if lease_end <= free_until:
        return 0
    return _param(params, "lease_exit_fee_months") * _f(van.get("monthly_lease_pln"))


def saving_for_model(van, ev_model, day_tariff_share, params, period_days):
    """Return annual_km, annual_fuel_saving_pln and saving_pln for one van replaced by ev_model."""
    annual_km = _f(van["km_period"]) * _param(params, "days_per_year") / (_f(van.get("scale_days") or 0) or period_days)
    diesel_cost = (annual_km * _param(params, "fuel_l_per_100km." + van["model"]) / 100
                   * _param(params, "diesel_price_pln_per_l"))
    kwh = (annual_km * _param(params, "ev." + ev_model + ".kwh_per_100km") / 100
           * _param(params, "winter_energy_uplift"))
    fuel_saving = diesel_cost - kwh * _electricity_price(params, _f(day_tariff_share))
    maintenance_saving = annual_km * (_param(params, "maintenance_diesel_pln_per_km")
                                      - _param(params, "maintenance_ev_pln_per_km"))
    ev_cost = _param(params, "ev." + ev_model + ".price_pln") * (1 - _param(params, "grant_share_of_price"))
    saving = (_param(params, "saving_horizon_years") * (fuel_saving + maintenance_saving)
              - ev_cost - lease_exit_fee(van, params))
    return {"annual_km": annual_km, "annual_fuel_saving_pln": fuel_saving, "saving_pln": saving}


def economics(profile, feasibility, params, period_days):
    """One row per van in `profile`: van_id, annual_km, annual_fuel_saving_pln, saving_pln.

    Savings are blank ("") for vans without an ev_model in `feasibility`.
    saving_pln follows the board's five-year rule: see saving_basis().
    """
    feas = {r["van_id"]: r for r in feasibility}
    rows = []
    for van in profile:
        row = {
            "van_id": van["van_id"],
            "annual_km": (_f(van["km_period"]) * _param(params, "days_per_year")
                          / (_f(van.get("scale_days") or 0) or period_days)),
            "annual_fuel_saving_pln": "",
            "saving_pln": "",
        }
        f = feas.get(van["van_id"], {})
        if f.get("ev_model"):
            row.update(saving_for_model(van, f["ev_model"], f.get("day_tariff_share"), params, period_days))
        rows.append(row)
    return rows


def saving_basis(params):
    """One sentence for summary.csv describing what saving_pln counts."""
    years = int(_param(params, "saving_horizon_years"))
    grant = round(_param(params, "grant_share_of_price") * 100)
    fee_months = int(_param(params, "lease_exit_fee_months"))
    free_months = int(_param(params, "lease_free_exit_within_months"))
    return (
        "Saving over %d years per van: diesel fuel minus EV charging plus diesel minus EV maintenance"
        " at current prices minus the EV purchase price after the %d%% grant minus a lease exit fee"
        " of %d monthly payments if the diesel lease runs more than %d months;"
        " diesel lease payments and resale values are not included." % (years, grant, fee_months, free_months)
    )
