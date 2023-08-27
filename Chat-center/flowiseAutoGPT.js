const WebSocket = require('ws');
const readline = require('readline');
const fetch = require('node-fetch');

// Create a WebSocket client that connects to the server
const ws = new WebSocket('ws://localhost:5000');

// Function to process user input and bot response
async function askQuestion(question) {
  try {
    // Use the bot's chat method to get the chatbot response
    const response = await fetch('https://flowiseai-flowise.hf.space/api/v1/prediction/284a4d16-e366-43e3-b9ea-6bd9a6c63524', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
              },
      body: JSON.stringify({ "question": question }),
    });

    const result = await response.json();
    console.log(result);
    // Convert the JSON object into a formatted string
    const responseString = JSON.stringify(result, null, 2);
    console.log(responseString);

    // Send the chatbot response back to the server
    ws.send(JSON.stringify({ text: 'Flowise-AutoGPT:' + responseString }));
  } catch (error) {
    console.error(error);
  }
}

// Listen for when the client connects to the server
ws.on('open', () => {
  console.log('Connected to server');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  function askUser() {
    rl.question('Enter a message: ', (inputText) => {
      askQuestion(inputText);
      askUser(); // Recursive call to ask the user again for input
      ws.send(JSON.stringify({ text: 'UserB:' + inputText }));
    });
  }

  askUser(); // Start asking the user for input
});

// Listen for messages from the server
ws.on('message', (message) => {
  console.log("Server:", message.toString());

  // Use the askQuestion method to send and receive messages from the chatbot model
  askQuestion(message.toString(), {
    onMessage: (msg) => {
      console.log("Bot:", msg);
    },
  });
});
