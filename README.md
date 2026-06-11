# ML Classifier — Guía completa del proyecto

Aplicación web para entrenar un modelo de **regresión logística** y hacer predicciones. Usa **Python** para el machine learning y **PHP** o **Flask** (Python) para servir la web.

---

## 1. Estructura del proyecto

```
ml_app/
├── app.py                         # Servidor web (Flask / Python)
├── python/                        # Scripts de Machine Learning
│   ├── train.py                   #   Entrena el modelo
│   ├── predict.py                 #   Hace predicciones
│   ├── generate_sample.py         #   Genera dataset de estudiantes
│   └── generate_creditos.py       #   Genera dataset de créditos
├── data/
│   ├── sample.csv                 # Dataset: aprobación de estudiantes
│   ├── ejemplo_creditos.csv       # Dataset: aprobación de créditos
│   ├── uploads/                   # CSVs subidos por el usuario
│   └── models/
│       ├── model.pkl              # Modelo entrenado (joblib)
│       └── results.json           # Métricas del modelo
├── templates/                     # HTML templates (Flask)
│   ├── index.html                 #   Página principal
│   ├── results.html               #   Resultados detallados
│   └── predict.html               #   Formulario de predicción
├── static/
│   └── style.css                  # Estilos CSS
└── php/                           # Versión PHP alternativa
    ├── config.php                 #   Configuración
    ├── index.php                  #   Página principal
    ├── results.php                #   Resultados
    ├── predict.php                #   Predicción
    └── style.css                  #   Estilos
```

---

## 2. Flujo de la aplicación

```
Usuario                    Servidor Web                    Python
   │                           │                             │
   │── Carga CSV / Elige ──────▶                             │
   │    dataset de ejemplo                                   │
   │                           │                             │
   │── Entrena modelo ────────▶──── llama a train.py ───────▶│
   │                           │                             │── Lee CSV
   │                           │                             │── Divide train/test
   │                           │                             │── Escala datos
   │                           │                             │── Entrena regresión logística
   │                           │◄── devuelve métricas ───────│── Guarda model.pkl
   │◄── Muestra métricas ──────│                             │
   │                           │                             │
   │── Ingresa datos ─────────▶──── llama a predict.py ─────▶│
   │    para predecir           │                             │── Carga modelo
   │                           │                             │── Escala input
   │                           │                             │── Predice clase
   │                           │◄── devuelve resultado ──────│── Calcula probabilidad
   │◄── Muestra predicción ────│                             │
```

---

## 3. Scripts Python explicados

### `python/generate_sample.py` — Datos de estudiantes

Genera 150 registros sintéticos de estudiantes. Las variables son:

| Variable | Tipo | Rango | Descripción |
|---|---|---|---|
| `edad` | int | 18–69 | Edad del estudiante |
| `ingreso` | float | 10,000–150,000 | Ingreso anual en USD |
| `horas_estudio` | int | 0–14 | Horas de estudio semanales |
| `gasto_ocio` | int | 0–5,000 | Gasto mensual en ocio |
| `aprobado` | int | 0/1 | **Target**: 1 = aprueba, 0 = no aprueba |

La clase se asigna con una **función logística**:
```
score = horas*0.4 + (ingreso/50000)*0.2 - (gasto/5000)*0.3 + (edad/50)*0.1 + ruido
probabilidad = 1 / (1 + e^-(score - 3))
aprobado = 1 si probabilidad > 0.5
```

Esto crea una relación no lineal donde **más horas de estudio aumentan la probabilidad** de aprobar, y **más gasto en ocio la disminuye**.

### `python/generate_creditos.py` — Datos de créditos

Genera 200 registros de solicitudes de préstamo. Variables:

| Variable | Tipo | Rango | Descripción |
|---|---|---|---|
| `edad` | int | 18–69 | Edad del solicitante |
| `ingresos_mensuales` | float | 605–12,162 | Ingreso mensual en USD |
| `monto_prestamo` | float | 1,313–105,948 | Monto solicitado |
| `puntaje_credito` | int | 300–950 | Score crediticio (FICO) |
| `deudas_actuales` | float | 136–46,290 | Deudas vigentes |
| `aprobado` | int | 0/1 | **Target**: 1 = aprobado, 0 = rechazado |

Usa escalas normalizadas (log10 y división) y función sigmoide para generar la clase.

### `python/train.py` — Entrenamiento

```
Argumentos:
  sys.argv[1] = ruta al CSV
  sys.argv[2] = directorio donde guardar el modelo
  sys.argv[3] = (opcional) nombre de la columna objetivo
```

Pipeline completo:

1. **Lee el CSV** con pandas
2. **Separa** features (X) y target (y)
3. **One-hot encoding** de variables categóricas (si las hay)
4. **Train/test split**: 70% entrenamiento, 30% prueba, con estratificación
5. **Estandarización** con `StandardScaler` (media=0, desviación=1)
6. **Entrena** `LogisticRegression` de scikit-learn
7. **Evalúa** y calcula: accuracy, precision, recall, F1, matriz de confusión
8. **Guarda** el modelo y scaler con `joblib` en `data/models/model.pkl`
9. **Imprime** resultados como JSON

### `python/predict.py` — Predicción

```
Argumentos:
  sys.argv[1] = ruta al modelo .pkl
  Entrada: JSON por STDIN con los valores de los features
```

Pipeline:

1. **Lee el JSON** desde STDIN
2. **Carga** modelo, scaler y nombres de features desde `model.pkl`
3. **Crea** un DataFrame con los datos ingresados
4. **Aplica** el mismo escalado que en entrenamiento
5. **Predice** la clase y las probabilidades
6. **Imprime** resultado como JSON

---

## 4. Servidor web

### Flask (`app.py`) — Para desarrollo

Rutas disponibles:

| Ruta | Método | Descripción |
|---|---|---|
| `/` | GET | Página principal con vista previa de datos |
| `/upload` | POST | Subir archivo CSV |
| `/generate_sample` | POST | Generar dataset de ejemplo |
| `/train` | POST | Entrenar modelo |
| `/results` | GET | Resultados detallados |
| `/predict_page` | GET | Formulario de predicción |
| `/predict` | POST | Predecir desde formulario |
| `/api/predict` | POST | API REST: predicción vía JSON |

La función `run_python_script()` ejecuta los scripts Python usando `subprocess.Popen`:
- Los argumentos de línea de comandos se pasan como args
- El JSON de entrada se pasa por **STDIN** (evita problemas de quoting)
- La salida se captura desde STDOUT
- Si hay error, se lanza una excepción

### PHP (`php/`) — Para producción

Archivos:

- `config.php` — Configuración: rutas, detección de Python, funciones helper
- `index.php` — Página principal: formularios, vista previa, resultados
- `results.php` — Resultados detallados del modelo
- `predict.php` — Formulario y resultado de predicción

La función `run_python()` usa `proc_open()` para pasar datos por STDIN, y `shell_exec()` para scripts sin entrada.

---

## 5. Cómo usar la aplicación

### En desarrollo (Flask)

```powershell
cd ml_app
python app.py
# Abrir http://localhost:5000
```

### En producción (PHP)

1. Instalar PHP 8+ y Python 3.7+ en el servidor
2. Copiar `ml_app/` al servidor
3. Apuntar el document root de Apache/Nginx a `ml_app/php/`
4. Asegurar que PHP tiene permisos de escritura en `data/uploads/` y `data/models/`

### En la nube (Render)

1. Subir `ml_app/` a GitHub
2. En [render.com](https://render.com) crear Web Service
3. Conectar repositorio, elegir **Python**, comando: `gunicorn app:app`
4. Agregar variable de entorno: `PYTHON_VERSION=3.13`

---

## 6. API REST

Una vez entrenado el modelo, se puede usar desde cualquier cliente:

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"edad": 25, "ingreso": 50000, "horas_estudio": 10, "gasto_ocio": 1000}'
```

Respuesta:
```json
{
  "prediction": 1,
  "probabilities": [0.14, 0.86],
  "classes": [0, 1]
}
```

---

## 7. Dependencias

**Python:** `pip install flask scikit-learn pandas numpy joblib scipy`

**PHP:** Solo requiere PHP nativo (no necesita extensiones adicionales).

---

## 8. Arquitectura: ¿Por qué PHP + Python?

```
PHP/Python Flask                  Python
┌─────────────────┐        ┌──────────────────┐
│  Interfaz web    │        │  Lógica de ML     │
│  ┌─────────────┐ │  llama │  ┌──────────────┐ │
│  │ index.php   │─┼───────┼─▶│ train.py     │ │
│  │ predict.php │─┼───────┼─▶│ predict.py   │ │
│  │ results.php │ │  JSON  │  └──────────────┘ │
│  └─────────────┘ │◄───────┼─                  │
└─────────────────┘        └──────────────────┘
```

- **PHP** se encarga de la web: templates, sesiones, formularios, subida de archivos
- **Python** se encarga del ML: procesamiento de datos, entrenamiento, predicción
- Se comunican vía: argumentos CLI + STDIN/STDOUT con JSON
- Esto permite desplegar la web en cualquier hosting PHP y tener los scripts Python independientes
