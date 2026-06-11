<?php
// index.php - Página principal
require_once __DIR__ . '/config.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action'])) {
        try {
            if ($_POST['action'] === 'upload' && isset($_FILES['file'])) {
                $f = $_FILES['file'];
                if ($f['error'] === 0 && pathinfo($f['name'], PATHINFO_EXTENSION) === 'csv') {
                    move_uploaded_file($f['tmp_name'], UPLOAD_DIR . '/' . basename($f['name']));
                    $_SESSION['msg'] = 'Archivo subido correctamente';
                }
            } elseif ($_POST['action'] === 'generate') {
                run_python('generate_sample.py');
                $_SESSION['msg'] = 'Datos de ejemplo generados';
            } elseif ($_POST['action'] === 'train') {
                $csv = $_POST['csv_path'] ?? '';
                $target = $_POST['target_col'] ?? '';
                $args = [$csv, MODEL_DIR];
                if ($target) $args[] = $target;
                $output = run_python('train.py', $args);
                $results = json_decode($output, true);
                if ($results) file_put_contents(MODEL_DIR . '/results.json', json_encode($results, JSON_PRETTY_PRINT));
                $_SESSION['msg'] = 'Modelo entrenado correctamente';
            }
        } catch (Exception $e) {
            $_SESSION['msg'] = 'Error: ' . $e->getMessage();
        }
    }
    header('Location: index.php');
    exit;
}

$files = list_csv_files();
$model_info = get_model_info();
$selected = $_GET['file'] ?? ($files[0]['path'] ?? '');
$preview = $selected ? get_csv_preview($selected) : null;
$msg = $_SESSION['msg'] ?? ''; unset($_SESSION['msg']);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clasificador ML - PHP + Python</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="container">
    <header>
        <h1>Clasificador con Regresión Logística</h1>
        <p>PHP + Python · Entrena un modelo con tus datos CSV</p>
    </header>
    <?php if ($msg): ?><div class="flash"><?= htmlspecialchars($msg) ?></div><?php endif; ?>

    <div class="grid-2col">
        <section class="card">
            <h2>1. Cargar datos</h2>
            <form method="post" enctype="multipart/form-data" class="upload-form">
                <input type="hidden" name="action" value="upload">
                <input type="file" name="file" accept=".csv" required>
                <button type="submit" class="btn">Subir CSV</button>
            </form>
            <form method="post" style="margin-top:10px">
                <input type="hidden" name="action" value="generate">
                <button type="submit" class="btn btn-secondary">Usar datos de ejemplo</button>
            </form>
            <?php if ($files): ?>
                <h3>Archivos:</h3>
                <ul class="file-list">
                    <?php foreach ($files as $f): ?>
                        <li>
                            <a href="?file=<?= urlencode($f['path']) ?>" class="<?= $selected === $f['path'] ? 'active' : '' ?>">
                                <?= htmlspecialchars($f['name']) ?>
                            </a>
                            <span class="badge"><?= $f['type'] ?></span>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
        </section>
        <section class="card">
            <h2>2. Entrenar modelo</h2>
            <?php if ($preview): ?>
                <form method="post">
                    <input type="hidden" name="action" value="train">
                    <input type="hidden" name="csv_path" value="<?= htmlspecialchars($selected ?: $files[0]['path']) ?>">
                    <div class="form-group">
                        <label>Columna objetivo:</label>
                        <select name="target_col" class="target-select">
                            <option value="">Última columna</option>
                            <?php foreach ($preview['columns'] as $col): ?>
                                <option value="<?= htmlspecialchars($col) ?>"><?= htmlspecialchars($col) ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Entrenar</button>
                </form>
            <?php endif; ?>
        </section>
    </div>

    <?php if ($preview): ?>
        <section class="card">
            <h2>Vista previa</h2>
            <p class="dim"><?= $preview['shape'][0] ?> filas x <?= $preview['shape'][1] ?> columnas</p>
            <div class="table-wrapper">
                <table>
                    <thead><tr><?php foreach ($preview['columns'] as $c): ?><th><?= htmlspecialchars($c) ?></th><?php endforeach; ?></tr></thead>
                    <tbody>
                        <?php foreach ($preview['rows'] as $row): ?>
                            <tr><?php foreach ($preview['columns'] as $c): ?><td><?= htmlspecialchars($row[$c] ?? '') ?></td><?php endforeach; ?></tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </section>
    <?php endif; ?>

    <?php if ($model_info): ?>
        <section class="card">
            <h2>3. Resultados</h2>
            <div class="metrics">
                <?php foreach (['accuracy' => 'Accuracy', 'precision' => 'Precision', 'recall' => 'Recall', 'f1_score' => 'F1-Score'] as $k => $l): ?>
                    <div class="metric">
                        <span class="metric-value"><?= $model_info[$k] ?? '-' ?></span>
                        <span class="metric-label"><?= $l ?></span>
                    </div>
                <?php endforeach; ?>
            </div>
            <div class="actions">
                <a href="results.php" class="btn btn-secondary">Ver detalles</a>
                <a href="predict.php" class="btn btn-primary">Predecir</a>
            </div>
        </section>
    <?php endif; ?>
</div>
</body>
</html>
