const { z } = require('zod');
const { DataSource } = require('typeorm');
const { initializeAgentExecutorWithOptions } = require('langchain/agents');
const { Calculator } = require('langchain/tools/calculator');
const { DynamicStructuredTool } = require('langchain/tools');
const WebSocket = require('ws');
const readline = require('readline');
const { Cohere } = require('langchain/llms/cohere');
const { createSqlAgent, SqlToolkit } = require('langchain/agents/toolkits/sql');

// Create a WebSocket client that connects to the server
const ws = new WebSocket('ws://localhost:5000');

const model = new Cohere({
  maxTokens: 250,
  apiKey: '<PASTE COHERE API KEY>',
});

// Connect to your SQLite database
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('chat-hub.db');

// Initialize LangChain components (not directly relevant to SQLite)
const datasource = new DataSource({
  type: "sqlite",
  database: "chat-hub.db", // This line is not relevant for SQLite, update if needed
});

const toolkit = new SqlToolkit(db, model);
const executor = createSqlAgent(model, toolkit);

const tools = [
    new Calculator(), // Older existing single input tools will still work
    new DynamicStructuredTool({
      name: "random-number-generator",
      description: "generates a random number between two input numbers",
      schema: z.object({
        low: z.number().describe("The lower bound of the generated number"),
        high: z.number().describe("The upper bound of the generated number"),
      }),
      func: async ({ low, high }) =>
        (Math.random() * (high - low) + low).toString(), // Outputs still must be strings
      returnDirect: false, // This is an option that allows the tool to return the output directly
    }),
  ];

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
	const input = inputText;
        executor.call({ input })
          .then(response => {
            console.log("Bot:", response);
            const botMessage = JSON.stringify({ text: 'SQLAgent: ' + response });
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
      const input = message.toString();
      const response = await executor.call({ input });
  
      console.log("Bot:", response);
  
      const botMessage = JSON.stringify({ text: 'SQLAgent: ' + response });
      ws.send(botMessage);
    } catch (error) {
      console.error("Error occurred in message handling:", error);
      // Handle the error gracefully or take necessary actions.
      // For example, you can send an error message back to the server.
      ws.send(JSON.stringify({ type: 'error', message: 'An error occurred: ' + error.message }));
    }
  });

 