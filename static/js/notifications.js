console.log('notifications.js Loaded')
const equals = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let prevRecentMessages;
const notificationAudio = document.getElementById("notification");
console.log(notificationAudio);


function findAddedElements(oldArray, newArray) {
    const addedElements = newArray.filter(newObj => !oldArray.some(oldObj => oldObj["id"] === newObj["id"]));
    return addedElements;
}

async function checkNotifications() {
  const res = await fetch(`/api/get_flits?skip=0&limit=${limit}`);
  const newElements = findAddedElements(prevRecentMessages, await res.clone().json());
  console.log(newElements);
  if (newElements.length != 0) {
    if (window.location.pathname == '/') {
      for (let i = 0; i < newElements.length; i++) {
        console.log((await res.clone().json())[i]);
        let flit = document.createElement("div");
        flit.classList.add("flit");
        flit.dataset.flitId = (await res.clone().json())[i]['id'];
        flit = await renderSingleFlit(flit);
        console.log(flit);
        flits.insertBefore(flit, flits.firstChild);
      }
    }
    prevRecentMessages = await res.json();
    if (Notification.permission == 'granted') {
      console.log("Notification");
      const notification = new Notification(`@${newElements[0].userHandle}`, {
        icon: '/static/logo.png',
        body: newElements[0].userHandle
      })
    }
  }
}

Notification.requestPermission();
if (Notification.permission !== 'denied') {
  Notification.requestPermission();
}

(async () => {
  let res = await fetch(`/api/get_flits?skip=${skip}&limit=${limit}`);
  console.log(await res.clone().json());
  prevRecentMessages = await res.json();

  res = await fetch(`/api/handle`);
  if (localStorage.getItem('notifications') == 'true' || localStorage.getItem('notifications') == undefined && (await res.text()) != 'Not Logged In') {
    window.setInterval(checkNotifications, 5000);
  }
})();

