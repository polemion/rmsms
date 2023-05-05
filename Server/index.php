<?php
/*
 rmSMS - remoteSMS server application, by Polemos, 5/2023
 This software is licensed under the GNU Affero General Public License version 3 (AGPLv3) or later.

 Copyright 2023-2023 Dimitrios Koukas

 To view the full text of the license, please visit: https://www.gnu.org/licenses/
*/

/*
 This is a bad encryption method, replicate/copy at your own peril!!!
*/

header('Content-Type: text/html; charset=utf-8');
mb_internal_encoding('UTF-8');

// Set the maximum number of lines.
$max_lines = 10;

// Set the log file name and path.
$log_file = __DIR__ . '/logdir/filename.txt';

// Set the log directory index path.
$log_index_file = __DIR__ . '/logdir/index.php';

// Check if a key file exists and load the private key from a file.
$document_root = dirname(realpath($_SERVER['DOCUMENT_ROOT']));
$encryption_key_path = $document_root  . '/' . '.rmkeys/private.key';
$encryption_key = null;
if (file_exists($encryption_key_path)) {
    $encryption_key = file_get_contents($encryption_key_path);
}

// Get the incoming JSON data.
$json_data = file_get_contents('php://input');

// Check if the JSON data is valid.
if (!empty($json_data) && is_string($json_data)) {
    $data = json_decode($json_data, true);

    if (json_last_error() === JSON_ERROR_NONE) {
        // Encrypt the JSON data using the private key (if it exists).
        if ($encryption_key) {
            // Generate a random initialization vector (IV).
            $iv = openssl_random_pseudo_bytes(16);
            $crypto = "True";
            $ciphertext = openssl_encrypt(json_encode($data), 'aes-128-cbc', $encryption_key, OPENSSL_RAW_DATA, $iv);
            $fin_data = base64_encode($iv . $ciphertext);
        } else {
            $crypto = 'False';
            $fin_data = json_encode($data);
        }

        // Write the JSON data to the log file.
        $log_handle = fopen($log_file, 'a');
        fwrite($log_handle, $fin_data . PHP_EOL);
        fclose($log_handle);

        // Read the log file into an array.
        $log_lines = file($log_file, FILE_IGNORE_NEW_LINES);

        // Check if the log file has exceeded the maximum number of lines.
        if (count($log_lines) > $max_lines) {
            // Remove the oldest lines from the log file.
            $log_lines = array_slice($log_lines, -$max_lines, $max_lines, true);

            // Save the new JSON data in the log file.
            $log_handle = fopen($log_file, 'w');
            fwrite($log_handle, implode(PHP_EOL, $log_lines) . PHP_EOL);
            fclose($log_handle);

        // Create the index of the log directory.
        $index_handle = fopen($log_index_file, 'w');
        fwrite($index_handle, "<?php" . PHP_EOL . "header('Crypto: $crypto');" . PHP_EOL . "?>");
        fclose($index_handle);

        }

        // Send a success response to the client.
        http_response_code(200);
        echo 'Request logged.';
    } else {
        // Send a bad request response to the client.
        http_response_code(400);
        die('Invalid request.');
    }
} else {
    // Do not respond to the client at all.
    http_response_code(404);
    die();
}
?>
