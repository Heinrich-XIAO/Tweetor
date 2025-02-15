console.log("renderDMs.js loaded");


const url = window.location.href;
const mainUrl = url.split('?')[0];
const receiverHandle = mainUrl.substring(mainUrl.lastIndexOf('/') + 1);
let dm_skip = 0;
const dm_limit = 100;

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
			if (!data.blocked_users.includes(message.sender_handle)) {
				const p = document.createElement('p');
				p.textContent = `${message.sender_handle}: ${message.content}`;
				messageContainer.appendChild(p);
			}
		});

		// Update pagination info
		updatePaginationInfo();

		// Handle pagination
		if (data.pagination.has_more) {
			const nextBtn = document.getElementById('next-btn');
			nextBtn.style.display = 'inline-block';
		} else {
			hideNextButton();
		}

		// Handle going back
		if (dm_skip > 0) {
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

function updatePaginationInfo() {
	const infoSpan = document.getElementById('pagination-info');
	infoSpan.textContent = `Current Page: ${1+Math.ceil(dm_skip / dm_limit)}`;
}

function hideNextButton() {
  const nextBtn = document.getElementById('next-btn');
  nextBtn.style.display = 'none';
}

function hidePrevButton() {
  const prevBtn = document.getElementById('prev-btn');
  prevBtn.style.display = 'none';
}

function showErrorMessage(container) {
  const errorMessage = document.createElement('p');
  errorMessage.textContent = 'Failed to load messages. Please try again later.';
  container.appendChild(errorMessage);
}

document.addEventListener('DOMContentLoaded', () => {
  loadMessages();
});

document.getElementById('prev-btn').addEventListener('click', function() {
  if (dm_skip > 0) {
    dm_skip -= dm_limit;
    loadMessages();
  } else {
    console.log("Cannot decrease further");
  }
});

// Modify the next button click event listener
document.getElementById('next-btn').addEventListener('click', function() {
	dm_skip += dm_limit;
  loadMessages();
});
