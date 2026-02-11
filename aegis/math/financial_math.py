import math

def apr(nominal_rate, compounding_per_year):
    r = float(nominal_rate)
    m = int(compounding_per_year) if compounding_per_year else 1
    return (1 + r / m) ** m - 1

def emi(principal, annual_rate, months):
    P = float(principal)
    r = float(annual_rate) / 12.0
    n = int(months)
    if n <= 0:
        return 0.0
    if r == 0:
        return P / n
    f = (1 + r) ** n
    return P * r * f / (f - 1)

def npv(cashflows, discount_rate):
    r = float(discount_rate)
    total = 0.0
    for i, cf in enumerate(cashflows):
        total += cf / ((1 + r) ** i)
    return total

def irr(cashflows, guess=0.1, max_iter=32, tol=1e-6):
    def f(rate):
        return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))
    lo, hi = -0.99, 10.0
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        val = f(mid)
        if abs(val) < tol:
            return mid
        if val > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
