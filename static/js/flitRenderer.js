console.log("Flit renderer loaded");

async function renderSingleFlit(flit) {
  const flitId = flit.dataset.flitId;
  const res = await fetch(`/api/flit?flit_id=${flitId}`);
  const json = await res.json();
  console.log(json)
  if (json['flit']) {
    const flit_data_div = document.createElement('div');
    flit_data_div.classList.add("flit-username");
    flit_data_div.classList.add("flit-timestamp");

    const username = document.createElement('a');
    username.innerText = json.flit.username;
    username.href = `user/${json.flit.userHandle}`;

    const handle = document.createElement('a');
    handle.innerText = '@' + json.flit.userHandle;
    username.href = `user/${json.flit.userHandle}`;
    handle.classList.add("user-handle");

    let timestamp = new Date(json.flit.timestamp.replace(/-/g, "/").replace(/T/, " "));

    // Function to get the abbreviated month name
    function getMonthAbbreviation(date) {
      const months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
      ];
      return months[date.getMonth()];
    }

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

    const timestampElement = document.createElement("a");
    timestampElement.innerText = formatted_timestamp;
    timestampElement.classList.add("user-handle");
    
    flit_data_div.appendChild(username);
    flit_data_div.innerHTML += '&#160;&#160;';
    flit_data_div.appendChild(handle);
    flit_data_div.innerHTML += '&#160;·&#160;';
    flit_data_div.appendChild(timestampElement);

    flit.appendChild(flit_data_div);

    const flitContentDiv = document.createElement('div');
    flitContentDiv.classList.add('flit-content');

    if (json.flit.is_reflit) {
      const originalFlit = document.createElement('div');
      originalFlit.classList.add('flit');
      originalFlit.dataset.flitId = json.flit.original_flit_id;
      renderSingleFlit(originalFlit);
      flitContentDiv.appendChild(originalFlit);
      flit.appendChild(flitContentDiv);
    } else {
      const content = document.createElement('a');
      content.innerText = json.flit.content + ' ' + json.flit.hashtag;
      content.href = `/flits/${flitId}`;

      flitContentDiv.appendChild(content);
      if (json.flit.meme_link) {
        const image = document.createElement('img');
        image.src = json.flit.meme_link;
        flitContentDiv.appendChild(document.createElement('br'));
        flitContentDiv.appendChild(image);
      }

      flit.appendChild(flitContentDiv);
    }
    flit.innerHTML += `<form action="/submit_flit" method="POST">
      <input type="hidden" name="original_flit_id" value="${flitId}">
      <button type="submit" class="retweet-button"><span class="iconify" data-icon="ps:retweet-1"></span></button>
    </form>`;
  }
  flit.href = `/flits/${flitId}`;
}

const flits = document.getElementsByClassName('flit');

async function renderAll() {
  for (let i = 0; i < flits.length; i++) {
    await renderSingleFlit(flits[i]);
  }
}

renderAll();