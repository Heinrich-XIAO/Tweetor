let dmData = [];

async function fetchDMs() {
  const res = await fetch("/api/engaged_dms");
  const json = await res.json();
  if (json.logged_in == false) {
    return;
  }
  dmData = json;
}

function renderDMs() {
  const dmList = document.getElementById('dm_list');
  for (let i = 0; i < dmData.length; i++) {
    const dmElement = document.createElement('a');
    dmElement.href = `/dm/${dmData[i]}`;
    dmElement.classList.add("w3-bar-item");
    dmElement.classList.add("w3-button");
    dmElement.classList.add("dm_with_person");
    dmElement.textContent = dmData[i];

    const redDot = document.createElement('span');
    redDot.style.display = 'none';
    redDot.classList.add('red-dot');
    redDot.id = `red-dot-${dmData[i]}`;
    dmElement.appendChild(redDot);

    const dmWrapper = document.createElement('div');
    dmWrapper.appendChild(dmElement);

    dmList.appendChild(dmWrapper);
  }
}

fetchDMs().then(
  () => {
    if (document.readyState == "loading") {
      document.addEventListener('DOMContentLoaded', async () => {
        renderDMs();
      });
      return;
    }
    renderDMs();
  }
)

