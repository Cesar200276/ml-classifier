import pandas as pd
import numpy as np
import os

np.random.seed(42)
n = 150

horas = np.random.randint(0, 15, n)
gasto = np.random.randint(0, 5000, n)
ingreso = np.random.normal(50000, 20000, n).clip(10000, 150000).round(0)
edad = np.random.randint(18, 70, n)

data = {'edad': edad, 'ingreso': ingreso, 'horas_estudio': horas, 'gasto_ocio': gasto, 'aprobado': [0] * n}
df = pd.DataFrame(data)

for i in range(n):
    score = (df.loc[i, 'horas_estudio'] * 0.4 + df.loc[i, 'ingreso'] / 50000 * 0.2
             - df.loc[i, 'gasto_ocio'] / 5000 * 0.3 + df.loc[i, 'edad'] / 50 * 0.1 + np.random.uniform(-0.5, 0.5))
    prob = 1 / (1 + np.exp(-(score - 3)))
    df.loc[i, 'aprobado'] = 1 if prob > 0.5 else 0

out = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample.csv')
df.to_csv(out, index=False)
print(f"Muestra guardada en {out}")
print(f"Clases: {df['aprobado'].value_counts().to_dict()}")
