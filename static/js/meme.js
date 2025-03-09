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
          // Create an img element
          const img = document.createElement("img");

          // Set the src attribute to the gif url
          img.src = result.media_formats.gif.url;
          img.height = 100;
          img.dataset['id'] = result.id;
          img.onclick = (e) => {
            const img = document.createElement("img");
            img.src = e.srcElement.src;
            img.width = e.srcElement.width * 3;
            img.dataset = e.srcElement.dataset;
            memeImages.innerHTML = '';
            document.getElementById("addedElements").innerHTML = "";
            document.getElementById("addedElements").appendChild(img);
            document.getElementById("meme_link").value = img.src;
            closeMeme();
          }

          // Append the img element to the div
          images.appendChild(img);
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
