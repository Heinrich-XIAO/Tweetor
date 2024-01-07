console.log('notifications.js Loaded')
const equals = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let prevRecentMessages;
const notificationAudio = document.getElementById("notification");
console.log(notificationAudio);

async function checkNotifications() {
  const res = await fetch(`/api/get_flits?skip=0&limit=${limit}`);
  if (!equals(await res.clone().json(), prevRecentMessages)) {
    if (window.location.pathname == '/') {
      console.log((await res.clone().json())[0]);
      let flit = document.createElement("div");
      flit.classList.add("flit");
      flit.dataset.flitId = (await res.clone().json())[0]['id'];
      flit = await renderSingleFlit(flit);
      console.log(flit);
      flits.insertBefore(flit, flits.firstChild);
    }
    prevRecentMessages = await res.json();
    if (Notification.permission == 'granted') {
      console.log("Notification");
      const notification = new Notification('Message in Main', {
        icon: '/static/logo.png',
        body: 'Somebody sent something on tweetor'
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
    window.setInterval(checkNotifications, 1000);
  }
})();

