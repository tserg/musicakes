const pendingTransactionsButton = document.querySelector('#pending-transactions-btn');

const pendingTransactionPlaceholder = document.querySelector('#pending-transactions-block');

const csrf_token = window.appConfig.csrf_token.value;

pendingTransactionsButton.addEventListener('click', () => {

	pendingTransactionPlaceholder.innerHTML = "";

	getPendingTransactions();

	if (pendingTransactionPlaceholder.style.display != "block") {
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
        console.log(data['data'].length);

        for (i=0; i<data['data'].length; i++) {
        	console.log(i);
        	console.log(data['data'][i]);
        	var link = document.createElement("A");
        	link.innerHTML = "Your purchase of " + data['data'][i]['purchase_description'] + " is pending confirmation.";
        	link.href = "https://etherscan.io/tx/" + data['data'][i]['transaction_hash'];
          link.target ="_blank";
        	pendingTransactionPlaceholder.appendChild(link);
        } 

      });

}