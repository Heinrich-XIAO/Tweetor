console.log("Flit renderer loaded");

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
  console.log(await res.clone().text())
  const json = await res.json();
  console.log(json)
  for (let flitJSON of json) {
    const flit = document.createElement('div');
    flit.classList.add('flit');
    const flit_data_div = document.createElement('div');
    flit_data_div.classList.add("flit-username");
    flit_data_div.classList.add("flit-timestamp");

    const username = document.createElement('a');
    username.innerText = flitJSON.username;
    username.href = `user/${flitJSON.userHandle}`;
    username.classList.add("user-handle");

    const handle = document.createElement('a');
    handle.innerText = '@' + flitJSON.userHandle;
    handle.href = `user/${flitJSON.userHandle}`;
    handle.classList.add("user-handle");

    let timestamp = new Date(flitJSON.timestamp.replace(/-/g, "/").replace(/T/, " "));
    
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
    flit_data_div.innerHTML += `<button style="float: right; border: none;" onclick='openReportModal(${flitJSON.id})' aria-label='report'><span class="iconify" data-icon="mdi:report" data-width="25"></span></button>`;

    flit.appendChild(flit_data_div);

    const flitContentDiv = document.createElement('div');
    flitContentDiv.classList.add('flit-content');

    if (flitJSON.is_reflit) {
      const originalFlit = document.createElement('div');
      originalFlit.classList.add('flit');
      originalFlit.classList.add('originalFlit');
      originalFlit.dataset.flitId = flitJSON.original_flit_id;
      if (await renderSingleFlit(originalFlit) == 'profane') {
        continue;
      }
      flitContentDiv.appendChild(document.createElement('br'));
      flitContentDiv.appendChild(originalFlit);
      flit.appendChild(flitContentDiv);
    } else {
      const content = document.createElement('a');
      content.innerText = flitJSON.content + ' ' + flitJSON.hashtag;
      content.href = `/flits/${flitJSON.id}`;

      flitContentDiv.appendChild(content);
      if (flitJSON.meme_link && (localStorage.getItem('renderGifs') == 'true' || localStorage.getItem('renderGifs') == undefined)) {
        const image = document.createElement('img');
        image.src = flitJSON.meme_link;
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
    reflitInput.value = flitJSON.id;
    reflitForm.appendChild(reflitInput);
    reflitForm.innerHTML += '<button type="submit" class="retweet-button" aria-label="reflit"><span class="iconify" data-icon="ps:retweet-1"></span></button>';

    flit.appendChild(reflitForm);

    flit.innerHTML += '';
    flit.href = `/flits/${flitJSON.id}`;

    // Add flit in flits div
    flits.appendChild(flit);
  }
  skip += limit;
}
renderFlits();

async function renderSingleFlit(flit) {
  const flitId = flit.dataset.flitId;
  const res = await fetch(`/api/flit?flit_id=${flitId}`);
  if (await res.clone().text() == 'profane') {
    return 'profane';
  }
  console.log(await res.clone().text());
  const json = await res.json();
  console.log(json)
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
    flit_data_div.innerHTML += `<button style="float: right; border: none;" onclick='openReportModal(${flitId})'><span class="iconify" data-icon="mdi:report" data-width="25"></span></button>`;

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
      content.href = `/flits/${flitId}`;

      flitContentDiv.appendChild(content);
      if (json.flit.meme_link && (localStorage.getItem('renderGifs') == 'true' || localStorage.getItem('renderGifs') == undefined)) {
        const image = document.createElement('img');
        image.src = json.flit.meme_link;
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
    reflitInput.value = flitId;
    reflitForm.appendChild(reflitInput);
    reflitForm.innerHTML += '<button type="submit" class="retweet-button"><span class="iconify" data-icon="ps:retweet-1"></span></button>';

    flit.appendChild(reflitForm);

    flit.innerHTML += '';
  }
  flit.href = `/flits/${flitId}`;
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
    console.log(skip);
    renderFlits();
  }
};