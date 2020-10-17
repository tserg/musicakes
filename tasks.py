import os
import json

from celery import Celery

from dotenv import load_dotenv

from web3 import Web3, HTTPProvider
#from web3.middleware import geth_poa_middleware


load_dotenv()

WEB3_INFURA_PROJECT_ID = os.getenv('WEB3_INFURA_PROJECT_ID', 'Does not exist')
WEB3_INFURA_API_SECRET = os.getenv('WEB3_INFURA_API_SECRET', 'Does not exist')
#WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI', 'Does not exist')
ETHEREUM_CHAIN_ID = os.getenv('ETHEREUM_CHAIN_ID', 3)

# Automatically inject Infura based on selected Ethereum network in environment

if ETHEREUM_CHAIN_ID == 1:
	from web3.auto.infura import w3
else:
	from web3.auto.infura.ropsten import w3


app = Celery('tasks', broker='redis://localhost//')

@app.task
def hello():
	print("Hello")


@app.task
def print_transaction_hash(_transactionHash):

	print(_transactionHash)

	print("w3 connection: ")
	print(w3.isConnected())

	receipt = w3.eth.waitForTransactionReceipt(_transactionHash)

	print(receipt)	

	