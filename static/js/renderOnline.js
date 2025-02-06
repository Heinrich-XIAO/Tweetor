console.log("renderOnline.js loaded");

fetch("/api/render_online", { cache: "no-store" });

window.setInterval(() => {
  fetch("/api/render_online", { cache: "no-store" });
}, 10000);

