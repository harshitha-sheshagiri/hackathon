const chat = document.getElementById('chat');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send');

const socket = new WebSocket('ws://localhost:8080');

socket.onmessage = function(event) {
    const message = document.createElement('div');
    message.textContent = event.data;
    chat.appendChild(message);
};

sendButton.addEventListener('click', function() {
    const message = messageInput.value;
    socket.send(message);
    messageInput.value = '';
});
