var chatWindow = document.createElement("div");
chatWindow.id = "chat-window";
document.body.appendChild(chatWindow);
var chatInput = document.createElement("input");
chatInput.type = "text";
chatInput.id = "chat-input";
chatWindow.appendChild(chatInput);
var chatButton = document.createElement("button");
chatButton.innerHTML = "Send";
chatButton.onclick = function() {
 var message = document.getElementById("chat-input").value;
 document.getElementById("chat-input").value = "";
 sendMessage(message);
}
chatWindow.appendChild(chatButton);
var chatLog = document.createElement("div");
chatLog.id = "chat-log";
chatWindow.appendChild(chatLog);
function sendMessage(message) {
 var xhr = new XMLHttpRequest();
 xhr.onreadystatechange = function() {
 if (xhr.readyState === 4 && xhr.status === 200) {
 var response = JSON.parse(xhr.responseText);
 addMessage(response.message, "bot");
 }
 }
 xhr.open("POST", "/wp-admin/admin-ajax.php?action=neuralgpt_chat", true);
 xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
 xhr.send("message=" + message);
}
function addMessage(message, sender) {
 var messageElement = document.createElement("div");
 messageElement.innerHTML = message;
 messageElement.className = "message " + sender;
 chatLog.appendChild(messageElement);
}