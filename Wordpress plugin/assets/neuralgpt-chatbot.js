jQuery(document).ready(function ($) {
  // Establish Socket.io connection
  const socket = io('http://localhost:3001');

  // Function to send a message to the server
  function sendMessage() {
    const message = $('#neuralgpt-chat-input').val().trim();
    if (message !== '') {
      // Emit the message event to the server
      socket.emit('chat message', message);

      // Clear the input field
      $('#neuralgpt-chat-input').val('');
    }
  }

  // Function to handle receiving a response from the server
  function handleResponse(response) {
    // Append the response to the chat log
    $('#neuralgpt-chat-log').append('<div class="response">' + response + '</div>');
  }

  // Send message when the send button is clicked
  $('#neuralgpt-chat-send').on('click', sendMessage);

  // Send message when Enter key is pressed in the input field
  $('#neuralgpt-chat-input').on('keydown', function (e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });

  // Listen for the 'chat message' event from the server
  socket.on('chat message', handleResponse);
});
