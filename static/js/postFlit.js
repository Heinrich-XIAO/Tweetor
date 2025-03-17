const postFlit = event => {
  event.preventDefault(); // Prevent the default form submission

  const formData = new FormData(document.getElementById('post_flit')); // Create a new FormData object from the form
  document.getElementById('post_flit').reset(); // Reset the form before making the request
  document.getElementById('addedElements').innerHTML = ''; // Clear the added elements

  fetch('/submit_flit', {
    method: 'POST',
    body: formData
  })
}

String.prototype.trimEllip = function (length) {
  return this.length > length ? this.substring(0, length) : this;
}

// Get the textarea element and the form input element
const textarea = document.getElementById('field');
const flitInput = document.querySelector('form#post_flit input[name="content"]');
const characterCounter = document.getElementById('character-counter');

document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('keydown', () => {
      textarea.focus();
  }, {once: true});
  document.getElementById('post_flit').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      postFlit(event)
    }
  });
});



textarea.addEventListener('input', function() {
  let content = textarea.value;
  // Update the form input value with the formatted content
  textarea.value = content.trimEllip(300);
  characterCounter.innerHTML = `${textarea.value.length}/300`;
});

document.getElementById('post_flit').addEventListener('submit', postFlit);
