// Import required modules
const express = require('express');
const bodyParser = require('body-parser');
const { startTraining } = require('./train');

// Create a new Express app
const app = express();

// Parse request body as JSON
app.use(bodyParser.json());

// Define the endpoint for starting the training process
app.post('/train', async (req, res) => {
  // Get the hyperparameters from the request body
  const { epochs, batch_size, learning_rate } = req.body;

  // Start the training process with the given hyperparameters
  const result = await startTraining(epochs, batch_size, learning_rate);

  // Return the result as JSON
  res.json(result);
});

// Start the server
app.listen(3000, () => {
  console.log('Server started on port 3000');
});