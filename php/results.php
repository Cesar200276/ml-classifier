<?php
// results.php - Resultados detallados
require_once __DIR__ . '/config.php';
$model_info = get_model_info();
if (!$model_info) { header('Location: index.php'); exit; }
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultados del Modelo</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="container">
    <header>
        <h1>Resultados del Modelo</h1>
        <a href="index.php" class="back-link">&larr; Volver</a>
    </header>
    <section class="card">
        <h2>Métricas</h2>
        <div class="metrics">
            <?php foreach (['accuracy' => 'Accuracy', 'precision' => 'Precision', 'recall' => 'Recall', 'f1_score' => 'F1-Score'] as $k => $l): ?>
                <div class="metric">
                    <span class="metric-value"><?= $model_info[$k] ?? '-' ?></span>
                    <span class="metric-label"><?= $l ?></span>
                </div>
            <?php endforeach; ?>
        </div>
    </section>
    <section class="card">
        <h2>Matriz de confusión</h2>
        <?php if (isset($model_info['confusion_matrix'])): $cm = $model_info['confusion_matrix']; ?>
            <table class="confusion-matrix">
                <tr><td></td><th>Pred: Neg</th><th>Pred: Pos</th></tr>
                <tr><th>Real: Neg</th><td class="cm-tn"><?= $cm[0][0] ?></td><td class="cm-fp"><?= $cm[0][1] ?></td></tr>
                <tr><th>Real: Pos</th><td class="cm-fn"><?= $cm[1][0] ?></td><td class="cm-tp"><?= $cm[1][1] ?></td></tr>
            </table>
        <?php endif; ?>
    </section>
    <section class="card">
        <h2>Detalles</h2>
        <ul class="info-list">
            <li><strong>Muestras:</strong> <?= $model_info['n_samples'] ?? '-' ?></li>
            <li><strong>Features:</strong> <?= $model_info['n_features'] ?? '-' ?></li>
            <li><strong>Target:</strong> <?= $model_info['target_column'] ?? '-' ?></li>
            <li><strong>Clases:</strong> <?= isset($model_info['classes']) ? implode(', ', $model_info['classes']) : '-' ?></li>
        </ul>
    </section>
    <a href="predict.php" class="btn btn-primary">Hacer predicción</a>
</div>
</body>
</html>
