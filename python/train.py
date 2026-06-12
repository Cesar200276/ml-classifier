import sys
import json
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

csv_path = sys.argv[1]
model_dir = sys.argv[2]
target_col = sys.argv[3] if len(sys.argv) > 3 else None

os.makedirs(model_dir, exist_ok=True)

try:
    df = pd.read_csv(csv_path)
except Exception as e:
    print(json.dumps({"error": f"No se pudo leer el CSV: {str(e)}"}))
    sys.exit(1)

if target_col is None:
    target_col = df.columns[-1]

if df[target_col].nunique() < 2:
    print(json.dumps({"error": f"La columna '{target_col}' debe tener al menos 2 valores distintos (0 y 1). Valores encontrados: {df[target_col].unique().tolist()}"}))
    sys.exit(1)

if target_col not in df.columns:
    print(json.dumps({"error": f"La columna '{target_col}' no existe en el CSV. Columnas disponibles: {df.columns.tolist()}"}))
    sys.exit(1)

y = df[target_col]
X = df.drop(columns=[target_col])

for col in X.columns:
    if X[col].dtype == 'object':
        X[col] = pd.to_numeric(X[col], errors='coerce')
    if X[col].isna().any():
        X[col] = X[col].fillna(X[col].median())

cat_cols = X.select_dtypes(include=['object', 'category']).columns
X = pd.get_dummies(X, columns=cat_cols, drop_first=True)

feature_names = X.columns.tolist()

stratify_ok = len(y.unique()) >= 2 and all(y.value_counts() >= 2)
split_kwargs = {'test_size': 0.3, 'random_state': 42}
if stratify_ok:
    split_kwargs['stratify'] = y
X_train, X_test, y_train, y_test = train_test_split(X, y, **split_kwargs)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

cm = confusion_matrix(y_test, y_pred)
results = {
    'accuracy': round(accuracy_score(y_test, y_pred), 4),
    'precision': round(precision_score(y_test, y_pred, zero_division=0), 4),
    'recall': round(recall_score(y_test, y_pred, zero_division=0), 4),
    'f1_score': round(f1_score(y_test, y_pred, zero_division=0), 4),
    'confusion_matrix': cm.tolist(),
    'class_report': classification_report(y_test, y_pred, output_dict=True, zero_division=0),
    'feature_names': feature_names,
    'n_features': len(feature_names),
    'n_samples': len(df),
    'target_column': target_col,
    'classes': y.unique().tolist()
}

joblib.dump({'model': model, 'scaler': scaler, 'feature_names': feature_names, 'target_col': target_col},
            os.path.join(model_dir, 'model.pkl'))

model_json = {
    'coefficients': model.coef_[0].tolist(),
    'intercept': float(model.intercept_[0]),
    'scaler_mean': scaler.mean_.tolist(),
    'scaler_scale': scaler.scale_.tolist(),
    'feature_names': feature_names,
    'classes': results['classes'],
    'target_col': target_col
}
with open(os.path.join(model_dir, 'model.json'), 'w') as f:
    json.dump(model_json, f, indent=2)

print(json.dumps(results))
