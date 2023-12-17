console.log("flitRenderer.js loaded");

const flits = document.getElementById('flits');
let skip = 0;
let limit = 10;

// Function to get the abbreviated month name
function getMonthAbbreviation(date) {
  const months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
  ];
  return months[date.getMonth()];
}

async function renderFlits() {
  const res = await fetch(`/api/get_flits?skip=${skip}&limit=${limit}`); //////////////////////////////// possible http param inject
  const json = await res.json();
  for (let flitJSON of json) {
    let flit = document.createElement("div");
    flit.classList.add("flit");
    flit = await renderFlitWithFlitJSON({"flit": flitJSON}, flit);
    if (flit === 'profane') {
      continue;
    }
    flits.appendChild(flit);
  }
  checkGreenDot();
  skip += limit;
}
renderFlits();

async function renderSingleFlit(flit) {
  const flitId = flit.dataset.flitId;
  const res = await fetch(`/api/flit?flit_id=${flitId}`);
  if (await res.clone().text() == 'profane') {
    return 'profane';
  }
  const json = await res.json();
  flit = renderFlitWithFlitJSON(json, flit);

  flit.href = `/flits/${flitId}`;
  checkGreenDot();
  return flit;
}

async function renderFlitWithFlitJSON(json, flit) {
  if (json['flit']) {
    const flit_data_div = document.createElement('div');
    flit_data_div.classList.add("flit-username");
    flit_data_div.classList.add("flit-timestamp");

    const username = document.createElement('a');
    username.innerText = json.flit.username;
    username.href = `user/${json.flit.userHandle}`;
    username.classList.add("user-handle");

    const handle = document.createElement('a');
    handle.innerText = '@' + json.flit.userHandle;
    handle.href = `user/${json.flit.userHandle}`;
    handle.classList.add("user-handle");

    let timestamp = new Date(json.flit.timestamp.replace(/-/g, "/").replace(/T/, " "));

    // Format the Date object
    let now = new Date();
    let formatted_timestamp;

    if (timestamp.getFullYear() !== now.getFullYear()) {
      let options = { year: 'numeric', month: 'short', day: 'numeric' };
      formatted_timestamp = timestamp.toLocaleDateString(undefined, options);
    } else {
      let monthAbbreviation = getMonthAbbreviation(timestamp);
      formatted_timestamp = monthAbbreviation + " " + timestamp.getDate();
    }

    const timestampElement = document.createElement("span");
    timestampElement.innerText = formatted_timestamp;
    timestampElement.classList.add("user-handle");
    
    flit_data_div.appendChild(username);
    flit_data_div.innerHTML += '&#160;&#160;';
    flit_data_div.appendChild(handle);
    flit_data_div.innerHTML += '&#160;·&#160;';
    flit_data_div.appendChild(timestampElement);
    flit_data_div.innerHTML += `<button style="float: right; border: none;" onclick='openReportModal(${json.flit.id})'><span class="iconify" data-icon="mdi:report" data-width="25"></span></button>`;

    flit.appendChild(flit_data_div);

    const flitContentDiv = document.createElement('div');
    flitContentDiv.classList.add('flit-content');

    if (json.flit.is_reflit) {
      const originalFlit = document.createElement('div');
      originalFlit.classList.add('flit');
      originalFlit.classList.add('originalFlit');
      originalFlit.dataset.flitId = json.flit.original_flit_id;
      if (await renderSingleFlit(originalFlit) == 'profane') {
        return 'profane';
      };
      flitContentDiv.appendChild(document.createElement('br'));
      flitContentDiv.appendChild(originalFlit);
      flit.appendChild(flitContentDiv);
    } else {
      const content = document.createElement('a');
      content.innerText = json.flit.content + ' ' + json.flit.hashtag;
      content.href = `/flits/${json.flit.id}`;

      flitContentDiv.appendChild(content);
      if (json.flit.meme_link && (localStorage.getItem('renderGifs') == 'true' || localStorage.getItem('renderGifs') == undefined)) {
        const image = document.createElement('img');
        image.src = json.flit.meme_link;
        image.width = 100;
        flitContentDiv.appendChild(document.createElement('br'));
        flitContentDiv.appendChild(image);
      }

      flit.appendChild(flitContentDiv);
    }

    const reflitForm = document.createElement('form');
    reflitForm.action = '/submit_flit';
    reflitForm.method = 'POST';

    const reflitInput = document.createElement('input');
    reflitInput.type = 'hidden';
    reflitInput.name = 'original_flit_id';
    reflitInput.value = json.flit.id;
    reflitForm.appendChild(reflitInput);
    reflitForm.innerHTML += '<button type="submit" class="retweet-button"><span class="iconify" data-icon="ps:retweet-1"></span></button>';

    flit.appendChild(reflitForm);

    flit.innerHTML += '';
  }
  return flit;
}

const flitsList = document.getElementsByClassName('flit');

async function renderAll() {
  for (let i = 0; i < flitsList.length; i++) {
    await renderSingleFlit(flitsList[i]);
  }
}

renderAll();

window.onscroll = function (ev) {
  if (Math.round(window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
    renderFlits();
  }
};

async function checkGreenDot() {
  console.log('checking green dot')
  const res = await fetch("/api/render_online");
  const data = await res.json();
  // Get the list of online users
  const onlineUsers = Object.keys(data);

  // Update the user page
  const handles = document.querySelectorAll(".user-handle");
  console.log(handles);
  console.log(onlineUsers)

  handles.forEach((handle, index) => {
    if (index % 3 != 0) {
      return;
    }
    // Remove the green circle from the user
    const nextSibling = handle.nextSibling;
    if (nextSibling && nextSibling.nodeType === Node.ELEMENT_NODE && (nextSibling.style.backgroundColor === "green" || nextSibling.style.backgroundColor === "grey")) {
      nextSibling.parentNode.removeChild(nextSibling);
    }
    console.log(onlineUsers.includes(handle.innerText))
  
    // Check if the user is online
    if (onlineUsers.includes(handle.innerText)) {
      // Add a green circle next to the user's handle
      const greenCircle = document.createElement("span");
      greenCircle.style.backgroundColor = "green";
      greenCircle.style.borderRadius = "50%";
      greenCircle.style.width = "10px";
      greenCircle.style.height = "10px";
      greenCircle.style.display = "inline-block";
      greenCircle.style.marginLeft = "5px";
      handle.parentNode.insertBefore(greenCircle, handle.nextSibling);
    } else {
      // Add a green circle next to the user's handle
      const greyCircle = document.createElement("span");
      greyCircle.style.backgroundColor = "grey";
      greyCircle.style.borderRadius = "50%";
      greyCircle.style.width = "10px";
      greyCircle.style.height = "10px";
      greyCircle.style.display = "inline-block";
      greyCircle.style.marginLeft = "5px";
      handle.parentNode.insertBefore(greyCircle, handle.nextSibling);
    }
  })
}

window.setInterval(checkGreenDot, 5000);