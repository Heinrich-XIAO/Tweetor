console.log('notifications.js Loaded')
const equals = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let prevRecentMessages;
const notificationAudio = document.getElementById("notification");
console.log(notificationAudio);

async function checkNotifications() {
  const res = await fetch(`/api/get_flits?skip=0&limit=${limit}`);
  if (!equals(await res.clone().json(), prevRecentMessages)) {
    prevRecentMessages = await res.json();
    if (Notification.permission == 'granted') {
      notificationAudio.play()
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
  const res = await fetch(`/api/get_flits?skip=${skip}&limit=${limit}`);
  console.log(await res.clone().json());
  prevRecentMessages = await res.json();
})();

window.setInterval(checkNotifications, 1000);