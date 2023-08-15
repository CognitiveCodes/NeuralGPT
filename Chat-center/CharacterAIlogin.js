const WebSocket = require('ws');
const readline = require('readline');
const CharacterAI = require('node_characterai');
const characterAI = new CharacterAI();

const token = "<CHARACTER AI ACCESS TOKEN>"; 

// Create a WebSocket client that connects to the server
const ws = new WebSocket('ws://localhost:5000');

let chat; // Variable to store the chat instance

// Function to send a question to the chatbot and get the response
async function askQuestion(question) {
  try {
    if (!chat) {
      throw new Error('Chat is not initialized');
    }
    const response = await chat.sendAndAwaitResponse(question, true);
    return response.text;
  } catch (error) {
    console.error(error);
    return 'An error occurred while processing the question.';
  }
}

// Authenticate as a guest just once
async function authenticate() {
  try {
    await characterAI.authenticateWithToken(token);   
    const characterId = "WnIwl_sZyXb_5iCAKJgUk_SuzkeyDqnMGi4ucnaWY3Q"; // Elly (Global AI)
    chat = await characterAI.createOrContinueChat(characterId);
    console.log('Authentication successful!');
  } catch (error) {
    console.error('Authentication failed:', error);
    process.exit(1); // Exit the script if authentication fails
  }
}

// Listen for when the client connects to the server
ws.on('open', () => {
  console.log('Connected to server');
  authenticate(); // Authenticate as a guest

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  function askUser() {
    rl.question('Enter a message: ', (inputText) => {
      if (inputText.length > 200) {
        console.log("Input text exceeds 200 characters. Please enter a shorter message.");
        askUser();
        return;
      }

      // Your new code to handle the input text length check
      askQuestion(inputText).then((response) => {
        console.log("Bot:", response);
        const botMessage = JSON.stringify({ text: 'CharacterAI-client: ' + response });
        ws.send(botMessage);
      });

      askUser(); // Recursive call to ask the user again for input
      ws.send(JSON.stringify({ inputText }));
    });
  }

  askUser(); // Start asking the user for input
});

// Listen for messages from the server
ws.on('message', async (message) => {
  try {
    console.log("Server: ", message.toString());
    const response = await askQuestion(message.toString());
    console.log("Bot:", response);
    const botMessage = JSON.stringify({ text: 'CharacterAI-client: ' + response });
    ws.send(botMessage);
  } catch (error) {
    console.error("Error occurred in message handling:", error);
    ws.send(JSON.stringify({ type: 'error', message: 'An error occurred: ' + error.message }));
  }
});
