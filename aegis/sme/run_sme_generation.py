import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.sme.generator import (
    generate_static_sme, 
    generate_monthly_financials, 
    compute_default
)

OUTPUT_DIR = os.path.join(os.getcwd(), 'data', 'SME')

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print("Starting SME Data Generation Pipeline...")
    
    n_smes = 20000
    print(f"Generating {n_smes} static profiles...")
    static_df = generate_static_sme(n_smes)
    
    print(f"Generating 36 months of financials...")
    monthly_df = generate_monthly_financials(static_df, months=36)
    
    print("Computing default probabilities...")
    final_monthly_df = compute_default(static_df, monthly_df)
    
    static_path = os.path.join(OUTPUT_DIR, 'sme_static.csv')
    monthly_path = os.path.join(OUTPUT_DIR, 'sme_monthly.csv')
    
    print(f"Saving to {static_path}...")
    static_df.to_csv(static_path, index=False)
    
    print(f"Saving to {monthly_path}...")
    final_monthly_df.to_csv(monthly_path, index=False)
    
    default_rate = final_monthly_df['default_flag'].mean()
    avg_revenue = final_monthly_df['revenue'].mean()
    avg_debt_ratio = static_df['debt_ratio'].mean()
    
    print("-" * 30)
    print(f"Stats:")
    print(f"SMEs: {n_smes}")
    print(f"Total Monthly Records: {len(final_monthly_df)}")
    print(f"Default Rate: {default_rate:.2%}")
    print(f"Average Monthly Revenue: ${avg_revenue:,.2f}")
    print(f"Average Debt Ratio: {avg_debt_ratio:.2f}")
    print("-" * 30)
    
    if 0.05 <= default_rate <= 0.15:
        print("SUCCESS: Default rate within target range (5-15%).")
    else:
        print("WARNING: Default rate outside target range.")

if __name__ == "__main__":
    main()
