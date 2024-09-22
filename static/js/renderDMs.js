console.log("renderDMs.js loaded");


const url = window.location.href;
const mainUrl = url.split('?')[0];
const receiverHandle = mainUrl.substring(mainUrl.lastIndexOf('/') + 1);
const dm_skip = 0;
const dm_limit = 10;
const dm_inc = 10;

async function loadMessages() {
    try {
        const response = await fetch(`/api/dm/${receiverHandle}?skip=${dm_skip}&limit=${dm_limit}`);
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        console.log('Received data:', data);

        const messageContainer = document.getElementById('message-container');
        messageContainer.innerHTML = '';

        // Insert messages in chronological order
        data.messages.forEach(message => {
            if (message.sender_handle !== receiverHandle && !data.blocked_users.includes(message.sender_handle)) {
                const p = document.createElement('p');
                p.textContent = `${message.sender_handle}: ${message.content}`;
                messageContainer.appendChild(p);
            }
        });

        // Update pagination info
        updatePaginationInfo(data);

        // Handle pagination
        if (data.pagination.has_more) {

            const nextBtn = document.getElementById('next-btn');
            nextBtn.style.display = 'inline-block';
        } else {
            hideNextButton();
        }

        // Handle going back
        if (dm_skip > -1) {
            const prevBtn = document.getElementById('prev-btn');
            prevBtn.style.display = 'inline-block';
        } else {
            hidePrevButton();
        }
    } catch (error) {
        console.error('Error loading messages:', error);
        showErrorMessage(messageContainer);
    }
}

function updatePaginationInfo(data) {
    const infoSpan = document.getElementById('pagination-info');
    infoSpan.textContent = `Current Page: ${Math.ceil(dm_skip / dm_limit)} | Skip: ${dm_skip} | Limit: ${dm_limit}`;
}

function hideNextButton() {
  const nextBtn = document.getElementById('next-btn');
  nextBtn.style.display = 'none';
}

function showErrorMessage(container) {
  const errorMessage = document.createElement('p');
  errorMessage.textContent = 'Failed to load messages. Please try again later.';
  container.appendChild(errorMessage);
}

document.addEventListener('DOMContentLoaded', () => {
  loadMessages();
});

document.getElementById('prev-btn').addEventListener('click',  async function() {
    await loadMessages();

});

// Modify the next button click event listener
document.getElementById('next-btn').addEventListener('click', async function() {
  await loadMessages();
});
