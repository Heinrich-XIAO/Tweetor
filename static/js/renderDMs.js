if (window.location.pathname.startsWith('/dm/')) {
  const url = window.location.href;
  const mainUrl = url.split('?')[0];
  const receiverHandle = mainUrl.substring(mainUrl.lastIndexOf('/') + 1);
  let dm_skip = 0;
  const dm_limit = 30;
  let hasSentRequest = false;

  function formatTimestamp(timestamp) {
    const dt = new Date(timestamp.replace(" ", "T"));
    const now = new Date();
    function isSameDay(a, b) {
      return a.getFullYear() === b.getFullYear() &&
             a.getMonth() === b.getMonth() &&
             a.getDate() === b.getDate();
    }
    const yesterday = new Date();
    yesterday.setDate(now.getDate() - 1);
    
    const fullOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const fullDate = dt.toLocaleDateString(undefined, fullOptions) + " at " +
                     dt.toLocaleTimeString([], {hour: 'numeric', minute: '2-digit'});
    
    let display;
    if (isSameDay(dt, now)) {
      display = dt.toLocaleTimeString([], {hour: 'numeric', minute: '2-digit'});
    } else if (isSameDay(dt, yesterday)) {
      display = "Yesterday";
    } else if (dt.getFullYear() === now.getFullYear()) {
      display = dt.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } else {
      const yearsAgo = now.getFullYear() - dt.getFullYear();
      display = yearsAgo === 1 ? "1 year ago" : yearsAgo + ' years ago';
    }
    return { display, full: fullDate };
  }

  // Add helper function to render a message
  function renderMessage(message, prepend = false) {
    // Get container and check if message already exists
    const messageContainer = document.getElementById('message-container');
    if (!messageContainer || document.getElementById(`message-${message.id}`)) return;
  
    const p = document.createElement('p');
    p.id = `message-${message.id}`;
    
    const timestampData = formatTimestamp(message.timestamp);
    const timestampSpan = document.createElement('span');
    timestampSpan.textContent = timestampData.display;
    timestampSpan.title = timestampData.full;
    timestampSpan.classList.add('dm-timestamp');
    // Unified styling for new messages
    timestampSpan.style.fontWeight = 'lighter';
    timestampSpan.style.marginLeft = '10px';
    p.appendChild(timestampSpan);
    
    const b = document.createElement('b');
    b.textContent = message.sender_handle;
    p.appendChild(b);
    
    const spaceSpan = document.createElement('span');
    spaceSpan.textContent = ' ';
    p.appendChild(spaceSpan);
    
    const contentSpan = document.createElement('span');
    contentSpan.textContent = message.content;
    p.appendChild(contentSpan);
  
    if (prepend) {
      messageContainer.prepend(p);
    } else {
      messageContainer.appendChild(p);
    }
  }

  async function loadMessages() {
    try {
      const response = await fetch(`/api/dm/${receiverHandle}?skip=${dm_skip}&limit=${dm_limit}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      const messageContainer = document.getElementById('message-container');

      data.messages.forEach(message => {
        if (!data.blocked_users.includes(message.sender_handle)) {
          renderMessage(message);
        }
      });

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

    const sendMessageForm = document.getElementById('send-message-form');
    if (sendMessageForm) {
      sendMessageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(sendMessageForm);
        try {
          sendMessageForm.reset();
          const response = await fetch(sendMessageForm.action, {
            method: 'POST',
            body: formData
          });
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          const data = await response.json();
          renderMessage(data, true);
        } catch (error) {
          console.error('Error sending message:', error);
        }
      });
    }

    // Socket listener for new direct messages
    socket.on('new_dm', (message) => {
      const messageContainer = document.getElementById('message-container');
      if (!messageContainer) return;
      
      renderMessage(message, true);
      
      const redDot = document.getElementById(`red-dot-${message.sender_handle}`);
      if (redDot) {
        redDot.style.display = 'block';
        document.addEventListener('click', () => {
          redDot.style.display = 'none';
        }, { once: true });
      }

      // Show desktop notification
      if (Notification.permission === 'granted') {
        new Notification(`${message.sender_handle+' '}said ...`, { body: message.content });
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            new Notification(`${message.sender_handle} said ...`, { body: message.content });
          }
        });
      }
    });
  });
}
