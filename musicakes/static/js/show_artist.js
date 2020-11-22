const supportArtistButton = document.querySelector('#btn-support-artist');
const supportArtistValue = document.querySelector('#support-artist-amount');

const ethereumChainId = parseInt(window.appConfig.chain_id.value);

var web3 = new Web3(Web3.givenProvider);

const artistWalletAddress = window.appConfig.artist_wallet_address.value;

/* Payment token contract */

const paymentTokenAddress = window.appConfig.payment_token_address.value;

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

const paymentTokenContract = new web3.eth.Contract(_paymentTokenAbi, paymentTokenAddress);

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

  }
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

});

async function getAccount() {
	await ethereum.enable();

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
