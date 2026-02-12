import pandas as pd
import numpy as np
import os
import pickle
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STATIC_PATH = os.path.join('data', 'SME', 'sme_static.csv')
MONTHLY_PATH = os.path.join('data', 'SME', 'sme_monthly.csv')
MODEL_DIR = 'models'
SEED = 42

def engineer_sme_features(static_df, monthly_df):
    
    logger.info("Engineering SME features...")
    
    agg_funcs = {
        'revenue': ['mean', 'std'],
        'EBITDA': ['mean', 'std'],
        'cash': ['mean', 'min'],
        'debt_payment': ['mean'],
        'PD': ['mean', 'max'],
        'macro_state': ['mean']
    }
    
    available = {k: v for k, v in agg_funcs.items() if k in monthly_df.columns}
    
    monthly_agg = monthly_df.groupby('SME_ID').agg(available)
    monthly_agg.columns = ['_'.join(col).upper() for col in monthly_agg.columns.values]
    monthly_agg.reset_index(inplace=True)
    
    if 'REVENUE_STD' in monthly_agg.columns and 'REVENUE_MEAN' in monthly_agg.columns:
        monthly_agg['REVENUE_VOLATILITY'] = monthly_agg['REVENUE_STD'] / (monthly_agg['REVENUE_MEAN'] + 1)
    
    if 'EBITDA_MEAN' in monthly_agg.columns and 'REVENUE_MEAN' in monthly_agg.columns:
        monthly_agg['MARGIN_MEAN'] = monthly_agg['EBITDA_MEAN'] / (monthly_agg['REVENUE_MEAN'] + 1)
    
    if 'CASH_MEAN' in monthly_agg.columns and 'DEBT_PAYMENT_MEAN' in monthly_agg.columns:
        monthly_agg['LIQUIDITY_MEAN'] = monthly_agg['CASH_MEAN'] / (monthly_agg['DEBT_PAYMENT_MEAN'] + 1)
    
    growth_records = []
    for sme_id, grp in monthly_df.groupby('SME_ID'):
        grp_sorted = grp.sort_values('month')
        first_half = grp_sorted[grp_sorted['month'] <= 18]['revenue'].mean()
        second_half = grp_sorted[grp_sorted['month'] > 18]['revenue'].mean()
        growth = (second_half - first_half) / (first_half + 1)
        growth_records.append({'SME_ID': sme_id, 'GROWTH_RATE': growth})
    growth_df = pd.DataFrame(growth_records)
    
    monthly_agg = monthly_agg.merge(growth_df, on='SME_ID', how='left')
    
    if 'default_flag' in monthly_df.columns:
        default_per_sme = monthly_df.groupby('SME_ID')['default_flag'].max().rename('TARGET')
        monthly_agg = monthly_agg.merge(default_per_sme, on='SME_ID', how='left')
    
    merged = static_df.merge(monthly_agg, on='SME_ID', how='inner')
    
    logger.info(f"Final SME feature table shape: {merged.shape}")
    return merged

def train_sme_model():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    logger.info("Loading SME data...")
    static_df = pd.read_csv(STATIC_PATH)
    monthly_df = pd.read_csv(MONTHLY_PATH)
    logger.info(f"Static: {static_df.shape}, Monthly: {monthly_df.shape}")
    
    df = engineer_sme_features(static_df, monthly_df)
    
    if 'TARGET' not in df.columns:
        logger.error("TARGET column missing.")
        return
    
    y = df['TARGET']
    drop_cols = ['TARGET', 'SME_ID']
    leak_cols = [c for c in df.columns if 'PD' in c.upper()]
    drop_cols.extend(leak_cols)
    
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    logger.info(f"Numeric: {len(numeric_features)}, Categorical: {len(categorical_features)}")
    
    le_dict = {}
    for col in categorical_features:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        le_dict[col] = le
    
    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores = []
    oof_preds = np.zeros(len(X_imputed))
    
    logger.info("Starting CV Training...")
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X_imputed, y)):
        X_train, X_val = X_imputed.iloc[train_idx], X_imputed.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        model = lgb.LGBMClassifier(random_state=SEED, n_jobs=-1, verbose=-1)
        model.fit(X_train, y_train)
        
        val_preds = model.predict_proba(X_val)[:, 1]
        oof_preds[val_idx] = val_preds
        
        score = roc_auc_score(y_val, val_preds)
        cv_scores.append(score)
        logger.info(f"Fold {fold+1} AUC: {score:.4f}")
    
    logger.info(f"Mean CV AUC: {np.mean(cv_scores):.4f}")
    
    logger.info("Retraining on full data...")
    final_model = lgb.LGBMClassifier(random_state=SEED, n_jobs=-1, verbose=-1)
    final_model.fit(X_imputed, y)
    
    model_path = os.path.join(MODEL_DIR, 'sme_pd_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump({'model': final_model, 'imputer': imputer, 'label_encoders': le_dict, 'features': X.columns.tolist()}, f)
    logger.info(f"Model saved to {model_path}")
    
    fi_df = pd.DataFrame({
        'feature': X_imputed.columns,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    fi_path = os.path.join(MODEL_DIR, 'sme_feature_importance.csv')
    fi_df.to_csv(fi_path, index=False)
    logger.info(f"Feature importance saved to {fi_path}")
    
    print("\nTop 20 SME Features:")
    print(fi_df.head(20))

if __name__ == "__main__":
    train_sme_model()
