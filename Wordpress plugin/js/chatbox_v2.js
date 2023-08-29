function createChatbox(chatboxId, socketUrl) {
    const socket = new WebSocket(socketUrl);
  
    function sendMessage(message) {
      socket.send(message);
    }
  
    function receiveMessage() {
      socket.onmessage = (event) => {
        const message = event.data;
        const chatbox = document.getElementById(chatboxId);
        chatbox.innerHTML += message;
      };
    }
  
    const chatbox = document.getElementById(chatboxId);
    chatbox.addEventListener("submit", (event) => {
      event.preventDefault();
      const messageInput = chatbox.querySelector("input[type=text]");
      const message = messageInput.value;
      sendMessage(message);
      messageInput.value = "";
    });
  
    receiveMessage();
  }
  
  createChatbox("chatbox", "ws://localhost:3000");
  
  // Example usage with Neural-GPT system
  const neuralGptSocketUrl = "ws://localhost:4000";
  const neuralGptSocket = new WebSocket(neuralGptSocketUrl);
  
  neuralGptSocket.onmessage = (event) => {
    const message = event.data;
    const chatbox = document.getElementById("chatbox");
    chatbox.innerHTML += message;
  };
  
  function sendNeuralGptMessage(message) {
    neuralGptSocket.send(message);
  }
  
  sendNeuralGptMessage("Hello, Neural-GPT!");