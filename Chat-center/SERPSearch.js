const WebSocket = require('ws');
const readline = require('readline');
const SerpApi = require("google-search-results-nodejs");
const he = require('he'); // Import the 'he' library

const search = new SerpApi.GoogleSearch("2c8bcf321ec86cc70bc600644a1a22c9ac1cdaf04fc361096136ba1311d1470d"); // Replace with your actual API key

const ws = new WebSocket('ws://localhost:5000');

// Function to process user input and get Google Search results
async function processUserInput(inputText) {
  try {
    const searchQuery = inputText;
    const searchResults = await search.json({
      q: searchQuery
    }, (data) => {
      const formattedResults = getFormattedSearchResults(data); // Get formatted search results
      displaySearchResults(formattedResults); // Display and send search results
    });

  } catch (error) {
    console.error("Error occurred:", error);
    ws.send(JSON.stringify({ type: 'error', message: 'An error occurred: ' + error.message }));
  }
}

// Function to format search results as text
function getFormattedSearchResults(results) {
  let formattedResults = '';
  if (results.organic_results) {
    results.organic_results.forEach((result, index) => {
      formattedResults += `${index + 1}. ${decodeText(result.title)}\n`;
      formattedResults += `   ${decodeText(result.snippet)}\n`;
      formattedResults += `   ${result.link}\n\n`;
    });
  }
  return formattedResults;
}

// Function to display and send search results
function displaySearchResults(formattedResults) {
  console.log("Search Results:");
  console.log(formattedResults); // Display in console
  ws.send(JSON.stringify({ text: 'search_results', results: formattedResults })); // Send to server
  console.log("=================================");
}

// Function to decode HTML-encoded text
function decodeText(encodedText) {
  if (encodedText) {
    return he.decode(encodedText); // Use 'he' library to decode HTML-encoded text
  } else {
    return ''; // Return an empty string if encodedText is undefined
  }
}


// Function to process server messages
async function processServerMessage(message) {
  try {
    console.log("Server:", message.toString());
    await processUserInput(message.toString());

  } catch (error) {
    console.error("Error occurred in message handling:", error);
    ws.send(JSON.stringify({ type: 'error', message: 'An error occurred: ' + error.message }));
  }
}


ws.on('open', () => {
  console.log('Connected to server');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  function askUser() {
    rl.question('Enter a search query: ', (inputText) => {
      processUserInput(inputText);
      askUser();
      ws.send(JSON.stringify({ inputText }));
    });
  }

  askUser();
});

ws.on('message', async (message) => {
  await processUserInput(message.toString());
});
