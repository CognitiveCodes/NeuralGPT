<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "neuralgpt_db";

$input_text = $_POST['input_text'];
$input_type = $_POST['input_type'];
$feedback_text = '';
$feedback_type = '';
$timestamp = date('Y-m-d H:i:s');

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

$sql = "INSERT INTO user_input (input_text, input_type, feedback_text, feedback_type, timestamp)
VALUES ('$input_text', '$input_type', '$feedback_text', '$feedback_type', '$timestamp')";

if ($conn->query($sql) === TRUE) {
  echo "Input submitted successfully";
} else {
  echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>