const supportArtistButton = document.querySelector('#btn-support-artist');
const supportArtistValue = document.querySelector('#support-artist-amount');

const showAccountAddressSupportArtist = document.querySelector('#support-artist-account-address');
const showAccountPaymentTokenBalanceSupportArtist = document.querySelector('#payment-token-balance-support-artist');
const launchSupportArtistModalButton = document.querySelector("#support-artist-modal-btn");

var ethereumChainId = parseInt(document.querySelector('meta[property~="chain-id"]').getAttribute('content'));

const artistWalletAddress = document.querySelector('meta[property~="artist-wallet-address"]').getAttribute('content');
console.log(artistWalletAddress);

/* Payment token contract */
const paymentTokenSelectSupportArtist = document.querySelector('#paymentTokenSelectSupportArtist');
var supportArtistPaymentTokenAddress = paymentTokenSelectSupportArtist.value;

var _paymentTokenAbi = [
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
        }
      ],
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "gas": 74710,
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
      "gas": 111065,
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
      "gas": 37791,
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
      "gas": 75641,
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
      "name": "mint",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 75298,
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
      "gas": 111649,
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
      "gas": 7670,
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
      "gas": 6723,
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
      "gas": 1328,
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
      "gas": 1573,
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
    },
    {
      "gas": 1818,
      "inputs": [
        {
          "name": "arg0",
          "type": "address"
        },
        {
          "name": "arg1",
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
      "gas": 1418,
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

    window.supportArtistPaymentTokenContract = new web3.eth.Contract(_paymentTokenAbi, web3.utils.toChecksumAddress(supportArtistPaymentTokenAddress));

  } else {

    // if the provider is not detected, detectEthereumProvider resolves to null
    alert('Please install MetaMask to continue!');
  }

});

if (launchSupportArtistModalButton != null) {

  launchSupportArtistModalButton.addEventListener('click', () => {
	console.log("support artist modal launched");
    if (web3) {

      if (checkChainId(window.currentChainId, ethereumChainId)) {
        loadSupportArtistInterface();
      }
    } else {
      alert('Please install MetaMask to continue!');
    }
  });
}

if (paymentTokenSelectSupportArtist != null) {
	paymentTokenSelectSupportArtist.addEventListener('change', () => {
		if (web3) {
		  if (checkChainId(window.currentChainId, ethereumChainId)) {
			var supportArtistPaymentTokenAddress = paymentTokenSelectSupportArtist.value;
			console.log(supportArtistPaymentTokenAddress);
			window.supportArtistPaymentTokenContract = new web3.eth.Contract(_paymentTokenAbi, supportArtistPaymentTokenAddress);
		        loadSupportArtistInterface();
		      }
		} else {
			alert('Please install MetaMask to continue!');
		}
	});
}

if (supportArtistButton != null) {
  supportArtistButton.addEventListener('click', () => {

    if (web3) {

      if (checkChainId(window.currentChainId, ethereumChainId)) {
        supportArtist();
      }
    } else {
      alert('Please install MetaMask to continue!');
    }
  });
}

async function loadSupportArtistInterface() {

  const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });

  const account = web3.utils.toChecksumAddress(accounts[0]);

  if (showAccountAddressSupportArtist) {
	  showAccountAddressSupportArtist.innerHTML = account;
  }

	// Get payment token balance of current address

	var accountPaymentTokenBalanceSupportArtist = supportArtistPaymentTokenContract.methods.balanceOf(account).call(function(error, result) {
		if (!error) {
			var accountPaymentTokenBalanceSupportArtistFormatted = (parseFloat(result)/parseFloat(10**18)).toFixed(18);
			if (showAccountPaymentTokenBalanceSupportArtist) {
				showAccountPaymentTokenBalanceSupportArtist.innerHTML = accountPaymentTokenBalanceSupportArtistFormatted;
			}
		} else {
			console.log(error);
		}
	});


}

async function supportArtist() {

  var accounts = await web3.eth.getAccounts();
  const account = accounts[0];

  var supportAmount = supportArtistValue.value;
  var supportAmountFormatted = web3.utils.toWei(supportAmount);

  supportArtistPaymentTokenContract.methods.transfer(artistWalletAddress, supportAmountFormatted).send({from: account})
  .once('transactionHash', function(hash) {
    console.log(hash);
  })
  .catch(error => {
    console.log(error);
  });

}
