import pandas as pd
import numpy as np

def generate_static_sme(n_smes: int, random_state: int = 42) -> pd.DataFrame:
    
    rng = np.random.default_rng(random_state)
    
    industries = ['Retail', 'Manufacturing', 'Tech', 'Services', 'Agriculture']
    probs = [0.3, 0.2, 0.15, 0.25, 0.1]
    
    industry_col = rng.choice(industries, size=n_smes, p=probs)
    
    ages = rng.gamma(shape=2.0, scale=3.0, size=n_smes)
    ages = np.clip(ages, 0.5, 30)
    
    lambdas = {
        'Retail': 10,
        'Manufacturing': 50,
        'Tech': 15,
        'Services': 8,
        'Agriculture': 5
    }
    
    employees = np.array([rng.poisson(lambdas[ind]) for ind in industry_col])
    employees = np.maximum(employees, 1)
    
    base_revenue = rng.lognormal(mean=11.9, sigma=0.8, size=n_smes)
    
    debt_ratio = rng.beta(a=2, b=5, size=n_smes)
    
    loan_amount = base_revenue * 12 * debt_ratio
    
    risk_map = {
        'Retail': 0.02,
        'Manufacturing': 0.03,
        'Tech': 0.04,
        'Services': 0.01,
        'Agriculture': 0.03
    }
    industry_risk = np.array([risk_map[ind] for ind in industry_col])
    
    base_rate = 0.05
    interest_rate = base_rate + (0.1 * debt_ratio) + industry_risk
    
    duration = rng.integers(12, 49, size=n_smes)
    
    df = pd.DataFrame({
        'SME_ID': np.arange(n_smes),
        'industry': industry_col,
        'business_age': ages,
        'employee_count': employees,
        'base_revenue': base_revenue,
        'debt_ratio': debt_ratio,
        'loan_amount': loan_amount,
        'interest_rate': interest_rate,
        'duration': duration
    })
    
    return df

def generate_monthly_financials(static_df: pd.DataFrame, months: int = 36) -> pd.DataFrame:
    
    records = []
    rng = np.random.default_rng(42)
    
    n_smes = len(static_df)
    
    
    macro_process = np.zeros(months)
    z = 0
    for t in range(months):
        z = 0.7 * z + rng.normal(0, 0.1)
        macro_process[t] = z
        
    macro_effect = 1 + 0.2 * macro_process
    
    for idx, row in static_df.iterrows():
        sme_id = row['SME_ID']
        base_rev = row['base_revenue']
        loan_amt = row['loan_amount']
        int_rate = row['interest_rate']
        dur = row['duration']
        
        phase = rng.uniform(0, 2*np.pi)
        
        cash = base_rev * 0.5
        
        r_m = int_rate / 12
        if r_m > 0:
            emi = (loan_amt * r_m * (1+r_m)**dur) / ((1+r_m)**dur - 1)
        else:
            emi = loan_amt / dur
            
        for t in range(months):
            season = 1 + 0.3 * np.sin(2 * np.pi * t / 12 + phase)
            
            noise = rng.lognormal(0, 0.1)
            
            revenue = base_rev * season * macro_effect[t] * noise
            
            fixed_cost = 0.3 * base_rev
            variable_cost = 0.5 * revenue
            
            ebitda = revenue - fixed_cost - variable_cost
            
            payment = emi if t < dur else 0
            
            cash = cash + ebitda - payment
            
            records.append({
                'SME_ID': sme_id,
                'month': t + 1,
                'revenue': revenue,
                'EBITDA': ebitda,
                'cash': cash,
                'debt_payment': payment,
                'macro_state': macro_effect[t]
            })
            
    return pd.DataFrame(records)

def compute_default(static_df: pd.DataFrame, monthly_df: pd.DataFrame) -> pd.DataFrame:
    
    merged = monthly_df.merge(static_df[['SME_ID', 'debt_ratio']], on='SME_ID', how='left')
    
    merged.sort_values(['SME_ID', 'month'], inplace=True)
    
    merged['prev_rev'] = merged.groupby('SME_ID')['revenue'].shift(6)
    merged['trend'] = (merged['revenue'] - merged['prev_rev']) / merged['prev_rev']
    merged['trend'] = merged['trend'].fillna(0)
    
    merged['volatility'] = merged.groupby('SME_ID')['revenue'].transform(lambda x: x.rolling(12, min_periods=3).std())
    merged['rev_mean'] = merged.groupby('SME_ID')['revenue'].transform(lambda x: x.rolling(12, min_periods=3).mean())
    merged['volatility_ratio'] = (merged['volatility'] / merged['rev_mean']).fillna(0.2)
    
    merged['cash_ratio'] = merged['cash'] / merged['revenue']
    merged['cash_ratio'] = merged['cash_ratio'].clip(-10, 10).fillna(0)
    
    
    w1 = 3.0
    w2 = 2.0
    w3 = 1.0
    w4 = 1.0
    w5 = 2.0
    w0 = -4.0
    
    macro_stress = 1 - merged['macro_state']
    
    logit = (
        w0 
        + w1 * merged['debt_ratio']
        + w2 * merged['volatility_ratio']
        - w3 * merged['cash_ratio']
        - w4 * merged['trend']
        + w5 * macro_stress
    )
    
    merged['PD'] = 1 / (1 + np.exp(-logit))
    
    rng = np.random.default_rng(42)
    random_vals = rng.random(len(merged))
    merged['default_flag'] = (random_vals < merged['PD']).astype(int)
    
    
    mask = merged['default_flag'] == 1
    merged.loc[mask, 'revenue'] *= 0.5
    merged.loc[mask, 'cash'] = -1000.0
    
    return merged

if __name__ == "__main__":
    print("Testing SME Generator...")
    static = generate_static_sme(100)
    monthly = generate_monthly_financials(static, 24)
    final = compute_default(static, monthly)
    
    print(f"Static: {static.shape}")
    print(f"Monthly: {monthly.shape}")
    print("Default Rate:", final['default_flag'].mean())
    print("Passed.")
