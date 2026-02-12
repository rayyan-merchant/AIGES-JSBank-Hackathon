import pandas as pd
import numpy as np
import os
import gc

PROCESSED_DIR = os.path.join(os.getcwd(), 'data', 'processed')

def load_parquet(name):
    path = os.path.join(PROCESSED_DIR, f"{name}.parquet")
    if os.path.exists(path):
        print(f"Loading {name}...")
        df = pd.read_parquet(path)
        if df.empty or len(df.columns) <= 1:
            print(f"Warning: {name} is empty or invalid. Skipping.")
            return None
        return df
    print(f"Warning: {name} not found.")
    return None

def aggregate_bureau_balance(bureau_balance):
    if bureau_balance is None:
        return None
    print("Aggregating bureau_balance...")
    bb_agg = bureau_balance.groupby('SK_ID_BUREAU').agg({
        'MONTHS_BALANCE': ['min', 'max', 'size']
    })
    bb_agg.columns = pd.Index(['BB_' + e[0] + "_" + e[1].upper() for e in bb_agg.columns.tolist()])
    return bb_agg

def aggregate_bureau(bureau, bb_agg=None):
    if bureau is None:
        return None
    print("Aggregating bureau...")
    
    if bb_agg is not None:
        bureau = bureau.merge(bb_agg, on='SK_ID_BUREAU', how='left')
    
    num_aggregations = {
        'DAYS_CREDIT': ['min', 'max', 'mean', 'var'],
        'DAYS_CREDIT_ENDDATE': ['min', 'max', 'mean'],
        'DAYS_CREDIT_UPDATE': ['mean'],
        'CREDIT_DAY_OVERDUE': ['max', 'mean'],
        'AMT_CREDIT_MAX_OVERDUE': ['mean'],
        'AMT_CREDIT_SUM': ['max', 'mean', 'sum'],
        'AMT_CREDIT_SUM_DEBT': ['max', 'mean', 'sum'],
        'AMT_CREDIT_SUM_OVERDUE': ['mean'],
        'AMT_CREDIT_SUM_LIMIT': ['mean', 'sum'],
        'CNT_CREDIT_PROLONG': ['sum'],
    }
    
    if bb_agg is not None:
        for col in bb_agg.columns:
            num_aggregations[col] = ['min', 'max', 'mean']

    existing_cols = [c for c in num_aggregations.keys() if c in bureau.columns]
    
    for col in existing_cols:
         bureau[col] = pd.to_numeric(bureau[col], errors='coerce')

    agg_dict = {k: num_aggregations[k] for k in existing_cols}
    
    bureau_agg = bureau.groupby('SK_ID_CURR').agg(agg_dict)
    bureau_agg.columns = pd.Index(['BUREAU_' + e[0] + "_" + e[1].upper() for e in bureau_agg.columns.tolist()])
    
    active_agg = bureau[bureau['CREDIT_ACTIVE'] == 'Active'].groupby('SK_ID_CURR').agg(agg_dict)
    active_agg.columns = pd.Index(['BUREAU_ACTIVE_' + e[0] + "_" + e[1].upper() for e in active_agg.columns.tolist()])
    bureau_agg = bureau_agg.join(active_agg, how='left')
    
    return bureau_agg

def aggregate_previous_application(prev):
    if prev is None:
        return None
    print("Aggregating previous_application...")
    
    num_aggregations = {
        'AMT_ANNUITY': ['min', 'max', 'mean'],
        'AMT_APPLICATION': ['min', 'max', 'mean'],
        'AMT_CREDIT': ['min', 'max', 'mean'],
        'AMT_DOWN_PAYMENT': ['min', 'max', 'mean'],
        'AMT_GOODS_PRICE': ['min', 'max', 'mean'],
        'HOUR_APPR_PROCESS_START': ['min', 'max', 'mean'],
        'RATE_DOWN_PAYMENT': ['min', 'max', 'mean'],
        'DAYS_DECISION': ['min', 'max', 'mean'],
        'CNT_PAYMENT': ['mean', 'sum'],
    }
    
    existing_cols = [c for c in num_aggregations.keys() if c in prev.columns]
    
    for col in existing_cols:
        prev[col] = pd.to_numeric(prev[col], errors='coerce')

    agg_dict = {k: num_aggregations[k] for k in existing_cols}
    
    prev_agg = prev.groupby('SK_ID_CURR').agg(agg_dict)
    prev_agg.columns = pd.Index(['PREV_' + e[0] + "_" + e[1].upper() for e in prev_agg.columns.tolist()])
    
    approved = prev[prev['NAME_CONTRACT_STATUS'] == 'Approved'].groupby('SK_ID_CURR').agg(agg_dict)
    approved.columns = pd.Index(['PREV_APPROVED_' + e[0] + "_" + e[1].upper() for e in approved.columns.tolist()])
    prev_agg = prev_agg.join(approved, how='left')
    
    return prev_agg

def aggregate_pos_cash(pos):
    if pos is None:
        return None
    print("Aggregating POS_CASH_balance...")
    
    aggregations = {
        'MONTHS_BALANCE': ['max', 'mean', 'size'],
        'SK_DPD': ['max', 'mean'],
        'SK_DPD_DEF': ['max', 'mean']
    }
    
    existing_cols = [c for c in aggregations.keys() if c in pos.columns]
    for col in existing_cols:
        pos[col] = pd.to_numeric(pos[col], errors='coerce')
        
    agg_dict = {k: aggregations[k] for k in existing_cols}
    
    pos_agg = pos.groupby('SK_ID_CURR').agg(agg_dict)
    pos_agg.columns = pd.Index(['POS_' + e[0] + "_" + e[1].upper() for e in pos_agg.columns.tolist()])
    return pos_agg

def aggregate_installments(ins):
    if ins is None:
        return None
    print("Aggregating installments_payments...")
    
    num_cols = ['AMT_PAYMENT', 'AMT_INSTALMENT', 'DAYS_ENTRY_PAYMENT', 'DAYS_INSTALMENT']
    for col in num_cols:
        if col in ins.columns:
            ins[col] = pd.to_numeric(ins[col], errors='coerce')
            
    ins['PAYMENT_PERC'] = ins['AMT_PAYMENT'] / ins['AMT_INSTALMENT']
    ins['PAYMENT_DIFF'] = ins['AMT_INSTALMENT'] - ins['AMT_PAYMENT']
    ins['DPD'] = ins['DAYS_ENTRY_PAYMENT'] - ins['DAYS_INSTALMENT']
    ins['DBD'] = ins['DAYS_INSTALMENT'] - ins['DAYS_ENTRY_PAYMENT']
    ins['DPD'] = ins['DPD'].apply(lambda x: x if x > 0 else 0)
    ins['DBD'] = ins['DBD'].apply(lambda x: x if x > 0 else 0)
    
    aggregations = {
        'NUM_INSTALMENT_VERSION': ['nunique'],
        'DPD': ['max', 'mean', 'sum'],
        'DBD': ['max', 'mean', 'sum'],
        'PAYMENT_PERC': ['max', 'mean', 'std', 'var'],
        'PAYMENT_DIFF': ['max', 'mean', 'std', 'var'],
        'AMT_INSTALMENT': ['max', 'mean', 'sum'],
        'AMT_PAYMENT': ['min', 'max', 'mean', 'sum'],
        'DAYS_ENTRY_PAYMENT': ['max', 'mean', 'sum']
    }
    
    existing_cols = [c for c in aggregations.keys() if c in ins.columns]
    agg_dict = {k: aggregations[k] for k in existing_cols}
    
    ins_agg = ins.groupby('SK_ID_CURR').agg(agg_dict)
    ins_agg.columns = pd.Index(['INSTAL_' + e[0] + "_" + e[1].upper() for e in ins_agg.columns.tolist()])
    return ins_agg

def aggregate_credit_card(cc):
    if cc is None:
        return None
    print("Aggregating credit_card_balance...")
    
    cc.drop(['SK_ID_PREV'], axis= 1, inplace = True)
    
    for col in cc.columns:
        if col != 'SK_ID_CURR':
            cc[col] = pd.to_numeric(cc[col], errors='coerce')
            
    cc_agg = cc.groupby('SK_ID_CURR').agg(['min', 'max', 'mean', 'sum', 'var'])
    cc_agg.columns = pd.Index(['CC_' + e[0] + "_" + e[1].upper() for e in cc_agg.columns.tolist()])
    return cc_agg

def main():
    df = load_parquet('clean_application_df')
    if df is None:
        print("Error: clean_application_df not found. Run Step 1 first.")
        return

    bureau = load_parquet('clean_bureau')
    bureau_balance = load_parquet('clean_bureau_balance')
    pos = load_parquet('clean_POS_CASH_balance')
    ins = load_parquet('clean_installments_payments')
    cc = load_parquet('clean_credit_card_balance')
    prev = load_parquet('clean_previous_application')
    
    if bureau_balance is not None:
        bb_agg = aggregate_bureau_balance(bureau_balance)
    else:
        bb_agg = None
        
    if bureau is not None:
        bureau_agg = aggregate_bureau(bureau, bb_agg)
        if bureau_agg is not None:
            df = df.merge(bureau_agg, on='SK_ID_CURR', how='left')
    
    if prev is not None:
        prev_agg = aggregate_previous_application(prev)
        if prev_agg is not None:
            df = df.merge(prev_agg, on='SK_ID_CURR', how='left')

    if pos is not None:
        pos_agg = aggregate_pos_cash(pos)
        if pos_agg is not None:
            df = df.merge(pos_agg, on='SK_ID_CURR', how='left')
            
    if ins is not None:
        ins_agg = aggregate_installments(ins)
        if ins_agg is not None:
            df = df.merge(ins_agg, on='SK_ID_CURR', how='left')
            
    if cc is not None:
        cc_agg = aggregate_credit_card(cc)
        if cc_agg is not None:
            df = df.merge(cc_agg, on='SK_ID_CURR', how='left')
            
    
    print("Computing derived features...")
    
    if 'BUREAU_AMT_CREDIT_SUM_DEBT_SUM' in df.columns:
        df['TOTAL_DEBT'] = df['BUREAU_AMT_CREDIT_SUM_DEBT_SUM'].fillna(0)
    else:
        df['TOTAL_DEBT'] = 0
        
    
    
    
    df['INCOME_MONTHLY'] = df['AMT_INCOME_TOTAL'] / 12
    df['SIMPLE_DTI'] = df['AMT_ANNUITY'] / df['INCOME_MONTHLY']
    
    cc_cols = [c for c in df.columns if 'CC_AMT_BALANCE' in c]
    
    
    print(f"Final shape: {df.shape}")
    
    output_path = os.path.join(PROCESSED_DIR, 'retail_features.parquet')
    print(f"Saving to {output_path}...")
    df.to_parquet(output_path, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
