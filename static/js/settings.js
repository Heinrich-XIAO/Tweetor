console.log("Settings.js loaded");

const theme = document.getElementById("theme_input");
const theme_submit = document.getElementById("theme_submit");

console.log(theme);
console.log(theme_submit);
theme_submit.addEventListener('click', (e) => {
  localStorage.setItem('theme', theme.value);
  location.reload();
})