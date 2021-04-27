import os

from celery import Celery
from celery.app.control import Control

from dotenv import load_dotenv

from pathlib import Path

from web3 import Web3

from . import make_celery

from .models import (
    Release,
    Purchase,
    PurchaseCeleryTask,
    DeployCeleryTask
)

from .web3_utils import (
    check_transaction_receipt
)

env_path = Path().absolute() / '.env'

load_dotenv(dotenv_path=env_path)

# Environment variables for Ethereum blockchain

ETHEREUM_CHAIN_ID = os.getenv('ETHEREUM_CHAIN_ID', 'Does not exist')

# Environment variables for Infura

WEB3_INFURA_PROJECT_ID = os.getenv('WEB3_INFURA_PROJECT_ID', 'Does not exist')
WEB3_INFURA_API_SECRET = os.getenv('WEB3_INFURA_API_SECRET', 'Does not exist')

celery_app = make_celery()

celery_control = Control(celery_app)

@celery_app.task(bind=True)
def remove_celery_task(self, _taskId):
    celery_control.revoke(_taskId, terminate=True)
    return True

@celery_app.task(bind=True)
def check_smart_contract_deployed(self, _transactionHash, _releaseId):

    receipt = check_transaction_receipt(ETHEREUM_CHAIN_ID, _transactionHash)

    if receipt:
        print("deploy celery task receipt")
        print(receipt)
        print("logs")
        print(receipt.logs[0].address)

        transactionHash = receipt.transactionHash.hex()
        smart_contract_address = receipt.logs[0].address

        task_id = self.request.id

        deploy_celery_task = DeployCeleryTask.query.filter(DeployCeleryTask.task_id==task_id).one_or_none()

        deploy_celery_task.is_confirmed = True
        deploy_celery_task.update()

        release = Release.query.get(_releaseId)
        release.smart_contract_address = smart_contract_address
        release.update()

    return True

@celery_app.task(bind=True)
def check_purchase_transaction_confirmed(self, _transactionHash, _userId):

    receipt = check_transaction_receipt(ETHEREUM_CHAIN_ID, _transactionHash)

    if receipt:

        print(receipt)

        transactionHash = receipt.transactionHash.hex()
        paid = Web3.fromWei(Web3.toInt(hexstr=receipt.logs[0].data), 'ether')
        walletAddress = receipt['from']

        # Checks if wallet address matches

        task_id = self.request.id

        purchase_celery_task = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.task_id==task_id).one_or_none()

        # Checks if wallet address is same as when transaction hash was first submitted

        if str(walletAddress).lower() == purchase_celery_task.wallet_address:

            # Update the task status to confirmed

            purchase_celery_task.is_confirmed = True

            purchase_celery_task.update()

            # Add the purchase depending on whether it is a track or release

            if purchase_celery_task.purchase_type == 'release':

                purchase = Purchase(
                        user_id = _userId,
                        release_id = purchase_celery_task.purchase_type_id,
                        paid = paid,
                        wallet_address = walletAddress,
                        transaction_hash = transactionHash
                    )

                purchase.insert()

            elif purchase_celery_task.purchase_type == 'track':

                purchase = Purchase(
                        user_id = _userId,
                        track_id = purchase_celery_task.purchase_type_id,
                        paid = paid,
                        wallet_address = walletAddress,
                        transaction_hash = transactionHash
                    )

                purchase.insert()

    return True
