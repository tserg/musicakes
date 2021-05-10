const supportArtistButton = document.querySelector('#btn-support-artist');
const supportArtistValue = document.querySelector('#support-artist-amount');

var ethereumChainId = parseInt(document.querySelector('meta[property~="chain-id"]').getAttribute('content'));

const artistWalletAddress = document.querySelector('meta[property~="artist-wallet-address"]').getAttribute('content');
console.log(artistWalletAddress);

/* Payment token contract */
var paymentTokenAddress = document.querySelector('meta[property~="payment-token-address"]').getAttribute('content');

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

    window.paymentTokenContract = new web3.eth.Contract(_paymentTokenAbi, paymentTokenAddress);

  } else {

    // if the provider is not detected, detectEthereumProvider resolves to null
    alert('Please install MetaMask to continue!');
  }

});

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

async function supportArtist() {

  var accounts = await web3.eth.getAccounts();
  const account = accounts[0];

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
