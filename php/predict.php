<?php
// predict.php - Hacer predicciones
require_once __DIR__ . '/config.php';
$model_info = get_model_info();
if (!$model_info) { header('Location: index.php'); exit; }

$prediction = null;
$input_data = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = [];
    foreach ($model_info['feature_names'] as $feat) {
        $data[$feat] = $_POST[$feat] ?? '0';
    }
    $input_data = $data;
    $input_json = json_encode($data);
    try {
        $output = run_python('predict.py', [MODEL_DIR . '/model.pkl'], $input_json);
        $prediction = json_decode($output, true);
    } catch (Exception $e) {
        $error = $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predecir</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="container">
    <header>
        <h1>Hacer una predicción</h1>
        <a href="index.php" class="back-link">&larr; Volver</a>
    </header>
    <?php if (isset($error)): ?><div class="flash" style="background:#f8d7da;color:#721c24;"><?= htmlspecialchars($error) ?></div><?php endif; ?>
    <div class="grid-2col">
        <section class="card">
            <h2>Ingresa los datos</h2>
            <form method="post">
                <?php foreach ($model_info['feature_names'] as $feat): ?>
                    <div class="form-group">
                        <label><?= htmlspecialchars($feat) ?>:</label>
                        <input type="text" name="<?= htmlspecialchars($feat) ?>" value="<?= htmlspecialchars($input_data[$feat] ?? '') ?>" required>
                    </div>
                <?php endforeach; ?>
                <button type="submit" class="btn btn-primary">Predecir</button>
            </form>
        </section>
        <?php if ($prediction): ?>
            <section class="card">
                <h2>Resultado</h2>
                <div class="prediction-value <?= $prediction['prediction'] == 1 ? 'positive' : 'negative' ?>">
                    Clase: <strong><?= $prediction['prediction'] ?></strong>
                </div>
                <div class="probabilities">
                    <h3>Probabilidades:</h3>
                    <?php foreach ($prediction['classes'] as $i => $cls): ?>
                        <div class="prob-bar">
                            <span class="prob-label">Clase <?= $cls ?>:</span>
                            <div class="bar-container">
                                <div class="bar" style="width:<?= round($prediction['probabilities'][$i] * 100) ?>%;">
                                    <?= round($prediction['probabilities'][$i] * 100, 1) ?>%
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </section>
        <?php endif; ?>
    </div>
</div>
</body>
</html>
