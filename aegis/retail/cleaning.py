import pandas as pd
import numpy as np

def clean_application_data(df: pd.DataFrame) -> pd.DataFrame:
    
    if df is None or df.empty:
        return df

    df = df.copy()
    
    if 'DAYS_EMPLOYED' in df.columns:
        df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace(365243, np.nan)
        
    days_map = {
        'DAYS_BIRTH': 'age_years',
        'DAYS_EMPLOYED': 'employment_years',
        'DAYS_REGISTRATION': 'registration_years',
        'DAYS_ID_PUBLISH': 'id_publish_years'
    }
    
    for day_col, year_col in days_map.items():
        if day_col in df.columns:
            df[year_col] = df[day_col] / -365.25
            df.drop(columns=[day_col], inplace=True)
            
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ['TARGET', 'SK_ID_CURR']
    numeric_cols = [c for c in numeric_cols if c not in exclude_cols]
    
    for col in numeric_cols:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    for col in categorical_cols:
        if isinstance(df[col].dtype, pd.CategoricalDtype):
             if 'UNKNOWN' not in df[col].cat.categories:
                 df[col] = df[col].cat.add_categories('UNKNOWN')
             df[col] = df[col].fillna('UNKNOWN')
        else:
             df[col] = df[col].fillna('UNKNOWN')
        
    for col in categorical_cols:
        unique_vals = df[col].dropna().unique()
        if set(unique_vals) <= {'Y', 'N'}:
            df[col] = df[col].map({'Y': 1, 'N': 0})
        elif set(unique_vals) <= {'F', 'M'}:
             pass
             
    flags = ['FLAG_OWN_CAR', 'FLAG_OWN_REALTY']
    for col in flags:
        if col in df.columns:
             df[col] = df[col].map({'Y': 1, 'N': 0})

    return df

if __name__ == "__main__":
    print("Testing cleaning module...")
    
    data = {
        'SK_ID_CURR': [1, 2, 3],
        'TARGET': [0, 1, 0],
        'DAYS_BIRTH': [-10000, -15000, -20000],
        'DAYS_EMPLOYED': [-1000, 365243, -2000],
        'AMT_INCOME_TOTAL': [50000, np.nan, 70000],
        'NAME_CONTRACT_TYPE': ['Cash loans', np.nan, 'Revolving loans'],
        'FLAG_OWN_CAR': ['Y', 'N', 'Y']
    }
    
    df_raw = pd.DataFrame(data)
    print("Raw:")
    print(df_raw)
    
    df_clean = clean_application_data(df_raw)
    print("\nCleaned:")
    print(df_clean)
    
    assert df_clean['age_years'].iloc[0] > 0
    assert np.isnan(df_raw['DAYS_EMPLOYED'].iloc[1]) == False
    
    print(df_clean['employment_years'])
    
    assert df_clean['AMT_INCOME_TOTAL'].isna().sum() == 0
    assert df_clean['NAME_CONTRACT_TYPE'].iloc[1] == 'UNKNOWN'
    assert df_clean['FLAG_OWN_CAR'].dtype in [np.int64, np.float64, int]
    print("\nTest Passed!")
