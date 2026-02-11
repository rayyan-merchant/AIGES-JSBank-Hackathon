import numpy as np

def predict_default(emi_ratio, cashflow_mean):
    s = max(0.0, (emi_ratio - cashflow_mean / max(cashflow_mean, 1e-6)))
    p = 1.0 / (1.0 + np.exp(-3.0 * (emi_ratio + 0.5 * s - 0.6)))
    return float(np.clip(p, 0.0, 1.0))
