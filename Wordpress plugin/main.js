jQuery(function($) {
  var socket = io('http://localhost:3001'); // Update the Socket.io server URL if needed

  // Send message on form submission
  $('#neuralgpt-chat-send').on('click', function(e) {
    e.preventDefault();
    var message = $('#neuralgpt-chat-input').val().trim();
    if (message !== '') {
      appendMessage('You', message);
      sendMessage(message);
      $('#neuralgpt-chat-input').val('');
    }
  });

  // Send message on pressing Enter key
  $('#neuralgpt-chat-input').on('keydown', function(e) {
    if (e.keyCode === 13) {
      e.preventDefault();
      $('#neuralgpt-chat-send').trigger('click');
    }
  });

  // Receive message from server and display
  socket.on('message', function(data) {
    var message = data.message;
    appendMessage('Chatbot', message);
  });

  // Function to send message to server
  function sendMessage(message) {
    $.ajax({
      url: ajax_object.ajax_url, // URL from localized script
      type: 'POST',
      data: {
        action: 'neuralgpt_chatbot',
        message: message,
      },
      dataType: 'json',
      success: function(response) {
        var message = response.message;
        appendMessage('Chatbot', message);
      },
      error: function(xhr, status, error) {
        console.error(error);
      }
    });
  }

  // Function to append a message to the chat log
  function appendMessage(sender, message) {
    var chatLog = $('#neuralgpt-chat-log');
    var messageHTML = '<div class="neuralgpt-chat-message">';
    messageHTML += '<strong>' + sender + ':</strong> ';
    messageHTML += message;
    messageHTML += '</div>';
    chatLog.append(messageHTML);
    chatLog.scrollTop(chatLog.prop('scrollHeight'));
  }
});
