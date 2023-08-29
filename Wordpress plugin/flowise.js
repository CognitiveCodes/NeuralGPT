// main.js

// Initialize FlowiseAI chatbot
import Chatbot from "https://cdn.jsdelivr.net/npm/flowise-embed@latest/dist/web.js";
Chatbot.init({
    chatflowid: "d196feb4-7375-4328-9f39-a3dfdef9a3f4",
    apiHost: "http://localhost:3000",
    onMessage: function (message) {
        if (message.type == 'text' && message.text) {
            var input_text = message.text.trim();
            var input_type = 'suggest'; // or 'accept' or 'reject' depending on user input
            $.ajax({
                url: 'get_feedback.php',
                type: 'POST',
                data: { input_text: input_text, input_type: input_type },
                success: function (response) {
                    Chatbot.sendMessage(response);
                },
                error: function (xhr, status, error) {
                    console.log(error);
                }
            });
        }
    }
});

// Handle user input
const form = document.getElementById("input-form");
const input = document.getElementById("input-field");
const messages = document.getElementById("messages");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (text) {
    // Add user message to chat
    messages.innerHTML += `<div class="message user">${text}</div>`;
    // Send user message to FlowiseAI chatbot
    Chatbot.send(text).then((response) => {
      // Add chatbot message to chat
      messages.innerHTML += `<div class="message chatbot">${response.text}</div>`;
      // Handle chatbot actions (proposing/accepting/rejecting ideas)
      if (response.actions) {
        response.actions.forEach((action) => {
          if (action.type === "proposal") {
            // Display chatbot proposal to user
            messages.innerHTML += `<div class="message chatbot">${action.text}</div>`;
          } else if (action.type === "acceptance") {
            // Handle user acceptance of chatbot proposal
            // (e.g. call a function to execute the accepted idea)
            handleAcceptance(action.text);
          } else if (action.type === "rejection") {
            // Handle user rejection of chatbot proposal
            // (e.g. call a function to propose a different idea)
            handleRejection(action.text);
          }
        });
      }
      // Scroll to bottom of chat
      messages.scrollTop = messages.scrollHeight;
    });
    // Clear input field
    input.value = "";
  }
});

// Helper functions for handling chatbot actions
function handleAcceptance(text) {
  console.log(`User accepted: ${text}`);
  // TODO: Implement logic for executing the accepted idea
}

function handleRejection(text) {
  console.log(`User rejected: ${text}`);
  // TODO: Implement logic for proposing a different idea
}
css
Copy code

/* style.css */

body {
  margin: 0;
  padding: 0;
  font-family: sans-serif;
}

#app {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

#header {
  margin-bottom: 2rem;
}

#chatbot {
  width: 100%;
  max-width: 600px;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  overflow: hidden;
}

#messages {
  height: 300px;
  overflow-y: scroll;
  padding: 1rem;
}

.message {
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
}

.user {
  background-color: #f2f2f2;
  text-align: right;
}

.chatbot {
  background-color: #e6e6e6;
  text-align: left;
}

#input-form {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  background-color: #f2f2f2;
}

#input-field {
  flex-grow: 1;
  margin-right: 1rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: none;
}

button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: none;
  background-color: #4caf50;
  color: white;
  font-weight: bold;
  cursor: pointer;
}

button:hover {
  background-color: #3e8e41;
}