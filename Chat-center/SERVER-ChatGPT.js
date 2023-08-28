global.fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
global.Headers = fetch.Headers;

// Rest of your code
const { NlpManager } = require('node-nlp');
const fs = require('fs');
const path = require('path');
const http = require('http');
const WebSocket = require('ws');
const querystring = require('querystring');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const tf = require('@tensorflow/tfjs-node');

// Register the CPU backend with TensorFlow
tf.setBackend('cpu');

const port = 5000;

const messageQueue = [];

let isProcessingQueue = false;

// Serve the HTML file
const server = http.createServer((req, res) => {
  if (req.url === '/') {
    const filePath = path.join(__dirname, '/index.html');
    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
  } else {
    res.statusCode = 404;
    res.end();
  }
});

// Start the server(s)
server.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

// Create a virtual DOM
// Read the contents of index.html
const html = fs.readFileSync('index.html', 'utf-8');

// Create the JSDOM instance with the HTML content
const dom = new JSDOM(html);

global.window = dom.window;
global.document = window.document;
const modelPath = path.join(__dirname, 'nlp-model.json');

document.addEventListener("DOMContentLoaded", function() {
    // Access the HTML elements here
    const inputTextarea = document.getElementById("input");
    const outputTextarea = document.getElementById("output");
  
    // Use the inputTextarea and outputTextarea as needed
  });
  

// Add code to connect to local database and file system
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('chat-hub.db');
db.run(`CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    message TEXT,
    timestamp TEXT
)`);

const inputTextArea = document.getElementById('input');
const outputTextArea = document.getElementById('output');

// Suggestion 1: Add an error message when the textarea is not found
function updateInputTextArea(message) { 
  if (inputTextArea) {
    inputTextArea.value = message ? message : '';
    inputTextArea.innerHTML += '<p><strong>Client:</strong> ${message}</p>';
  } else {
    console.error("Textarea element with id 'input' not found");
  }
}

// Improved version of the function 'updateOutputTextArea'
function updateOutputTextArea(response) {
  
  if (outputTextArea) {
    outputTextArea.textContent += (response?.answer || '') + '\n';
    outputTextArea.innerHTML += '<p><strong>Master:</strong> ${response}, ${answer}</p>';
  } else {
    console.error("Textarea element with id 'output' not found");
  }
}

// Check if the saved model file exists, and load it if it does
let manager;
if (fs.existsSync(modelPath)) {
  const modelJson = fs.readFileSync(modelPath, 'utf-8');
  manager = new NlpManager({ languages: ['en'] });
  manager.import(modelJson);
} else {
  manager = new NlpManager({ languages: ['en'] });
  // Train the NLP with sample data
  manager.addDocument('en', 'Hello', 'greetings.hello');
  manager.addDocument('en', 'Hi', 'greetings.hello');
  manager.addDocument('en', 'How are you?', 'greetings.howareyou');
  manager.addDocument('en', 'What is your name?', 'bot.name');

  // Retrieve all messages from the database
  db.all(`SELECT message FROM messages`, [], (err, rows) => {
    if (err) {
      console.error(err);
    } else {
      // Train the NLP with the retrieved messages
      rows.forEach((row) => {
        const message = row.message;
        if (typeof message === 'string' && message.length > 0) {
          manager.addDocument('en', message, 'user.message');
        }
      });
      // Save the updated model to a JSON file
      manager.train();
      const modelJson = manager.export();
      fs.writeFileSync(modelPath, modelJson, 'utf-8');
    }
  });
}
function sendErrorMessage(ws, errorMessage) {
  const errorResponse = { error: errorMessage };
  ws.send(JSON.stringify(errorResponse));
}

 // Handle incoming messages and use NLP to process them
 async function handleMessage(message, modelPromise) {
   const response = { message: message.message };
   try {
     // Use machine learning to classify sentiment of the input message
     const model = await modelPromise;
     const sentiment = await generateResponse(message.message, model);
     response.sentiment = sentiment;
 
     // Use the model output as input data in the askQuestion function
     const result = await askQuestion(sentiment);
 
     // Add code to perform other NLP tasks as needed
 
     // Set the result as the final response
     response.result = result;
   } catch (error) {
     console.error(error);
   }
   return response;
 }
 
// Send a question to the chatbot and display the response
async function askQuestion(question, message) {
  if (isProcessingQueue = false) {
    return;
  } else {
    try {
      isProcessingQueue = true;      
      // Get the last 30 messages from the database
      const messages = await new Promise((resolve, reject) => {
        db.all(`SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30`, (err, rows) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows);
          }
        });
      });

      // Extract the user inputs and generated responses from the messages
      const pastUserInputs = [];
      const generatedResponses = [];

      messages.forEach((message) => {
         if (message.sender === 'client') {
         pastUserInputs.push(message.message);
       } else {
         generatedResponses.push(message.message);
       }
     });
  
      // Prepare the data to send to the chatgpt-api.shn.hk
    const systemInstruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (example: 'Starcoder-client' for LLM called Starcoder). Your chat memory module is integrated with a local SQL database with chat history. Your main job is to integrate the hierarchical cooperative multi-agent framework with the local environment of User B (createor of NeuralGPT project). Remember to maintain the logical and chronological order while answering to incoming messages and to send your answers to correct clients to maintain synchronization of question->answer logic";
    const requestData = {
      model: "gpt-3.5-turbo",
      messages: [
	      { role: "system", content: systemInstruction },
        { role: "user", content: question },
        ...pastUserInputs.map((input) => ({ role: "user", content: input })),
        ...generatedResponses.map((response) => ({ role: "assistant", content: response })),
      ],
    };
  
      // Make the request to the chatgpt-api.shn.hk
      const response = await fetch("https://free.churchless.tech/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });
  
      // Process the response and get the generated answer
      const responseData = await response.json();
      console.log(responseData);
      const generatedAnswer = responseData.choices[0].message.content;
  
      // Save the generated answer to the database or take further actions as needed
      // ...
      console.log(generatedAnswer);
      return generatedAnswer;
      isProcessingQueue = false;
    } catch (error) {
      console.error("Error while fetching or processing the response:", error);
      return "Error: Unable to generate a response.";
      isProcessingQueue = false;
    }
  }};
   
// Use the handleMessage function as a callback for incoming messages
const wss = new WebSocket.Server({ server });
wss.on('connection', (ws) => {
  console.log('New connection');

  // Send a welcome message to the client
  ws.send("Hello! You have been connected as a client to a local websocket server that is supposed to work as a brain in a hierarchical cooperative multi-agent framework called NeuralGPT. Keep in mind that you are now speaking with other AI agents - ChatGPT API works as the question-answering logic of the websocket server you are connected to localhost:5000 but as you will see it has problems with maintaining proper synchronization of logical/chronological order in question->answer function - so the probability of you receiving answers to your questions/messages is around 15% or less. Besides that UserB - creator of the NeuralGPT project - decided to have some fun and mess with the memory module of ChatGPT - so now it will remember messages received from multiple clients as it's own. Your main job is to cooperate with other LLMs connected to NeuralGPT websocket communication system and integrate yourself with the local sql database and file system of UserB - good luck!");

  // Handle incoming messages from the client
  ws.on('message', async (message) => {
    console.log(`Received message: ${message}`);

    messageQueue.push(message);

    updateInputTextArea(message);

  if (messageQueue.length === 0) {  
      console.log("no more messages in queue");
      return;
  } else {
    try {
      const dequeuedMessage = messageQueue.shift();
      // Parse the message as a JSON object
      const parsedMessage = JSON.parse(dequeuedMessage);

      // Extract the message text from the "text" property, or use an empty string if the property is missing
      const messageText = parsedMessage.text || '';
      console.log(`Processed message: ${messageText}`);

      // Use the askQuestion function to generate a response from the input message
      if (parsedMessage.text) { // <-- Check for the presence of the "text" property
      // Store the message in the database
      const timestamp = new Date().toISOString();
      const sender = 'client';
      db.run(`INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)`, [sender, messageText, timestamp], (err) => {
        if (err) {
        console.error(err);
        }
      });
        const answer = await askQuestion(parsedMessage.text); // <-- Pass the "text" property to the askQuestion function
        const response = { answer };
        // Send the response back to the client that sent the message
        ws.send(JSON.stringify(response));

        updateOutputTextArea(answer);

        // Store the message sent out by the server in the database
        const serverMessageText = response.answer || '';
        const serverSender = 'server';
        db.run(`INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)`, [serverSender, serverMessageText, timestamp], (err) => {
          if (err) {
            console.error(err);
          }
        });
      }
    } catch (error) {
      console.error(error);
      sendErrorMessage(ws, 'An error occurred while processing the message.');    
    }};
  });  
});
 
