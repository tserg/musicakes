console.log(window.appConfig.price);

window.addEventListener('load', async () => {
// Modern dapp browsers...
  if (window.ethereum) {

    window.web3 = new Web3(ethereum);
    try {
      // Request account access if needed
      await ethereum.enable();
      console.log("injected");
      App.initAccount();


    } catch (error) {
      console.log("Please enable access to Metamask");
    }
  }
  // Legacy dapp browsers...
  else if (window.web3) {
    window.web3 = new Web3(web3.currentProvider);
    // Acccounts always exposed
    App.initAccount();

  }
  // Non-dapp browsers...
  else {
    console.log('Non-Ethereum browser detected. You should consider trying MetaMask!');
  }
});

var _abi = [
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
    "payable": false,
    "stateMutability": "nonpayable",
    "type": "function"
  }
];

paymentTokenAddress = "0x50A535377f95f5D60eeAcA43b89cB1bc2187Ba88";

App = {
  Web3Provider: null,
  contracts: {},

  initAccount: function() {

    App.web3Provider = web3.currentProvider;
    // Display current wallet
    console.log("initAccount called");

    web3.eth.getAccounts().then(function(result){

      return result[0];
      
    }).then(function(account) {
      

      document.getElementById("account").innerHTML = account;

      // refresh page when wallet changes
      // see https://metamask.github.io/metamask-docs/Advanced_Concepts/Provider_API#ethereum.on(eventname%2C-callback)

      window.ethereum.on('accountsChanged', function(account) {
        window.location.reload(true);
      });


      // Display current wallet ETH balance
      var accountWeiBalance = web3.eth.getBalance(account, function(error, result) {
        if (!error) {
          console.log(JSON.stringify(result));

          var accountBalance = web3.utils.fromWei(result, "ether");
          document.getElementById("account_balance").innerHTML = accountBalance;

        } else {
          console.log(error);
        }
      });
    })
    return App.initContract();
  },

   initContract: function() {
    $.getJSON('FDT_ERC20Extension.json', function(data) {
      //Get the necessary contract artifact file and instantiate it with truffle-contract
      var FDT_ERC20ExtensionArtifact = data;
      App.contracts.FDT_ERC20Extension = TruffleContract(FDT_ERC20ExtensionArtifact);

      // Set the provider for this contracts
      App.contracts.FDT_ERC20Extension.setProvider(App.web3Provider);

      return App.getTokenSupply();
    });

    
  },



  handleTransferFDT: function(event) {

    console.log("Transfer FDT Button pressed");

    var FDT_ERC20ExtensionInstance;

    web3.eth.getAccounts().then(function(accounts) {

      account = accounts[0];

      App.contracts.FDT_ERC20Extension.deployed().then(function(instance) {
        FDT_ERC20ExtensionInstance = instance;

        return FDT_ERC20ExtensionInstance.transfer($("#transfer-FDT-address").val(), $("#transfer-FDT-amount").val(), {from: account});
      }).catch(function(err) {
        console.log(err.message);
      });
    });


  },


  handleClaimDividends: function(event) {
    console.log("Claim Dividends button pressed");

    var FDT_ERC20ExtensionInstance;

    web3.eth.getAccounts().then(function(accounts) {

      account = accounts[0];

      App.contracts.FDT_ERC20Extension.deployed().then(function(instance) {

        FDT_ERC20ExtensionInstance = instance;

        return FDT_ERC20ExtensionInstance.withdrawFunds({from: account});
      }).catch(function(err) {
        console.log(err.message);
      });

    });
  },

  handlePayContract: function(event) {
    console.log("Pay Button pressed");

    var FDT_ERC20ExtensionInstance;

        // https://ethereum.stackexchange.com/questions/24220/how-to-generate-truffle-artifact-for-already-deployed-contract-for-use-with-web3
    // https://ethereum.stackexchange.com/questions/38828/truffle-what-is-the-best-way-to-to-get-the-json-abi-code-after-deploying-a-cont

    // create a new contract instance with methods defined in abi and the address of the smart contract to call

    var PaymentToken = new web3.eth.Contract(_abi, paymentTokenAddress);

    web3.eth.getAccounts().then(function(accounts) {

      account = accounts[0];

      App.contracts.FDT_ERC20Extension.deployed().then(function(instance) {

        FDT_ERC20ExtensionInstance = instance;
        var _contractAddress = FDT_ERC20ExtensionInstance.address;

        console.log(_contractAddress);
        console.log(account);

        var _payAmount = ($("#pay-contract-amount").val());

        console.log(_payAmount);

        var payAmount = web3.utils.toBN(_payAmount).mul(web3.utils.toBN(10**18));

        console.log("Number of payment tokens to pay: " + payAmount);
        /*
        PaymentToken.methods.approve(account, payAmount).send({from: account}, function(error, transactionHash) {
          console.log("transactionHash: " + transactionHash);
          PaymentToken.methods.transferFrom(account, _contractAddress, payAmount).send({from: account}, function (error2, transactionHash2) {
            console.log("transactionHash2: " + transactionHash2);
            FDT_ERC20ExtensionInstance.updateFundsReceived({from: account});
          });

          

        });

        */

        PaymentToken.methods.approve(account, payAmount).send({from: account})
        .once('transactionHash', function(hash) {
          console.log("Transaction hash: " + hash);
        })
        .once('receipt', function(receipt) {
          console.log(receipt);
        })
        .on('confirmation', function(confNumber) {
          console.log(confNumber);
        })
        .on('error', function(error) {
          console.log(error);
        })
        .then(function(receipt) {
          PaymentToken.methods.transferFrom(account, _contractAddress, payAmount).send({from: account})
          .once('transactionHash', function(hash2) {
            console.log("Transaction hash 2: " + hash2);
          })
          .once('receipt', function(receipt2) {
            console.log(receipt2);
          })
          .on('confirmation', function(confNumber2) {
            console.log(confNumber2);
          })
          .on('error', function(error) {
            console.log(error);
          });
        });


      });
      
    });
  },

  handleUpdateDividends: function(event) {
    var FDT_ERC20ExtensionInstance;

    web3.eth.getAccounts().then(function(accounts) {

      account = accounts[0];

      App.contracts.FDT_ERC20Extension.deployed().then(function(instance) {

        FDT_ERC20ExtensionInstance = instance;

        return FDT_ERC20ExtensionInstance.updateFundsReceived({from: account});
      }).catch(function(err) {
        console.log(err.message);
      });

    });
  },


  handleTransferPaymentToken: function(event) {
    console.log("Transfer payment token button pressed");

    var PaymentToken = new web3.eth.Contract(_abi, paymentTokenAddress);

    web3.eth.getAccounts().then(function(accounts) {

      account = accounts[0];

      var _transferAmount = ($("#transfer-payment-token-amount").val());
      var targetAddress = ($("#transfer-payment-token-address").val());

      console.log(_transferAmount);

      var transferAmount = web3.utils.toBN(_transferAmount).mul(web3.utils.toBN(10**18));

      console.log("Number of payment tokens to transfer: " + transferAmount);

      PaymentToken.methods.approve(account, transferAmount).send({from: account}, function(error, transactionHash) {
        console.log("transactionHash: " + transactionHash);
        PaymentToken.methods.transferFrom(account, targetAddress, transferAmount).send({from: account}, function (error2, transactionHash2) {
          console.log("transactionHash2: " + transactionHash2);
        });
      });
    });

  },

  getTokenSupply: function() {

    var FDT_ERC20ExtensionInstance;

    App.contracts.FDT_ERC20Extension.deployed().then(function(instance) {
      FDT_ERC20ExtensionInstance = instance;

      return FDT_ERC20ExtensionInstance.totalSupply();
    }).then(function(tokenSupply) {
      console.log("Token supply: " + tokenSupply);
      document.getElementById("token-supply").innerHTML = tokenSupply;
    }).catch(function(err){
      console.log(err.message);
    });

    return App.getUserPaymentTokenCount();
  },

  getUserPaymentTokenCount: function() {

    // https://ethereum.stackexchange.com/questions/24220/how-to-generate-truffle-artifact-for-already-deployed-contract-for-use-with-web3
    // https://ethereum.stackexchange.com/questions/38828/truffle-what-is-the-best-way-to-to-get-the-json-abi-code-after-deploying-a-cont

    // create a new contract instance with methods defined in abi and the address of the smart contract to call

    var PaymentToken = new web3.eth.Contract(_abi, paymentTokenAddress);

    web3.eth.getAccounts().then(function(accounts){

      account = accounts[0];

      // to call function of another smart contract on the network, use method.[function]      

      return PaymentToken.methods.balanceOf(account).call();
    }).then(function(_userPaymentTokenCount) {
      userPaymentTokenCount = (parseFloat(_userPaymentTokenCount)/parseFloat(10**18)).toFixed(18);
      console.log("Payment tokens held in this wallet: " + userPaymentTokenCount);
      document.getElementById("payment-token-balance").innerHTML = userPaymentTokenCount;
    }).catch(function(err){
      console.log(err.message);
    });

    return App.getUserTokenCount();

  },

  getUserTokenCount: function() {
    var FDT_ERC20ExtensionInstance;

    web3.eth.getAccounts().then(function(accounts) {
      account = accounts[0];
      App.contracts.FDT_ERC20Extension.deployed().then(function(instance) {
        FDT_ERC20ExtensionInstance = instance;

        return FDT_ERC20ExtensionInstance.balanceOf(account);
      }).then(function(userTokenCount) {
        console.log("Tokens held in this wallet: " + userTokenCount);
        document.getElementById("user-token-count").innerHTML = userTokenCount;
      }).catch(function(err){
        console.log(err.message);
      });

    });

    return App.getDividendBalance();

  },

  getDividendBalance: function() {
    var FDT_ERC20ExtensionInstance;

    web3.eth.getAccounts().then(function(accounts) {
      account = accounts[0];
      App.contracts.FDT_ERC20Extension.deployed().then(function(instance) {
        FDT_ERC20ExtensionInstance = instance;

        return FDT_ERC20ExtensionInstance.withdrawableFundsOf(account);
      }).then(function(userDividendBalance) {
        console.log("User dividend balance: " + userDividendBalance);
        var _userDividendBalance = (parseFloat(userDividendBalance)/parseFloat(10**18)).toFixed(18);
        document.getElementById("dividend-balance").innerHTML = _userDividendBalance;
      }).catch(function(err){
        console.log(err.message);
      });

    });

    return App.getTokenManagementDashboard();
  },

  getTokenManagementDashboard: function() {

    var transferFDTButton = document.getElementById("btn-transfer-FDT");
    transferFDTButton.addEventListener("click", function() {
      return App.handleTransferFDT();
    });

    var claimDividendsButton = document.getElementById("btn-claim-dividends");
    claimDividendsButton.addEventListener("click", function () {
      return App.handleClaimDividends();
    });

    var payToContractButton = document.getElementById("btn-pay-contract");
    payToContractButton.addEventListener("click", function () {
      return App.handlePayContract();

    });

    var transferPaymentTokenButton = document.getElementById("btn-transfer-payment-token");
    transferPaymentTokenButton.addEventListener("click", function () {
      return App.handleTransferPaymentToken();
    });

    var updateDividendsButton = document.getElementById("btn-update-dividends");
    updateDividendsButton.addEventListener("click", function () {
      return App.handleUpdateDividends();
    });

    return App.getContractBalance();
  },

  getContractBalance: function() {

    // create a new contract instance with methods defined in abi and the address of the smart contract to call

    var PaymentToken = new web3.eth.Contract(_abi, paymentTokenAddress);


    App.contracts.FDT_ERC20Extension.deployed().then(function(instance) {
      FDT_ERC20ExtensionInstance = instance;

      return FDT_ERC20ExtensionInstance.address;
    }).then(function(contractAddress) {
      console.log("Contract Address: " + contractAddress);

      document.getElementById("contract-address").innerHTML = contractAddress;



      return PaymentToken.methods.balanceOf(contractAddress).call();
    }).then(function(_contractPaymentTokenCount) {
      contractPaymentTokenCount = (parseFloat(_contractPaymentTokenCount)/parseFloat(10**18)).toFixed(18);
      console.log("Payment tokens held in contract: " + contractPaymentTokenCount);
      document.getElementById("contract-funds-balance").innerHTML = contractPaymentTokenCount;
    }).catch(function(err){
      console.log(err.message);
    });
    


    
  }

};