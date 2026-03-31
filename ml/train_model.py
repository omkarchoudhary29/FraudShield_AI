import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from xgboost import XGBClassifier
from sklearn.ensemble import IsolationForest
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Create directories
os.makedirs("models", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("reports", exist_ok=True)

def load_or_generate_data():
    """Load existing dataset or generate new one"""
    if os.path.exists("data/fraud_dataset.csv"):
        print("Loading existing dataset...")
        df = pd.read_csv("data/fraud_dataset.csv")
    else:
        print("Generating new dataset...")
        from generate_dataset import generate_fraud_dataset
        df = generate_fraud_dataset(n_samples=10000, fraud_ratio=0.15)
        df.to_csv("data/fraud_dataset.csv", index=False)
    
    return df

def prepare_features(df):
    """Prepare features for training"""
    # Separate features and target
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]
    
    # Handle categorical features
    categorical_cols = ["merchant_category"]
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    
    if categorical_cols[0] in X.columns:
        cat_encoded = encoder.fit_transform(X[categorical_cols])
        cat_df = pd.DataFrame(
            cat_encoded,
            columns=encoder.get_feature_names_out(categorical_cols)
        )
        X = X.drop(columns=categorical_cols)
        X = pd.concat([X.reset_index(drop=True), cat_df.reset_index(drop=True)], axis=1)
    
    return X, y, encoder

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple models and select the best"""
    
    print("\n" + "="*50)
    print("Training Random Forest...")
    print("="*50)
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_proba = rf_model.predict_proba(X_test)[:, 1]
    
    print("\nRandom Forest Results:")
    print(f"Accuracy: {accuracy_score(y_test, rf_pred):.4f}")
    print(f"Precision: {precision_score(y_test, rf_pred):.4f}")
    print(f"Recall: {recall_score(y_test, rf_pred):.4f}")
    print(f"F1 Score: {f1_score(y_test, rf_pred):.4f}")
    print(f"AUC-ROC: {roc_auc_score(y_test, rf_proba):.4f}")
    
    print("\n" + "="*50)
    print("Training XGBoost...")
    print("="*50)
    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=(len(y_train) - y_train.sum()) / y_train.sum(),
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train, y_train)
    xgb_pred = xgb_model.predict(X_test)
    xgb_proba = xgb_model.predict_proba(X_test)[:, 1]
    
    print("\nXGBoost Results:")
    print(f"Accuracy: {accuracy_score(y_test, xgb_pred):.4f}")
    print(f"Precision: {precision_score(y_test, xgb_pred):.4f}")
    print(f"Recall: {recall_score(y_test, xgb_pred):.4f}")
    print(f"F1 Score: {f1_score(y_test, xgb_pred):.4f}")
    print(f"AUC-ROC: {roc_auc_score(y_test, xgb_proba):.4f}")
    
    # Select best model based on F1 score
    rf_f1 = f1_score(y_test, rf_pred)
    xgb_f1 = f1_score(y_test, xgb_pred)
    
    if xgb_f1 >= rf_f1:
        print("\n✓ XGBoost selected as best model")
        best_model = xgb_model
        best_pred = xgb_pred
        best_proba = xgb_proba
        model_name = "XGBoost"
    else:
        print("\n✓ Random Forest selected as best model")
        best_model = rf_model
        best_pred = rf_pred
        best_proba = rf_proba
        model_name = "RandomForest"
    
    return best_model, best_pred, best_proba, model_name

def evaluate_model(y_test, y_pred, y_proba, model_name):
    """Evaluate and visualize model performance"""
    
    print("\n" + "="*50)
    print(f"Final {model_name} Model Evaluation")
    print("="*50)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc_roc = roc_auc_score(y_test, y_proba)
    
    print(f"\nAccuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"AUC-ROC:   {auc_roc:.4f}")
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Fraud"]))
    
    # Save metrics
    metrics = {
        "model_name": model_name,
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "auc_roc": float(auc_roc),
        "confusion_matrix": cm.tolist()
    }
    
    return metrics

def get_feature_importance(model, feature_names, top_n=15):
    """Get and display feature importance"""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]
        
        print("\n" + "="*50)
        print("Top Feature Importances:")
        print("="*50)
        
        feature_importance_dict = {}
        for i, idx in enumerate(indices):
            importance = importances[idx]
            feature_name = feature_names[idx]
            print(f"{i+1}. {feature_name}: {importance:.4f}")
            feature_importance_dict[feature_name] = float(importance)
        
        return feature_importance_dict
    
    return {}

def main():
    print("="*50)
    print("FraudShield AI - Model Training Pipeline")
    print("="*50)
    
    # Load data
    df = load_or_generate_data()
    print(f"\nDataset loaded: {len(df)} samples")
    print(f"Fraud cases: {df['is_fraud'].sum()} ({df['is_fraud'].mean()*100:.2f}%)")
    
    # Prepare features
    print("\nPreparing features...")
    X, y, encoder = prepare_features(df)
    print(f"Features: {X.shape[1]}")
    print(f"Feature names: {list(X.columns)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Scale features
    print("\nScaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    best_model, y_pred, y_proba, model_name = train_models(
        X_train_scaled, X_test_scaled, y_train, y_test
    )
    
    # Evaluate
    metrics = evaluate_model(y_test, y_pred, y_proba, model_name)
    
    # Feature importance
    feature_importance = get_feature_importance(best_model, X.columns)
    
    # Save model and preprocessors
    print("\n" + "="*50)
    print("Saving model and preprocessors...")
    print("="*50)
    
    joblib.dump(best_model, "models/fraud_model.joblib")
    joblib.dump(scaler, "models/scaler.joblib")
    joblib.dump(encoder, "models/encoder.joblib")
    
    # Save metadata
    import json
    metadata = {
        "model_type": model_name,
        "version": "1.0.0",
        "metrics": metrics,
        "feature_importance": feature_importance,
        "feature_names": list(X.columns),
        "threshold": 0.5,
        "trained_at": pd.Timestamp.now().isoformat()
    }
    
    with open("models/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("\n✓ Model saved to models/fraud_model.joblib")
    print("✓ Scaler saved to models/scaler.joblib")
    print("✓ Encoder saved to models/encoder.joblib")
    print("✓ Metadata saved to models/model_metadata.json")
    
    print("\n" + "="*50)
    print("Training Complete!")
    print("="*50)
    print(f"\nFinal Model: {model_name}")
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall: {metrics['recall']:.2%}")
    print(f"F1 Score: {metrics['f1_score']:.2%}")
    print(f"AUC-ROC: {metrics['auc_roc']:.4f}")

if __name__ == "__main__":
    main()
