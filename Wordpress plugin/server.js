 const http = require('http');
const server = http.createServer();
const io = require('socket.io')(server);

io.on('connection', (socket) => {
  console.log('A user connected');

  // Handle events from the client
  socket.on('chat message', (message) => {
    console.log('Received message:', message);
    // Process the message and send a response if needed
  });

  // Handle disconnection
  socket.on('disconnect', () => {
    console.log('A user disconnected');
  });
});

const port = 3001; // Specify the port number for your server
server.listen(port, () => {
  console.log(`Socket.io server listening on port ${port}`);
});
