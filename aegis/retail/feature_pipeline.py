import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.retail.data_loader import load_all_data
from src.retail.cleaning import clean_application_data
from src.retail.aggregations import (
    aggregate_bureau,
    aggregate_bureau_balance,
    aggregate_pos_cash,
    aggregate_credit_card,
    aggregate_installments,
    aggregate_previous_application
)

OUTPUT_DIR = os.path.join(os.getcwd(), 'outputs')

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    data_path = os.path.join(os.getcwd(), 'data', 'home-credit-default-risk')
    data = load_all_data(data_path)
    
    
    app_train = data.get('application_train')
    app_test = data.get('application_test')
    
    if app_train is None and app_test is None:
        print("Error: No application data found.")
        return

    dfs = []
    if app_train is not None:
        dfs.append(app_train)
    if app_test is not None:
        dfs.append(app_test)
        
    if not dfs:
        print("No application data.")
        return
        
    main_df = pd.concat(dfs, ignore_index=True, sort=False)
    print(f"Main DF shape before cleaning: {main_df.shape}")
    
    main_df = clean_application_data(main_df)
    print(f"Main DF shape after cleaning: {main_df.shape}")
    
    if 'TARGET' not in main_df.columns:
        print("Warning: TARGET column missing (likely using test data only). Generating Synthetic TARGET for training demo.")
        import numpy as np
        rng = np.random.default_rng(42)
        
        dti = main_df['AMT_CREDIT'] / (main_df['AMT_INCOME_TOTAL'] + 1)
        dti_norm = (dti - dti.mean()) / (dti.std() + 1e-5)
        
        prob = 1 / (1 + np.exp(-( -2.5 + 0.5 * dti_norm + rng.normal(0, 1, len(main_df)) )))
        main_df['TARGET'] = (prob > rng.random(len(main_df))).astype(int)
        print(f"Generated synthetic TARGET with mean: {main_df['TARGET'].mean():.4f}")

    
    bureau = data.get('bureau')
    bureau_balance = data.get('bureau_balance')
    
    if bureau_balance is not None:
        bb_agg = aggregate_bureau_balance(bureau_balance)
        
        if bureau is not None and bb_agg is not None:
             bureau = bureau.merge(bb_agg, on='SK_ID_BUREAU', how='left')
    
    bureau_agg = aggregate_bureau(bureau)
    if bureau_agg is not None:
        print(f"Bureau features: {bureau_agg.shape}")
        
    pos_agg = aggregate_pos_cash(data.get('POS_CASH_balance'))
    if pos_agg is not None:
        print(f"POS features: {pos_agg.shape}")
        
    cc_agg = aggregate_credit_card(data.get('credit_card_balance'))
    if cc_agg is not None:
        print(f"CC features: {cc_agg.shape}")
        
    inst_agg = aggregate_installments(data.get('installments_payments'))
    if inst_agg is not None:
        print(f"Installments features: {inst_agg.shape}")
        
    prev_agg = aggregate_previous_application(data.get('previous_application'))
    if prev_agg is not None:
        print(f"Prev App features: {prev_agg.shape}")
        
    
    features = main_df
    
    for agg_df in [bureau_agg, pos_agg, cc_agg, inst_agg, prev_agg]:
        if agg_df is not None:
            features = features.merge(agg_df, on='SK_ID_CURR', how='left')
            
    features = features.drop_duplicates(subset=['SK_ID_CURR'])
    
    print(f"Final feature count: {features.shape[1]}")
    print(f"Final row count: {features.shape[0]}")
    
    output_path = os.path.join(OUTPUT_DIR, 'retail_features.parquet')
    print(f"Saving to {output_path}...")
    features.to_parquet(output_path, compression='snappy', index=False)
    print("Unbelievable pipeline success.")

if __name__ == "__main__":
    main()
