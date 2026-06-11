<?php
// config.php - Configuración para la versión PHP
define('BASE_DIR', dirname(__DIR__));
define('DATA_DIR', BASE_DIR . '/data');
define('UPLOAD_DIR', DATA_DIR . '/uploads');
define('MODEL_DIR', DATA_DIR . '/models');
define('PYTHON_DIR', BASE_DIR . '/python');
define('SAMPLE_CSV', DATA_DIR . '/sample.csv');
define('PYTHON_BIN', 'python');
// Múltiples intentos para encontrar Python en el servidor
$python_candidates = ['python3', 'python', 'py'];
foreach ($python_candidates as $candidate) {
    $out = null; $code = null;
    exec("$candidate --version 2>&1", $out, $code);
    if ($code === 0) { define('PYTHON', $candidate); break; }
}
if (!defined('PYTHON')) define('PYTHON', 'python');

foreach ([DATA_DIR, UPLOAD_DIR, MODEL_DIR] as $dir) {
    if (!is_dir($dir)) mkdir($dir, 0777, true);
}

function run_python($script, $args = [], $stdin = null) {
    $script_path = PYTHON_DIR . '/' . $script;
    $cmd = PYTHON . ' ' . escapeshellarg($script_path);
    foreach ($args as $a) $cmd .= ' ' . escapeshellarg($a);
    if ($stdin !== null) {
        $descriptorspec = [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']];
        $proc = proc_open($cmd, $descriptorspec, $pipes);
        if (is_resource($proc)) {
            fwrite($pipes[0], $stdin);
            fclose($pipes[0]);
            $output = stream_get_contents($pipes[1]);
            fclose($pipes[1]);
            proc_close($proc);
            return trim($output);
        }
        throw new Exception("Error ejecutando Python");
    }
    $output = shell_exec($cmd . ' 2>&1');
    if ($output === null) throw new Exception("Error ejecutando Python");
    return trim($output);
}

function get_csv_preview($path, $n = 5) {
    if (!file_exists($path)) return null;
    $lines = file($path, FILE_IGNORE_NEW_LINES);
    if (!$lines) return null;
    $headers = str_getcsv(array_shift($lines));
    $rows = [];
    foreach (array_slice($lines, 0, $n) as $line) {
        $vals = str_getcsv($line);
        $row = [];
        foreach ($headers as $i => $h) $row[$h] = $vals[$i] ?? '';
        $rows[] = $row;
    }
    return ['columns' => $headers, 'rows' => $rows, 'shape' => [count($lines), count($headers)]];
}

function get_model_info() {
    $path = MODEL_DIR . '/results.json';
    return file_exists($path) ? json_decode(file_get_contents($path), true) : null;
}

function list_csv_files() {
    $files = [];
    if (file_exists(SAMPLE_CSV))
        $files[] = ['name' => 'sample.csv', 'path' => realpath(SAMPLE_CSV), 'type' => 'Ejemplo'];
    if (is_dir(UPLOAD_DIR)) {
        foreach (scandir(UPLOAD_DIR) as $f) {
            if (pathinfo($f, PATHINFO_EXTENSION) === 'csv')
                $files[] = ['name' => $f, 'path' => realpath(UPLOAD_DIR . '/' . $f), 'type' => 'Subido'];
        }
    }
    return $files;
}
