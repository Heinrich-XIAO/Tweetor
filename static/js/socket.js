const socket = io({
  transports: ['websocket']
});

function showNotification(message) {
  new Notification(`${message.sender_handle + ' '}said ...`, {
    body: `${message.content}`,
  });
}

socket.on('new_dm', (message) => {
  if (Notification.permission === 'granted') {
    showNotification(message);
  } else if (Notification.permission !== 'denied') {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        showNotification(message);
      }
    });
  }
});
