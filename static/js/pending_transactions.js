const pendingTransactionsButton = document.querySelector('#pending-transactions-btn');

const pendingTransactionPlaceholder = document.querySelector('#pending-transactions-block');

const csrf_token = window.appConfig.csrf_token.value;

pendingTransactionsButton.addEventListener('click', () => {

	pendingTransactionPlaceholder.innerHTML = "";



	if (pendingTransactionPlaceholder.style.display != "block") {
    getPendingTransactions();
		pendingTransactionPlaceholder.style.display = "block";
	} else {
		pendingTransactionPlaceholder.style.display = "none";
	}
});

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

        if (data['data'].length > 0) {

          for (i=0; i<data['data'].length; i++) {

          	var link = document.createElement("A");
          	link.innerHTML = "Your purchase of " + data['data'][i]['purchase_description'] + " is pending confirmation.";
            link.className = "dropdown-item";

            if (chainId === 1) {
          	  link.href = "https://etherscan.io/tx/" + data['data'][i]['transaction_hash'];
            } else {
              link.href = "https://ropsten.etherscan.io/tx/" + data['data'][i]['transaction_hash'];
            }

            link.target ="_blank";
          	pendingTransactionPlaceholder.appendChild(link);
          }

        } else {
          var link = document.createElement("A");

          link.innerHTML = "You do not have any pending transactions.";
          pendingTransactionPlaceholder.appendChild(link);
        }

      });

}