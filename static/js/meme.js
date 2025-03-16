document.addEventListener('DOMContentLoaded', function() {
  if (document.querySelector('#memePopup')) {
    let meme = document.querySelector('#memePopup');
    let memeImages = document.querySelector('#memeBackgrounds');
    let addMemeButton = document.querySelector('#addMeme');
    let finalMemeURL;
    let selectedMemeBG;
    let searchTimeout;

    window.closeMeme = function() {
      meme.style.display = 'none';
    }

    window.makeMeme = function() {
      meme.style.display = 'block';
    }

    async function searchTenor(q) {
      if (q == '')  
        return;
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
      searchTimeout = setTimeout(async () => {
        const response = await fetch(`/api/get_gif`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
          },
          body: JSON.stringify({q}),
        });
        const data = await response.json();

        if (data['error']) {
          console.error(data['error']);
          return;
        }
        data['results'] = data['results'].slice(0, 8);
        const images = document.createElement('div');

        for (const result of data['results']) {
          // Determine smallest media and its format key
          let smallestMedia, chosenFormat;
          for (const [format, mediaObj] of Object.entries(result.media_formats)) {
            if (!smallestMedia || mediaObj.size < smallestMedia.size) {
              smallestMedia = mediaObj;
              chosenFormat = format;
            }
          }
          // Create either a video or an image element based on the chosen format
          let mediaElement;
          if (chosenFormat.toLowerCase().includes("webm")) {
            mediaElement = document.createElement("video");
            mediaElement.src = smallestMedia.url;
            mediaElement.height = 100;
            mediaElement.controls = false;
            mediaElement.autoplay = true;
            mediaElement.muted = true; // Mute by default
          } else {
            mediaElement = document.createElement("img");
            mediaElement.src = smallestMedia.url;
            mediaElement.height = 100;
          }
          mediaElement.dataset['id'] = result.id;
          mediaElement.onclick = (e) => {
            let newElement;
            if (e.target.tagName.toLowerCase() === 'video') {
              newElement = document.createElement("video");
              newElement.src = e.target.src;
              newElement.width = e.target.tagName.toLowerCase() === 'video' ? e.target.videoWidth : e.target.width;
              newElement.controls = false;
              newElement.autoplay = true;
            } else {
              newElement = document.createElement("img");
              newElement.src = e.target.src;
              newElement.width = e.target.width;
            }
            newElement.dataset = e.target.dataset;
            memeImages.innerHTML = '';
            document.getElementById("addedElements").innerHTML = "";
            document.getElementById("addedElements").appendChild(newElement);
            document.getElementById("meme_link").value = newElement.src;
            closeMeme();
          }
          images.appendChild(mediaElement);
        }
        memeImages.innerHTML = '';
        memeImages.appendChild(images);
      }, 500);
    }

    document.getElementById("search-tenor").addEventListener("input", async function (e) {
      memeImages.innerHTML = '';
      searchTenor(this.value);
    });
  }
});
