const WebSocket = require('ws');
const readline = require('readline');
const { GradioChatBot } = require('gradio-chatbot');

// Create a WebSocket client that connects to the server
const ws = new WebSocket('ws://localhost:5000');

const bot = new GradioChatBot({
  url: 'https://huggingface.co/spaces/Open-Orca/OpenOrca-Preview1-GGML',
  fnIndex: 2,
});

// Function to process user input and bot response
async function processUserInput(inputText) {
  if (inputText.startsWith('/qna ')) {
    // Parse the input text as a QnA message
    const [question, passage] = inputText.substring(5).split('|').map((s) => s.trim());
    if (!question || !passage) {
      console.log('Invalid /qna command. Usage: /qna <question> | <passage>');
      return;
    }    
    // Use the bot's QnA method to get the answer
    const answer = await bot.qna(question, passage);
    console.log("Bot:", answer);
    // Send the QnA answer back to the server
    ws.send(JSON.stringify({ type: 'qna_response', answer }));
  } else {
    // Use the bot's chat method to get the chatbot response
    const response = await bot.chat(inputText);
    console.log("Bot:", response);
    // Send the chatbot response back to the server
    ws.send(JSON.stringify({ type: 'chatbot_response', response }));
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
      processUserInput(inputText);
      askUser(); // Recursive call to ask the user again for input
      ws.send(JSON.stringify({ inputText }));
    });
  }

  askUser(); // Start asking the user for input
});

// Listen for messages from the server
ws.on('message', (message) => {
  console.log("Server:", message.toString());

  // Use the bot.chat() method to send and receive messages from the chatbot model
  bot.chat(message.toString(), {
    onMessage: (msg) => {
      console.log("Bot:", msg);
    },
  });
});
