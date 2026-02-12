import pandas as pd
import numpy as np
import os
import pickle
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_PATH = os.path.join('outputs', 'retail_features.parquet')
MODEL_DIR = os.path.join('models')
SEED = 42

def train_retail_model():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    logger.info(f"Loading data from {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        logger.error(f"Data file not found: {DATA_PATH}")
        return

    df = pd.read_parquet(DATA_PATH)
    logger.info(f"Data loaded. Shape: {df.shape}")

    if 'TARGET' not in df.columns:
        logger.error("TARGET column missing in data.")
        return

    y = df['TARGET']
    X = df.drop(columns=['TARGET', 'SK_ID_CURR'])

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    logger.info(f"Numeric features: {len(numeric_features)}")
    logger.info(f"Categorical features: {len(categorical_features)}")

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    
    cv_scores = []
    feature_importances = np.zeros(len(numeric_features) + 100)
    
    
    
    logger.info("Starting CV Training...")
    
    oof_preds = np.zeros(len(X))
    models = []
    
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        clf = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', lgb.LGBMClassifier(random_state=SEED, n_jobs=-1, verbose=-1))
        ])
        
        clf.fit(X_train, y_train)
        
        val_preds = clf.predict_proba(X_val)[:, 1]
        oof_preds[val_idx] = val_preds
        
        score = roc_auc_score(y_val, val_preds)
        cv_scores.append(score)
        logger.info(f"Fold {fold+1} AUC: {score:.4f}")
        
        
    logger.info(f"Mean CV AUC: {np.mean(cv_scores):.4f}")
    
    logger.info("Retraining on full dataset...")
    final_model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', lgb.LGBMClassifier(random_state=SEED, n_jobs=-1, verbose=-1))
    ])
    final_model.fit(X, y)
    
    model_path = os.path.join(MODEL_DIR, 'retail_pd_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(final_model, f)
    logger.info(f"Model saved to {model_path}")
    
    oof_df = pd.DataFrame({'SK_ID_CURR': df.iloc[X.index]['SK_ID_CURR'], 'TARGET': y, 'PREDICTION': oof_preds})
    oof_path = os.path.join(MODEL_DIR, 'oof_predictions.csv')
    oof_df.to_csv(oof_path, index=False)
    logger.info(f"OOF predictions saved to {oof_path}")
    
    lgbm = final_model.named_steps['classifier']
    
    
    try:
        feature_names = final_model.named_steps['preprocessor'].get_feature_names_out()
        importances = lgbm.feature_importances_
        
        if len(feature_names) != len(importances):
            logger.warning(f"Feature names ({len(feature_names)}) != importances ({len(importances)}). Using indices.")
            feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        fi_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
        fi_df = fi_df.sort_values(by='importance', ascending=False)
        
        fi_path = os.path.join(MODEL_DIR, 'retail_feature_importance.csv')
        fi_df.to_csv(fi_path, index=False)
        logger.info(f"Feature importance saved to {fi_path}")
        
        print("\nTop 20 Features:")
        print(fi_df.head(20))
        
    except Exception as e:
        logger.error(f"Error extracting feature importance: {e}")
        importances = lgbm.feature_importances_
        fi_df = pd.DataFrame({'feature': [f"feature_{i}" for i in range(len(importances))], 'importance': importances})
        fi_df = fi_df.sort_values(by='importance', ascending=False)
        fi_path = os.path.join(MODEL_DIR, 'retail_feature_importance.csv')
        fi_df.to_csv(fi_path, index=False)
        logger.info(f"Feature importance (with fallback names) saved to {fi_path}")
        print("\nTop 20 Features:")
        print(fi_df.head(20))

if __name__ == "__main__":
    train_retail_model()
