const ethereumChainId = parseInt(window.appConfig.chain_id.value);

const release_id = parseInt(window.appConfig.release_id.address);
const contract_factory_address = window.appConfig.contract_factory_address.address;
console.log(contract_factory_address);


console.log(release_id);
const deployContractButton = document.querySelector('#deploy-contract-btn');

var web3 = new Web3(Web3.givenProvider);

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
]

// Initialise Metamask

window.addEventListener('load', async () => {

  window.provider = await detectEthereumProvider();

  if (provider) {

    console.log('Ethereum successfully detected!');

    ethereum.on('accountsChanged', function(accounts) {

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

})


const musicakesFactoryContractAddress = contract_factory_address;
// const musicakesFactoryContractAddress = "0xec67abe36b67afB03228101b7110A0a6155fdCdD";
const musicakesFactoryContract = new web3.eth.Contract(_abi, musicakesFactoryContractAddress);

async function deployMusicakesContract() {
  await ethereum.enable();

  const account = ethereum.selectedAddress;

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

function addSmartContractToRelease(release_id, smart_contract_address) {

  var csrf_token = document.getElementById('csrf_token').value;

  var data = JSON.stringify({
    smart_contract_address: smart_contract_address
  });

  var xhr = new XMLHttpRequest();
  xhr.open("POST", '/releases/' + release_id.toString() + "/deploy");

  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Accept", "application/json");
  xhr.setRequestHeader('X-CSRFToken', csrf_token)

  xhr.onreadystatechange = function(error, result) {
    if(xhr.readyState === 4){
      if(xhr.status === 200){

        console.log("Smart contract address added to database.");
        alert("Your Musicakes smart contract has been deployed.");
        window.location.replace('/home');

      }
      else{
        console.log(error);
        alert("Your Musicakes smart contract could not be deployed.");
      }
   }
  };
  xhr.send(data);

}
