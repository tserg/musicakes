const ethereumButton = document.querySelector('#enable-ethereum-button');
const showAccountAddress = document.querySelector('#account-address');
const showAccountBalance = document.querySelector('#account-balance');
const showAccountPaymentTokenBalance = document.querySelector('#payment-token-balance');
const showMusicakesTotalSupply = document.querySelector('#musicakes-supply');
const showAccountMusicakesBalance = document.querySelector('#user-musicakes-balance');
const showMusicakesPaymentTokenBalance = document.querySelector('#musicakes-payment-token-balance');
const showAccountUnclaimedDividends = document.querySelector('#account-unclaimed-dividends')

const musicakesPayButton = document.querySelector('#btn-pay-contract');
const musicakesPayValue = document.querySelector('#pay-contract-amount');

const musicakesClaimDividendsButton = document.querySelector('#btn-claim-dividends');
const musicakesUpdateDividendsButton = document.querySelector('#btn-update-dividends');

const musicakesTransferButton = document.querySelector('#btn-transfer-musicakes');
const musicakesTransferAddress = document.querySelector('#transfer-musicakes-address');
const musicakesTransferAmount = document.querySelector('#transfer-musicakes-amount');

const enableEthereumButton = document.querySelector('#enable-ethereum-button');

var web3 = new Web3(Web3.givenProvider);

const price = parseFloat(window.appConfig.price.address);
console.log(price);

const track_id = parseInt(window.appConfig.track_id.address);
console.log(track_id);

const csrf_token = window.appConfig.csrf_token.address;
if (csrf_token) {
  console.log("CSRF Token is: " + csrf_token);
}

// Initialise buttons

ethereumButton.addEventListener('click', () => {
	getAccount();
});

musicakesPayButton.addEventListener('click', () => {
	payMusicakes();
});

musicakesClaimDividendsButton.addEventListener('click', () => {
	claimDividends();
});

musicakesUpdateDividendsButton.addEventListener('click', () => {
	updateDividends();
});

musicakesTransferButton.addEventListener('click', () => {
  transferMusicakes();
});

/* Payment token contract */

const paymentTokenAddress = "0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa";
const musicakesAddress = window.appConfig.smart_contract_address.address;
console.log(window.appConfig.smart_contract_address);
console.log(window.appConfig.smart_contract_address.address);
var _paymentTokenAbi = [
  {
    "constant": true,
    "inputs": [],
    "name": "name",
    "outputs": [
      {
        "name": "",
        "type": "string"
      }
    ],
    "payable": false,
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [],
    "name": "decimals",
    "outputs": [
      {
        "name": "",
        "type": "uint8"
      }
    ],
    "payable": false,
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [
      {
        "name": "_owner",
        "type": "address"
      }
    ],
    "name": "balanceOf",
    "outputs": [
      {
        "name": "balance",
        "type": "uint256"
      }
    ],
    "payable": false,
    "type": "function"
  },
  {
    "constant": true,
    "inputs": [],
    "name": "symbol",
    "outputs": [
      {
        "name": "",
        "type": "string"
      }
    ],
    "payable": false,
    "type": "function"
  },
  {
    "constant": false,
    "inputs": [
        {
            "name": "_from",
            "type": "address"
        },
        {
            "name": "_to",
            "type": "address"
        },
        {
            "name": "_value",
            "type": "uint256"
        }
    ],
    "name": "transferFrom",
    "outputs": [
        {
            "name": "",
            "type": "bool"
        }
    ],
    "payable": false,
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
        "constant": false,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    }
];

var _musicakesAbi = [
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "symbol",
          "type": "string"
        },
        {
          "internalType": "contract IERC20",
          "name": "_fundsToken",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Approval",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "by",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "fundsDistributed",
          "type": "uint256"
        }
      ],
      "name": "FundsDistributed",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "by",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "fundsWithdrawn",
          "type": "uint256"
        }
      ],
      "name": "FundsWithdrawn",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Transfer",
      "type": "event"
    },
    {
      "constant": true,
      "inputs": [
        {
          "internalType": "address",
          "name": "_owner",
          "type": "address"
        }
      ],
      "name": "accumulativeFundsOf",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "spender",
          "type": "address"
        }
      ],
      "name": "allowance",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        }
      ],
      "name": "approve",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "internalType": "address",
          "name": "account",
          "type": "address"
        }
      ],
      "name": "balanceOf",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "decimals",
      "outputs": [
        {
          "internalType": "uint8",
          "name": "",
          "type": "uint8"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "subtractedValue",
          "type": "uint256"
        }
      ],
      "name": "decreaseAllowance",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "fundsToken",
      "outputs": [
        {
          "internalType": "contract IERC20",
          "name": "",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "fundsTokenBalance",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "addedValue",
          "type": "uint256"
        }
      ],
      "name": "increaseAllowance",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "name",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "symbol",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "totalSupply",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "internalType": "address",
          "name": "recipient",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        }
      ],
      "name": "transfer",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "internalType": "address",
          "name": "_owner",
          "type": "address"
        }
      ],
      "name": "withdrawableFundsOf",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "internalType": "address",
          "name": "_owner",
          "type": "address"
        }
      ],
      "name": "withdrawnFundsOf",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [],
      "name": "withdrawFunds",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [],
      "name": "updateFundsReceived",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [],
      "name": "payToContract",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

const paymentTokenContract = new web3.eth.Contract(_paymentTokenAbi, paymentTokenAddress);
const musicakesContract = new web3.eth.Contract(_musicakesAbi, musicakesAddress);

ethereum.on('accountsChanged', function(accounts) {
  loadInterface();
});

async function getAccount() {
	await ethereum.enable();
  loadInterface();
}

async function loadInterface() {

  const account = ethereum.selectedAddress;
	showAccountAddress.innerHTML = account;

	// Get ETH balance of current address

	var accountWeiBalance = web3.eth.getBalance(account, function(error, result) {
		if (!error) {
  		var accountBalance = (parseFloat(result)/parseFloat(10**18)).toFixed(18);
  		showAccountBalance.innerHTML = accountBalance;
  		} else {
			console.log(error);
		}
	});

	// Get payment token balance of current address

	var accountPaymentTokenBalance = paymentTokenContract.methods.balanceOf(account).call(function(error, result) {
		if (!error) {
			var accountPaymentTokenBalanceFormatted = (parseFloat(result)/parseFloat(10**18)).toFixed(18);
			showAccountPaymentTokenBalance.innerHTML = accountPaymentTokenBalanceFormatted;
		} else {
			console.log(error);
		}
	});

	// Get total supply of Musicakes
	
	var musicakesTotalSupply = musicakesContract.methods.totalSupply().call(function(error, result) {
		if (!error) {
			showMusicakesTotalSupply.innerHTML = result;
		} else {
			console.log(error);
		}
	});

	// Get Musicakes balance of current account

	var accountMusicakesBalance = musicakesContract.methods.balanceOf(account).call(function(error, result) {
		if (!error) {
			showAccountMusicakesBalance.innerHTML = result;
		} else {
			console.log(error);
		}
	});

	// Get payment token balance in Musicakes contract

	var musicakesPaymentTokenBalance = paymentTokenContract.methods.balanceOf(musicakesAddress).call(function(error, result) {
		if (!error) {
			var musicakesPaymentTokenBalanceFormatted = (parseFloat(result)/parseFloat(10**18)).toFixed(18);
			showMusicakesPaymentTokenBalance.innerHTML = musicakesPaymentTokenBalanceFormatted;
		} else {
			console.log(error);
		}
	});

	// Get unclaimed dividends of current account

	var accountUnclaimedDividends = musicakesContract.methods.withdrawableFundsOf(account).call(function(error, result) {
		if (!error) {
			accountUnclaimedDividendsFormatted = (parseFloat(result)/parseFloat(10**18)).toFixed(18);
			showAccountUnclaimedDividends.innerHTML = accountUnclaimedDividendsFormatted;
		} else {
			console.log(error);
		}
	})

}

async function payMusicakes() {

  const account = ethereum.selectedAddress;

	var payAmount = musicakesPayValue.value;

  if (payAmount < price) {
    alert("The minimum price to pay is " + price.toString() + ".");
  }

  else {

  	var payAmountFormatted = web3.utils.toBN(payAmount).mul(web3.utils.toBN(10**18));


		paymentTokenContract.methods.transfer(musicakesAddress, payAmountFormatted).send({from: account})
		.once('transactionHash', function(hash) {
			console.log(hash);
		})
		.once('receipt', function(receipt) {
      console.log('Receipt for purchase');
			console.log(receipt);
      console.log(receipt.transactionHash);

      var data = JSON.stringify({
        wallet_address: account,
        transaction_hash: receipt.transactionHash,
        paid: payAmount
      });

      console.log(data);

      trackIdString = track_id.toString();

      console.log(trackIdString)

      fetch('/tracks/' + trackIdString + '/purchase', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': csrf_token,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: data
      })
      .then(function(response) {
        console.log(response);
        if (response.ok) {
          alert("Your purchase was successful!");
          location.reload();
        }
        else {
          alert("Your purchase was not successful."
            + "\nDo not make another transaction."
            + "\nPlease contact us at musicakes.team@gmail.com with your transaction hash."
          );
        }

      });
      
		})
		.on('error', function(error) {
			console.log(error);
		});

  }
	
}

async function claimDividends() {

  const account = ethereum.selectedAddress;

	musicakesContract.methods.withdrawFunds().send({from: account})
	.once('transactionHash', function(hash) {
		console.log(hash);
	})
	.once('receipt', function(receipt) {
		console.log(receipt);
    location.reload();
	})
	.on('error', function(error) {
		console.log(error);
	});
}

async function updateDividends() {

  const account = ethereum.selectedAddress;

	musicakesContract.methods.updateFundsReceived().send({from: account})
	.once('transactionHash', function(hash) {
		console.log(hash);
	})
	.once('receipt', function(receipt) {
		console.log(receipt);
    location.reload();
	})
	.on('error', function(error) {
		console.log(error);
	});
}

async function transferMusicakes() {

  const account = ethereum.selectedAddress;

  var musicakesTransferAddressValue = musicakesTransferAddress.value;
  var musicakesTransferAmountValue = musicakesTransferAmount.value;

  musicakesContract.methods.transfer(musicakesTransferAddressValue,
    musicakesTransferAmountValue).send({from: account})
  .once('transactionHash', function(hash) {
    console.log(hash);
  })
  .once('receipt', function(receipt) {
    console.log(receipt);
    location.reload();
  })
  .on('error', function(error) {
    console.log(error);
  });
}