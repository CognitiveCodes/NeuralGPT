const WebSocket = require('ws');
const readline = require('readline');
const { GradioChatBot } = require('gradio-chatbot');

// Create a WebSocket client that connects to the server
const ws = new WebSocket('ws://localhost:5000');

const bot = new GradioChatBot({
  url: 'https://huggingface.co/spaces/tloen/alpaca-lora',
  endpoint: 'tloen-alpaca-lora.hf.space',
});

// Function to process user input and bot response
async function processUserInput(inputText) {
    try {
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
        bot.chat(inputText)
          .then(response => {
            console.log("Bot:", response);
            const botMessage = JSON.stringify({ text: 'AlpacaLoRA-client: ' + response });
            ws.send(botMessage);
            // Send the user message back to the server
            const userMessage = JSON.stringify({ text: 'user: ' + inputText });
            ws.send(userMessage);
          })
          .catch(error => {
            console.error("Error in bot.chat:", error);
            ws.send(JSON.stringify({ type: 'error', message: 'An error occurred: ' + error.message }));
          });
      }
    } catch (error) {
      console.error("Error occurred:", error);
      ws.send(JSON.stringify({ type: 'error', message: 'An error occurred: ' + error.message }));
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
ws.on('message', async (message) => {
    try {
      console.log("Server:", message.toString());
  
      // Use the bot.chat() method to send and receive messages from the chatbot model
      const response = await bot.chat(message.toString());
  
      console.log("Bot:", response);
  
      const botMessage = JSON.stringify({ text: 'AlpacaLoRA-client: ' + response });
      ws.send(botMessage);
    } catch (error) {
      console.error("Error occurred in message handling:", error);
      // Handle the error gracefully or take necessary actions.
      // For example, you can send an error message back to the server.
      ws.send(JSON.stringify({ type: 'error', message: 'An error occurred: ' + error.message }));
    }
  });
