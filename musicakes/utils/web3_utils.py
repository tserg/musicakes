import json
import os
import time

from dotenv import load_dotenv

from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound

load_dotenv()

# Environment variables for Ethereum blockchain

FDT_FACTORY_ADDRESS = os.getenv('FDT_FACTORY_ADDRESS', 'Does not exist')

dir = os.path.dirname(__file__)
ptg_filename = os.path.join(dir, 'abis/PaymentTokenGovernorProxy.json')
erc20_filename = os.path.join(dir, 'abis/ERC20.json')
fdtf_filename = os.path.join(dir, 'abis/FundsDistributionTokenMultiERC20WithFeeFactory.json')

with open(ptg_filename) as f:
	ptg_json = json.load(f)

with open(erc20_filename) as f:
	erc20_json = json.load(f)

with open(fdtf_filename) as f:
	fdtf_json = json.load(f)

ptg_abi = ptg_json["abi"]
erc20_abi = erc20_json["abi"]
fdtf_abi = fdtf_json["abi"]

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

def get_accepted_payment_tokens_info(_chainId):
	"""
	Helper function to get list of accepted payment tokens and related information

    @param: _chainId The ID of the chain that is currently being used

	@returns: A list of tuples (address, name, symbol)
	"""
	if _chainId == 1:
		from web3.auto.infura import w3
	else:
		from web3.auto.infura.ropsten import w3

	print(w3.isConnected())

	result = []

	fdt_factory_instance = w3.eth.contract(address=Web3.toChecksumAddress(FDT_FACTORY_ADDRESS), abi=fdtf_abi)

	_payment_token_governor_proxy_address = fdt_factory_instance.functions.payment_token_governor_proxy_address().call()

	payment_token_governor_instance = w3.eth.contract(address=_payment_token_governor_proxy_address, abi=ptg_abi)

	_accepted_payment_token_count = payment_token_governor_instance.functions.get_accepted_payment_token_count().call()

	if _accepted_payment_token_count == 0:
		return result

	for i in range(1, _accepted_payment_token_count+1):
		_payment_token_address = payment_token_governor_instance.functions.get_accepted_payment_tokens(i).call()
		print(_payment_token_address)

		_payment_token = w3.eth.contract(address=_payment_token_address, abi=erc20_abi)
		_payment_token_name = _payment_token.functions.name().call()
		_payment_token_symbol = _payment_token.functions.symbol().call()

		result.append({'address': _payment_token_address, 'name': _payment_token_name, 'symbol': _payment_token_symbol})

	print(result)
	return result
