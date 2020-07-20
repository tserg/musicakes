const release_id = parseInt(window.appConfig.release_id.address);
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

const musicakesFactoryContractAddress = "0xec67abe36b67afB03228101b7110A0a6155fdCdD";
const musicakesFactoryContract = new web3.eth.Contract(_abi, musicakesFactoryContractAddress);

async function deployMusicakesContract() {
  await ethereum.enable();

  const account = ethereum.selectedAddress;

  const token_name = "Musicakes" + release_id.toString();
  const token_symbol = "MSC_" + release_id.toString();

  musicakesFactoryContract.methods.createNewMusicakes(token_name, token_symbol).send({from: account})
  .once('transactionHash', function(hash) {
    console.log(hash);
  })
  .once('receipt', function(receipt) {
    console.log(receipt);
    const smart_contract_address = receipt['events']['0']['address'];
    console.log(receipt['events']['0']['address']);
    addSmartContractToRelease(release_id, smart_contract_address);

  })
  .on('error', function(error) {
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

      }
      else{
        console.log(error);
        alert("Your Musicakes smart contract could not be deployed.");
      }
   }
  };
  xhr.send(data);

}
