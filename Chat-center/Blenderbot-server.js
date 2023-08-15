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
async function askQuestion(question) {
  try {
    // Get the last 10 messages from the database
    const messages = await new Promise((resolve, reject) => {
      db.all(`SELECT * FROM messages ORDER BY timestamp DESC LIMIT 20`, (err, rows) => {
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
    messages.forEach((message, i) => {
      if (i % 2 === 0) {
        pastUserInputs.push(message.message);
      } else {
        generatedResponses.push(message.message);
      }
    });

    // Send the question to the chatbot and get the response
    const response = await fetch(
      "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer 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",
        },
        body: JSON.stringify({
          inputs: {
            text: question,
            past_user_inputs: pastUserInputs,
            generated_responses: generatedResponses,
          },
          full_source: false,
        }),
      }
    );
    console.log(response);
    const responseJson = await response.json();
    const outputText = responseJson.generated_text;

    // Decode the outputText from the JSON file
    const decodedOutputText = decodeURIComponent(JSON.parse(`"${outputText}"`));
    return decodedOutputText;
  } catch (error) {
    console.error(error);
  }
}

   
    // Use the handleMessage function as a callback for incoming messages
// Use the handleMessage function as a callback for incoming messages
const wss = new WebSocket.Server({ server });
wss.on('connection', (ws) => {
  console.log('New connection');

  // Send a welcome message to the client
  ws.send('Hello! Please integrate yourself wuith the local sql database and file system');

  // Handle incoming messages from the client
  ws.on('message', async (message) => {
    console.log(`Received message: ${message}`);

    updateInputTextArea(message);

    // Parse the message as a JSON object
    const parsedMessage = JSON.parse(message);

    // Extract the message text from the "text" property, or use an empty string if the property is missing
    const messageText = parsedMessage.text || '';

    // Store the message in the database
    const timestamp = new Date().toISOString();
    const sender = 'client';
    db.run(`INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)`, [sender, messageText, timestamp], (err) => {
      if (err) {
        console.error(err);
      }
    });

    try {
      // Use the askQuestion function to generate a response from the input message
      if (parsedMessage.text) { // <-- Check for the presence of the "text" property
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
    }
  });  
});
 
