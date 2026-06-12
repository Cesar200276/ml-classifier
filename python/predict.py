import sys
import json
import os
import math


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


model_path = sys.argv[1]
model_dir = os.path.dirname(model_path)
model_json_path = os.path.join(model_dir, 'model.json')

with open(model_json_path, 'r') as f:
    model_data = json.load(f)

input_json = sys.stdin.read()
data = json.loads(input_json)

feature_names = model_data['feature_names']
coefficients = model_data['coefficients']
intercept = model_data['intercept']
scaler_mean = model_data['scaler_mean']
scaler_scale = model_data['scaler_scale']

vals = []
for col in feature_names:
    v = data.get(col, 0)
    try:
        vals.append(float(v))
    except (ValueError, TypeError):
        vals.append(0.0)

x_scaled = [(vals[i] - scaler_mean[i]) / scaler_scale[i] for i in range(len(vals))]

z = intercept
for i in range(len(x_scaled)):
    z += coefficients[i] * x_scaled[i]

prob_class1 = sigmoid(z)
prob_class0 = 1.0 - prob_class1

classes = model_data['classes']
prediction = classes[1] if prob_class1 > 0.5 else classes[0]

result = {
    'prediction': prediction,
    'probabilities': [prob_class0, prob_class1],
    'classes': classes
}

print(json.dumps(result))
