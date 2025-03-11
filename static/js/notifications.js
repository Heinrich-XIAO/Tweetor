('notifications.js Loaded')
const equals = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let prevRecentMessages;
const notificationAudio = document.getElementById("notification");
const hasNotificationSupport = 'Notification' in window;


function findAddedElements(oldArray, newArray) {
    const addedElements = newArray.filter(newObj => !oldArray.some(oldObj => oldObj["id"] === newObj["id"]));
    return addedElements;
}

async function checkNotifications() {
  const res = await fetch(`/api/get_flits?skip=0&limit=${limit}`);
  const newElements = findAddedElements(prevRecentMessages, await res.clone().json());
  if (newElements.length != 0) {
    if (window.location.pathname == '/') {
      for (let i = 0; i < newElements.length; i++) {
        let flit = document.createElement("div");
        flit.classList.add("flit");
        flit.dataset.flitId = newElements[i].id;
        flit = await renderSingleFlit(flit);
        flits.insertBefore(flit, flits.firstChild);
      }
    }
    prevRecentMessages = await res.json();
    if (hasNotificationSupport && Notification.permission == 'granted') {
      const notification = new Notification(`@${newElements[0].userHandle}`, {
        icon: '/static/logo.svg',
        body: newElements[0].content
      })
    }
  }
}

document.addEventListener('click', () => {
  if (hasNotificationSupport && Notification.permission !== 'granted') {
    Notification.requestPermission();
  }
}, { once: true });

socket.on('new_flit', checkNotifications);

(async () => {
  let res = await fetch(`/api/get_flits?skip=${skip}&limit=${limit}`);
  prevRecentMessages = await res.json();
})();

