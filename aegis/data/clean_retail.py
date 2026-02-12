import pandas as pd
import numpy as np
import os
import sys

DATA_DIR = os.path.join(os.getcwd(), 'data', 'home-credit-default-risk')
OUTPUT_DIR = os.path.join(os.getcwd(), 'data', 'processed')

def load_data(file_name):
    
    path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return None
    
    if os.path.getsize(path) == 0:
        print(f"File is empty: {path}. Skipping.")
        return None

    print(f"Loading {file_name}...")
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        return None

def clean_application_data(df):
    
    if df is None or df.empty:
        print("Application data is empty.")
        return None

    print("Cleaning application data...")
    
    
    days_cols = [col for col in df.columns if 'DAYS' in col]
    for col in days_cols:
        df[col] = df[col].replace(365243, np.nan)
        if 'BIRTH' in col or 'EMPLOYED' in col or 'REGISTRATION' in col or 'ID_PUBLISH' in col:
             df[f'YEARS_{col.replace("DAYS_", "")}'] = df[col] / -365.25

    return df

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    app_train = load_data('application_train.csv')
    app_test = load_data('application_test.csv')
    
    start_dfs = []
    if app_train is not None:
        app_train['TARGET'] = app_train['TARGET']
        start_dfs.append(app_train)
    else:
        print("Warning: application_train.csv is missing or empty.")

    if app_test is not None:
        app_test['TARGET'] = np.nan
        start_dfs.append(app_test)

    if start_dfs:
        df = pd.concat(start_dfs, axis=0, ignore_index=True)
        clean_df = clean_application_data(df)
        if clean_df is not None:
            output_path = os.path.join(OUTPUT_DIR, 'clean_application_df.parquet')
            print(f"Saving cleaned data to {output_path}...")
            clean_df.to_parquet(output_path, index=False)
    else:
        print("No application data to process.")
    
    tables = [
        'bureau.csv', 'bureau_balance.csv', 'POS_CASH_balance.csv', 
        'credit_card_balance.csv', 'previous_application.csv', 'installments_payments.csv'
    ]
    
    for table_name in tables:
        tbl = load_data(table_name)
        if tbl is not None:
            days_cols = [col for col in tbl.columns if 'DAYS' in col]
            for col in days_cols:
                tbl[col] = tbl[col].replace(365243, np.nan)
            
            clean_name = f"clean_{table_name.replace('.csv', '')}.parquet"
            tbl.to_parquet(os.path.join(OUTPUT_DIR, clean_name), index=False)
            print(f"Saved {clean_name}")

if __name__ == "__main__":
    main()
