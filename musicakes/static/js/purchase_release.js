// const ethereumButton = document.querySelector('#btn-enable-ethereum');
// const showAccountAddress = document.querySelector('#account-address');
// const showAccountBalance = document.querySelector('#account-balance');

// const showAccountPaymentTokenBalance = document.querySelector('#payment-token-balance');

const supportArtistButton = document.querySelector('#btn-support-artist');
const supportArtistValue = document.querySelector('#support-artist-amount');

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

const ethereumChainId = parseInt(window.appConfig.chain_id.value);

var web3 = new Web3(Web3.givenProvider);

const price = parseFloat(window.appConfig.price.value);

const release_id = parseInt(window.appConfig.release_id.value);

const csrf_token_purchase = window.appConfig.csrf_token.value;
if (csrf_token_purchase) {
  console.log("CSRF Token loaded");
}

const artistWalletAddress = window.appConfig.artist_wallet_address.value;

/* Payment token contract */

const paymentTokenAddress = window.appConfig.payment_token_address.value;
const musicakesAddress = window.appConfig.smart_contract_address.value;

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
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "symbol",
          "type": "string"
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
      "constant": false,
      "inputs": [
        {
          "internalType": "address",
          "name": "sender",
          "type": "address"
        },
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
      "name": "transferFrom",
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
  ];

const paymentTokenContract = new web3.eth.Contract(_paymentTokenAbi, paymentTokenAddress);

if (musicakesAddress.length > 2) {
  window.musicakesContract = new web3.eth.Contract(_musicakesAbi, musicakesAddress);
} else {
  window.musicakesContract = null;
}

// Initialise Metamask

window.addEventListener('load', async () => {

  window.provider = await detectEthereumProvider();

  if (provider) {

    console.log('Ethereum successfully detected!');

    ethereum.on('accountsChanged', function(accounts) {
      loadInterface();
    });

    // From now on, this should always be true:
    // provider === window.ethereum

    // Access the decentralized web!

    // Legacy providers may only have ethereum.sendAsync
    const chainId = await provider.request({
      method: 'eth_chainId'
    })

    window.currentChainId = parseInt(chainId);

    if (currentChainId != ethereumChainId) {

      if (ethereumChainId == 1) {
        alert('You are connected to the wrong network. Please switch to the Ethereum mainnet to continue!')
      } else if (ethereumChainId == 3) {
        alert('You are connected to the wrong network. Please switch to the Ropsten testnet to continue!')
      } else {
        alert('You are connected to the wrong network.')
      }

    }

  } else {

    // if the provider is not detected, detectEthereumProvider resolves to null
    alert('Please install MetaMask to continue!');
  }
  startApp();

})

// Initialise buttons

function startApp() {


  if (supportArtistButton != null) {
    supportArtistButton.addEventListener('click', () => {
      if (provider) {

        if (currentChainId != ethereumChainId) {

          if (ethereumChainId == 1) {
            alert('You are connected to the wrong network. Please switch to the Ethereum mainnet to continue!')
          } else if (ethereumChainId == 3) {
            alert('You are connected to the wrong network. Please switch to the Ropsten testnet to continue!')
          } else {
            alert('You are connected to the wrong network.')
          }

        } else {
          supportArtist();
        }
      } else {
        alert('Please install MetaMask to continue!');
      }
    });
  }


  if (manageMusicakesButton != null) {

    manageMusicakesButton.addEventListener('click', () => {
      if (provider) {

        if (currentChainId != ethereumChainId) {

          if (ethereumChainId == 1) {
            alert('You are connected to the wrong network. Please switch to the Ethereum mainnet to continue!')
          } else if (ethereumChainId == 3) {
            alert('You are connected to the wrong network. Please switch to the Ropsten testnet to continue!')
          } else {
            alert('You are connected to the wrong network.')
          }

        } else {
          getAccount();
        }
      } else {
        alert('Please install MetaMask to continue!');
      }
    });
  }




  if (musicakesPayButton != null) {

    musicakesPayButton.addEventListener('click', () => {

      if (provider) {

        if (currentChainId != ethereumChainId) {

          if (ethereumChainId == 1) {
            alert('You are connected to the wrong network. Please switch to the Ethereum mainnet to continue!')
          } else if (ethereumChainId == 3) {
            alert('You are connected to the wrong network. Please switch to the Ropsten testnet to continue!')
          } else {
            alert('You are connected to the wrong network.')
          }

        } else {
          payMusicakes();
        }

      } else {
        alert('Please install MetaMask to continue!');
      }
    });
  }

  if (musicakesClaimDividendsButton != null) {

    musicakesClaimDividendsButton.addEventListener('click', () => {

      if (provider) {

        if (currentChainId != ethereumChainId) {

          if (ethereumChainId == 1) {
            alert('You are connected to the wrong network. Please switch to the Ethereum mainnet to continue!')
          } else if (ethereumChainId == 3) {
            alert('You are connected to the wrong network. Please switch to the Ropsten testnet to continue!')
          } else {
            alert('You are connected to the wrong network.')
          }

        } else {
          claimDividends();
        }

      } else {
        alert('Please install MetaMask to continue!');
      }
    });
  }

  if (musicakesUpdateDividendsButton != null) {
    musicakesUpdateDividendsButton.addEventListener('click', () => {

      if (provider) {

        if (currentChainId != ethereumChainId) {

          if (ethereumChainId == 1) {
            alert('You are connected to the wrong network. Please switch to the Ethereum mainnet to continue!')
          } else if (ethereumChainId == 3) {
            alert('You are connected to the wrong network. Please switch to the Ropsten testnet to continue!')
          } else {
            alert('You are connected to the wrong network.')
          }

        } else {
          updateDividends();
        }

      } else {
        alert('Please install MetaMask to continue!');
      }

    });
  }

  if (musicakesTransferButton != null) {
    musicakesTransferButton.addEventListener('click', () => {

      if (provider) {

        if (currentChainId != ethereumChainId) {

          if (ethereumChainId == 1) {
            alert('You are connected to the wrong network. Please switch to the Ethereum mainnet to continue!')
          } else if (ethereumChainId == 3) {
            alert('You are connected to the wrong network. Please switch to the Ropsten testnet to continue!')
          } else {
            alert('You are connected to the wrong network.')
          }

        } else {
          transferMusicakes();
        }
      } else {
        alert('Please install MetaMask to continue!');
      }
    });
  }
}

async function getAccount() {
	await ethereum.enable();
  loadInterface();
}

async function loadInterface() {

  const account = ethereum.selectedAddress;
	// showAccountAddress.innerHTML = account;

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
			// showAccountPaymentTokenBalance.innerHTML = accountPaymentTokenBalanceFormatted;
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

async function supportArtist() {

  getAccount();

  const account = ethereum.selectedAddress;

  var supportAmount = supportArtistValue.value;

  var supportAmountFormatted = web3.utils.toWei(supportAmount);

  paymentTokenContract.methods.transfer(artistWalletAddress, supportAmountFormatted).send({from: account})
  .once('transactionHash', function(hash) {
    console.log(hash);
  })
  .catch(error => {
    console.log(error);
  });

}

async function payMusicakes() {

  getAccount();

  const account = ethereum.selectedAddress;

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
      releaseIdString = release_id.toString();
      fetch('/releases/' + releaseIdString + '/purchase', {
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

  getAccount();

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

  getAccount();

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

  getAccount();

  const account = ethereum.selectedAddress;

  var musicakesTransferAddressValue = musicakesTransferAddress.value;
  var musicakesTransferAmountValue = Number(musicakesTransferAmount.value);

  if (musicakesTransferAddressValue.length != 42 || musicakesTransferAddressValue.indexOf('0x') != 0) {
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

/*
seeMoreButton.addEventListener('click', () => {
    if (seeMoreArrow.className == "arrow down") {
      seeMoreArrow.className = "arrow up";
      seeMoreText.innerHTML = "  See less";
      musicakesDashboard.style.display = "block";
      // musicakesManagementDashboard.style.display = "block";
    } else {
      seeMoreArrow.className = "arrow down";
      seeMoreText.innerHTML = "  See more";
      musicakesDashboard.style.display = "none";
      // musicakesManagementDashboard.style.display = "none";
    }
});
*/
