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

  async function loadMessages() {
    try {
      const response = await fetch(`/api/dm/${receiverHandle}?skip=${dm_skip}&limit=${dm_limit}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();

      const messageContainer = document.getElementById('message-container');

      // Insert messages in chronological order
      data.messages.forEach(message => {
        if (!data.blocked_users.includes(message.sender_handle)) {
          // Check if the message already exists to avoid duplication
          if (!document.getElementById(`message-${message.id}`)) {
            const p = document.createElement('p');
            p.id = `message-${message.id}`;
 
            const timestampData = formatTimestamp(message.timestamp);
            const timestampSpan = document.createElement('span');
            timestampSpan.style.fontWeight = 'lighter';
            timestampSpan.style.marginLeft = '10px';
            timestampSpan.classList.add('dm-timestamp');
            timestampSpan.textContent = timestampData.display;
            timestampSpan.title = timestampData.full;
            p.appendChild(timestampSpan);
            
            
            const b = document.createElement('b');
            b.textContent = message.sender_handle;
            p.appendChild(b);
            
            // Use a span for the colon and space, then a separate span for the message content.
            const spaceSpan = document.createElement('span');
            spaceSpan.textContent = ' ';
            p.appendChild(spaceSpan);
            
            const contentSpan = document.createElement('span');
            contentSpan.textContent = message.content;
            p.appendChild(contentSpan);
           
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

    const sendMessageForm = document.getElementById('send-message-form');
    if (sendMessageForm) {
      sendMessageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(sendMessageForm);
        try {
          const response = await fetch(sendMessageForm.action, {
            method: 'POST',
            body: formData
          });
          sendMessageForm.reset();
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          const data = await response.json();
          const messageContainer = document.getElementById('message-container');
          const p = document.createElement('p');
          p.id = `message-${data.id}`;
          
          const timestampData = formatTimestamp(data.timestamp);
          const timestampSpan = document.createElement('span');
          timestampSpan.style.fontWeight = 'lighter';
          timestampSpan.style.marginLeft = '10px';
          timestampSpan.classList.add('dm-timestamp');
          timestampSpan.textContent = timestampData.display;
          timestampSpan.title = timestampData.full;
          p.appendChild(timestampSpan);
          
          const b = document.createElement('b');
          b.textContent = data.sender_handle;
          p.appendChild(b);
          
          const spaceSpan = document.createElement('span');
          spaceSpan.textContent = ' ';
          p.appendChild(spaceSpan);
          
          const contentSpan = document.createElement('span');
          contentSpan.textContent = data.content;
          p.appendChild(contentSpan);
          
          messageContainer.prepend(p);
        } catch (error) {
          console.error('Error sending message:', error);
        }
      });
    }
  });
}
