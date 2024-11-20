document.addEventListener('htmx:afterRequest', function () {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll to the latest message
});
