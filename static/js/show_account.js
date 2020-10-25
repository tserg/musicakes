$('.remove-txn-btn').bind("click", function() {

  var transactionHash = this.dataset.transactionHash;
  hideTransaction(transactionHash);

});

$('.update-txn-btn').bind("click", function() {

  var transactionHash = this.dataset.transactionHash;
  updateTransaction(transactionHash);

});

async function hideTransaction(_transactionHash) {

	fetch('/transactions/' + _transactionHash + '/hide', {
        method: 'POST',
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
        if (data['success'] === true) {
          alert("Transaction has been successfully removed from history.");
        } else {
          alert("The transaction could not be removed. Please try again.");
        }
        window.location.reload();
      });

}

async function updateTransaction(_transactionHash) {

  fetch('/transactions/' + _transactionHash + '/update', {
        method: 'POST',
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
        if (data['success'] === true) {
          alert("We are retrieving the latest status. Please refresh your page.");
        } else {
          alert("Latest transaction status could not be retrieved. Please try again.");
        }
      });

}