import numpy as np
import pandas as pd
import os

np.random.seed(42)

OUTPUT_DIR = os.path.join(os.getcwd(), 'data', 'processed')
N_SMES = 1000
T_MONTHS = 36

INDUSTRIES = ['Retail', 'Manufacturing', 'Services', 'Tech', 'Agriculture']
INDUSTRY_PROBS = [0.30, 0.20, 0.25, 0.15, 0.10]
INDUSTRY_CONFIG = {
    'Retail': {'lambda': 12, 'alpha_range': (0.15, 0.25), 'volatility': 0.2},
    'Manufacturing': {'lambda': 25, 'alpha_range': (0.05, 0.15), 'volatility': 0.15},
    'Services': {'lambda': 6, 'alpha_range': (0.05, 0.15), 'volatility': 0.15},
    'Tech': {'lambda': 8, 'alpha_range': (0.05, 0.15), 'volatility': 0.3},
    'Agriculture': {'lambda': 4, 'alpha_range': (0.2, 0.3), 'volatility': 0.25},
}

def generate_static_sme(n=N_SMES):
    
    print(f"Generating {n} static SMEs...")
    
    ids = np.arange(n)
    
    industries = np.random.choice(INDUSTRIES, size=n, p=INDUSTRY_PROBS)
    
    ages = np.random.gamma(shape=2, scale=3, size=n)
    ages = np.clip(ages, 1, 25)
    
    employees = []
    for ind in industries:
        lam = INDUSTRY_CONFIG[ind]['lambda']
        employees.append(np.random.poisson(lam))
    employees = np.array(employees)
    
    base_revenues = np.random.lognormal(mean=12, sigma=1.0, size=n)
    
    loans = np.random.lognormal(mean=10, sigma=0.5, size=n)
    
    durations = np.random.uniform(12, 48, size=n).astype(int)
    
    df = pd.DataFrame({
        'SME_ID': ids,
        'Industry': industries,
        'Age_Years': ages,
        'Employees': employees,
        'Base_Revenue': base_revenues,
        'Loan_Amount': loans,
        'Loan_Duration_Months': durations
    })
    
    
    df['Debt_Ratio'] = df['Loan_Amount'] / df['Base_Revenue']
    
    risk_map = {'Retail': 1.0, 'Manufacturing': 1.5, 'Services': 0.8, 'Tech': 2.0, 'Agriculture': 1.8}
    df['Industry_Risk'] = df['Industry'].map(risk_map)
    
    r_base = 0.08
    
    df['Interest_Rate_Annual'] = r_base + 0.02 * df['Debt_Ratio'] + 0.01 * df['Industry_Risk']
    df['Interest_Rate_Annual'] = np.clip(df['Interest_Rate_Annual'], 0.05, 0.35)
    
    return df

def generate_monthly_financials(static_df, months=T_MONTHS):
    
    print(f"Simulating {months} months for {len(static_df)} SMEs...")
    
    records = []
    
    Z = np.zeros(months)
    eta = np.random.normal(0, 0.05, months)
    for t in range(1, months):
        Z[t] = 0.7 * Z[t-1] + eta[t]
    
    beta = 1.0
    M_t = 1 + 0.5 * Z
    
    for _, row in static_df.iterrows():
        sme_id = row['SME_ID']
        base_rev = row['Base_Revenue']
        ind = row['Industry']
        volatility = INDUSTRY_CONFIG[ind]['volatility']
        
        alpha = np.random.uniform(*INDUSTRY_CONFIG[ind]['alpha_range'])
        
        cash = base_rev * 0.2
        
        theta = np.random.uniform(0.4, 0.7)
        
        fixed_cost = base_rev * np.random.uniform(0.15, 0.35)
        
        loan_amt = row['Loan_Amount']
        duration = row['Loan_Duration_Months']
        annual_rate = row['Interest_Rate_Annual']
        monthly_rate = annual_rate / 12
        
        if monthly_rate > 0:
            emi = (loan_amt * monthly_rate * (1 + monthly_rate)**duration) / ((1+monthly_rate)**duration - 1)
        else:
            emi = loan_amt / duration
            
        revenue_history = []
        
        for t in range(months):
            S_t = 1 + alpha * np.sin(2 * np.pi * t / 12)
            
            epsilon = np.random.lognormal(0, volatility)
            
            revenue = base_rev * S_t * M_t[t] * epsilon
            revenue_history.append(revenue)
            
            var_cost = revenue * theta
            ebitda = revenue - fixed_cost - var_cost
            
            payment = emi if t < duration else 0.0
            
            shock = np.random.normal(0, 0.05 * revenue)
            
            cash_prev = cash
            cash = cash_prev + ebitda - payment + shock
            
            trend = 0.0
            if t >= 6:
                prev_rev = revenue_history[t-6]
                if prev_rev > 0:
                    trend = (revenue - prev_rev) / prev_rev
            
            curr_vol = np.std(revenue_history) if len(revenue_history) > 1 else 0.0
            
            
            debt_ratio_dynamic = loan_amt / revenue if revenue > 0 else 10.0
            
            
            logit = (
                -6.0
                + 3.0 * row['Debt_Ratio'] 
                + 3.0 * curr_vol / base_rev 
                - 2.0 * (cash / revenue if revenue > 1 else 0)
                - 2.0 * trend
                + 2.0 * (1 - M_t[t]) 
            )
            pd_val = 1 / (1 + np.exp(-logit))
            
            default_event = np.random.binomial(1, pd_val)
            
            records.append({
                'SME_ID': sme_id,
                'Month': t + 1,
                'Revenue': revenue,
                'EBITDA': ebitda,
                'Cash': cash,
                'Debt_Payment': payment,
                'Macro_Index': M_t[t],
                'PD': pd_val,
                'Default_Flag': default_event
            })
            
            if default_event == 1:
                break
                
    return pd.DataFrame(records)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    static_df = generate_static_sme(N_SMES)
    static_path = os.path.join(OUTPUT_DIR, 'sme_static.csv')
    print(f"Saving static data to {static_path}...")
    static_df.to_csv(static_path, index=False)
    
    monthly_df = generate_monthly_financials(static_df)
    monthly_path = os.path.join(OUTPUT_DIR, 'sme_monthly.csv')
    print(f"Saving monthly data to {monthly_path}...")
    monthly_df.to_csv(monthly_path, index=False)
    
    print("Done.")

if __name__ == "__main__":
    main()
