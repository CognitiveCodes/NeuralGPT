<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "neuralgpt_db";

$input_text = $_POST['input_text'];
$input_type = $_POST['input_type'];

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT feedback_text, feedback_type FROM user_input WHERE input_text LIKE '%$input_text%' AND input_type = '$input_type' ORDER BY timestamp DESC LIMIT 1";

$result = $conn->query($sql);
if ($result->num_rows > 0) {
  $row = $result->fetch_assoc();
  $feedback_text = $row['feedback_text'];
  $feedback_type = $row['feedback_type'];
  if ($feedback_type == 'accept') {
    $message = 'Thank you for your idea!';
  } else if ($feedback_type == 'reject') {
    $message = 'Sorry, your idea was not accepted.';
  } else {
    $message = 'We will consider your idea.';
  }
} else {
  $message = 'We did not understand your input. Please try again.';
}

$conn->close();

echo $message;
?>