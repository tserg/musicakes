const ethereumButton = document.querySelector('#enableEthereumButton');
const showAccountAddress = document.querySelector('#account_address');
const showAccountBalance = document.querySelector('#account_balance');

console.log(ethereumButton);
console.log(showAccountAddress);
console.log(showAccountBalance);

var web3 = new Web3(Web3.givenProvider);

console.log(web3);

ethereumButton.addEventListener('click', () => {
	getAccount();
});

async function getAccount() {
	const accounts = await ethereum.enable();
	console.log(accounts);
	const account = accounts[0];
	console.log(account)
	showAccountAddress.innerHTML = account;

	var accountWeiBalance = web3.eth.getBalance(account, function(error, result) {
		if (!error) {


		console.log(result);
		var accountBalance = web3.utils.fromWei(result, "ether");
		showAccountBalance.innerHTML = accountBalance;
		} else {
			console.log(error);
		}
	});

}

/* Payment token contract */



