console.log("Settings.js loaded");

const theme = document.getElementById("theme_input");
const theme_submit = document.getElementById("theme_submit");

console.log(theme);
console.log(theme_submit);
theme_submit.addEventListener('click', (e) => {
  localStorage.setItem('theme', theme.value);
  location.reload();
})

const renderGifs = document.getElementById("render_gifs");
renderGifs.checked = localStorage.getItem('renderGifs') == 'true' || localStorage.getItem('renderGifs') == undefined;

renderGifs.addEventListener('change', (e) => {
  localStorage.setItem('renderGifs', renderGifs.checked);
  location.reload();
})


renderGifs.addEventListener('change', (e) => {
  localStorage.setItem('renderGifs', renderGifs.checked);
  location.reload();
})




const notifications = document.getElementById("notifications");
notifications.checked = localStorage.getItem('notifications') == 'true' || localStorage.getItem('notifications') == undefined;

notifications.addEventListener('change', (e) => {
  localStorage.setItem('notifications', notifications.checked);
  location.reload();
})
