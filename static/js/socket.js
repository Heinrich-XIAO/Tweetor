const socket = io({
  transports: ['websocket']
});

function showNotification(message) {
  new Notification(`${message.sender_handle + ' '}said ...`, {
    body: `${message.content}`,
  });
}
