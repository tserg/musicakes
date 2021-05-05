import time

from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound

def check_transaction_receipt(_chainId, _transactionHash):
    """
    Helper function to check for the receipt of a transaction

    @param: _chainId The ID of the chain that is currently being used
    @param: _transactionHash The transaction hash to check for

    @returns: The transaction receipt from web3 API
    """
    if _chainId == 1:
        from web3.auto.infura import w3
    else:
        from web3.auto.infura.ropsten import w3

    print(_transactionHash)

    print("w3 connection: ")
    print(w3.isConnected())

    current_check = 0
    check_duration = 10

    # Checks for 5 minutes based on 10 intervals of 30 seconds each

    receipt = None

    while current_check < check_duration:

        try:
            receipt = w3.eth.getTransactionReceipt(_transactionHash)

        except TransactionNotFound as e:

            # Retries after 30 seconds if transaction is not found

            time.sleep(30)
            current_check += 1
            continue

        except Exception as o:
            print(o)
            continue

        break

    return receipt
