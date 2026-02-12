
import sys
from unittest.mock import MagicMock
sys.modules["cv2"] = MagicMock()

import os
import pickle
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

MODEL_DIR = 'models'
OUTPUT_DIR = 'outputs'

def load_model(model_name):
    
    path = os.path.join(MODEL_DIR, model_name)
    with open(path, 'rb') as f:
        return pickle.load(f)

def explain_customer(customer_row, model_type='retail'):
    
    try:
        import shap
    except ImportError:
        logger.error("SHAP not installed. Run: pip install shap")
        return _fallback_explain(customer_row, model_type)
    
    if model_type == 'retail':
        pipeline = load_model('retail_pd_model.pkl')
        lgbm = pipeline.named_steps['classifier']
        preprocessor = pipeline.named_steps['preprocessor']
        
        if isinstance(customer_row, dict):
            customer_df = pd.DataFrame([customer_row])
        else:
            customer_df = pd.DataFrame([customer_row.to_dict()])
        
        X_transformed = preprocessor.transform(customer_df)
        
        explainer = shap.TreeExplainer(lgbm)
        shap_values = explainer.shap_values(X_transformed)
        
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]
        
        try:
            feature_names = preprocessor.get_feature_names_out()
        except:
            feature_names = [f"feature_{i}" for i in range(len(sv))]
        
    elif model_type == 'sme':
        model_dict = load_model('sme_pd_model.pkl')
        lgbm = model_dict['model']
        features = model_dict['features']
        
        if isinstance(customer_row, dict):
            customer_df = pd.DataFrame([customer_row])
        else:
            customer_df = pd.DataFrame([customer_row.to_dict()])
        
        available = [f for f in features if f in customer_df.columns]
        X = customer_df[available]
        
        explainer = shap.TreeExplainer(lgbm)
        shap_values = explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]
        
        feature_names = available
    else:
        return {"error": f"Unknown model type: {model_type}"}
    
    feature_contrib = sorted(
        zip(feature_names, sv),
        key=lambda x: abs(x[1]),
        reverse=True
    )
    
    top_features = feature_contrib[:10]
    
    explanation = {
        'model_type': model_type,
        'prediction': float(lgbm.predict_proba(X_transformed if model_type == 'retail' else X)[0][1]),
        'top_contributing_features': [
            {'feature': f, 'shap_value': float(v)} for f, v in top_features
        ],
        'base_value': float(explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value),
        'all_shap_values': {str(f): float(v) for f, v in zip(feature_names, sv)}
    }
    
    return explanation

def _fallback_explain(customer_row, model_type):
    
    logger.warning("Using fallback explanation (feature importance based)")
    
    if model_type == 'retail':
        fi_path = os.path.join(MODEL_DIR, 'retail_feature_importance.csv')
    else:
        fi_path = os.path.join(MODEL_DIR, 'sme_feature_importance.csv')
    
    if os.path.exists(fi_path):
        fi = pd.read_csv(fi_path)
        top = fi.head(10)
        return {
            'model_type': model_type,
            'method': 'feature_importance_fallback',
            'top_features': top.to_dict(orient='records')
        }
    
    return {'error': 'No explanation available'}

def generate_shap_artifacts(model_type='retail', n_samples=100):
    
    try:
        import shap
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        logger.error("SHAP or matplotlib not installed.")
        return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    if model_type == 'retail':
        pipeline = load_model('retail_pd_model.pkl')
        lgbm = pipeline.named_steps['classifier']
        preprocessor = pipeline.named_steps['preprocessor']
        
        df = pd.read_parquet(os.path.join('outputs', 'retail_features.parquet'))
        X = df.drop(columns=['TARGET', 'SK_ID_CURR'], errors='ignore').head(n_samples)
        X_transformed = preprocessor.transform(X)
        
        try:
            feature_names = list(preprocessor.get_feature_names_out())
        except:
            feature_names = [f"f_{i}" for i in range(X_transformed.shape[1])]
    else:
        model_dict = load_model('sme_pd_model.pkl')
        lgbm = model_dict['model']
        features = model_dict['features']
        imputer = model_dict['imputer']
        
        df = pd.read_csv(os.path.join('data', 'SME', 'sme_static.csv')).head(n_samples)
        available = [f for f in features if f in df.columns]
        X = df[available]
        X_transformed = imputer.transform(X)
        feature_names = available
    
    explainer = shap.TreeExplainer(lgbm)
    shap_values = explainer.shap_values(X_transformed)
    
    if isinstance(shap_values, list):
        sv = shap_values[1]
    else:
        sv = shap_values
    
    plt.figure(figsize=(12, 8))
    shap.summary_plot(sv, X_transformed, feature_names=feature_names, show=False)
    plot_path = os.path.join(OUTPUT_DIR, f'shap_summary_plot_{model_type}.png')
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()
    logger.info(f"SHAP summary plot saved to {plot_path}")
    
    sv_df = pd.DataFrame(sv, columns=feature_names)
    csv_path = os.path.join(OUTPUT_DIR, f'shap_values_sample_{model_type}.csv')
    sv_df.to_csv(csv_path, index=False)
    logger.info(f"SHAP values saved to {csv_path}")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Generating SHAP artifacts for Retail model...")
    generate_shap_artifacts('retail', n_samples=50)
    
    print("\nGenerating SHAP artifacts for SME model...")
    generate_shap_artifacts('sme', n_samples=50)
    
    print("\nDone!")
