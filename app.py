import os
import sys
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'ml_app_secret_key_2024'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
MODEL_DIR = os.path.join(DATA_DIR, 'models')
PYTHON_DIR = os.path.join(BASE_DIR, 'python')
SAMPLE_CSV = os.path.join(DATA_DIR, 'sample.csv')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def run_python_script(script_name, args, input_data=None):
    script_path = os.path.join(PYTHON_DIR, script_name)
    cmd = [sys.executable, script_path] + args
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    try:
        stdout, stderr = proc.communicate(input=input_data, timeout=120)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        raise RuntimeError(f"Timeout en {script_name}. El proceso tardó más de 120 segundos.")
    if proc.returncode != 0:
        error_msg = stderr.strip() if stderr else "Error desconocido"
        raise RuntimeError(f"Error en {script_name}: {error_msg}")
    return stdout


def list_csv_files():
    files = []
    if os.path.exists(SAMPLE_CSV):
        files.append({'name': 'sample.csv', 'path': SAMPLE_CSV, 'type': 'Ejemplo predefinido'})
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            if f.endswith('.csv'):
                path = os.path.join(UPLOAD_DIR, f)
                files.append({'name': f, 'path': path, 'type': 'Subido por usuario'})
    return files


def get_csv_preview(path, n=5):
    import pandas as pd
    df = pd.read_csv(path)
    return {
        'columns': df.columns.tolist(),
        'rows': df.head(n).to_dict('records'),
        'shape': list(df.shape)
    }


def get_model_info():
    model_path = os.path.join(MODEL_DIR, 'model.pkl')
    results_path = os.path.join(MODEL_DIR, 'results.json')
    if os.path.exists(model_path) and os.path.exists(results_path):
        with open(results_path, 'r') as f:
            return json.load(f)
    return None


@app.route('/')
def index():
    files = list_csv_files()
    model_info = get_model_info()
    preview = None
    selected = request.args.get('file', '')
    if selected and os.path.exists(selected):
        preview = get_csv_preview(selected)
    elif files:
        preview = get_csv_preview(files[0]['path'])
    return render_template('index.html', files=files, preview=preview,
                           model_info=model_info, selected=selected)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('Nombre de archivo vacío')
        return redirect(url_for('index'))
    if not file.filename.endswith('.csv'):
        flash('Solo se permiten archivos CSV')
        return redirect(url_for('index'))
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    file.save(filepath)
    flash(f'Archivo {file.filename} subido correctamente')
    return redirect(url_for('index', file=filepath))


@app.route('/generate_sample', methods=['POST'])
def generate_sample():
    try:
        run_python_script('generate_sample.py', [])
        flash('Datos de ejemplo generados correctamente')
    except Exception as e:
        flash(f'Error: {str(e)}')
    return redirect(url_for('index'))


@app.route('/train', methods=['POST'])
def train():
    csv_path = request.form.get('csv_path', '')
    target_col = request.form.get('target_col', '')
    if not csv_path or not os.path.exists(csv_path):
        flash('Selecciona un archivo CSV válido')
        return redirect(url_for('index'))
    try:
        args = [csv_path, MODEL_DIR]
        if target_col:
            args.append(target_col)
        output = run_python_script('train.py', args)
        results = json.loads(output.strip())
        with open(os.path.join(MODEL_DIR, 'results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        flash('Modelo entrenado correctamente')
        return redirect(url_for('index', file=csv_path))
    except json.JSONDecodeError:
        flash('Error: el script de entrenamiento no devolvió resultados válidos. Verifica que el CSV tenga datos numéricos y una columna target con valores 0 y 1.')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error al entrenar: {str(e)}')
        return redirect(url_for('index'))


@app.route('/predict_page')
def predict_page():
    model_info = get_model_info()
    if not model_info:
        flash('Primero debes entrenar un modelo')
        return redirect(url_for('index'))
    return render_template('predict.html', model_info=model_info)


@app.route('/predict', methods=['POST'])
def predict():
    model_path = os.path.join(MODEL_DIR, 'model.pkl')
    model_info = get_model_info()
    if not model_info:
        return jsonify({'error': 'No hay modelo entrenado'}), 400
    try:
        data = {}
        for feat in model_info['feature_names']:
            val = request.form.get(feat, '0')
            try:
                data[feat] = float(val)
            except ValueError:
                data[feat] = val
        input_json = json.dumps(data)
        output = run_python_script('predict.py', [model_path], input_data=input_json)
        result = json.loads(output.strip())
        return render_template('predict.html', model_info=model_info,
                               prediction=result, input_data=data)
    except Exception as e:
        flash(f'Error en predicción: {str(e)}')
        return redirect(url_for('predict_page'))


@app.route('/api/predict', methods=['POST'])
def api_predict():
    model_path = os.path.join(MODEL_DIR, 'model.pkl')
    model_info = get_model_info()
    if not model_info:
        return jsonify({'error': 'No hay modelo entrenado'}), 400
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Enviar JSON con los features'}), 400
        input_json = json.dumps(data)
        output = run_python_script('predict.py', [model_path], input_data=input_json)
        result = json.loads(output.strip())
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/graphs')
def graphs():
    return render_template('graphs.html')


@app.route('/results')
def results():
    model_info = get_model_info()
    if not model_info:
        flash('Primero debes entrenar un modelo')
        return redirect(url_for('index'))
    return render_template('results.html', model_info=model_info)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
