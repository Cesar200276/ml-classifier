import sys
import json
import pandas as pd
import joblib
import os

model_path = sys.argv[1]
input_json = sys.stdin.read()

data = json.loads(input_json)
artifacts = joblib.load(model_path)
model = artifacts['model']
scaler = artifacts['scaler']
feature_names = artifacts['feature_names']
target_col = artifacts.get('target_col', 'target')

input_df = pd.DataFrame([data])

cat_cols = input_df.select_dtypes(include=['object']).columns
input_df = pd.get_dummies(input_df, columns=cat_cols, drop_first=True)

for col in feature_names:
    if col not in input_df.columns:
        input_df[col] = 0

input_df = input_df[feature_names]

input_scaled = scaler.transform(input_df)

prediction = int(model.predict(input_scaled)[0])
probabilities = model.predict_proba(input_scaled)[0].tolist()

result = {
    'prediction': prediction,
    'probabilities': probabilities,
    'classes': model.classes_.tolist()
}

print(json.dumps(result))
