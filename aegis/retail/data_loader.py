import pandas as pd
import os
import sys

def load_all_data(data_path: str) -> dict:
    
    files = {
        'application_train': 'application_train.csv',
        'application_test': 'application_test.csv',
        'bureau': 'bureau.csv',
        'bureau_balance': 'bureau_balance.csv',
        'previous_application': 'previous_application.csv',
        'POS_CASH_balance': 'POS_CASH_balance.csv',
        'credit_card_balance': 'credit_card_balance.csv',
        'installments_payments': 'installments_payments.csv',
        'description': 'HomeCredit_columns_description.csv'
    }
    
    data = {}
    
    print(f"Loading data from {data_path}...")
    
    for key, filename in files.items():
        file_path = os.path.join(data_path, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            data[key] = None
            continue
            
        try:
            if os.path.getsize(file_path) == 0:
                print(f"Warning: File is empty: {filename}")
                data[key] = None
                continue

            
            if key == 'description':
                df = pd.read_csv(file_path, encoding='ISO-8859-1')
            else:
                df = pd.read_csv(file_path)
                
            print(f"Loaded {key}: {df.shape}")
            data[key] = df
            
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            data[key] = None
            
    return data

if __name__ == "__main__":
    import os
    DATA_DIR = os.path.join(os.getcwd(), 'data', 'home-credit-default-risk')
    if not os.path.exists(DATA_DIR):
        print(f"Directory not found: {DATA_DIR}")
    else:
        data = load_all_data(DATA_DIR)
        
        for k, v in data.items():
            if v is not None:
                print(f"{k}: OK {v.shape}")
            else:
                print(f"{k}: MISSING/EMPTY")
