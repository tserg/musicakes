const ethereumChainId = parseInt(window.appConfig.chain_id.value);

const release_id = parseInt(window.appConfig.release_id.address);
const musicakesFactoryContractAddress = window.appConfig.contract_factory_address.address;
console.log(musicakesFactoryContractAddress);


console.log(release_id);
const deployContractButton = document.querySelector('#deploy-contract-btn');

deployContractButton.addEventListener('click', () => {

  deployMusicakesContract();

});

var _abi = [
    {
      "constant": true,
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "contracts",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
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
      "name": "createNewMusicakes",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "getMusicakesCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "musicakesCount",
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
          "internalType": "uint256",
          "name": "count",
          "type": "uint256"
        }
      ],
      "name": "getMusicakesAddress",
      "outputs": [
        {
          "internalType": "address",
          "name": "musicakesAddress",
          "type": "address"
        }
      ],
      "payable": false,
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

  musicakesFactoryContract.methods.createNewMusicakes(token_name, token_symbol).send({from: account})
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
