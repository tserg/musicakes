const searchButton = document.querySelector('#search-btn');

console.log(searchButton);

searchButton.addEventListener('click', () => {
  var searchTerm = document.querySelector('#search-term').value;
  window.location.href='/search?query=' + searchTerm;
});

async function search(_searchTerm) {

  var data = JSON.stringify({
    search_term: _searchTerm 
  });

	fetch('/search', {
        method: 'POST',
        body: data,
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': csrf_token,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
      })
      .then(response => {
        console.log(response);
        return response.json();
      })
      .then(data => {
        console.log(data);

      });

}