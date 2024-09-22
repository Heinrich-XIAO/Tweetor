console.log("engagedDMs.js loaded");

const dmList = document.getElementById('dm_list');

async function renderDMs() {
  const res = await fetch("/api/engaged_dms");
  const json = await res.json();
  console.log(json);
  if (json.logged_in == false) {
    return;
  }
  for (let i = 0; i < json.length; i++) {
    const dmElement = document.createElement('a');
    dmElement.href = `/dm/${json[i]}`;
    dmElement.classList.add("w3-bar-item");
    dmElement.classList.add("w3-button");
    dmElement.classList.add("dm_with_person");
    dmElement.textContent = json[i].length > 7 ? json[i].slice(0, 5).concat('...') : json[i];
    dmList.appendChild(dmElement);
  }
}

renderDMs();
