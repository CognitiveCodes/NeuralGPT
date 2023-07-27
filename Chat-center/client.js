const WebSocket = require('ws');
const readline = require('readline');

// Create a WebSocket client that connects to the server
const ws = new WebSocket('ws://localhost:5000');

// Listen for when the client connects to the server
ws.on('open', () => {
  console.log('Connected to server');

  // Start reading input from the user and sending messages to the server
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  rl.on('line', (inputText) => {
    if (inputText.startsWith('/qna ')) {
      // Parse the input text as a QnA message
      const [question, passage] = inputText.substring(5).split('|').map((s) => s.trim());
      if (!question || !passage) {
        console.log('Invalid /qna command. Usage: /qna <question> | <passage>');
        return;
      }

      // Send the QnA message to the server
      ws.send(JSON.stringify({ type: 'qna', question, passage }));
    } else {
      // Send a regular chat message to the server
      ws.send(JSON.stringify(('text:', inputText) ));
    }
  });
});

// Listen for messages from the server
ws.on('message', (message) => {
  console.log(message.toString());
});
