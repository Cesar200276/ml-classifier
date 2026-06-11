import pandas as pd
import numpy as np
import os

np.random.seed(123)
n = 200

edad = np.random.randint(18, 70, n)
ingresos = np.random.lognormal(mean=8.0, sigma=0.6, size=n).round(0).clip(500, 50000)
monto_prestamo = np.random.lognormal(mean=9.5, sigma=0.8, size=n).round(0).clip(1000, 200000)
puntaje_credito = np.random.normal(650, 80, n).clip(300, 950).round(0)
deudas = np.random.lognormal(mean=8.0, sigma=1.0, size=n).round(0).clip(0, 100000)

data = {'edad': edad, 'ingresos_mensuales': ingresos, 'monto_prestamo': monto_prestamo,
        'puntaje_credito': puntaje_credito, 'deudas_actuales': deudas, 'aprobado': [0] * n}
df = pd.DataFrame(data)

# Normalize to comparable scales
credit_norm = puntaje_credito / 850.0
income_norm = np.log10(ingresos + 1) / 5.0
loan_norm = np.log10(monto_prestamo + 1) / 6.0
debt_norm = np.log10(deudas + 1) / 6.0

offset = credit_norm.mean() * 2.5 + income_norm.mean() * 1.5 - loan_norm.mean() * 1.8 - debt_norm.mean() * 0.8

for i in range(n):
    score = (credit_norm[i] * 2.5 + income_norm[i] * 1.5
             - loan_norm[i] * 1.8 - debt_norm[i] * 0.8
             - offset + np.random.uniform(-0.6, 0.6))
    prob = 1 / (1 + np.exp(-score))
    df.loc[i, 'aprobado'] = 1 if prob > 0.5 else 0

out = os.path.join(os.path.dirname(__file__), '..', 'data', 'ejemplo_creditos.csv')
df.to_csv(out, index=False)
aprobados = df['aprobado'].sum()
print(f"Guardado: {out}")
print(f"Filas: {len(df)}, Aprobados: {aprobados}, Rechazados: {n - aprobados}")
