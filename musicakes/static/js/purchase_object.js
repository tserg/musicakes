// const ethereumButton = document.querySelector('#btn-enable-ethereum');
const showAccountAddress = document.querySelector('#account-address');
// const showAccountBalance = document.querySelector('#account-balance');

const launchPurchaseModalButton = document.querySelector("#buy-modal-btn");
const showAccountPaymentTokenBalance = document.querySelector('#payment-token-balance');

const manageMusicakesButton = document.querySelector('#btn-manage-musicakes');

const showMusicakesTotalSupply = document.querySelector('#musicakes-supply');
const showAccountMusicakesBalance = document.querySelector('#user-musicakes-balance');
const showMusicakesPaymentTokenBalance = document.querySelector('#musicakes-payment-token-balance');
const showAccountUnclaimedDividends = document.querySelector('#account-unclaimed-dividends');

const musicakesPayButton = document.querySelector('#btn-pay-contract');
const musicakesPayValue = document.querySelector('#pay-contract-amount');

const musicakesClaimDividendsButton = document.querySelector('#btn-claim-dividends');
const musicakesUpdateDividendsButton = document.querySelector('#btn-update-dividends');

const musicakesTransferButton = document.querySelector('#btn-transfer-musicakes');
const musicakesTransferAddress = document.querySelector('#transfer-musicakes-address');
const musicakesTransferAmount = document.querySelector('#transfer-musicakes-amount');

const seeMoreButton = document.querySelector('#btn-see-more');
const seeMoreArrow = document.querySelector('#icon-see-more');
const seeMoreText = document.querySelector('#text-see-more');
const musicakesDashboard = document.querySelector('#musicakes-dashboard');
// const musicakesManagementDashboard = document.querySelector('#musicakes-management-dashboard');

var ethereumChainId = parseInt(document.querySelector('meta[property~="chain-id"]').getAttribute('content'));

const price = parseFloat(document.querySelector('meta[property~="price"]').getAttribute('content'));
const objectId = parseInt(document.querySelector('meta[property~="object-id"]').getAttribute('content'));
const objectType = document.querySelector('meta[property~="object-type"]').getAttribute('content')

const csrf_token_purchase = document.querySelector('meta[property~="csrf-token"]').getAttribute('content');
if (csrf_token_purchase) {
  console.log("CSRF Token loaded");
}

/* Payment token contract */

// paymentTokenAddress is declared as var because it may be re-declared in support-artist.js

var paymentTokenAddress = document.querySelector('meta[property~="payment-token-address"]').getAttribute('content');
const musicakesAddress = document.querySelector('meta[property~="smart-contract-address"]').getAttribute('content');

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
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "name": "sender",
          "type": "address"
        },
        {
          "indexed": true,
          "name": "receiver",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Transfer",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": true,
          "name": "spender",
          "type": "address"
        },
        {
          "indexed": false,
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
          "name": "sender",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "FundsDeposited",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "name": "receiver",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "value",
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
          "name": "receiver",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "FundsWithdrawn",
      "type": "event"
    },
    {
      "inputs": [],
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "gas": 415269,
      "inputs": [
        {
          "name": "_name",
          "type": "string"
        },
        {
          "name": "_symbol",
          "type": "string"
        },
        {
          "name": "_decimals",
          "type": "uint256"
        },
        {
          "name": "_supply",
          "type": "uint256"
        },
        {
          "name": "_ownerAddress",
          "type": "address"
        },
        {
          "name": "_paymentTokenAddress",
          "type": "address"
        }
      ],
      "name": "initialize",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 1208,
      "inputs": [],
      "name": "totalSupply",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1668,
      "inputs": [
        {
          "name": "_owner",
          "type": "address"
        },
        {
          "name": "_spender",
          "type": "address"
        }
      ],
      "name": "allowance",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 148546,
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
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 111245,
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
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 37971,
      "inputs": [
        {
          "name": "_spender",
          "type": "address"
        },
        {
          "name": "_value",
          "type": "uint256"
        }
      ],
      "name": "approve",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 75508,
      "inputs": [
        {
          "name": "_value",
          "type": "uint256"
        }
      ],
      "name": "burn",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 111859,
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
      "name": "burnFrom",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 166839,
      "inputs": [],
      "name": "withdrawFunds",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 81882,
      "inputs": [],
      "name": "updateFundsTokenBalance",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 1872,
      "inputs": [
        {
          "name": "_receiver",
          "type": "address"
        }
      ],
      "name": "withdrawableFundsOf",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1723,
      "inputs": [
        {
          "name": "_receiver",
          "type": "address"
        }
      ],
      "name": "withdrawnFundsOf",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 6060,
      "inputs": [
        {
          "name": "_amount",
          "type": "uint256"
        }
      ],
      "name": "payToContract",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "stateMutability": "payable",
      "type": "fallback"
    },
    {
      "gas": 1568,
      "inputs": [],
      "name": "getPointsPerShare",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 8000,
      "inputs": [],
      "name": "name",
      "outputs": [
        {
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 7053,
      "inputs": [],
      "name": "symbol",
      "outputs": [
        {
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1658,
      "inputs": [],
      "name": "decimals",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1903,
      "inputs": [
        {
          "name": "arg0",
          "type": "address"
        }
      ],
      "name": "balanceOf",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
  ];

// Helper function to check chain ID

function checkChainId(_current, _expected) {
  if (_current !== _expected) {

    if (_current === 1) {
      alert('You are connected to the wrong network. Please switch to the Ethereum mainnet to continue!')
    } else if (_current === 3) {
      alert('You are connected to the wrong network. Please switch to the Ropsten testnet to continue!')
    } else {
      alert('You are connected to the wrong network.')
    }
    return false;
  }
  return true;
}

// Initialise Metamask

window.addEventListener('load', async () => {

  if (window.ethereum) {

    window.web3 = new Web3(window.ethereum);

    console.log('Ethereum successfully detected!');

    ethereum.on('accountsChanged', function(accounts) {
      location.reload();
    });

    // From now on, this should always be true:
    // provider === window.ethereum

    // Access the decentralized web!

    // Legacy providers may only have ethereum.sendAsync
    var chainId = await web3.eth.getChainId();

    window.currentChainId = parseInt(chainId);

    checkChainId(currentChainId, ethereumChainId);

    window.paymentTokenContract = new web3.eth.Contract(_paymentTokenAbi, paymentTokenAddress);

    if (musicakesAddress.length > 2) {
      window.musicakesContract = new web3.eth.Contract(_musicakesAbi, musicakesAddress);
    } else {
      window.musicakesContract = null;
    }


  } else {

    // if the provider is not detected, detectEthereumProvider resolves to null
    alert('Please install MetaMask to continue!');
  }

});

// Initialise buttons



if (launchPurchaseModalButton != null) {

  launchPurchaseModalButton.addEventListener('click', () => {
    if (web3) {

      if (checkChainId(window.currentChainId, ethereumChainId)) {
        loadInterface();
      }
    } else {
      alert('Please install MetaMask to continue!');
    }
  });
}

if (manageMusicakesButton != null) {

  manageMusicakesButton.addEventListener('click', () => {
    if (web3) {

      if (checkChainId(window.currentChainId, ethereumChainId)) {
        loadInterface();
      }
    } else {
      alert('Please install MetaMask to continue!');
    }
  });
}

if (musicakesPayButton != null) {

  musicakesPayButton.addEventListener('click', () => {

    if (web3) {

      if (checkChainId(window.currentChainId, ethereumChainId)) {
        payMusicakes();
      }

    } else {
      alert('Please install MetaMask to continue!');
    }
  });
}

if (musicakesClaimDividendsButton != null) {

  musicakesClaimDividendsButton.addEventListener('click', () => {

    if (web3) {

      if (checkChainId(window.currentChainId, ethereumChainId)) {
        claimDividends();
      }

    } else {
      alert('Please install MetaMask to continue!');
    }
  });
}

if (musicakesUpdateDividendsButton != null) {
  musicakesUpdateDividendsButton.addEventListener('click', () => {

    if (web3) {

      if (checkChainId(window.currentChainId, ethereumChainId)) {
        updateDividends();
      }

    } else {
      alert('Please install MetaMask to continue!');
    }

  });
}

if (musicakesTransferButton != null) {
  musicakesTransferButton.addEventListener('click', () => {

    if (web3) {

      if (checkChainId(window.currentChainId, ethereumChainId)) {
        transferMusicakes();
      }
    } else {
      alert('Please install MetaMask to continue!');
    }
  });
}


async function loadInterface() {

  var accounts = await web3.eth.getAccounts();
  const account = accounts[0];
  showAccountAddress.innerHTML = account;

	// Get ETH balance of current address

	var accountWeiBalance = web3.eth.getBalance(account, function(error, result) {
		if (!error) {
  		var accountBalance = (parseFloat(result)/parseFloat(10**18)).toFixed(18);
  		// showAccountBalance.innerHTML = accountBalance;
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
	});

}

async function payMusicakes() {

  var accounts = await web3.eth.getAccounts();
  const account = accounts[0];

	var payAmount = musicakesPayValue.value;

  if (payAmount < price) {
    alert("The minimum price to pay is " + price.toString() + ".");
  }

  else {

  	var payAmountFormatted = web3.utils.toWei(payAmount);


		paymentTokenContract.methods.transfer(musicakesAddress, payAmountFormatted).send({from: account})
		.once('transactionHash', function(hash) {
			console.log(hash);

      var data = JSON.stringify({
        transaction_hash: hash,
        wallet_address: account
      });

      var url;

      if (objectType === 'release') {
        url = '/releases/' + objectId.toString() + '/purchase';
      } else if (objectType === 'track') {
        url = '/tracks/' + objectId.toString() + '/purchase';
      }

      fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': csrf_token_purchase,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: data
      })
      .then(response => {
        console.log(response);
        if (response.ok) {
          alert("Your transaction is pending.");
        }
        return response.json();
      })
      .then(data => {
        console.log(data);
      });

		})
		.catch(error => {
			console.log(error);
		});

  }

}

async function claimDividends() {

  var accounts = await web3.eth.getAccounts();
  const account = accounts[0];

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

  var accounts = await web3.eth.getAccounts();
  const account = accounts[0];

	musicakesContract.methods.updateFundsTokenBalance().send({from: account})
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

  var accounts = await web3.eth.getAccounts();
  const account = accounts[0];

  var musicakesTransferAddressValue = musicakesTransferAddress.value;
  var musicakesTransferAmountValue = Number(musicakesTransferAmount.value);

  if (musicakesTransferAddressValue.length !== 42 || musicakesTransferAddressValue.indexOf('0x') !== 0) {
    alert('Please enter a valid Ethereum address.');
  }

  if (Number.isInteger(musicakesTransferAmountValue) == false) {
    alert("The amount must be an integer.");
  }

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
