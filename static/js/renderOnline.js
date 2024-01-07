console.log("renderOnline.js loaded");

fetch("/api/render_online");

window.setInterval(()=> {
  fetch("/api/render_online");
}, 5000)