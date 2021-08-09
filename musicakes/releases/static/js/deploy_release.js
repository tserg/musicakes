var ethereumChainId = parseInt(document.querySelector('meta[property~="chain-id"]').getAttribute('content'));

const release_id = parseInt(document.querySelector('meta[property~="release-id"]').getAttribute('content'));

const musicakesFactoryContractAddress = document.querySelector('meta[property~="contract-factory-address"]').getAttribute('content');



console.log(release_id);
const deployContractButton = document.querySelector('#deploy-contract-btn');

deployContractButton.addEventListener('click', () => {

  deployMusicakesContract();

});

var _abi = [
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "fundsId",
          "type": "uint256"
        },
        {
          "indexed": false,
          "name": "token",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "name",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "symbol",
          "type": "string"
        }
      ],
      "name": "FundsDistributionTokenCreated",
      "type": "event"
    },
    {
      "inputs": [
        {
          "name": "_target",
          "type": "address"
        },
        {
          "name": "_admin",
          "type": "address"
        },
        {
          "name": "_payment_token_governor_proxy_address",
          "type": "address"
        },
        {
          "name": "_fee_governor_proxy_address",
          "type": "address"
        }
      ],
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "gas": 134529,
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
      "name": "deploy_fdt_contract",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "gas": 1118,
      "inputs": [],
      "name": "admin",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1148,
      "inputs": [],
      "name": "target",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1178,
      "inputs": [],
      "name": "funds_id",
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
      "gas": 1323,
      "inputs": [
        {
          "name": "arg0",
          "type": "uint256"
        }
      ],
      "name": "funds_id_to_address",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1238,
      "inputs": [],
      "name": "payment_token_address",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1268,
      "inputs": [],
      "name": "payment_token_governor_proxy_address",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "gas": 1298,
      "inputs": [],
      "name": "fee_governor_proxy_address",
      "outputs": [
        {
          "name": "",
          "type": "address"
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

    if (musicakesFactoryContractAddress.length > 2) {
      window.musicakesFactoryContract = new web3.eth.Contract(_abi, musicakesFactoryContractAddress);
    } else {
      window.musicakesContract = null;
    }

  } else {

    // if the provider is not detected, detectEthereumProvider resolves to null
    alert('Please install MetaMask to continue!');
  }

});

async function deployMusicakesContract() {

  var accounts = await web3.eth.getAccounts();
  const account = accounts[0];

  const token_name = "Musicakes" + release_id.toString();
  const token_symbol = "MSC_" + release_id.toString();

  musicakesFactoryContract.methods.deploy_fdt_contract(token_name, token_symbol, 0, 100).send({from: account})
  .once('transactionHash', function(hash) {
    console.log(hash);

    var data = JSON.stringify({
      transaction_hash: hash,
      wallet_address: account
    });

    fetch('/releases/' + release_id.toString() + '/deploy', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
          'X-CSRFToken': csrf_token,
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
