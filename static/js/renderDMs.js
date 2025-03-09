console.log("renderDMs.js loaded");

if (window.location.pathname.startsWith('/dm/')) {
  const url = window.location.href;
  const mainUrl = url.split('?')[0];
  const receiverHandle = mainUrl.substring(mainUrl.lastIndexOf('/') + 1);
  let dm_skip = 0;
  const dm_limit = 30;
  let hasSentRequest = false;

  async function loadMessages() {
    try {
      const response = await fetch(`/api/dm/${receiverHandle}?skip=${dm_skip}&limit=${dm_limit}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      console.log('Received data:', data);

      const messageContainer = document.getElementById('message-container');

      // Insert messages in chronological order
      data.messages.forEach(message => {
        if (!data.blocked_users.includes(message.sender_handle)) {
          // Check if the message already exists to avoid duplication
          if (!document.getElementById(`message-${message.id}`)) {
            const p = document.createElement('p');
            p.id = `message-${message.id}`;
            p.textContent = `${message.sender_handle}: ${message.content}`;
            messageContainer.appendChild(p);
          }
        }
      });

      // Handle loading more messages
      if (data.pagination.has_more) {
        dm_skip += dm_limit;
      } else {
        window.removeEventListener('scroll', handleScroll);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
      showErrorMessage(messageContainer);
    }
    hasSentRequest = false;
  }

  function showErrorMessage(container) {
    const errorMessage = document.createElement('p');
    errorMessage.textContent = 'Failed to load messages. Please try again later.';
    container.appendChild(errorMessage);
  }

  function handleScroll() {
    if (!hasSentRequest && window.innerHeight + window.scrollY >= document.body.offsetHeight-window.innerHeight/2) { 
      hasSentRequest = true;
      loadMessages();
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    hasSentRequest = true;
    loadMessages();
    window.addEventListener('scroll', handleScroll);
  });
}
