let skip = 0;
const limit = 20;

let bulkFlitCache = {};

let initialFlitsPromise;
{
  const url = new URL(window.location.href);
  const path = url.pathname;
  let params = `skip=${skip}&limit=${limit}`;
  if (path.startsWith('/user/')) {
    const userId = path.split('/').pop();
    params += `&user=${encodeURIComponent(userId)}`;
  }
  initialFlitsPromise = fetch(`/api/get_flits?${params}`)
    .then(res => res.json())
    .then(json => {
      json.forEach(flit => {
        bulkFlitCache[flit.id] = flit;
      });
      return json;
    });
}

function makeUrlsClickable(content) {
  const escapedContent = content.replace(/&/g, '&amp;')
                                .replace(/</g, '&lt;')
                                .replace(/>/g, '&gt;');
  const urlRegex = /(https?:\/\/[^\s]+)/gi;
  const usernameRegex = /\((\w+):\)/gi;

  const allowedImageSites = [
    'https://.*\\.imgur\\.com/',
    'https://.*\\.imgbb\\.com/',
    'https://upload\\.wikimedia\\.org/',
    'https://commons\\.wikimedia\\.org/',
    'https://*terryfox*',
    'https://*imgur*'
  ];

  function isImageUrl(url) {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
    return imageExtensions.some(ext => url.toLowerCase().endsWith(ext));
  }

  let modifiedContent = escapedContent.replace(urlRegex, function(url) {
    const element = document.createElement('a');
    if (allowedImageSites.some(site => new RegExp(site).test(url)) && isImageUrl(url)) {
      const imgElement = document.createElement('img');
      imgElement.src = encodeURI(url);
      imgElement.setAttribute('loading', 'lazy');
      imgElement.onload = function() {
        const aspectRatio = imgElement.width / imgElement.height;
        let maxWidth = 400;
        let maxHeight = 400;
        if (aspectRatio > 1) {
          maxHeight = Math.floor(maxWidth / aspectRatio);
        } else {
          maxWidth = Math.floor(maxHeight * aspectRatio);
        }
        imgElement.width = maxWidth;
        imgElement.height = maxHeight;
        updateImageContainer(imgElement);
      };
      imgElement.alt = "Loading...";
      imgElement.className = "placeholder";
      element.href = url;
      element.target = "_blank";
      element.rel = "noopener noreferrer";
      element.appendChild(imgElement);
    } else {
      element.href = encodeURI(url);
      element.textContent = url;
      element.target = "_blank";
      element.rel = "noopener noreferrer";
    }
    return element.outerHTML;
  });

  modifiedContent = modifiedContent.replace(usernameRegex, (match, username) => {
    return `<a href="/user/${encodeURIComponent(username)}">${username}</a>`;
  });
  modifiedContent = modifiedContent.replace(/<img[^>]*>/g, '<p class="image-container">$&</p>');
  return modifiedContent;
}

function updateImageContainer(imgElement) {
  const container = imgElement.closest('.image-container');
  if (container) {
    container.innerHTML = `<img src="${imgElement.src}" alt="${imgElement.alt || ''}" width="${imgElement.width}" height="${imgElement.height}">`;
  }
}

async function fetchBulkFlits(ids) {
	let idsToFetch = ids.filter(id => !(id in bulkFlitCache));
	if (idsToFetch.length === 0) return bulkFlitCache;
	const query = `?ids=${idsToFetch.join(",")}`;
	const res = await fetch('/api/flits_bulk' + query);
	const data = await res.json();
	for (const key in data) {
		if (Object.prototype.hasOwnProperty.call(data, key)) {
			const flit = data[key];
			bulkFlitCache[flit.id] = flit;
		}
	}
	return bulkFlitCache;
}

async function getBulkFlit(flitId) {
  const bulk = await fetchBulkFlits([flitId]);
  return bulk[flitId];
}

function convertUSTtoEST(date) {
  const ustDate = new Date(date);
  const estDate = new Date(ustDate.toLocaleString('en-US', { timeZone: 'America/New_York' }));
  return estDate;
}

function getMonthAbbreviation(date) {
  const months = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ];
  return months[date.getMonth()];
}

async function renderFlitWithFlitJSON(json, flit) {
  if (json['flit']) {
    const flit_data_div = document.createElement('div');
    flit_data_div.classList.add("flit-username");
    flit_data_div.classList.add("flit-timestamp");
    
    const username = document.createElement('a');
    username.innerText = json.flit.username;
    username.href = `/user/${json.flit.userHandle}`;
    username.classList.add("user-handle");
    
    const handle = document.createElement('a');
    handle.innerText = '@' + json.flit.userHandle;
    handle.href = `/user/${json.flit.userHandle}`;
    handle.classList.add("user-handle");
    
    let timestamp = new Date(json.flit.timestamp.replace(/\s/g, 'T') + "Z");
    timestamp = convertUSTtoEST(timestamp);
    let options = { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric'};
    let formatted_timestamp = timestamp.toLocaleDateString(undefined, options);
    
    const timestampElement = document.createElement("span");
    timestampElement.innerText = formatted_timestamp;
    timestampElement.classList.add("user-handle");
    
    flit_data_div.appendChild(username);
    flit_data_div.innerHTML += '&#160;&#160;';
    flit_data_div.appendChild(handle);
    flit_data_div.innerHTML += '&#160;·&#160;';
    flit_data_div.appendChild(timestampElement);
    flit_data_div.innerHTML += `<button style="float: right; border: none;" onclick='openModal(${json.flit.id})'><span class="iconify" data-icon="mdi:report" data-width="25"></span></button>`;
    
    flit.appendChild(flit_data_div);
    
    const flitContentDiv = document.createElement('div');
    flitContentDiv.classList.add('flit-content');
    
    const content = document.createElement('a');
    content.classList.add('flit-content');
    content.href = `/flits/${json.flit.id}`;
    const processedContent = makeUrlsClickable(json.flit.content);
    content.innerHTML += processedContent;
    flit.appendChild(content);
    
    if (json.flit.meme_link && (localStorage.getItem('renderGifs') === 'true' || localStorage.getItem('renderGifs') === null)) {
      const image = document.createElement('img');
      image.src = json.flit.meme_link;
      image.width = 100;
      flitContentDiv.appendChild(document.createElement('br'));
      flitContentDiv.appendChild(image);
    }
    
    if (json.flit.is_reflit) {
      const originalFlit = document.createElement('div');
      originalFlit.classList.add('flit');
      originalFlit.classList.add('originalFlit');
      originalFlit.dataset.flitId = json.flit.original_flit_id;
      const originalData = await getBulkFlit(json.flit.original_flit_id);
      if (originalData === 'profane') return 'profane';
      await renderFlitWithFlitJSON({ flit: originalData }, originalFlit);
      flitContentDiv.appendChild(originalFlit);
    }
    
    flit.appendChild(flitContentDiv);
    
    let reflit_button = document.createElement("button");
    reflit_button.classList.add("retweet-button");
    reflit_button.addEventListener("click", function() {
      reflit(json.flit.id);
    });
    const icon = document.createElement("span");
    icon.classList.add("iconify");
    icon.setAttribute("data-icon", "ps:retweet-1");
    reflit_button.appendChild(icon);
    reflit_button.style.float = 'right';
    flit_data_div.appendChild(reflit_button);
    flit.dataset.flitId = json.flit.id;
  }
  return flit;
}

async function renderSingleFlit(flit) {
  const flitId = flit.dataset.flitId;
  const data = await getBulkFlit(flitId);
  if (data === 'profane') {
    return 'profane';
  }
  const json = { flit: data };
  await renderFlitWithFlitJSON(json, flit);
  flit.href = `/flits/${flitId}`;
  checkGreenDot();
  return flit;
}

async function renderFlits() {
  if (renderFlits.isRendering) return;
  renderFlits.isRendering = true;
  const url = new URL(window.location.href);
  const path = url.pathname;
  let params = `skip=${skip}&limit=${limit}`;
  if (path.startsWith('/user/')) {
    const userId = path.split('/').pop();
    params += `&user=${encodeURIComponent(userId)}`;
  }
  if (!path.startsWith('/user/') && path !== "/") {
    renderFlits.isRendering = false;
    return;
  }
  let json;
  try {
    if (skip === 0 && initialFlitsPromise) {
      json = await initialFlitsPromise;
      initialFlitsPromise = null;
    } else {
      const res = await fetch(`/api/get_flits?${params}`);
      json = await res.json();
    }
    json.forEach(flit => {
      bulkFlitCache[flit.id] = flit;
    });
  
    const flits = document.getElementById('flits');
    const flitPromises = json.map(async (flitJSON) => {
      let flit = document.createElement("div");
      flit.classList.add("flit");
      return await renderFlitWithFlitJSON({ flit: flitJSON }, flit);
    });
    const flitElements = await Promise.all(flitPromises);
  
    const maxKey = Math.max(...Object.keys(bulkFlitCache).map(Number));
    for (let i = maxKey - skip; i > maxKey - skip - limit; i--) {
      if (bulkFlitCache[i]) {
        const flit = flitElements.find(flit => flit.dataset.flitId == i);
        if (flit !== 'profane') {
          flits.appendChild(flit);
        }
      }
    }
    checkGreenDot();
    skip += limit;
  } catch (error) {
    console.error('Error fetching flits:', error);
  } finally {
    renderFlits.isRendering = false;
  }
}

async function renderAll() {
  const flitsList = Array.from(document.getElementsByClassName('flit'));
  await Promise.all(flitsList.map(async (flit) => renderSingleFlit(flit)));
}

async function reflit(id) {
  const data = await getBulkFlit(id);
  const json = { flit: data };
  let flit = document.createElement('div');
  flit.classList.add('flit');
  flit = await renderFlitWithFlitJSON(json, flit);
  const addedElements = document.getElementById('addedElements');
  addedElements.appendChild(flit);
  const original_flit_id_input = document.getElementById('original_flit_id');
  original_flit_id_input.value = json.flit.id;
}

async function checkGreenDot() {
  const onlineUsers = await fetch('/api/render_online').then(res => res.json());
  updateGreenDots(Object.keys(onlineUsers));
}

async function updateGreenDots(onlineUsers) {
  const handles = document.querySelectorAll(".user-handle");
  handles.forEach((handle, index) => {
    if (index % 3 !== 0) return;
    const nextSibling = handle.nextSibling;
    if (nextSibling && nextSibling.nodeType === Node.ELEMENT_NODE && 
       (nextSibling.style.backgroundColor === "green" || nextSibling.style.backgroundColor === "grey")) {
      nextSibling.parentNode.removeChild(nextSibling);
    }
    if (onlineUsers.includes(handle.innerText)) {
      const greenCircle = document.createElement("span");
      greenCircle.style.backgroundColor = "green";
      greenCircle.style.borderRadius = "50%";
      greenCircle.style.width = "10px";
      greenCircle.style.height = "10px";
      greenCircle.style.display = "inline-block";
      greenCircle.style.marginLeft = "5px";
      handle.parentNode.insertBefore(greenCircle, handle.nextSibling);
    } else {
      const greyCircle = document.createElement("span");
      greyCircle.style.backgroundColor = "grey";
      greyCircle.style.borderRadius = "50%";
      greyCircle.style.width = "10px";
      greyCircle.style.height = "10px";
      greyCircle.style.display = "inline-block";
      greyCircle.style.marginLeft = "5px";
      handle.parentNode.insertBefore(greyCircle, handle.nextSibling);
    }
  });
}

socket.on('online_update', function(online) {
  updateGreenDots(Object.keys(online));
});

document.addEventListener('DOMContentLoaded', () => {
  renderAll();
  renderFlits();
  
  window.onscroll = function(ev) {
    if (Math.round(window.innerHeight + window.scrollY) > document.body.offsetHeight - window.innerHeight) {
      renderFlits();
    }
  };
});
