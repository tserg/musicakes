const pendingTransactionsButton = document.querySelector('#pending-transactions-btn');

const pendingTransactionPlaceholder = document.querySelector('#pending-transactions-block');

const csrf_token = window.appConfig.csrf_token.value;

if (pendingTransactionsButton != null) {

  pendingTransactionsButton.addEventListener('click', () => {

  	pendingTransactionPlaceholder.innerHTML = "";



  	if (pendingTransactionPlaceholder.style.display != "block") {
      getPendingTransactions();
  		pendingTransactionPlaceholder.style.display = "block";
  	} else {
  		pendingTransactionPlaceholder.style.display = "none";
  	}
  });
}

async function getPendingTransactions() {

	fetch('/pending_transactions', {
        method: 'GET',
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

        const chainId = data['chain_id'];

        if (data['pending_purchases'].length > 0 || data['pending_deployments'].length > 0) {

          for (i=0; i<data['pending_purchases'].length; i++) {

          	var link = document.createElement("A");
          	link.innerHTML = "Your purchase of " + data['pending_purchases'][i]['purchase_description'] + " is pending confirmation.";
            link.className = "dropdown-item";

            if (chainId === 1) {
          	  link.href = "https://etherscan.io/tx/" + data['pending_purchases'][i]['transaction_hash'];
            } else {
              link.href = "https://ropsten.etherscan.io/tx/" + data['pending_purchases'][i]['transaction_hash'];
            }

            link.target ="_blank";
          	pendingTransactionPlaceholder.appendChild(link);
          }

          for (i=0; i<data['pending_deployments'].length; i++) {

          	var link = document.createElement("A");
          	link.innerHTML = "Your Musicakes deployment for " + data['pending_deployments'][i]['release_name'] + " is pending confirmation.";
            link.className = "dropdown-item";

            if (chainId === 1) {
          	  link.href = "https://etherscan.io/tx/" + data['pending_deployments'][i]['transaction_hash'];
            } else {
              link.href = "https://ropsten.etherscan.io/tx/" + data['pending_deployments'][i]['transaction_hash'];
            }

            link.target ="_blank";
          	pendingTransactionPlaceholder.appendChild(link);
          }


        } else {
          var link = document.createElement("A");

          link.innerHTML = "You do not have any pending transactions.";
          link.className = "dropdown-item";
          link.style.fontSize = "80%";
          pendingTransactionPlaceholder.appendChild(link);
        }

      }).catch(function(error) {
        var link = document.createElement("A");

        link.innerHTML = "We encountered an error. Please try again";
        link.className = "dropdown-item";
        link.style.fontSize = "80%";
        pendingTransactionPlaceholder.appendChild(link);
      });

}
