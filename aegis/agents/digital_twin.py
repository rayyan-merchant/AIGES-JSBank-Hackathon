import os
import numpy as np
import pandas as pd

class DigitalTwinAgent:
    def __init__(self, use_torch=True):
        self.use_torch = use_torch
        self.torch = None
        if use_torch:
            try:
                import torch
                import torch.nn as nn
                self.torch = torch
                class LSTMModel(nn.Module):
                    def __init__(self, input_size=1, hidden_size=16, num_layers=1):
                        super().__init__()
                        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                        self.fc = nn.Linear(hidden_size, 1)
                    def forward(self, x):
                        out, _ = self.lstm(x)
                        out = self.fc(out[:, -1, :])
                        return out
                self.Model = LSTMModel
            except Exception:
                self.use_torch = False

    def load_transactions(self, csv_path):
        df = pd.read_csv(csv_path)
        if "date" in df.columns and "amount" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df["month"] = df["date"].dt.to_period("M")
            series = df.groupby("month")["amount"].sum().astype(float).values
        else:
            series = df.iloc[:, -1].astype(float).values
        return series

    def forecast(self, series, months=12):
        if self.use_torch and self.torch is not None:
            torch = self.torch
            nn = torch.nn
            model = self.Model()
            model.eval()
            arr = torch.tensor(series, dtype=torch.float32).view(1, -1, 1)
            preds = []
            last = arr
            for _ in range(months):
                y = model(last)
                preds.append(float(y.detach().numpy()))
                last = torch.cat([last[:, 1:, :], y.view(1, 1, 1)], dim=1)
            return np.array(preds)
        ma = np.convolve(series, np.ones(3) / 3, mode="valid")
        last = float(ma[-1]) if len(ma) else float(series[-1]) if len(series) else 0.0
        base = np.array([last * (0.98 + 0.04 * np.random.rand()) for _ in range(months)])
        w = np.linspace(0.6, 1.0, num=min(len(series), 6))
        tail = np.array(series[-len(w):]) if len(series) >= len(w) else np.array(series)
        att = (tail * w[:len(tail)]) if len(tail) else np.array([last])
        bias = float(np.mean(att)) if len(att) else last
        return np.clip(base * (0.9 + 0.2 * np.random.rand()), 0.0, None) + (0.05 * bias)

    def default_probability(self, income, debt, emi, forecast):
        ratio = emi / max(income, 1e-6)
        cf = float(np.mean(forecast))
        stress = max(0.0, (emi - max(cf, 1e-6)) / max(income, 1e-6))
        p = 1.0 / (1.0 + np.exp(-3.0 * (ratio + 0.5 * stress - 0.6)))
        return float(np.clip(p, 0.0, 1.0)), float(stress)

    def _risk_trajectory(self, income, emi, forecast):
        traj = []
        for v in forecast:
            cf = float(v)
            ratio = emi / max(income, 1e-6)
            stress = max(0.0, (emi - max(cf, 1e-6)) / max(income, 1e-6))
            p = 1.0 / (1.0 + np.exp(-3.0 * (ratio + 0.5 * stress - 0.6)))
            traj.append(float(np.clip(p, 0.0, 1.0)))
        return traj

    def _behavioral_drift(self, series):
        if len(series) < 4:
            return {"drift_score": 0.0, "volatility_shift": 0.0}
        mid = len(series) // 2
        first = np.array(series[:mid], dtype=float)
        second = np.array(series[mid:], dtype=float)
        mean_diff = float(abs(second.mean() - first.mean()) / (abs(first.mean()) + 1e-6))
        vol_shift = float(abs(np.std(second) - np.std(first)) / (np.std(first) + 1e-6))
        return {"drift_score": float(np.clip(mean_diff, 0.0, 1.0)), "volatility_shift": float(np.clip(vol_shift, 0.0, 1.0))}

    def build(self, csv_path, income, debt, emi, documents=None, credit_utilization=None):
        series = self.load_transactions(csv_path)
        forecast = self.forecast(series)
        p_default, liquidity_stress = self.default_probability(income, debt, emi, forecast)
        traj = self._risk_trajectory(income, emi, forecast)
        drift = self._behavioral_drift(series.tolist() if hasattr(series, "tolist") else list(series))
        cu_adj = float(np.clip((credit_utilization or 0.3) - 0.3, -0.3, 0.7))
        p_default = float(np.clip(p_default + 0.2 * cu_adj, 0.0, 1.0))
        return {
            "cashflow_forecast": forecast.tolist(),
            "default_probability": p_default,
            "liquidity_stress_score": liquidity_stress,
            "risk_trajectory_curve": traj,
            "behavioral_drift_metrics": drift,
            "survival_curve": [float(1.0 - p) for p in traj],
            "reasoning": "cashflow and affordability estimated",
        }
