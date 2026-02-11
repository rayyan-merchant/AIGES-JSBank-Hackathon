import numpy as np

def apply_shocks(income_series, params):
    income_shock = params.get("income_shock_pct", 0.0)
    rate_hike = params.get("rate_hike_pct", 0.0)
    inflation = params.get("inflation_pct", 0.0)
    contraction = params.get("market_contraction_pct", 0.0)
    s_income = income_series * (1.0 - income_shock)
    macro_factor = (1.0 + inflation) * (1.0 - contraction)
    s_income = s_income * max(0.1, macro_factor)
    rate_multiplier = 1.0 + rate_hike
    return s_income, rate_multiplier
