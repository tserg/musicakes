const ethereumButton = document.querySelector('#enableEthereumButton');
const showAccount = document.querySelector('#account_address');

console.log(ethereumButton);
console.log(showAccount);

ethereumButton.addEventListener('click', () => {
	getAccount();
});

async function getAccount() {
	const accounts = await ethereum.enable();
	console.log(accounts);
	const account = accounts[0];
	console.log(account)
	showAccount.innerHTML = account;
}