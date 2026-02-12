import pandas as pd
import numpy as np
import os

OUTPUT_DIR = os.path.join(os.getcwd(), 'data', 'processed')

def validate_sme_data():
    static_path = os.path.join(OUTPUT_DIR, 'sme_static.csv')
    monthly_path = os.path.join(OUTPUT_DIR, 'sme_monthly.csv')
    
    if not os.path.exists(static_path) or not os.path.exists(monthly_path):
        print("Data files missing!")
        return
    
    static_df = pd.read_csv(static_path)
    monthly_df = pd.read_csv(monthly_path)
    
    print(f"Static SMEs: {len(static_df)}")
    print(f"Monthly Records: {len(monthly_df)}")
    
    defaulted_smes = monthly_df[monthly_df['Default_Flag'] == 1]['SME_ID'].unique()
    default_rate = len(defaulted_smes) / len(static_df)
    print(f"Default Rate: {default_rate:.2%}")
    
    if default_rate < 0.05 or default_rate > 0.15:
        print("WARNING: Default rate outside 5-15% range.")
    else:
        print("Default rate within target range.")
        
    if (monthly_df['Revenue'] < 0).any():
        print("WARNING: Negative Revenue detected.")
    
    min_cash = monthly_df['Cash'].min()
    print(f"Min Cash: {min_cash:.2f}")
    
    print("\nRevenue Stats:")
    print(monthly_df['Revenue'].describe())
    
    print("\nDebt Payment Stats:")
    print(monthly_df['Debt_Payment'].describe())

if __name__ == "__main__":
    validate_sme_data()
