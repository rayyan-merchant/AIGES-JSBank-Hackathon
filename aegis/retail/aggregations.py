import pandas as pd
import numpy as np

def aggregate_bureau(bureau_df):
    
    if bureau_df is None or bureau_df.empty:
        return None
        
    print("Aggregating bureau...")
    
    
    cols = ['AMT_CREDIT_SUM', 'AMT_CREDIT_SUM_DEBT', 'AMT_CREDIT_MAX_OVERDUE']
    for c in cols:
        if c in bureau_df.columns:
            bureau_df[c] = pd.to_numeric(bureau_df[c], errors='coerce')
            
    active_loans = bureau_df[bureau_df['CREDIT_ACTIVE'] == 'Active'].groupby('SK_ID_CURR').size().rename('BUREAU_ACTIVE_LOANS_COUNT')
    
    agg_funcs = {
        'SK_ID_BUREAU': 'count',
        'AMT_CREDIT_SUM': 'mean',
        'AMT_CREDIT_SUM_DEBT': 'sum',
        'AMT_CREDIT_MAX_OVERDUE': 'max'
    }
    agg_funcs = {k: v for k, v in agg_funcs.items() if k in bureau_df.columns}
    
    bureau_agg = bureau_df.groupby('SK_ID_CURR').agg(agg_funcs)
    
    rename_map = {
        'SK_ID_BUREAU': 'BUREAU_LOAN_COUNT',
        'AMT_CREDIT_SUM': 'BUREAU_AMT_CREDIT_SUM_MEAN',
        'AMT_CREDIT_SUM_DEBT': 'BUREAU_AMT_DEBT_SUM',
        'AMT_CREDIT_MAX_OVERDUE': 'BUREAU_AMT_MAX_OVERDUE_MAX'
    }
    bureau_agg.rename(columns=rename_map, inplace=True)
    
    bureau_agg = bureau_agg.join(active_loans, how='left').fillna({'BUREAU_ACTIVE_LOANS_COUNT': 0})
    
    
    total_credit = bureau_df.groupby('SK_ID_CURR')['AMT_CREDIT_SUM'].sum()
    bureau_agg['BUREAU_UTILIZATION'] = bureau_agg['BUREAU_AMT_DEBT_SUM'] / total_credit
    bureau_agg['BUREAU_UTILIZATION'] = bureau_agg['BUREAU_UTILIZATION'].replace([np.inf, -np.inf], 0).fillna(0)
    
    return bureau_agg

def aggregate_bureau_balance(bureau_balance_df):
    
    if bureau_balance_df is None or bureau_balance_df.empty:
        return None
    print("Aggregating bureau_balance...")
    
    
    bb = bureau_balance_df.copy()
    
    
    status_map = {'C': 0, 'X': 0, '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5}
    bb['STATUS_NUM'] = bb['STATUS'].map(status_map).fillna(0).astype(int)
    
    
    agg_funcs = {
        'STATUS_NUM': 'max'
    }
    
    bb_agg = bb.groupby('SK_ID_BUREAU').agg(agg_funcs).rename(columns={'STATUS_NUM': 'BB_STATUS_MAX'})
    
    delinq = bb[bb['STATUS_NUM'] >= 1].groupby('SK_ID_BUREAU').size().rename('BB_DELINQ_MONTHS')
    
    bb_agg = bb_agg.join(delinq, how='left').fillna({'BB_DELINQ_MONTHS': 0})
    
    return bb_agg

def aggregate_pos_cash(pos_df):
    
    if pos_df is None or pos_df.empty:
        return None
    print("Aggregating POS_CASH...")
    
    
    cols = ['SK_DPD', 'CNT_INSTALMENT_FUTURE']
    for c in cols:
        pos_df[c] = pd.to_numeric(pos_df[c], errors='coerce')

    agg_funcs = {
        'SK_DPD': ['mean', 'max'],
        'CNT_INSTALMENT_FUTURE': 'mean'
    }
    
    pos_agg = pos_df.groupby('SK_ID_CURR').agg(agg_funcs)
    pos_agg.columns = ['_'.join(col).upper() for col in pos_agg.columns.values]
    pos_agg.rename(columns={
        'SK_DPD_MEAN': 'POS_SK_DPD_MEAN',
        'SK_DPD_MAX': 'POS_SK_DPD_MAX',
        'CNT_INSTALMENT_FUTURE_MEAN': 'POS_FUTURE_INSTALMENTS_MEAN'
    }, inplace=True)
    
    
    active_rows = pos_df[pos_df['NAME_CONTRACT_STATUS'] == 'Active'].groupby('SK_ID_CURR').size()
    total_rows = pos_df.groupby('SK_ID_CURR').size()
    
    pos_agg['POS_ACTIVE_RATIO'] = (active_rows / total_rows).fillna(0)
    
    return pos_agg

def aggregate_credit_card(cc_df):
    
    if cc_df is None or cc_df.empty:
        return None
    print("Aggregating Credit Card...")
    
    
    cols = ['AMT_BALANCE', 'AMT_CREDIT_LIMIT_ACTUAL', 'SK_DPD', 'AMT_PAYMENT_CURRENT', 'AMT_TOTAL_RECEIVABLE']
    for c in cols:
        if c in cc_df.columns:
            cc_df[c] = pd.to_numeric(cc_df[c], errors='coerce')
            
    cc_df['UTILIZATION'] = cc_df['AMT_BALANCE'] / cc_df['AMT_CREDIT_LIMIT_ACTUAL'].replace(0, np.nan)
    cc_df['PAYMENT_RATIO'] = cc_df['AMT_PAYMENT_CURRENT'] / cc_df['AMT_TOTAL_RECEIVABLE'].replace(0, np.nan)
    
    agg_funcs = {
        'UTILIZATION': ['mean', 'max'],
        'SK_DPD': 'mean',
        'PAYMENT_RATIO': 'mean'
    }
    
    cc_agg = cc_df.groupby('SK_ID_CURR').agg(agg_funcs)
    cc_agg.columns = ['_'.join(col).upper() for col in cc_agg.columns.values]
    
    rename_map = {
        'UTILIZATION_MEAN': 'CC_UTILIZATION_MEAN',
        'UTILIZATION_MAX': 'CC_UTILIZATION_MAX',
        'SK_DPD_MEAN': 'CC_SK_DPD_MEAN',
        'PAYMENT_RATIO_MEAN': 'CC_PAYMENT_RATIO_MEAN'
    }
    cc_agg.rename(columns=rename_map, inplace=True)
    
    return cc_agg

def aggregate_installments(inst_df):
    
    if inst_df is None or inst_df.empty:
        return None
    print("Aggregating Installments...")
    
    
    cols = ['DAYS_ENTRY_PAYMENT', 'DAYS_INSTALMENT']
    for c in cols:
        inst_df[c] = pd.to_numeric(inst_df[c], errors='coerce')
        
    inst_df['DELAY'] = inst_df['DAYS_ENTRY_PAYMENT'] - inst_df['DAYS_INSTALMENT']
    inst_df['IS_LATE'] = (inst_df['DELAY'] > 0).astype(int)
    
    agg_funcs = {
        'DELAY': ['mean', 'max'],
        'IS_LATE': 'mean'
    }
    
    inst_agg = inst_df.groupby('SK_ID_CURR').agg(agg_funcs)
    inst_agg.columns = ['_'.join(col).upper() for col in inst_agg.columns.values]
    
    rename_map = {
        'DELAY_MEAN': 'INSTAL_DELAY_MEAN',
        'DELAY_MAX': 'INSTAL_DELAY_MAX',
        'IS_LATE_MEAN': 'INSTAL_LATE_PAYMENT_RATIO'
    }
    inst_agg.rename(columns=rename_map, inplace=True)
    
    return inst_agg

def aggregate_previous_application(prev_df):
    
    if prev_df is None or prev_df.empty:
        return None
    print("Aggregating Previous Applications...")
    
    
    cols = ['AMT_APPLICATION', 'AMT_CREDIT']
    for c in cols:
        prev_df[c] = pd.to_numeric(prev_df[c], errors='coerce')
        
    prev_df['IS_APPROVED'] = (prev_df['NAME_CONTRACT_STATUS'] == 'Approved').astype(int)
    prev_df['IS_REFUSED'] = (prev_df['NAME_CONTRACT_STATUS'] == 'Refused').astype(int)
    
    agg_funcs = {
        'IS_APPROVED': 'mean',
        'AMT_APPLICATION': 'mean',
        'AMT_CREDIT': 'mean',
        'IS_REFUSED': 'sum'
    }
    
    prev_agg = prev_df.groupby('SK_ID_CURR').agg(agg_funcs)
    
    rename_map = {
        'IS_APPROVED': 'PREV_APPROVAL_RATE',
        'AMT_APPLICATION': 'PREV_AMT_APPLICATION_MEAN',
        'AMT_CREDIT': 'PREV_AMT_CREDIT_MEAN',
        'IS_REFUSED': 'PREV_REJECTION_COUNT'
    }
    prev_agg.rename(columns=rename_map, inplace=True)
    
    return prev_agg
